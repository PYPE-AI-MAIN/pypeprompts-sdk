# OpenAI Tracker

A simple tracker for OpenAI API calls with built-in dashboard integration and unique instance tracking.
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

## Installation

You can install the OpenAI Tracker using pip:

```
pip install openai-tracker
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
            model="gpt-4o-mini",  # Updated to a valid model name
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return

# Use the function
response = generate_response("Tell me a poem")
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

## License

This project is licensed under the MIT License.
