"""
복습률 디버깅
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re

LOAD_WAIT = 5
MAX_WAIT = 60


async def debug_wrongnote():
    """복습률 상세 확인"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        entry_page = await context.new_page()

        try:
            await entry_page.goto(TEST_URL, timeout=60000)
            await entry_page.wait_for_load_state("networkidle")
            await asyncio.sleep(LOAD_WAIT)

            teacher_btn = entry_page.locator("button").filter(has_text="선생님 입장하기")
            async with context.expect_page(timeout=MAX_WAIT * 1000) as new_page_info:
                await teacher_btn.click()

            main_page = await new_page_info.value

            try:
                await main_page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)
            except:
                pass

            await asyncio.sleep(LOAD_WAIT)
            try:
                await main_page.wait_for_selector(".loading", state="hidden", timeout=30000)
            except:
                pass

            print("=" * 60)
            print("복습률 디버깅")
            print("=" * 60)

            # 전체 텍스트
            body_text = await main_page.locator("body").inner_text()

            # 복습률 주변 텍스트
            print("\n1. 복습률 검색:")
            if "복습률" in body_text:
                idx = body_text.find("복습률")
                print(f"   복습률 주변: {body_text[idx:idx+100]}")

            # 오답노트 관련 텍스트
            print("\n2. 오답노트 섹션:")
            if "오답" in body_text:
                idx = body_text.find("오답")
                print(body_text[idx:idx+300])

            # 복습 전/완료 패턴
            print("\n3. 복습 전/완료 패턴:")
            before_match = re.search(r'복습\s*전[^\d]*(\d+)', body_text)
            complete_match = re.search(r'복습\s*완료[^\d]*(\d+)', body_text)
            rate_match = re.search(r'복습률[^\d]*(\d+)', body_text)

            print(f"   복습 전: {before_match.group(1) if before_match else '미발견'}")
            print(f"   복습 완료: {complete_match.group(1) if complete_match else '미발견'}")
            print(f"   복습률: {rate_match.group(1) if rate_match else '미발견'}")

            # % 패턴 모두
            print("\n4. 모든 % 패턴:")
            percent_matches = re.findall(r'(\d+)\s*%', body_text)
            print(f"   {percent_matches}")

            # 클래스로 찾기
            print("\n5. 복습 관련 클래스:")
            wrongnote_elems = await main_page.locator("[class*='wrong'], [class*='note'], [class*='복습']").all()
            print(f"   요소 수: {len(wrongnote_elems)}")

            print("\n15초 후 종료...")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_wrongnote())
