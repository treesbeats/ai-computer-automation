"""Pytest configuration and fixtures."""

import pytest
import os
from pathlib import Path


@pytest.fixture
def temp_env_file(tmp_path):
    """Create a temporary .env file for testing."""
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_KEY=test_value\n")
    return env_file


@pytest.fixture
def sample_config():
    """Provide a sample configuration dictionary."""
    return {
        "automation_delay": 0.5,
        "timeout": 30,
        "log_level": "INFO",
    }


@pytest.fixture(autouse=True)
def reset_env():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)
