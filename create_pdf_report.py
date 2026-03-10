# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from datetime import datetime
import json
import os

# 한글 폰트 등록
pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))

# 테스트 데이터 정의
test_data = {
    "TC-T-01": {
        "name": "교사 홈 진입 테스트",
        "date": "2026-03-10 12:45:51",
        "result": "PASS",
        "steps": [
            (1, "진입 페이지 접속", "진입 페이지", "진입 URL 접속 완료", "PASS"),
            (2, "선생님 입장하기 클릭 및 새 창 진입", "메인 페이지 진입", "선생님 입장하기 버튼 클릭 > 새 창으로 메인 페이지 이동", "PASS"),
            (3, "메인 페이지 요소 확인", "오늘 수업/수업 시작하기", "[class*='today'] 요소 확인", "PASS"),
            (4, "메인 페이지 요소 확인", "교과서", "[class*='textbook'] 요소 확인", "PASS"),
            (5, "메인 페이지 요소 확인", "출석체크", "[class*='attendance'] 요소 확인", "PASS"),
            (6, "메인 페이지 요소 확인", "과제", "[class*='assignment'] 요소 확인", "PASS"),
            (7, "메인 페이지 요소 확인", "수업 분석/학급 분석", "[class*='analysis'] 요소 확인", "PASS"),
            (8, "메인 페이지 요소 확인", "우리반 기분", "[class*='mood'] 요소 확인", "PASS"),
            (9, "메인 페이지 요소 확인", "게시판/공지사항", "[class*='board'] 요소 확인", "PASS"),
        ]
    },
    "TC-T-02": {
        "name": "홈 카드 인사이트 노출 확인",
        "date": "2026-03-10 12:47:00",
        "result": "PASS",
        "steps": [
            (1, "진입 페이지 접속", "진입 페이지", "진입 URL 접속 완료", "PASS"),
            (2, "새 창 진입", "메인 페이지 진입", "선생님 입장하기 > 메인 페이지 이동", "PASS"),
            (3, "프로필 섹션 확인", "프로필 섹션", "최파랑 선생님, 전시관_1 학급, 학급 분석 버튼 확인", "PASS"),
            (4, "오늘수업 카드 확인", "오늘수업 카드", "Lesson 1. The Future Is in Our Hands", "PASS"),
            (5, "교과서 카드 확인", "교과서 카드", "재구성하기 버튼 확인", "PASS"),
            (6, "진도 카드 확인", "진도 카드", "2개: AI 단원 진단평가, Before You Begin", "PASS"),
            (7, "출석체크 카드 확인", "출석체크 카드", "총 5명, 출석 0명, 결석 5명", "PASS"),
            (8, "진행중인 과제 카드 확인", "진행중인 과제 카드", "총 4건, 제출 현황 확인", "PASS"),
            (9, "수업 분석 카드 확인", "수업 분석 카드", "AI 단원 진단평가 60점, AI 형성평가 58점", "PASS"),
            (10, "오답노트 카드 확인", "오답노트 카드", "복습 전 62개, 복습 완료 3개, 복습률 5%", "PASS"),
            (11, "우리반 기분 카드 확인", "우리반 기분 카드", "1명, 2명, 2명, 0명, 0명 분포 확인", "PASS"),
            (12, "공지사항 카드 확인", "공지사항 카드", "공지 3건 (2026.03.06, 2026.03.09, 2026.02.09)", "PASS"),
        ]
    },
    "TC-T-03": {
        "name": "수업 시작하기 버튼 테스트",
        "date": "2026-03-10 12:48:08",
        "result": "PASS",
        "steps": [
            (1, "선생님 입장하기", "진입 페이지", "선생님 입장하기 버튼 클릭", "PASS"),
            (2, "수업 시작하기 버튼 확인", "버튼 노출", "수업 시작하기 버튼 존재 확인", "PASS"),
            (3, "수업 시작하기 클릭 및 새 창 확인", "새 창 열림", "새 창 URL 확인", "PASS"),
            (4, "수업 뷰어 페이지 로딩", "뷰어 로딩", "뷰어 페이지 로딩 완료", "PASS"),
            (5, "뷰어 페이지 요소 확인", "뷰어 컨테이너", "뷰어 컨테이너 1개 확인", "PASS"),
            (6, "뷰어 페이지 요소 확인", "메뉴/네비게이션", "메뉴 또는 네비게이션 3개 확인", "PASS"),
            (7, "뷰어 페이지 요소 확인", "컨텐츠 영역", "컨텐츠 영역 24개 확인", "PASS"),
            (8, "뷰어 URL 패턴 확인", "뷰어 URL", "https://eng-mn1-mid-2.aidt.ai/v-web/.../entrance?mode=default", "CHECK"),
        ]
    },
    "TC-T-04": {
        "name": "교과서 보기 버튼 테스트",
        "date": "2026-03-10 12:50:22",
        "result": "PASS",
        "steps": [
            (1, "선생님 입장하기", "진입 페이지", "선생님 입장하기 버튼 클릭", "PASS"),
            (2, "교과서 메뉴 클릭", "LNB 메뉴", "교과서 메뉴 클릭 > 단원 리스트 페이지 이동", "PASS"),
            (3, "단원 리스트 노출 확인", "단원 리스트", "단원 텍스트 존재 확인", "PASS"),
            (4, "단원 번호 오름차순 확인", "단원 번호 순서", "1, 2, 3, 4, 5, 6, 7, 8 오름차순 확인", "PASS"),
            (5, "교과서 보기 버튼 클릭", "버튼 클릭", "교과서 보기 버튼 클릭", "PASS"),
            (6, "뷰어 새 창 확인", "새 창 열림", "URL: https://eng-mn1-mid-2.aidt.ai/v-web/...", "PASS"),
            (7, "콘텐츠 정상 노출 확인", "콘텐츠 노출", "뷰어 컨테이너 1개, 콘텐츠 영역 2개 확인", "PASS"),
        ]
    },
    "TC-T-05": {
        "name": "단원 상세 보기 테스트",
        "date": "2026-03-10 12:52:41",
        "result": "PASS",
        "steps": [
            (1, "선생님 입장하기", "진입 페이지", "선생님 입장하기 버튼 클릭", "PASS"),
            (2, "교과서 메뉴 클릭", "LNB 메뉴", "교과서 메뉴 클릭 > 단원 리스트 페이지 이동", "PASS"),
            (3, "단원 리스트 노출 확인", "단원 리스트", "단원 텍스트 존재 확인", "PASS"),
            (4, "단원 번호 오름차순 확인", "단원 번호 순서", "1, 2, 3, 4, 5, 6, 7, 8 오름차순 확인", "PASS"),
            (5, "단원 상세 보기 버튼 클릭", "버튼 클릭", "단원 상세 보기 버튼 8개 중 첫 번째 클릭", "PASS"),
            (6, "모듈 리스트 노출 확인", "모듈 리스트", "모듈, Reading, Talk, Watch 키워드, ViewerLinkBox 23개", "PASS"),
            (7, "모듈 클릭 및 뷰어 새 창 확인", "새 창 열림", "URL: https://eng-mn1-mid-2.aidt.ai/v-web/...", "PASS"),
            (8, "콘텐츠 정상 노출 확인", "콘텐츠 노출", "뷰어 컨테이너 1개, 콘텐츠 영역 24개 확인", "PASS"),
        ]
    },
    "TC-T-06": {
        "name": "재구성하기 테스트",
        "date": "2026-03-10 12:55:09",
        "result": "PASS",
        "steps": [
            (1, "선생님 입장하기", "진입 페이지", "선생님 입장하기 버튼 클릭", "PASS"),
            (2, "교과서 메뉴 클릭", "LNB 메뉴", "교과서 메뉴 클릭 > 단원 리스트 페이지 이동", "PASS"),
            (3, "단원 리스트 노출 확인", "단원 리스트", "단원 텍스트 존재 확인", "PASS"),
            (4, "재구성하기 버튼 클릭", "버튼 클릭", "재구성하기 버튼 8개 중 첫 번째 클릭", "PASS"),
            (5, "재구성 페이지 확인", "페이지 전환", "URL: .../textbook/detail/49727, 키워드: 재구성, 저장 확인", "PASS"),
            (6, "임시저장 삭제 버튼 확인", "삭제 버튼", "임시저장 삭제 버튼 없음", "SKIP"),
            (7, "임시저장 버튼 클릭", "저장 버튼", "임시저장 버튼 1개 클릭", "PASS"),
            (8, "미리보기 뷰어 확인", "뷰어 새 창", "URL: .../entrance?mode=course_preview, 목차 키워드 확인", "PASS"),
        ]
    },
    "TC-T-07": {
        "name": "재구성 배포 동작 확인",
        "date": "2026-03-10 12:56:43",
        "result": "PASS",
        "steps": [
            (1, "선생님 입장하기", "진입 페이지", "선생님 입장하기 버튼 클릭", "PASS"),
            (2, "교과서 메뉴 클릭", "LNB 메뉴", "교과서 메뉴 클릭 > 단원 리스트 페이지 이동", "PASS"),
            (3, "단원 리스트 노출 확인", "단원 리스트", "단원 텍스트 존재 확인", "PASS"),
            (4, "재구성하기 버튼 클릭", "버튼 클릭", "재구성하기 버튼 8개 중 첫 번째 클릭", "PASS"),
            (5, "재구성 페이지 확인", "페이지 전환", "URL: .../textbook/detail/49565, 키워드: 재구성, 저장, 배포 확인", "PASS"),
            (6, "임시저장 삭제 버튼 확인", "삭제 버튼", "임시저장 삭제 버튼 없음", "SKIP"),
            (7, "임시저장 버튼 클릭", "저장 버튼", "임시저장 버튼 1개 클릭", "PASS"),
            (8, "배포 버튼 클릭", "배포 버튼", "배포 버튼 1개 클릭", "PASS"),
            (9, "배포 확인 버튼 클릭", "모달 확인", "배포 확인 모달 버튼 클릭", "PASS"),
        ]
    },
    "TC-T-08": {
        "name": "단원 초기화 동작 확인",
        "date": "2026-03-10 12:58:10",
        "result": "PASS",
        "steps": [
            (1, "선생님 입장하기", "진입 페이지", "선생님 입장하기 버튼 클릭 > 메인 페이지 이동", "PASS"),
            (2, "교과서 메뉴 클릭", "LNB 메뉴", "교과서 메뉴 클릭 > 단원 리스트 노출", "PASS"),
            (3, "단원 리스트 확인", "단원 노출", "단원 텍스트 존재 확인 (found: True)", "PASS"),
            (4, "재구성하기 버튼 클릭", "버튼 클릭", "첫 번째 단원 재구성하기 버튼 클릭 (8개 중)", "PASS"),
            (5, "재구성 페이지 확인", "페이지 전환", "URL 변경 및 키워드 확인 (재구성, 저장, 초기화)", "PASS"),
            (6, "임시저장 삭제", "삭제 동작", "임시저장 삭제 버튼 클릭 > 모달 확인 버튼 클릭", "PASS"),
            (7, "임시저장 버튼 클릭", "저장 동작", "임시저장 버튼 클릭 > 데이터 생성 확인", "PASS"),
            (8, "초기화 버튼 클릭", "버튼 클릭", "초기화 버튼 클릭 (1개 발견)", "PASS"),
            (9, "초기화 확인", "모달 + 토스트", "초기화 확인 모달 클릭 > 17초 후 토스트 알림 확인", "PASS"),
        ]
    },
    "TC-T-09": {
        "name": "모둠활동 작성하기 - 타일형",
        "date": "2026-03-10 13:00:02",
        "result": "PASS",
        "steps": [
            (1, "선생님 입장하기", "진입 페이지", "선생님 입장하기 버튼 클릭 > 메인 페이지 이동", "PASS"),
            (2, "모둠활동 메뉴 클릭", "LNB 메뉴", "모둠활동 메뉴 클릭 > 모둠활동 리스트 페이지 이동", "PASS"),
            (3, "모둠활동 페이지 확인", "페이지 노출", "모둠활동 리스트 페이지 키워드 확인 (found: True)", "PASS"),
            (4, "작성하기 버튼 클릭", "버튼 클릭", "작성하기 버튼 클릭 (1개 발견)", "PASS"),
            (5, "활동 만들기 팝업 확인", "팝업 노출", "활동 만들기 팝업 키워드 확인 (found: True)", "PASS"),
            (6, "활동 이름 입력", "입력 필드", "활동 이름 'sample' 입력 (성공)", "PASS"),
            (7, "타일형 선택 확인", "라디오 버튼", "타일형 옵션 선택 확인 (성공)", "PASS"),
            (8, "만들기 버튼 클릭", "버튼 클릭", "만들기 버튼 클릭 > 새 창 열림", "PASS"),
            (9, "새 창 확인", "새 창 URL", "https://eng-mn1-mid-2.aidt.ai/.../activity/board/2573?isNew=true", "PASS"),
        ]
    },
    "TC-T-10": {
        "name": "모둠활동 작성하기 - 모둠형",
        "date": "2026-03-10 13:02:34",
        "result": "PASS",
        "steps": [
            (1, "선생님 입장하기", "진입 페이지", "선생님 입장하기 버튼 클릭 > 메인 페이지 이동", "PASS"),
            (2, "모둠활동 메뉴 클릭", "LNB 메뉴", "모둠활동 메뉴 클릭 > 모둠활동 리스트 페이지 이동", "PASS"),
            (3, "모둠활동 페이지 확인", "페이지 노출", "모둠활동 리스트 페이지 키워드 확인 (found: True)", "PASS"),
            (4, "작성하기 버튼 클릭", "버튼 클릭", "작성하기 버튼 클릭 (1개 발견)", "PASS"),
            (5, "활동 만들기 팝업 확인", "팝업 노출", "활동 만들기 팝업 키워드 확인 (found: True)", "PASS"),
            (6, "활동 이름 입력", "입력 필드", "활동 이름 'sample' 입력 (성공)", "PASS"),
            (7, "모둠형 선택", "라디오 버튼", "모둠형 옵션 선택 (성공)", "PASS"),
            (8, "만들기 버튼 클릭", "버튼 클릭", "만들기 버튼 클릭 > 새 창 열림", "PASS"),
            (9, "새 창 확인", "새 창 URL", "https://eng-mn1-mid-2.aidt.ai/.../activity/board/2574?isNew=true", "PASS"),
        ]
    },
    "TC-T-11": {
        "name": "모둠활동 복사/공개/비공개/삭제",
        "date": "2026-03-10 13:05:08",
        "result": "PASS",
        "steps": [
            (1, "[환경설정] sample 활동 생성", "sample 활동 생성", "sample 이름의 타일형 활동 생성 완료", "PASS"),
            (2, "[테스트 1] 복사하기", "[복사본]sample 생성", "[복사본]sample 활동 생성 확인", "PASS"),
            (3, "[테스트 2] 공개하기", "공개 변경 + 토스트", "토스트 알림: '활동이 공개 되었습니다.'", "PASS"),
            (4, "[테스트 3] 비공개하기", "비공개 변경 + 토스트", "토스트 알림: '활동이 비공개 되었습니다.'", "PASS"),
            (5, "[테스트 4] 삭제하기", "삭제 + 토스트", "토스트 알림: '활동이 삭제 되었습니다.'", "PASS"),
            (6, "[테스트 5] [복사본]sample 삭제하기", "삭제 + 토스트", "토스트 알림: '활동이 삭제 되었습니다.'", "PASS"),
        ]
    },
    "TC-T-12": {
        "name": "모둠 활동 선택 > 활동보드판 진입 동작 확인",
        "date": "2026-03-10 13:08:32",
        "result": "PASS",
        "steps": [
            (1, "진입 페이지 > 선생님 입장", "메인 페이지 진입", "URL: .../lms/class/0/dashboard", "PASS"),
            (2, "모둠활동 메뉴 클릭", "모둠활동 리스트 페이지", "모둠활동 메뉴 클릭 완료", "PASS"),
            (3, "작성하기 버튼 클릭", "활동 만들기 팝업", "활동 만들기 팝업 표시", "PASS"),
            (4, "활동 생성 > 새 창 열림", "모둠활동창 새 창", "URL: .../activity/board/2577?isNew=true", "PASS"),
            (5, "새 창 닫기", "모둠활동창 닫기", "모둠활동창 닫기 완료", "PASS"),
            (6, "sample 활동 클릭 > 새 창 열림", "모둠활동창 새 창 재진입", "URL: .../activity/board/2577?isNew=true", "PASS"),
            (7, "열린 창 닫기", "모둠활동창 닫기", "재진입한 모둠활동창 닫기 완료", "PASS"),
            (8, "sample 활동 삭제", "삭제 + 토스트", "토스트 알림: '활동이 삭제 되었습니다.'", "PASS"),
        ]
    },
    "TC-T-13": {
        "name": "모둠 활동 선택 > 활동 보드판 > 게시글 작성 동작 확인",
        "date": "2026-03-10 13:16:20",
        "result": "PASS",
        "steps": [
            (1, "진입 페이지 > 선생님 입장하기", "메인 페이지 진입", "URL: .../lms/class/0/dashboard", "PASS"),
            (2, "모둠활동 메뉴 클릭", "모둠활동 리스트 페이지 이동", "모둠활동 메뉴 클릭 완료", "PASS"),
            (3, "작성하기 버튼 클릭", "활동 만들기 팝업 표시", "활동 만들기 팝업 표시됨", "PASS"),
            (4, "활동 이름 'sample' 입력 > 타일형 선택 > 만들기 클릭", "새 창으로 모둠활동창 열림", "URL: .../activity/board/2578?isNew=true", "PASS"),
            (5, "활동 설정 패널 닫기", "패널 닫기", "패널 닫기 완료", "PASS"),
            (6, "우측 하단 '게시글 만들기' 버튼 클릭", "게시글 작성 패널 열림", "플로팅 버튼 클릭 완료", "PASS"),
            (7, "게시글 제목 'title', 내용 'Input contents' 입력", "제목/내용 입력 완료", "제목: True, 내용: True", "PASS"),
            (8, "게시글 컬러 노란색 선택", "노란색 선택 완료", "노란색 컬러 선택 완료", "PASS"),
            (9, "만들기 버튼 클릭", "게시글 생성", "만들기 버튼 클릭 완료", "PASS"),
            (10, "토스트 알림 확인", "'활동 게시글이 생성되었습니다.'", "토스트: '활동 게시글이 생성되었습니다.'", "PASS"),
            (11, "보드에 게시글 생성 확인", "보드에 게시글 존재", "게시글이 보드에 생성됨", "PASS"),
            (12, "창 닫기", "활동 창 닫기", "활동 창 닫기 완료", "PASS"),
            (13, "sample 활동 삭제", "삭제 + 토스트 알림", "토스트: '활동이 삭제 되었습니다.'", "PASS"),
        ]
    },
}

def create_pdf():
    output_path = r"D:\jaehyuk.myung\claude_demo\Demo_13_QA\QA_Test_Report_2026.03.10.pdf"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()

    # 한글 스타일 정의
    title_style = ParagraphStyle('Title', fontName='Malgun', fontSize=18, spaceAfter=15, alignment=1)
    heading_style = ParagraphStyle('Heading', fontName='Malgun', fontSize=12, spaceAfter=8, spaceBefore=10)
    normal_style = ParagraphStyle('Normal', fontName='Malgun', fontSize=9)
    cell_style = ParagraphStyle('Cell', fontName='Malgun', fontSize=8, leading=10)

    story = []

    # 타이틀
    story.append(Paragraph("AIDT QA Test Report", title_style))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 10))

    # 요약 테이블
    story.append(Paragraph("Test Summary", heading_style))

    summary_data = [['TC', 'Test Name', 'Result', 'PASS', 'CHECK', 'FAIL', 'SKIP']]
    total_pass = total_check = total_fail = total_skip = 0

    for tc_id, tc_info in test_data.items():
        pass_count = sum(1 for s in tc_info['steps'] if s[4] == 'PASS')
        check_count = sum(1 for s in tc_info['steps'] if s[4] == 'CHECK')
        fail_count = sum(1 for s in tc_info['steps'] if s[4] == 'FAIL')
        skip_count = sum(1 for s in tc_info['steps'] if s[4] == 'SKIP')

        total_pass += pass_count
        total_check += check_count
        total_fail += fail_count
        total_skip += skip_count

        summary_data.append([
            tc_id,
            tc_info['name'][:25],
            tc_info['result'],
            str(pass_count),
            str(check_count),
            str(fail_count),
            str(skip_count)
        ])

    summary_data.append(['TOTAL', '', 'PASS', str(total_pass), str(total_check), str(total_fail), str(total_skip)])

    summary_table = Table(summary_data, colWidths=[50, 200, 50, 40, 40, 40, 40])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Malgun'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    # 각 TC 상세 결과
    for tc_id, tc_info in test_data.items():
        # TC 헤더
        story.append(Paragraph(f"{tc_id}: {tc_info['name']}", heading_style))
        story.append(Paragraph(f"Execution Date: {tc_info['date']} | Result: {tc_info['result']}", normal_style))
        story.append(Spacer(1, 5))

        # 테이블 데이터
        table_data = [['STEP', 'Action', 'Check Item', 'Detail', 'Result']]

        for step in tc_info['steps']:
            step_num, action, check_item, detail, result = step

            # 긴 텍스트 줄임
            action_short = action[:30] + '...' if len(action) > 30 else action
            check_short = check_item[:25] + '...' if len(check_item) > 25 else check_item
            detail_short = detail[:50] + '...' if len(detail) > 50 else detail

            table_data.append([
                str(step_num),
                Paragraph(action_short, cell_style),
                Paragraph(check_short, cell_style),
                Paragraph(detail_short, cell_style),
                result
            ])

        detail_table = Table(table_data, colWidths=[30, 130, 100, 300, 50])

        # 결과에 따른 색상 설정
        style_commands = [
            ('FONTNAME', (0, 0), (-1, -1), 'Malgun'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]

        # 결과 컬럼 색상
        for i, step in enumerate(tc_info['steps'], 1):
            result = step[4]
            if result == 'PASS':
                style_commands.append(('TEXTCOLOR', (4, i), (4, i), colors.green))
            elif result == 'FAIL':
                style_commands.append(('TEXTCOLOR', (4, i), (4, i), colors.red))
            elif result == 'CHECK':
                style_commands.append(('TEXTCOLOR', (4, i), (4, i), colors.orange))
            elif result == 'SKIP':
                style_commands.append(('TEXTCOLOR', (4, i), (4, i), colors.grey))

        detail_table.setStyle(TableStyle(style_commands))
        story.append(detail_table)
        story.append(Spacer(1, 15))

    doc.build(story)
    print(f"PDF Report saved: {output_path}")
    return output_path

if __name__ == "__main__":
    create_pdf()
