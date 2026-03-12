"""
AI 점수 및 복습률 상세 디버깅
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_scores():
    """AI 점수와 복습률 상세 확인"""

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
            print("AI 점수 및 복습률 디버깅")
            print("=" * 60)

            # 전체 페이지 텍스트
            body_text = await main_page.locator("body").inner_text()

            # 1. AI 관련 부분
            print("\n1. AI 관련 텍스트:")
            lines = body_text.split('\n')
            for i, line in enumerate(lines):
                if 'AI' in line and ('단원' in line or '형성' in line or '평가' in line):
                    print(f"   [{i}] {line}")
                    # 다음 줄도 출력
                    if i+1 < len(lines):
                        print(f"        -> {lines[i+1]}")

            # 2. 점수 패턴
            print("\n2. 모든 점수 패턴:")
            score_patterns = re.findall(r'(AI[^점]*|학습[^점]*|복습[^점]*)?(\d+)\s*점', body_text)
            for name, score in score_patterns[:10]:
                print(f"   '{name.strip()}' -> {score}점")

            # 3. 복습률
            print("\n3. 복습률 검색:")
            if "복습률" in body_text:
                idx = body_text.find("복습률")
                print(f"   복습률 주변: {body_text[idx:idx+50]}")

            # 복습률 % 패턴
            rate_patterns = re.findall(r'복습률[^\d]*(\d+)\s*%', body_text)
            print(f"   복습률 패턴: {rate_patterns}")

            # 모든 % 패턴
            all_percent = re.findall(r'(\d+)\s*%', body_text)
            print(f"   모든 % 패턴: {all_percent}")

            # 4. 수업 분석 섹션 전체
            print("\n4. 수업 분석 섹션:")
            analysis_idx = body_text.find("수업 분석")
            if analysis_idx != -1:
                print(body_text[analysis_idx:analysis_idx+800])

            print("\n15초 후 종료...")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_scores())
