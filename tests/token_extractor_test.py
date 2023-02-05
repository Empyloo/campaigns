# tests/test_token_extractor.py
import pytest
from unittest.mock import Mock, patch

from src.utils.token_extractor import extract_token_from_header


def test_extract_token_from_header():
    headers = {"Authorization": "Bearer 12345"}
    assert extract_token_from_header(headers) == "12345"


def test_extract_token_from_header_no_header():
    headers = {}
    assert (
        extract_token_from_header(headers) == "Error: No Authorization header found: {}"
    )


def test_extract_token_from_header_invalid_header():
    headers = {"Authorization": "Bearer 12345 67890"}
    assert (
        extract_token_from_header(headers)
        == "Error: Invalid Authorization header, more than 2 parts: {'Authorization': 'Bearer 12345 67890'}"
    )
