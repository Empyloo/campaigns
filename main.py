import os
import dotenv
import logging
import pandas as pd
import datetime as dt
import google_crc32c
import functions_framework
from typing import List, Optional, Tuple
from google.cloud import secretmanager
from src.services.campaign_service import CampaignService

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@functions_framework.http
def main(request) -> None:
    env_vars = {
        "PROJECT_ID": os.environ.get("PROJECT_ID"),
        "REGION": os.environ.get("REGION"),
        "SURVEY_FUNCTION_URL": os.environ.get("SURVEY_FUNCTION_URL"),
        "SERVICE_ACCOUNT": os.environ.get("SERVICE_ACCOUNT"),
        "QUEUE_NAME": os.environ.get("QUEUE_NAME")
    }
    campaign_service = CampaignService(env_vars)
    payload = request.get("payload")
    action = payload.get("action")

    if action == "create_task":
        create_task(payload, campaign_service)
    elif action == "edit_task":
        edit_task(payload, campaign_service)
    elif action == "delete_task":
        delete_task(payload, campaign_service)
    elif action == "edit_schedule":
        edit_schedule(payload, campaign_service)
    elif action == "delete_schedule":
        delete_schedule(payload, campaign_service)
    else:
        logger.error("Invalid action provided: %s", action)

def create_task(payload, campaign_service):
    schedule_time = dt.datetime.strptime(payload.get("schedule_time"), "%Y-%m-%d %H:%M:%S")
    queue_name = payload.get("queue_name")
    campaign_service.create_task(payload, schedule_time, queue_name)

def edit_task(payload, campaign_service):
    campaign_service.edit_task(payload)

def delete_task(payload, campaign_service):
    campaign_service.delete_task(payload)

def edit_schedule(payload, campaign_service):
    campaign_service.edit_schedule(payload)

def delete_schedule(payload, campaign_service):
    campaign_service.delete_schedule(payload)
