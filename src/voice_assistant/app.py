"""High-level orchestration for the voice automation app."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from threading import Event
from typing import Callable, Iterable, Optional

from .chatgpt_client import ChatGPTClient
from .command_parser import CommandParser
from .config import AppConfig
from .action_executor import ActionExecutor, ExecutionError
from .speech_input import SpeechRecognizer, SpeechRecognitionError


LOGGER = logging.getLogger(__name__)


@dataclass
class VoiceAutomationApp:
    """Main entry point that wires input, interpretation, and execution."""

    config: AppConfig
    recognizer: SpeechRecognizer = field(init=False)
    chat_client: ChatGPTClient = field(init=False)
    parser: CommandParser = field(init=False)
    executor: ActionExecutor = field(init=False)

    stop_event: Event = field(init=False)

    def __post_init__(self) -> None:
        self.recognizer = SpeechRecognizer(self.config.speech_recognition)
        self.chat_client = ChatGPTClient(self.config.chatgpt)
        self.parser = CommandParser()
        self.executor = ActionExecutor(self.config.execution)
        self.stop_event = Event()

    # Internal state flags used by the dashboard to reflect status in real time.
    _running: bool = field(default=False, init=False, repr=False)

    def run(self, status_callback: Optional[Callable[[str], None]] = None) -> None:
        """Continuously listen for commands and execute them.

        Args:
            status_callback: Optional callable to receive human-readable status
                updates. This is primarily used by the graphical dashboard to
                surface the assistant's state to the user.
        """

        self._running = True
        self.stop_event.clear()
        self._notify(status_callback, "Listening for commands…")
        LOGGER.info(
            "Voice automation app started. Say '%s' to stop.",
            self.config.speech_recognition.stop_phrase,
        )

        while not self.stop_event.is_set():
            try:
                transcript = self.recognizer.listen_and_transcribe()
            except SpeechRecognitionError as exc:
                LOGGER.warning("Speech recognition failed: %s", exc)
                self._notify(status_callback, "Speech recognition failed. Waiting…")
                continue

            if not transcript:
                LOGGER.debug("No transcript captured; continuing.")
                continue

            LOGGER.info("Heard: %s", transcript)
            self._notify(status_callback, f"Heard: {transcript}")

            if self.recognizer.should_stop(transcript):
                LOGGER.info("Stop phrase detected. Shutting down.")
                self._notify(status_callback, "Stop phrase detected.")
                break

            try:
                actions = self._interpret(transcript)
            except Exception as exc:  # noqa: BLE001 - high-level loop should keep running
                LOGGER.error("Failed to interpret command: %s", exc)
                self._notify(status_callback, "Unable to interpret command.")
                continue

            self._execute(actions, status_callback)

        self._running = False
        self.stop_event.set()
        self._notify(status_callback, "Assistant stopped.")

    def stop(self) -> None:
        """Signal the run loop to exit after the current iteration."""

        LOGGER.info("Stop requested via dashboard/UI.")
        self.stop_event.set()

    @property
    def is_running(self) -> bool:
        return self._running and not self.stop_event.is_set()

    def _interpret(self, transcript: str) -> Iterable[dict]:
        prompt = self.config.chatgpt.command_prompt.format(user_command=transcript)
        LOGGER.debug("Sending prompt to ChatGPT: %s", prompt)
        structured = self.chat_client.request_actions(prompt)
        LOGGER.debug("Received structured actions: %s", structured)
        return self.parser.parse(structured)

    def _execute(
        self, actions: Iterable[dict], status_callback: Optional[Callable[[str], None]]
    ) -> None:
        if not actions:
            LOGGER.info("No actions returned for command; skipping execution.")
            self._notify(status_callback, "No actionable steps returned.")
            return

        try:
            self.executor.execute(actions)
            self._notify(status_callback, "Actions executed successfully.")
        except ExecutionError as exc:
            LOGGER.error("Execution error: %s", exc)
            self._notify(status_callback, "Execution error.")
        except Exception as exc:  # noqa: BLE001 - guard unexpected issues to keep loop running
            LOGGER.exception("Unexpected exception during execution: %s", exc)
            self._notify(status_callback, "Unexpected error during execution.")

    @staticmethod
    def _notify(
        callback: Optional[Callable[[str], None]],
        message: str,
    ) -> None:
        if callback is not None:
            try:
                callback(message)
            except Exception:  # noqa: BLE001 - guard UI callbacks from crashing core loop
                LOGGER.debug("Status callback raised unexpectedly", exc_info=True)


__all__ = ["VoiceAutomationApp"]
