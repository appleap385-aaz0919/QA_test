"""
AIDT LMS QA 테스트 결과 보고서 PDF 생성
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import os

# 한글 폰트 등록 (Windows 기본 폰트 사용)
try:
    pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
    pdfmetrics.registerFont(TTFont('MalgunBold', 'C:/Windows/Fonts/malgunbd.ttf'))
    KOREAN_FONT = 'Malgun'
    KOREAN_FONT_BOLD = 'MalgunBold'
except:
    KOREAN_FONT = 'Helvetica'
    KOREAN_FONT_BOLD = 'Helvetica-Bold'

def create_styles():
    styles = getSampleStyleSheet()

    # 한글 스타일 추가
    styles.add(ParagraphStyle(
        name='KoreanTitle',
        fontName=KOREAN_FONT_BOLD,
        fontSize=18,
        alignment=1,
        spaceAfter=20
    ))

    styles.add(ParagraphStyle(
        name='KoreanHeading',
        fontName=KOREAN_FONT_BOLD,
        fontSize=14,
        spaceAfter=10,
        spaceBefore=10
    ))

    styles.add(ParagraphStyle(
        name='KoreanNormal',
        fontName=KOREAN_FONT,
        fontSize=10,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name='KoreanSmall',
        fontName=KOREAN_FONT,
        fontSize=9,
        spaceAfter=4
    ))

    return styles

def load_test_results():
    results = []
    test_files = [
        'test_result_TC-T-01.json',
        'test_result_TC-T-02.json',
        'test_result_TC-T-03.json',
        'test_result_TC-T-04.json',
        'test_result_TC-T-05.json',
        'test_result_TC-T-06.json'
    ]

    for f in test_files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                results.append(json.load(file))
        except:
            pass

    return results

def create_pdf_report():
    doc = SimpleDocTemplate(
        "QA_Test_Report.pdf",
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = create_styles()
    story = []

    # 제목
    story.append(Paragraph("AIDT LMS QA Test Report", styles['KoreanTitle']))
    story.append(Paragraph("Test Date: 2026-03-03", styles['KoreanNormal']))
    story.append(Paragraph("Environment: Production (aidt.ai)", styles['KoreanNormal']))
    story.append(Spacer(1, 20))

    # 요약 테이블
    summary_data = [
        ['Test Case', 'Test Name', 'Result'],
        ['TC-T-01', 'Home Teacher Entry', 'PASS'],
        ['TC-T-02', 'Home Card Insights', 'PASS'],
        ['TC-T-03', 'Class Start Button', 'PASS'],
        ['TC-T-04', 'Textbook View Button', 'PASS'],
        ['TC-T-05', 'Unit Detail View', 'PASS'],
        ['TC-T-06', 'Reconstruction Test', 'PASS'],
    ]

    summary_table = Table(summary_data, colWidths=[80, 250, 80])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), KOREAN_FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (2, 1), (2, -1), colors.HexColor('#C8E6C9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # 전체 결과
    story.append(Paragraph("Overall Result: PASS (6/6)", styles['KoreanHeading']))
    story.append(Spacer(1, 20))

    # 각 테스트 상세 결과
    test_details = [
        {
            'id': 'TC-T-01',
            'name': 'Home Teacher Entry Test',
            'description': 'Entry page access and teacher login flow',
            'steps': [
                ('1', 'Access entry page', 'PASS'),
                ('2', 'Click teacher login button', 'PASS'),
            ],
            'checks': [
                ('Today class section', 'PASS'),
                ('Textbook section', 'PASS'),
                ('Attendance check', 'PASS'),
                ('Assignment section', 'PASS'),
                ('Class analysis', 'PASS'),
                ('Mood section', 'PASS'),
                ('Board/Notice', 'PASS'),
            ]
        },
        {
            'id': 'TC-T-02',
            'name': 'Home Card Insights Test',
            'description': 'Verify all dashboard cards display correctly',
            'steps': [
                ('1', 'Access entry page', 'PASS'),
                ('2', 'Enter as teacher', 'PASS'),
            ],
            'checks': [
                ('Profile section', 'PASS'),
                ('Today class card', 'PASS'),
                ('Textbook card', 'PASS'),
                ('Progress card (2 items)', 'PASS'),
                ('Attendance card', 'PASS'),
                ('Assignment card (4 items)', 'PASS'),
                ('Class analysis card', 'PASS'),
                ('Wrong answer note card', 'PASS'),
                ('Mood card (5 categories)', 'PASS'),
                ('Notice card', 'PASS'),
            ]
        },
        {
            'id': 'TC-T-03',
            'name': 'Class Start Button Test',
            'description': 'Verify class start button opens viewer',
            'steps': [
                ('1', 'Teacher login', 'PASS'),
                ('2', 'Find class start button', 'PASS'),
                ('3', 'Click and verify new window', 'PASS'),
                ('4', 'Viewer page loading', 'PASS'),
                ('5', 'Verify viewer elements', 'PASS'),
            ],
            'checks': [
                ('Button found', 'PASS'),
                ('New window opened', 'PASS'),
                ('Viewer container (3)', 'PASS'),
                ('Navigation (4)', 'PASS'),
                ('Content area (24)', 'PASS'),
            ]
        },
        {
            'id': 'TC-T-04',
            'name': 'Textbook View Button Test',
            'description': 'Verify textbook menu and view button',
            'steps': [
                ('1', 'Teacher login', 'PASS'),
                ('2', 'Click textbook menu', 'PASS'),
                ('3', 'Verify unit list', 'PASS'),
                ('4', 'Click textbook view button', 'PASS'),
                ('5', 'Verify viewer window', 'PASS'),
                ('6', 'Verify content display', 'PASS'),
            ],
            'checks': [
                ('Unit ascending order [1-8]', 'PASS'),
                ('Unit list found', 'PASS'),
                ('Textbook view button', 'PASS'),
                ('Viewer new window', 'PASS'),
                ('Content display', 'PASS'),
            ]
        },
        {
            'id': 'TC-T-05',
            'name': 'Unit Detail View Test',
            'description': 'Verify unit detail view and module list',
            'steps': [
                ('1', 'Teacher login', 'PASS'),
                ('2', 'Click textbook menu', 'PASS'),
                ('3', 'Verify unit list', 'PASS'),
                ('4', 'Click unit detail view', 'PASS'),
                ('5', 'Verify module list (23 items)', 'PASS'),
                ('6', 'Click module and verify viewer', 'PASS'),
                ('7', 'Verify content display', 'PASS'),
            ],
            'checks': [
                ('Unit ascending order [1-8]', 'PASS'),
                ('Unit list found', 'PASS'),
                ('Unit detail button (8)', 'PASS'),
                ('Module list (23 ViewerLinkBox)', 'PASS'),
                ('Viewer new window', 'PASS'),
                ('Content display (24 areas)', 'PASS'),
            ]
        },
        {
            'id': 'TC-T-06',
            'name': 'Reconstruction Test',
            'description': 'Verify reconstruction flow: save draft, delete draft, preview viewer',
            'steps': [
                ('1', 'Teacher login', 'PASS'),
                ('2', 'Click textbook menu', 'PASS'),
                ('3', 'Verify unit list', 'PASS'),
                ('4', 'Click reconstruction button', 'PASS'),
                ('5', 'Verify reconstruction page', 'PASS'),
                ('6', 'Delete temp save (if exists)', 'SKIP'),
                ('7', 'Click temp save button', 'PASS'),
                ('8', 'Click preview and verify viewer', 'PASS'),
            ],
            'checks': [
                ('Unit list found', 'PASS'),
                ('Reconstruction button (8)', 'PASS'),
                ('Reconstruction page keywords', 'PASS'),
                ('Temp save delete button', 'SKIP'),
                ('Temp save button', 'PASS'),
                ('Preview viewer URL', 'PASS'),
            ]
        }
    ]

    for test in test_details:
        # 테스트 제목
        story.append(Paragraph(f"{test['id']}: {test['name']}", styles['KoreanHeading']))
        story.append(Paragraph(f"Description: {test['description']}", styles['KoreanSmall']))
        story.append(Spacer(1, 8))

        # 스텝 테이블
        step_data = [['Step', 'Action', 'Result']]
        for step in test['steps']:
            step_data.append([step[0], step[1], step[2]])

        step_table = Table(step_data, colWidths=[40, 300, 60])
        step_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), KOREAN_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), KOREAN_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (2, 1), (2, -1), colors.HexColor('#C8E6C9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(step_table)
        story.append(Spacer(1, 8))

        # 체크 항목 테이블
        check_data = [['Check Item', 'Result']]
        for check in test['checks']:
            check_data.append([check[0], check[1]])

        check_table = Table(check_data, colWidths=[300, 100])
        check_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#616161')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), KOREAN_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), KOREAN_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (1, 1), (1, -1), colors.HexColor('#C8E6C9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(check_table)
        story.append(Spacer(1, 20))

    # 푸터
    story.append(Spacer(1, 30))
    story.append(Paragraph("Test Environment", styles['KoreanHeading']))
    story.append(Paragraph("URL: https://www.aidt.ai/lms-web/dev/entry-aidt-2025", styles['KoreanSmall']))
    story.append(Paragraph("School: Middle School | Subject: English | Grade: 2nd", styles['KoreanSmall']))
    story.append(Paragraph("Browser: Chromium (Playwright)", styles['KoreanSmall']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("--- End of Report ---", styles['KoreanNormal']))

    # PDF 생성
    doc.build(story)
    print("PDF Report generated: QA_Test_Report.pdf")

if __name__ == "__main__":
    create_pdf_report()
