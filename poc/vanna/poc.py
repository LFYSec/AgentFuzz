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
        page.goto("http://localhost:8501/")
        page.get_by_test_id("stChatInputTextArea").click()
        page.get_by_test_id("stChatInputTextArea").fill("hi")
        page.get_by_test_id("stChatInputSubmitButton").click()
        time.sleep(3)
        while "..." in page.content():
            time.sleep(1)
        page.close()
        context.close()
        browser.close()

if __name__ == "__main__":
    connect_with_auth("hello")