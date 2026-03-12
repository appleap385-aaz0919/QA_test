"""
QA 테스트 공통 유틸리티
- 속도 최적화된 대기 전략
- 공통 설정 및 헬퍼 함수
"""

import asyncio
from playwright.async_api import Page, TimeoutError

# 최적화된 대기 시간 설정
QUICK_WAIT = 0.5      # 빠른 대기 (요소 확인용)
SHORT_WAIT = 1        # 짧은 대기
MAX_WAIT = 30         # 최대 대기 (기존 60초에서 단축)
LOAD_TIMEOUT = 15000  # 페이지 로딩 타임아웃 (ms)


async def fast_page_wait(page: Page, wait_for_loading: bool = True):
    """
    최적화된 페이지 대기 함수
    - networkidle 대신 domcontentloaded 사용
    - 로딩 indicator 빠르게 체크
    """
    try:
        await page.wait_for_load_state("domcontentloaded", timeout=LOAD_TIMEOUT)
    except TimeoutError:
        pass

    if wait_for_loading:
        # 로딩 indicator 빠르게 체크 (최대 5초)
        try:
            loading = await page.locator(".loading").count()
            if loading > 0:
                await page.wait_for_selector(".loading", state="hidden", timeout=5000)
        except TimeoutError:
            pass

    # 짧은 안정화 대기
    await asyncio.sleep(QUICK_WAIT)


async def wait_for_new_page(context, click_action, timeout: int = MAX_WAIT * 1000):
    """
    새 창 열림 대기 (최적화됨)
    """
    async with context.expect_page(timeout=timeout) as page_info:
        await click_action()
    new_page = await page_info.value
    await fast_page_wait(new_page)
    return new_page


async def check_element_exists(page: Page, selectors: list, timeout: int = 3000) -> tuple:
    """
    요소 존재 여부 빠르게 확인
    반환: (found: bool, found_selector: str or None)
    """
    for selector in selectors:
        try:
            count = await page.locator(selector).count()
            if count > 0:
                visible = await page.locator(selector + ":visible").count()
                if visible > 0:
                    return True, selector
        except:
            continue
    return False, None


async def quick_click(page: Page, selector: str, timeout: int = 5000):
    """
    빠른 클릭 (요소 대기 후 즉시 클릭)
    """
    await page.wait_for_selector(selector, state="visible", timeout=timeout)
    await page.click(selector)


# 브라우저 실행 설정 (속도 최적화)
BROWSER_ARGS = [
    "--disable-extensions",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
]

def get_browser_config(headless: bool = False):
    """
    최적화된 브라우저 설정 반환
    """
    return {
        "headless": headless,
        "slow_mo": 50,  # 300ms -> 50ms로 단축
        "args": BROWSER_ARGS
    }
