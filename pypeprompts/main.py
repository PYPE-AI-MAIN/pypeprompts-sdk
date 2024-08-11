from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Generator, AsyncGenerator
import requests
import json
import uuid
import time
import asyncio
from functools import wraps
from .config.config import config
import logging
import aiohttp


class AnalyticsItem(BaseModel):
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
        api_key: str,
        enabled: bool = True,
    ):
        self.instance_id = str(uuid.uuid4())
        self.api_key = api_key
        self.dashboard_url = config.DEFAULT_DASHBOARD_URL
        self.enabled = enabled
        self.custom_metadata: Dict[str, Any] = {}

        # Set up logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

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

                if isinstance(result, Generator):
                    return self._handle_sync_generator(
                        prompt_id, start_time, func.__name__, args, kwargs, result
                    )
                elif asyncio.iscoroutine(result) or isinstance(result, AsyncGenerator):
                    return self._handle_async_response(
                        prompt_id, start_time, func.__name__, args, kwargs, result
                    )
                else:
                    analytics = AnalyticsItem(
                        instanceId=self.instance_id,
                        promptId=prompt_id,
                        name=func.__name__,
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
                self.logger.error(f"Error in tracked function: {e}")
                analytics = AnalyticsItem(
                    instanceId=self.instance_id,
                    promptId=prompt_id,
                    name=func.__name__,
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

    def __call__(self, label: str, prompt: str, output: Any, **kwargs):
        if not self.enabled:
            return output

        prompt_id = str(
            uuid.uuid4()
        )  # Todo: Use this to correlate with prompt version in the project
        start_time = time.time()

        if asyncio.iscoroutine(output) or isinstance(output, AsyncGenerator):
            return self._handle_async_response(
                prompt_id, start_time, label, prompt, output, **kwargs
            )
        elif isinstance(output, Generator):
            return self._handle_sync_generator(
                prompt_id, start_time, label, prompt, output, **kwargs
            )
        else:
            end_time = time.time()
            analytics = AnalyticsItem(
                instanceId=self.instance_id,
                promptId=prompt_id,
                name=label,
                processingTime=end_time - start_time,
                input=prompt,
                inputLength=len(prompt),
                output=json.dumps(output),
                outputLength=len(json.dumps(output)),
                functionName=kwargs.get("function_name", ""),
                custom_fields={**self.custom_metadata, **kwargs},
            )
            self._send_analytics(analytics)
            return output

    def _handle_sync_generator(
        self,
        prompt_id: str,
        start_time: float,
        name: str,
        prompt: str,
        generator: Generator,
        **kwargs,
    ):
        full_output = []
        for chunk in generator:
            full_output.append(chunk)
            yield chunk

        end_time = time.time()
        analytics = AnalyticsItem(
            instanceId=self.instance_id,
            promptId=prompt_id,
            name=name,
            processingTime=end_time - start_time,
            input=prompt,
            inputLength=len(prompt),
            output=json.dumps(full_output),
            outputLength=len(json.dumps(full_output)),
            functionName=kwargs.get("function_name", ""),
            custom_fields={**self.custom_metadata, **kwargs},
        )
        self._send_analytics(analytics)

    async def _handle_async_response(
        self,
        prompt_id: str,
        start_time: float,
        name: str,
        prompt: str,
        generator: AsyncGenerator,
        **kwargs,
    ):
        full_output = []
        async for chunk in generator:
            full_output.append(chunk)
            yield chunk

        end_time = time.time()
        analytics = AnalyticsItem(
            instanceId=self.instance_id,
            promptId=prompt_id,
            name=name,
            processingTime=end_time - start_time,
            input=prompt,
            inputLength=len(prompt),
            output=json.dumps(full_output),
            outputLength=len(json.dumps(full_output)),
            functionName=kwargs.get("function_name", ""),
            custom_fields={**self.custom_metadata, **kwargs},
        )
        await self._send_analytics_async(analytics)

    def _send_analytics(self, analytics: AnalyticsItem):
        if not self.enabled:
            self.logger.info("Analytics tracker is disabled. Skipping data submission.")
            return

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            self.logger.debug(f"Sending analytics data to {self.dashboard_url}")
            response = requests.post(
                self.dashboard_url, json=analytics.model_dump(), headers=headers
            )
            response.raise_for_status()
            self.logger.info("Analytics data submitted successfully.")
        except requests.RequestException as e:
            self.logger.error(f"Failed to submit analytics data: {e}")
            self.logger.error(
                f"Response status code: {e.response.status_code if e.response else 'N/A'}"
            )
            self.logger.error(
                f"Response content: {e.response.text if e.response else 'N/A'}"
            )
            self.logger.error(f"Request URL: {self.dashboard_url}")
            self.logger.error(f"Request headers: {headers}")
            self.logger.error(
                f"Request payload: {json.dumps(analytics.model_dump(), indent=2)}"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error when submitting analytics data: {e}")

    async def _send_analytics_async(self, analytics: AnalyticsItem):
        if not self.enabled:
            self.logger.info("Analytics tracker is disabled. Skipping data submission.")
            return

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            self.logger.debug(f"Sending analytics data to {self.dashboard_url}")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.dashboard_url, json=analytics.model_dump(), headers=headers
                ) as response:
                    response.raise_for_status()
                    self.logger.info("Analytics data submitted successfully.")
        except aiohttp.ClientError as e:
            self.logger.error(f"Failed to submit analytics data: {e}")
            self.logger.error(
                f"Response status code: {e.status if hasattr(e, 'status') else 'N/A'}"
            )
            self.logger.error(
                f"Response content: {await e.text() if hasattr(e, 'text') else 'N/A'}"
            )
            self.logger.error(f"Request URL: {self.dashboard_url}")
            self.logger.error(f"Request headers: {headers}")
            self.logger.error(
                f"Request payload: {json.dumps(analytics.model_dump(), indent=2)}"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error when submitting analytics data: {e}")

    def add_metadata(self, key: str, value: Any):
        self.custom_metadata[key] = value
