"""
진도 카드 bounding box 디버깅
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_bbox():
    """진도 카드 bounding box 확인"""

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
            except TimeoutError:
                pass

            await asyncio.sleep(LOAD_WAIT)
            try:
                await main_page.wait_for_selector(".loading", state="hidden", timeout=30000)
            except TimeoutError:
                pass

            print("=" * 60)
            print("진도 카드 Bounding Box 디버깅")
            print("=" * 60)

            # 1. 뷰포트 크기
            viewport = main_page.viewport_size
            print(f"\n뷰포트: {viewport}")

            # 2. 각 progress-card의 bounding box
            all_progress = await main_page.locator(".progress-card").all()
            print(f"\n.progress-card 총 {len(all_progress)}개")

            for i, card in enumerate(all_progress):
                try:
                    box = await card.bounding_box()
                    text = await card.inner_text()
                    class_name = await card.get_attribute("class") or ""

                    print(f"\n[{i+1}] class: {class_name}")
                    if box:
                        print(f"    box: x={box['x']:.1f}, y={box['y']:.1f}, w={box['width']:.1f}, h={box['height']:.1f}")
                        print(f"    범위: x {box['x']:.1f} ~ {box['x']+box['width']:.1f}")
                    else:
                        print(f"    box: None (숨겨짐)")
                    print(f"    text: {text[:80]}")
                except Exception as e:
                    print(f"    에러: {e}")

            # 3. 진도 카드 부모 컨테이너 찾기
            print("\n" + "=" * 60)
            print("부모 컨테이너 확인")
            print("=" * 60)

            # progress-card의 부모들 찾기
            if all_progress:
                first_card = all_progress[0]
                # 부모, 조부모 찾기
                for level in range(1, 5):
                    try:
                        parent = first_card.locator(f"xpath=ancestor::div[{level}]")
                        parent_class = await parent.get_attribute("class") or ""
                        parent_box = await parent.bounding_box()
                        print(f"\n{level}단계 부모: {parent_class[:50]}")
                        if parent_box:
                            print(f"    box: x={parent_box['x']:.1f}, y={parent_box['y']:.1f}, w={parent_box['width']:.1f}")
                    except:
                        break

            print("\n15초 후 종료...")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_bbox())
