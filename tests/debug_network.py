"""
페이지 구조 디버깅 스크립트 v3
- 네트워크 요청 모니터링
- 콘솔 로그 확인
- 클릭 이벤트 상세 추적
"""

import asyncio
from playwright.async_api import async_playwright

LOAD_WAIT = 5
MAX_WAIT = 30

async def debug_with_network():
    """네트워크 요청과 함께 디버깅"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # 네트워크 요청 로깅
        requests_log = []
        responses_log = []

        def on_request(request):
            req_info = {
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type
            }
            requests_log.append(req_info)
            # API 요청만 출력
            if "api" in request.url.lower() or request.resource_type in ["xhr", "fetch"]:
                print(f"   [API 요청] {request.method} {request.url[:80]}")

        def on_response(response):
            resp_info = {
                "url": response.url,
                "status": response.status,
                "ok": response.ok
            }
            responses_log.append(resp_info)
            # API 응답만 출력
            if "api" in response.url.lower() or response.request.resource_type in ["xhr", "fetch"]:
                print(f"   [API 응답] {response.status} {response.url[:80]}")

        def on_console(msg):
            print(f"   [Console] {msg.type}: {msg.text[:100]}")

        def on_dialog(dialog):
            print(f"   [Dialog] {dialog.type}: {dialog.message}")
            asyncio.create_task(dialog.dismiss())

        page.on("request", on_request)
        page.on("response", on_response)
        page.on("console", on_console)
        page.on("dialog", on_dialog)

        try:
            print("=" * 60)
            print("1. 페이지 접속")
            print("=" * 60)
            await page.goto(TEST_URL, timeout=60000)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(LOAD_WAIT)

            await page.screenshot(path="screenshots/v3_01_initial.png", full_page=True)
            print(f"   URL: {page.url}")
            print(f"   제목: {await page.title()}")

            # 버튼 정보
            print("\n" + "=" * 60)
            print("2. 선생님 입장하기 버튼 분석")
            print("=" * 60)

            teacher_btn = page.locator("button").filter(has_text="선생님 입장하기")
            btn_count = await teacher_btn.count()
            print(f"   버튼 개수: {btn_count}")

            if btn_count > 0:
                # 버튼 속성 확인
                btn = teacher_btn.first
                btn_html = await btn.evaluate("el => el.outerHTML")
                print(f"   버튼 HTML: {btn_html[:200]}")

                # 버튼 클릭 핸들러 확인
                has_click = await btn.evaluate("el => el.onclick !== null")
                print(f"   onclick 핸들러 있음: {has_click}")

                # 부모 요소 확인
                parent_tag = await btn.evaluate("el => el.parentElement.tagName")
                parent_class = await btn.evaluate("el => el.parentElement.className")
                print(f"   부모 태그: {parent_tag}, 클래스: {parent_class}")

            # 클릭 전 상태
            print("\n" + "=" * 60)
            print("3. 버튼 클릭")
            print("=" * 60)

            # 방법 1: 일반 클릭
            print("   방법 1: 일반 click() 시도...")
            try:
                await teacher_btn.click(timeout=5000)
                print("   클릭 완료")
            except Exception as e:
                print(f"   실패: {e}")

            # 잠시 대기
            await asyncio.sleep(2)

            # 진입 팝업 확인
            popup_count = await page.locator(".entry-popup").count()
            print(f"   진입 팝업 존재: {popup_count > 0}")

            if popup_count > 0:
                # 방법 2: JavaScript로 직접 클릭
                print("\n   방법 2: JavaScript click() 시도...")
                try:
                    await teacher_btn.evaluate("el => el.click()")
                    print("   JS 클릭 완료")
                except Exception as e:
                    print(f"   실패: {e}")

                await asyncio.sleep(3)

                popup_count = await page.locator(".entry-popup").count()
                print(f"   진입 팝업 존재: {popup_count > 0}")

            if popup_count > 0:
                # 방법 3: dispatchEvent
                print("\n   방법 3: dispatchEvent 시도...")
                try:
                    await teacher_btn.dispatch_event("click")
                    print("   dispatchEvent 완료")
                except Exception as e:
                    print(f"   실패: {e}")

                await asyncio.sleep(3)

                popup_count = await page.locator(".entry-popup").count()
                print(f"   진입 팝업 존재: {popup_count > 0}")

            # 방법 4: 마우스로 클릭
            if popup_count > 0:
                print("\n   방법 4: 마우스 클릭 시도...")
                try:
                    box = await teacher_btn.bounding_box()
                    if box:
                        x = box["x"] + box["width"] / 2
                        y = box["y"] + box["height"] / 2
                        await page.mouse.click(x, y)
                        print(f"   마우스 클릭 완료 ({x}, {y})")
                except Exception as e:
                    print(f"   실패: {e}")

                await asyncio.sleep(3)

            # 최종 상태 확인
            print("\n" + "=" * 60)
            print("4. 최종 상태 확인")
            print("=" * 60)

            await page.screenshot(path="screenshots/v3_02_after_click.png", full_page=True)

            popup_count = await page.locator(".entry-popup").count()
            print(f"   진입 팝업: {popup_count}")

            loading_count = await page.locator(".loading").count()
            print(f"   로딩 요소: {loading_count}")

            # URL 확인
            print(f"   현재 URL: {page.url}")

            # 버튼 상태 확인
            buttons = await page.locator("button:visible").all()
            print(f"   보이는 버튼: {len(buttons)}개")

            # 네트워크 요청 요약
            print("\n" + "=" * 60)
            print("5. 네트워크 요약")
            print("=" * 60)
            print(f"   총 요청: {len(requests_log)}개")
            print(f"   총 응답: {len(responses_log)}개")

            # API 요청만 필터링
            api_requests = [r for r in requests_log if "api" in r["url"].lower() or r["resource_type"] in ["xhr", "fetch"]]
            print(f"   API 요청: {len(api_requests)}개")

            for req in api_requests[:10]:
                print(f"      - {req['method']} {req['url'][:60]}")

            # 에러 응답 확인
            error_responses = [r for r in responses_log if not r["ok"]]
            if error_responses:
                print(f"\n   에러 응답: {len(error_responses)}개")
                for resp in error_responses[:5]:
                    print(f"      - {resp['status']} {resp['url'][:60]}")

            # HTML 저장
            body_html = await page.locator("body").inner_html()
            with open("debug_body_html_v3.txt", "w", encoding="utf-8") as f:
                f.write(body_html[:50000])
            print("\n   HTML 저장: debug_body_html_v3.txt")

            print("\n10초 후 종료...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="screenshots/v3_error.png")

        finally:
            await browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    asyncio.run(debug_with_network())
