import pytest
import asyncio
import os
from dotenv import load_dotenv
from pypeprompts import PromptAnalyticsTracker, PromptAnalyticsError
import aiohttp
import json

# Load environment variables
load_dotenv()

PROJECT_TOKEN = os.getenv("PROJECT_TOKEN")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:3000/api/analytics")


@pytest.fixture
def tracker():
    return PromptAnalyticsTracker(project_token=PROJECT_TOKEN, enabled=True)


def test_tracker_initialization(tracker):
    assert tracker.project_token == PROJECT_TOKEN
    assert tracker.enabled == True
    assert tracker.dashboard_url == DASHBOARD_URL


def test_tracker_initialization_error():
    with pytest.raises(PromptAnalyticsError, match="project_token is required"):
        PromptAnalyticsTracker(project_token="")


def test_sync_tracking(tracker):
    messages = [
        {
            """
            \"System: \\nYour task is to take a set of facts, ensure they fit a certain criteria, then return the facts in exactly the same format as the input, but with the criteria met. Make sure to NOT CHANGE THE FACT AT ALL, make as minimal changes as possible to meet the criteria.\\n\\n# Criteria 1: Every fact should only use the first name of the client, never anything else.\\n- The output facts should follow the following criteria: Every fact should only use the first name of the client, never anything else.\\n- The fact should not refer to the client as 'the client', 'He', 'She', 'Speaker B', .... It should refer to them as the first name.\\n- The fact may refer to other names (e.g. the partner's name may be mentioned), ensure that these names are not changed.\\n\\n# Criteria 2: The fact should use British English\\n- The fact should use British English instead of American English or any other dialect.\\n- Ensure that the spelling, grammar, and punctuation are all in British English.\\n- For example, 'color' should be changed to 'colour', 'center' should be changed to 'centre', 'realize' should be changed to 'realise', etc.\\n\\n# Response Format\\n- The response should be in EXACTLY the same JSON format as the input.\\n- Ensure that you return ALL facts from the input. If you receive 1, return 1. If you receive 10, return 10. Do not change the number of facts in the response.\\n\\n\\nHuman: Here the facts for client Nikhil:\\n[{\\\"id\\\": 4, \\\"fact\\\": \\\"\\\\nHe has historically set aside money annually for holidays, vehicle expenses, and Christmas. He believes in financial stability and the reason he has\\\\nset aside money annually for holidays, vehicle expenses, and Christmas.\\\\nHe can be confident that he has set aside money annually for holidays, vehicle expenses, and Christmas.\\\\n\\\", \\\"first_name\\\": \\\"Nikhil\\\"
            """
        },
    ]

    response_content = '{"id": 4, "fact": "\\nNikhil has historically set aside money annually for holidays, vehicle expenses, and Christmas. Nikhil believes in financial stability and the reason Nikhil has\\nset aside money annually for holidays, vehicle expenses, and Christmas.\\nNikhil can be confident that Nikhil has set aside money annually for holidays, vehicle expenses, and Christmas.\\n", "first_name": "Nikhil"}'

    workflow_name = "saturn fact check"
    properties = {
        "prompt": str(messages),
        "output": response_content,
        "processingTime": 0.5,
        "functionName": "fact_polishing",
        "tags": ["pronoun issue"],
        "attributes": {
            "user_category": "Fresher",
            "domain": "Frontend",
            "slide_type": "MCQ",
        },
    }

    try:
        id = tracker.track(workflow_name, properties)
        print("Prompt Id:", id)
        # If no exception is raised, the test passes
        assert True
    except PromptAnalyticsError as e:
        print(f"Detailed error: {str(e)}")
        pytest.fail(f"Failed to send analytics data: {str(e)}")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
