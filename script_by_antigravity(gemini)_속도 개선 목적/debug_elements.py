"""
특정 요소 디버깅 - 진도, 우리반 기분, 오답노트
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_elements():
    """특정 요소 상세 확인"""

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

            # 1. 진도 카드 상세
            print("=" * 60)
            print("1. 진도 카드 상세")
            print("=" * 60)

            # 다양한 셀렉터 시도
            selectors = [
                "[class*='progress']",
                "[class*='진도']",
                "[class*='card']",
                "div:has-text('진도')",
            ]

            for sel in selectors:
                try:
                    count = await main_page.locator(sel).count()
                    if count > 0 and count < 20:
                        print(f"\n   [{sel}] {count}개")
                        elems = await main_page.locator(sel).all()
                        for i, elem in enumerate(elems[:5]):
                            try:
                                text = await elem.inner_text()
                                class_name = await elem.get_attribute("class") or ""
                                if "단원" in text or "모듈" in text or "Lesson" in text:
                                    print(f"      [{i+1}] {class_name[:50]}")
                                    print(f"          {text[:150]}")
                            except:
                                pass
                except:
                    pass

            # 2. 우리반 기분 카드
            print("\n" + "=" * 60)
            print("2. 우리반 기분 카드")
            print("=" * 60)

            mood_selectors = [
                "[class*='mood']",
                "[class*='emotion']",
                "[class*='feeling']",
                "div:has-text('우리반 기분')",
                "div:has-text('기분')",
            ]

            for sel in mood_selectors:
                try:
                    count = await main_page.locator(sel).count()
                    if count > 0:
                        print(f"\n   [{sel}] {count}개")
                        elem = main_page.locator(sel).first
                        text = await elem.inner_text()
                        class_name = await elem.get_attribute("class") or ""
                        print(f"      class: {class_name}")
                        print(f"      text: {text[:300]}")

                        # N명 패턴
                        counts = re.findall(r'(\d+)명', text)
                        print(f"      N명 패턴: {counts}")

                        # 이모지/아이콘 확인
                        icons = re.findall(r'[😊😐😢😡😍👍👎❤️💯⭐]', text)
                        print(f"      이모지: {icons}")
                except:
                    pass

            # 3. 오답노트 카드
            print("\n" + "=" * 60)
            print("3. 오답노트 카드")
            print("=" * 60)

            wrongnote_selectors = [
                "[class*='wrong']",
                "[class*='note']",
                "[class*='오답']",
                "[class*='복습']",
                "div:has-text('오답노트')",
                "div:has-text('복습 전')",
                "div:has-text('복습률')",
            ]

            for sel in wrongnote_selectors:
                try:
                    count = await main_page.locator(sel).count()
                    if count > 0:
                        print(f"\n   [{sel}] {count}개")
                        elem = main_page.locator(sel).first
                        text = await elem.inner_text()
                        class_name = await elem.get_attribute("class") or ""
                        print(f"      class: {class_name}")
                        print(f"      text: {text[:300]}")
                except:
                    pass

            # 전체 페이지에서 키워드 검색
            print("\n" + "=" * 60)
            print("4. 전체 텍스트에서 키워드 검색")
            print("=" * 60)

            body_text = await main_page.locator("body").inner_text()

            keywords = ["복습 전", "복습 완료", "복습률", "우리반 기분", "진도"]
            for kw in keywords:
                if kw in body_text:
                    # 키워드 주변 텍스트 추출
                    idx = body_text.find(kw)
                    start = max(0, idx - 50)
                    end = min(len(body_text), idx + 100)
                    context = body_text[start:end].replace('\n', ' ')
                    print(f"\n   [{kw}]")
                    print(f"      context: {context}")

            await main_page.screenshot(path="screenshots/debug_elements.png", full_page=True)
            print("\n   스크린샷 저장: screenshots/debug_elements.png")

            print("\n15초 후 종료...")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    asyncio.run(debug_elements())
