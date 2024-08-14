from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
import requests
import json
import uuid
import time
import asyncio
import aiohttp
import logging
from datetime import datetime
from .config.config import config


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
    tags: List[str] = Field(default_factory=list)


class PromptAnalyticsError(Exception):
    """Custom exception for PromptAnalyticsTracker errors"""

    pass


class PromptAnalyticsTracker:
    def __init__(
        self,
        project_token: str,
        enabled: bool = True,
    ):
        if not project_token:
            raise PromptAnalyticsError("project_token is required")

        self.instance_id = str(uuid.uuid4())
        self.project_token = project_token
        self.dashboard_url = config.DEFAULT_DASHBOARD_URL
        self.enabled = enabled

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler("prompt_analytics.log")
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.logger.info(
            f"PromptAnalyticsTracker initialized with project_token: {project_token}"
        )

    def track(self, workflow_name: str, properties: Dict[str, Any]):
        if not self.enabled:
            self.logger.info("Analytics tracker is disabled. Skipping data submission.")
            return

        try:
            analytics = self._create_analytics_item(workflow_name, properties)
            self._send_analytics(analytics)
        except Exception as e:
            self.logger.error(f"Error in track method: {str(e)}")
            raise PromptAnalyticsError(f"Failed to track analytics: {str(e)}")

    async def track_async(self, workflow_name: str, properties: Dict[str, Any]):
        if not self.enabled:
            self.logger.info("Analytics tracker is disabled. Skipping data submission.")
            return

        try:
            analytics = self._create_analytics_item(workflow_name, properties)
            await self._send_analytics_async(analytics)
        except Exception as e:
            self.logger.error(f"Error in track_async method: {str(e)}")
            raise PromptAnalyticsError(
                f"Failed to track analytics asynchronously: {str(e)}"
            )

    def _create_analytics_item(
        self, workflow_name: str, properties: Dict[str, Any]
    ) -> AnalyticsItem:
        if not workflow_name:
            raise PromptAnalyticsError("workflow_name is required")

        prompt = properties.get("prompt", "")
        output = properties.get("output", "")

        if not prompt:
            self.logger.warning("'prompt' is missing from properties")
        if not output:
            self.logger.warning("'output' is missing from properties")

        try:
            return AnalyticsItem(
                instanceId=self.instance_id,
                promptId=str(uuid.uuid4()),
                name=workflow_name,
                processingTime=properties.get("processingTime", 0.0),
                input=prompt,
                inputLength=len(prompt),
                output=output,
                outputLength=len(output),
                functionName=properties.get("functionName", workflow_name),
                tags=properties.get("tags", []),
            )
        except Exception as e:
            self.logger.error(f"Error creating AnalyticsItem: {str(e)}")
            raise PromptAnalyticsError(f"Failed to create AnalyticsItem: {str(e)}")

    def _send_analytics(self, analytics: AnalyticsItem):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.project_token}",
        }
        try:
            data = analytics.model_dump(exclude_none=True)
            self.logger.debug(f"Sending analytics data to {self.dashboard_url}")
            self.logger.debug(f"Data being sent: {json.dumps(data, indent=2)}")
            response = requests.post(
                self.dashboard_url,
                json=data,
                headers=headers,
            )
            response.raise_for_status()
            self.logger.info(
                f"Analytics data submitted successfully. Response: {response.text}"
            )
        except requests.RequestException as e:
            self.logger.error(f"Failed to submit analytics data: {e}")
            self.logger.error(
                f"Response status code: {e.response.status_code if e.response else 'N/A'}"
            )
            self.logger.error(
                f"Response content: {e.response.text if e.response else 'N/A'}"
            )
            raise PromptAnalyticsError(f"Failed to submit analytics data: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error when submitting analytics data: {e}")
            raise PromptAnalyticsError(
                f"Unexpected error when submitting analytics data: {str(e)}"
            )

    async def _send_analytics_async(self, analytics: AnalyticsItem):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.project_token}",
        }
        try:
            data = analytics.model_dump(exclude_none=True)
            self.logger.debug(f"Sending analytics data to {self.dashboard_url}")
            self.logger.debug(f"Data being sent: {json.dumps(data, indent=2)}")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.dashboard_url,
                    json=data,
                    headers=headers,
                ) as response:
                    response.raise_for_status()
                    response_text = await response.text()
                    self.logger.info(
                        f"Analytics data submitted successfully. Response: {response_text}"
                    )
        except aiohttp.ClientError as e:
            self.logger.error(f"Failed to submit analytics data: {e}")
            self.logger.error(
                f"Response status code: {e.status if hasattr(e, 'status') else 'N/A'}"
            )
            self.logger.error(
                f"Response content: {await e.text() if hasattr(e, 'text') else 'N/A'}"
            )
            raise PromptAnalyticsError(
                f"Failed to submit analytics data asynchronously: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error when submitting analytics data: {e}")
            raise PromptAnalyticsError(
                f"Unexpected error when submitting analytics data asynchronously: {str(e)}"
            )
