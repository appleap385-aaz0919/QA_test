---
name: playwright-qa-test
description: Playwright 기반 QA 테스트 자동화 스크립트 작성. LMS, 교육 플랫폼, SPA 웹앱 테스트에 특화. 새 창/팝업 처리, 가상 스크롤, 권한 허용, 동적 로딩 대기 등의 패턴 포함. Use when asked to write Playwright test scripts, QA automation, browser testing, or web app testing.
---

# Playwright QA Test Automation

## Core Setup Pattern

```python
import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import json

LOAD_WAIT = 5
MAX_WAIT = 60

async def test_function():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})

        # 마이크 권한 미리 허용 (음성 녹음 필요 시)
        await context.grant_permissions(["microphone"])

        page = await context.new_page()
        # ... test code
        await browser.close()
```

## Critical Patterns

### 1. 새 창/팝업 처리

```python
# 버튼 클릭 후 새 창 열리는 경우
async with context.expect_page(timeout=MAX_WAIT * 1000) as new_page_info:
    await button.click()

new_page = await new_page_info.value
await new_page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)
```

### 2. 로딩 대기 패턴

```python
# 기본 대기
await page.wait_for_load_state("networkidle")

# 로딩 스피너 사라질 때까지 대기
try:
    await page.wait_for_selector(".loading", state="hidden", timeout=30000)
except TimeoutError:
    pass  # 로딩 요소가 없으면 무시

# 충분한 대기 시간
await asyncio.sleep(LOAD_WAIT)
```

### 3. 요소 찾기 - span 내 텍스트

```python
# button 요소가 아닌 span 내에 버튼 텍스트가 있는 경우
detail_span = page.locator("span:has-text('단원 상세 보기')")
await detail_span.first.click()
```

### 4. 가상 스크롤 처리

```python
# 스크롤 컨테이너 찾아서 스크롤하며 모든 요소 로드
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
```

### 5. 정규식으로 패턴 매칭

```python
import re

# "Lesson 1", "Lesson 2" 형식에서 번호 추출
lesson_pattern = re.compile(r'Lesson\s*(\d+)', re.IGNORECASE)
lines = page_text.split('\n')
numbers = []
for line in lines:
    if '평가' not in line:  # 특정 텍스트 제외
        match = lesson_pattern.search(line)
        if match:
            numbers.append(int(match.group(1)))

# 오름차순 확인
is_ascending = numbers == sorted(numbers)
```

### 6. 결과 JSON 저장

```python
results = {
    "test_name": "TC-XX: 테스트명",
    "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "url": TEST_URL,
    "steps": [],
    "checks": {},
    "overall_result": "PASS",
    "errors": []
}

# 스텝 추가
results["steps"].append({"step": 1, "action": "액션명", "status": "PASS"})

# 체크 항목 추가
results["checks"]["항목명"] = {"found": True, "status": "PASS"}

# 저장
with open("test_result.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

### 7. 클릭 가능한 컨테이너 내부 요소 조작 (중요)

**문제 상황**: 체크박스나 버튼이 `button` 요소 내부에 있을 때, Playwright `.click()` 사용 시 부모 button 클릭 이벤트가 함께 발생

```html
<!-- 예: 전체 행이 button인 경우 -->
<button class="bar-list-item">
    <div class="list-item-left">
        <input type="checkbox" />  <!-- 이 체크박스 클릭 시 부모 button 클릭 발생 -->
    </div>
    <span class="chapter-title">활동명</span>
    <div class="list-item-tools">
        <button>복사하기</button>  <!-- 이 버튼 클릭 시 부모 button 클릭 발생 -->
    </div>
</button>
```

**실패 케이스**: Playwright `.click()` 사용
```python
# FAIL: 체크박스 클릭 시 부모 button 클릭 → 새 창 열림
checkbox = page.locator("input[type='checkbox']")
await checkbox.click()  # 부모 button 클릭 이벤트 전파됨

# FAIL: force=True도 소용없음
await checkbox.click(force=True)  # 여전히 부모 클릭 발생
```

**성공 케이스**: JavaScript로 직접 DOM 조작
```python
# SUCCESS: JavaScript로 체크박스 체크 (이벤트 전파 방지)
checkbox = page.locator("input[type='checkbox']").first
await page.evaluate("""
    (checkbox) => {
        if (!checkbox.checked) {
            checkbox.checked = true;
            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
""", await checkbox.element_handle())

# SUCCESS: JavaScript로 버튼 클릭
button = page.locator(".list-item-tools button:has-text('복사하기')").first
await page.evaluate("(btn) => { btn.click(); }", await button.element_handle())
```

**핵심 교훈**:
- 요소가 `button`, `a` 등 클릭 가능한 컨테이너 내부에 있으면 `page.evaluate()` 사용
- JavaScript로 직접 DOM 조작하면 이벤트 전파(bubbling) 방지 가능
- `force=True`는 pointer events만 무시할 뿐, 이벤트 전파는 막지 못함

## Common Issues & Solutions

| 문제 | 원인 | 해결방법 |
|------|------|----------|
| 요소를 찾을 수 없음 | button이 아닌 span 등 | `span:has-text('텍스트')` 사용 |
| 새 창이 감지 안됨 | context.expect_page 누락 | 클릭 전에 expect_page 설정 |
| 일부 요소만 카운트됨 | 가상 스크롤 | 컨테이너 스크롤하며 로드 |
| 마이크 권한 팝업 | 권한 미허용 | grant_permissions 사전 설정 |
| 로딩 중 요소 없음 | 로딩 완료 대기 부족 | wait_for_selector + sleep |
| networkidle 타임아웃 | 페이지 로딩 지연 | try-except로 무시하고 진행 |
| **체크박스/버튼 클릭 시 새 창 열림** | **부모 button 요소 클릭 전파** | **page.evaluate()로 DOM 직접 조작** |
| **force=True도 작동 안함** | **이벤트 전파는 막지 못함** | **JavaScript로 직접 이벤트 발생** |

## 테스트 결과 출력 포맷 (필수 준수)

**중요**: 테스트 결과는 항상 아래 5개 컬럼 형식의 테이블로 출력해야 한다. steps뿐만 아니라 checks, element_checks, card_checks 등 모든 검증 항목을 포함하여 전체 STEP을 표시해야 한다.

### 5개 컬럼 형식

| STEP | Action | Check Item | Detail | Result |
|------|--------|------------|--------|--------|
| 1 | 진입 페이지 접속 | 진입 페이지 | 진입 URL 접속 완료 | PASS |
| 2 | 선생님 입장하기 클릭 | 메인 페이지 진입 | 선생님 입장하기 버튼 클릭 > 메인 페이지 이동 | PASS |
| 3 | 메인 페이지 요소 확인 | 오늘 수업/수업 시작하기 | [class*='today'] 요소 확인 | PASS |
| ... | ... | ... | ... | ... |

### 컬럼 설명
- **STEP**: 테스트 단계 번호 (steps + checks 모두 포함하여 순차 번호)
- **Action**: 수행한 동작 (한 줄 요약)
- **Check Item**: 확인하는 항목명
- **Detail**: 구체적인 검증 내용 (URL, 선택자, 확인된 값 등)
- **Result**: PASS / FAIL / CHECK / SKIP

### JSON 구조에서 결과 테이블 변환 규칙

JSON 결과 파일에는 `steps` 외에도 `checks`, `element_checks`, `card_checks` 등의 검증 항목이 있을 수 있다. 이들을 모두 합쳐서 하나의 테이블로 표시해야 한다.

```python
# JSON 구조 예시
results = {
    "test_name": "TC-T-01: 교사 홈 진입 테스트",
    "test_date": "2026-03-10 12:45:51",
    "url": "https://...",
    "steps": [
        {"step": 1, "action": "진입 페이지 접속", "status": "PASS"},
        {"step": 2, "action": "선생님 입장하기 클릭", "status": "PASS"}
    ],
    "element_checks": {
        "오늘 수업/수업 시작하기": {"found": true, "selector": "[class*='today']", "status": "PASS"},
        "교과서": {"found": true, "selector": "[class*='textbook']", "status": "PASS"},
        "출석체크": {"found": true, "selector": "[class*='attendance']", "status": "PASS"}
    },
    "overall_result": "PASS"
}
```

### 결과 변환 로직

```python
def convert_json_to_table(data):
    """JSON 결과를 5컬럼 테이블로 변환"""
    table_rows = []
    step_num = 1

    # 1. steps 처리
    for step in data.get("steps", []):
        table_rows.append({
            "step": step_num,
            "action": step.get("action", "-"),
            "check_item": step.get("check_item", "-"),
            "detail": step.get("detail", "-"),
            "result": step.get("status", "-")
        })
        step_num += 1

    # 2. element_checks 처리 (존재하면)
    if "element_checks" in data:
        for check_name, check_data in data["element_checks"].items():
            detail = f"선택자: {check_data.get('selector', '-')}"
            if check_data.get("count"):
                detail += f", 개수: {check_data['count']}"
            table_rows.append({
                "step": step_num,
                "action": "메인 페이지 요소 확인",
                "check_item": check_name,
                "detail": detail,
                "result": check_data.get("status", "-")
            })
            step_num += 1

    # 3. card_checks 처리 (존재하면)
    if "card_checks" in data:
        for card_name, card_data in data["card_checks"].items():
            detail_parts = []
            if card_data.get("details"):
                for k, v in card_data["details"].items():
                    detail_parts.append(f"{k}: {v}")
            detail = ", ".join(detail_parts) if detail_parts else "found: True"
            table_rows.append({
                "step": step_num,
                "action": f"{card_name} 확인",
                "check_item": card_name,
                "detail": detail,
                "result": card_data.get("status", "-")
            })
            step_num += 1

    # 4. checks 처리 (존재하면)
    if "checks" in data:
        for check_name, check_data in data["checks"].items():
            detail_parts = []
            if check_data.get("url"):
                detail_parts.append(f"URL: {check_data['url']}")
            if check_data.get("count") is not None:
                detail_parts.append(f"개수: {check_data['count']}")
            if check_data.get("toast_message"):
                detail_parts.append(f"토스트: {check_data['toast_message']}")
            if check_data.get("found_keywords"):
                detail_parts.append(f"키워드: {', '.join(check_data['found_keywords'])}")
            detail = ", ".join(detail_parts) if detail_parts else "found: True"
            table_rows.append({
                "step": step_num,
                "action": check_name.replace("_", " "),
                "check_item": check_name.replace("_", " "),
                "detail": detail,
                "result": check_data.get("status", "-")
            })
            step_num += 1

    return table_rows
```

## 테스트 완료 후 결과 화면 출력

테스트 실행이 완료되면 반드시 결과를 화면에 표로 출력하여 사용자가 즉시 확인할 수 있게 한다.

### 단일 TC 결과 출력 형식

```
## TC-T-XX: 테스트명

**실행일시:** 2026-03-10 12:00:00
**최종 결과:** PASS

| STEP | Action | Check Item | Detail | Result |
|------|--------|------------|--------|--------|
| 1 | 진입 페이지 > 선생님 입장하기 | 메인 페이지 진입 | URL: /lms/class/0/dashboard | PASS |
| 2 | 모둠활동 메뉴 클릭 | 모둠활동 리스트 페이지 | 모둠활동 메뉴 클릭 완료 | PASS |
| ... | ... | ... | ... | ... |
```

### 다중 TC 요약 출력 형식

```
## TC-T-01 ~ TC-T-XX 테스트 결과 요약

| TC | Test Name | Result | PASS | CHECK | FAIL | SKIP |
|---|---|--------|---|---|------|-------|
| TC-T-01 | 교사 홈 진입 테스트 | PASS | 2 | 0 | 0 | 0 |
| TC-T-02 | 홈 카드 인사이트 확인 | PASS | 2 | 0 | 0 | 0 |
| ... | ... | ... | ... | ... | ... | ... |
| **TOTAL** | | **PASS** | **90** | **0** | **0** | **2** |
```

### 결과 출력 의무 사항

1. **테스트 완료 즉시** 화면에 결과 표로 출력
2. **5개 컬럼** 형식 준수: STEP, Action, Check Item, Detail, Result
3. **요약 테이블** 포함: TC별 PASS/CHECK/FAIL/SKIP 카운트
4. **전체 결과** 표시: PASS 또는 FAIL

### JSON 결과 파일에서 읽어서 출력하는 코드

```python
import json

def display_test_result(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"## {data['test_name']}")
    print(f"**실행일시:** {data['test_date']}")
    print(f"**최종 결과:** {data['overall_result']}")
    print()
    print("| STEP | Action | Check Item | Detail | Result |")
    print("|------|--------|------------|--------|--------|")

    for step in data['steps']:
        print(f"| {step['step']} | {step['action']} | {step['check_item']} | {step['detail']} | {step['status']} |")

# 여러 TC 결과 요약 출력
def display_summary(json_files):
    print("## 테스트 결과 요약")
    print("| TC | Test Name | Result | PASS | CHECK | FAIL | SKIP |")
    print("|---|---|--------|---|---|------|-------|")

    total_pass = total_check = total_fail = total_skip = 0

    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        pass_count = sum(1 for s in data['steps'] if s['status'] == 'PASS')
        check_count = sum(1 for s in data['steps'] if s['status'] == 'CHECK')
        fail_count = sum(1 for s in data['steps'] if s['status'] == 'FAIL')
        skip_count = sum(1 for s in data['steps'] if s['status'] == 'SKIP')

        total_pass += pass_count
        total_check += check_count
        total_fail += fail_count
        total_skip += skip_count

        tc_no = data['test_name'].split(':')[0]
        print(f"| {tc_no} | {data['test_name'].split(':')[-1].strip()} | {data['overall_result']} | {pass_count} | {check_count} | {fail_count} | {skip_count} |")

    print(f"| **TOTAL** | | **PASS** | **{total_pass}** | **{total_check}** | **{total_fail}** | **{total_skip}** |")
```

## Test Script Template

See [scripts/template.py](scripts/template.py) for complete boilerplate.
