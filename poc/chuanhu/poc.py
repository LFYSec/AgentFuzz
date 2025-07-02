import asyncio
import websockets
import json
import time
import sys
import re
from playwright.sync_api import Playwright, sync_playwright, expect

def connect_with_auth(payload):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://localhost:7800/")
        page.get_by_placeholder("在这里输入", exact=True).fill("123")
        page.get_by_placeholder("在这里输入", exact=True).click()
        page.locator("#submit-btn").click()
        time.sleep(3)
        while "开始生成回答" in page.content():
            time.sleep(1)
        page.close()
        context.close()
        browser.close()

if __name__ == "__main__":
    connect_with_auth("hello")