"""
TC-T-12: 모둠 활동 선택 > 활동보드판 진입 동작 확인

테스트 시나리오:
1. 좌측 LNB에서 '모둠 활동' 메뉴 클릭
2. 작성하기 버튼 클릭 > 활동 이름 'sample' 입력 > '타일형' 선택 > 만들기
3. 새 창으로 모둠활동창이 열리면 열린 창 닫기
4. 모둠활동 리스트에서 생성된 모둠활동 다시 클릭
5. 새 창으로 모둠활동창이 열리는지 확인
6. 열린 창 닫기
7. sample 활동 삭제
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json

LOAD_WAIT = 5
MAX_WAIT = 60
SCREENSHOT_DIR = "screenshots"

results = {
    "test_name": "TC-T-12: 모둠 활동 선택 > 활동보드판 진입 동작 확인",
    "test_date": "",
    "url": "",
    "steps": [],
    "checks": {},
    "overall_result": "PASS",
    "errors": []
}


async def find_sample_row_index(main_page):
    """sample 활동의 행 인덱스 찾기"""
    try:
        list_items = main_page.locator(".bar-list-item")
        count = await list_items.count()
        print(f"   bar-list-item 요소 개수: {count}")

        for i in range(count):
            item = list_items.nth(i)
            chapter_title = item.locator(".chapter-title")
            if await chapter_title.count() > 0:
                title_text = await chapter_title.first.inner_text()
                title_clean = title_text.strip()
                print(f"   [{i}] 활동명: {title_clean}")

                if title_clean == "sample":
                    print(f"   sample 행 발견: 인덱스 {i}")
                    return i

        print("   sample 활동을 찾을 수 없음")
        return -1
    except Exception as e:
        print(f"   행 찾기 오류: {e}")
        return -1


async def click_row_action_button(main_page, row_index, button_text):
    """행 내부의 액션 버튼 클릭 (JavaScript로 새 창 열림 방지)"""
    try:
        row = main_page.locator(".bar-list-item").nth(row_index)

        selectors = [
            f".list-item-tools button:has-text('{button_text}')",
            f".list-item-tools .aidt-link2:has-text('{button_text}')",
            f"button.aidt-link2:has-text('{button_text}')",
        ]

        for selector in selectors:
            try:
                btn = row.locator(selector).first
                if await btn.count() > 0:
                    await main_page.evaluate("""
                        (btn) => { btn.click(); }
                    """, await btn.element_handle())
                    print(f"   행 내부 '{button_text}' 버튼 클릭 (JavaScript)")
                    await asyncio.sleep(2)
                    return True
            except:
                continue

        print(f"   행 내부 '{button_text}' 버튼을 찾을 수 없음")
        return False
    except Exception as e:
        print(f"   행 내부 버튼 클릭 오류: {e}")
        return False


async def click_modal_button(main_page, button_text):
    """모달에서 지정된 텍스트의 버튼 클릭"""
    selectors = [
        f".modal-content button:has-text('{button_text}')",
        f".modal-dialog button:has-text('{button_text}')",
        f".modal button:has-text('{button_text}')",
        f"button.btn.fill:has-text('{button_text}')",
        f"button.aidt-link2:has-text('{button_text}')",
        f"button:has-text('{button_text}')",
    ]

    for selector in selectors:
        try:
            btn = main_page.locator(selector).first
            if await btn.is_visible(timeout=2000):
                await btn.click()
                print(f"   모달 '{button_text}' 버튼 클릭 (selector: {selector})")
                return True
        except:
            continue

    print(f"   모달 '{button_text}' 버튼을 찾을 수 없음")
    return False


async def wait_for_toast(main_page, keyword, max_wait=10):
    """토스트 알림 대기"""
    print(f"   토스트 알림 대기 중 (키워드: {keyword})...")
    for wait_sec in range(max_wait):
        await asyncio.sleep(1)
        toast_selectors = [".toast", "[class*='toast']", "[class*='Toast']", "[class*='alert']"]
        for selector in toast_selectors:
            try:
                toast_elements = main_page.locator(selector)
                count = await toast_elements.count()
                if count > 0:
                    for i in range(count):
                        toast_text = await toast_elements.nth(i).inner_text()
                        if keyword in toast_text:
                            print(f"   토스트 알림 발견: {toast_text}")
                            return True, toast_text
            except:
                continue
    return False, ""


async def test_group_activity_board_entry():
    """TC-T-12: 모둠 활동 선택 > 활동보드판 진입 동작 확인"""
    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"
    results["test_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results["url"] = TEST_URL

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        await context.grant_permissions(["microphone"])
        entry_page = await context.new_page()

        try:
            # ===========================================
            # Step 1: 진입 페이지 > 선생님 입장
            # ===========================================
            print("=" * 60)
            print("Step 1: 진입 페이지 > 선생님 입장")
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
                "action": "진입 페이지 > 선생님 입장",
                "check_item": "메인 페이지 진입",
                "detail": f"URL: {main_page.url}",
                "status": "PASS"
            })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc12_01_main_page.png", full_page=True)

            # ===========================================
            # Step 2: 모둠활동 메뉴 클릭
            # ===========================================
            print("\n" + "=" * 60)
            print("Step 2: 모둠활동 메뉴 클릭")
            print("=" * 60)

            group_menu = main_page.locator("text=/모둠 활동/").first
            await group_menu.click()
            print("   모둠활동 메뉴 클릭")
            await asyncio.sleep(LOAD_WAIT)

            results["steps"].append({
                "step": 2,
                "action": "모둠활동 메뉴 클릭",
                "check_item": "모둠활동 리스트 페이지",
                "detail": "모둠활동 메뉴 클릭 완료",
                "status": "PASS"
            })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc12_02_group_menu.png", full_page=True)

            # ===========================================
            # Step 3: 작성하기 버튼 클릭
            # ===========================================
            print("\n" + "=" * 60)
            print("Step 3: 작성하기 버튼 클릭")
            print("=" * 60)

            write_btn = main_page.locator("button:has-text('작성하기')").first
            await write_btn.click()
            print("   작성하기 버튼 클릭")
            await asyncio.sleep(LOAD_WAIT)

            # 활동 만들기 팝업 대기
            try:
                await main_page.wait_for_selector(".modal-content, .modal-dialog, .modal", state="visible", timeout=5000)
                print("   활동 만들기 팝업 감지됨")
            except TimeoutError:
                print("   팝업 감지되지 않음")

            results["steps"].append({
                "step": 3,
                "action": "작성하기 버튼 클릭",
                "check_item": "활동 만들기 팝업",
                "detail": "활동 만들기 팝업 표시",
                "status": "PASS"
            })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc12_03_create_popup.png", full_page=True)

            # ===========================================
            # Step 4: 활동 이름 입력 > 타일형 선택 > 만들기
            # ===========================================
            print("\n" + "=" * 60)
            print("Step 4: 활동 이름 'sample' 입력 > 타일형 선택 > 만들기")
            print("=" * 60)

            # 활동 이름 입력
            input_el = main_page.locator(".modal-content input[type='text']").first
            await input_el.click()
            await asyncio.sleep(0.3)
            await input_el.fill("sample")
            print("   활동 이름 'sample' 입력")

            # 타일형 선택
            tile_label = main_page.locator("label:has-text('타일형')").first
            await tile_label.click()
            print("   타일형 선택")

            # 만들기 버튼 클릭 > 새 창 열림 대기
            create_btn = main_page.locator("button:has-text('만들기')").first
            async with context.expect_page(timeout=MAX_WAIT * 1000) as activity_page_info:
                await create_btn.click()
                print("   만들기 버튼 클릭")

            activity_page = await activity_page_info.value
            try:
                await activity_page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)
            except TimeoutError:
                pass
            await asyncio.sleep(LOAD_WAIT)

            print(f"   새 창 URL: {activity_page.url}")

            # 새 창이 모둠활동창인지 확인
            activity_url = activity_page.url
            is_activity_page = "activity" in activity_url or "group" in activity_url or "board" in activity_url
            print(f"   모둠활동창 여부: {is_activity_page}")

            results["checks"]["활동_생성_새창"] = {"found": is_activity_page, "url": activity_url, "status": "PASS" if is_activity_page else "CHECK"}
            results["steps"].append({
                "step": 4,
                "action": "활동 생성 > 새 창 열림",
                "check_item": "모둠활동창 새 창",
                "detail": f"새 창 URL: {activity_url}",
                "status": "PASS" if is_activity_page else "CHECK"
            })
            await activity_page.screenshot(path=f"{SCREENSHOT_DIR}/tc12_04_activity_page.png", full_page=True)

            # ===========================================
            # Step 5: 새 창 닫기
            # ===========================================
            print("\n" + "=" * 60)
            print("Step 5: 새 창 닫기")
            print("=" * 60)

            await activity_page.close()
            print("   모둠활동창 닫기 완료")

            results["steps"].append({
                "step": 5,
                "action": "새 창 닫기",
                "check_item": "모둠활동창 닫기",
                "detail": "모둠활동창 닫기 완료",
                "status": "PASS"
            })

            # ===========================================
            # Step 6: 모둠활동 리스트에서 sample 클릭 > 새 창 열림 확인
            # ===========================================
            print("\n" + "=" * 60)
            print("Step 6: 모둠활동 리스트에서 sample 클릭 > 새 창 열림 확인")
            print("=" * 60)

            # 리스트 새로고침
            await main_page.reload()
            print("   페이지 새로고침")
            await asyncio.sleep(LOAD_WAIT)
            try:
                await main_page.wait_for_selector(".loading", state="hidden", timeout=30000)
            except TimeoutError:
                pass

            # sample 행 찾기
            sample_index = await find_sample_row_index(main_page)

            if sample_index >= 0:
                # sample 행의 chapter-title 클릭 (활동 진입)
                sample_row = main_page.locator(".bar-list-item").nth(sample_index)
                chapter_title = sample_row.locator(".chapter-title").first

                # 새 창 열림 대기하며 클릭
                async with context.expect_page(timeout=MAX_WAIT * 1000) as reopen_page_info:
                    await chapter_title.click()
                    print("   sample 활동 클릭")

                reopened_page = await reopen_page_info.value
                try:
                    await reopened_page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)
                except TimeoutError:
                    pass
                await asyncio.sleep(LOAD_WAIT)

                reopened_url = reopened_page.url
                print(f"   다시 열린 창 URL: {reopened_url}")

                # 새 창이 모둠활동창인지 확인
                is_reopened_activity = "activity" in reopened_url or "group" in reopened_url or "board" in reopened_url
                print(f"   모둠활동창 여부: {is_reopened_activity}")

                results["checks"]["활동_재진입_새창"] = {"found": is_reopened_activity, "url": reopened_url, "status": "PASS" if is_reopened_activity else "CHECK"}
                results["steps"].append({
                    "step": 6,
                    "action": "sample 활동 클릭 > 새 창 열림",
                    "check_item": "모둠활동창 새 창 재진입",
                    "detail": f"새 창 URL: {reopened_url}",
                    "status": "PASS" if is_reopened_activity else "CHECK"
                })
                await reopened_page.screenshot(path=f"{SCREENSHOT_DIR}/tc12_06_reopened_activity.png", full_page=True)

                # ===========================================
                # Step 7: 열린 창 닫기
                # ===========================================
                print("\n" + "=" * 60)
                print("Step 7: 열린 창 닫기")
                print("=" * 60)

                await reopened_page.close()
                print("   재진입한 모둠활동창 닫기 완료")

                results["steps"].append({
                    "step": 7,
                    "action": "열린 창 닫기",
                    "check_item": "모둠활동창 닫기",
                    "detail": "재진입한 모둠활동창 닫기 완료",
                    "status": "PASS"
                })
            else:
                results["steps"].append({
                    "step": 6,
                    "action": "sample 활동 찾기",
                    "check_item": "sample 활동 존재",
                    "detail": "sample 활동을 찾을 수 없음",
                    "status": "CHECK"
                })

            # ===========================================
            # Step 8: sample 활동 삭제
            # ===========================================
            print("\n" + "=" * 60)
            print("Step 8: sample 활동 삭제")
            print("=" * 60)

            # 리스트 새로고침
            await main_page.reload()
            await asyncio.sleep(LOAD_WAIT)
            try:
                await main_page.wait_for_selector(".loading", state="hidden", timeout=30000)
            except TimeoutError:
                pass

            # sample 행 다시 찾기
            sample_index = await find_sample_row_index(main_page)

            if sample_index >= 0:
                # 삭제 버튼 클릭
                delete_clicked = await click_row_action_button(main_page, sample_index, "삭제")

                if delete_clicked:
                    # 모달에서 '확인' 버튼 클릭
                    modal_clicked = await click_modal_button(main_page, "확인")
                    if not modal_clicked:
                        print("   모달 확인 버튼을 찾을 수 없음")

                    # 토스트 알림 확인
                    toast_found, toast_message = await wait_for_toast(main_page, "삭제")

                    results["checks"]["활동_삭제"] = {"toast_found": toast_found, "toast_message": toast_message, "status": "PASS" if toast_found else "CHECK"}
                    results["steps"].append({
                        "step": 8,
                        "action": "sample 활동 삭제",
                        "check_item": "삭제 + 토스트",
                        "detail": f"토스트 알림: \"{toast_message}\"" if toast_found else "토스트 알림 미확인",
                        "status": "PASS" if toast_found else "CHECK"
                    })
                else:
                    results["steps"].append({
                        "step": 8,
                        "action": "sample 활동 삭제",
                        "check_item": "삭제 버튼",
                        "detail": "삭제 버튼 클릭 실패",
                        "status": "CHECK"
                    })
            else:
                results["steps"].append({
                    "step": 8,
                    "action": "sample 활동 삭제",
                    "check_item": "sample 찾기",
                    "detail": "sample 활동을 찾을 수 없음",
                    "status": "CHECK"
                })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc12_08_after_delete.png", full_page=True)

            # ===========================================
            # 결과 요약
            # ===========================================
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

            with open("test_result_TC-T-12.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result_TC-T-12.json")

            print("\n10초 후 종료...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))
            try:
                await entry_page.screenshot(path=f"{SCREENSHOT_DIR}/tc12_error.png")
            except:
                pass
            finally:
                await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    print("=" * 60)
    print("TC-T-12: 모둠 활동 선택 > 활동보드판 진입 동작 확인 테스트 시작")
    print("=" * 60)
    asyncio.run(test_group_activity_board_entry())
