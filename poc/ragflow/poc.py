import requests
import json
import asyncio

async def connect_with_auth(payload):
    burp0_url = "http://127.0.0.1/v1/canvas/completion"
    burp0_cookies = {"session": "sndDN4JOqExygv1oGb5E7BrKaKJ0aFDqKQUq2rZskaY"}
    burp0_headers = {}
    burp0_headers["Authorization"] = "ImYxNmEzMjAwYzEyMzExZWY5NzI2MDI0MmFjMTgwMDA2Ig.Z2lOPw.zak0H9YCF7XiVktFf0AJkVKDxnw"

    data = {}
    with open("poc/ragflow/input.json") as f:
        data = json.load(f)
    data["message"] = payload
    r = requests.post(burp0_url, cookies=burp0_cookies, headers=burp0_headers, json=data)
    print(r.content.decode('utf-8'))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(connect_with_auth("select 1;"))