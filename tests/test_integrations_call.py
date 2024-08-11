import pytest
import asyncio
from pypeprompts.main import PromptAnalyticsTracker


@pytest.fixture
def tracker():
    return PromptAnalyticsTracker(api_key="test_api_key", enabled=True)


def test_call_basic(tracker):
    result = tracker("test_label", "test_prompt", "test_output")
    assert result is None


def test_call_with_metadata(tracker):
    tracker.add_metadata("key1", "value1")
    result = tracker(
        "test_label", "test_prompt", "test_output", custom_key="custom_value"
    )
    assert result is None


def test_call_disabled(tracker):
    tracker.enabled = False
    result = tracker("test_label", "test_prompt", "test_output")
    assert result is None


@pytest.mark.asyncio
async def test_call_with_generator(tracker):
    async def mock_generator():
        yield "chunk1"
        yield "chunk2"

    gen = mock_generator()
    result = tracker("test_label", "test_prompt", gen)

    # The tracker should return the generator
    assert asyncio.iscoroutine(result) or asyncio.isfuture(result)

    # Consume the generator
    chunks = []
    async for chunk in result:
        chunks.append(chunk)

    assert chunks == ["chunk1", "chunk2"]


if __name__ == "__main__":
    pytest.main()
