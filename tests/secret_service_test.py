import pytest
from unittest import mock
from src.services.secret_service import get_secret_payload


@mock.patch("src.services.secret_service.secretmanager.SecretManagerServiceClient")
@mock.patch("src.services.secret_service.logger")
@mock.patch("src.services.secret_service.google_crc32c")
def test_get_secret_payload(
    mock_google_crc32c,
    mock_logger,
    mock_client,
):
    mock_client.return_value.access_secret_version.return_value = mock.Mock(
        payload=mock.Mock(
            data=b"test",
            data_crc32c=0,
        )
    )
    mock_google_crc32c.Checksum.return_value.hexdigest.return_value = "0"
    mock_google_crc32c.Checksum.return_value.update.return_value = None
    payload = get_secret_payload("test-project", "test-secret", "test-version")

    assert payload == "test"
    mock_logger.debug.assert_called_once_with("Secret request response successful.")
    mock_logger.error.assert_not_called()


@mock.patch("src.services.secret_service.secretmanager.SecretManagerServiceClient")
@mock.patch("src.services.secret_service.logger")
@mock.patch("src.services.secret_service.google_crc32c")
def test_get_secret_payload_access_secret_version_error(
    mock_google_crc32c,
    mock_logger,
    mock_client,
):
    mock_client.return_value.access_secret_version.side_effect = Exception("test")
    payload = get_secret_payload("test-project", "test-secret", "test-version")

    assert payload is None
    mock_logger.exception.assert_called_once_with("Error accessing secret payload")
    mock_logger.debug.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_called_once_with("Error accessing secret payload")
