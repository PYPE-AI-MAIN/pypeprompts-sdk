from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
import requests
import json
import uuid
import time
from functools import wraps
from .config.config import config


class AnalyticsItem(BaseModel):
    # projectId: str
    instanceId: str
    promptId: str
    name: str
    processingTime: float
    input: str
    inputLength: int
    output: str
    outputLength: int
    functionName: str
    timestamp: Optional[str] = None
    error: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class PromptAnalyticsTracker:
    def __init__(
        self,
        name: str,
        api_key: str,
        enabled: bool = True,
    ):
        self.instance_id = str(uuid.uuid4())
        self.name = name
        self.api_key = api_key
        self.dashboard_url = config.DEFAULT_DASHBOARD_URL
        self.enabled = enabled
        self.custom_metadata: Dict[str, Any] = {}

    def track_prompt(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return func(*args, **kwargs)

            prompt_id = str(uuid.uuid4())
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()

                analytics = AnalyticsItem(
                    instanceId=self.instance_id,
                    promptId=prompt_id,
                    name=self.name,
                    processingTime=end_time - start_time,
                    input=json.dumps({"args": args, "kwargs": kwargs}),
                    inputLength=len(json.dumps({"args": args, "kwargs": kwargs})),
                    output=json.dumps(result),
                    outputLength=len(json.dumps(result)),
                    functionName=func.__name__,
                    custom_fields=self.custom_metadata,
                )
                self._send_analytics(analytics)
                return result
            except Exception as e:
                end_time = time.time()
                analytics = AnalyticsItem(
                    instanceId=self.instance_id,
                    promptId=prompt_id,
                    name=self.name,
                    processingTime=end_time - start_time,
                    input=json.dumps({"args": args, "kwargs": kwargs}),
                    inputLength=len(json.dumps({"args": args, "kwargs": kwargs})),
                    output="",
                    outputLength=0,
                    functionName=func.__name__,
                    error=str(e),
                    custom_fields=self.custom_metadata,
                )
                self._send_analytics(analytics)
                raise

        return wrapper

    def _send_analytics(self, analytics: AnalyticsItem):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            response = requests.post(
                self.dashboard_url, json=analytics.model_dump(), headers=headers
            )
            response.raise_for_status()
            print("Analytics data submitted successfully.")
        except requests.RequestException as e:
            print(f"Failed to submit analytics data: {e}")
            print(
                f"Response status code: {e.response.status_code if e.response else 'N/A'}"
            )
            print(f"Response content: {e.response.text if e.response else 'N/A'}")
            print(f"Request URL: {self.dashboard_url}")
            print(f"Request headers: {headers}")
            print(f"Request payload: {json.dumps(analytics.model_dump(), indent=2)}")

    def add_metadata(self, key: str, value: Any):
        self.custom_metadata[key] = value
