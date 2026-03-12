"""
카드 구조 상세 디버깅
- 교과서 카드 (재구성 하기 버튼)
- 진도 카드 (2개, 단원명/모듈명)
- 수업 분석 카드 상세
- 공지사항 카드 상세
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_cards_detail():
    """카드 상세 구조 확인"""

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

            # 1. 교과서 카드 상세
            print("=" * 60)
            print("1. 교과서 카드 상세")
            print("=" * 60)
            textbook = await main_page.locator("[class*='textbook']").all()
            for i, elem in enumerate(textbook[:3]):
                try:
                    text = await elem.inner_text()
                    class_name = await elem.get_attribute("class")
                    print(f"\n[{i+1}] {class_name[:40]}")
                    print(f"    {text[:300]}")
                except:
                    pass

            # 재구성 하기 버튼 확인
            print("\n   [재구성 하기 버튼 확인]")
            restructure_btn = await main_page.locator("button:has-text('재구성'), [class*='restructure'], [class*='reconstruct']").count()
            print(f"   재구성 관련 요소: {restructure_btn}개")

            buttons = await main_page.locator("button").all()
            for btn in buttons[:30]:
                try:
                    text = await btn.inner_text()
                    if "재구성" in text or "복습" in text:
                        print(f"   발견: '{text[:50]}'")
                except:
                    pass

            # 2. 진도 카드 확인
            print("\n" + "=" * 60)
            print("2. 진도 카드 확인")
            print("=" * 60)
            progress_cards = await main_page.locator("[class*='progress']").all()
            print(f"   progress 클래스 요소: {len(progress_cards)}개")

            for i, card in enumerate(progress_cards[:5]):
                try:
                    text = await card.inner_text()
                    class_name = await card.get_attribute("class")
                    print(f"\n   [{i+1}] {class_name[:40]}")
                    print(f"   {text[:200]}")
                except:
                    pass

            # 3. 수업 분석 카드 상세
            print("\n" + "=" * 60)
            print("3. 수업 분석 카드 상세")
            print("=" * 60)
            analysis_elements = await main_page.locator("[class*='analysis']").all()
            for i, elem in enumerate(analysis_elements[:3]):
                try:
                    text = await elem.inner_text()
                    class_name = await elem.get_attribute("class")
                    print(f"\n   [{i+1}] {class_name[:40]}")
                    print(f"   {text[:400]}")
                except:
                    pass

            # 4. 공지사항 카드 상세
            print("\n" + "=" * 60)
            print("4. 공지사항 카드 상세")
            print("=" * 60)
            notice = await main_page.locator("[class*='board'], [class*='notice']").all()
            for i, elem in enumerate(notice[:3]):
                try:
                    text = await elem.inner_text()
                    class_name = await elem.get_attribute("class")
                    print(f"\n   [{i+1}] {class_name[:40]}")
                    print(f"   {text[:300]}")
                except:
                    pass

            # 5. 스크린샷
            await main_page.screenshot(path="screenshots/debug_cards_detail.png", full_page=True)
            print("\n   스크린샷 저장: screenshots/debug_cards_detail.png")

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
    asyncio.run(debug_cards_detail())
