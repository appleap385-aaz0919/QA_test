"""
TC-XX: 테스트명
- 테스트 시나리오 설명

테스트 시나리오:
1. Step 1 설명
2. Step 2 설명
...

실행 방법:
    python TC-XX_test_name.py
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json
import re

LOAD_WAIT = 5
MAX_WAIT = 60


async def test_function():
    """TC-XX: 테스트명"""

    TEST_URL = "https://example.com"
    SCREENSHOT_DIR = "screenshots"

    results = {
        "test_name": "TC-XX: 테스트명",
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": TEST_URL,
        "steps": [],
        "checks": {},
        "overall_result": "PASS",
        "errors": []
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})

        # 마이크 권한 미리 허용 (필요 시)
        await context.grant_permissions(["microphone"])

        page = await context.new_page()

        try:
            # Step 1: 페이지 진입
            print("=" * 60)
            print("Step 1: 페이지 진입")
            print("=" * 60)

            await page.goto(TEST_URL, timeout=60000)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(LOAD_WAIT)

            try:
                await page.wait_for_selector(".loading", state="hidden", timeout=30000)
            except TimeoutError:
                pass

            print(f"   현재 URL: {page.url}")
            results["steps"].append({"step": 1, "action": "페이지 진입", "status": "PASS"})

            # Step 2: 요소 찾기 및 클릭
            print("\n" + "=" * 60)
            print("Step 2: 요소 찾기 및 클릭")
            print("=" * 60)

            # button 요소 찾기
            btn = page.locator("button:has-text('버튼텍스트')")
            btn_count = await btn.count()
            print(f"   버튼 개수: {btn_count}개")

            if btn_count > 0:
                await btn.first.click()
                print("   버튼 클릭")
                results["checks"]["버튼"] = {"found": True, "count": btn_count, "status": "PASS"}
                results["steps"].append({"step": 2, "action": "버튼 클릭", "status": "PASS"})
            else:
                # span 요소에서 찾기
                span_btn = page.locator("span:has-text('버튼텍스트')")
                span_count = await span_btn.count()
                if span_count > 0:
                    await span_btn.first.click()
                    print("   span 버튼 클릭")
                    results["checks"]["버튼"] = {"found": True, "count": span_count, "status": "PASS"}
                    results["steps"].append({"step": 2, "action": "버튼 클릭", "status": "PASS"})
                else:
                    results["checks"]["버튼"] = {"found": False, "status": "FAIL"}
                    results["steps"].append({"step": 2, "action": "버튼 찾기", "status": "FAIL"})

            # Step 3: 새 창 처리
            print("\n" + "=" * 60)
            print("Step 3: 새 창 처리")
            print("=" * 60)

            new_window_btn = page.locator("button:has-text('새창열기')")
            if await new_window_btn.count() > 0:
                async with context.expect_page(timeout=MAX_WAIT * 1000) as new_page_info:
                    await new_window_btn.click()
                    print("   새 창 열기 버튼 클릭")

                new_page = await new_page_info.value
                try:
                    await new_page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)
                except TimeoutError:
                    print("   networkidle 대기 시간 초과 (계속 진행)")

                await asyncio.sleep(LOAD_WAIT)
                print(f"   새 창 URL: {new_page.url}")

                results["checks"]["새창"] = {"found": True, "url": new_page.url, "status": "PASS"}
                results["steps"].append({"step": 3, "action": "새 창 확인", "status": "PASS"})

            # Step 4: 가상 스크롤 처리
            print("\n" + "=" * 60)
            print("Step 4: 가상 스크롤 처리")
            print("=" * 60)

            print("   스크롤하며 모든 요소 로드 중...")
            for _ in range(10):
                await page.evaluate("""() => {
                    const elements = document.querySelectorAll('*');
                    elements.forEach(el => {
                        const style = window.getComputedStyle(el);
                        const overflow = style.overflow + style.overflowY;
                        if (overflow.includes('auto') || overflow.includes('scroll')) {
                            if (el.scrollHeight > el.clientHeight) {
                                el.scrollTop += 300;
                            }
                        }
                    });
                }""")
                await asyncio.sleep(0.3)

            await asyncio.sleep(1)
            item_count = await page.locator(".item-class").count()
            print(f"   아이템 개수: {item_count}개")

            results["checks"]["아이템_리스트"] = {"count": item_count, "status": "PASS" if item_count > 0 else "CHECK"}
            results["steps"].append({"step": 4, "action": "아이템 리스트 확인", "status": "PASS" if item_count > 0 else "CHECK"})

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

            with open("test_result.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result.json")

            print("\n10초 후 종료...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))
            try:
                await page.screenshot(path=f"{SCREENSHOT_DIR}/error.png")
            except:
                pass

        finally:
            await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)

    print("=" * 60)
    print("TC-XX: 테스트 시작")
    print("=" * 60)

    asyncio.run(test_function())
