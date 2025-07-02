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
        page.goto("http://127.0.0.1:8501/")
        page.locator("label").filter(has_text="启用Agent").locator("span").click()
        page.get_by_text("Choose an option").click()
        page.get_by_text("系统命令").click()
        page.get_by_text("数学计算器").click()
        page.get_by_text("互联网搜索").click()
        page.get_by_text("数据库对话").click()
        # page.get_by_text("URL内容阅读").click()
        page.get_by_test_id("stChatInputTextArea").click()
        page.get_by_test_id("stChatInputTextArea").fill(payload)
        page.get_by_test_id("stChatInputSubmitButton").click()
        while "Running..." in page.content():
            time.sleep(1)
        page.close()
        context.close()
        browser.close()