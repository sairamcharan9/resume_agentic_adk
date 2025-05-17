"""
Pytest configuration file for the Resume Optimizer project.

This file contains fixtures and configuration used across test modules.
"""

import os
import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_openai_api_key():
    """Automatically mock the OPENAI_API_KEY environment variable for all tests."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-api-key"}):
        yield
