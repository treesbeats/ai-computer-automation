"""Speech recognition module for MouseGPT."""

import queue
import threading
from typing import Callable, Optional, Generator
from dataclasses import dataclass
from enum import Enum

try:
    import speech_recognition as sr
except ImportError:
    sr = None

from mousegpt.config.settings import Settings, SpeechBackend, get_settings


class RecognitionState(Enum):
    """State of the speech recognizer."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    ERROR = "error"


@dataclass
class RecognitionResult:
    """Result from speech recognition."""
    text: str
    confidence: float
    is_final: bool
    raw_data: Optional[dict] = None


class SpeechRecognizer:
    """
    Speech recognition engine supporting multiple backends.

    Supports:
    - Google Speech Recognition (free, requires internet)
    - OpenAI Whisper API (requires API key)
    - Local Whisper (requires local installation)
    - CMU Sphinx (offline, less accurate)
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the speech recognizer."""
        if sr is None:
            raise ImportError(
                "speech_recognition package not installed. "
                "Install with: pip install SpeechRecognition"
            )

        self.settings = settings or get_settings()
        self.recognizer = sr.Recognizer()
        self.microphone: Optional[sr.Microphone] = None
        self.state = RecognitionState.IDLE
        self._audio_queue: queue.Queue = queue.Queue()
        self._stop_listening: Optional[Callable] = None
        self._callbacks: list[Callable[[RecognitionResult], None]] = []

        # Configure recognizer
        self.recognizer.energy_threshold = self.settings.speech_energy_threshold
        self.recognizer.dynamic_energy_threshold = self.settings.speech_dynamic_energy
        self.recognizer.pause_threshold = self.settings.speech_phrase_timeout

    def _get_microphone(self) -> sr.Microphone:
        """Get or create microphone instance."""
        if self.microphone is None:
            self.microphone = sr.Microphone()
        return self.microphone

    def calibrate(self, duration: float = 1.0) -> None:
        """
        Calibrate the recognizer for ambient noise.

        Args:
            duration: Duration to listen for ambient noise in seconds.
        """
        with self._get_microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)

    def listen_once(self, timeout: Optional[float] = None) -> Optional[RecognitionResult]:
        """
        Listen for a single phrase and return the recognition result.

        Args:
            timeout: Maximum time to wait for speech (None for settings default).

        Returns:
            RecognitionResult or None if recognition failed.
        """
        timeout = timeout or self.settings.speech_timeout
        self.state = RecognitionState.LISTENING

        try:
            with self._get_microphone() as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=self.settings.speech_phrase_timeout,
                )

            self.state = RecognitionState.PROCESSING
            return self._recognize_audio(audio)

        except sr.WaitTimeoutError:
            self.state = RecognitionState.IDLE
            return None
        except Exception as e:
            self.state = RecognitionState.ERROR
            raise RuntimeError(f"Speech recognition error: {e}") from e
        finally:
            self.state = RecognitionState.IDLE

    def _recognize_audio(self, audio: sr.AudioData) -> Optional[RecognitionResult]:
        """
        Recognize speech from audio data using configured backend.

        Args:
            audio: Audio data to recognize.

        Returns:
            RecognitionResult or None if recognition failed.
        """
        backend = self.settings.speech_backend

        try:
            if backend == SpeechBackend.GOOGLE:
                return self._recognize_google(audio)
            elif backend == SpeechBackend.WHISPER_API:
                return self._recognize_whisper_api(audio)
            elif backend == SpeechBackend.WHISPER_LOCAL:
                return self._recognize_whisper_local(audio)
            elif backend == SpeechBackend.SPHINX:
                return self._recognize_sphinx(audio)
            else:
                raise ValueError(f"Unknown speech backend: {backend}")

        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            raise RuntimeError(f"Speech recognition service error: {e}") from e

    def _recognize_google(self, audio: sr.AudioData) -> Optional[RecognitionResult]:
        """Recognize using Google Speech Recognition."""
        try:
            text = self.recognizer.recognize_google(
                audio,
                language=self.settings.speech_language,
                show_all=False,
            )
            return RecognitionResult(
                text=text,
                confidence=0.9,  # Google doesn't return confidence for simple API
                is_final=True,
            )
        except sr.UnknownValueError:
            return None

    def _recognize_whisper_api(self, audio: sr.AudioData) -> Optional[RecognitionResult]:
        """Recognize using OpenAI Whisper API."""
        if not self.settings.openai_api_key:
            raise ValueError("OpenAI API key required for Whisper API backend")

        try:
            text = self.recognizer.recognize_whisper_api(
                audio,
                api_key=self.settings.openai_api_key,
            )
            return RecognitionResult(
                text=text,
                confidence=0.95,
                is_final=True,
            )
        except sr.UnknownValueError:
            return None

    def _recognize_whisper_local(self, audio: sr.AudioData) -> Optional[RecognitionResult]:
        """Recognize using local Whisper model."""
        try:
            text = self.recognizer.recognize_whisper(
                audio,
                language=self.settings.speech_language.split("-")[0],
            )
            return RecognitionResult(
                text=text,
                confidence=0.9,
                is_final=True,
            )
        except sr.UnknownValueError:
            return None

    def _recognize_sphinx(self, audio: sr.AudioData) -> Optional[RecognitionResult]:
        """Recognize using CMU Sphinx (offline)."""
        try:
            text = self.recognizer.recognize_sphinx(audio)
            return RecognitionResult(
                text=text,
                confidence=0.7,  # Sphinx is less accurate
                is_final=True,
            )
        except sr.UnknownValueError:
            return None

    def start_continuous_listening(
        self,
        callback: Callable[[RecognitionResult], None],
    ) -> None:
        """
        Start continuous listening in the background.

        Args:
            callback: Function to call with recognition results.
        """
        if self._stop_listening is not None:
            raise RuntimeError("Already listening")

        self._callbacks.append(callback)

        def audio_callback(recognizer: sr.Recognizer, audio: sr.AudioData) -> None:
            """Callback for background listening."""
            self._audio_queue.put(audio)

        # Start background listening
        self._stop_listening = self.recognizer.listen_in_background(
            self._get_microphone(),
            audio_callback,
            phrase_time_limit=self.settings.speech_phrase_timeout,
        )

        # Start processing thread
        self._processing_thread = threading.Thread(
            target=self._process_audio_queue,
            daemon=True,
        )
        self._processing_thread.start()
        self.state = RecognitionState.LISTENING

    def _process_audio_queue(self) -> None:
        """Process audio from the queue in a separate thread."""
        while self.state == RecognitionState.LISTENING:
            try:
                audio = self._audio_queue.get(timeout=1.0)
                result = self._recognize_audio(audio)
                if result:
                    for callback in self._callbacks:
                        callback(result)
            except queue.Empty:
                continue
            except Exception:
                continue

    def stop_continuous_listening(self) -> None:
        """Stop continuous listening."""
        if self._stop_listening is not None:
            self._stop_listening(wait_for_stop=False)
            self._stop_listening = None

        self.state = RecognitionState.IDLE
        self._callbacks.clear()

    def listen_stream(self) -> Generator[RecognitionResult, None, None]:
        """
        Generator that yields recognition results continuously.

        Yields:
            RecognitionResult objects as speech is recognized.
        """
        result_queue: queue.Queue = queue.Queue()

        def callback(result: RecognitionResult) -> None:
            result_queue.put(result)

        self.start_continuous_listening(callback)

        try:
            while True:
                try:
                    result = result_queue.get(timeout=1.0)
                    yield result
                except queue.Empty:
                    continue
        finally:
            self.stop_continuous_listening()

    def check_wake_word(self, text: str) -> bool:
        """
        Check if the text contains the wake word.

        Args:
            text: Text to check for wake word.

        Returns:
            True if wake word detected or wake word is disabled.
        """
        if not self.settings.wake_word_enabled or not self.settings.wake_word:
            return True

        wake_word = self.settings.wake_word.lower()
        return wake_word in text.lower()

    def extract_command_after_wake_word(self, text: str) -> str:
        """
        Extract the command portion after the wake word.

        Args:
            text: Full recognized text.

        Returns:
            Command text after wake word, or full text if no wake word.
        """
        if not self.settings.wake_word_enabled or not self.settings.wake_word:
            return text

        wake_word = self.settings.wake_word.lower()
        text_lower = text.lower()

        if wake_word in text_lower:
            idx = text_lower.find(wake_word) + len(wake_word)
            return text[idx:].strip()

        return text

    @staticmethod
    def list_microphones() -> list[dict]:
        """
        List available microphones.

        Returns:
            List of dictionaries with microphone info.
        """
        if sr is None:
            return []

        mics = []
        for i, name in enumerate(sr.Microphone.list_microphone_names()):
            mics.append({
                "index": i,
                "name": name,
            })
        return mics
