"""
AIDT LMS 인터랙티브 디버깅 스크립트
- 직접 조작하면서 페이지 상태 확인
"""

import asyncio
from playwright.async_api import async_playwright

async def interactive_debug():
    """인터랙티브 디버깅"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            print("1. 페이지 접속...")
            await page.goto(TEST_URL, timeout=60000)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(5)

            print("\n2. 현재 상태:")
            print(f"   URL: {page.url}")
            print(f"   entry-popup count: {await page.locator('.entry-popup').count()}")
            print(f"   loading count: {await page.locator('.loading').count()}")

            # 로딩 요소의 display 상태 확인
            loading_display = await page.locator(".loading").evaluate("el => window.getComputedStyle(el).display")
            print(f"   loading display: {loading_display}")

            # entry-popup의 display 상태 확인
            popup_display = await page.locator(".entry-popup").evaluate("el => window.getComputedStyle(el).display")
            print(f"   entry-popup display: {popup_display}")

            # 버튼 클릭
            print("\n3. 선생님 입장하기 버튼 클릭...")
            await page.click("button:has-text('선생님 입장하기')")
            print("   클릭 완료")

            # 10초 대기하며 상태 변화 관찰
            print("\n4. 15초간 상태 변화 관찰...")
            for i in range(15):
                await asyncio.sleep(1)

                popup_count = await page.locator(".entry-popup").count()
                loading_count = await page.locator(".loading").count()

                # 실제 display 상태 확인
                popup_visible = False
                loading_visible = False

                try:
                    popup_display = await page.locator(".entry-popup").evaluate("el => window.getComputedStyle(el).display")
                    popup_visible = popup_display != "none"
                except:
                    pass

                try:
                    loading_display = await page.locator(".loading").evaluate("el => window.getComputedStyle(el).display")
                    loading_visible = loading_display != "none"
                except:
                    pass

                # URL 확인
                current_url = page.url
                url_changed = "main" in current_url or "home" in current_url or "class" in current_url

                print(f"   [{i+1}s] popup: {popup_count}(visible:{popup_visible}), loading: {loading_count}(visible:{loading_visible}), url_changed: {url_changed}")

                # 스크린샷
                await page.screenshot(path=f"screenshots/frame_{i+1:02d}.png")

            # 최종 상태 확인
            print("\n5. 최종 상태:")
            print(f"   URL: {page.url}")

            # 전체 HTML 구조 확인
            app_html = await page.locator("#app").inner_html()
            print(f"   #app HTML 길이: {len(app_html)}")

            # 주요 요소 확인
            print("\n6. 주요 요소 확인:")

            # 사이드바 확인
            sidebar_count = await page.locator("[class*='sidebar']").count()
            print(f"   sidebar: {sidebar_count}")

            # 메인 콘텐츠 확인
            main_count = await page.locator("main").count()
            print(f"   main: {main_count}")

            # 네비게이션 확인
            nav_count = await page.locator("nav").count()
            print(f"   nav: {nav_count}")

            # 메뉴 아이템 확인
            menu_items = await page.locator("[class*='menu']").count()
            print(f"   menu items: {menu_items}")

            # 모든 visible 텍스트 수집
            print("\n7. 페이지 내 visible 텍스트:")
            body_text = await page.locator("body").inner_text()
            lines = [line.strip() for line in body_text.split('\n') if line.strip()][:30]
            for line in lines:
                print(f"   - {line[:50]}")

            # HTML 저장
            with open("debug_final_html.txt", "w", encoding="utf-8") as f:
                f.write(await page.content())
            print("\n   HTML 저장: debug_final_html.txt")

            # 종료
            print("\n5초 후 종료...")
            await asyncio.sleep(5)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    asyncio.run(interactive_debug())
