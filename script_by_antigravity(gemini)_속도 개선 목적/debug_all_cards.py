"""
홈 화면 카드 구조 디버깅
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_all_cards():
    """홈 화면 모든 카드 구조 확인"""

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
            print("홈 화면 카드 구조 분석")
            print("=" * 60)

            # 1. 교과서 관련 요소
            print("\n1. 교과서 관련 요소:")
            textbook_elements = await main_page.locator("[class*='textbook'], [class*='book']").all()
            print(f"   총 {len(textbook_elements)}개")
            for i, elem in enumerate(textbook_elements[:5]):
                try:
                    text = await elem.inner_text()
                    class_name = await elem.get_attribute("class")
                    print(f"\n   [{i+1}] class: {class_name[:50]}")
                    print(f"       text: {text[:100]}")
                except:
                    pass

            # 2. 분석 관련 요소
            print("\n\n2. 분석(analysis) 관련 요소:")
            analysis_elements = await main_page.locator("[class*='analysis'], [class*='analytics']").all()
            print(f"   총 {len(analysis_elements)}개")
            for i, elem in enumerate(analysis_elements[:5]):
                try:
                    text = await elem.inner_text()
                    class_name = await elem.get_attribute("class")
                    print(f"\n   [{i+1}] class: {class_name[:50]}")
                    print(f"       text: {text[:150]}")
                except:
                    pass

            # 3. 인사이트 관련 요소
            print("\n\n3. 인사이트(insight) 관련 요소:")
            insight_elements = await main_page.locator("[class*='insight']").all()
            print(f"   총 {len(insight_elements)}개")
            for i, elem in enumerate(insight_elements[:5]):
                try:
                    text = await elem.inner_text()
                    class_name = await elem.get_attribute("class")
                    print(f"\n   [{i+1}] class: {class_name[:50]}")
                    print(f"       text: {text[:150]}")
                except:
                    pass

            # 4. 전체 섹션/카드 구조
            print("\n\n4. 주요 섹션/카드 구조:")
            section_patterns = ["section", "card", "widget", "box", "container"]
            for pattern in section_patterns:
                elements = await main_page.locator(f"[class*='{pattern}']").all()
                if len(elements) > 0:
                    print(f"\n   [{pattern}] {len(elements)}개")

            # 5. 헤더/타이틀 텍스트 모두 수집
            print("\n\n5. 카드 타이틀/헤더 텍스트:")
            headers = await main_page.locator("h1, h2, h3, h4, [class*='title'], [class*='header']").all()
            for i, h in enumerate(headers[:20]):
                try:
                    text = await h.inner_text()
                    if text.strip():
                        class_name = await h.get_attribute("class") or ""
                        print(f"   [{i+1}] {text.strip()[:40]} ({class_name[:30]})")
                except:
                    pass

            # 6. 스크린샷
            await main_page.screenshot(path="screenshots/debug_all_cards.png", full_page=True)
            print("\n   스크린샷 저장: screenshots/debug_all_cards.png")

            print("\n20초 후 종료...")
            await asyncio.sleep(20)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    asyncio.run(debug_all_cards())
