# pypeprompts

[![PyPI version](https://badge.fury.io/py/pypeprompts.svg)](https://badge.fury.io/py/pypeprompts)
[![Python Versions](https://img.shields.io/pypi/pyversions/pypeprompts.svg)](https://pypi.org/project/pypeprompts/)
[![Downloads](https://pepy.tech/badge/pypeprompts)](https://pepy.tech/project/pypeprompts)

A Python SDK for tracking and sending analytics data to Pype App.

## Important Notice

This package is designed to send data to Pype App, a SaaS application. By using this package, you agree to the terms of service of Pype App. Please ensure you have the necessary rights and permissions to send this data.

## Installation

You can install `pypeprompts` using pip:

```bash
pip install --upgrade pypeprompts
```

Or if you prefer using Poetry:

```bash
poetry add pypeprompts
```

## Requirements

- Python 3.8.1 or higher

## Usage

Here's a quick example of how to use `pypeprompts`:

```python
from pypeprompts import PromptAnalyticsTracker

# Initialize the tracker
tracker = PromptAnalyticsTracker(project_token="your_project_token")

# Track an event
tracker.track("workflow_name", {
    "prompt": "Your input prompt",
    "output": "Generated output",
    "processingTime": 1.5,
    "tags": ["tag1", "tag2"],
    "attributes": {"key": "value"}
})

# Async tracking
import asyncio

async def async_track():
    await tracker.track_async("async_workflow", {
        "prompt": "Async input prompt",
        "output": "Async generated output",
        "processingTime": 0.8,
        "tags": ["async", "example"],
        "attributes": {"async_key": "async_value"}
    })

asyncio.run(async_track())
```

## Features

- Simple API for tracking and sending analytics data to Pype App
- Synchronous and asynchronous tracking methods
- Customizable logging
- Error handling and reporting

## Configuration

You can configure the `PromptAnalyticsTracker` with the following parameters:

- `project_token` (required): Your project token for authentication
- `enabled` (optional): Set to `False` to disable tracking (default: `True`)

## Error Handling

The package uses a custom `PromptAnalyticsError` for error handling. Make sure to catch this exception in your code for proper error management.

## Logging

`pypeprompts` uses Python's built-in `logging` module. Logs are written to both a file (`prompt_analytics.log`) and the console. You can adjust the log level as needed.

## Data Privacy and Security

This package sends data to Pype App. Please ensure you comply with all applicable data protection laws and regulations when using this package. Do not send sensitive or personal information unless you have the necessary permissions and security measures in place.

## License

This project is proprietary software. All rights reserved. You are granted a limited license to use this software in conjunction with Pype App services, subject to the terms of service of Pype App.

## Support

If you encounter any problems or have any questions, please open an issue on the GitHub repository or contact the author at dhruv@pypeai.com.
