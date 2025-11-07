"""Utilities for validating structured commands produced by ChatGPT."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

LOGGER = logging.getLogger(__name__)


SUPPORTED_ACTIONS = {
    "mouse_move": {"required": {"x": int, "y": int}},
    "mouse_click": {
        "required": {"button": str},
        "optional": {"clicks": int},
    },
    "type_text": {"required": {"text": str}},
    "hotkey": {"required": {"keys": list}},
    "open_application": {"required": {"target": str}},
    "open_website": {"required": {"url": str}},
    "sleep": {"required": {"seconds": (int, float)}},
}


class CommandValidationError(RuntimeError):
    """Raised when ChatGPT returns malformed actions."""


@dataclass
class CommandParser:
    strict: bool = True

    def parse(self, response: Any) -> List[Dict[str, Any]]:
        data = self._load_json(response)
        LOGGER.debug("Parsing actions from data: %s", data)

        if not isinstance(data, dict):
            raise CommandValidationError("Expected top-level JSON object with an 'actions' array")

        actions = data.get("actions")
        if not isinstance(actions, list):
            raise CommandValidationError("Missing or invalid 'actions' array in response")

        validated: List[Dict[str, Any]] = []
        for action in actions:
            validated.append(self._validate_action(action))

        return validated

    def _load_json(self, response: Any) -> Any:
        if isinstance(response, dict):
            return response

        if isinstance(response, str):
            try:
                return json.loads(response)
            except json.JSONDecodeError as exc:
                raise CommandValidationError(f"ChatGPT response was not valid JSON: {exc}") from exc

        raise CommandValidationError(f"Unsupported response type: {type(response)!r}")

    def _validate_action(self, action: Any) -> Dict[str, Any]:
        if not isinstance(action, dict):
            raise CommandValidationError(f"Action must be an object: {action!r}")

        action_type = action.get("type")
        if action_type not in SUPPORTED_ACTIONS:
            raise CommandValidationError(f"Unsupported action type: {action_type}")

        schema = SUPPORTED_ACTIONS[action_type]
        validated: Dict[str, Any] = {"type": action_type}

        for field, expected_type in schema.get("required", {}).items():
            if field not in action:
                raise CommandValidationError(f"Missing required field '{field}' for action {action_type}")
            value = action[field]
            self._check_type(field, value, expected_type)
            validated[field] = value

        for field, expected_type in schema.get("optional", {}).items():
            if field in action:
                value = action[field]
                self._check_type(field, value, expected_type)
                validated[field] = value

        return validated

    def _check_type(self, field: str, value: Any, expected: Any) -> None:
        if isinstance(expected, tuple):
            if not isinstance(value, expected):
                raise CommandValidationError(f"Field '{field}' expected types {expected} but received {type(value)}")
        else:
            if expected is list and not isinstance(value, list):
                raise CommandValidationError(f"Field '{field}' must be a list")
            elif expected is int and not isinstance(value, int):
                raise CommandValidationError(f"Field '{field}' must be an integer")
            elif expected is str and not isinstance(value, str):
                raise CommandValidationError(f"Field '{field}' must be a string")


__all__ = ["CommandParser", "CommandValidationError", "SUPPORTED_ACTIONS"]
