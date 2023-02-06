import os
import json
import datetime as dt
import pytest
from unittest import mock
from google.cloud import tasks_v2
from src.services.campaign_service import CampaignService


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


def test_create_task_missing_env_variables(mock_env_vars, mock_client, mock_queue_path):
    """Test that the create_task method returns None if a required environment variable is missing."""
    campaign_service = CampaignService(mock_env_vars)
    payload = {"test": "test"}
    schedule_time = dt.datetime.now()
    mock_client.return_value.create_task.return_value = tasks_v2.types.task.Task()
    mock_queue_path.return_value = "test-queue-path"
    mock_env_vars["PROJECT_ID"] = None
    task = campaign_service.create_task(payload, schedule_time)
    assert task is None
    assert not mock_client.return_value.create_task.called


def test_create_task_retry(mock_env_vars, mock_client, mock_queue_path):
    """Test that the create_task method retries if the first attempt fails."""
    campaign_service = CampaignService(mock_env_vars)
    payload = {"test": "test"}
    schedule_time = dt.datetime.now()
    mock_client.return_value.create_task.side_effect = Exception("test exception")
    mock_queue_path.return_value = "test-queue-path"
    with pytest.raises(Exception):
        campaign_service.create_task(payload, schedule_time)
    assert mock_client.return_value.create_task.call_count == 3


def test_create_task_retry_success(mock_env_vars, mock_client, mock_queue_path):
    """Test that the create_task method retries if the first attempt fails."""
    campaign_service = CampaignService(mock_env_vars)
    payload = {"test": "test"}
    schedule_time = dt.datetime.now()
    mock_client.return_value.create_task.side_effect = [
        Exception("test exception"),
        tasks_v2.types.task.Task(),
    ]
    mock_queue_path.return_value = "test-queue-path"
    task = campaign_service.create_task(payload, schedule_time)
    assert isinstance(task, tasks_v2.types.task.Task)
    assert mock_client.return_value.create_task.call_count == 2
