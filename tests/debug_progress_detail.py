"""
진도 카드 상세 디버깅 - 정확한 셀렉터 찾기
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re

LOAD_WAIT = 5
MAX_WAIT = 60


async def debug_progress():
    """진도 카드 정확한 구조 확인"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
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
            print("진도 카드 상세 디버깅")
            print("=" * 60)

            # 1. progress-card 클래스 전체 확인
            print("\n1. .progress-card 클래스 요소들:")
            progress_cards = await main_page.locator(".progress-card").all()
            print(f"   총 {len(progress_cards)}개")
            for i, card in enumerate(progress_cards):
                try:
                    text = await card.inner_text()
                    class_name = await card.get_attribute("class") or ""
                    print(f"\n   [{i+1}] class: {class_name}")
                    print(f"       text: {text[:200]}")
                except:
                    pass

            # 2. progress-card--prev 클래스 확인 (이전 진도)
            print("\n\n2. .progress-card--prev 클래스 (이전 진도):")
            prev_cards = await main_page.locator(".progress-card--prev").all()
            print(f"   총 {len(prev_cards)}개")
            for i, card in enumerate(prev_cards):
                try:
                    text = await card.inner_text()
                    print(f"   [{i+1}] {text[:150]}")
                except:
                    pass

            # 3. 현재 진도 카드만 찾기 (--prev 없는 것)
            print("\n\n3. .progress-card:not(.progress-card--prev) 클래스:")
            current_cards = await main_page.locator(".progress-card:not(.progress-card--prev)").all()
            print(f"   총 {len(current_cards)}개")
            for i, card in enumerate(current_cards):
                try:
                    text = await card.inner_text()
                    print(f"   [{i+1}] {text[:150]}")
                except:
                    pass

            # 4. 진도 관련 모든 클래스 패턴
            print("\n\n4. 진도 관련 클래스 패턴:")
            patterns = ["progress", "진도", "current"]
            for pattern in patterns:
                elems = await main_page.locator(f"[class*='{pattern}']").all()
                unique_classes = set()
                for elem in elems[:20]:
                    try:
                        cls = await elem.get_attribute("class") or ""
                        if cls:
                            # 클래스명에서 패턴이 포함된 것만
                            for c in cls.split():
                                if pattern in c.lower():
                                    unique_classes.add(c)
                    except:
                        pass
                print(f"   [{pattern}] 클래스: {list(unique_classes)[:10]}")

            # 5. 스크린샷
            await main_page.screenshot(path="screenshots/debug_progress.png", full_page=True)
            print("\n   스크린샷 저장: screenshots/debug_progress.png")

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
    asyncio.run(debug_progress())
