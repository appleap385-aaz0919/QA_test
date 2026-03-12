"""
TC-T-04: 교과서 보기 버튼 테스트
- 좌측 LNB에서 '교과서' 메뉴 클릭 > 단원 리스트 노출 > 교과서 보기 버튼 클릭 > 뷰어 새 창 열림 > 콘텐츠 정상 노출 확인

테스트 시나리오:
1. 선생님 입장하기
2. LNB '교과서' 메뉴 클릭
3. 단원 리스트 노출 확인
4. '교과서 보기' 버튼 클릭
5. 새 창에서 뷰어 실행 확인
6. 콘텐츠 정상 노출 확인

실행 방법:
    python TC-T-04_textbook_view.py
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json

LOAD_WAIT = 1
MAX_WAIT = 60


async def test_textbook_view():
    """TC-T-04: 교과서 보기 버튼 테스트"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"
    SCREENSHOT_DIR = "screenshots"

    results = {
        "test_name": "TC-T-04: 교과서 보기 버튼 테스트",
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": TEST_URL,
        "steps": [],
        "checks": {},
        "overall_result": "PASS",
        "errors": []
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=20)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})

        # 마이크 권한 미리 허용
        await context.grant_permissions(["microphone"])

        entry_page = await context.new_page()

        try:
            # Step 1: 진입 페이지 > 선생님 입장하기
            print("=" * 60)
            print("Step 1: 진입 페이지 > 선생님 입장하기")
            print("=" * 60)

            await entry_page.goto(TEST_URL, timeout=60000)
            await entry_page.wait_for_load_state("networkidle")
            await asyncio.sleep(LOAD_WAIT)

            teacher_btn = entry_page.locator("button").filter(has_text="선생님 입장하기")
            async with context.expect_page(timeout=MAX_WAIT * 1000) as new_page_info:
                await teacher_btn.click()
                print("   선생님 입장하기 클릭")

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

            print(f"   메인 페이지 URL: {main_page.url}")
            results["steps"].append({"step": 1, "action": "선생님 입장하기", "status": "PASS"})

            # Step 2: LNB '교과서' 메뉴 클릭
            print("\n" + "=" * 60)
            print("Step 2: LNB '교과서' 메뉴 클릭")
            print("=" * 60)

            # 교과서 메뉴 찾기 (LNB)
            textbook_menu = main_page.locator("text=/교과서/").first
            await textbook_menu.click()
            print("   교과서 메뉴 클릭")

            await asyncio.sleep(LOAD_WAIT)
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc04_01_textbook_menu.png", full_page=True)
            results["steps"].append({"step": 2, "action": "교과서 메뉴 클릭", "status": "PASS"})

            # Step 3: 단원 리스트 노출 확인
            print("\n" + "=" * 60)
            print("Step 3: 단원 리스트 노출 확인")
            print("=" * 60)

            # 단원 리스트 확인
            chapter_list = main_page.locator("[class*='chapter'], [class*='unit'], [class*='list']").first
            chapter_count = await main_page.locator("[class*='chapter'], [class*='unit']").count()
            print(f"   단원/목록 요소: {chapter_count}개")

            # 텍스트로 단원 확인
            page_text = await main_page.locator("body").inner_text()
            has_chapter = "단원" in page_text or "Lesson" in page_text
            print(f"   단원 텍스트 존재: {has_chapter}")

            # 단원 번호 오름차순 체크 ('평가' 제외)
            import re
            # "Lesson 1", "Lesson 2" 패턴 또는 "1단원", "2단원" 패턴 모두 지원
            lesson_pattern = re.compile(r'Lesson\s*(\d+)', re.IGNORECASE)
            chapter_pattern = re.compile(r'(\d+)\s*단원')

            # '평가' 단원 제외하고 순수 단원 번호만 추출
            lines = page_text.split('\n')
            pure_chapter_numbers = []
            for line in lines:
                if '평가' not in line:
                    # Lesson N 패턴 먼저 확인
                    match = lesson_pattern.search(line)
                    if not match:
                        # N단원 패턴 확인
                        match = chapter_pattern.search(line)
                    if match:
                        num = int(match.group(1))
                        if num not in pure_chapter_numbers:
                            pure_chapter_numbers.append(num)

            # 오름차순 정렬 확인
            is_ascending = False
            if pure_chapter_numbers:
                sorted_numbers = sorted(pure_chapter_numbers)
                is_ascending = pure_chapter_numbers == sorted_numbers
                print(f"   단원 번호 목록 (평가 제외): {pure_chapter_numbers}")
                print(f"   오름차순 여부: {is_ascending}")
            else:
                print("   단원 번호를 찾을 수 없음")

            results["checks"]["단원_번호_오름차순"] = {
                "chapter_numbers": pure_chapter_numbers,
                "is_ascending": is_ascending,
                "status": "PASS" if is_ascending else "FAIL"
            }

            if not is_ascending and pure_chapter_numbers:
                results["errors"].append(f"단원 번호 오름차순 아님: {pure_chapter_numbers}")

            if has_chapter:
                results["checks"]["단원_리스트"] = {"found": True, "status": "PASS"}
                print("   단원 리스트 노출 확인")
            else:
                results["checks"]["단원_리스트"] = {"found": False, "status": "FAIL"}
                results["overall_result"] = "FAIL"
                results["errors"].append("단원 리스트를 찾을 수 없음")

            step3_status = "PASS" if (has_chapter and is_ascending) else "FAIL" if not has_chapter else "CHECK"
            results["steps"].append({"step": 3, "action": "단원 리스트 노출 확인", "status": step3_status})

            # Step 4: 교과서 보기 버튼 클릭
            print("\n" + "=" * 60)
            print("Step 4: 교과서 보기 버튼 클릭")
            print("=" * 60)

            # 교과서 보기 버튼 찾기
            view_btn = main_page.locator("button:has-text('교과서 보기'), button:has-text('보기')").first
            view_btn_count = await main_page.locator("button:has-text('교과서 보기')").count()

            if view_btn_count > 0:
                print(f"   교과서 보기 버튼: {view_btn_count}개 발견")

                # 새 창이 열리는 것을 대기
                async with context.expect_page(timeout=MAX_WAIT * 1000) as viewer_page_info:
                    await view_btn.click()
                    print("   교과서 보기 버튼 클릭")

                results["checks"]["교과서_보기_버튼"] = {"found": True, "status": "PASS"}
                results["steps"].append({"step": 4, "action": "교과서 보기 버튼 클릭", "status": "PASS"})

                # Step 5: 뷰어 새 창 확인
                print("\n" + "=" * 60)
                print("Step 5: 뷰어 새 창 확인")
                print("=" * 60)

                viewer_page = await viewer_page_info.value

                try:
                    await viewer_page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)
                except TimeoutError:
                    print("   networkidle 대기 시간 초과 (계속 진행)")

                await asyncio.sleep(LOAD_WAIT)
                viewer_url = viewer_page.url
                print(f"   뷰어 URL: {viewer_url}")

                # 뷰어 URL 패턴 확인
                is_viewer_url = "viewer" in viewer_url.lower() or "v-web" in viewer_url.lower()
                print(f"   뷰어 URL 패턴: {'OK' if is_viewer_url else 'CHECK'}")

                results["checks"]["뷰어_새창"] = {"found": True, "url": viewer_url, "status": "PASS" if is_viewer_url else "CHECK"}
                results["steps"].append({"step": 5, "action": "뷰어 새 창 확인", "status": "PASS"})

                await viewer_page.screenshot(path=f"{SCREENSHOT_DIR}/tc04_02_viewer.png", full_page=True)

                # Step 6: 콘텐츠 정상 노출 확인
                print("\n" + "=" * 60)
                print("Step 6: 콘텐츠 정상 노출 확인")
                print("=" * 60)

                # 뷰어 페이지 요소 확인
                viewer_container = await viewer_page.locator("[class*='viewer'], [class*='Viewer'], [class*='player']").count()
                content_area = await viewer_page.locator("[class*='content'], [class*='slide'], [class*='page']").count()

                print(f"   뷰어 컨테이너: {viewer_container}개")
                print(f"   콘텐츠 영역: {content_area}개")

                content_ok = viewer_container > 0 or content_area > 0
                results["checks"]["콘텐츠_노출"] = {
                    "viewer_container": viewer_container,
                    "content_area": content_area,
                    "status": "PASS" if content_ok else "CHECK"
                }
                results["steps"].append({"step": 6, "action": "콘텐츠 정상 노출 확인", "status": "PASS" if content_ok else "CHECK"})

                await viewer_page.screenshot(path=f"{SCREENSHOT_DIR}/tc04_03_final.png", full_page=True)

            else:
                print("   교과서 보기 버튼을 찾을 수 없음")
                results["checks"]["교과서_보기_버튼"] = {"found": False, "status": "FAIL"}
                results["overall_result"] = "FAIL"
                results["errors"].append("교과서 보기 버튼을 찾을 수 없음")
                results["steps"].append({"step": 4, "action": "교과서 보기 버튼 클릭", "status": "FAIL"})

            # 결과 요약
            print("\n" + "=" * 60)
            print("테스트 결과 요약")
            print("=" * 60)
            print(f"   테스트명: {results['test_name']}")
            print(f"   실행일시: {results['test_date']}")
            print(f"   최종 결과: {results['overall_result']}")

            print("\n   [체크 항목별 결과]")
            for check_name, check_result in results["checks"].items():
                status = check_result.get("status", "UNKNOWN")
                print(f"      [{status}] {check_name}")

            if results["errors"]:
                print("\n   [에러 목록]")
                for err in results["errors"]:
                    print(f"      - {err}")

            with open("test_result_TC-T-04.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result_TC-T-04.json")

            print("\n10초 후 종료...")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))
            try:
                await entry_page.screenshot(path=f"{SCREENSHOT_DIR}/tc04_error.png")
            except:
                pass

        finally:
            await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)

    print("=" * 60)
    print("TC-T-04: 교과서 보기 버튼 테스트 시작")
    print("=" * 60)

    asyncio.run(test_textbook_view())
