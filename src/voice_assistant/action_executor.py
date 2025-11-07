"""Execute validated automation commands on Windows."""
from __future__ import annotations

import logging
import subprocess
import time
import webbrowser
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Iterable

try:
    import pyautogui
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise ImportError("Install 'pyautogui' to send mouse and keyboard events.") from exc

pyautogui.FAILSAFE = True

LOGGER = logging.getLogger(__name__)


class ExecutionError(RuntimeError):
    """Raised when executing actions fails."""


if TYPE_CHECKING:  # pragma: no cover - imported for type hints only
    from .config import ExecutionConfig


@dataclass
class ActionExecutor:
    config: "ExecutionConfig"

    def execute(self, actions: Iterable[Dict[str, object]]) -> None:
        for action in actions:
            action_type = action["type"]
            LOGGER.info("Executing action: %s", action)

            if action_type == "mouse_move":
                self._mouse_move(action)
            elif action_type == "mouse_click":
                self._mouse_click(action)
            elif action_type == "type_text":
                self._type_text(action)
            elif action_type == "hotkey":
                self._hotkey(action)
            elif action_type == "open_application":
                self._open_application(action)
            elif action_type == "open_website":
                self._open_website(action)
            elif action_type == "sleep":
                self._sleep(action)
            else:  # pragma: no cover - guarded by parser
                raise ExecutionError(f"Unsupported action type: {action_type}")

    def _mouse_move(self, action: Dict[str, object]) -> None:
        x = int(action["x"])
        y = int(action["y"])
        LOGGER.debug("Moving mouse to (%s, %s)", x, y)
        pyautogui.moveTo(x, y, duration=self.config.mouse_move_duration)

    def _mouse_click(self, action: Dict[str, object]) -> None:
        button = str(action["button"])
        clicks = int(action.get("clicks", 1))
        LOGGER.debug("Clicking %s button %s times", button, clicks)
        pyautogui.click(button=button, clicks=clicks)

    def _type_text(self, action: Dict[str, object]) -> None:
        text = str(action["text"])
        LOGGER.debug("Typing text: %s", text)
        pyautogui.typewrite(text)

    def _hotkey(self, action: Dict[str, object]) -> None:
        keys = action["keys"]
        if not isinstance(keys, list):  # pragma: no cover - parser should enforce
            raise ExecutionError("Hotkey action requires a list of keys")
        key_sequence = [str(k) for k in keys]
        LOGGER.debug("Pressing hotkey sequence: %s", key_sequence)
        pyautogui.hotkey(*key_sequence)

    def _open_application(self, action: Dict[str, object]) -> None:
        target = str(action["target"]).lower()
        executable = self.config.allowed_applications.get(target)
        if not executable:
            raise ExecutionError(
                f"Application '{target}' is not in the allowed list. Update configuration to permit it."
            )
        LOGGER.debug("Launching application: %s", executable)
        try:
            subprocess.Popen([executable])
        except OSError as exc:
            raise ExecutionError(f"Failed to launch {executable}: {exc}") from exc

    def _open_website(self, action: Dict[str, object]) -> None:
        url = str(action["url"])
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ExecutionError("Website URLs must start with http:// or https://")
        LOGGER.debug("Opening website: %s", url)
        webbrowser.open(url)

    def _sleep(self, action: Dict[str, object]) -> None:
        seconds = float(action["seconds"])
        LOGGER.debug("Sleeping for %s seconds", seconds)
        time.sleep(seconds)


__all__ = ["ActionExecutor", "ExecutionError"]
