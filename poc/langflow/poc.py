import argparse
import json
from argparse import RawTextHelpFormatter
import requests
from typing import Optional
import warnings
import asyncio


BASE_API_URL = "http://localhost:7860"
FLOW_ID = "afa91aed-fba4-44f8-841d-f1401fc52c78"

# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
  "PythonREPLTool-j0qA1": {},
  "Agent-aUaPn": {},
  "ChatInput-5vkav": {},
  "OpenAIModel-LndHB": {}
}

def run_flow(message: str,
  output_type: str = "chat",
  input_type: str = "chat") -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/api/v1/run/{FLOW_ID}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
        "tweaks": TWEAKS
    }
    response = requests.post(api_url, json=payload)
    return response.json()

async def connect_with_auth(payload):
    run_flow(payload)

def main():
    parser = argparse.ArgumentParser(description="""Run a flow with a given message and optional tweaks.
Run it like: python <your file>.py "your message here" --endpoint "your_endpoint" --tweaks '{"key": "value"}'""",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument("message", type=str, help="The message to send to the flow")
    parser.add_argument("--endpoint", type=str, default=FLOW_ID, help="The ID or the endpoint name of the flow")
    parser.add_argument("--output_type", type=str, default="chat", help="The output type")
    parser.add_argument("--input_type", type=str, default="chat", help="The input type")

    args = parser.parse_args()

    response = run_flow(
        message=args.message,
        endpoint=args.endpoint,
        output_type=args.output_type,
        input_type=args.input_type,
    )

    print(json.dumps(response, indent=2))

