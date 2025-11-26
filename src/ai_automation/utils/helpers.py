"""Helper utility functions."""

import time
import functools
import logging
from typing import Callable, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}"
                        )

            raise last_exception

        return wrapper

    return decorator


def timer(func: Callable) -> Callable:
    """
    Decorator to time function execution.

    Args:
        func: Function to time

    Returns:
        Decorated function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time

        logger.debug(f"{func.__name__} took {duration:.4f}s to execute")
        return result

    return wrapper


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if it doesn't.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {dir_path}")
    return dir_path


def safe_filename(filename: str, replacement: str = "_") -> str:
    """
    Create a safe filename by removing/replacing invalid characters.

    Args:
        filename: Original filename
        replacement: Character to replace invalid characters with

    Returns:
        Safe filename
    """
    import re

    # Replace invalid characters
    safe = re.sub(r'[<>:"/\\|?*]', replacement, filename)

    # Remove leading/trailing spaces and dots
    safe = safe.strip(". ")

    # Ensure not empty
    if not safe:
        safe = "unnamed"

    logger.debug(f"Sanitized filename: '{filename}' -> '{safe}'")
    return safe


def measure_time(func: Callable, *args, **kwargs) -> tuple:
    """
    Measure execution time of a function.

    Args:
        func: Function to execute
        *args: Positional arguments for function
        **kwargs: Keyword arguments for function

    Returns:
        Tuple of (result, duration_in_seconds)
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    duration = time.time() - start_time

    return result, duration


def chunks(lst: list, chunk_size: int) -> list:
    """
    Split list into chunks.

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human-readable string.

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0

    return f"{bytes_value:.1f} PB"


def validate_api_key(api_key: Optional[str], provider: str) -> bool:
    """
    Validate API key format.

    Args:
        api_key: API key to validate
        provider: Provider name (e.g., 'openai', 'anthropic')

    Returns:
        True if valid format
    """
    if not api_key:
        return False

    api_key = api_key.strip()

    # Basic validation - check length and prefix
    if provider.lower() == "openai":
        return api_key.startswith("sk-") and len(api_key) > 20
    elif provider.lower() == "anthropic":
        return api_key.startswith("sk-ant-") and len(api_key) > 20

    # For other providers, just check it's not empty
    return len(api_key) > 10


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls: int, time_window: float):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def __call__(self, func: Callable) -> Callable:
        """Decorator to rate limit a function."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # Remove old calls outside time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

            # Check if we've exceeded the limit
            if len(self.calls) >= self.max_calls:
                oldest_call = min(self.calls)
                wait_time = self.time_window - (now - oldest_call)
                if wait_time > 0:
                    logger.warning(
                        f"Rate limit reached. Waiting {wait_time:.2f}s before calling {func.__name__}"
                    )
                    time.sleep(wait_time)
                    # Remove old calls again after waiting
                    now = time.time()
                    self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

            # Record this call
            self.calls.append(now)

            # Execute function
            return func(*args, **kwargs)

        return wrapper
