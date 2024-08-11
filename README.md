# OpenAI Tracker

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/openai-tracker.svg)](https://badge.fury.io/py/openai-tracker)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/openai-tracker)](https://github.com/yourusername/openai-tracker/issues)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/openai-tracker)](https://github.com/yourusername/openai-tracker/stargazers)

A simple tracker for OpenAI API calls with built-in dashboard integration and unique instance tracking.

## Features

- Easy integration with OpenAI API
- Built-in dashboard for analytics
- Unique instance tracking
- Support for multiple trackers in a single application

## Installation

You can install the OpenAI Tracker using pip:

```bash
pip install pypeprompts
```

Or if you're using Poetry:

```bash
poetry add pypeprompts
```

## Usage

### Basic Usage

For simple use cases where you want all tracked calls to share the same instance ID:

```python
from openai import OpenAI
from pypeprompts import PromptAnalyticsTracker

client = OpenAI(api_key="your-api-key")

# Initialize the PromptAnalyticsTracker
tracker = PromptAnalyticsTracker(
    name="OpenAI API Tracker",
    api_key=analytics_api_key,
)

@tracker.track_prompt
def generate_text(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return

# Use the function
response = generate_text("Tell me a poem")
print(response)
```

### Advanced Usage

For cases where you want to track different parts of your application separately:

```python
from openai import OpenAI
from pypeprompts import PromptAnalyticsTracker

client = OpenAI(api_key="your-api-key")

# Create separate trackers for different parts of your application
user_tracker = PromptAnalyticsTracker(
    name="User prompts tracker",
    api_key=analytics_api_key,
)
admin_tracker = PromptAnalyticsTracker(
    name="Admin prompts tracker",
    api_key=analytics_api_key,
)

@user_tracker.track_prompt
def user_generate_response(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

@admin_tracker.track_prompt
def admin_generate_response(prompt):
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    return completion.choices[0].message.content

# Use the functions
user_response = user_generate_response("Tell me a joke")
admin_response = admin_generate_response("Explain quantum computing")
```

## Configuration

Detailed configuration options and environment variables...

## Dashboard

Information about accessing and using the built-in dashboard...

## Contributing

We welcome contributions to OpenAI Tracker! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## Testing

To run the tests, use the following command:

```bash
poetry run pytest
```

## Changelog

See the [CHANGELOG.md](CHANGELOG.md) file for details on what has changed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for their excellent API
- Contributors who have helped to improve this project
