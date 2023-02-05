import os
import logging
import json
import datetime as dt
from typing import Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential
from google.cloud import tasks_v2

logger = logging.getLogger(__name__)


class CampaignService:
    def __init__(self, env_vars):
        self.env_vars = env_vars
        self.project = env_vars.get("PROJECT_ID")
        self.location = env_vars.get("REGION")
        self.url = env_vars.get("SCHEDULER_FUNCTION_URL")
        self.audience = env_vars.get("SCHEDULER_FUNCTION_URL")
        self.service_account_email = env_vars.get("SERVICE_ACCOUNT")
        self.queue_name = env_vars.get("QUEUE_NAME")

    def check_variables(self) -> List[str]:
        """Check that all required environment variables are set."""
        variables = [
            "PROJECT_ID",
            "REGION",
            "SCHEDULER_FUNCTION_URL",
            "SERVICE_ACCOUNT",
            "QUEUE_NAME",
        ]
        undefined_variables = []
        for var in variables:
            if not self.env_vars.get(var):
                undefined_variables.append(var)
        return undefined_variables

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=3))
    def create_task(
        self, payload: dict, schedule_time: dt, queue_name: str = None
    ) -> tasks_v2.types.task.Task:
        """Create a task for a given queue with an arbitrary payload and schedule time.
        Args:
            payload: The task HTTP request body.
            schedule_time: The time the task should be scheduled for.
            queue_name: The queue name. If None, the default queue name from self.env_vars is used.
        Returns:
            The created task.
        """
        try:
            missing_env_variable = self.check_variables()
            if missing_env_variable:
                logger.error(
                    "Missing environment variables %s", missing_env_variable, exc_info=1
                )
                return None

            queue_name = queue_name or self.queue_name

            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(self.project, self.location, queue_name)
            task = {
                "http_request": {
                    "http_method": tasks_v2.HttpMethod.POST,
                    "url": self.url,
                    "oidc_token": {
                        "service_account_email": self.service_account_email,
                        "audience": self.audience,
                    },
                },
                "schedule_time": schedule_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }

            payload_str = json.dumps(payload)
            converted_payload = payload_str.encode()
            task["http_request"]["body"] = converted_payload

            response = client.create_task(request={"parent": parent, "task": task})

            logger.info("Created task %s", response.name)
            return response
        except Exception as error:
            logger.error(
                "Error creating task for queue '%s' with payload '%s' and schedule time '%s': %s",
                queue_name,
                payload,
                schedule_time,
                error,
            )
            raise

    def edit_task(self, payload: Dict):
        # code to edit a task in Cloud Tasks
        pass

    def delete_task(self, payload: Dict):
        # code to delete a task in Cloud Tasks
        pass
    
    def create_schedule(self, payload: Dict):
        # code to create a schedule in Cloud Scheduler
        pass

    def edit_schedule(self, payload: Dict):
        # code to edit a schedule in Cloud Scheduler
        pass

    def delete_schedule(self, payload: Dict):
        # code to delete a schedule in Cloud Scheduler
        pass


