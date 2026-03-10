"""
AIDT LMS TC-T-01 테스트 스크립트
- 선생님 입장하기 > 홈 화면 요소 노출 확인
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json

LOAD_WAIT = 5
MAX_WAIT = 60  # 60초까지 대기

async def wait_for_main_app(page):
    """메인 앱 화면이 로드될 때까지 대기"""
    print("   메인 앱 로딩 대기 중...")

    # 1. 로딩 indicator 사라질 때까지 대기
    try:
        await page.wait_for_selector(".loading", state="hidden", timeout=MAX_WAIT * 1000)
        print("   로딩 indicator 사라짐")
    except TimeoutError:
        print("   로딩 indicator 대기 시간 초과 (계속 진행)")

    # 2. entry-popup 사라질 때까지 대기
    try:
        await page.wait_for_selector(".entry-popup", state="hidden", timeout=MAX_WAIT * 1000)
        print("   진입 팝업 사라짐")
    except TimeoutError:
        print("   진입 팝업 대기 시간 초과")

    # 3. 추가 대기
    await asyncio.sleep(3)

async def test_teacher_home():
    """TC-T-01: 교사 홈 진입 테스트"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    results = {
        "test_name": "TC-T-01: 교사 홈 진입 테스트",
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": TEST_URL,
        "steps": [],
        "element_checks": {},
        "overall_result": "PASS",
        "errors": []
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            # Step 1: 페이지 접속
            print("=" * 60)
            print("Step 1: 페이지 접속")
            print("=" * 60)
            await page.goto(TEST_URL, timeout=60000)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(LOAD_WAIT)

            await page.screenshot(path="screenshots/tc01_01_initial.png", full_page=True)
            print(f"   URL: {page.url}")
            results["steps"].append({"step": 1, "action": "페이지 접속", "status": "PASS"})

            # Step 2: 선생님 입장하기 버튼 클릭
            print("\n" + "=" * 60)
            print("Step 2: 선생님 입장하기 버튼 클릭")
            print("=" * 60)

            teacher_btn = page.locator("button").filter(has_text="선생님 입장하기")
            await teacher_btn.click()
            print("   버튼 클릭 완료")

            # Step 3: 메인 앱 로딩 대기
            print("\n" + "=" * 60)
            print("Step 3: 메인 앱 로딩 대기")
            print("=" * 60)
            await wait_for_main_app(page)

            await page.screenshot(path="screenshots/tc01_02_after_entry.png", full_page=True)
            print(f"   현재 URL: {page.url}")

            # 진입 팝업 확인
            popup_count = await page.locator(".entry-popup").count()
            print(f"   진입 팝업: {popup_count}")

            if popup_count > 0:
                print("   [주의] 진입 팝업이 아직 존재함")
                results["errors"].append("진입 팝업이 사라지지 않음")

            # Step 4: 페이지 요소 확인
            print("\n" + "=" * 60)
            print("Step 4: 홈 화면 요소 확인")
            print("=" * 60)

            # 확인할 요소들과 선택자
            elements_to_check = {
                "오늘 수업/수업 시작하기": [
                    "text=/오늘.*수업/i",
                    "text=수업 시작하기",
                    "text=/수업.*시작/i",
                    "[class*='today']",
                    "[class*='class']",
                ],
                "교과서": [
                    "text=교과서",
                    "text=교과서 보기",
                    "[class*='textbook']",
                ],
                "출석체크": [
                    "text=출석",
                    "text=출석체크",
                    "text=/출석.*체크/i",
                    "[class*='attendance']",
                ],
                "과제": [
                    "text=과제",
                    "text=/진행.*과제/i",
                    "[class*='assignment']",
                    "[class*='homework']",
                ],
                "수업 분석/학급 분석": [
                    "text=분석",
                    "text=수업 분석",
                    "text=학급 분석",
                    "[class*='analysis']",
                    "[class*='analytics']",
                ],
                "우리반 기분": [
                    "text=기분",
                    "text=우리반 기분",
                    "[class*='mood']",
                    "[class*='emotion']",
                ],
                "게시판/공지사항": [
                    "text=게시판",
                    "text=공지",
                    "text=공지사항",
                    "[class*='board']",
                    "[class*='notice']",
                ],
            }

            for element_name, selectors in elements_to_check.items():
                print(f"\n   [{element_name}] 확인 중...")
                found = False
                found_selector = None

                for selector in selectors:
                    try:
                        count = await page.locator(selector).count()
                        if count > 0:
                            # visible 체크
                            visible_count = await page.locator(selector + ":visible").count()
                            if visible_count > 0:
                                found = True
                                found_selector = selector
                                print(f"      발견: {selector} ({visible_count}개)")
                                break
                    except:
                        continue

                results["element_checks"][element_name] = {
                    "found": found,
                    "selector": found_selector,
                    "status": "PASS" if found else "FAIL"
                }

                if not found:
                    print(f"      미발견")
                    results["overall_result"] = "FAIL"
                    results["errors"].append(f"요소 미발견: {element_name}")

            # 추가 정보 수집
            print("\n" + "=" * 60)
            print("추가 정보")
            print("=" * 60)

            # 보이는 버튼 수
            visible_buttons = await page.locator("button:visible").count()
            print(f"   보이는 버튼: {visible_buttons}개")

            # 보이는 링크 수
            visible_links = await page.locator("a:visible").count()
            print(f"   보이는 링크: {visible_links}개")

            # 주요 텍스트 스캔
            print("\n   [페이지 내 주요 텍스트]")
            all_text = await page.locator("body").inner_text()
            keywords_found = []
            for keyword in ["홈", "교과서", "과제", "평가", "학생", "자료", "설정"]:
                if keyword in all_text:
                    keywords_found.append(keyword)
            print(f"   발견된 키워드: {keywords_found}")

            # 최종 스크린샷
            await page.screenshot(path="screenshots/tc01_03_final.png", full_page=True)

            # 결과 요약
            print("\n" + "=" * 60)
            print("테스트 결과 요약")
            print("=" * 60)
            print(f"   테스트명: {results['test_name']}")
            print(f"   실행일시: {results['test_date']}")
            print(f"   최종 결과: {results['overall_result']}")

            print("\n   [요소별 결과]")
            for elem, check in results["element_checks"].items():
                status = "OK" if check["found"] else "FAIL"
                print(f"      [{status}] {elem}")

            if results["errors"]:
                print("\n   [에러 목록]")
                for err in results["errors"]:
                    print(f"      - {err}")

            # 결과 저장
            with open("test_result_TC-T-01.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result_TC-T-01.json")

            print("\n10초 후 종료...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))
            await page.screenshot(path="screenshots/tc01_error.png")

        finally:
            await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    asyncio.run(test_teacher_home())
