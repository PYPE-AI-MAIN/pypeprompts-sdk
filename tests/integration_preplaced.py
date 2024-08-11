import asyncio
import os
from dotenv import load_dotenv
from pypeprompts.main import PromptAnalyticsTracker
from pypeprompts.config.config import config

# Load environment variables from .env file
load_dotenv()

TEST_API_KEY = os.getenv("ANALYTICS_API_KEY")

# Initialize the tracker
tracker = PromptAnalyticsTracker(api_key=TEST_API_KEY, enabled=True)


# Simulate the streaming response
async def mock_streaming_response(messages):
    chunks = [
        "This is the first part of the response. ",
        "Here's the second part. ",
        "And finally, the conclusion.",
    ]
    for chunk in chunks:
        yield chunk
        await asyncio.sleep(0.5)  # Simulate some processing time


async def test_get_streaming_response():
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about the benefits of exercise."},
    ]

    response_content = ""
    async for chunk in mock_streaming_response(messages):
        response_content += chunk
        print(f"Received chunk: {chunk}")

    # This is where we use the tracker, similar to the original function
    tracker("roadmap_creator", prompt=str(messages), output=response_content)

    print(f"\nFinal response: {response_content}")
    print(f"\nAnalytics data sent to: {config.DEFAULT_DASHBOARD_URL}")


# Run the test
asyncio.run(test_get_streaming_response())
