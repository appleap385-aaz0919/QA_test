"""
복습률 및 프로필 카드 디버깅
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re

LOAD_WAIT = 1
MAX_WAIT = 60


async def debug_profile_and_rate():
    """복습률과 프로필 카드 확인"""

    TEST_URL = "https://www.aidt.ai/lms-web/dev/entry-aidt-2025?school=m&subject=eng&grade=2&semester=all&authorName=yoon"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=20)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        entry_page = await context.new_page()

        try:
            await entry_page.goto(TEST_URL, timeout=60000)
            await entry_page.wait_for_load_state("networkidle")
            await asyncio.sleep(LOAD_WAIT)

            teacher_btn = entry_page.locator("button").filter(has_text="선생님 입장하기")
            async with context.expect_page(timeout=MAX_WAIT * 1000) as new_page_info:
                await teacher_btn.click()

            main_page = await new_page_info.value

            try:
                await main_page.wait_for_load_state("networkidle", timeout=MAX_WAIT * 1000)
            except:
                pass

            await asyncio.sleep(LOAD_WAIT)
            try:
                await main_page.wait_for_selector(".loading", state="hidden", timeout=30000)
            except:
                pass

            print("=" * 60)
            print("1. 프로필 카드 디버깅")
            print("=" * 60)

            # teacher-profile__image
            print("\n[teacher-profile__image]")
            profile_img = await main_page.locator(".teacher-profile__image").count()
            print(f"   count: {profile_img}")
            if profile_img > 0:
                elem = main_page.locator(".teacher-profile__image").first
                tag = await elem.evaluate("el => el.tagName")
                print(f"   tag: {tag}")

            # profile-section__name
            print("\n[profile-section__name]")
            name_count = await main_page.locator(".profile-section__name").count()
            print(f"   count: {name_count}")
            if name_count > 0:
                text = await main_page.locator(".profile-section__name").first.inner_text()
                print(f"   text: {text}")

            # profile-section__class
            print("\n[profile-section__class]")
            class_count = await main_page.locator(".profile-section__class").count()
            print(f"   count: {class_count}")
            if class_count > 0:
                text = await main_page.locator(".profile-section__class").first.inner_text()
                print(f"   text: {text}")

            # profile-section__btn
            print("\n[profile-section__btn]")
            btn_count = await main_page.locator(".profile-section__btn").count()
            print(f"   count: {btn_count}")
            if btn_count > 0:
                text = await main_page.locator(".profile-section__btn").first.inner_text()
                print(f"   text: {text}")

            # profile-section 전체
            print("\n[profile-section 전체]")
            profile_section = await main_page.locator("[class*='profile-section']").all()
            print(f"   요소 수: {len(profile_section)}")
            for i, elem in enumerate(profile_section[:5]):
                try:
                    class_name = await elem.get_attribute("class") or ""
                    text = await elem.inner_text()
                    print(f"   [{i+1}] {class_name}: {text[:80]}")
                except:
                    pass

            print("\n" + "=" * 60)
            print("2. 복습률 디버깅")
            print("=" * 60)

            # donut-center__number
            print("\n[donut-center__number]")
            donut_count = await main_page.locator(".donut-center__number").count()
            print(f"   count: {donut_count}")
            if donut_count > 0:
                text = await main_page.locator(".donut-center__number").first.inner_text()
                print(f"   text: '{text}'")

            # review-donut-chart 전체
            print("\n[review-donut-chart 전체]")
            review_chart = await main_page.locator(".review-donut-chart").count()
            if review_chart > 0:
                text = await main_page.locator(".review-donut-chart").first.inner_text()
                print(f"   text: {text}")

            # 전체 텍스트에서 복습률 확인
            print("\n[전체 텍스트에서 복습률]")
            body_text = await main_page.locator("body").inner_text()
            if "복습률" in body_text:
                idx = body_text.find("복습률")
                print(f"   주변: {body_text[idx:idx+50]}")

            # 스크린샷
            await main_page.screenshot(path="screenshots/debug_profile.png", full_page=True)
            print("\n   스크린샷: screenshots/debug_profile.png")

            print("\n15초 후 종료...")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\n에러: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    asyncio.run(debug_profile_and_rate())
