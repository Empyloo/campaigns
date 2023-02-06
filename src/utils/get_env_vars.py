import os
import logging

logger = logging.getLogger(__name__)


def get_env_vars() -> dict:
    try:
        return {
            "PROJECT_ID": os.environ.get("PROJECT_ID"),
            "REGION": os.environ.get("REGION"),
            "SCHEDULER_FUNCTION_URL": os.environ.get("SCHEDULER_FUNCTION_URL"),
            "SERVICE_ACCOUNT": os.environ.get("SERVICE_ACCOUNT"),
            "QUEUE_NAME": os.environ.get("QUEUE_NAME"),
        }
    except Exception as error:
        logger.error("Error getting env vars: %s", error, exc_info=1)
        return {}
