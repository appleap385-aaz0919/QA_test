"""
과제 카드 상세 디버깅 - 스크린샷 포함
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_assignment_detail():
    """과제 카드 상세 확인"""

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
            print("과제 카드 상세 디버깅")
            print("=" * 60)

            # 과제 섹션 전체 텍스트
            assignment_elem = main_page.locator(".assignment-section")
            assignment_text = await assignment_elem.inner_text()

            print("\n1. 과제 섹션 전체 텍스트:")
            print("-" * 40)
            print(assignment_text)
            print("-" * 40)

            # 패턴 분석
            print("\n2. 패턴 분석:")

            # N건 찾기
            건_matches = re.findall(r'(\d+)\s*건', assignment_text)
            print(f"   'N건' 패턴: {건_matches}")

            # 제출 N/N 찾기
            제출_matches = re.findall(r'제출[^\d]*(\d+)/(\d+)', assignment_text)
            print(f"   '제출 N/N' 패턴: {제출_matches}")

            # 평가 N/N 찾기
            평가_matches = re.findall(r'평가[^\d]*(\d+)/(\d+)', assignment_text)
            print(f"   '평가 N/N' 패턴: {평가_matches}")

            # 과제명 찾기 (Lesson 또는 AI로 시작)
            과제명_matches = re.findall(r'(Lesson[^_\n]+|AI\s*\w+[^_\n]*)', assignment_text)
            print(f"   과제명 패턴: {과제명_matches[:5]}")

            # 스크린샷 저장
            await main_page.screenshot(path="screenshots/debug_assignment_detail.png", full_page=True)
            print("\n   스크린샷 저장: screenshots/debug_assignment_detail.png")

            # 과제 카드 영역만 별도 스크린샷
            try:
                await assignment_elem.screenshot(path="screenshots/debug_assignment_card_only.png")
                print("   과제 카드 스크린샷: screenshots/debug_assignment_card_only.png")
            except:
                pass

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
    asyncio.run(debug_assignment_detail())
