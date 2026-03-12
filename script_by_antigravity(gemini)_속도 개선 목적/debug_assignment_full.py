"""
과제 카드 전체 텍스트 확인
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_full_text():
    """전체 텍스트에서 과제 패턴 찾기"""

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
            print("전체 텍스트에서 과제 패턴 찾기")
            print("=" * 60)

            # 전체 body 텍스트
            body_text = await main_page.locator("body").inner_text()

            # 과제 섹션 찾기
            idx = body_text.find("진행 중인 과제")
            if idx != -1:
                # 과제 섹션부터 1000자
                section_text = body_text[idx:idx+1500]
                print("\n1. 과제 섹션 텍스트:")
                print("-" * 40)
                print(section_text)
                print("-" * 40)

            # 제출/평가 패턴 전체에서 찾기
            print("\n2. 전체 텍스트에서 패턴:")
            all_제출 = re.findall(r'제출[^\d]*(\d+)/(\d+)', body_text)
            all_평가 = re.findall(r'평가[^\d]*(\d+)/(\d+)', body_text)
            all_건 = re.findall(r'(\d+)\s*건', body_text)

            print(f"   제출 N/N: {all_제출}")
            print(f"   평가 N/N: {all_평가}")
            print(f"   N건: {all_건}")

            # 과제 카드 요소 개수 확인
            print("\n3. 과제 관련 요소:")
            assignment_items = await main_page.locator("[class*='assignment-item'], [class*='assignment-card']").count()
            print(f"   assignment-item/card: {assignment_items}개")

            # 과제 목록 아이템 찾기
            items = await main_page.locator(".assignment-section *").all()
            print(f"   assignment-section 자식 요소: {len(items)}개")

            # 스크린샷
            await main_page.screenshot(path="screenshots/debug_full_page.png", full_page=True)
            print("\n   스크린샷: screenshots/debug_full_page.png")

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
    asyncio.run(debug_full_text())
