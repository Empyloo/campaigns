import pytest
from unittest import mock

from src.utils.get_env_vars import get_env_vars


@mock.patch("src.utils.get_env_vars.logger")
def test_get_env_vars(mock_logger):
    os_environ = {
        "PROJECT_ID": "project_id",
        "REGION": "region",
        "SURVEY_EXECUTOR_FUNCTION_URL": "SURVEY_EXECUTOR_FUNCTION_URL",
        "SERVICE_ACCOUNT": "service_account",
        "QUEUE_NAME": "queue_name",
    }
    with mock.patch.dict("os.environ", os_environ):
        env_vars = get_env_vars()
        assert env_vars == os_environ
        mock_logger.error.assert_not_called()

    with mock.patch.dict("os.environ", {}):
        env_vars = get_env_vars()
        assert env_vars == {
            "PROJECT_ID": None,
            "REGION": None,
            "SURVEY_EXECUTOR_FUNCTION_URL": None,
            "SERVICE_ACCOUNT": None,
            "QUEUE_NAME": None,
        }
