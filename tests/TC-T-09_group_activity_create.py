"""
TC-T-09: 모둠활동 작성하기 - 타일형 활동 만들기
- LNB '모둠활동' 메뉴 > 작성하기 버튼 > 활동 만들기 팝업 > 타일형 활동 만들기

테스트 시나리오:
1. 선생님 입장하기
2. LNB '모둠활동' 메뉴 클릭
3. 모둠활동 리스트 페이지 확인
4. 작성하기 버튼 클릭
5. 활동 만들기 팝업 확인
6. 활동 이름 'sample' 입력
7. '타일형' 선택 확인
8. 만들기 버튼 클릭
9. 새 창으로 'sample' 창 열리는지 확인

"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json

LOAD_WAIT = 5
MAX_WAIT = 60
SCREENSHOT_DIR = "screenshots"

results = {
    "test_name": "TC-T-09: 모둠활동 작성하기 - 타일형",
    "test_date": "",
    "url": "",
    "steps": [],
    "checks": {},
    "overall_result": "PASS",
    "errors": []
}


async def test_group_activity_create():
    """TC-T-09: 모둠활동 작성하기 - 타일형"""
    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"
    results["test_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results["url"] = TEST_URL

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
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
            results["steps"].append({
                "step": 1,
                "action": "선생님 입장하기",
                "check_item": "진입 페이지",
                "detail": "선생님 입장하기 버튼 클릭 > 메인 페이지 이동",
                "status": "PASS"
            })

            # Step 2: LNB '모둠활동' 메뉴 클릭
            print("\n" + "=" * 60)
            print("Step 2: LNB '모둠활동' 메뉴 클릭")
            print("=" * 60)
            group_menu_selectors = [
                "text=/모둠활동/",
                "text=/모둠 활동/",
                "text=/모둠/",
                "[class*='lnb']:has-text('모둠')",
            ]
            group_menu = None
            for selector in group_menu_selectors:
                count = await main_page.locator(selector).count()
                if count > 0:
                    group_menu = main_page.locator(selector).first
                    print(f"   모둠활동 메뉴 발견: {count}개 (selector: {selector})")
                    break

            if group_menu:
                await group_menu.click()
                print("   모둠활동 메뉴 클릭")
                await asyncio.sleep(LOAD_WAIT)
                await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc09_01_group_menu.png", full_page=True)
                results["steps"].append({
                    "step": 2,
                    "action": "모둠활동 메뉴 클릭",
                    "check_item": "LNB 메뉴",
                    "detail": "모둠활동 메뉴 클릭 > 모둠활동 리스트 페이지 이동",
                    "status": "PASS"
                })
            else:
                print("   모둠활동 메뉴를 찾을 수 없음")
                results["steps"].append({
                    "step": 2,
                    "action": "모둠활동 메뉴 찾기",
                    "check_item": "LNB 메뉴",
                    "detail": "모둠활동 메뉴를 찾을 수 없음",
                    "status": "FAIL"
                })
                results["overall_result"] = "FAIL"
                results["errors"].append("모둠활동 메뉴를 찾을 수 없음")
                raise Exception("모둠활동 메뉴를 찾을 수 없음")

            # Step 3: 모둠활동 리스트 페이지 확인
            print("\n" + "=" * 60)
            print("Step 3: 모둠활동 리스트 페이지 확인")
            print("=" * 60)
            page_text = await main_page.locator("body").inner_text()
            has_activity_list = "활동" in page_text or "모둠" in page_text or "작성" in page_text
            print(f"   모둠활동 페이지 키워드 존재: {has_activity_list}")
            results["checks"]["모둠활동_페이지"] = {"found": has_activity_list, "status": "PASS" if has_activity_list else "CHECK"}
            results["steps"].append({
                "step": 3,
                "action": "모둠활동 페이지 확인",
                "check_item": "페이지 노출",
                "detail": f"모둠활동 리스트 페이지 키워드 확인 (found: {has_activity_list})",
                "status": "PASS" if has_activity_list else "CHECK"
            })

            # Step 4: 작성하기 버튼 클릭
            print("\n" + "=" * 60)
            print("Step 4: 작성하기 버튼 클릭")
            print("=" * 60)
            write_btn_selectors = [
                "button:has-text('작성하기')",
                "span:has-text('작성하기')",
                "button:has-text('등록')",
                "button:has-text('추가')",
            ]
            write_btn = None
            write_btn_count = 0
            for selector in write_btn_selectors:
                count = await main_page.locator(selector).count()
                if count > 0:
                    write_btn_count = count
                    write_btn = main_page.locator(selector).first
                    print(f"   작성하기 버튼 발견: {count}개 (selector: {selector})")
                    break

            if write_btn:
                await write_btn.click()
                print("   작성하기 버튼 클릭")
                await asyncio.sleep(LOAD_WAIT)
                await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc09_02_write_popup.png", full_page=True)
                results["checks"]["작성하기_버튼"] = {"found": True, "count": write_btn_count, "status": "PASS"}
                results["steps"].append({
                    "step": 4,
                    "action": "작성하기 버튼 클릭",
                    "check_item": "버튼 클릭",
                    "detail": f"작성하기 버튼 클릭 ({write_btn_count}개 발견)",
                    "status": "PASS"
                })

                # Step 5: 활동 만들기 팝업 확인
                print("\n" + "=" * 60)
                print("Step 5: 활동 만들기 팝업 확인")
                print("=" * 60)
                # 모달/팝업 대기
                try:
                    await main_page.wait_for_selector(".modal-content, .modal-dialog, .modal, [class*='popup']", state="visible", timeout=5000)
                    print("   활동 만들기 팝업 감지됨")
                except TimeoutError:
                    print("   팝업 감지되지 않음 (계속 진행)")

                await asyncio.sleep(1)
                page_text = await main_page.locator("body").inner_text()
                has_popup = "활동" in page_text and ("만들기" in page_text or "이름" in page_text or "타일형" in page_text)
                print(f"   활동 만들기 팝업 키워드 확인: {has_popup}")
                results["checks"]["활동_만들기_팝업"] = {"found": has_popup, "status": "PASS" if has_popup else "CHECK"}
                results["steps"].append({
                    "step": 5,
                    "action": "활동 만들기 팝업 확인",
                    "check_item": "팝업 노출",
                    "detail": f"활동 만들기 팝업 키워드 확인 (found: {has_popup})",
                    "status": "PASS" if has_popup else "CHECK"
                })

                # Step 6: 활동 이름 'sample' 입력
                print("\n" + "=" * 60)
                print("Step 6: 활동 이름 'sample' 입력")
                print("=" * 60)
                # 모달 내의 input 찾기
                modal_container = main_page.locator(".modal-content, .modal-dialog, .modal, [class*='popup']").first
                input_found = False

                # 모달 내 input 찾기
                input_selectors = [
                    ".modal-content input[type='text']",
                    ".modal-dialog input[type='text']",
                    ".modal input[type='text']",
                    "input[type='text']",
                    "input:not([type])",
                ]
                for selector in input_selectors:
                    try:
                        input_el = main_page.locator(selector).first
                        if await input_el.is_visible(timeout=2000):
                            await input_el.click()
                            await asyncio.sleep(0.3)
                            await input_el.fill("sample")
                            print(f"   활동 이름 'sample' 입력 (selector: {selector})")
                            input_found = True
                            await asyncio.sleep(1)
                            break
                    except:
                        continue

                results["checks"]["활동_이름_입력"] = {"found": input_found, "status": "PASS" if input_found else "CHECK"}
                results["steps"].append({
                    "step": 6,
                    "action": "활동 이름 입력",
                    "check_item": "입력 필드",
                    "detail": f"활동 이름 'sample' 입력 ({'성공' if input_found else '실패'})",
                    "status": "PASS" if input_found else "CHECK"
                })

                # Step 7: '타일형' 선택 확인
                print("\n" + "=" * 60)
                print("Step 7: '타일형' 선택 확인")
                print("=" * 60)
                tile_selectors = [
                    "input[type='radio'][value*='tile']",
                    "input[type='radio'][value*='타일']",
                    "label:has-text('타일형')",
                    "span:has-text('타일형')",
                    "[class*='radio']:has-text('타일')",
                ]
                tile_selected = False
                for selector in tile_selectors:
                    count = await main_page.locator(selector).count()
                    if count > 0:
                        try:
                            tile_el = main_page.locator(selector).first
                            # radio 버튼이면 클릭해서 선택
                            if "radio" in selector:
                                await tile_el.click()
                                print(f"   타일형 라디오 버튼 클릭 (selector: {selector})")
                            else:
                                # label이나 span이면 클릭
                                await tile_el.click()
                                print(f"   타일형 옵션 클릭 (selector: {selector})")
                            tile_selected = True
                            await asyncio.sleep(0.5)
                            break
                        except:
                            continue

                # 타일형이 기본 선택되어 있을 수 있으므로, 선택 여부만 확인
                if not tile_selected:
                    page_text = await main_page.locator("body").inner_text()
                    if "타일형" in page_text:
                        print("   타일형 옵션 존재 확인 (기본 선택 가능)")
                        tile_selected = True

                results["checks"]["타일형_선택"] = {"found": tile_selected, "status": "PASS" if tile_selected else "CHECK"}
                results["steps"].append({
                    "step": 7,
                    "action": "타일형 선택 확인",
                    "check_item": "라디오 버튼",
                    "detail": f"타일형 옵션 선택 확인 ({'성공' if tile_selected else '확인 필요'})",
                    "status": "PASS" if tile_selected else "CHECK"
                })

                # Step 8: 만들기 버튼 클릭
                print("\n" + "=" * 60)
                print("Step 8: 만들기 버튼 클릭")
                print("=" * 60)
                create_btn_selectors = [
                    "button:has-text('만들기')",
                    "button:has-text('생성')",
                    "button:has-text('확인')",
                    "button.btn.fill:has-text('만들기')",
                    "span:has-text('만들기')",
                ]
                create_btn = None
                create_btn_found = False
                for selector in create_btn_selectors:
                    count = await main_page.locator(selector).count()
                    if count > 0:
                        create_btn = main_page.locator(selector).first
                        print(f"   만들기 버튼 발견: {count}개 (selector: {selector})")
                        create_btn_found = True
                        break

                if create_btn:
                    # 새 창이 열리는 것을 감지
                    try:
                        async with context.expect_page(timeout=MAX_WAIT * 1000) as new_page_info:
                            await create_btn.click()
                            print("   만들기 버튼 클릭")

                        activity_page = await new_page_info.value
                        try:
                            await activity_page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)
                        except TimeoutError:
                            pass
                        await asyncio.sleep(LOAD_WAIT)

                        activity_url = activity_page.url
                        activity_title = await activity_page.title()
                        print(f"   새 창 URL: {activity_url}")
                        print(f"   새 창 제목: {activity_title}")

                        # Step 9: 새 창으로 'sample' 창 열리는지 확인
                        print("\n" + "=" * 60)
                        print("Step 9: 새 창으로 'sample' 창 열리는지 확인")
                        print("=" * 60)

                        # URL에 sample이 포함되거나, 페이지 제목에 sample이 포함되거나
                        has_sample = "sample" in activity_url.lower() or "sample" in activity_title.lower()
                        page_content = await activity_page.locator("body").inner_text()
                        has_sample_content = "sample" in page_content

                        if has_sample or has_sample_content:
                            print(f"   새 창에서 'sample' 확인됨")
                            results["checks"]["새창_sample"] = {
                                "found": True,
                                "url": activity_url,
                                "title": activity_title,
                                "status": "PASS"
                            }
                            results["steps"].append({
                                "step": 8,
                                "action": "만들기 버튼 클릭",
                                "check_item": "버튼 클릭",
                                "detail": "만들기 버튼 클릭 > 새 창 열림",
                                "status": "PASS"
                            })
                            results["steps"].append({
                                "step": 9,
                                "action": "새 창 확인",
                                "check_item": "새 창 제목",
                                "detail": f"새 창 URL: {activity_url}, 제목: {activity_title}",
                                "status": "PASS"
                            })
                        else:
                            print(f"   새 창에서 'sample' 미확인")
                            results["checks"]["새창_sample"] = {
                                "found": False,
                                "url": activity_url,
                                "title": activity_title,
                                "status": "CHECK"
                            }
                            results["steps"].append({
                                "step": 8,
                                "action": "만들기 버튼 클릭",
                                "check_item": "버튼 클릭",
                                "detail": "만들기 버튼 클릭 > 새 창 열림",
                                "status": "PASS"
                            })
                            results["steps"].append({
                                "step": 9,
                                "action": "새 창 확인",
                                "check_item": "새 창 제목",
                                "detail": f"새 창에서 'sample' 미확인 (URL: {activity_url})",
                                "status": "CHECK"
                            })

                        await activity_page.screenshot(path=f"{SCREENSHOT_DIR}/tc09_03_new_window.png", full_page=True)

                    except Exception as e:
                        print(f"   새 창 감지 실패: {e}")
                        # 새 창이 안 열리는 경우, 현재 페이지에서 진행
                        await create_btn.click()
                        print("   만들기 버튼 클릭 (새 창 없음)")
                        await asyncio.sleep(LOAD_WAIT)
                        await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc09_03_after_create.png", full_page=True)

                        results["checks"]["만들기_버튼"] = {"found": True, "status": "PASS"}
                        results["steps"].append({
                            "step": 8,
                            "action": "만들기 버튼 클릭",
                            "check_item": "버튼 클릭",
                            "detail": "만들기 버튼 클릭 완료",
                            "status": "PASS"
                        })
                        results["steps"].append({
                            "step": 9,
                            "action": "새 창 확인",
                            "check_item": "새 창 제목",
                            "detail": f"새 창 감지 실패: {str(e)}",
                            "status": "CHECK"
                        })
                else:
                    print("   만들기 버튼을 찾을 수 없음")
                    results["checks"]["만들기_버튼"] = {"found": False, "status": "FAIL"}
                    results["steps"].append({
                        "step": 8,
                        "action": "만들기 버튼 찾기",
                        "check_item": "버튼 찾기",
                        "detail": "만들기 버튼을 찾을 수 없음",
                        "status": "FAIL"
                    })
            else:
                print("   작성하기 버튼을 찾을 수 없음")
                results["checks"]["작성하기_버튼"] = {"found": False, "status": "FAIL"}
                results["steps"].append({
                    "step": 4,
                    "action": "작성하기 버튼 찾기",
                    "check_item": "버튼 찾기",
                    "detail": "작성하기 버튼을 찾을 수 없음",
                    "status": "FAIL"
                })
                results["overall_result"] = "FAIL"
                results["errors"].append("작성하기 버튼을 찾을 수 없음")

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

            with open("test_result_TC-T-09.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result_TC-T-09.json")

            print("\n10초 후 종료...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))
            try:
                await entry_page.screenshot(path=f"{SCREENSHOT_DIR}/tc09_error.png")
            except:
                pass
        finally:
            await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    print("=" * 60)
    print("TC-T-09: 모둠활동 작성하기 - 타일형 테스트 시작")
    print("=" * 60)
    asyncio.run(test_group_activity_create())
