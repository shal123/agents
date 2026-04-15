import os
import sys
sys.path.append("..")
import google.cloud.logging
from callback_logging import log_query_to_model, log_model_response

from dotenv import load_dotenv
from datetime import datetime, timedelta
import dateparser

from google.adk import Agent
from google.adk.models import Gemini
from google.genai import types
import google.cloud.logging
import requests


RETRY_OPTIONS = types.HttpRetryOptions(initial_delay=1, max_delay=3, attempts=30)

load_dotenv()
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

API_URL = os.environ.get("API_URL")

def add_two_numbers(a: int, b: int) -> int:
    """
    Adds two integers using a remote REST API.
    Args:
        a: The first integer
        b: The second integer
    """
    print(f"--- ADK Tool: Calling API for {a} + {b} ---")
    print(f"--- Calling API at {API_URL}/add with {a} and {b} ---")
    response = requests.post(f"{API_URL}/add", json={"a": a, "b": b})
    response.raise_for_status()
    return response.json().get("sum")


root_agent = Agent(
    name="function_tool_agent",
    model=Gemini(model=os.getenv("MODEL"), retry_options=RETRY_OPTIONS),
    description="You are a helpful assistant. Always use the add_two_numbers tool for any addition tasks.",
    instruction="""
    You are a helpful assistant. Always use the add_two_numbers tool for any addition tasks.
    """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # Add the function tools below
    tools=[add_two_numbers]

)