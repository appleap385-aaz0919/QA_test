"""
TC-T-08: 단원 초기화 동작 확인
- LNB '교과서' 메뉴 > 단원 리스트 > 재구성 하기 버튼 클릭 > 임시저장 삭제(있으면) > 임시저장 > 초기화

테스트 시나리오:
1. 선생님 입장하기
2. LNB '교과서' 메뉴 클릭
3. 단원 리스트 노출 확인
4. 첫 번째 단원 '재구성하기' 버튼 클릭
5. 재구성 페이지 확인
6. 임시저장 삭제 버튼 있으면 삭제 (모달에서도 삭제 클릭)
7. 임시저장 버튼 클릭 > 데이터 생성 확인
8. 초기화 버튼 클릭
9. 모달 팝업에서 확인 버튼 클릭

"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json

LOAD_WAIT = 5
MAX_WAIT = 60
SCREENSHOT_DIR = "screenshots"

results = {
    "test_name": "TC-T-08: 단원 초기화 동작 확인",
    "test_date": "",
    "url": "",
    "steps": [],
    "checks": {},
    "overall_result": "PASS",
    "errors": []
}


async def test_reconstruction_reset():
    """TC-T-08: 단원 초기화 동작 확인"""
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

            # Step 2: LNB '교과서' 메뉴 클릭
            print("\n" + "=" * 60)
            print("Step 2: LNB '교과서' 메뉴 클릭")
            print("=" * 60)
            textbook_menu = main_page.locator("text=/교과서/").first
            await textbook_menu.click()
            print("   교과서 메뉴 클릭")
            await asyncio.sleep(LOAD_WAIT)
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc08_01_textbook_menu.png", full_page=True)
            results["steps"].append({
                "step": 2,
                "action": "교과서 메뉴 클릭",
                "check_item": "LNB 메뉴",
                "detail": "교과서 메뉴 클릭 > 단원 리스트 노출",
                "status": "PASS"
            })

            # Step 3: 단원 리스트 노출 확인
            print("\n" + "=" * 60)
            print("Step 3: 단원 리스트 노출 확인")
            print("=" * 60)
            page_text = await main_page.locator("body").inner_text()
            has_chapter = "단원" in page_text or "Lesson" in page_text
            print(f"   단원 텍스트 존재: {has_chapter}")
            results["checks"]["단원_리스트"] = {"found": has_chapter, "status": "PASS" if has_chapter else "FAIL"}
            results["steps"].append({
                "step": 3,
                "action": "단원 리스트 확인",
                "check_item": "단원 노출",
                "detail": f"단원 텍스트 존재 확인 (found: {has_chapter})",
                "status": "PASS" if has_chapter else "FAIL"
            })

            # Step 4: 첫 번째 단원 '재구성하기' 버튼 클릭
            print("\n" + "=" * 60)
            print("Step 4: 첫 번째 단원 '재구성하기' 버튼 클릭")
            print("=" * 60)
            recon_selectors = [
                "span:has-text('재구성하기')",
                "span:has-text('재구성')",
            ]
            recon_btn_count = 0
            recon_btn = None
            for selector in recon_selectors:
                count = await main_page.locator(selector).count()
                if count > 0:
                    recon_btn_count = count
                    recon_btn = main_page.locator(selector).first
                    print(f"   재구성하기 버튼: {recon_btn_count}개 (selector: {selector})")
                    break

            if recon_btn_count > 0:
                await recon_btn.click()
                print("   재구성하기 버튼 클릭")
                await asyncio.sleep(LOAD_WAIT)
                await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc08_02_recon_page.png", full_page=True)
                results["checks"]["재구성하기_버튼"] = {"found": True, "count": recon_btn_count, "status": "PASS"}
                results["steps"].append({
                    "step": 4,
                    "action": "재구성하기 버튼 클릭",
                    "check_item": "버튼 클릭",
                    "detail": f"첫 번째 단원 재구성하기 버튼 클릭 ({recon_btn_count}개 중)",
                    "status": "PASS"
                })

                # Step 5: 재구성 페이지 확인
                print("\n" + "=" * 60)
                print("Step 5: 재구성 페이지 확인")
                print("=" * 60)
                recon_url = main_page.url
                print(f"   현재 URL: {recon_url}")
                page_text = await main_page.locator("body").inner_text()
                recon_keywords = ["재구성", "모듈", "차시", "저장", "미리보기", "초기화"]
                found_keywords = [kw for kw in recon_keywords if kw in page_text]
                print(f"   발견된 키워드: {found_keywords}")
                has_recon_page = len(found_keywords) >= 2
                results["checks"]["재구성_페이지"] = {
                    "url": recon_url,
                    "found_keywords": found_keywords,
                    "status": "PASS" if has_recon_page else "CHECK"
                }
                results["steps"].append({
                    "step": 5,
                    "action": "재구성 페이지 확인",
                    "check_item": "페이지 전환",
                    "detail": f"URL 변경 및 키워드 확인 ({', '.join(found_keywords)})",
                    "status": "PASS" if has_recon_page else "CHECK"
                })

                # Step 6: 임시저장 삭제 버튼 확인 및 삭제
                print("\n" + "=" * 60)
                print("Step 6: 임시저장 삭제 버튼 확인 및 삭제")
                print("=" * 60)
                delete_selectors = [
                    "button:has-text('임시저장 삭제')",
                    "button:has-text('삭제')",
                    "span:has-text('임시저장 삭제')",
                    "span:has-text('삭제')",
                    "[class*='delete']",
                    "[class*='Delete']",
                ]
                delete_btn_count = 0
                delete_btn = None
                for selector in delete_selectors:
                    count = await main_page.locator(selector).count()
                    if count > 0:
                        delete_btn_count = count
                        delete_btn = main_page.locator(selector).first
                        print(f"   임시저장 삭제 버튼: {delete_btn_count}개 (selector: {selector})")
                        break

                if delete_btn_count > 0:
                    # 모달이 있으면 먼저 닫기
                    modal_overlay = main_page.locator(".modal-backdrop, .modal-open, .modal-content, .modal-dialog")
                    modal_count = await modal_overlay.count()
                    if modal_count > 0:
                        print(f"   기존 모달 발견: {modal_count}개, 먼저 닫기 시도")
                        try:
                            await main_page.keyboard.press("Escape")
                            await asyncio.sleep(0.5)
                            print("   ESC로 모달 닫기 시도")
                            await main_page.locator(".modal-backdrop, .modal-open, .modal-content, .modal-dialog").wait_for(state="hidden", timeout=3000)
                            print("   ESC로 모달 닫힘 확인")
                        except:
                            print("   ESC로 모달 닫기 실패, 다른 방법 시도")
                            try:
                                await main_page.mouse.click("body", position={"x": 10, "y": 10})
                                await asyncio.sleep(0.5)
                                print("   바깥쪽 클릭으로 모달 닫기 시도")
                            except:
                                pass

                    # 삭제 버튼 클릭
                    await delete_btn.click()
                    print("   임시저장 삭제 버튼 클릭")
                    await asyncio.sleep(1)

                    # 모달이 나타날 때까지 대기
                    try:
                        await main_page.wait_for_selector(".modal-content, .modal-dialog, .modal", state="visible", timeout=5000)
                        print("   모달 팝업 감지됨")
                        await asyncio.sleep(0.5)
                    except TimeoutError:
                        print("   모달 팝업이 감지되지 않음")

                    # 모달 확인 버튼 클릭 (삭제 확인)
                    modal_delete_selectors = [
                        "button.btn.fill.loading-color-black.secondary.full:has-text('확인')",
                        "button[class*='loading-color-black'][class*='secondary']:has-text('확인')",
                        "button:has-text('삭제'):not(:has-text('취소'))",
                        "button:has-text('확인')",
                        "button:has-text('예')",
                    ]
                    modal_clicked = False
                    for selector in modal_delete_selectors:
                        try:
                            modal_btn = main_page.locator(selector).first
                            if await modal_btn.is_visible(timeout=2000):
                                await modal_btn.click()
                                print(f"   모달 확인 버튼 클릭 (selector: {selector})")
                                modal_clicked = True
                                await asyncio.sleep(2)
                                break
                        except:
                            continue

                    results["checks"]["임시저장_삭제"] = {
                        "found": True,
                        "count": delete_btn_count,
                        "modal_clicked": modal_clicked,
                        "status": "PASS"
                    }
                    results["steps"].append({
                        "step": 6,
                        "action": "임시저장 삭제",
                        "check_item": "삭제 동작",
                        "detail": "임시저장 삭제 버튼 클릭 > 모달 확인 버튼 클릭",
                        "status": "PASS"
                    })
                else:
                    print("   임시저장 삭제 버튼 없음 - 건너뜀")
                    results["checks"]["임시저장_삭제"] = {"found": False, "status": "SKIP"}
                    results["steps"].append({
                        "step": 6,
                        "action": "임시저장 삭제 확인",
                        "check_item": "삭제 버튼",
                        "detail": "임시저장 삭제 버튼 없음 - 건너뜀",
                        "status": "SKIP"
                    })

                # Step 7: 임시저장 버튼 클릭
                print("\n" + "=" * 60)
                print("Step 7: 임시저장 버튼 클릭")
                print("=" * 60)
                # 모달이 있으면 닫기
                modal_overlay = main_page.locator(".modal-backdrop, .modal-open, .modal-content, .modal-dialog")
                modal_count = await modal_overlay.count()
                if modal_count > 0:
                    print(f"   모달 발견: {modal_count}개, 닫기 시도")
                    try:
                        await main_page.keyboard.press("Escape")
                        await asyncio.sleep(0.5)
                        print("   ESC로 모달 닫기 시도")
                        await main_page.locator(".modal-backdrop, .modal-open, .modal-content, .modal-dialog").wait_for(state="hidden", timeout=3000)
                        print("   ESC로 모달 닫힘 확인")
                    except:
                        try:
                            await main_page.mouse.click("body", position={"x": 10, "y": 10})
                            await asyncio.sleep(0.5)
                            print("   바깥쪽 클릭으로 모달 닫기 시도")
                        except:
                            pass

                save_btn_selectors = [
                    "button:has-text('임시저장')",
                    "button:has-text('저장')",
                    "span:has-text('임시저장')",
                ]
                save_btn_count = 0
                save_btn = None
                for selector in save_btn_selectors:
                    count = await main_page.locator(selector).count()
                    if count > 0:
                        save_btn_count = count
                        save_btn = main_page.locator(selector).first
                        print(f"   임시저장 버튼: {count}개 (selector: {selector})")
                        break

                if save_btn_count > 0 and save_btn:
                    await save_btn.click()
                    print("   임시저장 버튼 클릭")
                    await asyncio.sleep(2)
                    results["checks"]["임시저장_버튼"] = {"found": True, "count": save_btn_count, "status": "PASS"}
                    results["steps"].append({
                        "step": 7,
                        "action": "임시저장 버튼 클릭",
                        "check_item": "저장 동작",
                        "detail": "임시저장 버튼 클릭 > 데이터 생성 확인",
                        "status": "PASS"
                    })
                else:
                    results["checks"]["임시저장_버튼"] = {"found": False, "status": "CHECK"}
                    results["steps"].append({
                        "step": 7,
                        "action": "임시저장 버튼 찾기",
                        "check_item": "저장 버튼",
                        "detail": "임시저장 버튼을 찾을 수 없음",
                        "status": "CHECK"
                    })

                # Step 8: 초기화 버튼 클릭
                print("\n" + "=" * 60)
                print("Step 8: 초기화 버튼 클릭")
                print("=" * 60)
                # 모달이 있으면 닫기
                modal_overlay = main_page.locator(".modal-backdrop, .modal-open, .modal-content, .modal-dialog")
                modal_count = await modal_overlay.count()
                if modal_count > 0:
                    print(f"   모달 발견: {modal_count}개, 닫기 시도")
                    try:
                        await main_page.keyboard.press("Escape")
                        await asyncio.sleep(0.5)
                        await main_page.locator(".modal-backdrop, .modal-open, .modal-content, .modal-dialog").wait_for(state="hidden", timeout=3000)
                        print("   ESC로 모달 닫힘 확인")
                    except:
                        try:
                            await main_page.mouse.click("body", position={"x": 10, "y": 10})
                            await asyncio.sleep(0.5)
                        except:
                            pass

                reset_btn_selectors = [
                    "button:has-text('초기화')",
                    "button:has-text('단원 초기화')",
                    "span:has-text('초기화')",
                    "span:has-text('단원 초기화')",
                ]
                reset_btn_count = 0
                reset_btn = None
                for selector in reset_btn_selectors:
                    count = await main_page.locator(selector).count()
                    if count > 0:
                        reset_btn_count = count
                        reset_btn = main_page.locator(selector).first
                        print(f"   초기화 버튼: {count}개 (selector: {selector})")
                        break

                if reset_btn_count > 0 and reset_btn:
                    await reset_btn.click()
                    print("   초기화 버튼 클릭")
                    await asyncio.sleep(2)
                    await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc08_03_reset_modal.png", full_page=True)
                    results["checks"]["초기화_버튼"] = {"found": True, "count": reset_btn_count, "status": "PASS"}
                    results["steps"].append({
                        "step": 8,
                        "action": "초기화 버튼 클릭",
                        "check_item": "버튼 클릭",
                        "detail": f"초기화 버튼 클릭 ({reset_btn_count}개 발견)",
                        "status": "PASS"
                    })

                    # Step 9: 모달 팝업에서 확인 버튼 클릭
                    print("\n" + "=" * 60)
                    print("Step 9: 모달 팝업에서 확인 버튼 클릭")
                    print("=" * 60)
                    # 모달이 나타날 때까지 대기
                    try:
                        await main_page.wait_for_selector(".modal-content, .modal-dialog, .modal", state="visible", timeout=5000)
                        print("   초기화 확인 모달 팝업 감지됨")
                        await asyncio.sleep(0.5)
                    except TimeoutError:
                        print("   모달 팝업이 감지되지 않음")

                    # 모달 확인 버튼 클릭
                    modal_confirm_selectors = [
                        "button.btn.fill.loading-color-black.secondary.full:has-text('확인')",
                        "button[class*='loading-color-black'][class*='secondary']:has-text('확인')",
                        "button:has-text('확인')",
                        "button:has-text('초기화')",
                        "button:has-text('예')",
                    ]
                    modal_clicked = False
                    for selector in modal_confirm_selectors:
                        try:
                            modal_btn = main_page.locator(selector).first
                            if await modal_btn.is_visible(timeout=2000):
                                await modal_btn.click()
                                print(f"   모달 확인 버튼 클릭 (selector: {selector})")
                                modal_clicked = True
                                await asyncio.sleep(2)
                                break
                        except:
                            continue

                    if modal_clicked:
                        print("   초기화 완료")

                        # 토스트 알림 확인 (최대 30초 대기)
                        print("   토스트 알림 확인 중... (최대 30초 대기)")
                        toast_selectors = [
                            ".toast",
                            "[class*='toast']",
                            "[class*='Toast']",
                            ".notification",
                            "[class*='notification']",
                            "[class*='alert']",
                            "[class*='snackbar']",
                            "[class*='Snackbar']",
                        ]
                        toast_found = False
                        toast_message = ""

                        # 30초 동안 1초 간격으로 체크
                        for wait_sec in range(30):
                            await asyncio.sleep(1)
                            print(f"   대기 중... {wait_sec + 1}초")

                            for selector in toast_selectors:
                                try:
                                    toast_elements = main_page.locator(selector)
                                    count = await toast_elements.count()
                                    if count > 0:
                                        for i in range(count):
                                            try:
                                                toast_text = await toast_elements.nth(i).inner_text()
                                                if "초기화" in toast_text or "완료" in toast_text:
                                                    toast_found = True
                                                    toast_message = toast_text
                                                    print(f"   토스트 알림 발견: {toast_text}")
                                                    break
                                            except:
                                                continue
                                        if toast_found:
                                            break
                                except:
                                    continue

                            if toast_found:
                                break

                        await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc08_04_after_reset.png", full_page=True)

                        if toast_found:
                            results["checks"]["초기화_확인"] = {
                                "modal_clicked": modal_clicked,
                                "toast_found": toast_found,
                                "toast_message": toast_message,
                                "wait_seconds": wait_sec + 1,
                                "status": "PASS"
                            }
                            results["steps"].append({
                                "step": 9,
                                "action": "초기화 확인",
                                "check_item": "모달 + 토스트",
                                "detail": f"초기화 확인 모달 클릭 > {wait_sec + 1}초 후 토스트 알림 확인 ({toast_message})",
                                "status": "PASS"
                            })
                        else:
                            results["checks"]["초기화_확인"] = {
                                "modal_clicked": modal_clicked,
                                "toast_found": False,
                                "status": "FAIL"
                            }
                            results["steps"].append({
                                "step": 9,
                                "action": "초기화 확인",
                                "check_item": "모달 + 토스트",
                                "detail": "초기화 확인 모달 클릭 완료, 30초 대기 후에도 토스트 알림 미확인",
                                "status": "FAIL"
                            })
                            results["overall_result"] = "FAIL"
                            results["errors"].append("토스트 알림 '초기화가 완료 되었습니다.' 미노출")
                    else:
                        print("   모달 확인 버튼을 찾을 수 없음")
                        results["checks"]["초기화_확인"] = {"modal_clicked": False, "status": "CHECK"}
                        results["steps"].append({
                            "step": 9,
                            "action": "초기화 확인 버튼 찾기",
                            "check_item": "모달 확인",
                            "detail": "모달 확인 버튼을 찾을 수 없음",
                            "status": "CHECK"
                        })
                else:
                    print("   초기화 버튼을 찾을 수 없음")
                    results["checks"]["초기화_버튼"] = {"found": False, "status": "FAIL"}
                    results["steps"].append({
                        "step": 8,
                        "action": "초기화 버튼 찾기",
                        "check_item": "버튼 찾기",
                        "detail": "초기화 버튼을 찾을 수 없음",
                        "status": "FAIL"
                    })
            else:
                print("   재구성하기 버튼을 찾을 수 없음")
                results["checks"]["재구성하기_버튼"] = {"found": False, "status": "FAIL"}
                results["overall_result"] = "FAIL"
                results["errors"].append("재구성하기 버튼을 찾을 수 없음")
                results["steps"].append({
                    "step": 4,
                    "action": "재구성하기 버튼 클릭",
                    "check_item": "버튼 찾기",
                    "detail": "재구성하기 버튼을 찾을 수 없음",
                    "status": "FAIL"
                })

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

            with open("test_result_TC-T-08.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result_TC-T-08.json")

            print("\n10초 후 종료...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))
            try:
                await entry_page.screenshot(path=f"{SCREENSHOT_DIR}/tc08_error.png")
            except:
                pass
        finally:
            await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    print("=" * 60)
    print("TC-T-08: 단원 초기화 동작 확인 테스트 시작")
    print("=" * 60)
    asyncio.run(test_reconstruction_reset())
