import re
import time

from config import OPENAI_API_KEY
from playwright.sync_api import Playwright, sync_playwright, expect


def connect_with_auth(payload):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://10.176.46.200:5000/")
        page.locator("#workstation-tab-btn").get_by_text("Workstation").click()
        page.locator("#workstation-iframe").content_frame.get_by_title("Load workflow", exact=True).click()
        page.locator("#workstation-iframe").content_frame.locator("#swal2-select").select_option("rce.json")
        page.locator("#workstation-iframe").content_frame.get_by_role("button", name="Load").click()
        page.locator("#workstation-iframe").content_frame.get_by_role("button", name="OK").click()
        page.locator("#workstation-iframe").content_frame.locator("#node-8").get_by_role("textbox").nth(1).click()
        page.locator("#workstation-iframe").content_frame.locator("#node-8").get_by_role("textbox").nth(1).fill(
            OPENAI_API_KEY)
        page.locator("#workstation-iframe").content_frame.get_by_title("Run the workflow").get_by_role("img").click()
        page.wait_for_selector("#workstation-iframe")
        iframe = page.query_selector("#workstation-iframe").content_frame()
        iframe.wait_for_selector("#swal2-html-container > p:nth-child(2)")
        task_id = iframe.query_selector("#swal2-html-container > p:nth-child(2)").inner_text()
        task_id = re.compile(r"(?<=^Task ID:).*$").findall(task_id)[0]
        print(f"[*] conversation created, id is {task_id}")
        page.locator("#workstation-iframe").content_frame.get_by_role("button", name="Close", exact=True).click()
        page.locator("#dashboard-tab-btn").get_by_role("img").click()

        while True:
            try:
                page.get_by_text(task_id).click(timeout=2000)
                break
            except Exception as e:
                print(e)
                page.reload()
                page.locator("#dashboard-tab-btn").get_by_role("img").click()

        page.get_by_placeholder("Input message here, Ctrl +").click()
        page.get_by_placeholder("Input message here, Ctrl +").fill(payload)
        page.get_by_role("button", name="Send").click()
        time.sleep(25)
        # ---------------------
        context.close()
        browser.close()

