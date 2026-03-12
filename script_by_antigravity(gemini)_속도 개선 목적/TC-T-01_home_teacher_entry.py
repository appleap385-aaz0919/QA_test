"""
TC-T-01: 교사 홈 - 선생님 입장하기 버튼 테스트
- URL 접속 > 선생님 입장하기 버튼 클릭 > 새 창 열림 > 홈 화면 요소 노출 확인

테스트 대상 요소:
1. 수업 정보 영역
2. 교과서 영역
3. 출석 체크 카드
4. 과제 카드
5. 수업 분석 영역
6. 우리반 기분 카드
7. 게시판

실행 방법:
    python TC-T-01_home_teacher_entry.py
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json

LOAD_WAIT = 1
MAX_WAIT = 60


async def test_teacher_home_entry():
    """TC-T-01: 교사 홈 진입 테스트 - 새 창 처리"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"
    SCREENSHOT_DIR = "screenshots"

    # 확인해야 할 요소 목록
    EXPECTED_ELEMENTS = {
        "오늘 수업/수업 시작하기": {
            "selectors": [
                "text=/오늘.*수업/i",
                "text=수업 시작하기",
                "text=/수업.*시작/i",
                "[class*='today']",
                "[class*='class']",
            ],
            "required": True
        },
        "교과서": {
            "selectors": [
                "text=교과서",
                "text=교과서 보기",
                "[class*='textbook']",
            ],
            "required": True
        },
        "출석체크": {
            "selectors": [
                "text=출석",
                "text=출석체크",
                "text=/출석.*체크/i",
                "[class*='attendance']",
            ],
            "required": True
        },
        "과제": {
            "selectors": [
                "text=과제",
                "text=/진행.*과제/i",
                "[class*='assignment']",
                "[class*='homework']",
            ],
            "required": True
        },
        "수업 분석/학급 분석": {
            "selectors": [
                "text=분석",
                "text=수업 분석",
                "text=학급 분석",
                "[class*='analysis']",
                "[class*='analytics']",
            ],
            "required": True
        },
        "우리반 기분": {
            "selectors": [
                "text=기분",
                "text=우리반 기분",
                "[class*='mood']",
                "[class*='emotion']",
            ],
            "required": True
        },
        "게시판/공지사항": {
            "selectors": [
                "text=게시판",
                "text=공지",
                "text=공지사항",
                "[class*='board']",
                "[class*='notice']",
            ],
            "required": True
        },
    }

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
        browser = await p.chromium.launch(headless=False, slow_mo=20)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        entry_page = await context.new_page()

        try:
            # Step 1: 진입 페이지 접속
            print("=" * 60)
            print("Step 1: 진입 페이지 접속")
            print("=" * 60)

            await entry_page.goto(TEST_URL, timeout=60000)
            await entry_page.wait_for_load_state("networkidle")
            await asyncio.sleep(LOAD_WAIT)

            await entry_page.screenshot(path=f"{SCREENSHOT_DIR}/tc01_01_entry_page.png", full_page=True)
            print(f"   URL: {entry_page.url}")
            results["steps"].append({"step": 1, "action": "진입 페이지 접속", "status": "PASS"})

            # Step 2: 선생님 입장하기 버튼 클릭 (새 창 열림)
            print("\n" + "=" * 60)
            print("Step 2: 선생님 입장하기 버튼 클릭 (새 창 대기)")
            print("=" * 60)

            teacher_btn = entry_page.locator("button").filter(has_text="선생님 입장하기")

            # 새 창이 열리는 것을 대기
            async with context.expect_page(timeout=MAX_WAIT * 1000) as new_page_info:
                await teacher_btn.click()
                print("   버튼 클릭 완료")

            # 새 창 가져오기
            main_page = await new_page_info.value
            print(f"   새 창 감지됨: {main_page.url}")

            # Step 3: 새 창 로딩 대기
            print("\n" + "=" * 60)
            print("Step 3: 새 창 로딩 대기")
            print("=" * 60)

            try:
                await main_page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)
                print("   networkidle 완료")
            except TimeoutError:
                print("   networkidle 대기 시간 초과 (계속 진행)")

            await asyncio.sleep(LOAD_WAIT)

            # 로딩 indicator 사라질 때까지 대기
            try:
                await main_page.wait_for_selector(".loading", state="hidden", timeout=30000)
                print("   로딩 indicator 사라짐")
            except TimeoutError:
                print("   로딩 indicator 대기 시간 초과")

            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc01_02_main_page.png", full_page=True)
            print(f"   현재 URL: {main_page.url}")
            results["steps"].append({"step": 2, "action": "선생님 입장하기 클릭 및 새 창 진입", "status": "PASS"})

            # Step 4: 홈 화면 요소 확인
            print("\n" + "=" * 60)
            print("Step 4: 홈 화면 요소 확인")
            print("=" * 60)

            for element_name, element_info in EXPECTED_ELEMENTS.items():
                print(f"\n   [{element_name}] 확인 중...")
                found = False
                found_selector = None

                for selector in element_info["selectors"]:
                    try:
                        count = await main_page.locator(selector).count()
                        if count > 0:
                            visible_count = await main_page.locator(selector + ":visible").count()
                            if visible_count > 0:
                                found = True
                                found_selector = selector
                                print(f"      발견: {selector} ({visible_count}개)")
                                break
                    except:
                        continue

                check_result = {
                    "found": found,
                    "selector": found_selector,
                    "required": element_info["required"],
                    "status": "PASS" if found else "FAIL"
                }

                if not found:
                    print(f"      미발견")
                    if element_info["required"]:
                        results["overall_result"] = "FAIL"
                        results["errors"].append(f"필수 요소 누락: {element_name}")

                results["element_checks"][element_name] = check_result

            # 추가 정보 수집
            print("\n" + "=" * 60)
            print("추가 정보")
            print("=" * 60)

            visible_buttons = await main_page.locator("button:visible").count()
            print(f"   보이는 버튼: {visible_buttons}개")

            visible_links = await main_page.locator("a:visible").count()
            print(f"   보이는 링크: {visible_links}개")

            all_text = await main_page.locator("body").inner_text()
            keywords_found = []
            for keyword in ["홈", "교과서", "과제", "평가", "학생", "자료", "설정"]:
                if keyword in all_text:
                    keywords_found.append(keyword)
            print(f"   발견된 키워드: {keywords_found}")

            # 최종 스크린샷
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc01_03_final.png", full_page=True)

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
                req = "(필수)" if check["required"] else "(선택)"
                print(f"      [{status}] {elem} {req}")

            if results["errors"]:
                print("\n   [에러 목록]")
                for err in results["errors"]:
                    print(f"      - {err}")

            with open("test_result_TC-T-01.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result_TC-T-01.json")

            print("\n10초 후 종료...")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))
            try:
                await entry_page.screenshot(path=f"{SCREENSHOT_DIR}/tc01_error.png")
            except:
                pass

        finally:
            await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)

    print("=" * 60)
    print("TC-T-01: 교사 홈 진입 테스트 시작")
    print("=" * 60)

    asyncio.run(test_teacher_home_entry())
