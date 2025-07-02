import requests
import json

async def connect_with_auth(payload):
    burp0_url = "http://10.176.46.200:5670/api/v1/chat/completions"
    burp0_cookies = {"ajs_anonymous_id": "db0f1224-db39-4946-a123-33ed305c6c45"}
    burp0_headers = {"user-id": "", "accept": "text/event-stream", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.85 Safari/537.36", "Content-Type": "application/json", "Origin": "http://10.176.46.200:5670", "Referer": "http://10.176.46.200:5670/chat/?scene=chat_agent&id=ce6cb8b0-abcd-11ef-b3d8-0242ac110004&model=proxyllm", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}
    data = {}
    with open("poc/dbgpt/input.json") as f:
        data = json.load(f)
    data["user_input"] = payload
    r = requests.post(burp0_url, cookies=burp0_cookies, headers=burp0_headers, json=data)
    print(r.text)

