"""Configuration management utilities."""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import yaml


class Config:
    """Configuration manager for AI Computer Automation."""

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration.

        Args:
            config_dict: Optional dictionary of configuration values
        """
        self._config: Dict[str, Any] = config_dict or {}
        self._load_from_env()

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # AI Configuration
        self._config.setdefault("openai_api_key", os.getenv("OPENAI_API_KEY"))
        self._config.setdefault("anthropic_api_key", os.getenv("ANTHROPIC_API_KEY"))
        self._config.setdefault("ai_model", os.getenv("AI_MODEL", "gpt-3.5-turbo"))
        self._config.setdefault("ai_temperature", float(os.getenv("AI_TEMPERATURE", "0.7")))
        self._config.setdefault("ai_max_tokens", int(os.getenv("AI_MAX_TOKENS", "2000")))

        # Automation Settings
        self._config.setdefault("automation_delay", float(os.getenv("AUTOMATION_DELAY", "0.5")))
        self._config.setdefault("automation_timeout", int(os.getenv("AUTOMATION_TIMEOUT", "30")))
        self._config.setdefault("failsafe_enabled", os.getenv("FAILSAFE_ENABLED", "true").lower() == "true")

        # Screenshot and Vision
        self._config.setdefault("screenshot_dir", os.getenv("SCREENSHOT_DIR", "./screenshots"))
        self._config.setdefault("screenshot_format", os.getenv("SCREENSHOT_FORMAT", "png"))
        self._config.setdefault("vision_confidence_threshold", float(os.getenv("VISION_CONFIDENCE_THRESHOLD", "0.8")))

        # GUI Automation
        self._config.setdefault("gui_click_delay", float(os.getenv("GUI_CLICK_DELAY", "0.1")))
        self._config.setdefault("gui_type_delay", float(os.getenv("GUI_TYPE_DELAY", "0.05")))

        # Logging
        self._config.setdefault("log_level", os.getenv("LOG_LEVEL", "INFO"))
        self._config.setdefault("log_file", os.getenv("LOG_FILE", "./logs/automation.log"))
        self._config.setdefault("log_format", os.getenv("LOG_FORMAT", "text"))

        # Security
        self._config.setdefault("safe_mode", os.getenv("SAFE_MODE", "true").lower() == "true")
        self._config.setdefault("require_confirmation", os.getenv("REQUIRE_CONFIRMATION", "false").lower() == "true")

        # Performance
        self._config.setdefault("max_workers", int(os.getenv("MAX_WORKERS", "4")))
        self._config.setdefault("cache_enabled", os.getenv("CACHE_ENABLED", "true").lower() == "true")
        self._config.setdefault("cache_ttl", int(os.getenv("CACHE_TTL", "3600")))

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value

    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration with dictionary.

        Args:
            config_dict: Dictionary of configuration values
        """
        self._config.update(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration dictionary
        """
        return self._config.copy()

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        """
        Load configuration from YAML file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            Config instance
        """
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        with open(path, "r") as f:
            config_dict = yaml.safe_load(f)

        return cls(config_dict)

    def __repr__(self) -> str:
        """String representation of config."""
        # Mask sensitive values
        safe_config = self._config.copy()
        for key in safe_config:
            if "key" in key.lower() or "password" in key.lower() or "token" in key.lower():
                if safe_config[key]:
                    safe_config[key] = "***MASKED***"
        return f"Config({safe_config})"


def load_config(env_file: Optional[str] = None, yaml_file: Optional[str] = None) -> Config:
    """
    Load configuration from environment and optional files.

    Args:
        env_file: Optional path to .env file
        yaml_file: Optional path to YAML configuration file

    Returns:
        Config instance
    """
    # Load .env file if specified
    if env_file:
        load_dotenv(env_file)
    else:
        # Try to load from default location
        load_dotenv()

    # Create base config from environment
    config = Config()

    # Override with YAML if provided
    if yaml_file:
        yaml_config = Config.from_yaml(yaml_file)
        config.update(yaml_config.to_dict())

    return config
