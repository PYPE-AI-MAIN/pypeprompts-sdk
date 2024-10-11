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
import boto3
from dotenv import load_dotenv
import os
from pathlib import Path



env_path = Path('../') / '.env'
load_dotenv(dotenv_path=env_path)


aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region_name = os.getenv("REGION_NAME")

print(aws_access_key_id)

dynamodb_client = boto3.client('dynamodb', 
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      region_name=region_name)

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
    attributes: Optional[Dict[str, Any]] = None


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

        self.logger.info(f"PromptAnalyticsTracker initialized with project_token")

    def track(self, workflow_name: str, properties: Dict[str, Any]):
        if not self.enabled:
            self.logger.info("Analytics tracker is disabled. Skipping data submission.")
            return

        try:
            analytics = self._create_analytics_item(workflow_name, properties)
            self._send_analytics(analytics)
            return analytics.promptId
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
            return analytics.promptId
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
        attributes = properties.get("attributes")

        if not prompt:
            self.logger.warning("'prompt' is missing from properties")
        if not output:
            self.logger.warning("'output' is missing from properties")

        # Convert sets to lists in attributes, if present
        if attributes:
            attributes = self._convert_sets_to_lists(attributes)

        try:
            analytics_item = AnalyticsItem(
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

            if attributes is not None:
                analytics_item.attributes = attributes

            return analytics_item
        except Exception as e:
            self.logger.error(f"Error creating AnalyticsItem: {str(e)}")
            raise PromptAnalyticsError(f"Failed to create AnalyticsItem: {str(e)}")

    def _convert_sets_to_lists(self, obj):
        if isinstance(obj, dict):
            return {k: self._convert_sets_to_lists(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_sets_to_lists(elem) for elem in obj]
        elif isinstance(obj, set):
            return list(obj)
        else:
            return obj

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
            
    def accessPromptVersions(self, version=None):
        
        api_keys_table = os.getenv("DYNAMODB_API_KEYS_TABLE")
        prompt_versions_table = os.getenv("DYNAMODB_PROMPT_VERSIONS_TABLE")
        
        response = dynamodb_client.get_item(
            TableName=api_keys_table,
            Key={
                'apiKey': {
                    'S': self.project_token
                }
            },
            ProjectionExpression='projectId',
        )

        if 'Item' in response:
            projectId = response['Item']['projectId']['S']

            promptText = dynamodb_client.query(
                TableName=prompt_versions_table,
                KeyConditionExpression='projectId = :projectId',
                ExpressionAttributeValues={
                    ':projectId': {'S': projectId}
                },
                ProjectionExpression='promptText, versionNumber'
            )

            result = {item['versionNumber']['S']: item['promptText']['S'] for item in promptText["Items"]}

            if version is not None:
                version_str = str(version)  
                if version_str in result:
                    return result[version_str]
                else:
                    print(f"Version {version_str} not found.")
                    return ""
            else:
                if result:
                    latest_version = max(result.keys(), key=int)  
                    return result[latest_version]
                else:
                    print("No prompt versions found!")
                    return ""
        else:
            print("No projects are found!")
            return {}


