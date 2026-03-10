"""마크다운 파일을 PDF로 변환 (Playwright 사용)"""
import asyncio
import markdown
from pathlib import Path

MD_FILE = r"c:\Users\jaehyuk.myung\.gemini\antigravity\brain\5144e89d-4ea1-45d0-8b78-f04dc7afb1f2\walkthrough.md.resolved"
OUTPUT_PDF = r"d:\jaehyuk.myung\claude_demo\Demo_13_QA\AIDT_테스트_결과_리포트.pdf"

# 마크다운 → HTML 변환
md_text = Path(MD_FILE).read_text(encoding="utf-8")
html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

# 이모지를 HTML 엔티티로 치환
html_body = html_body.replace("✅", "&#10003;")

html_full = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 20mm 15mm;
  }}
  body {{
    font-family: 'Malgun Gothic', 'NanumGothic', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1a1a1a;
  }}
  h1 {{
    font-size: 20pt;
    color: #1a365d;
    border-bottom: 3px solid #2b6cb0;
    padding-bottom: 8px;
    margin-bottom: 16px;
  }}
  h2 {{
    font-size: 15pt;
    color: #2b6cb0;
    border-bottom: 1px solid #bee3f8;
    padding-bottom: 6px;
    margin-top: 24px;
  }}
  h3 {{
    font-size: 13pt;
    color: #2c5282;
    margin-top: 20px;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 10pt;
  }}
  th {{
    background-color: #2b6cb0;
    color: white;
    padding: 8px 10px;
    text-align: left;
    font-weight: 600;
  }}
  td {{
    padding: 7px 10px;
    border-bottom: 1px solid #e2e8f0;
  }}
  tr:nth-child(even) {{
    background-color: #f7fafc;
  }}
  code {{
    background-color: #edf2f7;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 9pt;
    font-family: 'Consolas', monospace;
    color: #c53030;
  }}
  strong {{
    color: #1a365d;
  }}
  hr {{
    border: none;
    border-top: 1px solid #cbd5e0;
    margin: 20px 0;
  }}
  blockquote {{
    border-left: 4px solid #48bb78;
    background-color: #f0fff4;
    padding: 10px 16px;
    margin: 12px 0;
    border-radius: 4px;
    font-size: 10pt;
  }}
  ul, ol {{
    padding-left: 24px;
  }}
  li {{
    margin: 4px 0;
  }}
  .footer {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 8pt;
    color: #a0aec0;
    padding: 8px;
  }}
</style>
</head>
<body>
{html_body}
<div class="footer">AIDT QA 자동화 테스트 리포트 | 생성일: 2026-03-03</div>
</body>
</html>"""

async def generate_pdf():
    from playwright.async_api import async_playwright
    
    # HTML 파일을 임시로 저장
    import tempfile, os
    html_path = os.path.join(tempfile.gettempdir(), "report.html")
    Path(html_path).write_text(html_full, encoding="utf-8")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file:///{Path(html_path).as_posix()}")
        await page.pdf(
            path=OUTPUT_PDF,
            format="A4",
            margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"},
            print_background=True
        )
        await browser.close()
    
    print(f"PDF 생성 완료: {OUTPUT_PDF}")

asyncio.run(generate_pdf())
