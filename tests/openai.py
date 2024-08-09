# Not to be run in CI/CD. Just for Manual testing
import os
from dotenv import load_dotenv
from openai import OpenAI
from pypeprompts import PromptAnalyticsTracker

# Load environment variables from .env file
load_dotenv()

# Load API keys and project ID from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
analytics_api_key = os.getenv("ANALYTICS_API_KEY")

# Ensure the required environment variables are set
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
if not analytics_api_key:
    raise ValueError("ANALYTICS_API_KEY environment variable is not set")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Initialize the PromptAnalyticsTracker
tracker = PromptAnalyticsTracker(
    name="OpenAI API Tracker",
    api_key=analytics_api_key,
    enabled=True,
)


@tracker.track_prompt
def generate_text(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Updated to a valid model name
            messages=[
                {
                    "role": "system",
                    "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        print("Total tokens:", response.usage.total_tokens)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return ""


# Example usage
if __name__ == "__main__":
    result = generate_text("Write a short poem about Python programming.")
