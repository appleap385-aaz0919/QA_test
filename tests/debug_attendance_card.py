"""
출석체크 카드 상세 디버깅
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError

LOAD_WAIT = 5
MAX_WAIT = 60


async def debug_attendance_card():
    """출석체크 카드 내용 상세 확인"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        entry_page = await context.new_page()

        try:
            # 진입
            await entry_page.goto(TEST_URL, timeout=60000)
            await entry_page.wait_for_load_state("networkidle")
            await asyncio.sleep(LOAD_WAIT)

            # 새 창 열기
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
            print("출석체크 카드 상세 분석")
            print("=" * 60)

            # 방법 1: attendance 클래스 요소 찾기
            print("\n1. [class*='attendance'] 요소들:")
            attendance_elements = await main_page.locator("[class*='attendance']").all()
            print(f"   총 {len(attendance_elements)}개 발견")

            for i, elem in enumerate(attendance_elements[:5]):
                try:
                    text = await elem.inner_text()
                    class_name = await elem.get_attribute("class")
                    print(f"\n   [{i+1}] class: {class_name}")
                    print(f"       text: {text[:200]}")
                except:
                    pass

            # 방법 2: 출석 관련 텍스트 검색
            print("\n\n2. 출석 관련 텍스트 검색:")
            keywords = ["출석", "결석", "지각", "미동의", "명"]

            for keyword in keywords:
                try:
                    elements = await main_page.locator(f"text=/{keyword}/").all()
                    if elements:
                        print(f"\n   '{keyword}' 포함 요소 {len(elements)}개:")
                        for j, elem in enumerate(elements[:3]):
                            try:
                                text = await elem.inner_text()
                                parent = await elem.evaluate("el => el.parentElement?.innerText || ''")
                                print(f"      [{j+1}] {text[:50]} | 부모: {parent[:80]}")
                            except:
                                pass
                except:
                    pass

            # 방법 3: 전체 페이지에서 출석 섹션 찾기
            print("\n\n3. 전체 HTML에서 출석 섹션 추출:")
            body_html = await main_page.locator("body").inner_html()

            # 출석 관련 div 찾기
            import re
            attendance_sections = re.findall(r'<div[^>]*class="[^"]*attendance[^"]*"[^>]*>(.*?)</div>', body_html[:50000], re.DOTALL)

            print(f"   attendance 클래스 div {len(attendance_sections)}개 발견")
            for i, section in enumerate(attendance_sections[:3]):
                # HTML 태그 제거
                clean_text = re.sub(r'<[^>]+>', ' ', section)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                print(f"\n   [{i+1}] {clean_text[:200]}")

            # 방법 4: 스크린샷 저장
            await main_page.screenshot(path="screenshots/debug_attendance_full.png", full_page=True)

            # 출석체크 카드 영역만 스크린샷
            try:
                card = main_page.locator("[class*='attendance']").first
                await card.screenshot(path="screenshots/debug_attendance_card.png")
                print("\n   스크린샷 저장: screenshots/debug_attendance_card.png")
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
    import os
    os.makedirs("screenshots", exist_ok=True)
    asyncio.run(debug_attendance_card())
