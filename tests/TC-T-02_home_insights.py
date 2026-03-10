"""
TC-T-02: 홈 오늘수업 카드 인사이트 노출유무 확인
- 각 카드에 인사이트(데이터)가 정상적으로 노출되는지 확인

확인 대상:
1. 프로필 섹션 (프로필 이미지, 선생님 이름, 학급 이름, 학급 분석 버튼)
2. 오늘수업 카드 (단원, 차시, 수업명)
3. 교과서 카드 (재구성 하기 버튼)
4. 진도 카드 (2개 노출, 단원명/모듈명)
5. 출석체크 카드 (전체, 출석, 미출석, 미동의)
6. 진행중인 과제 카드 (총 N건, 제출 현황)
7. 수업 분석 카드 (학생현황: 학습수준, 학습태도, AI진단평가점수, AI형성평가점수)
8. 오답노트 카드 (복습 전, 복습 완료, 복습률)
9. 우리반 기분 카드 (5가지 분류)
10. 공지사항 카드 (분류값, 타이틀, 날짜)

실행 방법:
    python TC-T-02_home_insights.py
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json
import re

LOAD_WAIT = 5
MAX_WAIT = 60


async def test_home_insights():
    """TC-T-02: 홈 카드 인사이트 노출 확인 테스트"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"
    SCREENSHOT_DIR = "screenshots"

    results = {
        "test_name": "TC-T-02: 홈 카드 인사이트 노출 확인",
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": TEST_URL,
        "steps": [],
        "card_checks": {},
        "overall_result": "PASS",
        "errors": []
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        entry_page = await context.new_page()

        try:
            # Step 1: 진입 페이지 접속
            print("=" * 60)
            print("Step 1: 진입 페이지 접속")
            print("=" * 60)

            await entry_page.goto(TEST_URL, timeout=60000)
            await entry_page.wait_for_load_state("networkidle")
            await asyncio.sleep(LOAD_WAIT)

            results["steps"].append({"step": 1, "action": "진입 페이지 접속", "status": "PASS"})

            # Step 2: 선생님 입장하기 (새 창)
            print("\n" + "=" * 60)
            print("Step 2: 선생님 입장하기 (새 창)")
            print("=" * 60)

            teacher_btn = entry_page.locator("button").filter(has_text="선생님 입장하기")

            async with context.expect_page(timeout=MAX_WAIT * 1000) as new_page_info:
                await teacher_btn.click()
                print("   버튼 클릭 완료")

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

            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc02_main_page.png", full_page=True)
            print(f"   현재 URL: {main_page.url}")
            results["steps"].append({"step": 2, "action": "새 창 진입", "status": "PASS"})

            # Step 3: 카드별 인사이트 확인
            print("\n" + "=" * 60)
            print("Step 3: 카드별 인사이트 노출 확인")
            print("=" * 60)

            # ===== 0. 프로필 섹션 =====
            print("\n   [0. 프로필 섹션] 확인 중...")
            profile_details = {
                "프로필_이미지": False,
                "선생님_이름": "미발견",
                "학급_이름": "미발견",
                "학급_분석_버튼": False
            }

            try:
                # 프로필 이미지 (teacher-profile__image)
                profile_img_count = await main_page.locator(".teacher-profile__image").count()
                profile_details["프로필_이미지"] = profile_img_count > 0

                # 선생님 이름 (profile-section__name)
                name_count = await main_page.locator(".profile-section__name").count()
                if name_count > 0:
                    profile_details["선생님_이름"] = await main_page.locator(".profile-section__name").first.inner_text()

                # 학급 이름 (profile-section__class)
                class_count = await main_page.locator(".profile-section__class").count()
                if class_count > 0:
                    profile_details["학급_이름"] = await main_page.locator(".profile-section__class").first.inner_text()

                # 학급 분석 버튼 (profile-section__btn)
                btn_count = await main_page.locator(".profile-section__btn").count()
                profile_details["학급_분석_버튼"] = btn_count > 0

            except:
                pass

            profile_pass = (profile_details["프로필_이미지"] and
                          profile_details["선생님_이름"] != "미발견" and
                          profile_details["학급_이름"] != "미발견" and
                          profile_details["학급_분석_버튼"])

            results["card_checks"]["프로필 섹션"] = {
                "found": profile_pass,
                "details": profile_details,
                "status": "PASS" if profile_pass else "FAIL"
            }
            print(f"      프로필_이미지: {'OK' if profile_details['프로필_이미지'] else 'FAIL'}")
            print(f"      선생님_이름: {profile_details['선생님_이름']}")
            print(f"      학급_이름: {profile_details['학급_이름']}")
            print(f"      학급_분석_버튼: {'OK' if profile_details['학급_분석_버튼'] else 'FAIL'}")

            # ===== 1. 오늘수업 카드 =====
            print("\n   [1. 오늘수업 카드] 확인 중...")
            today_details = {
                "chapter": "미발견",
                "session": "미발견",
                "lesson_name": "미발견"
            }

            try:
                today_elem = main_page.locator("[class*='today']").first
                today_text = await today_elem.inner_text()

                # 단원 추출
                chapter_match = re.search(r'(\d+단원[^\n]*)', today_text)
                if chapter_match:
                    today_details["chapter"] = chapter_match.group(1).strip()

                # 차시 추출
                session_match = re.search(r'(\d+차시)', today_text)
                if session_match:
                    today_details["session"] = session_match.group(1)

                # 수업명 추출 (Lesson 또는 단원 제목)
                lesson_match = re.search(r'(Lesson[^,\n]*|[\w\s]+Project|Language in Use)', today_text)
                if lesson_match:
                    today_details["lesson_name"] = lesson_match.group(1).strip()

            except:
                pass

            today_pass = today_details["chapter"] != "미발견" or today_details["lesson_name"] != "미발견"
            results["card_checks"]["오늘수업 카드"] = {
                "found": today_pass,
                "details": today_details,
                "status": "PASS" if today_pass else "FAIL"
            }
            print(f"      단원: {today_details['chapter']}")
            print(f"      차시: {today_details['session']}")
            print(f"      수업명: {today_details['lesson_name']}")

            # ===== 2. 교과서 카드 (재구성 하기 버튼) =====
            print("\n   [2. 교과서 카드] 확인 중...")
            textbook_found = False
            restructure_btn_found = False

            try:
                textbook_elem = main_page.locator("[class*='textbook']").first
                await textbook_elem.inner_text()
                textbook_found = True

                # 재구성 하기 버튼 확인
                restructure_btn = await main_page.locator("button:has-text('재구성')").count()
                restructure_btn_found = restructure_btn > 0
            except:
                pass

            results["card_checks"]["교과서 카드"] = {
                "found": textbook_found,
                "restructure_btn": restructure_btn_found,
                "status": "PASS" if (textbook_found and restructure_btn_found) else "FAIL"
            }
            print(f"      카드: {'OK' if textbook_found else 'FAIL'}, 재구성 하기 버튼: {'OK' if restructure_btn_found else 'FAIL'}")

            # ===== 3. 진도 카드 (2개 노출, 단원명/모듈명) =====
            print("\n   [3. 진도 카드] 확인 중...")
            progress_count = 0
            progress_cards_info = []

            try:
                # 뷰포트 크기 가져오기
                viewport = main_page.viewport_size
                viewport_width = viewport['width'] if viewport else 1920

                # textbook-section__viewport 컨테이너 찾기
                viewport_container = main_page.locator(".textbook-section__viewport").first
                container_box = await viewport_container.bounding_box()
                container_right = container_box['x'] + container_box['width'] if container_box else viewport_width

                # 모든 progress-card 가져오기
                all_progress = await main_page.locator(".progress-card").all()

                for i, progress_elem in enumerate(all_progress):
                    try:
                        # bounding box 확인
                        box = await progress_elem.bounding_box()
                        if not box:
                            continue

                        # 컨테이너 영역 내에 있는지 확인 (x 시작점이 컨테이너 끝보다 작아야 함)
                        if box['x'] >= container_right:
                            continue

                        card_text = await progress_elem.inner_text()

                        # 단원명 추출
                        chapter_match = re.search(r'(\d+단원[^\n]*)', card_text)
                        chapter_name = chapter_match.group(1).strip() if chapter_match else "단원명 없음"

                        # 모듈명 추출
                        module_patterns = [
                            "AI 단원 진단평가", "Before You Begin", "Watch and Talk",
                            "Language in Use", "AI Writing", "Culture Project"
                        ]
                        module_name = "모듈명 없음"
                        for mp in module_patterns:
                            if mp in card_text:
                                module_name = mp
                                break

                        progress_cards_info.append({
                            "chapter": chapter_name[:50],
                            "module": module_name
                        })
                    except:
                        pass

                progress_count = len(progress_cards_info)

            except:
                pass

            # 정확히 2개 확인
            progress_pass = progress_count == 2
            results["card_checks"]["진도 카드"] = {
                "count": progress_count,
                "expected_count": 2,
                "cards": progress_cards_info,
                "status": "PASS" if progress_pass else "FAIL"
            }
            print(f"      진도 카드 수: {progress_count}개 (정확히 2개 필요)")
            for i, info in enumerate(progress_cards_info):
                print(f"      [{i+1}] 단원: {info['chapter']}, 모듈: {info['module']}")

            # ===== 4. 출석체크 카드 =====
            print("\n   [4. 출석체크 카드] 확인 중...")
            attendance_details = {
                "total": "미발견",
                "present": "미발견",
                "absent": "미발견",
                "not_agreed": "미발견"
            }

            try:
                attendance_elem = main_page.locator("[class*='attendance']").first
                attendance_text = await attendance_elem.inner_text()

                # 전체
                total_match = re.search(r'전체\s*(\d+)명', attendance_text)
                if total_match:
                    attendance_details["total"] = total_match.group(1) + "명"

                # 출석
                present_match = re.search(r'출석\s*(\d+)명', attendance_text)
                if present_match:
                    attendance_details["present"] = present_match.group(1) + "명"

                # 미출석
                absent_match = re.search(r'미출석\s*(\d+)명', attendance_text)
                if absent_match:
                    attendance_details["absent"] = absent_match.group(1) + "명"

                # 미동의
                not_agreed_match = re.search(r'미동의\s*(\d+)명', attendance_text)
                if not_agreed_match:
                    attendance_details["not_agreed"] = not_agreed_match.group(1) + "명"

            except:
                pass

            attendance_pass = all(v != "미발견" for v in attendance_details.values())
            results["card_checks"]["출석체크 카드"] = {
                "found": True,
                "details": attendance_details,
                "status": "PASS" if attendance_pass else "FAIL"
            }
            print(f"      전체: {attendance_details['total']}, 출석: {attendance_details['present']}, 미출석: {attendance_details['absent']}, 미동의: {attendance_details['not_agreed']}")

            # ===== 5. 진행중인 과제 카드 =====
            print("\n   [5. 진행중인 과제 카드] 확인 중...")
            assignment_details = {
                "total_count": "미발견",
                "submission_status": [],
                "evaluation_status": []
            }

            try:
                # assignment-section 클래스에서 전체 HTML 가져오기
                assignment_elem = main_page.locator(".assignment-section")
                assignment_text = await assignment_elem.inner_text()

                # N건 패턴 찾기 (총 과제 수)
                total_match = re.search(r'(\d+)\s*건', assignment_text)
                if total_match:
                    assignment_details["total_count"] = total_match.group(1) + "건"

                # 제출 N/N 찾기
                submission_matches = re.findall(r'제출[^\d]*(\d+)/(\d+)', assignment_text)
                for num, denom in submission_matches:
                    assignment_details["submission_status"].append(f"제출 {num}/{denom}")

                # 평가 N/N 찾기
                evaluation_matches = re.findall(r'평가[^\d]*(\d+)/(\d+)', assignment_text)
                for num, denom in evaluation_matches:
                    assignment_details["evaluation_status"].append(f"평가 {num}/{denom}")

            except:
                pass

            assignment_pass = assignment_details["total_count"] != "미발견"
            results["card_checks"]["진행중인 과제 카드"] = {
                "found": assignment_pass,
                "details": assignment_details,
                "status": "PASS" if assignment_pass else "FAIL"
            }
            print(f"      총 과제 수: {assignment_details['total_count']}")
            print(f"      제출 현황: {assignment_details['submission_status']}")
            print(f"      평가 현황: {assignment_details['evaluation_status']}")

            # ===== 6. 수업 분석 카드 =====
            print("\n   [6. 수업 분석 카드] 확인 중...")
            analysis_details = {
                "학생_현황": False,
                "학습_수준": "미발견",
                "학습_태도": "미발견",
                "AI_단원_진단평가_점수": "미발견",
                "AI_형성평가_점수": "미발견"
            }

            try:
                analysis_elem = main_page.locator("[class*='analysis']").first
                analysis_text = await analysis_elem.inner_text()

                # 학생 현황
                analysis_details["학생_현황"] = "학생 현황" in analysis_text or "학생현황" in analysis_text

                # 학습 수준 (4개 값)
                level_idx = analysis_text.find("학습 수준")
                attitude_idx = analysis_text.find("학습 태도")
                if level_idx != -1 and attitude_idx != -1:
                    level_section = analysis_text[level_idx:attitude_idx]
                    level_values = re.findall(r'(\d+)명', level_section)
                    if len(level_values) >= 4:
                        analysis_details["학습_수준"] = ", ".join([v + "명" for v in level_values[:4]])

                # 학습 태도 (4개 값)
                if attitude_idx != -1:
                    ai_idx = analysis_text.find("AI 단원")
                    if ai_idx != -1 and ai_idx > attitude_idx:
                        attitude_section = analysis_text[attitude_idx:ai_idx]
                        attitude_values = re.findall(r'(\d+)명', attitude_section)
                        if len(attitude_values) >= 4:
                            analysis_details["학습_태도"] = ", ".join([v + "명" for v in attitude_values[:4]])

                # AI 점수 - ai-chart__score 클래스에서 직접 가져오기
                ai_score_elems = await main_page.locator(".ai-chart__score").all()
                if len(ai_score_elems) >= 1:
                    score1 = await ai_score_elems[0].inner_text()
                    analysis_details["AI_단원_진단평가_점수"] = score1.strip()
                if len(ai_score_elems) >= 2:
                    score2 = await ai_score_elems[1].inner_text()
                    analysis_details["AI_형성평가_점수"] = score2.strip()

            except:
                pass

            analysis_pass = analysis_details["학생_현황"]
            results["card_checks"]["수업 분석 카드"] = {
                "found": True,
                "details": analysis_details,
                "status": "PASS" if analysis_pass else "FAIL"
            }
            print(f"      학생_현황: {analysis_details['학생_현황']}")
            print(f"      학습_수준: {analysis_details['학습_수준']}")
            print(f"      학습_태도: {analysis_details['학습_태도']}")
            print(f"      AI_단원_진단평가_점수: {analysis_details['AI_단원_진단평가_점수']}")
            print(f"      AI_형성평가_점수: {analysis_details['AI_형성평가_점수']}")

            # ===== 7. 오답노트 카드 =====
            print("\n   [7. 오답노트 카드] 확인 중...")
            wrongnote_details = {
                "복습_전": "미발견",
                "복습_완료": "미발견",
                "복습률": "미발견"
            }

            try:
                # 전체 페이지 텍스트에서 오답노트 관련 정보 추출
                body_text = await main_page.locator("body").inner_text()

                # 복습 전 N개
                before_match = re.search(r'복습\s*전[^\d]*(\d+)개', body_text)
                if before_match:
                    wrongnote_details["복습_전"] = before_match.group(1) + "개"

                # 복습 완료 N개
                complete_match = re.search(r'복습\s*완료[^\d]*(\d+)개', body_text)
                if complete_match:
                    wrongnote_details["복습_완료"] = complete_match.group(1) + "개"

                # 복습률 - donut-center__number 클래스에서 가져오기
                donut_elem = main_page.locator(".donut-center__number").first
                if await donut_elem.count() > 0:
                    rate_text = await donut_elem.inner_text()
                    # 숫자만 추출
                    rate_match = re.search(r'(\d+)', rate_text)
                    if rate_match:
                        wrongnote_details["복습률"] = rate_match.group(1) + "%"

            except:
                pass

            wrongnote_pass = (wrongnote_details["복습_전"] != "미발견" or
                            wrongnote_details["복습_완료"] != "미발견" or
                            wrongnote_details["복습률"] != "미발견")
            results["card_checks"]["오답노트 카드"] = {
                "found": wrongnote_pass,
                "details": wrongnote_details,
                "status": "PASS" if wrongnote_pass else "FAIL"
            }
            print(f"      복습_전: {wrongnote_details['복습_전']}, 복습_완료: {wrongnote_details['복습_완료']}, 복습률: {wrongnote_details['복습률']}")

            # ===== 8. 우리반 기분 카드 (5가지 분류) =====
            print("\n   [8. 우리반 기분 카드] 확인 중...")
            mood_details = {
                "counts": [],
                "classification_count": 0
            }

            try:
                # 전체 페이지 텍스트에서 우리반 기분 관련 정보 추출
                body_text = await main_page.locator("body").inner_text()

                # "우리반 기분" 뒤에 오는 N명 패턴 5개 찾기
                mood_section_match = re.search(r'우리반\s*기분[^\d]*([^\n]+)', body_text)
                if mood_section_match:
                    mood_section = mood_section_match.group(1)
                    # N명 패턴 추출
                    mood_counts = re.findall(r'(\d+)명', mood_section)
                    mood_details["counts"] = mood_counts[:5]
                    mood_details["classification_count"] = len(mood_counts[:5])

                # 위에서 찾지 못하면 전체에서 패턴 검색
                if mood_details["classification_count"] < 5:
                    # "우리반 기분 2명 3명 0명 0명 0명" 패턴 찾기
                    full_match = re.search(r'우리반\s*기분[^\d]*(\d+)명[^\d]*(\d+)명[^\d]*(\d+)명[^\d]*(\d+)명[^\d]*(\d+)명', body_text)
                    if full_match:
                        mood_details["counts"] = [full_match.group(i) + "명" for i in range(1, 6)]
                        mood_details["classification_count"] = 5

            except:
                pass

            mood_pass = mood_details["classification_count"] >= 5
            results["card_checks"]["우리반 기분 카드"] = {
                "found": mood_pass,
                "details": mood_details,
                "status": "PASS" if mood_pass else "FAIL"
            }
            print(f"      분류 수: {mood_details['classification_count']}개 (5개 필요)")
            print(f"      값: {mood_details['counts']}")

            # ===== 9. 공지사항 카드 =====
            print("\n   [9. 공지사항 카드] 확인 중...")
            notice_details = {
                "category": "미발견",
                "titles": [],
                "dates": []
            }

            try:
                # 공지사항/게시판 관련 요소 찾기
                notice_elem = main_page.locator("[class*='board'], [class*='notice']").first
                notice_text = await notice_elem.inner_text()

                # 분류값 (공지사항, 학급게시판 등)
                category_patterns = ["공지사항", "학급게시판", "게시판", "공지"]
                for cp in category_patterns:
                    if cp in notice_text:
                        notice_details["category"] = cp
                        break

                # 날짜 패턴
                dates = re.findall(r'(\d{4}\.\d{2}\.\d{2})', notice_text)
                notice_details["dates"] = dates[:5]

                # 타이틀 (날짜 앞의 텍스트들)
                # 공지사항 구조에서 제목 추출 시도

            except:
                pass

            notice_pass = notice_details["category"] != "미발견" and len(notice_details["dates"]) > 0
            results["card_checks"]["공지사항 카드"] = {
                "found": notice_pass,
                "details": notice_details,
                "status": "PASS" if notice_pass else "FAIL"
            }
            print(f"      분류값: {notice_details['category']}")
            print(f"      날짜: {notice_details['dates']}")

            # 최종 스크린샷
            await main_page.screenshot(path=f"{SCREENSHOT_DIR}/tc02_final.png", full_page=True)

            # 결과 요약
            print("\n" + "=" * 60)
            print("테스트 결과 요약")
            print("=" * 60)
            print(f"   테스트명: {results['test_name']}")
            print(f"   실행일시: {results['test_date']}")

            # 전체 결과 계산
            fail_count = sum(1 for c in results["card_checks"].values() if c["status"] == "FAIL")
            results["overall_result"] = "PASS" if fail_count == 0 else "FAIL"
            print(f"   최종 결과: {results['overall_result']}")

            print("\n   [카드별 결과]")
            for card, check in results["card_checks"].items():
                status = check["status"]
                print(f"      [{status}] {card}")

            with open("test_result_TC-T-02.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n   결과 저장: test_result_TC-T-02.json")

            print("\n10초 후 종료...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()
            results["overall_result"] = "ERROR"
            results["errors"].append(str(e))

        finally:
            await browser.close()

    return results


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)

    print("=" * 60)
    print("TC-T-02: 홈 카드 인사이트 노출 확인 테스트 시작")
    print("=" * 60)

    asyncio.run(test_home_insights())
