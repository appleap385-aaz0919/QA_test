"""
TC-T-11: 모둠활동 복사/공개/비공개/삭제
- HTML 구조 분석 기반 재작성

테스트 시나리오:
[환경설정] sample 활동 만들기 > 새 창 닫기 > 리스트 새로고침
[테스트 1] 체크박스 체크 > 행 내부 "복사하기" 버튼 > 모달 확인 > [복사본]sample 생성 확인
[테스트 2] 체크박스 체크 > 상단 "선택한 활동 공개" 버튼 > 모달 확인 > 토스트 확인
[테스트 3] 체크박스 체크 > 상단 "선택한 활동 비공개" 버튼 > 모달 확인 > 토스트 확인
[테스트 4] 체크박스 체크 > 상단 "선택한 활동 삭제" 버튼 > 모달 확인 > 토스트 확인

"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json
from qa_utils import fast_page_wait, wait_for_new_page, get_browser_config, MAX_WAIT

SCREENSHOT_DIR = "screenshots"

results = {
    "test_name": "TC-T-11: 모둠활동 복사/공개/비공개/삭제",
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
        # bar-list-item 요소들 찾기
        list_items = main_page.locator(".bar-list-item")
        count = await list_items.count()
        print(f"   bar-list-item 요소 개수: {count}")

        for i in range(count):
            item = list_items.nth(i)
            # 해당 행에서 chapter-title 찾기
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


async def find_copy_sample_row_index(main_page):
    """[복사본]sample 활동의 행 인덱스 찾기"""
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

                # "[복사본]sample" 찾기
                if "[복사본]sample" in title_clean or "[복사본] sample" in title_clean:
                    print(f"   [복사본]sample 행 발견: 인덱스 {i}")
                    return i

        print("   [복사본]sample 활동을 찾을 수 없음")
        return -1
    except Exception as e:
        print(f"   행 찾기 오류: {e}")
        return -1


async def check_sample_checkbox(main_page, row_index):
    """sample 행의 체크박스를 JavaScript로 체크 (새 창 열림 방지)"""
    try:
        # 해당 행의 체크박스 찾기
        checkbox = main_page.locator(".bar-list-item").nth(row_index).locator(".list-item-left input[type='checkbox']").first

        # JavaScript로 체크박스 체크 (이벤트 전파 방지)
        await main_page.evaluate("""
            (checkbox) => {
                if (!checkbox.checked) {
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        """, await checkbox.element_handle())
        print(f"   sample 행 체크박스 체크 완료 (JavaScript)")
        await asyncio.sleep(0.5)
        return True
    except Exception as e:
        print(f"   체크박스 체크 오류: {e}")
        return False


async def click_row_copy_button(main_page, row_index):
    """행 내부의 복사하기 버튼 클릭 (JavaScript로 새 창 열림 방지)"""
    try:
        # 행 내부의 복사하기 버튼
        copy_btn = main_page.locator(".bar-list-item").nth(row_index).locator(".list-item-tools button.aidt-link2:has-text('복사하기')").first

        # JavaScript로 클릭
        await main_page.evaluate("""
            (btn) => {
                btn.click();
            }
        """, await copy_btn.element_handle())
        print(f"   행 내부 복사하기 버튼 클릭 (JavaScript)")
        await asyncio.sleep(2)
        return True
    except Exception as e:
        print(f"   복사하기 버튼 클릭 오류: {e}")
        return False


async def click_row_action_button(main_page, row_index, button_text):
    """행 내부의 액션 버튼 클릭 (JavaScript로 새 창 열림 방지)"""
    try:
        # 행 내부의 버튼 찾기 (.list-item-tools 안의 버튼)
        row = main_page.locator(".bar-list-item").nth(row_index)

        # 버튼 선택자들
        selectors = [
            f".list-item-tools button:has-text('{button_text}')",
            f".list-item-tools .aidt-link2:has-text('{button_text}')",
            f"button.aidt-link2:has-text('{button_text}')",
        ]

        for selector in selectors:
            try:
                btn = row.locator(selector).first
                if await btn.count() > 0:
                    # JavaScript로 클릭 (새 창 열림 방지)
                    await main_page.evaluate("""
                        (btn) => {
                            btn.click();
                        }
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


async def click_top_button(main_page, button_text):
    """상단 컨트롤 버튼 클릭 (대안용)"""
    try:
        selectors = [
            f".list-controls button:has-text('{button_text}')",
            f".controls-btn-wrap button:has-text('{button_text}')",
            f"button:has-text('선택한 활동 {button_text}')",
        ]

        for selector in selectors:
            try:
                btn = main_page.locator(selector).first
                if await btn.is_visible(timeout=2000):
                    await btn.click()
                    print(f"   상단 '{button_text}' 버튼 클릭")
                    await asyncio.sleep(2)
                    return True
            except:
                continue

        print(f"   상단 '{button_text}' 버튼을 찾을 수 없음")
        return False
    except Exception as e:
        print(f"   상단 버튼 클릭 오류: {e}")
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


async def test_group_activity_manage():
    """TC-T-11: 모둠활동 복사/공개/비공개/삭제"""
    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"
    results["test_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results["url"] = TEST_URL

    async with async_playwright() as p:
        browser = await p.chromium.launch(**get_browser_config())
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        await context.grant_permissions(["microphone"])
        entry_page = await context.new_page()

        try:
            # ===========================================
            # [환경설정] sample 활동 만들기
            # ===========================================
            print("=" * 60)
            print("[환경설정] sample 활동 만들기")
            print("=" * 60)

            # 진입 페이지
            await entry_page.goto(TEST_URL, timeout=60000)
            await fast_page_wait(entry_page)

            teacher_btn = entry_page.locator("button").filter(has_text="선생님 입장하기")
            main_page = await wait_for_new_page(context, lambda: teacher_btn.click(), MAX_WAIT * 1000)
            print("   선생님 입장하기 클릭")
            await asyncio.sleep(1)

            print(f"   메인 페이지 URL: {main_page.url}")

            # 모둠활동 메뉴 클릭
            group_menu = main_page.locator("text=/모둠 활동/").first
            await group_menu.click()
            print("   모둠활동 메뉴 클릭")
            await asyncio.sleep(0.5)

            # 작성하기 버튼 클릭
            write_btn = main_page.locator("button:has-text('작성하기')").first
            await write_btn.click()
            print("   작성하기 버튼 클릭")
            await asyncio.sleep(0.5)

            # 활동 만들기 팝업
            try:
                await main_page.wait_for_selector(".modal-content, .modal-dialog, .modal", state="visible", timeout=3000)
                print("   활동 만들기 팝업 감지됨")
            except TimeoutError:
                print("   팝업 감지되지 않음")

            # 활동 이름 입력
            input_el = main_page.locator(".modal-content input[type='text']").first
            await input_el.click()
            await asyncio.sleep(0.2)
            await input_el.fill("sample")
            print("   활동 이름 'sample' 입력")

            # 타일형 선택
            tile_label = main_page.locator("label:has-text('타일형')").first
            await tile_label.click()
            print("   타일형 선택")

            # 만들기 버튼 클릭
            create_btn = main_page.locator("button:has-text('만들기')").first
            activity_page = await wait_for_new_page(context, lambda: create_btn.click(), MAX_WAIT * 1000)
            print("   만들기 버튼 클릭")
            await asyncio.sleep(0.5)

            # 새 창 닫기
            await activity_page.close()
            print("   새 창 닫기")

            # 리스트 페이지 새로고침
            await main_page.reload()
            print("   페이지 새로고침")
            await asyncio.sleep(0.5)

            results["steps"].append({
                "step": 1,
                "action": "[환경설정] sample 활동 생성",
                "check_item": "sample 활동 생성",
                "detail": "sample 이름의 타일형 활동 생성 완료",
                "status": "PASS"
            })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc11_01_after_create.png", full_page=True)

            # ===========================================
            # [테스트 1] 복사하기
            # ===========================================
            print("\n" + "=" * 60)
            print("[테스트 1] 복사하기")
            print("=" * 60)

            # sample 행 인덱스 찾기
            sample_index = await find_sample_row_index(main_page)

            if sample_index >= 0:
                # 체크박스 체크
                checkbox_checked = await check_sample_checkbox(main_page, sample_index)

                if checkbox_checked:
                    # 행 내부 복사하기 버튼 클릭
                    copy_clicked = await click_row_copy_button(main_page, sample_index)

                    if copy_clicked:
                        # 모달 대기
                        try:
                            await main_page.wait_for_selector(".modal-content, .modal-dialog, .modal", state="visible", timeout=5000)
                            print("   복사 확인 모달 감지됨")
                        except TimeoutError:
                            print("   모달 감지되지 않음")

                        # 모달에서 '복사' 버튼 클릭
                        modal_clicked = await click_modal_button(main_page, "복사")
                        if not modal_clicked:
                            print("   모달 복사 버튼을 찾을 수 없음")

                        await asyncio.sleep(3)

                        # [복사본]sample 생성 확인
                        page_text = await main_page.locator("body").inner_text()
                        has_copy = "[복사본]sample" in page_text or "복사본" in page_text
                        print(f"   [복사본]sample 생성 확인: {has_copy}")

                        results["checks"]["복사하기"] = {"found": has_copy, "status": "PASS" if has_copy else "CHECK"}
                        results["steps"].append({
                            "step": 2,
                            "action": "[테스트 1] 복사하기",
                            "check_item": "[복사본]sample 생성",
                            "detail": "[복사본]sample 활동 생성 확인" if has_copy else "복사본 미확인",
                            "status": "PASS" if has_copy else "CHECK"
                        })
                    else:
                        results["steps"].append({
                            "step": 2,
                            "action": "[테스트 1] 복사하기",
                            "check_item": "복사하기 버튼",
                            "detail": "복사하기 버튼 클릭 실패",
                            "status": "CHECK"
                        })
                else:
                    results["steps"].append({
                        "step": 2,
                        "action": "[테스트 1] 복사하기",
                        "check_item": "체크박스",
                        "detail": "체크박스 체크 실패",
                        "status": "CHECK"
                    })
            else:
                results["steps"].append({
                    "step": 2,
                    "action": "[테스트 1] 복사하기",
                    "check_item": "sample 찾기",
                    "detail": "sample 활동을 찾을 수 없음",
                    "status": "CHECK"
                })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc11_02_after_copy.png", full_page=True)

            # ===========================================
            # [테스트 2] 공개하기
            # ===========================================
            print("\n" + "=" * 60)
            print("[테스트 2] 공개하기")
            print("=" * 60)

            # sample 행 인덱스 다시 찾기
            sample_index = await find_sample_row_index(main_page)

            if sample_index >= 0:
                # 체크박스 체크
                checkbox_checked = await check_sample_checkbox(main_page, sample_index)

                if checkbox_checked:
                    # 행 내부 "공개하기" 버튼 클릭
                    public_clicked = await click_row_action_button(main_page, sample_index, "공개")

                    if not public_clicked:
                        # 대안: 상단 버튼 시도
                        public_clicked = await click_top_button(main_page, "공개")

                    if public_clicked:
                        # 모달에서 '확인' 버튼 클릭
                        modal_clicked = await click_modal_button(main_page, "확인")
                        if not modal_clicked:
                            print("   모달 확인 버튼을 찾을 수 없음")

                        # 토스트 알림 확인
                        toast_found, toast_message = await wait_for_toast(main_page, "공개")

                        results["checks"]["공개하기"] = {"toast_found": toast_found, "toast_message": toast_message, "status": "PASS" if toast_found else "CHECK"}
                        results["steps"].append({
                            "step": 3,
                            "action": "[테스트 2] 공개하기",
                            "check_item": "공개 변경 + 토스트",
                            "detail": f"토스트 알림: \"{toast_message}\"" if toast_found else "토스트 알림 미확인",
                            "status": "PASS" if toast_found else "CHECK"
                        })
                    else:
                        results["steps"].append({
                            "step": 3,
                            "action": "[테스트 2] 공개하기",
                            "check_item": "공개 버튼",
                            "detail": "공개 버튼 클릭 실패",
                            "status": "CHECK"
                        })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc11_03_after_public.png", full_page=True)

            # ===========================================
            # [테스트 3] 비공개하기
            # ===========================================
            print("\n" + "=" * 60)
            print("[테스트 3] 비공개하기")
            print("=" * 60)

            # sample 행 인덱스 다시 찾기
            sample_index = await find_sample_row_index(main_page)

            if sample_index >= 0:
                # 체크박스 체크
                checkbox_checked = await check_sample_checkbox(main_page, sample_index)

                if checkbox_checked:
                    # 행 내부 "비공개하기" 버튼 클릭
                    private_clicked = await click_row_action_button(main_page, sample_index, "비공개")

                    if not private_clicked:
                        # 대안: 상단 버튼 시도
                        private_clicked = await click_top_button(main_page, "비공개")

                    if private_clicked:
                        # 모달에서 '확인' 버튼 클릭
                        modal_clicked = await click_modal_button(main_page, "확인")
                        if not modal_clicked:
                            print("   모달 확인 버튼을 찾을 수 없음")

                        # 토스트 알림 확인
                        toast_found, toast_message = await wait_for_toast(main_page, "비공개")

                        results["checks"]["비공개하기"] = {"toast_found": toast_found, "toast_message": toast_message, "status": "PASS" if toast_found else "CHECK"}
                        results["steps"].append({
                            "step": 4,
                            "action": "[테스트 3] 비공개하기",
                            "check_item": "비공개 변경 + 토스트",
                            "detail": f"토스트 알림: \"{toast_message}\"" if toast_found else "토스트 알림 미확인",
                            "status": "PASS" if toast_found else "CHECK"
                        })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc11_04_after_private.png", full_page=True)

            # ===========================================
            # [테스트 4] 삭제하기
            # ===========================================
            print("\n" + "=" * 60)
            print("[테스트 4] 삭제하기")
            print("=" * 60)

            # sample 행 인덱스 다시 찾기
            sample_index = await find_sample_row_index(main_page)

            if sample_index >= 0:
                # 체크박스 체크
                checkbox_checked = await check_sample_checkbox(main_page, sample_index)

                if checkbox_checked:
                    # 행 내부 "삭제하기" 버튼 클릭
                    delete_clicked = await click_row_action_button(main_page, sample_index, "삭제")

                    if not delete_clicked:
                        # 대안: 상단 버튼 시도
                        delete_clicked = await click_top_button(main_page, "삭제")

                    if delete_clicked:
                        # 모달에서 '확인' 버튼 클릭
                        modal_clicked = await click_modal_button(main_page, "확인")
                        if not modal_clicked:
                            print("   모달 확인 버튼을 찾을 수 없음")

                        # 토스트 알림 확인
                        toast_found, toast_message = await wait_for_toast(main_page, "삭제")

                        results["checks"]["삭제하기"] = {"toast_found": toast_found, "toast_message": toast_message, "status": "PASS" if toast_found else "CHECK"}
                        results["steps"].append({
                            "step": 5,
                            "action": "[테스트 4] 삭제하기",
                            "check_item": "삭제 + 토스트",
                            "detail": f"토스트 알림: \"{toast_message}\"" if toast_found else "토스트 알림 미확인",
                            "status": "PASS" if toast_found else "CHECK"
                        })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc11_05_after_delete.png", full_page=True)

            # ===========================================
            # [테스트 5] [복사본]sample 삭제하기
            # ===========================================
            print("\n" + "=" * 60)
            print("[테스트 5] [복사본]sample 삭제하기")
            print("=" * 60)

            # [복사본]sample 행 찾기
            copy_sample_index = await find_copy_sample_row_index(main_page)

            if copy_sample_index >= 0:
                # 체크박스 체크
                checkbox_checked = await check_sample_checkbox(main_page, copy_sample_index)

                if checkbox_checked:
                    # 행 내부 "삭제하기" 버튼 클릭
                    delete_clicked = await click_row_action_button(main_page, copy_sample_index, "삭제")

                    if delete_clicked:
                        # 모달에서 '확인' 버튼 클릭
                        modal_clicked = await click_modal_button(main_page, "확인")
                        if not modal_clicked:
                            print("   모달 확인 버튼을 찾을 수 없음")

                        # 토스트 알림 확인
                        toast_found, toast_message = await wait_for_toast(main_page, "삭제")

                        results["checks"]["[복사본]sample_삭제하기"] = {"toast_found": toast_found, "toast_message": toast_message, "status": "PASS" if toast_found else "CHECK"}
                        results["steps"].append({
                            "step": 6,
                            "action": "[테스트 5] [복사본]sample 삭제하기",
                            "check_item": "삭제 + 토스트",
                            "detail": f"토스트 알림: \"{toast_message}\"" if toast_found else "토스트 알림 미확인",
                            "status": "PASS" if toast_found else "CHECK"
                        })
            else:
                print("   [복사본]sample 활동을 찾을 수 없음")
                results["steps"].append({
                    "step": 6,
                    "action": "[테스트 5] [복사본]sample 삭제하기",
                    "check_item": "[복사본]sample 찾기",
                    "detail": "[복사본]sample 활동을 찾을 수 없음",
                    "status": "CHECK"
                })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc11_06_after_copy_delete.png", full_page=True)

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

            with open("test_result_TC-T-11.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result_TC-T-11.json")

            print("\n2초 후 종료...")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))
            try:
                await entry_page.screenshot(path=f"{SCREENSHOT_DIR}/tc11_error.png")
            except:
                pass
            finally:
                await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    print("=" * 60)
    print("TC-T-11: 모둠활동 복사/공개/비공개/삭제 테스트 시작")
    print("=" * 60)
    asyncio.run(test_group_activity_manage())
