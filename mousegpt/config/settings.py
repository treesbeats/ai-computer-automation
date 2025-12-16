"""Configuration settings for MouseGPT."""

from enum import Enum
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SpeechBackend(str, Enum):
    """Available speech recognition backends."""
    GOOGLE = "google"
    WHISPER_API = "whisper_api"
    WHISPER_LOCAL = "whisper_local"
    SPHINX = "sphinx"
    WINDOWS_SAPI = "windows_sapi"  # Windows Speech API
    WINDOWS_VOICE_ACCESS = "windows_voice_access"  # Windows 11 Voice Access


class AIBackend(str, Enum):
    """Available AI backends for command parsing."""
    OPENAI = "openai"
    RULE_BASED = "rule_based"
    LOCAL = "local"


class Settings(BaseSettings):
    """MouseGPT configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="MOUSEGPT_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Speech Recognition Settings
    speech_backend: SpeechBackend = Field(
        default=SpeechBackend.GOOGLE,
        description="Speech recognition backend to use",
    )
    speech_language: str = Field(
        default="en-US",
        description="Language for speech recognition",
    )
    speech_timeout: float = Field(
        default=5.0,
        description="Timeout for speech recognition in seconds",
    )
    speech_phrase_timeout: float = Field(
        default=3.0,
        description="Timeout for phrase completion in seconds",
    )
    speech_energy_threshold: int = Field(
        default=300,
        description="Energy threshold for speech detection",
    )
    speech_dynamic_energy: bool = Field(
        default=True,
        description="Dynamically adjust energy threshold",
    )

    # Wake Word Settings
    wake_word: Optional[str] = Field(
        default="hey mouse",
        description="Wake word to activate listening (None for always-on)",
    )
    wake_word_enabled: bool = Field(
        default=True,
        description="Enable wake word detection",
    )

    # AI/NLP Settings
    ai_backend: AIBackend = Field(
        default=AIBackend.RULE_BASED,
        description="AI backend for command parsing",
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for GPT-based command parsing",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use for command parsing",
    )

    # Mouse Settings
    mouse_speed: float = Field(
        default=1.0,
        description="Mouse movement speed multiplier",
    )
    mouse_smooth_movement: bool = Field(
        default=True,
        description="Enable smooth mouse movement",
    )
    mouse_movement_duration: float = Field(
        default=0.5,
        description="Duration for mouse movement animations in seconds",
    )
    mouse_click_delay: float = Field(
        default=0.1,
        description="Delay between mouse down and up for clicks",
    )

    # Keyboard Settings
    keyboard_typing_speed: float = Field(
        default=0.05,
        description="Delay between key presses when typing",
    )
    keyboard_hold_duration: float = Field(
        default=0.1,
        description="Duration to hold keys",
    )

    # Safety Settings
    safe_mode: bool = Field(
        default=True,
        description="Enable safety features (confirm destructive actions)",
    )
    failsafe_enabled: bool = Field(
        default=True,
        description="Enable pyautogui failsafe (move to corner to abort)",
    )
    max_actions_per_command: int = Field(
        default=10,
        description="Maximum number of actions per command",
    )
    confirmation_required: bool = Field(
        default=False,
        description="Require confirmation before executing commands",
    )

    # TTS Settings
    tts_enabled: bool = Field(
        default=True,
        description="Enable text-to-speech feedback",
    )
    tts_rate: int = Field(
        default=175,
        description="Text-to-speech rate (words per minute)",
    )
    tts_volume: float = Field(
        default=0.9,
        description="Text-to-speech volume (0.0 to 1.0)",
    )

    # Logging Settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    log_commands: bool = Field(
        default=True,
        description="Log all commands to file",
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Path to log file",
    )

    # Screen Settings
    screen_capture_format: str = Field(
        default="png",
        description="Format for screen captures",
    )
    screen_highlight_duration: float = Field(
        default=0.3,
        description="Duration to highlight elements on screen",
    )

    # Windows-Specific Settings
    windows_use_sapi: bool = Field(
        default=False,
        description="Use Windows SAPI for speech recognition (Windows only)",
    )
    windows_use_shared_recognizer: bool = Field(
        default=True,
        description="Use shared Windows recognizer (integrates with Voice Control)",
    )
    windows_voice_access_integration: bool = Field(
        default=False,
        description="Enable integration with Windows 11 Voice Access",
    )
    windows_use_ui_automation: bool = Field(
        default=True,
        description="Use Windows UI Automation for element detection",
    )
    windows_use_sendinput: bool = Field(
        default=True,
        description="Use Windows SendInput API for input simulation",
    )
    windows_dictation_mode: bool = Field(
        default=True,
        description="Enable dictation mode for free-form text input",
    )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def configure(**kwargs) -> Settings:
    """Configure settings with provided values."""
    global _settings
    _settings = Settings(**kwargs)
    return _settings
