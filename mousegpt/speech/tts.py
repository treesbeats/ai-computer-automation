"""Text-to-speech module for MouseGPT feedback."""

import threading
from typing import Optional
from queue import Queue

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

from mousegpt.config.settings import Settings, get_settings


class TextToSpeech:
    """
    Text-to-speech engine for voice feedback.

    Provides audible feedback for command execution and status updates.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the text-to-speech engine."""
        self.settings = settings or get_settings()
        self._engine: Optional[pyttsx3.Engine] = None
        self._speech_queue: Queue = Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False

    def _get_engine(self) -> pyttsx3.Engine:
        """Get or create the TTS engine."""
        if pyttsx3 is None:
            raise ImportError(
                "pyttsx3 package not installed. "
                "Install with: pip install pyttsx3"
            )

        if self._engine is None:
            self._engine = pyttsx3.init()
            self._configure_engine()
        return self._engine

    def _configure_engine(self) -> None:
        """Configure the TTS engine with current settings."""
        if self._engine is None:
            return

        self._engine.setProperty('rate', self.settings.tts_rate)
        self._engine.setProperty('volume', self.settings.tts_volume)

    def speak(self, text: str, block: bool = False) -> None:
        """
        Speak the given text.

        Args:
            text: Text to speak.
            block: If True, block until speech is complete.
        """
        if not self.settings.tts_enabled:
            return

        if block:
            self._speak_sync(text)
        else:
            self._speak_async(text)

    def _speak_sync(self, text: str) -> None:
        """Speak text synchronously."""
        engine = self._get_engine()
        engine.say(text)
        engine.runAndWait()

    def _speak_async(self, text: str) -> None:
        """Queue text for asynchronous speaking."""
        self._speech_queue.put(text)

        if not self._running:
            self._start_worker()

    def _start_worker(self) -> None:
        """Start the background worker thread."""
        if self._worker_thread is not None and self._worker_thread.is_alive():
            return

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True,
        )
        self._worker_thread.start()

    def _worker_loop(self) -> None:
        """Background worker loop for async speech."""
        engine = self._get_engine()

        while self._running or not self._speech_queue.empty():
            try:
                text = self._speech_queue.get(timeout=0.5)
                engine.say(text)
                engine.runAndWait()
                self._speech_queue.task_done()
            except Exception:
                continue

    def stop(self) -> None:
        """Stop any ongoing speech."""
        self._running = False
        if self._engine is not None:
            self._engine.stop()

        # Clear the queue
        while not self._speech_queue.empty():
            try:
                self._speech_queue.get_nowait()
            except Exception:
                break

    def wait(self) -> None:
        """Wait for all queued speech to complete."""
        self._speech_queue.join()

    @staticmethod
    def list_voices() -> list[dict]:
        """
        List available voices.

        Returns:
            List of dictionaries with voice info.
        """
        if pyttsx3 is None:
            return []

        engine = pyttsx3.init()
        voices = []

        for voice in engine.getProperty('voices'):
            voices.append({
                "id": voice.id,
                "name": voice.name,
                "languages": voice.languages,
                "gender": voice.gender,
            })

        return voices

    def set_voice(self, voice_id: str) -> None:
        """
        Set the voice to use for speech.

        Args:
            voice_id: ID of the voice to use.
        """
        engine = self._get_engine()
        engine.setProperty('voice', voice_id)

    def confirm(self, action: str) -> None:
        """
        Speak a confirmation message.

        Args:
            action: Description of the action being confirmed.
        """
        self.speak(f"Executing: {action}")

    def error(self, message: str) -> None:
        """
        Speak an error message.

        Args:
            message: Error message to speak.
        """
        self.speak(f"Error: {message}")

    def ready(self) -> None:
        """Indicate that the system is ready for commands."""
        self.speak("MouseGPT ready")

    def listening(self) -> None:
        """Indicate that the system is listening."""
        self.speak("Listening")

    def acknowledged(self) -> None:
        """Acknowledge a command."""
        self.speak("Got it")
