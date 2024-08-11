import pytest
import time
from pypeprompts import PromptAnalyticsTracker


def test_simple_tracking():
    # Initialize the tracker
    tracker = PromptAnalyticsTracker(api_key="test_api_key")

    # Define a simple function to track
    @tracker.track_prompt
    def simple_function(text):
        return f"Processed: {text}"

    # Call the function
    result = simple_function("Hello, World!")

    # Basic assertions
    assert result == "Processed: Hello, World!"

    # Wait a bit for any asynchronous operations
    time.sleep(1)

    print("Simple tracking test completed.")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
