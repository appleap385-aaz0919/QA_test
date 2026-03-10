import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

# 한글 폰트 등록
pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))

def load_json_files(base_path):
    """TC-T-01부터 TC-T-13까지 JSON 파일 로드"""
    results = []
    for i in range(1, 14):
        json_file = os.path.join(base_path, f"test_result_TC-T-{i:02d}.json")
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
    return results

def display_console_table(data):
    """화면에 5개 컬럼 테이블 출력"""
    print(f"\n## {data['test_name']}")
    print(f"**실행일시:** {data['test_date']}")
    print(f"**최종 결과:** {data['overall_result']}")
    print()
    print("| STEP | Action | Check Item | Detail | Result |")
    print("|------|--------|------------|--------|--------|")

    for step in data['steps']:
        step_num = step.get('step', '-')
        action = step.get('action', '-')
        check_item = step.get('check_item', '-')
        detail = step.get('detail', '-')
        status = step.get('status', '-')

        # detail이 너무 길면 줄임
        if len(str(detail)) > 50:
            detail = str(detail)[:47] + "..."

        print(f"| {step_num} | {action} | {check_item} | {detail} | {status} |")

def display_summary_table(results):
    """요약 테이블 출력"""
    print("\n## TC-T-01 ~ TC-T-13 테스트 결과 요약")
    print("| TC | Test Name | Result | PASS | CHECK | FAIL | SKIP |")
    print("|---|---|--------|---|---|------|-------|")

    total_pass = total_check = total_fail = total_skip = 0

    for data in results:
        pass_count = sum(1 for s in data['steps'] if s.get('status') == 'PASS')
        check_count = sum(1 for s in data['steps'] if s.get('status') == 'CHECK')
        fail_count = sum(1 for s in data['steps'] if s.get('status') == 'FAIL')
        skip_count = sum(1 for s in data['steps'] if s.get('status') == 'SKIP')

        total_pass += pass_count
        total_check += check_count
        total_fail += fail_count
        total_skip += skip_count

        tc_no = data['test_name'].split(':')[0]
        tc_name = data['test_name'].split(':')[-1].strip()
        if len(tc_name) > 25:
            tc_name = tc_name[:22] + "..."

        print(f"| {tc_no} | {tc_name} | {data['overall_result']} | {pass_count} | {check_count} | {fail_count} | {skip_count} |")

    print(f"| **TOTAL** | | **PASS** | **{total_pass}** | **{total_check}** | **{total_fail}** | **{total_skip}** |")

def create_pdf_report(results, output_path):
    """PDF 리포트 생성 (5개 컬럼)"""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           leftMargin=20, rightMargin=20,
                           topMargin=20, bottomMargin=20)

    styles = getSampleStyleSheet()

    # 한글 스타일 정의
    title_style = ParagraphStyle('Title', fontName='Malgun', fontSize=16,
                                 spaceAfter=20, alignment=1)
    heading_style = ParagraphStyle('Heading', fontName='Malgun', fontSize=12,
                                   spaceAfter=10, spaceBefore=10)
    normal_style = ParagraphStyle('Normal', fontName='Malgun', fontSize=9)

    story = []

    # 타이틀
    story.append(Paragraph("AIDT QA Test Report", title_style))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 20))

    # 요약 테이블
    story.append(Paragraph("Test Summary", heading_style))

    summary_data = [['TC', 'Test Name', 'Result', 'PASS', 'CHECK', 'FAIL', 'SKIP']]
    total_pass = total_check = total_fail = total_skip = 0

    for data in results:
        pass_count = sum(1 for s in data['steps'] if s.get('status') == 'PASS')
        check_count = sum(1 for s in data['steps'] if s.get('status') == 'CHECK')
        fail_count = sum(1 for s in data['steps'] if s.get('status') == 'FAIL')
        skip_count = sum(1 for s in data['steps'] if s.get('status') == 'SKIP')

        total_pass += pass_count
        total_check += check_count
        total_fail += fail_count
        total_skip += skip_count

        tc_no = data['test_name'].split(':')[0]
        tc_name = data['test_name'].split(':')[-1].strip()[:20]

        summary_data.append([tc_no, tc_name, data['overall_result'],
                           str(pass_count), str(check_count),
                           str(fail_count), str(skip_count)])

    summary_data.append(['TOTAL', '', 'PASS', str(total_pass),
                        str(total_check), str(total_fail), str(total_skip)])

    summary_table = Table(summary_data, colWidths=[50, 180, 50, 40, 40, 40, 40])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Malgun'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    # 각 TC 상세 결과
    for data in results:
        story.append(Paragraph(f"{data['test_name']}", heading_style))
        story.append(Paragraph(f"Execution Date: {data['test_date']}", normal_style))
        story.append(Paragraph(f"Overall Result: {data['overall_result']}", normal_style))
        story.append(Spacer(1, 10))

        # 5개 컬럼 테이블 데이터
        table_data = [['STEP', 'Action', 'Check Item', 'Detail', 'Result']]

        for step in data['steps']:
            step_num = str(step.get('step', '-'))
            action = step.get('action', '-')[:25]
            check_item = step.get('check_item', '-')[:20]
            detail = step.get('detail', '-')
            if len(str(detail)) > 40:
                detail = str(detail)[:37] + "..."
            status = step.get('status', '-')

            table_data.append([step_num, action, check_item, str(detail), status])

        detail_table = Table(table_data, colWidths=[30, 100, 80, 200, 50])
        detail_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Malgun'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (4, 1), (4, -1), colors.green),
        ]))
        story.append(detail_table)
        story.append(Spacer(1, 20))

    doc.build(story)
    print(f"\nPDF Report saved: {output_path}")

def main():
    base_path = r"D:\jaehyuk.myung\claude_demo\Demo_13_QA"

    # JSON 파일 로드
    results = load_json_files(base_path)

    # 각 TC 결과 화면 출력 (5개 컬럼)
    for data in results:
        display_console_table(data)
        print()

    # 요약 테이블 출력
    display_summary_table(results)

    # PDF 리포트 생성
    pdf_path = os.path.join(base_path, "QA_Test_Report_2026.03.10.pdf")
    create_pdf_report(results, pdf_path)

if __name__ == "__main__":
    main()
