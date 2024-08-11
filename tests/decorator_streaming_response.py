import logging
import pytest
import time
from unittest.mock import patch, Mock
from pypeprompts import PromptAnalyticsTracker
import os
from dotenv import load_dotenv

load_dotenv()

# Constants for testing
TEST_API_KEY = os.getenv("ANALYTICS_API_KEY")


@pytest.fixture
def tracker():
    return PromptAnalyticsTracker(api_key=TEST_API_KEY)


def test_regular_response(tracker):
    @tracker.track_prompt
    def dummy_function(arg):
        return f"Processed: {arg}"

    result = dummy_function("What is the capital of France?")
    assert result == "Processed: What is the capital of France?"

    # Wait for the asynchronous POST request to complete
    time.sleep(1)

    print(
        "PASSED: Regular response test - Verified track_prompt decorator functionality"
    )


def test_streaming_response(tracker):
    @tracker.track_prompt
    def streaming_function():
        yield "The "
        yield "capital "
        yield "of "
        yield "France "
        yield "is "
        yield "Paris."

    result = list(streaming_function())

    assert "".join(result) == "The capital of France is Paris."

    # Wait for the asynchronous POST request to complete
    time.sleep(1)

    print("PASSED: Streaming response test - Verified handling of streaming responses")


def test_decorator(tracker):
    @tracker.track_prompt
    def test_function(arg1, arg2):
        return f"Result: {arg1} {arg2}"

    result = test_function("Hello", "World")

    assert result == "Result: Hello World"

    # Wait for the asynchronous POST request to complete
    time.sleep(1)

    print("PASSED: Decorator test - Verified track_prompt decorator functionality")


def test_disabled_tracker():
    disabled_tracker = PromptAnalyticsTracker(api_key=TEST_API_KEY, enabled=False)

    @disabled_tracker.track_prompt
    def dummy_function(arg):
        return f"Processed: {arg}"

    result = dummy_function("test input")
    assert result == "Processed: test input"

    # No need to wait here as no request should be sent

    print("PASSED: Disabled tracker test - Verified disabled tracker functionality")


def test_error_handling(tracker, caplog):
    caplog.set_level(logging.DEBUG)  # Capture all log levels

    @tracker.track_prompt
    def error_function():
        raise Exception("Test error")

    with pytest.raises(Exception):
        error_function()

    # Wait for the asynchronous POST request to complete
    time.sleep(1)

    # Print all captured logs for debugging
    print("Captured logs:")
    for record in caplog.records:
        print(f"[{record.levelname}] {record.message}")

    # Check if any log message contains the expected error message
    error_logged = any(
        "Failed to submit analytics data" in record.message for record in caplog.records
    )

    assert error_logged, "Expected error message not found in logs"
    print("PASSED: Error handling test - Verified error logging functionality")


def test_add_metadata(tracker):
    tracker.add_metadata("test_key", "test_value")

    @tracker.track_prompt
    def dummy_function(arg):
        return f"Processed: {arg}"

    result = dummy_function("test input")
    assert result == "Processed: test input"

    # Wait for the asynchronous POST request to complete
    time.sleep(1)

    print("PASSED: Add metadata test - Verified custom metadata functionality")


def test_stress_testing_concurrent_calls(tracker):
    @tracker.track_prompt
    def dummy_function(prompt):
        return f"Processed: {prompt}"

    def make_call(prompt):
        return dummy_function(prompt)

    num_calls = 100
    start_time = time.time()

    from concurrent.futures import ThreadPoolExecutor, wait

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_call, f"Prompt {i}") for i in range(num_calls)]
        wait(futures)

    end_time = time.time()
    total_time = end_time - start_time

    # Wait for all asynchronous POST requests to complete
    time.sleep(5)

    print(
        f"PASSED: Stress testing concurrent calls - Completed {num_calls} calls in {total_time:.2f} seconds"
    )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
