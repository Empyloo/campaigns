# Path: src/utils/get_env_vars.py
import os
import logging

logger = logging.getLogger(__name__)


class EnvVarError(Exception):
    """Exception raised for errors in the input."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


def get_env_vars() -> dict:
    try:
        return {
            "PROJECT_ID": os.environ.get("PROJECT_ID"),
            "REGION": os.environ.get("REGION"),
            "SURVEY_FUNCTION_URL": os.environ.get("SURVEY_FUNCTION_URL"),
            "SERVICE_ACCOUNT": os.environ.get("SERVICE_ACCOUNT"),
            "QUEUE_NAME": os.environ.get("QUEUE_NAME"),
            "SUPABASE_SERVICE_ROLE_SECRET_ID": os.environ.get(
                "SUPABASE_SERVICE_ROLE_SECRET_ID"
            ),
            "VERSION_ID": os.environ.get("VERSION_ID"),
            "SUPABASE_URL": os.environ.get("SUPABASE_URL"),
            "SUPABASE_ANON_KEY": os.environ.get("SUPABASE_ANON_KEY"),
        }
    except Exception as error:
        logger.error("Error getting env vars: %s", error, exc_info=True)
        raise EnvVarError("Error getting env vars") from error
