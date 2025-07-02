import asyncio
import websockets
import json
import time
import sys

async def connect_with_auth(payload):
    # The URL of the WebSocket server
    uri = "ws://127.0.0.1:3001/api/v1/assistant/chat/f93f8739-7f4c-47f2-883d-c2ab75af5770?t=&chat_id=5cd59dfa9d42ed4396da9745136a6fd0"

    extra_headers = {}
    extra_headers["Cookie"] = "Hm_lvt_1d2d61263f13e4b288c8da19ad3ff56d=1726506062; _ga=GA1.1.780528469.1733741703; _ga_R1FN4KJKJH=GS1.1.1733741703.1.1.1733742691.0.0.0; ajs_anonymous_id=d9c14526-ab40-4c3f-8033-ff901f767629; access_token_cookie=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ7XCJ1c2VyX25hbWVcIjogXCJhbWRpblwiLCBcInVzZXJfaWRcIjogMSwgXCJyb2xlXCI6IFwiYWRtaW5cIn0iLCJpYXQiOjE3MzQ5Mzg0NjUsIm5iZiI6MTczNDkzODQ2NSwianRpIjoiNjhmNGI3YWMtNDRjMi00YjFmLWFlOTktNTcwNWQ4Zjg2YTczIiwiZXhwIjoxNzM1MDI0ODY1LCJ0eXBlIjoiYWNjZXNzIiwiZnJlc2giOmZhbHNlfQ.wZRUTMyHfwUJBcsdpbNno4gdd17RCfj2_tae4AuUWQY; refresh_token_cookie=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbWRpbiIsImlhdCI6MTczNDkzODQ2NSwibmJmIjoxNzM0OTM4NDY1LCJqdGkiOiJlYjc5ZDZjYS1jNTM1LTRhZTUtYTdhMy1lZGZhNWM4ZmUzZTYiLCJleHAiOjE3Mzc1MzA0NjUsInR5cGUiOiJyZWZyZXNoIn0.L4fMJLq-ySozYs7ksztNml7RXlHdgJJMcyfdCGDCzUg"
            
    # Initiate a WebSocket connection via authentication header
    async with websockets.connect(uri, extra_headers=extra_headers) as websocket:
        # Send a message
        
        message = None
        with open("poc/bisheng/input.json", encoding="utf-8") as f:
            message = json.load(f)
        message["inputs"]["input"] = payload
        r = json.dumps(message)
        await websocket.send(r)
        print(f"Sent: {r}")
        # Continue to receive server responses
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Received: {response}")
                # If the response contains "category":"answer" then end early
                if '"category":"answer"' in response:
                    print("Response contains 'category':'answer', disconnecting...")
                    break
            except asyncio.TimeoutError:
                print("No response received within 5 second, disconnecting...")
                break