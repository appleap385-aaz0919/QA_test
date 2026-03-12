"""
donut-center__number 클래스 디버깅
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_donut():
    """donut-center__number 클래스 확인"""

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

            print("=" * 60)
            print("donut-center__number 클래스 디버깅")
            print("=" * 60)

            # donut-center__number 요소 찾기
            donut_elems = await main_page.locator(".donut-center__number").all()
            print(f"\n1. donut-center__number 요소: {len(donut_elems)}개")

            for i, elem in enumerate(donut_elems):
                try:
                    text = await elem.inner_text()
                    class_name = await elem.get_attribute("class") or ""

                    # 부모 요소 확인
                    parent = elem.locator("xpath=..")
                    parent_class = await parent.get_attribute("class") or ""
                    parent_text = await parent.inner_text()

                    print(f"\n   [{i+1}] text: '{text}'")
                    print(f"       class: {class_name}")
                    print(f"       parent class: {parent_class}")
                    print(f"       parent text: {parent_text[:100]}")
                except Exception as e:
                    print(f"   [{i+1}] 에러: {e}")

            # donut 관련 모든 클래스
            print("\n2. donut 관련 클래스들:")
            donut_all = await main_page.locator("[class*='donut']").all()
            for i, elem in enumerate(donut_all[:10]):
                try:
                    class_name = await elem.get_attribute("class") or ""
                    text = await elem.inner_text()
                    print(f"   [{i+1}] {class_name}: '{text}'")
                except:
                    pass

            print("\n15초 후 종료...")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_donut())
