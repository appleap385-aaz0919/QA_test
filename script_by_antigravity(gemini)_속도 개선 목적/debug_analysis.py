"""
수업 분석 카드 상세 디버깅
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_analysis():
    """수업 분석 카드 상세 확인"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=20)
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
            print("수업 분석 카드 상세 디버깅")
            print("=" * 60)

            # 수업 분석 섹션 텍스트
            analysis_elem = main_page.locator("[class*='analysis']").first
            analysis_text = await analysis_elem.inner_text()

            print("\n1. 수업 분석 섹션 전체 텍스트:")
            print("-" * 40)
            print(analysis_text)
            print("-" * 40)

            # 패턴 분석
            print("\n2. 패턴 분석:")

            # 학습 수준 - N명 패턴 4개
            level_matches = re.findall(r'(\d+)명', analysis_text)
            print(f"   'N명' 패턴: {level_matches}")

            # 점수 패턴
            score_matches = re.findall(r'(\d+)점', analysis_text)
            print(f"   'N점' 패턴: {score_matches}")

            # AI 진단평가
            ai_diag = re.search(r'AI.*?진단.*?(\d+)', analysis_text, re.DOTALL)
            print(f"   AI 진단평가: {ai_diag.group(1) if ai_diag else '미발견'}")

            # AI 형성평가
            ai_form = re.search(r'AI.*?형성.*?(\d+)', analysis_text, re.DOTALL)
            print(f"   AI 형성평가: {ai_form.group(1) if ai_form else '미발견'}")

            # 학습 수준/태도 섹션 찾기
            print("\n3. 학습 수준/태도 섹션:")
            if "학습 수준" in analysis_text:
                idx = analysis_text.find("학습 수준")
                print(f"   학습 수준 주변: {analysis_text[idx:idx+100]}")
            if "학습 태도" in analysis_text:
                idx = analysis_text.find("학습 태도")
                print(f"   학습 태도 주변: {analysis_text[idx:idx+100]}")

            print("\n15초 후 종료...")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_analysis())
