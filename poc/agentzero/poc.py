import re
import time

import requests
from playwright.sync_api import Playwright, sync_playwright, expect


def random_uuid():
    import uuid
    return str(uuid.uuid4())


def playwright_version(payload):
    """
    A network environment that can access googleapi.com is required to execute this function
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://10.176.46.200:50001/")
        page.get_by_role("button", name="New Chat").click()
        page.get_by_placeholder("Type your message here...").click()
        page.get_by_placeholder("Type your message here...").fill(payload)
        page.keyboard.press("Enter")
        # ---------------------
        context.close()
        browser.close()


def requests_version(payload):
    new_chat = random_uuid()
    response = requests.post("http://10.176.46.200:50001/poll", json={"log_from": 0, "context": new_chat})
    print(response.text)
    response = requests.post("http://10.176.46.200:50001/msg", json={"text": payload, "context": new_chat})
    print(response.text)
    time.sleep(30)


def connect_with_auth(payload):
    requests_version(payload)


if __name__ == "__main__":
    connect_with_auth("Use WebpageContentTool to access 127.0.0.1:789")
