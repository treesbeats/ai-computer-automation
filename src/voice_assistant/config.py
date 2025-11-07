"""Configuration models for the voice automation app."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

LOGGER = logging.getLogger(__name__)


@dataclass
class SpeechRecognitionConfig:
    language: str = "en-US"
    energy_threshold: int = 300
    pause_threshold: float = 0.8
    phrase_time_limit: Optional[int] = 10
    stop_phrase: str = "stop listening"


@dataclass
class ChatGPTConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    command_prompt: str = (
        "You are a voice-controlled Windows automation assistant. "
        "Interpret the user's latest spoken instruction and respond with a JSON object "
        "containing an 'actions' array. Each action must be one of the following types: "
        "'mouse_move' (fields: x, y), 'mouse_click' (fields: button=left/right/middle, clicks=1), "
        "'type_text' (fields: text), 'hotkey' (fields: keys list), 'open_application' (fields: target), "
        "'open_website' (fields: url), or 'sleep' (fields: seconds). Use absolute screen coordinates "
        "for mouse_move. Only output valid JSON, no additional commentary.\n\nUser: {user_command}\n"
    )
    api_key_env: str = "OPENAI_API_KEY"


@dataclass
class ExecutionConfig:
    mouse_move_duration: float = 0.25
    enable_protection_prompt: bool = True
    allowed_applications: Dict[str, str] = field(
        default_factory=lambda: {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "explorer": "explorer.exe",
        }
    )


@dataclass
class AppConfig:
    speech_recognition: SpeechRecognitionConfig = field(default_factory=SpeechRecognitionConfig)
    chatgpt: ChatGPTConfig = field(default_factory=ChatGPTConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)

    @classmethod
    def from_file(cls, path: Path) -> "AppConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        speech_data = data.get("speech_recognition", {})
        chatgpt_data = data.get("chatgpt", {})
        execution_data = data.get("execution", {})

        config = cls(
            speech_recognition=SpeechRecognitionConfig(**speech_data),
            chatgpt=ChatGPTConfig(**chatgpt_data),
            execution=ExecutionConfig(**execution_data),
        )

        LOGGER.debug("Loaded configuration: %s", config)
        return config


__all__ = [
    "AppConfig",
    "SpeechRecognitionConfig",
    "ChatGPTConfig",
    "ExecutionConfig",
]
