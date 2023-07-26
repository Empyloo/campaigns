import os
import logging
import google_crc32c
from typing import List, Optional, Tuple
from google.cloud import secretmanager

logger = logging.getLogger(__name__)


def get_secret_payload(
    project_id: str, secret_id: str, version_id: str
) -> Optional[str]:
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": secret_name})
        logger.debug("Secret request response successful.")

        crc32c = google_crc32c.Checksum()
        crc32c.update(response.payload.data)

        if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
            logger.error("Data corruption detected for secret: {}", secret_name)
            logger.error("Error response: {}", response)
            return None

        payload = response.payload.data.decode("UTF-8")
        return payload
    except Exception:
        logger.exception("Error accessing secret payload")
        raise
