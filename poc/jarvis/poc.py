import re
import time

from playwright.sync_api import Playwright, sync_playwright, expect



def connect_with_auth(payload):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://127.0.0.1:9999/")
        page.get_by_placeholder("Input your message").click()
        page.get_by_placeholder("Input your message").fill(payload)
        page.get_by_text("Submit").click()
        time.sleep(10)
        # ---------------------
        context.close()
        browser.close()


if __name__ == "__main__":
    connect_with_auth("Hello!")
