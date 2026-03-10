"""
진행중인 과제 카드 디버깅
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re

LOAD_WAIT = 5
MAX_WAIT = 60


async def debug_assignment():
    """과제 카드 상세 확인"""

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
            print("진행중인 과제 카드 디버깅")
            print("=" * 60)

            # 1. assignment 클래스 요소
            print("\n1. [class*='assignment'] 요소들:")
            assignment_elems = await main_page.locator("[class*='assignment']").all()
            print(f"   총 {len(assignment_elems)}개")

            for i, elem in enumerate(assignment_elems[:3]):
                try:
                    text = await elem.inner_text()
                    class_name = await elem.get_attribute("class") or ""
                    print(f"\n   [{i+1}] class: {class_name}")
                    print(f"       text:\n{text}")
                except:
                    pass

            # 2. "과제" 키워드 포함 요소
            print("\n" + "=" * 60)
            print("2. '과제' 키워드 포함 요소:")
            과제_elems = await main_page.locator("text=/과제/").all()
            print(f"   총 {len(과제_elems)}개")

            for i, elem in enumerate(과제_elems[:5]):
                try:
                    text = await elem.inner_text()
                    parent = elem.locator("xpath=..")
                    parent_text = await parent.inner_text()
                    print(f"\n   [{i+1}] text: {text[:100]}")
                    print(f"       parent: {parent_text[:200]}")
                except:
                    pass

            # 3. 전체 텍스트에서 과제 관련 부분 추출
            print("\n" + "=" * 60)
            print("3. 전체 텍스트에서 과제 섹션:")
            body_text = await main_page.locator("body").inner_text()

            # "과제" 주변 텍스트 찾기
            idx = body_text.find("진행중인 과제")
            if idx == -1:
                idx = body_text.find("과제")
            if idx != -1:
                start = max(0, idx - 50)
                end = min(len(body_text), idx + 500)
                context = body_text[start:end]
                print(f"\n{context}")

            # 4. N/N, N건 패턴 분석
            print("\n" + "=" * 60)
            print("4. 패턴 분석:")

            # 총 N건
            total_matches = re.findall(r'총\s*(\d+)\s*건', body_text)
            print(f"   '총 N건' 패턴: {total_matches}")

            # N/N 패턴
            nn_matches = re.findall(r'(\d+)/(\d+)', body_text)
            print(f"   'N/N' 패턴: {nn_matches[:10]}")

            # 날짜 패턴 (M/D 또는 M월 D일)
            date_matches = re.findall(r'(\d{1,2})/(\d{1,2})', body_text)
            print(f"   'M/D' 날짜 패턴: {date_matches[:10]}")

            await main_page.screenshot(path="screenshots/debug_assignment.png", full_page=True)
            print("\n   스크린샷 저장: screenshots/debug_assignment.png")

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
    asyncio.run(debug_assignment())
