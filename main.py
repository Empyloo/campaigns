import os
import logging
import datetime as dt
import google_crc32c
import functions_framework
from google.cloud import secretmanager
from src.services.campaign_service import CampaignService
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
from flask import Response


@functions_framework.http
def main(request) -> Response:
    env_vars = {
        "PROJECT_ID": os.environ.get("PROJECT_ID"),
        "REGION": os.environ.get("REGION"),
        "SCHEDULER_FUNCTION_URL": os.environ.get("SCHEDULER_FUNCTION_URL"),
        "SERVICE_ACCOUNT": os.environ.get("SERVICE_ACCOUNT"),
        "QUEUE_NAME": os.environ.get("QUEUE_NAME"),
    }
    campaign_service = CampaignService(env_vars)

    payload = request.get("payload")
    action = payload.get("action")

    if action == "create_task":
        response = create_task(request, campaign_service)
    elif action == "edit_task":
        response = edit_task(request, campaign_service)
    elif action == "delete_task":
        response = delete_task(request, campaign_service)
    elif action == "edit_schedule":
        response = edit_schedule(request, campaign_service)
    elif action == "delete_schedule":
        response = delete_schedule(request, campaign_service)
    else:
        logger.error("Invalid action provided: %s", action)
        return Response(status=400, response="Invalid action provided")

    return Response(response, status=200)


def create_task(payload, campaign_service) -> str:
    schedule_time = dt.datetime.strptime(
        payload.get("schedule_time"), "%Y-%m-%d %H:%M:%S"
    )
    queue_name = payload.get("queue_name")
    campaign_service.create_task(payload, schedule_time, queue_name)
    return "Created task"


def edit_task(payload, campaign_service) -> str:
    try:
        campaign_service.edit_task(payload)
        return "Edited task"
    except Exception as error:
        logger.error("Error editing task: %s", error, exc_info=1)
        return "Error editing task %s" % error


def delete_task(payload, campaign_service) -> str:
    try:
        campaign_service.delete_task(payload)
        return "Deleted task"
    except Exception as error:
        logger.error("Error deleting task: %s", error, exc_info=1)
        return "Error deleting task %s" % error


def create_schedule(payload, campaign_service) -> str:
    try:
        campaign_service.create_cron_schedule(payload)
        return "Created schedule"
    except Exception as error:
        logger.error("Error creating schedule: %s", error, exc_info=1)
        return "Error creating schedule %s" % error


def edit_schedule(payload, campaign_service) -> str:
    try:
        campaign_service.edit_schedule(payload)
        return "Edited schedule"
    except Exception as error:
        logger.error("Error editing schedule: %s", error, exc_info=1)
        return "Error editing schedule %s" % error


def delete_schedule(payload, campaign_service) -> str:
    try:
        campaign_service.delete_schedule(payload)
        return "Deleted schedule"
    except Exception as error:
        logger.error("Error deleting schedule: %s", error, exc_info=1)
        return "Error deleting schedule %s" % error
