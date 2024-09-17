# pypeprompts

[![PyPI version](https://badge.fury.io/py/pypeprompts.svg)](https://badge.fury.io/py/pypeprompts)
[![Python Versions](https://img.shields.io/pypi/pyversions/pypeprompts.svg)](https://pypi.org/project/pypeprompts/)
[![Downloads](https://pepy.tech/badge/pypeprompts)](https://pepy.tech/project/pypeprompts)

A Python SDK for tracking and sending analytics data to Pype App.

## Important Notice

This package is designed to send data to Pype App, a SaaS application. By using this package, you agree to the terms of service of Pype App. Please ensure you have the necessary rights and permissions to send this data.

## Installation

### For Production Use (PyPI Package)

You can install `pypeprompts` using pip:

```bash
pip install --upgrade pypeprompts
```

Or if you prefer using Poetry:

```bash
poetry add pypeprompts
```

### For Development Use

If you're developing or contributing to `pypeprompts`, clone the repository and install it in editable mode:

```bash
git clone https://github.com/yourusername/pypeprompts.git
cd pypeprompts
poetry install
```

This will install the package in editable mode, allowing you to make changes to the code and immediately see the effects without reinstalling.

## Requirements

- Python 3.8.1 or higher

## Obtaining Your Project Token

To use `pypeprompts`, you'll need a project token. This token is used to authenticate your requests and associate the analytics data with your account. You can obtain your project token by following these steps:

1. Visit [pypeai.com](https://www.pypeai.com) and log in to your account.
2. Create a project.
3. Click on Publish to generate the token.

If you encounter any issues or need assistance obtaining your project token, please contact dhruv@pypeai.com

## Usage

Here's a quick example of how to use `pypeprompts`:

```python
from pypeprompts import PromptAnalyticsTracker

# Initialize the tracker with your project token from pypeai.com
tracker = PromptAnalyticsTracker(project_token="your_project_token")

# Track an event and get the promptId
prompt_id = tracker.track("workflow_name", {
    "prompt": "Your input prompt",
    "output": "Generated output",
    "processingTime": 1.5,
    "tags": ["tag1", "tag2"],
    "attributes": {"key": "value"}
})
print(f"Prompt ID: {prompt_id}")

# Async tracking
import asyncio

async def async_track():
    prompt_id = await tracker.track_async("async_workflow", {
        "prompt": "Async input prompt",
        "output": "Async generated output",
        "processingTime": 0.8,
        "tags": ["async", "example"],
        "attributes": {"async_key": "async_value"}
    })
    print(f"Async Prompt ID: {prompt_id}")

asyncio.run(async_track())
```

## Development Server Usage

When using `pypeprompts` in a development environment:

1. Set up environment variables:

   ```bash
   export PYPE_PROJECT_TOKEN=your_development_token
   export PYPE_ENV=development
   ```

2. In your development code:

   ```python
   import os
   from pypeprompts import PromptAnalyticsTracker

   tracker = PromptAnalyticsTracker(
       project_token=os.getenv('PYPE_PROJECT_TOKEN'),
       enabled=os.getenv('PYPE_ENV') == 'development'
   )

   # Use tracker as normal...
   ```

This setup allows you to easily switch between development and production environments by changing the `PYPE_ENV` variable.

## Features

- Simple API for tracking and sending analytics data to Pype App
- Synchronous and asynchronous tracking methods
- Returns a unique `promptId` for each tracked event
- Customizable logging
- Error handling and reporting
- Development mode for testing without affecting production data

## Configuration

You can configure the `PromptAnalyticsTracker` with the following parameters:

- `project_token` (required): Your project token for authentication (obtained from pypeai.com)
- `enabled` (optional): Set to `False` to disable tracking (default: `True`)

## Error Handling

The package uses a custom `PromptAnalyticsError` for error handling. Make sure to catch this exception in your code for proper error management.

## Logging

`pypeprompts` uses Python's built-in `logging` module. Logs are written to both a file (`prompt_analytics.log`) and the console. You can adjust the log level as needed.

## Data Privacy and Security

This package sends data to Pype App. Please ensure you comply with all applicable data protection laws and regulations when using this package. Do not send sensitive or personal information unless you have the necessary permissions and security measures in place.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details on how to get started.

## License

This project is proprietary software. All rights reserved. You are granted a limited license to use this software in conjunction with Pype App services, subject to the terms of service of Pype App.

## Support

If you encounter any problems or have any questions, please open an issue on the GitHub repository or contact the author at dhruv@pypeai.com.
