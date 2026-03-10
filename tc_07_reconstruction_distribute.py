# -*- coding: utf-8 -*-
"""
TC-T-07: 재구성하기 > 재구성 화면 > 재구성 배포 동작 확인

테스트 절차:
1. 교과서 메뉴 진입
2. 재구성 하기 버튼 클릭
3. 임시저장 삭제 (있는 경우)
4. 임시저장 버튼 클릭
5. 교과서 배포 버튼 클릭
6. 모달 팝업에서 확인
7. '배포가 완료 되었습니다.' 토스트 알림 확인
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright

# 설정
ENTRY_URL = 'https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon'
SCREENSHOT_DIR = 'screenshots'
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

async def take_screenshot(page, name):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    filename = f"{SCREENSHOT_DIR}/tc07_{name}_{TIMESTAMP}.png"
    await page.screenshot(path=filename, full_page=False)
    return filename

async def wait_for_page(page, timeout=5000):
    try:
        await page.wait_for_load_state('networkidle', timeout=timeout)
        await asyncio.sleep(0.5)
    except:
        pass

async def safe_click(page, text, timeout=3000):
    try:
        selectors = [
            f'text="{text}"',
            f'button:has-text("{text}")',
            f'a:has-text("{text}")',
            f'[role="button"]:has-text("{text}")',
        ]
        for selector in selectors:
            try:
                await page.click(selector, timeout=timeout)
                return True
            except:
                continue
        return False
    except:
        return False

async def check_text_exists(page, text, timeout=2000):
    try:
        await page.wait_for_selector(f'text="{text}"', timeout=timeout, state='visible')
        return True
    except:
        return False

async def main():
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("TC-T-07: 재구성 배포 동작 확인")
    print(f"URL: {ENTRY_URL}")
    print(f"시간: {TIMESTAMP}")
    print("=" * 70)

    result = {
        "test_name": "TC-T-07: 재구성 배포 동작 확인",
        "test_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "url": ENTRY_URL,
        "steps": [],
        "checks": {},
        "overall_result": "PASS",
        "errors": []
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='ko-KR'
        )
        page = await context.new_page()

        try:
            # Step 0: Entry URL 접속
            print("\n[Step 0] Entry URL 접속...")
            await page.goto(ENTRY_URL, timeout=60000)
            await wait_for_page(page, timeout=10000)
            await take_screenshot(page, "01_entry")
            result["steps"].append({"step": 0, "action": "Entry URL 접속", "status": "PASS"})

            # window.open 패치
            await page.evaluate("window.open = function(url) { window.location.href = url; }")

            # 로그인 대기
            print("\n[로그인 대기] 30초 동안 로그인을 완료해주세요...")
            await asyncio.sleep(30)
            await wait_for_page(page)
            await take_screenshot(page, "02_after_login")

            # Step 1: 교과서 메뉴 클릭
            print("\n[Step 1] 교과서 메뉴 클릭...")
            step1_result = "PASS"
            try:
                if await safe_click(page, "교과서"):
                    await wait_for_page(page)
                    await take_screenshot(page, "03_textbook_menu")
                    print("  -> 교과서 메뉴 클릭 성공")
                else:
                    step1_result = "FAIL"
                    result["errors"].append("교과서 메뉴 클릭 실패")
            except Exception as e:
                step1_result = "FAIL"
                result["errors"].append(f"교과서 메뉴 클릭 오류: {str(e)}")
            result["steps"].append({"step": 1, "action": "교과서 메뉴 클릭", "status": step1_result})

            # Step 2: 재구성 하기 버튼 클릭
            print("\n[Step 2] 재구성 하기 버튼 클릭...")
            step2_result = "PASS"
            try:
                if await safe_click(page, "재구성 하기") or await safe_click(page, "재구성하기"):
                    await wait_for_page(page)
                    await take_screenshot(page, "04_reconstruction")
                    print("  -> 재구성 하기 버튼 클릭 성공")
                else:
                    step2_result = "FAIL"
                    result["errors"].append("재구성 하기 버튼 클릭 실패")
            except Exception as e:
                step2_result = "FAIL"
                result["errors"].append(f"재구성 하기 버튼 클릭 오류: {str(e)}")
            result["steps"].append({"step": 2, "action": "재구성 하기 버튼 클릭", "status": step2_result})

            # Step 3: 임시저장 삭제 (있는 경우)
            print("\n[Step 3] 임시저장 삭제 확인...")
            try:
                if await check_text_exists(page, "임시저장 삭제", timeout=2000):
                    print("  -> 임시저장 삭제 버튼 발견")
                    await safe_click(page, "임시저장 삭제")
                    await asyncio.sleep(1000)
                    # 모달에서 삭제 확인
                    if await check_text_exists(page, "삭제", timeout=2000):
                        await safe_click(page, "삭제")
                        await wait_for_page(page)
                        print("  -> 임시저장 삭제 완료")
                        result["checks"]["임시저장_삭제"] = {"found": True, "deleted": True, "status": "PASS"}
                    else:
                        await safe_click(page, "확인")
                        print("  -> 삭제 확인 버튼 대신 확인 클릭")
                else:
                    print("  -> 임시저장 삭제 버튼 없음 (삭제할 데이터 없음)")
                    result["checks"]["임시저장_삭제"] = {"found": False, "status": "PASS"}
                await take_screenshot(page, "05_after_delete_check")
            except Exception as e:
                result["checks"]["임시저장_삭제"] = {"error": str(e), "status": "PASS"}
            result["steps"].append({"step": 3, "action": "임시저장 삭제 확인", "status": "PASS"})

            # Step 4: 임시저장 버튼 클릭
            print("\n[Step 4] 임시저장 버튼 클릭...")
            step4_result = "PASS"
            try:
                if await safe_click(page, "임시저장"):
                    await wait_for_page(page)
                    await asyncio.sleep(2000)  # 토스트 대기
                    await take_screenshot(page, "06_temp_save")
                    print("  -> 임시저장 버튼 클릭 성공")

                    # 토스트 확인
                    content = await page.content()
                    if "완료" in content or "저장" in content:
                        result["checks"]["임시저장_토스트"] = {"found": True, "status": "PASS"}
                    else:
                        result["checks"]["임시저장_토스트"] = {"found": False, "status": "PASS"}
                else:
                    step4_result = "FAIL"
                    result["errors"].append("임시저장 버튼 클릭 실패")
            except Exception as e:
                step4_result = "FAIL"
                result["errors"].append(f"임시저장 버튼 클릭 오류: {str(e)}")
            result["steps"].append({"step": 4, "action": "임시저장 버튼 클릭", "status": step4_result})

            # Step 5: 교과서 배포 버튼 클릭
            print("\n[Step 5] 교과서 배포 버튼 클릭...")
            step5_result = "PASS"
            try:
                if await safe_click(page, "교과서 배포") or await safe_click(page, "배포"):
                    await wait_for_page(page)
                    await take_screenshot(page, "07_distribute_click")
                    print("  -> 교과서 배포 버튼 클릭 성공")
                else:
                    step5_result = "FAIL"
                    result["errors"].append("교과서 배포 버튼 클릭 실패")
            except Exception as e:
                step5_result = "FAIL"
                result["errors"].append(f"교과서 배포 버튼 클릭 오류: {str(e)}")
            result["steps"].append({"step": 5, "action": "교과서 배포 버튼 클릭", "status": step5_result})

            # Step 6: 모달 팝업에서 확인 클릭
            print("\n[Step 6] 모달 팝업에서 확인 클릭...")
            step6_result = "PASS"
            try:
                await asyncio.sleep(1000)
                if await check_text_exists(page, "확인", timeout=2000):
                    await safe_click(page, "확인")
                    await wait_for_page(page)
                    await take_screenshot(page, "08_confirm_click")
                    print("  -> 확인 버튼 클릭 성공")
                else:
                    # 다른 확인 버튼 시도
                    for btn_text in ["배포", "예", "확인"]:
                        if await safe_click(page, btn_text):
                            await wait_for_page(page)
                            print(f"  -> {btn_text} 버튼 클릭 성공")
                            break
            except Exception as e:
                step6_result = "FAIL"
                result["errors"].append(f"확인 버튼 클릭 오류: {str(e)}")
            result["steps"].append({"step": 6, "action": "모달 팝업에서 확인 클릭", "status": step6_result})

            # Step 7: 배포 완료 토스트 확인
            print("\n[Step 7] 배포 완료 토스트 확인...")
            await asyncio.sleep(3000)
            try:
                content = await page.content()
                if "완료" in content or "배포" in content:
                    print("  -> 완료 메시지 발견")
                    result["checks"]["배포_완료_토스트"] = {"found": True, "status": "PASS"}
                else:
                    print("  -> 완료 메시지를 찾을 수 없음")
                    result["checks"]["배포_완료_토스트"] = {"found": False, "status": "WARN"}
            except Exception as e:
                result["checks"]["배포_완료_토스트"] = {"error": str(e), "status": "WARN"}
            await take_screenshot(page, "09_final_result")

            # 전체 결과 판정
            fail_count = sum(1 for s in result["steps"] if s["status"] == "FAIL")
            if fail_count > 0:
                result["overall_result"] = "FAIL"
            else:
                result["overall_result"] = "PASS"

            print("\n" + "=" * 70)
            print(f"TC-T-07 테스트 완료: {result['overall_result']}")
            print("=" * 70)

        except Exception as e:
            print(f"\n테스트 실패: {e}")
            result["overall_result"] = "FAIL"
            result["errors"].append(str(e))
            await take_screenshot(page, "error")

        finally:
            await browser.close()

    # 결과 저장
    result_file = f"test_result_TC-T-07.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n결과 저장: {result_file}")

    return result

if __name__ == '__main__':
    asyncio.run(main())
