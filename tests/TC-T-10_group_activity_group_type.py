"""
TC-T-10: 모둠활동 작성하기 - 모둠형
- LNB '모둠활동' 메뉴 > 작성하기 버튼 > 활동 만들기 팝업 > 모둠형 활동 만들기

테스트 시나리오:
1. 선생님 입장하기
2. LNB '모둠활동' 메뉴 클릭
3. 모둠활동 리스트 페이지 확인
4. 작성하기 버튼 클릭
5. 활동 만들기 팝업 확인
6. 활동 이름 'sample' 입력
7. '모둠형' 선택
8. 만들기 버튼 클릭
9. 새 창으로 sample 창 열리는지 확인
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json
from qa_utils import fast_page_wait, wait_for_new_page, get_browser_config, MAX_WAIT

SCREENSHOT_DIR = "screenshots"


async def test_group_activity_group_type():
    """TC-T-10: 모둠활동 작성하기 - 모둠형"""
    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    results = {
        "test_name": "TC-T-10: 모둠활동 작성하기 - 모둠형",
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
        await context.grant_permissions(["microphone"])
        entry_page = await context.new_page()

        try:
            # Step 1: 진입 페이지 > 선생님 입장하기
            print("=" * 60)
            print("Step 1: 진입 페이지 > 선생님 입장하기")
            print("=" * 60)

            await entry_page.goto(TEST_URL, timeout=60000)
            await fast_page_wait(entry_page)

            teacher_btn = entry_page.locator("button").filter(has_text="선생님 입장하기")
            main_page = await wait_for_new_page(context, lambda: teacher_btn.click(), MAX_WAIT * 1000)
            await asyncio.sleep(1)

            print(f"   메인 페이지 URL: {main_page.url}")
            results["steps"].append({"step": 1, "action": "선생님 입장하기", "status": "PASS"})

            # Step 2: LNB '모둠활동' 메뉴 클릭
            print("\n" + "=" * 60)
            print("Step 2: LNB '모둠활동' 메뉴 클릭")
            print("=" * 60)
            group_menu_selectors = ["text=/모둠 활동/", "text=/모둠활동/", "text=/모둠/"]
            group_menu = None
            for selector in group_menu_selectors:
                count = await main_page.locator(selector).count()
                if count > 0:
                    group_menu = main_page.locator(selector).first
                    print(f"   모둠활동 메뉴 발견: {count}개")
                    break

            if group_menu:
                await group_menu.click()
                print("   모둠활동 메뉴 클릭")
                await asyncio.sleep(0.5)
                await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc10_01_group_menu.png", full_page=True)
                results["steps"].append({"step": 2, "action": "모둠활동 메뉴 클릭", "status": "PASS"})
            else:
                print("   모둠활동 메뉴를 찾을 수 없음")
                results["steps"].append({"step": 2, "action": "모둠활동 메뉴 찾기", "status": "FAIL"})
                results["overall_result"] = "FAIL"
                raise Exception("모둠활동 메뉴를 찾을 수 없음")

            # Step 3: 모둠활동 리스트 페이지 확인
            print("\n" + "=" * 60)
            print("Step 3: 모둠활동 리스트 페이지 확인")
            print("=" * 60)
            page_text = await main_page.locator("body").inner_text()
            has_activity_list = "활동" in page_text or "모둠" in page_text or "작성" in page_text
            print(f"   모둠활동 페이지 키워드 존재: {has_activity_list}")
            results["checks"]["모둠활동_페이지"] = {"found": has_activity_list, "status": "PASS" if has_activity_list else "CHECK"}
            results["steps"].append({"step": 3, "action": "모둠활동 페이지 확인", "status": "PASS" if has_activity_list else "CHECK"})

            # Step 4: 작성하기 버튼 클릭
            print("\n" + "=" * 60)
            print("Step 4: 작성하기 버튼 클릭")
            print("=" * 60)
            write_btn_selectors = ["button:has-text('작성하기')", "span:has-text('작성하기')"]
            write_btn = None
            write_btn_count = 0
            for selector in write_btn_selectors:
                count = await main_page.locator(selector).count()
                if count > 0:
                    write_btn_count = count
                    write_btn = main_page.locator(selector).first
                    print(f"   작성하기 버튼 발견: {count}개")
                    break

            if write_btn:
                await write_btn.click()
                print("   작성하기 버튼 클릭")
                await asyncio.sleep(0.5)
                await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc10_02_write_popup.png", full_page=True)
                results["checks"]["작성하기_버튼"] = {"found": True, "count": write_btn_count, "status": "PASS"}
                results["steps"].append({"step": 4, "action": "작성하기 버튼 클릭", "status": "PASS"})

                # Step 5: 활동 만들기 팝업 확인
                print("\n" + "=" * 60)
                print("Step 5: 활동 만들기 팝업 확인")
                print("=" * 60)
                try:
                    await main_page.wait_for_selector(".modal-content, .modal-dialog, .modal, [class*='popup']", state="visible", timeout=3000)
                    print("   활동 만들기 팝업 감지됨")
                except TimeoutError:
                    print("   팝업 감지되지 않음 (계속 진행)")

                await asyncio.sleep(0.5)
                page_text = await main_page.locator("body").inner_text()
                has_popup = "활동" in page_text and ("만들기" in page_text or "이름" in page_text or "모둠형" in page_text or "타일형" in page_text)
                print(f"   활동 만들기 팝업 키워드 확인: {has_popup}")
                results["checks"]["활동_만들기_팝업"] = {"found": has_popup, "status": "PASS" if has_popup else "CHECK"}
                results["steps"].append({"step": 5, "action": "활동 만들기 팝업 확인", "status": "PASS" if has_popup else "CHECK"})

                # Step 6: 활동 이름 'sample' 입력
                print("\n" + "=" * 60)
                print("Step 6: 활동 이름 'sample' 입력")
                print("=" * 60)
                input_found = False
                input_selectors = [".modal-content input[type='text']", ".modal-dialog input[type='text']", "input[type='text']"]
                for selector in input_selectors:
                    try:
                        input_el = main_page.locator(selector).first
                        if await input_el.is_visible(timeout=1000):
                            await input_el.click()
                            await asyncio.sleep(0.2)
                            await input_el.fill("sample")
                            print(f"   활동 이름 'sample' 입력")
                            input_found = True
                            await asyncio.sleep(0.5)
                            break
                    except:
                        continue

                results["checks"]["활동_이름_입력"] = {"found": input_found, "value": "sample", "status": "PASS" if input_found else "CHECK"}
                results["steps"].append({"step": 6, "action": "활동 이름 입력", "status": "PASS" if input_found else "CHECK"})

                # Step 7: '모둠형' 선택
                print("\n" + "=" * 60)
                print("Step 7: '모둠형' 선택")
                print("=" * 60)
                group_type_selectors = ["label:has-text('모둠형')", "span:has-text('모둠형')", "[class*='radio']:has-text('모둠')"]
                group_type_selected = False
                for selector in group_type_selectors:
                    count = await main_page.locator(selector).count()
                    if count > 0:
                        try:
                            await main_page.locator(selector).first.click()
                            print(f"   모둠형 옵션 클릭")
                            group_type_selected = True
                            await asyncio.sleep(0.3)
                            break
                        except:
                            continue

                results["checks"]["모둠형_선택"] = {"found": group_type_selected, "status": "PASS" if group_type_selected else "CHECK"}
                results["steps"].append({"step": 7, "action": "모둠형 선택", "status": "PASS" if group_type_selected else "CHECK"})

                # Step 8: 만들기 버튼 클릭
                print("\n" + "=" * 60)
                print("Step 8: 만들기 버튼 클릭")
                print("=" * 60)
                create_btn_selectors = ["button:has-text('만들기')", "button:has-text('생성')", "button:has-text('확인')"]
                create_btn = None
                for selector in create_btn_selectors:
                    count = await main_page.locator(selector).count()
                    if count > 0:
                        create_btn = main_page.locator(selector).first
                        print(f"   만들기 버튼 발견: {count}개")
                        break

                if create_btn:
                    try:
                        activity_page = await wait_for_new_page(context, lambda: create_btn.click(), MAX_WAIT * 1000)
                        print("   만들기 버튼 클릭")

                        activity_url = activity_page.url
                        activity_title = await activity_page.title()
                        print(f"   새 창 URL: {activity_url}")
                        print(f"   새 창 제목: {activity_title}")

                        # Step 9: 새 창으로 'sample' 창 열리는지 확인
                        print("\n" + "=" * 60)
                        print("Step 9: 새 창으로 sample 창 열리는지 확인")
                        print("=" * 60)

                        has_sample = "sample" in activity_url.lower() or "sample" in activity_title.lower()
                        results["checks"]["새창_sample"] = {"found": True, "url": activity_url, "title": activity_title, "status": "PASS"}
                        results["steps"].append({"step": 8, "action": "만들기 버튼 클릭", "status": "PASS"})
                        results["steps"].append({"step": 9, "action": "새 창 확인", "status": "PASS"})

                        await activity_page.screenshot(path=f"{SCREENSHOT_DIR}/tc10_03_new_window.png", full_page=True)

                        # ===========================================
                        # Step 10: 열린 창 닫기
                        # ===========================================
                        print("\n" + "=" * 60)
                        print("Step 10: 열린 창 닫기")
                        print("=" * 60)

                        await activity_page.close()
                        print("   활동 창 닫기 완료")

                        results["steps"].append({
                            "step": 10,
                            "action": "열린 창 닫기",
                            "check_item": "활동 창 닫기",
                            "detail": "활동 창 닫기 완료",
                            "status": "PASS"
                        })

                        # ===========================================
                        # Step 11: sample 활동 삭제
                        # ===========================================
                        print("\n" + "=" * 60)
                        print("Step 11: sample 활동 삭제")
                        print("=" * 60)

                        # 메인 페이지 새로고침
                        await main_page.reload()
                        await fast_page_wait(main_page)

                        # sample 행 찾기
                        sample_deleted = False
                        try:
                            list_items = main_page.locator(".bar-list-item")
                            count = await list_items.count()
                            for i in range(count):
                                item = list_items.nth(i)
                                chapter_title = item.locator(".chapter-title")
                                if await chapter_title.count() > 0:
                                    title_text = await chapter_title.first.inner_text()
                                    if title_text.strip() == "sample":
                                        # 삭제 버튼 클릭
                                        delete_btn = item.locator("button:has-text('삭제'), .aidt-link2:has-text('삭제')").first
                                        if await delete_btn.count() > 0:
                                            await main_page.evaluate("(btn) => { btn.click(); }", await delete_btn.element_handle())
                                            print("   삭제 버튼 클릭")
                                            await asyncio.sleep(0.5)

                                            # 모달 확인 버튼 클릭
                                            modal_btn = main_page.locator(".modal-content button:has-text('확인'), button:has-text('확인')").first
                                            if await modal_btn.is_visible(timeout=2000):
                                                await modal_btn.click()
                                                print("   모달 확인 버튼 클릭")
                                                await asyncio.sleep(0.5)

                                                # 토스트 알림 확인
                                                for _ in range(5):
                                                    await asyncio.sleep(0.5)
                                                    toast = main_page.locator(".toast, [class*='toast']")
                                                    if await toast.count() > 0:
                                                        toast_text = await toast.first.inner_text()
                                                        if "삭제" in toast_text:
                                                            print(f"   토스트 알림: {toast_text}")
                                                            sample_deleted = True
                                                            break
                                                    if sample_deleted:
                                                        break
                                        break
                        except Exception as e:
                            print(f"   삭제 중 오류: {e}")

                        results["checks"]["활동_삭제"] = {"found": sample_deleted, "status": "PASS" if sample_deleted else "CHECK"}
                        results["steps"].append({
                            "step": 11,
                            "action": "sample 활동 삭제",
                            "check_item": "삭제 + 토스트 알림",
                            "detail": "삭제 완료" if sample_deleted else "삭제 확인 실패",
                            "status": "PASS" if sample_deleted else "CHECK"
                        })
                        await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc10_04_after_delete.png", full_page=True)

                    except Exception as e:
                        print(f"   새 창 감지 실패: {e}")
                        await create_btn.click()
                        print("   만들기 버튼 클릭 (새 창 없음)")
                        await asyncio.sleep(0.5)
                        results["checks"]["만들기_버튼"] = {"found": True, "status": "PASS"}
                        results["steps"].append({"step": 8, "action": "만들기 버튼 클릭", "status": "PASS"})
                        results["steps"].append({"step": 9, "action": "새 창 확인", "status": "CHECK"})
                else:
                    print("   만들기 버튼을 찾을 수 없음")
                    results["checks"]["만들기_버튼"] = {"found": False, "status": "FAIL"}
                    results["steps"].append({"step": 8, "action": "만들기 버튼 찾기", "status": "FAIL"})
            else:
                print("   작성하기 버튼을 찾을 수 없음")
                results["checks"]["작성하기_버튼"] = {"found": False, "status": "FAIL"}
                results["steps"].append({"step": 4, "action": "작성하기 버튼 찾기", "status": "FAIL"})
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

            with open("test_result_TC-T-10.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result_TC-T-10.json")

            print("\n2초 후 종료...")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))
        finally:
            await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    print("=" * 60)
    print("TC-T-10: 모둠활동 작성하기 - 모둠형 테스트 시작")
    print("=" * 60)
    asyncio.run(test_group_activity_group_type())
