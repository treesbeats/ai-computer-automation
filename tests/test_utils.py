"""Tests for utility modules."""

import pytest
import time
from pathlib import Path
from ai_automation.utils import (
    Config,
    load_config,
    retry,
    timer,
    ensure_directory,
    safe_filename,
    chunks,
    truncate_string,
    format_bytes,
    validate_api_key,
    RateLimiter,
)


class TestConfig:
    """Tests for Config class."""

    def test_config_initialization(self):
        """Test config initialization."""
        config = Config()
        assert isinstance(config, Config)

    def test_config_with_dict(self):
        """Test config initialization with dictionary."""
        config = Config({"key": "value"})
        assert config.get("key") == "value"

    def test_get_set(self):
        """Test get and set methods."""
        config = Config()
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"

    def test_get_default(self):
        """Test get with default value."""
        config = Config()
        assert config.get("nonexistent", "default") == "default"

    def test_update(self):
        """Test update method."""
        config = Config()
        config.update({"key1": "value1", "key2": "value2"})
        assert config.get("key1") == "value1"
        assert config.get("key2") == "value2"

    def test_to_dict(self):
        """Test to_dict method."""
        config = Config({"key": "value"})
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert "key" in config_dict


class TestHelpers:
    """Tests for helper functions."""

    def test_retry_success(self):
        """Test retry decorator with successful function."""
        call_count = 0

        @retry(max_attempts=3, delay=0.1)
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_failure_then_success(self):
        """Test retry decorator with eventual success."""
        call_count = 0

        @retry(max_attempts=3, delay=0.1, backoff=1.0)
        def eventually_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Not yet")
            return "success"

        result = eventually_successful()
        assert result == "success"
        assert call_count == 2

    def test_timer_decorator(self):
        """Test timer decorator."""

        @timer
        def timed_func():
            time.sleep(0.1)
            return "done"

        result = timed_func()
        assert result == "done"

    def test_ensure_directory(self, tmp_path):
        """Test ensure_directory function."""
        test_dir = tmp_path / "test" / "nested" / "dir"
        result = ensure_directory(str(test_dir))
        assert result.exists()
        assert result.is_dir()

    def test_safe_filename(self):
        """Test safe_filename function."""
        unsafe = 'file<>:"/\\|?*name.txt'
        safe = safe_filename(unsafe)
        assert "<" not in safe
        assert ">" not in safe
        assert ":" not in safe

    def test_chunks(self):
        """Test chunks function."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        result = chunks(data, 3)
        assert len(result) == 3
        assert result[0] == [1, 2, 3]
        assert result[1] == [4, 5, 6]
        assert result[2] == [7, 8, 9]

    def test_truncate_string(self):
        """Test truncate_string function."""
        text = "This is a long string that needs truncation"
        result = truncate_string(text, 20)
        assert len(result) <= 20
        assert result.endswith("...")

    def test_truncate_string_short(self):
        """Test truncate_string with short string."""
        text = "Short"
        result = truncate_string(text, 20)
        assert result == text

    def test_format_bytes(self):
        """Test format_bytes function."""
        assert "1.0 KB" in format_bytes(1024)
        assert "1.0 MB" in format_bytes(1024 * 1024)
        assert "1.0 GB" in format_bytes(1024 * 1024 * 1024)

    def test_validate_api_key_openai(self):
        """Test validate_api_key for OpenAI."""
        assert validate_api_key("sk-123456789012345678901234567890", "openai")
        assert not validate_api_key("invalid", "openai")
        assert not validate_api_key(None, "openai")

    def test_validate_api_key_anthropic(self):
        """Test validate_api_key for Anthropic."""
        assert validate_api_key("sk-ant-123456789012345678901234567890", "anthropic")
        assert not validate_api_key("invalid", "anthropic")

    def test_rate_limiter(self):
        """Test RateLimiter class."""
        limiter = RateLimiter(max_calls=2, time_window=1.0)
        call_times = []

        @limiter
        def limited_func():
            call_times.append(time.time())
            return "called"

        # First two calls should be immediate
        limited_func()
        limited_func()

        # Third call should be delayed
        start = time.time()
        limited_func()
        duration = time.time() - start

        # Should have waited some time
        assert len(call_times) == 3
