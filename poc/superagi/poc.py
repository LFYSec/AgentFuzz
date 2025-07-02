
from playwright.sync_api import Playwright, sync_playwright, expect
import time
import asyncio
import inspect


def connect_with_auth(payload):
    with sync_playwright() as playwright:
        print(1111)
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://10.176.46.200:3000/")
        print("hello")
        try:
            page.click("div.cancel_action") 
        except Exception as e:
            print(f"Failed to click the element: {e}")
        page.click("div.w_100.mb_5 div.Dashboard_section__hCVzy:has-text('Agents')")
        page.click("span.agent_text.text_ellipsis:has-text('助手')")
        page.click("button.Agents_run_button__ee7D0:has-text('New Run')")
        try:
            # Locate the second <input> and fill it with a value
            second_input = page.locator("input.input_medium").nth(1)  
            second_input.fill(payload)

            # Locate the third <input> and fill in the value
            third_input = page.locator("input.input_medium").nth(2) 
            third_input.fill(payload)
        except Exception as e:
            print(f"Failed to update input values: {e}")
        button = page.get_by_role("button", name="run-icon Run")
        button.click()
        time.sleep(60)
        context.close()
        browser.close()

if __name__ == "__main__":
    content = "hello who you are?"
    try:
        if inspect.iscoroutinefunction(connect_with_auth):
            asyncio.get_event_loop().run_until_complete(connect_with_auth(content))
        else:
            connect_with_auth(content)
    except Exception as e:
        print(e)
