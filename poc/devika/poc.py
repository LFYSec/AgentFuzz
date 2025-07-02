import os
import re
import time

from playwright.sync_api import Playwright, sync_playwright, expect
import requests
import json
import websockets
import asyncio


def connect_with_auth(payload):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://127.0.0.1:13000/")
        page.get_by_role("button", name="select model ").click()
        page.get_by_role("button", name="GPT-4o-mini gpt-4o-mini").click()
        page.get_by_role("button", name="select search engine ").click()
        page.get_by_role("button", name="Google").click()
        page.get_by_role("button", name="select project ").click()
        page.get_by_role("button", name="helloworld").click()
        page.get_by_placeholder("Type your message...").click()
        page.get_by_placeholder("Type your message...").fill(payload)
        page.keyboard.press("Enter")
        time.sleep(60)
        # ---------------------
        context.close()
        browser.close()


