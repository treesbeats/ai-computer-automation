"""Microphone input utilities built on top of SpeechRecognition."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

try:
    import speech_recognition as sr
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise ImportError(
        "The 'speech_recognition' package is required. Install it with 'pip install speechrecognition pyaudio'."
    ) from exc


LOGGER = logging.getLogger(__name__)


class SpeechRecognitionError(RuntimeError):
    """Raised when speech recognition fails."""


if TYPE_CHECKING:  # pragma: no cover - imported for type hints only
    from .config import SpeechRecognitionConfig


@dataclass
class SpeechRecognizer:
    config: "SpeechRecognitionConfig"
    recognizer: sr.Recognizer = None  # type: ignore[assignment]
    microphone: Optional[sr.Microphone] = None

    def __post_init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = self.config.energy_threshold
        self.recognizer.pause_threshold = self.config.pause_threshold
        LOGGER.debug(
            "Speech recognizer initialized with energy_threshold=%s pause_threshold=%s",
            self.config.energy_threshold,
            self.config.pause_threshold,
        )

    def listen_and_transcribe(self) -> str:
        if self.microphone is None:
            self.microphone = sr.Microphone()
            LOGGER.debug("Microphone initialized: %s", self.microphone)

        with self.microphone as source:
            LOGGER.info("Listening for speech...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(
                source,
                phrase_time_limit=self.config.phrase_time_limit,
            )

        try:
            LOGGER.debug("Sending audio to recognizer with language %s", self.config.language)
            return self.recognizer.recognize_google(audio, language=self.config.language)
        except sr.UnknownValueError as exc:  # pragma: no cover - depends on microphone input
            raise SpeechRecognitionError("Could not understand audio") from exc
        except sr.RequestError as exc:  # pragma: no cover - network error
            raise SpeechRecognitionError(f"Speech recognition service failed: {exc}") from exc

    def should_stop(self, transcript: str) -> bool:
        return transcript.strip().lower() == self.config.stop_phrase.lower()


__all__ = ["SpeechRecognizer", "SpeechRecognitionError"]
