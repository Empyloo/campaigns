import os
import json
import datetime as dt
import pytest
from unittest import mock
from google.cloud import tasks_v2
from src.services.campaign_service import CampaignService


@pytest.fixture
def mock_env_vars():
    return {
        "PROJECT_ID": "test-project",
        "REGION": "test-region",
        "SCHEDULER_FUNCTION_URL": "test-url",
        "SERVICE_ACCOUNT": "test-service-account",
        "QUEUE_NAME": "test-queue-name",
    }


@pytest.fixture
def mock_client(mock_env_vars):
    """Mock the tasks_v2.CloudTasksClient object."""
    with mock.patch("google.cloud.tasks_v2.CloudTasksClient") as mock_client:
        yield mock_client


@pytest.fixture
def mock_queue_path(mock_client):
    """Mock the queue_path method of the tasks_v2.CloudTasksClient object."""
    mock_queue_path = mock.Mock(
        return_value="projects/my-project/locations/us-central1/queues/my-queue"
    )
    mock_client.return_value.queue_path = mock_queue_path
    yield mock_queue_path


def test_check_variables(mock_env_vars):
    """Test that the check_variables method returns a list of missing environment variables."""
    campaign_service = CampaignService(mock_env_vars)
    assert campaign_service.check_variables() == []


def test_create_task(mock_env_vars, mock_client, mock_queue_path):
    """Test that the create_task method returns a task object."""
    campaign_service = CampaignService(mock_env_vars)
    payload = {"test": "test"}
    schedule_time = dt.datetime.now()
    mock_client.return_value.create_task.return_value = tasks_v2.types.task.Task()
    mock_queue_path.return_value = "test-queue-path"
    task = campaign_service.create_task(payload, schedule_time)
    assert isinstance(task, tasks_v2.types.task.Task)
    assert mock_client.return_value.create_task.called_once()