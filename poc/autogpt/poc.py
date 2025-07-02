import re
import sys
import time

from playwright.sync_api import Playwright, sync_playwright, expect


def connect_with_auth(payload):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://127.0.0.1:3000/login")
        page.get_by_placeholder("user@email.com").click()
        page.get_by_placeholder("user@email.com").fill("23210240093@m.fudan.edu.cn")
        page.get_by_placeholder("password").click()
        page.get_by_placeholder("password").fill("123456")
        page.get_by_label("I agree to the Terms of Use").click()
        page.get_by_role("button", name="Log in").click()
        time.sleep(1)
        page.goto("http://127.0.0.1:3000/build?flowID=9ed7aed7-3fa7-4698-bcfd-422d106ea016")
        page.get_by_role("button", name="Skip Tutorial").click()
        time.sleep(3)
        page.get_by_role("button", name="Run", exact=True).click()
        page.get_by_placeholder("Enter value", exact=True).fill(payload)
        page.get_by_role("button", name="Run").click()
        time.sleep(15)
        # ---------------------
        context.close()
        browser.close()
        