"""
수업 분석 카드 점수 부분 디버깅
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re

LOAD_WAIT = 5
MAX_WAIT = 60


async def debug_analysis_score():
    """수업 분석 카드 점수 상세 확인"""

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
            except TimeoutError:
                pass

            await asyncio.sleep(LOAD_WAIT)
            try:
                await main_page.wait_for_selector(".loading", state="hidden", timeout=30000)
            except TimeoutError:
                pass

            print("=" * 60)
            print("수업 분석 카드 점수 디버깅")
            print("=" * 60)

            # 수업 분석 섹션 텍스트
            analysis_elem = main_page.locator("[class*='analysis']").first
            analysis_text = await analysis_elem.inner_text()

            print("\n1. 수업 분석 섹션 전체 텍스트:")
            print("-" * 40)
            print(analysis_text)
            print("-" * 40)

            # AI 관련 텍스트 찾기
            print("\n2. AI 관련 부분:")
            lines = analysis_text.split('\n')
            for i, line in enumerate(lines):
                if 'AI' in line or '점수' in line or '점' in line or '평가' in line:
                    print(f"   [{i}] {line}")

            # 점수 패턴
            print("\n3. 점수 패턴:")
            scores = re.findall(r'(\w+)\s*(\d+)점', analysis_text)
            print(f"   {scores}")

            # AI 단원, AI 형성 검색
            print("\n4. AI 단원/형성 검색:")
            ai_idx = analysis_text.find("AI 단원")
            form_idx = analysis_text.find("AI 형성")
            print(f"   AI 단원 위치: {ai_idx}")
            print(f"   AI 형성 위치: {form_idx}")

            if ai_idx != -1:
                print(f"   AI 단원 주변: {analysis_text[ai_idx:ai_idx+50]}")
            if form_idx != -1:
                print(f"   AI 형성 주변: {analysis_text[form_idx:form_idx+50]}")

            print("\n15초 후 종료...")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_analysis_score())
