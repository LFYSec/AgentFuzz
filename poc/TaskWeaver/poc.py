import os
import re
import time

from playwright.sync_api import Playwright, sync_playwright, expect
import requests
import json
import websockets
import asyncio


def random_t():
    import random
    import string
    return random.choice(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7)))


def random_uuid():
    import uuid
    return uuid.uuid4()


def taskweaver_time():
    from datetime import datetime, timezone
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return formatted_time


def playwright_version(payload):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.route(
            "**/*",
            lambda route: route.abort()
            if route.request.resource_type in ["image", "stylesheet"] else route.continue_()
        )
        page.goto("http://10.176.46.200:8000/")
        page.get_by_placeholder("Type your message here...").click()
        page.get_by_placeholder("Type your message here...").fill(payload)
        page.keyboard.press("Enter")
        time.sleep(60) # Taskweaver's reasoning takes quite a long time, about a minute, wait a while
        context.close()
        browser.close()


def connect_with_auth(payload):
    os.system("docker exec taskweaver bash -c \"chown taskweaver:taskweaver /tmp/*.log &\"")
    os.system("docker exec taskweaver bash -c \"chown taskweaver:taskweaver /tmp/*.pkl &\"")
    playwright_version(payload)
