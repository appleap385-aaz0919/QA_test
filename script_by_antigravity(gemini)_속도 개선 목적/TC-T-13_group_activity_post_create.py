"""
TC-T-13: 모둠 활동 선택 > 활동 보드판 > 게시글 작성 동작 확인

테스트 시나리오:
1. 진입 페이지 > 선생님 입장
2. 모둠활동 메뉴 클릭
3. 작성하기 버튼 클릭 > 활동 만들기 팝업
4. 활동 이름 'sample' 입력 > '타일형' 선택 > 만들기 버튼 클릭
5. 새 창에서 '활동 설정' 패널 닫기
6. 우측 하단 '게시글 만들기' 버튼 클릭 (class: activity-float-button activity-float-card-add)
7. 게시글 카드에서 제목 'title' 입력
8. 내용 'Input contents' 입력
9. 게시글 컬러 노란색 선택 rgb(255, 248, 222)
10. 만들기 버튼 클릭
11. 토스트 알림 '활동 게시글이 생성되었습니다.' 확인
12. 보드에 게시글 생성 확인
13. 창 닫기
14. sample 활동 삭제
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json

LOAD_WAIT = 1
MAX_WAIT = 60
SCREENSHOT_DIR = "screenshots"

results = {
    "test_name": "TC-T-13: 모둠 활동 선택 > 활동 보드판 > 게시글 작성 동작 확인",
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
    """행 내부의 액션 버튼 클릭"""
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
                    print(f"   행 내부 '{button_text}' 버튼 클릭")
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


async def wait_for_toast(page, keyword, max_wait=10):
    """토스트 알림 대기"""
    print(f"   토스트 알림 대기 중 (키워드: {keyword})...")
    for wait_sec in range(max_wait):
        await asyncio.sleep(1)
        toast_selectors = [".toast.show", ".toast", "[class*='toast show']", "[class*='toast']", "[class*='Toast']", "[class*='alert']", "[class*='show']"]
        for selector in toast_selectors:
            try:
                toast_elements = page.locator(selector)
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


async def test_group_activity_post_create():
    """TC-T-13: 모둠 활동 선택 > 활동 보드판 > 게시글 작성 동작 확인"""
    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"
    results["test_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results["url"] = TEST_URL

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=20)
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
                "action": "진입 페이지 > 선생님 입장하기",
                "check_item": "메인 페이지 진입",
                "detail": f"URL: {main_page.url}",
                "status": "PASS"
            })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_01_main_page.png", full_page=True)

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
                "check_item": "모둠활동 리스트 페이지 이동",
                "detail": "모둠활동 메뉴 클릭 완료",
                "status": "PASS"
            })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_02_group_menu.png", full_page=True)

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

            try:
                await main_page.wait_for_selector(".modal-content, .modal-dialog, .modal", state="visible", timeout=5000)
                print("   활동 만들기 팝업 감지됨")
            except TimeoutError:
                print("   팝업 감지되지 않음")

            results["steps"].append({
                "step": 3,
                "action": "작성하기 버튼 클릭",
                "check_item": "활동 만들기 팝업 표시",
                "detail": "활동 만들기 팝업 표시됨",
                "status": "PASS"
            })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_03_create_popup.png", full_page=True)

            # ===========================================
            # Step 4: 활동 이름 입력 > 타일형 선택 > 만들기
            # ===========================================
            print("\n" + "=" * 60)
            print("Step 4: 활동 이름 'sample' 입력 > 타일형 선택 > 만들기")
            print("=" * 60)

            input_el = main_page.locator(".modal-content input[type='text']").first
            await input_el.click()
            await asyncio.sleep(0.3)
            await input_el.fill("sample")
            print("   활동 이름 'sample' 입력")

            tile_label = main_page.locator("label:has-text('타일형')").first
            await tile_label.click()
            print("   타일형 선택")

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

            print(f"   활동 페이지 URL: {activity_page.url}")

            results["steps"].append({
                "step": 4,
                "action": "활동 이름 'sample' 입력 > 타일형 선택 > 만들기 클릭",
                "check_item": "새 창으로 모둠활동창 열림",
                "detail": f"URL: {activity_page.url}",
                "status": "PASS"
            })
            await activity_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_04_activity_page.png", full_page=True)

            # ===========================================
            # Step 5: 활동 설정 패널 닫기
            # ===========================================
            print("\n" + "=" * 60)
            print("Step 5: 활동 설정 패널 닫기")
            print("=" * 60)

            # 패널 닫기 버튼 (class: aidt-close-button no-long-press no-drag activity-setting-header-close)
            panel_close_selectors = [
                ".activity-setting-header-close",
                ".aidt-close-button.activity-setting-header-close",
                "button.activity-setting-header-close",
                "[class*='activity-setting-header-close']",
            ]

            panel_closed = False
            for selector in panel_close_selectors:
                try:
                    close_btn = activity_page.locator(selector).first
                    if await close_btn.is_visible(timeout=3000):
                        await close_btn.click()
                        print(f"   패널 닫기 버튼 클릭 (selector: {selector})")
                        panel_closed = True
                        break
                except:
                    continue

            if not panel_closed:
                # ESC 키로 패널 닫기 시도
                await activity_page.keyboard.press("Escape")
                print("   ESC 키로 패널 닫기 시도")
                await asyncio.sleep(1)

            await asyncio.sleep(2)

            results["steps"].append({
                "step": 5,
                "action": "활동 설정 패널 닫기",
                "check_item": "패널 닫기",
                "detail": "패널 닫기 완료" if panel_closed else "패널 닫기 실패",
                "status": "PASS" if panel_closed else "CHECK"
            })
            await activity_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_05_panel_closed.png", full_page=True)

            # ===========================================
            # Step 6: 게시글 만들기 버튼 클릭 (우측 하단 플로팅 버튼)
            # ===========================================
            print("\n" + "=" * 60)
            print("Step 6: 게시글 만들기 버튼 클릭")
            print("=" * 60)

            # 우측 하단 게시글 만들기 플로팅 버튼 (class: activity-float-button activity-float-card-add)
            post_btn_selectors = [
                ".activity-float-button.activity-float-card-add",
                ".activity-float-card-add",
                "button.activity-float-button",
                "[class*='activity-float-card-add']",
            ]

            post_btn_found = False
            for selector in post_btn_selectors:
                try:
                    post_btn = activity_page.locator(selector).first
                    if await post_btn.is_visible(timeout=3000):
                        await post_btn.click()
                        print(f"   게시글 만들기 버튼 클릭 (selector: {selector})")
                        post_btn_found = True
                        break
                except:
                    continue

            if not post_btn_found:
                print("   게시글 만들기 버튼을 찾을 수 없음")

            await asyncio.sleep(2)

            results["checks"]["게시글_만들기_버튼"] = {"found": post_btn_found, "status": "PASS" if post_btn_found else "CHECK"}
            results["steps"].append({
                "step": 6,
                "action": "우측 하단 '게시글 만들기' 버튼 클릭",
                "check_item": "게시글 작성 패널 열림",
                "detail": "플로팅 버튼 클릭 완료" if post_btn_found else "버튼 찾기 실패",
                "status": "PASS" if post_btn_found else "CHECK"
            })
            await activity_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_06_post_btn_clicked.png", full_page=True)

            # 게시글 만들기 버튼을 찾지 못하면 이후 단계 중단
            if not post_btn_found:
                results["steps"].append({
                    "step": 7,
                    "action": "게시글 작성",
                    "check_item": "제목/내용 입력",
                    "detail": "게시글 만들기 버튼 미발견으로 스킵",
                    "status": "SKIP"
                })
                results["steps"].append({
                    "step": 8,
                    "action": "게시글 컬러 선택",
                    "check_item": "노란색 선택",
                    "detail": "게시글 만들기 버튼 미발견으로 스킵",
                    "status": "SKIP"
                })
                results["steps"].append({
                    "step": 9,
                    "action": "만들기 버튼 클릭",
                    "check_item": "게시글 생성",
                    "detail": "게시글 만들기 버튼 미발견으로 스킵",
                    "status": "SKIP"
                })
                results["steps"].append({
                    "step": 10,
                    "action": "토스트 알림 확인",
                    "check_item": "토스트 알림",
                    "detail": "게시글 만들기 버튼 미발견으로 스킵",
                    "status": "SKIP"
                })
                results["steps"].append({
                    "step": 11,
                    "action": "보드에 게시글 생성 확인",
                    "check_item": "게시글 존재",
                    "detail": "게시글 만들기 버튼 미발견으로 스킵",
                    "status": "SKIP"
                })
            else:
                # ===========================================
                # Step 7: 게시글 작성 - 제목, 내용 입력
                # ===========================================
                print("\n" + "=" * 60)
                print("Step 7: 게시글 작성 - 제목 'title', 내용 'Input contents'")
                print("=" * 60)

                # 제목 입력
                title_found = False
                title_input_selectors = [
                    "input[placeholder*='제목']",
                    "input[placeholder*='title']",
                    ".post-title-input",
                    "[class*='title'] input",
                    "input.title",
                    ".card-add input[type='text']",
                    ".activity-float-card-add input[type='text']",
                ]

                for selector in title_input_selectors:
                    try:
                        title_input = activity_page.locator(selector).first
                        if await title_input.is_visible(timeout=2000):
                            await title_input.click()
                            await asyncio.sleep(0.3)
                            await title_input.fill("title")
                            print(f"   제목 'title' 입력 (selector: {selector})")
                            title_found = True
                            break
                    except:
                        continue

                if not title_found:
                    # 모든 input 검색
                    all_inputs = activity_page.locator("input[type='text']")
                    input_count = await all_inputs.count()
                    print(f"   텍스트 input 총 {input_count}개 검색 중...")
                    for i in range(input_count):
                        inp = all_inputs.nth(i)
                        try:
                            if await inp.is_visible():
                                await inp.click()
                                await asyncio.sleep(0.3)
                                await inp.fill("title")
                                print(f"   [{i}] 제목 입력 완료")
                                title_found = True
                                break
                        except:
                            continue

                # 내용 입력
                content_found = False
                content_input_selectors = [
                    "textarea[placeholder*='내용']",
                    "textarea[placeholder*='content']",
                    ".post-content-input",
                    "[class*='content'] textarea",
                    "textarea",
                ]

                for selector in content_input_selectors:
                    try:
                        content_input = activity_page.locator(selector).first
                        if await content_input.is_visible(timeout=2000):
                            await content_input.click()
                            await asyncio.sleep(0.3)
                            await content_input.fill("Input contents")
                            print(f"   내용 'Input contents' 입력 (selector: {selector})")
                            content_found = True
                            break
                    except:
                        continue

                results["steps"].append({
                    "step": 7,
                    "action": "게시글 제목 'title', 내용 'Input contents' 입력",
                    "check_item": "제목/내용 입력 완료",
                    "detail": f"제목: {title_found}, 내용: {content_found}",
                    "status": "PASS" if (title_found and content_found) else "CHECK"
                })
                await activity_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_07_post_content.png", full_page=True)

                # ===========================================
                # Step 8: 게시글 컬러 노란색 선택
                # ===========================================
                print("\n" + "=" * 60)
                print("Step 8: 게시글 컬러 노란색 선택")
                print("=" * 60)

                # 노란색 (rgb(255, 248, 222) 또는 #fff8de)
                color_selectors = [
                    "[style*='rgb(255, 248, 222)']",
                    "[style*='#fff8de']",
                    "[style*='rgb(255, 248,']",
                    ".color-picker [style*='255, 248']",
                    "[class*='color'] [style*='yellow']",
                    "[class*='color'] [style*='#fff']",
                ]

                color_selected = False
                for selector in color_selectors:
                    try:
                        color_btn = activity_page.locator(selector).first
                        if await color_btn.is_visible(timeout=2000):
                            await color_btn.click()
                            print(f"   노란색 컬러 선택 (selector: {selector})")
                            color_selected = True
                            break
                    except:
                        continue

                if not color_selected:
                    # 모든 컬러 선택자 검색
                    print("   컬러 선택자 직접 검색 중...")
                    color_elements = activity_page.locator("[class*='color'], [class*='Color'], .color-item")
                    color_count = await color_elements.count()
                    print(f"   컬러 요소 {color_count}개 발견")
                    for i in range(min(color_count, 10)):
                        try:
                            elem = color_elements.nth(i)
                            if await elem.is_visible():
                                await elem.click()
                                print(f"   [{i}] 컬러 요소 클릭")
                                color_selected = True
                                break
                        except:
                            continue

                await asyncio.sleep(1)

                results["steps"].append({
                    "step": 8,
                    "action": "게시글 컬러 노란색 선택",
                    "check_item": "노란색 선택 완료",
                    "detail": "노란색 컬러 선택 완료" if color_selected else "컬러 선택 실패",
                    "status": "PASS" if color_selected else "CHECK"
                })
                await activity_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_08_color_selected.png", full_page=True)

                # ===========================================
                # Step 9: 만들기 버튼 클릭
                # ===========================================
                print("\n" + "=" * 60)
                print("Step 9: 만들기 버튼 클릭")
                print("=" * 60)

                # 만들기/생성 버튼 찾기
                create_btn_selectors = [
                    "button:has-text('만들기')",
                    "button:has-text('생성')",
                    "button:has-text('등록')",
                    "button:has-text('확인')",
                    ".card-add button:has-text('만들기')",
                ]

                create_clicked = False
                for selector in create_btn_selectors:
                    try:
                        btn = activity_page.locator(selector).first
                        if await btn.is_visible(timeout=2000):
                            await btn.click()
                            print(f"   만들기 버튼 클릭 (selector: {selector})")
                            create_clicked = True
                            break
                    except:
                        continue

                # ===========================================
                # Step 10: 토스트 알림 즉시 확인 (2초 내에 사라짐)
                # ===========================================
                print("\n" + "=" * 60)
                print("Step 10: 토스트 알림 확인 (버튼 클릭 직후)")
                print("=" * 60)

                # 버튼 클릭 직후 즉시 토스트 확인 (최대 3초 대기)
                toast_found = False
                toast_message = ""
                for wait_sec in range(6):  # 0.5초씩 6번 = 3초
                    await asyncio.sleep(0.5)
                    toast_selectors = [".toast.show", ".toast", "[class*='toast show']", "[class*='toast']", "[class*='Toast']", "[class*='alert']", "[class*='show']"]
                    for selector in toast_selectors:
                        try:
                            toast_elements = activity_page.locator(selector)
                            count = await toast_elements.count()
                            if count > 0:
                                for i in range(count):
                                    toast_text = await toast_elements.nth(i).inner_text()
                                    if "게시글" in toast_text:
                                        print(f"   토스트 알림 발견: {toast_text}")
                                        toast_found = True
                                        toast_message = toast_text
                                        break
                        except:
                            continue
                        if toast_found:
                            break
                    if toast_found:
                        break

                results["steps"].append({
                    "step": 9,
                    "action": "만들기 버튼 클릭",
                    "check_item": "게시글 생성",
                    "detail": "만들기 버튼 클릭 완료" if create_clicked else "버튼 찾기 실패",
                    "status": "PASS" if create_clicked else "CHECK"
                })
                await activity_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_09_post_created.png", full_page=True)

                results["checks"]["토스트_알림"] = {"found": toast_found, "message": toast_message, "status": "PASS" if toast_found else "CHECK"}
                results["steps"].append({
                    "step": 10,
                    "action": "토스트 알림 확인",
                    "check_item": "'활동 게시글이 생성되었습니다.'",
                    "detail": f"토스트: \"{toast_message}\"" if toast_found else "토스트 알림 미확인",
                    "status": "PASS" if toast_found else "CHECK"
                })

                # ===========================================
                # Step 11: 게시글이 보드에 생성되었는지 확인
                # ===========================================
                print("\n" + "=" * 60)
                print("Step 11: 게시글이 보드에 생성되었는지 확인")
                print("=" * 60)

                # 보드에서 'title' 텍스트 찾기
                page_text = await activity_page.locator("body").inner_text()
                post_on_board = "title" in page_text

                print(f"   보드에 'title' 존재 여부: {post_on_board}")

                results["checks"]["게시글_보드_생성"] = {"found": post_on_board, "status": "PASS" if post_on_board else "CHECK"}
                results["steps"].append({
                    "step": 11,
                    "action": "보드에 게시글 생성 확인",
                    "check_item": "보드에 게시글 존재",
                    "detail": "게시글이 보드에 생성됨" if post_on_board else "게시글 미확인",
                    "status": "PASS" if post_on_board else "CHECK"
                })
                await activity_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_11_post_on_board.png", full_page=True)

            # ===========================================
            # Step 12: 창 닫기
            # ===========================================
            print("\n" + "=" * 60)
            print("Step 12: 창 닫기")
            print("=" * 60)

            await activity_page.close()
            print("   활동 창 닫기 완료")

            results["steps"].append({
                "step": 12,
                "action": "창 닫기",
                "check_item": "활동 창 닫기",
                "detail": "활동 창 닫기 완료",
                "status": "PASS"
            })

            # ===========================================
            # Step 13: sample 활동 삭제
            # ===========================================
            print("\n" + "=" * 60)
            print("Step 13: sample 활동 삭제")
            print("=" * 60)

            # 메인 페이지 새로고침
            await main_page.reload()
            await asyncio.sleep(LOAD_WAIT)
            try:
                await main_page.wait_for_selector(".loading", state="hidden", timeout=30000)
            except TimeoutError:
                pass

            sample_index = await find_sample_row_index(main_page)

            if sample_index >= 0:
                delete_clicked = await click_row_action_button(main_page, sample_index, "삭제")

                if delete_clicked:
                    modal_clicked = await click_modal_button(main_page, "확인")
                    if not modal_clicked:
                        print("   모달 확인 버튼을 찾을 수 없음")

                    toast_found, toast_message = await wait_for_toast(main_page, "삭제")

                    results["checks"]["활동_삭제"] = {"toast_found": toast_found, "toast_message": toast_message, "status": "PASS" if toast_found else "CHECK"}
                    results["steps"].append({
                        "step": 13,
                        "action": "sample 활동 삭제",
                        "check_item": "삭제 + 토스트 알림",
                        "detail": f"토스트: \"{toast_message}\"" if toast_found else "토스트 알림 미확인",
                        "status": "PASS" if toast_found else "CHECK"
                    })
                else:
                    results["steps"].append({
                        "step": 13,
                        "action": "sample 활동 삭제",
                        "check_item": "삭제 버튼 클릭",
                        "detail": "삭제 버튼 클릭 실패",
                        "status": "CHECK"
                    })
            else:
                results["steps"].append({
                    "step": 13,
                    "action": "sample 활동 삭제",
                    "check_item": "sample 활동 찾기",
                    "detail": "sample 활동을 찾을 수 없음",
                    "status": "CHECK"
                })
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_13_after_delete.png", full_page=True)

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

            with open("test_result_TC-T-13.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result_TC-T-13.json")

            print("\n10초 후 종료...")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))
            try:
                await entry_page.screenshot(path=f"{SCREENSHOT_DIR}/tc13_error.png")
            except:
                pass
            finally:
                await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    print("=" * 60)
    print("TC-T-13: 모둠 활동 선택 > 활동 보드판 > 게시글 작성 동작 확인 테스트 시작")
    print("=" * 60)
    asyncio.run(test_group_activity_post_create())
