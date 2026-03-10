# AIDT LMS QA 테스트 패턴

## 진입 URL 패턴

```
https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon
```

- school: m (중학교), e (초등), h (고등)
- subject: eng (영어), math (수학)
- grade: 학년
- semester: 학기 (1, 2, all)

## 주요 클래스명

| 용도 | 클래스명 |
|------|----------|
| 모듈 보기 버튼 | `.ViewerLinkBox` |
| 단원 상세 보기 | `span:has-text('단원 상세 보기')` |
| 교과서 보기 | `button:has-text('교과서 보기')` |
| 로딩 스피너 | `.loading` |
| 대시보드 점수 | `.ai-chart__score`, `.donut-center__number` |

## 시행착오 사례

### Case 1: "단원 상세 보기" 버튼 찾지 못함

**문제**: `button:has-text('단원 상세 보기')`로 찾으려 했으나 실패

**원인**: 실제 HTML은 `<span data-v-f42de186>단원 상세 보기</span>` 형태

**해결**:
```python
detail_span = page.locator("span:has-text('단원 상세 보기')")
await detail_span.first.click()
```

### Case 2: 모듈 개수가 실제보다 적게 카운트됨

**문제**: HTML 소스에는 23개의 ViewerLinkBox가 있는데 16개만 카운트됨

**원인**: 가상 스크롤(Virtual Scroll)로 화면에 보이는 영역만 DOM에 렌더링

**해결**: 스크롤 컨테이너를 찾아서 스크롤하며 모든 요소 로드
```python
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

### Case 3: 단원 번호 오름차순 체크 실패

**문제**: "N단원" 패턴으로 찾으려 했으나 매칭 안됨

**원인**: 실제 페이지는 "Lesson 1. 단원명" 형식

**해결**:
```python
import re
lesson_pattern = re.compile(r'Lesson\s*(\d+)', re.IGNORECASE)
# '평가' 제외하고 순수 단원 번호만 추출
for line in lines:
    if '평가' not in line:
        match = lesson_pattern.search(line)
        if match:
            numbers.append(int(match.group(1)))
```

### Case 4: 마이크 권한 팝업으로 테스트 중단

**문제**: 음성 녹음 기능 사용 시 마이크 권한 팝업 발생

**해결**: 브라우저 컨텍스트 생성 후 미리 권한 허용
```python
context = await browser.new_context(viewport={"width": 1920, "height": 1080})
await context.grant_permissions(["microphone"])
```

### Case 5: 새 창이 감지되지 않음

**문제**: 버튼 클릭 후 새 창이 열리지만 감지 실패

**원인**: 클릭 후 expect_page를 설정하면 이미 늦음

**해결**: 클릭 전에 expect_page 설정
```python
async with context.expect_page(timeout=MAX_WAIT * 1000) as new_page_info:
    await button.click()  # 클릭이 expect_page 블록 안에 있어야 함

new_page = await new_page_info.value
```

### Case 6: networkidle 타임아웃 빈번 발생

**문제**: SPA에서 networkidle 대기 시 자주 타임아웃

**해결**: try-except로 무시하고 진행
```python
try:
    await page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)
except TimeoutError:
    pass  # 무시하고 계속 진행
```

### Case 7: "재구성하기" 버튼 찾지 못함

**문제**: `button:has-text('재구성하기')`로 찾으려 했으나 실패

**원인**: 실제 HTML은 `<span>재구성하기</span>` 형태로 button이 아님

**해결**: span 선택자 사용
```python
recon_btn = page.locator("span:has-text('재구성하기')")
await recon_btn.first.click()
```

### Case 8: 모달 팝업에서 확인 버튼 클릭 실패

**문제**: 임시저장 삭제 버튼 클릭 후 모달이 나타나지만, 확인 버튼 클릭이 안됨
```
Error: <div class="modal-content"> from <div class="modal-open"> subtree intercepts pointer events
```

**원인**:
1. 모달이 화면을 가려서 다른 요소 클릭 불가
2. 모달 확인 버튼의 정확한 선택자를 모름

**해결**: 모달 대기 후 정확한 클래스명으로 확인 버튼 클릭
```python
# 모달이 나타날 때까지 대기
await page.wait_for_selector(".modal-content, .modal-dialog, .modal", state="visible", timeout=5000)
await asyncio.sleep(0.5)

# 정확한 클래스명으로 확인 버튼 클릭
modal_selectors = [
    "button.btn.fill.loading-color-black.secondary.full:has-text('확인')",
    "button[class*='loading-color-black'][class*='secondary']:has-text('확인')",
    "button:has-text('확인')",
]
for selector in modal_selectors:
    try:
        modal_btn = page.locator(selector).first
        if await modal_btn.is_visible(timeout=2000):
            await modal_btn.click()
            break
    except:
        continue
```

### Case 9: 모달 닫기 후 다음 액션 수행 불가

**문제**: 모달이 열린 상태에서 다른 버튼 클릭 시도 시 실패

**원인**: 모달이 화면을 덮고 있어 다른 요소와 상호작용 불가

**해결**: 모달을 먼저 닫은 후 다음 액션 수행
```python
# ESC로 모달 닫기
try:
    await page.keyboard.press("Escape")
    await asyncio.sleep(0.5)
    await page.locator(".modal-backdrop, .modal-content").wait_for(state="hidden", timeout=3000)
except:
    # ESC로 안 닫히면 바깥쪽 클릭
    await page.mouse.click("body", position={"x": 10, "y": 10})
```

### Case 10: Python 문법 오류 (콜론 누락)

**문제**: if, else, for 문 뒤에 콜론(:) 누락으로 스크립트 실행 실패

**실패 예시**:
```python
if count > 0
    await btn.click()  # SyntaxError
else
    print("not found")  # SyntaxError
```

**해결**: 제어문 뒤에 콜론 필수 추가
```python
if count > 0:
    await btn.click()
else:
    print("not found")
```

## AIDT 모달 버튼 클래스명

| 버튼 | 클래스명 |
|------|----------|
| 확인 (기본) | `btn fill loading-color-black secondary full` |
| 삭제 | `button:has-text('삭제')` |
| 취소 | `button:has-text('취소')` |

## AIDT 주요 버튼 선택자

| 버튼명 | 선택자 |
|--------|--------|
| 재구성하기 | `span:has-text('재구성하기')` |
| 임시저장 | `button:has-text('저장')` |
| 임시저장 삭제 | `button:has-text('삭제')` |
| 미리보기 | `button:has-text('미리 보기')` |
| 단원 상세 보기 | `span:has-text('단원 상세 보기')` |
| 교과서 보기 | `button:has-text('교과서 보기')` |

### Case 11: 활동 설정 패널 닫기 버튼 찾지 못함 (TC-T-13)

**문제**: ESC 키로 패널 닫기 시도했으나 실패

**원인**: 패널 닫기 버튼이 별도의 class를 가짐

**해결**: 정확한 class 사용
```python
panel_close_selectors = [
    ".activity-setting-header-close",
    ".aidt-close-button.activity-setting-header-close",
    "button.activity-setting-header-close",
]
close_btn = activity_page.locator(".activity-setting-header-close").first
await close_btn.click()
```

**실패한 선택자**: ESC 키, `.close-btn`, `[class*='close']`

**성공한 선택자**: `.activity-setting-header-close`

### Case 12: 게시글 만들기 버튼 찾지 못함 (TC-T-13)

**문제**: 우측 하단 플로팅 버튼을 기존 선택자로 찾지 못함

**원인**: 플로팅 버튼이 별도의 class 조합을 가짐

**해결**: 정확한 class 조합 사용
```python
post_btn_selectors = [
    ".activity-float-button.activity-float-card-add",
    ".activity-float-card-add",
    "button.activity-float-button",
]
post_btn = activity_page.locator(".activity-float-button.activity-float-card-add").first
await post_btn.click()
```

**실패한 선택자**: `button:has-text('게시글 만들기')`, `.create-post-btn`

**성공한 선택자**: `.activity-float-button.activity-float-card-add`

### Case 13: 토스트 알림 확인 실패 (TC-T-13)

**문제**: 게시글 생성 후 토스트 알림을 확인하지 못함

**원인**:
1. 토스트 알림이 2초 후 자동으로 사라짐
2. `await asyncio.sleep(2)` 후에 토스트를 찾으려니 이미 사라진 상태
3. 토스트 선택자에 `.toast.show`가 없었음

**해결**: 버튼 클릭 직후 즉시 0.5초 간격으로 토스트 확인
```python
# 버튼 클릭 직후 즉시 토스트 확인 (최대 3초 대기)
toast_found = False
toast_message = ""
for wait_sec in range(6):  # 0.5초씩 6번 = 3초
    await asyncio.sleep(0.5)
    toast_selectors = [
        ".toast.show",
        ".toast",
        "[class*='toast show']",
        "[class*='toast']",
        "[class*='Toast']",
        "[class*='alert']",
        "[class*='show']",
    ]
    for selector in toast_selectors:
        toast_elements = page.locator(selector)
        count = await toast_elements.count()
        if count > 0:
            for i in range(count):
                toast_text = await toast_elements.nth(i).inner_text()
                if "게시글" in toast_text:
                    toast_found = True
                    toast_message = toast_text
                    break
        if toast_found:
            break
    if toast_found:
        break
```

**실패한 방식**: `await asyncio.sleep(2)` 후 토스트 확인

**성공한 방식**: 버튼 클릭 직후 0.5초 간격으로 즉시 확인

### Case 14: 모둠활동 리스트에서 활동 클릭 시 새 창 확인 (TC-T-12) - 성공 사례

**시나리오**: 모둠활동 리스트에서 sample 활동 클릭 > 새 창으로 모둠활동창이 열리는지 확인

**성공 코드**:
```python
# sample 행 찾기
sample_row = main_page.locator(".bar-list-item").nth(sample_index)
chapter_title = sample_row.locator(".chapter-title").first

# 새 창 열림 대기하며 클릭
async with context.expect_page(timeout=MAX_WAIT * 1000) as reopen_page_info:
    await chapter_title.click()
    print("   sample 활동 클릭")

reopened_page = await reopen_page_info.value
await reopened_page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)

# 새 창이 모둠활동창인지 확인
reopened_url = reopened_page.url
is_activity_page = "activity" in reopened_url or "board" in reopened_url
```

**핵심 포인트**:
- `.bar-list-item`에서 `.chapter-title` 찾기
- 클릭 전에 `context.expect_page()` 설정
- URL에 "activity" 또는 "board" 포함 여부로 확인

## AIDT 모둠활동 관련 클래스명

| 용도 | 클래스명 |
|------|----------|
| 활동 리스트 아이템 | `.bar-list-item` |
| 활동 제목 | `.chapter-title` |
| 활동 설정 패널 닫기 | `.activity-setting-header-close` |
| 게시글 만들기 버튼 | `.activity-float-button.activity-float-card-add` |
| 토스트 알림 | `.toast.show`, `.toast` |
| 활동 보드 URL 패턴 | `/lms/activity/board/{id}?isNew=true` |
