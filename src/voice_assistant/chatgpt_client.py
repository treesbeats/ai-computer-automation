"""Wrapper around the OpenAI Chat Completions API for structured commands."""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict

try:
    from openai import OpenAI
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise ImportError("Install the 'openai' package to communicate with ChatGPT.") from exc


LOGGER = logging.getLogger(__name__)


class ChatGPTError(RuntimeError):
    """Raised when the ChatGPT API call fails."""


if TYPE_CHECKING:  # pragma: no cover - imported for type hints only
    from .config import ChatGPTConfig


@dataclass
class ChatGPTClient:
    config: "ChatGPTConfig"

    def __post_init__(self) -> None:
        api_key = os.environ.get(self.config.api_key_env)
        if not api_key:
            raise ChatGPTError(
                f"Environment variable {self.config.api_key_env} is required to authenticate with OpenAI"
            )
        self.client = OpenAI(api_key=api_key)

    def request_actions(self, prompt: str) -> Dict[str, Any]:
        try:
            response = self.client.responses.create(
                model=self.config.model,
                input=prompt,
                temperature=self.config.temperature,
                response_format={"type": "json_object"},
            )
        except Exception as exc:  # pragma: no cover - network interaction
            raise ChatGPTError(f"Failed to call ChatGPT: {exc}") from exc

        LOGGER.debug("ChatGPT raw response: %s", response)

        try:
            message = response.output[0].content[0].text  # type: ignore[index]
        except Exception as exc:  # pragma: no cover - structure may change
            raise ChatGPTError(f"Unexpected response format: {exc}") from exc

        LOGGER.debug("ChatGPT message text: %s", message)

        try:
            return json.loads(message)
        except json.JSONDecodeError as exc:
            raise ChatGPTError(f"ChatGPT did not return valid JSON: {exc}") from exc


__all__ = ["ChatGPTClient", "ChatGPTError"]
