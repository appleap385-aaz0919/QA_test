"""
페이지 구조 디버깅 스크립트 v2
- 로딩 상태 확인 및 충분한 대기 시간 적용
"""

import asyncio
from playwright.async_api import async_playwright

LOAD_WAIT = 5  # 기본 대기 시간
MAX_WAIT = 30  # 최대 대기 시간

async def wait_for_app_loaded(page):
    """앱 로딩 완료 대기"""
    print("   앱 로딩 대기 중...")

    # entry-popup이 사라질 때까지 대기
    try:
        await page.wait_for_selector(".entry-popup", state="hidden", timeout=MAX_WAIT * 1000)
        print("   진입 팝업 사라짐")
    except:
        print("   진입 팝업 여전히 존재")

    # 로딩 indicator가 사라질 때까지 대기
    try:
        await page.wait_for_selector(".loading", state="hidden", timeout=MAX_WAIT * 1000)
        print("   로딩 indicator 사라짐")
    except:
        print("   로딩 indicator 여전히 존재")

    # 추가 대기
    await asyncio.sleep(LOAD_WAIT)

async def debug_page_structure():
    """페이지 구조 분석"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            print("=" * 60)
            print("1. 페이지 접속")
            print("=" * 60)
            await page.goto(TEST_URL, timeout=60000)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(LOAD_WAIT)

            # 초기 페이지 스크린샷
            await page.screenshot(path="screenshots/debug_01_initial.png", full_page=True)
            print(f"   스크린샷 저장: debug_01_initial.png")

            title = await page.title()
            print(f"   페이지 제목: {title}")
            print(f"   현재 URL: {page.url}")

            # 선생님 입장하기 버튼 찾기
            print("\n" + "=" * 60)
            print("2. 선생님 입장하기 버튼 클릭")
            print("=" * 60)

            buttons = await page.locator("button").all()
            print(f"   발견된 버튼 수: {len(buttons)}")

            for i, btn in enumerate(buttons[:10]):
                try:
                    text = await btn.text_content()
                    is_visible = await btn.is_visible()
                    if text and text.strip():
                        print(f"   버튼 {i+1}: '{text.strip()}' (visible: {is_visible})")
                except:
                    pass

            # 선생님 입장하기 버튼 클릭
            print("\n   클릭 시도...")
            try:
                teacher_btn = page.locator("button").filter(has_text="선생님 입장하기")
                await teacher_btn.click()
                print("   클릭 완료")
            except Exception as e:
                print(f"   클릭 실패: {e}")
                # 대체 방법
                await page.click("button:has-text('선생님 입장하기')")
                print("   대체 방법으로 클릭 완료")

            # 로딩 대기
            print("\n" + "=" * 60)
            print("3. 로딩 대기")
            print("=" * 60)
            await wait_for_app_loaded(page)

            # 클릭 후 상태 확인
            print(f"\n   현재 URL: {page.url}")
            await page.screenshot(path="screenshots/debug_02_after_entry.png", full_page=True)
            print("   스크린샷 저장: debug_02_after_entry.png")

            # entry-popup 존재 여부 확인
            popup_count = await page.locator(".entry-popup").count()
            print(f"   entry-popup 존재: {popup_count > 0}")

            # 페이지 내 주요 요소 분석
            print("\n" + "=" * 60)
            print("4. 페이지 요소 분석")
            print("=" * 60)

            # h1, h2, h3 태그 텍스트
            for tag in ["h1", "h2", "h3", "h4"]:
                count = await page.locator(tag).count()
                if count > 0:
                    print(f"\n   [{tag.upper()} 태그] {count}개")
                    elements = await page.locator(tag).all()
                    for i, elem in enumerate(elements[:5]):
                        try:
                            text = await elem.text_content()
                            if text and text.strip():
                                print(f"      {i+1}. {text.strip()[:60]}")
                        except:
                            pass

            # 주요 클래스 요소 분석
            print("\n   [클래스별 요소 수]")
            class_patterns = ["card", "section", "insight", "item", "menu", "nav", "sidebar", "content", "main", "container", "widget", "board", "notice"]
            for pattern in class_patterns:
                count = await page.locator(f"[class*='{pattern}']").count()
                if count > 0:
                    print(f"   - '{pattern}': {count}개")

            # 키워드 검색
            print("\n   [키워드 검색]")
            keywords = ["오늘 수업", "교과서", "출석", "과제", "분석", "기분", "게시판", "공지", "수업 시작", "인사이트", "홈", "내 자료"]

            found_keywords = []
            for keyword in keywords:
                try:
                    count = await page.locator(f"text=/{keyword}/i").count()
                    if count > 0:
                        found_keywords.append((keyword, count))
                        print(f"   - '{keyword}': {count}개 발견")
                except:
                    pass

            if not found_keywords:
                print("   키워드 없음")

            # 모든 버튼 다시 확인
            print("\n   [진입 후 버튼 목록]")
            buttons_after = await page.locator("button:visible").all()
            print(f"   보이는 버튼 수: {len(buttons_after)}")
            for i, btn in enumerate(buttons_after[:20]):
                try:
                    text = await btn.text_content()
                    if text and text.strip():
                        print(f"      {i+1}. '{text.strip()[:40]}'")
                except:
                    pass

            # 링크 분석
            print("\n   [링크 분석]")
            links = await page.locator("a:visible").all()
            print(f"   보이는 링크 수: {len(links)}")
            for i, link in enumerate(links[:15]):
                try:
                    text = await link.text_content()
                    href = await link.get_attribute("href")
                    if text and text.strip():
                        print(f"      {i+1}. '{text.strip()[:30]}' -> {href}")
                except:
                    pass

            # HTML 저장
            print("\n" + "=" * 60)
            print("5. 결과 저장")
            print("=" * 60)

            body_html = await page.locator("body").inner_html()
            with open("debug_body_html.txt", "w", encoding="utf-8") as f:
                f.write(body_html[:50000])
            print("   HTML 저장: debug_body_html.txt (처음 50000자)")

            await page.screenshot(path="screenshots/debug_03_final.png", full_page=True)
            print("   최종 스크린샷 저장: debug_03_final.png")

            # 결과 요약
            print("\n" + "=" * 60)
            print("결과 요약")
            print("=" * 60)
            print(f"   진입 팝업 사라짐: {popup_count == 0}")
            print(f"   발견된 키워드: {len(found_keywords)}개")
            print(f"   보이는 버튼: {len(buttons_after)}개")
            print(f"   보이는 링크: {len(links)}개")

            print("\n10초 후 브라우저 종료...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n에러 발생: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="screenshots/debug_error.png")

        finally:
            await browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    asyncio.run(debug_page_structure())
