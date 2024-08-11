import pytest
from unittest.mock import patch, MagicMock
from pypeprompts import PromptAnalyticsTracker, AnalyticsItem


@pytest.fixture
def tracker():
    return PromptAnalyticsTracker(api_key="test_api_key", enabled=True)


# Test basic functionality of the __call__ method
# Ensures that analytics are sent with correct data when called
def test_call_basic(tracker):
    with patch.object(tracker, "_send_analytics") as mock_send:
        tracker("test_label", "test_prompt", "test_output")

    mock_send.assert_called_once()
    args, _ = mock_send.call_args
    analytics_item = args[0]

    assert isinstance(analytics_item, AnalyticsItem)
    assert analytics_item.name == "test_label"
    assert analytics_item.input == "test_prompt"
    assert analytics_item.output == '"test_output"'


# Test if custom metadata is correctly included in the analytics item
# Checks both pre-added metadata and metadata passed during the call
def test_call_with_metadata(tracker):
    tracker.add_metadata("key1", "value1")

    with patch.object(tracker, "_send_analytics") as mock_send:
        tracker("test_label", "test_prompt", "test_output", custom_key="custom_value")

    mock_send.assert_called_once()
    args, _ = mock_send.call_args
    analytics_item = args[0]

    assert analytics_item.custom_fields == {
        "key1": "value1",
        "custom_key": "custom_value",
    }


# Test that no analytics are sent when the tracker is disabled
def test_call_disabled(tracker):
    tracker.enabled = False

    with patch.object(tracker, "_send_analytics") as mock_send:
        tracker("test_label", "test_prompt", "test_output")

    mock_send.assert_not_called()


# Test the handling of generator outputs
# Ensures that all chunks from the generator are collected and sent as analytics
@pytest.mark.asyncio
async def test_call_with_generator(tracker):
    async def mock_generator():
        yield "chunk1"
        yield "chunk2"

    with patch.object(tracker, "_send_analytics") as mock_send:
        result = tracker("test_label", "test_prompt", mock_generator())
        chunks = [chunk async for chunk in result]

    assert chunks == ["chunk1", "chunk2"]
    mock_send.assert_called_once()
    args, _ = mock_send.call_args
    analytics_item = args[0]

    assert analytics_item.output == '["chunk1", "chunk2"]'


if __name__ == "__main__":
    pytest.main()
