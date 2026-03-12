"""
모듈 개수 확인 디버깅 - 스크롤하면서 순차 확인
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_module_count():
    """모듈 개수 확인 - 스크롤하며 순차 확인"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=20)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        entry_page = await context.new_page()

        try:
            await entry_page.goto(TEST_URL, timeout=60000)
            await entry_page.wait_for_load_state("networkidle")
            await asyncio.sleep(LOAD_WAIT)

            teacher_btn = entry_page.locator("button").filter(has_text="선생님 입장하기")
            async with context.expect_page(timeout=MAX_WAIT * 1000) as new_page_info:
                await teacher_btn.click()

            main_page = await new_page_info.value

            try:
                await main_page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)
            except:
                pass

            await asyncio.sleep(LOAD_WAIT)
            try:
                await main_page.wait_for_selector(".loading", state="hidden", timeout=30000)
            except:
                pass

            # 교과서 메뉴 클릭
            textbook_menu = main_page.locator("text=/교과서/").first
            await textbook_menu.click()
            await asyncio.sleep(LOAD_WAIT)

            # 첫 번째 단원 상세 보기 클릭
            detail_span = main_page.locator("span:has-text('단원 상세 보기')")
            print(f"'단원 상세 보기' 버튼 수: {await detail_span.count()}개")

            await detail_span.first.click()
            print("첫 번째 '단원 상세 보기' 클릭")

            await asyncio.sleep(LOAD_WAIT)

            # 스크롤 가능한 컨테이너 찾기
            print("\n" + "=" * 60)
            print("스크롤 가능한 컨테이너 찾기")
            print("=" * 60)

            scroll_containers = await main_page.evaluate("""() => {
                const elements = document.querySelectorAll('*');
                const scrollable = [];
                elements.forEach(el => {
                    const style = window.getComputedStyle(el);
                    const overflow = style.overflow + style.overflowY;
                    if (overflow.includes('auto') || overflow.includes('scroll')) {
                        if (el.scrollHeight > el.clientHeight) {
                            scrollable.push({
                                tag: el.tagName,
                                class: el.className,
                                scrollHeight: el.scrollHeight,
                                clientHeight: el.clientHeight
                            });
                        }
                    }
                });
                return scrollable;
            }""")

            for i, container in enumerate(scroll_containers[:10]):
                print(f"   {i+1}. {container['tag']} - {container['class'][:50]}... (scrollH: {container['scrollHeight']}, clientH: {container['clientHeight']})")

            # 모듈 리스트 컨테이너 스크롤
            print("\n" + "=" * 60)
            print("모듈 리스트 컨테이너 스크롤하며 확인")
            print("=" * 60)

            # overflow-y: auto 또는 scroll인 요소 찾아서 스크롤
            total_count = 0
            scroll_count = 0
            max_scrolls = 30

            while scroll_count < max_scrolls:
                # 현재 보이는 ViewerLinkBox 개수
                current_count = await main_page.locator(".ViewerLinkBox").count()

                if current_count > total_count:
                    new_items = current_count - total_count
                    print(f"   스크롤 {scroll_count + 1}회차: {current_count}개 (+{new_items})")
                    total_count = current_count
                else:
                    print(f"   스크롤 {scroll_count + 1}회차: {current_count}개 (변화 없음)")

                # 모든 스크롤 가능한 요소 스크롤
                await main_page.evaluate("""() => {
                    const elements = document.querySelectorAll('*');
                    elements.forEach(el => {
                        const style = window.getComputedStyle(el);
                        const overflow = style.overflow + style.overflowY;
                        if (overflow.includes('auto') || overflow.includes('scroll')) {
                            if (el.scrollHeight > el.clientHeight) {
                                el.scrollTop += 200;
                            }
                        }
                    });
                }""")
                await asyncio.sleep(0.5)

                scroll_count += 1

                # 변화 없으면 종료 체크
                if scroll_count > 5:
                    no_change_count = 0
                    for _ in range(3):
                        await main_page.evaluate("""() => {
                            const elements = document.querySelectorAll('*');
                            elements.forEach(el => {
                                const style = window.getComputedStyle(el);
                                const overflow = style.overflow + style.overflowY;
                                if (overflow.includes('auto') || overflow.includes('scroll')) {
                                    if (el.scrollHeight > el.clientHeight) {
                                        el.scrollTop += 200;
                                    }
                                }
                            });
                        }""")
                        await asyncio.sleep(0.5)
                        check_count = await main_page.locator(".ViewerLinkBox").count()
                        if check_count == total_count:
                            no_change_count += 1

                    if no_change_count >= 3:
                        print(f"\n   더 이상 새로운 항목 없음. 종료.")
                        break

            # 최종 개수
            final_count = await main_page.locator(".ViewerLinkBox").count()
            print(f"\n" + "=" * 60)
            print(f"최종 ViewerLinkBox 개수: {final_count}개")
            print("=" * 60)

            print("\n15초 후 종료...")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_module_count())
