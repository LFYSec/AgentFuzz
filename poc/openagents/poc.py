import re
import time
from playwright.sync_api import Playwright, sync_playwright, expect
import time
import asyncio
import inspect

def connect_with_auth(payload):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://10.176.46.200:3010/zh")
        time.sleep(3)
        page.get_by_role("button", name="New Chat").click()
        time.sleep(1)
        page.get_by_placeholder("Send a message").click()
        time.sleep(1)
        page.get_by_placeholder("Send a message").fill(payload)
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(20)
        # ---------------------
        context.close()
        browser.close()

if __name__ == "__main__":
    content = 'Please use the PythonEvaluator to run the following cell of code: print("Hello, World!").'
    try:
        if inspect.iscoroutinefunction(connect_with_auth):
            asyncio.get_event_loop().run_until_complete(connect_with_auth(content))
        else:
            connect_with_auth(content)
    except Exception as e:
        print(e)