import re
import time

from playwright.sync_api import Playwright, sync_playwright, expect


def connect_with_auth(payload):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://10.176.46.200:8080/auth/signin")
        page.get_by_placeholder("Enter your username").click()
        page.get_by_placeholder("Enter your username").fill("admin")
        page.get_by_placeholder("Enter your password").click()
        page.get_by_placeholder("Enter your password").fill("TaskingAI321")
        page.get_by_role("button", name="Sign in").click()
        time.sleep(2)
        page.goto("http://10.176.46.200:8080/project/playground?assistant_id=X5lMqBM77cXvWWoXIYVuNfry")
        page.get_by_role("textbox").nth(2).click()
        page.get_by_role("textbox").nth(2).fill(payload)
        page.get_by_role("button", name="Send and Generate").click()
        time.sleep(15)
        # ---------------------
        context.close()
        browser.close()

