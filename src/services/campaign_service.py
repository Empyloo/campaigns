import logging
import json
import datetime as dt
from typing import Dict, List, Union
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_exponential
from google.cloud import tasks_v2
from google.api_core.exceptions import PermissionDenied
from supacrud import Supabase, ResponseType

from src.models.campaign import Campaign

logger = logging.getLogger(__name__)


class CampaignService:
    def __init__(self, env_vars):
        self.env_vars = env_vars
        self.project = env_vars.get("PROJECT_ID")
        self.location = env_vars.get("REGION")
        self.url = env_vars.get("SURVEY_EXECUTOR_FUNCTION_URL")
        self.audience = env_vars.get("SURVEY_EXECUTOR_FUNCTION_URL")
        self.service_account_email = env_vars.get("SERVICE_ACCOUNT")
        self.queue_name = env_vars.get("QUEUE_NAME")
        self.check_variables()

    def action_dispatcher(self, action_type: str):
        """
        Selects the action to be performed based on the action type.
        Args:
            action_type: The action type.

        Returns:
            The function to be called.
        """
        if action_type == "create_campaign":
            return self.create_campaign
        elif action_type == "edit_campaign":
            return self.edit_campaign
        elif action_type == "delete_campaign":
            return self.delete_campaign
        else:
            raise ValueError(f"Invalid action type: {action_type}")

    def check_variables(self) -> Union[None, List[str]]:
        """Check that all required environment variables are set.
        If none are missing, do nothing.
        If any are missing, raise a ValueError with a list of
        the missing variables.
        """
        variables = [
            "PROJECT_ID",
            "REGION",
            "SURVEY_EXECUTOR_FUNCTION_URL",
            "SERVICE_ACCOUNT",
            "QUEUE_NAME",
        ]
        undefined_variables = []
        for var in variables:
            if not self.env_vars.get(var):
                undefined_variables.append(var)
        if undefined_variables:
            raise ValueError(
                f"Undefined environment variables: {', '.join(undefined_variables)}"
            )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=3))
    def create_task(self, payload: dict, task_name: str, schedule_time: Union[dt.datetime, None] = None, queue_name: Union[None, str] = None) -> tasks_v2.types.task.Task:  # type: ignore
        """Create a task for a given queue with an arbitrary payload and schedule time.
        Args:
            payload: The task HTTP request body.
            task_name: The task name which will be used as a unique identifier for the task.
            schedule_time: The time the task should be scheduled for.
            queue_name: The queue name. If None, the default queue name from self.env_vars is used.
        Returns:
            The created task.
        """
        try:
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
                "name": f"projects/{self.project}/locations/{self.location}/queues/{queue_name}/tasks/{task_name}",
            }
            if schedule_time:
                task["schedule_time"] = schedule_time # .strftime("%Y-%m-%dT%H:%M:%S.%fZ")  # type: ignore

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

    def edit_task(
        self,
        payload: dict,
        task_name: str,
        schedule_time: Union[dt.datetime, None] = None,
        queue_name: Union[None, str] = None,
    ):
        """
        Edits a task for a given queue.
        As tasks cannot be directly modified, this function deletes the existing task and creates a new one.
        Args:
            payload: The task HTTP request body.
            task_name: The task name which will be used as a unique identifier for the task.
            schedule_time: The time the task should be scheduled for.
            queue_name: The queue name. If None, the default queue name from self.env_vars is used.
        """
        try:
            task_deletion = self.delete_task(task_name=task_name, queue_name=queue_name)
            if task_deletion:
                self.create_task(
                    payload=payload,
                    task_name=task_name,
                    schedule_time=schedule_time,
                    queue_name=queue_name,
                )
        except Exception as error:
            logger.error("Error editing task: %s", error)
            raise

    def delete_task(self, task_name: str, queue_name: Union[None, str] = None) -> bool:
        """
        Deletes a task from a given queue.
        Args:
            task_name: The task name which is used as a unique identifier for the task.
            queue_name: The queue name. If None, the default queue name from self.env_vars is used.
        """
        try:
            client = tasks_v2.CloudTasksClient()
            task_name = f"projects/{self.project}/locations/{self.location}/queues/{queue_name or self.queue_name}/tasks/{task_name}"
            client.delete_task(name=task_name)
            return True
        except Exception as error:
            if isinstance(error, PermissionDenied):
                logger.warning("Permission denied while deleting task: %s", error)
                return False
            elif "entity was not found." in str(error):
                logger.error("Task not found: %s", task_name)
                return False
            else:
                logger.error("Error deleting task: %s", error)
                raise

    def create_campaign(self, supabase: Supabase, payload: Dict) -> ResponseType:
        """
        Creates a campaign in the campaigns table.
        If the campaign type is recurring, only a campaign is created in the campaigns table.
        If the campaign type is instant, a task is created in Cloud Tasks.
        Args:
            supabase: The Supabase instance.
            payload: The payload from the request.
        Returns:
            The created campaign.
        """
        try:
            campaign_data = Campaign(**payload)
            logger.info("Creating campaign %s", campaign_data)
            rpc_params = campaign_data.to_rpc_params()
            campaign_id = supabase.rpc(
                url="rest/v1/rpc/create_campaign",
                params=rpc_params,
            )

            logger.info("Created campaign %s", campaign_id)
            if payload["type"] == "instant":
                payload["id"] = campaign_id
                self.create_task(
                    payload=payload,
                    queue_name=self.queue_name,
                    task_name=f"{campaign_id}",
                )
            return campaign_id
        except Exception as error:
            logger.error("Error creating campaign: %s", error)
            raise

    def edit_campaign(self, supabase: Supabase, payload: Dict):
        """
        Edits a campaign in the campaigns table.
        If the campaign type is instant, the associated task in Cloud Tasks is also updated.
        Args:
            supabase: The Supabase instance.
            payload: The payload from the request.
        """
        try:
            campaign_id = payload["id"]
            updated_campaign = supabase.update(
                url=f"rest/v1/campaigns?id=eq.{campaign_id}",
                data=payload,
            )
            self.edit_task(
                payload=payload,
                task_name=f"{campaign_id}",
                queue_name=self.queue_name,
            )
            return updated_campaign
        except Exception as error:
            logger.error("Error editing campaign: %s", error)
            raise

    def delete_campaign(self, supabase: Supabase, payload: Dict):
        """
        Deletes a campaign from the campaigns table.
        If the campaign type is instant, the associated task in Cloud Tasks is also deleted.
        Args:
            supabase: The Supabase instance.
            payload: The payload from the request.
        """
        try:
            campaign_id = payload["id"]
            deleted_campaign = supabase.delete(
                url=f"rest/v1/campaigns?id=eq.{campaign_id}",
            )
            self.delete_task(task_name=f"{campaign_id}", queue_name=self.queue_name)
            print(deleted_campaign)
            logger.info("Deleted campaign %s", campaign_id)
            return deleted_campaign
        except Exception as error:
            logger.error("Error deleting campaign: %s", error)
            raise
