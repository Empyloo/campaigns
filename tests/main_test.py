import pytest
import main

from unittest.mock import patch, Mock


@pytest.fixture
def campaign_service():
    return Mock()
