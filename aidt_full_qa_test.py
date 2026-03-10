# -*- coding: utf-8 -*-
"""
AIDT LMS 전체 QA 테스트 자동화 스크립트
- 엑셀의 '경로' 컬럼 내용을 모두 수행
- FAIL 시 '오류 현상 및 비고' 컬럼에 원인 기재
- 결과 엑셀 양식을 '개편수정' 시트와 동일하게 유지
"""

import asyncio
import pandas as pd
import os
import sys
import re
import json
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, Border, Side
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# 설정
EXCEL_FILE = 'Quick_TC_list/AIDT 모니터링_운영계_점검 리스트.xlsx'
SCREENSHOT_DIR = 'screenshots'
TODAY = datetime.now().strftime('%Y-%m-%d')

# Entry URL (운영 Backdoor) - 사용자 지정 URL
ENTRY_URL = 'https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon'

# 테스트 결과 저장
test_results = []

# 교사/학생 구분 (10-63: 교사, 64-91: 학생)
TEACHER_ROWS = range(10, 64)
STUDENT_ROWS = range(64, 92)

async def patch_window_open(page):
    """window.open을 window.location.href로 패치"""
    await page.evaluate("""() => {
        window.open = function(url) {
            window.location.href = url;
        };
    }""")

async def take_screenshot(page, name):
    """스크린샷 저장"""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    filename = f"{SCREENSHOT_DIR}/{TODAY}_{name}.png"
    await page.screenshot(path=filename, full_page=False)
    return filename

async def wait_for_page(page, timeout=5000):
    """페이지 로딩 대기"""
    try:
        await page.wait_for_load_state('networkidle', timeout=timeout)
        await asyncio.sleep(0.5)
    except:
        pass

async def safe_click(page, text, timeout=3000):
    """안전한 클릭"""
    try:
        # 여러 선택자 시도
        selectors = [
            f'text="{text}"',
            f'button:has-text("{text}")',
            f'a:has-text("{text}")',
            f'[role="button"]:has-text("{text}")',
            f'div:has-text("{text}")'
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

async def check_text_visible(page, text, timeout=2000):
    """텍스트 가시성 확인"""
    try:
        await page.wait_for_selector(f'text="{text}"', timeout=timeout, state='visible')
        return True
    except:
        return False

async def navigate_to_menu(page, menu_name):
    """메뉴로 이동"""
    try:
        # 사이드바 메뉴 클릭
        if await safe_click(page, menu_name, timeout=2000):
            await wait_for_page(page)
            return True
        return False
    except:
        return False

async def run_teacher_tests(page):
    """교사 테스트 수행"""
    results = []

    # 엑셀에서 테스트 데이터 읽기
    df = pd.read_excel(EXCEL_FILE, sheet_name='개편수정', header=None)

    for idx, row in df.iterrows():
        if idx not in TEACHER_ROWS:
            continue

        subject = str(row[1]) if pd.notna(row[1]) else ''
        step1 = str(row[3]) if pd.notna(row[3]) else ''
        step2 = str(row[4]) if pd.notna(row[4]) else ''
        path = str(row[5]) if pd.notna(row[5]) else ''

        if not path or path == 'nan':
            continue

        result = 'PASS'
        error_note = ''

        print(f"  [교사-{idx}] {step1}/{step2}: {path[:50]}...")

        try:
            # Step1 메뉴 이동
            if step1 and step1 != 'nan':
                # 메뉴 이동
                menu_name = step1.replace('[영어]', '').replace('[수학]', '').strip()
                if menu_name:
                    await navigate_to_menu(page, menu_name)
                    await wait_for_page(page)

            # 경로 실행
            path_result = await execute_path(page, path)
            if not path_result['success']:
                result = 'FAIL'
                error_note = path_result['error']

            # 스크린샷
            await take_screenshot(page, f"teacher_{idx}")

        except Exception as e:
            result = 'FAIL'
            error_note = f"실행 오류: {str(e)}"

        results.append({
            'idx': idx,
            'subject': subject,
            'role': '교사',
            'step1': step1,
            'step2': step2,
            'path': path,
            'result': result,
            'error_note': error_note
        })

        status = f"-> {result}"
        if error_note:
            status += f" ({error_note[:50]}...)"
        print(f"    {status}")
        sys.stdout.flush()

    return results

async def run_student_tests(page, browser):
    """학생 테스트 수행"""
    results = []

    df = pd.read_excel(EXCEL_FILE, sheet_name='개편수정', header=None)

    for idx, row in df.iterrows():
        if idx not in STUDENT_ROWS:
            continue

        subject = str(row[1]) if pd.notna(row[1]) else ''
        step1 = str(row[3]) if pd.notna(row[3]) else ''
        step2 = str(row[4]) if pd.notna(row[4]) else ''
        path = str(row[5]) if pd.notna(row[5]) else ''

        if not path or path == 'nan':
            continue

        result = 'PASS'
        error_note = ''

        print(f"  [학생-{idx}] {step1}/{step2}: {path[:50]}...")

        try:
            # Step1 메뉴 이동
            if step1 and step1 != 'nan':
                menu_name = step1.replace('[영어]', '').replace('[수학]', '').strip()
                if menu_name:
                    await navigate_to_menu(page, menu_name)
                    await wait_for_page(page)

            # 경로 실행
            path_result = await execute_path(page, path)
            if not path_result['success']:
                result = 'FAIL'
                error_note = path_result['error']

            # 스크린샷
            await take_screenshot(page, f"student_{idx}")

        except Exception as e:
            result = 'FAIL'
            error_note = f"실행 오류: {str(e)}"

        results.append({
            'idx': idx,
            'subject': subject,
            'role': '학생',
            'step1': step1,
            'step2': step2,
            'path': path,
            'result': result,
            'error_note': error_note
        })

        status = f"-> {result}"
        if error_note:
            status += f" ({error_note[:50]}...)"
        print(f"    {status}")
        sys.stdout.flush()

    return results

async def execute_path(page, path):
    """경로 실행 - 실제 UI 검증 포함"""
    try:
        # 경로를 '>'로 분리
        steps = [s.strip() for s in path.split('>') if s.strip()]

        for step in steps:
            # 페이지 대기
            await wait_for_page(page)
            await asyncio.sleep(0.5)

            # 확인/노출 키워드 - 실제 요소 존재 여부 확인
            if '확인' in step or '노출' in step:
                # 검증할 키워드 추출
                verify_text = re.sub(r'(확인|노출|정상적으로|정상|동작|버튼)', '', step).strip()
                if verify_text:
                    # 콤마로 구분된 여러 키워드 확인
                    keywords = [k.strip() for k in verify_text.split(',') if k.strip()]
                    found_count = 0
                    for kw in keywords:
                        if len(kw) < 2:
                            continue
                        try:
                            # 페이지 소스에서 확인
                            content = await page.content()
                            if kw in content:
                                found_count += 1
                            else:
                                # visible 요소 확인
                                if await check_text_visible(page, kw, 1500):
                                    found_count += 1
                        except:
                            pass

                    # 최소 1개 이상의 키워드가 발견되면 통과
                    if keywords and found_count == 0:
                        return {'success': False, 'error': f"'{verify_text[:50]}...' 요소를 찾을 수 없음"}
                continue

            # 버튼 클릭
            if '버튼' in step:
                btn_text = re.sub(r'(버튼|선택)', '', step).strip()
                if btn_text:
                    clicked = await safe_click(page, btn_text)
                    if not clicked:
                        # 부분 텍스트로 재시도
                        for word in btn_text.split():
                            if len(word) > 1:
                                clicked = await safe_click(page, word)
                                if clicked:
                                    break
                    if not clicked:
                        return {'success': False, 'error': f"'{btn_text}' 버튼 클릭 실패"}
                    await wait_for_page(page)
                continue

            # 팝업
            if '팝업' in step:
                await wait_for_page(page)
                continue

            # 진입/이동
            if '진입' in step or '이동' in step:
                target = re.sub(r'(진입|이동|확인|동작)', '', step).strip()
                if target:
                    await safe_click(page, target)
                    await wait_for_page(page)
                continue

            # 일반 클릭
            if len(step) > 1:
                await safe_click(page, step)
                await wait_for_page(page)

        return {'success': True, 'error': ''}

    except Exception as e:
        return {'success': False, 'error': str(e)}

def save_results_to_excel(all_results):
    """결과를 엑셀에 저장 - '개편수정' 시트와 동일한 양식"""
    # 원본 엑셀 읽기
    df_original = pd.read_excel(EXCEL_FILE, sheet_name='개편수정', header=None)

    # 결과 DataFrame 생성 (원본 형식 완전히 유지)
    result_data = []

    # 헤더 영역 (행 0-9)
    result_data.append(['', f'■ AIDT LMS QA 테스트 결과 ({TODAY})', '', '', '', '', '', ''])
    result_data.append(['', '', '', '', '', '', '', ''])
    result_data.append(['', 'Title', '서비스 기본 동작 점검', '', '', '', '', ''])
    result_data.append(['', 'Test 목적', '전체 기능 QA 테스트', '', '', '', '', ''])
    result_data.append(['', '릴리스 내용', '', '', '', '', '', ''])
    result_data.append(['', 'Tester', '자동화 테스트', '', '', '', '', ''])
    result_data.append(['', '서버', '운영계', '', '', '', '', ''])
    result_data.append(['', 'URL', ENTRY_URL, '', '', '', '', ''])
    result_data.append(['', '', '', '', '', '', '검증 결과', ''])
    result_data.append(['', '과목', '권한', 'Step1', 'Step2', '경로', '결과', '오류 현상 및 비고'])

    # 데이터 영역
    for r in all_results:
        result_data.append([
            '',  # 빈 컬럼
            r.get('subject', ''),  # 과목
            r['role'],  # 권한 (교사/학생)
            r['step1'],
            r['step2'],
            r['path'],
            r['result'],
            r['error_note']
        ])

    result_df = pd.DataFrame(result_data)

    # 엑셀에 새 시트로 저장
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        result_df.to_excel(writer, sheet_name=TODAY, index=False, header=False)

    print(f"\n결과 저장 완료: {EXCEL_FILE} (시트: {TODAY})")

async def run_interactive_test(page, test_data, test_num, total):
    """인터랙티브 테스트 수행"""
    idx = test_data['idx']
    step1 = test_data['step1']
    step2 = test_data['step2']
    path = test_data['path']
    role = test_data['role']

    print(f"\n{'='*70}")
    print(f"[{test_num}/{total}] [{role}] {step1} > {step2}")
    print(f"경로: {path}")
    print(f"{'='*70}")

    # 스크린샷 저장
    screenshot_file = await take_screenshot(page, f"{role}_{idx}_before")

    # 사용자 입력 대기
    print("\n테스트를 수행한 후 결과를 입력하세요:")
    print("  P = PASS")
    print("  F = FAIL")
    print("  S = 스킵")
    print("  Q = 종료")
    print("  R = 재시도")

    while True:
        result_input = input("\n결과 입력 (P/F/S/Q/R): ").strip().upper()

        if result_input == 'P':
            result = 'PASS'
            error_note = ''
            break
        elif result_input == 'F':
            result = 'FAIL'
            error_note = input("오류 현상 및 비고를 입력하세요: ").strip()
            break
        elif result_input == 'S':
            result = 'SKIP'
            error_note = '스킵됨'
            break
        elif result_input == 'Q':
            return None  # 종료 신호
        elif result_input == 'R':
            return await run_interactive_test(page, test_data, test_num, total)
        else:
            print("잘못된 입력입니다. P/F/S/Q/R 중 하나를 입력하세요.")

    # 결과 스크린샷
    await take_screenshot(page, f"{role}_{idx}_after")

    return {
        'idx': idx,
        'role': role,
        'step1': step1,
        'step2': step2,
        'path': path,
        'result': result,
        'error_note': error_note
    }

async def main():
    """메인 테스트 실행 - 교사/학생 구분하여 전체 QA 수행"""
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("AIDT LMS 전체 QA 테스트")
    print(f"날짜: {TODAY}")
    print(f"URL: {ENTRY_URL}")
    print("=" * 70)
    sys.stdout.flush()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='ko-KR'
        )
        page = await context.new_page()

        try:
            # Entry URL 접속
            print("\n1. Entry URL 접속 중...")
            sys.stdout.flush()
            await page.goto(ENTRY_URL, timeout=60000)
            await wait_for_page(page, timeout=10000)
            print("   -> 접속 완료")
            sys.stdout.flush()

            # window.open 패치
            await patch_window_open(page)
            print("   -> window.open 패치 완료")
            sys.stdout.flush()

            # 로그인 대기 (30초)
            print("\n2. 로그인 대기 중... (30초)")
            print("   브라우저에서 로그인을 완료해주세요.")
            sys.stdout.flush()
            await asyncio.sleep(30)
            await wait_for_page(page)
            print("   -> 로그인 대기 완료")
            sys.stdout.flush()

            # 교사 테스트
            print("\n3. 교사 테스트 시작...")
            sys.stdout.flush()
            teacher_results = await run_teacher_tests(page)
            print(f"\n   교사 테스트 완료: {len(teacher_results)}개 항목")
            sys.stdout.flush()

            # 학생 테스트
            print("\n4. 학생 테스트 시작...")
            print("   (학생 계정으로 전환하거나 동일 페이지에서 계속)")
            sys.stdout.flush()
            student_results = await run_student_tests(page, browser)
            print(f"\n   학생 테스트 완료: {len(student_results)}개 항목")
            sys.stdout.flush()

            # 결과 합치기
            all_results = teacher_results + student_results

            # 결과 저장
            print("\n5. 결과 저장 중...")
            sys.stdout.flush()
            save_results_to_excel(all_results)

            # 요약
            pass_count = sum(1 for r in all_results if r['result'] == 'PASS')
            fail_count = sum(1 for r in all_results if r['result'] == 'FAIL')
            print(f"\n{'='*70}")
            print(f"테스트 완료 요약")
            print(f"{'='*70}")
            print(f"총 {len(all_results)}개 항목 테스트 완료")
            print(f"  - 교사: {len(teacher_results)}개 (PASS: {sum(1 for r in teacher_results if r['result'] == 'PASS')}, FAIL: {sum(1 for r in teacher_results if r['result'] == 'FAIL')})")
            print(f"  - 학생: {len(student_results)}개 (PASS: {sum(1 for r in student_results if r['result'] == 'PASS')}, FAIL: {sum(1 for r in student_results if r['result'] == 'FAIL')})")
            print(f"  - 전체 PASS: {pass_count}, FAIL: {fail_count}")
            print(f"{'='*70}")
            sys.stdout.flush()

        except Exception as e:
            print(f"오류 발생: {e}")
            sys.stdout.flush()
            import traceback
            traceback.print_exc()
        finally:
            print("\n브라우저를 종료합니다...")
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
