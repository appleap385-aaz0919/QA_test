"""
모든 버튼 텍스트 확인
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_all_btns():
    """모든 버튼 확인"""

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

            print("=" * 60)
            print("모든 버튼 텍스트 (줄바꿈 → 공백으로 변환)")
            print("=" * 60)

            # 모든 버튼 수집
            all_buttons = await main_page.locator("button").all()
            print(f"\n총 버튼 수: {len(all_buttons)}개\n")

            unique_texts = set()
            for i, btn in enumerate(all_buttons):
                try:
                    inner_text = await btn.inner_text()
                    # 줄바꿈을 공백으로 변환
                    normalized_text = ' '.join(inner_text.split())
                    unique_texts.add(normalized_text)
                except:
                    pass

            print("고유 버튼 텍스트:")
            for text in sorted(unique_texts):
                print(f"   - '{text}'")

            # '상세' 포함 버튼 찾기
            print("\n'상세' 포함 버튼:")
            for text in sorted(unique_texts):
                if '상세' in text:
                    print(f"   - '{text}'")

            print("\n15초 후 종료...")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_all_btns())
