import pytest
from unittest import mock


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
