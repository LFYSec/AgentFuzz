import asyncio
import websockets
import json
import time
import sys

async def connect_with_auth(payload):
    # The URL of the WebSocket server
    uri = "ws://localhost:8000/ws/socket.io/?EIO=4&transport=websocket&sid=ZfMW557yvsONsHd_AAAC"
    extra_headers = {}      
    async with websockets.connect(uri, extra_headers=extra_headers) as websocket:
        # Send message
        
        message = '42["client_message",{"message":{"threadId":"","id":"3263c873-6347-449d-ab89-5c89eed1d8f0","name":"User","type":"user_message","output":"' + payload + '","createdAt":"2024-12-09T08:25:04.177Z"},"fileReferences":[]}]'
        r = json.dumps(message)
        await websocket.send(r)
        print(f"Sent: {r}")
        # Continue to receive server responses
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Received: {response}")
                if 'task_end' in response:
                    print("Response contains task_end, disconnecting...")
                    break
            except asyncio.TimeoutError:
                print("No response received within 5 second, disconnecting...")
                break

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(connect_with_auth("hello"))