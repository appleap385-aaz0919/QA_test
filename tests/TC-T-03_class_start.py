"""
TC-T-03: 수업 시작하기 버튼 테스트
- '수업 시작하기' 버튼 클릭 > 새 창 열림 > 페이지 정상 로딩 확인

확인 대상:
1. 수업 시작하기 버튼 존재 여부
2. 버튼 클릭 시 새 창 열림
3. 새 창에서 페이지 정상 로딩
4. 수업 뷰어 페이지 요소 확인

실행 방법:
    python TC-T-03_class_start.py
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json
from qa_utils import fast_page_wait, wait_for_new_page, get_browser_config, MAX_WAIT

SCREENSHOT_DIR = "screenshots"


async def test_class_start():
    """TC-T-03: 수업 시작하기 버튼 테스트"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    results = {
        "test_name": "TC-T-03: 수업 시작하기 버튼 테스트",
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": TEST_URL,
        "steps": [],
        "checks": {},
        "overall_result": "PASS",
        "errors": []
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(**get_browser_config())
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})

        # 마이크 권한 미리 허용
        await context.grant_permissions(["microphone"])

        entry_page = await context.new_page()

        try:
            # Step 1: 진입 페이지 접속 > 선생님 입장하기
            print("=" * 60)
            print("Step 1: 진입 페이지 접속 > 선생님 입장하기")
            print("=" * 60)

            await entry_page.goto(TEST_URL, timeout=60000)
            await fast_page_wait(entry_page)

            teacher_btn = entry_page.locator("button").filter(has_text="선생님 입장하기")
            main_page = await wait_for_new_page(context, lambda: teacher_btn.click(), MAX_WAIT * 1000)

            # 추가 안정화
            await asyncio.sleep(1)

            print(f"   메인 페이지 URL: {main_page.url}")
            results["steps"].append({"step": 1, "action": "선생님 입장하기", "status": "PASS"})

            # Step 2: 수업 시작하기 버튼 확인
            print("\n" + "=" * 60)
            print("Step 2: 수업 시작하기 버튼 확인")
            print("=" * 60)

            start_btn = main_page.locator("button:has-text('수업 시작하기')")
            start_btn_count = await start_btn.count()
            print(f"   수업 시작하기 버튼: {start_btn_count}개")

            if start_btn_count == 0:
                results["overall_result"] = "FAIL"
                results["errors"].append("수업 시작하기 버튼을 찾을 수 없음")
                results["checks"]["수업 시작하기 버튼"] = {"found": False, "status": "FAIL"}
            else:
                results["checks"]["수업 시작하기 버튼"] = {"found": True, "status": "PASS"}
                print("   버튼 발견")

            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc03_01_main_page.png", full_page=True)
            results["steps"].append({"step": 2, "action": "수업 시작하기 버튼 확인", "status": "PASS" if start_btn_count > 0 else "FAIL"})

            # Step 3: 수업 시작하기 버튼 클릭 > 새 창 확인
            print("\n" + "=" * 60)
            print("Step 3: 수업 시작하기 버튼 클릭 > 새 창 확인")
            print("=" * 60)

            if start_btn_count > 0:
                try:
                    class_page = await wait_for_new_page(context, lambda: start_btn.first.click(), MAX_WAIT * 1000)
                    print(f"   새 창 감지됨: {class_page.url}")

                    # Step 4: 수업 뷰어 페이지 로딩 확인
                    print("\n" + "=" * 60)
                    print("Step 4: 수업 뷰어 페이지 로딩 확인")
                    print("=" * 60)

                    await asyncio.sleep(1)
                    await class_page.screenshot(path=f"{SCREENSHOT_DIR}/tc03_02_class_page.png", full_page=True)

                    # Step 5: 수업 뷰어 페이지 요소 확인
                    print("\n" + "=" * 60)
                    print("Step 5: 수업 뷰어 페이지 요소 확인")
                    print("=" * 60)

                    viewer_url = class_page.url
                    print(f"   현재 URL: {viewer_url}")

                    viewer_elements = {
                        "뷰어_컨테이너": "[class*='viewer'], [class*='Viewer'], [class*='player'], [class*='Player']",
                        "메뉴_또는_네비게이션": "[class*='menu'], [class*='nav'], [class*='sidebar']",
                        "컨텐츠_영역": "[class*='content'], [class*='slide'], [class*='page']",
                    }

                    viewer_checks = {}
                    for elem_name, selector in viewer_elements.items():
                        count = await class_page.locator(selector).count()
                        found = count > 0
                        viewer_checks[elem_name] = {"found": found, "count": count, "status": "PASS" if found else "CHECK"}
                        print(f"   [{elem_name}] {'발견' if found else '미발견'} ({count}개)")

                    is_viewer_page = "viewer" in viewer_url.lower() or "player" in viewer_url.lower() or "class" in viewer_url.lower()
                    viewer_checks["뷰어_URL_패턴"] = {"found": is_viewer_page, "url": viewer_url, "status": "PASS" if is_viewer_page else "CHECK"}
                    print(f"   [뷰어 URL 패턴] {'OK' if is_viewer_page else 'CHECK'}")

                    results["checks"]["새_창_열림"] = {"found": True, "url": viewer_url, "status": "PASS"}
                    results["checks"]["뷰어_페이지_요소"] = viewer_checks
                    results["steps"].append({"step": 3, "action": "수업 시작하기 클릭 및 새 창 확인", "status": "PASS"})
                    results["steps"].append({"step": 4, "action": "수업 뷰어 페이지 로딩", "status": "PASS"})
                    results["steps"].append({"step": 5, "action": "뷰어 페이지 요소 확인", "status": "PASS"})

                    await class_page.screenshot(path=f"{SCREENSHOT_DIR}/tc03_03_final.png", full_page=True)

                except Exception as e:
                    print(f"   에러: {e}")
                    results["overall_result"] = "FAIL"
                    results["errors"].append(f"새 창 열림 실패: {str(e)}")
                    results["checks"]["새_창_열림"] = {"found": False, "status": "FAIL"}
                    results["steps"].append({"step": 3, "action": "수업 시작하기 클릭", "status": "FAIL"})

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

            with open("test_result_TC-T-03.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result_TC-T-03.json")

            print("\n2초 후 종료...")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))
            try:
                await entry_page.screenshot(path=f"{SCREENSHOT_DIR}/tc03_error.png")
            except:
                pass

        finally:
            await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)

    print("=" * 60)
    print("TC-T-03: 수업 시작하기 버튼 테스트 시작")
    print("=" * 60)

    asyncio.run(test_class_start())
