"""
Windows Speech Recognition using SAPI (Speech API).

This module provides integration with Windows native speech recognition,
leveraging the Windows Speech Platform for high-quality dictation.
"""

import threading
import queue
from typing import Callable, Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Windows-specific imports (only available on Windows)
try:
    import win32com.client
    import pythoncom
    SAPI_AVAILABLE = True
except ImportError:
    SAPI_AVAILABLE = False

try:
    # Alternative: Windows Speech Recognition via ctypes
    import ctypes
    from ctypes import wintypes
    CTYPES_AVAILABLE = True
except ImportError:
    CTYPES_AVAILABLE = False


class SAPIRecognitionState(Enum):
    """State of SAPI recognition."""
    INACTIVE = 0
    ACTIVE = 1
    ACTIVE_ALWAYS = 2
    INACTIVE_WITH_PURGE = 3


@dataclass
class WindowsRecognitionResult:
    """Result from Windows speech recognition."""
    text: str
    confidence: float
    is_final: bool
    rule_name: Optional[str] = None
    semantic_value: Optional[Dict[str, Any]] = None


class WindowsSpeechRecognizer:
    """
    Windows Speech Recognition using SAPI.

    Integrates with Windows native speech recognition for:
    - Dictation mode (free-form speech)
    - Command mode (grammar-based recognition)
    - Hybrid mode (both dictation and commands)

    This leverages the same engine used by Windows Voice Control
    and Windows Speech Recognition.
    """

    def __init__(
        self,
        use_shared_recognizer: bool = True,
        language: str = "en-US",
    ):
        """
        Initialize Windows Speech Recognizer.

        Args:
            use_shared_recognizer: Use the shared Windows recognizer (recommended).
            language: Recognition language (e.g., "en-US", "en-GB").
        """
        if not SAPI_AVAILABLE:
            raise ImportError(
                "pywin32 is required for Windows SAPI integration. "
                "Install with: pip install pywin32"
            )

        self.use_shared_recognizer = use_shared_recognizer
        self.language = language
        self._recognizer = None
        self._context = None
        self._grammar = None
        self._dictation_grammar = None
        self._is_listening = False
        self._result_queue: queue.Queue = queue.Queue()
        self._callbacks: List[Callable[[WindowsRecognitionResult], None]] = []
        self._recognition_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # SAPI constants
        self.SPRS_INACTIVE = 0
        self.SPRS_ACTIVE = 1
        self.SPRS_ACTIVE_ALWAYS = 2

    def _initialize_sapi(self) -> None:
        """Initialize SAPI COM objects."""
        pythoncom.CoInitialize()

        if self.use_shared_recognizer:
            # Use shared recognizer (Windows Speech Recognition)
            self._recognizer = win32com.client.Dispatch(
                "SAPI.SpSharedRecognizer"
            )
        else:
            # Create in-process recognizer
            self._recognizer = win32com.client.Dispatch(
                "SAPI.SpInprocRecognizer"
            )
            # Set up audio input
            audio_input = win32com.client.Dispatch("SAPI.SpMMAudioIn")
            self._recognizer.AudioInput = audio_input

        # Create recognition context
        self._context = self._recognizer.CreateRecoContext()

        # Set up event handlers
        self._setup_event_handlers()

    def _setup_event_handlers(self) -> None:
        """Set up SAPI event handlers."""
        # Enable recognition events
        self._context.EventInterests = (
            win32com.client.constants.SRERecognition |
            win32com.client.constants.SREHypothesis |
            win32com.client.constants.SRESoundStart |
            win32com.client.constants.SRESoundEnd |
            win32com.client.constants.SREPhraseStart |
            win32com.client.constants.SREInterference
        )

    def create_command_grammar(
        self,
        commands: Dict[str, List[str]],
        grammar_name: str = "MouseGPT",
    ) -> None:
        """
        Create a command grammar for recognition.

        Args:
            commands: Dictionary mapping command names to phrase lists.
            grammar_name: Name for the grammar.

        Example:
            commands = {
                "click": ["click", "tap", "select"],
                "scroll_up": ["scroll up", "page up"],
                "scroll_down": ["scroll down", "page down"],
            }
        """
        if self._context is None:
            self._initialize_sapi()

        # Create grammar
        self._grammar = self._context.CreateGrammar()

        # Create rules for each command
        rule_id = 1
        for command_name, phrases in commands.items():
            rule = self._grammar.Rules.Add(
                command_name,
                win32com.client.constants.SRATopLevel | win32com.client.constants.SRADynamic,
                rule_id
            )
            rule_id += 1

            # Add phrases to rule
            for phrase in phrases:
                rule.InitialState.AddWordTransition(None, phrase)

        # Commit grammar
        self._grammar.Rules.Commit()

    def enable_dictation(self) -> None:
        """Enable dictation mode for free-form speech."""
        if self._context is None:
            self._initialize_sapi()

        # Create dictation grammar
        self._dictation_grammar = self._context.CreateGrammar()
        self._dictation_grammar.DictationLoad()

    def start_listening(
        self,
        dictation: bool = True,
        commands: bool = True,
    ) -> None:
        """
        Start listening for speech.

        Args:
            dictation: Enable dictation recognition.
            commands: Enable command recognition.
        """
        if self._is_listening:
            return

        if self._context is None:
            self._initialize_sapi()

        # Enable grammars
        if dictation and self._dictation_grammar:
            self._dictation_grammar.DictationSetState(self.SPRS_ACTIVE)

        if commands and self._grammar:
            self._grammar.CmdSetRuleState(None, self.SPRS_ACTIVE)

        self._is_listening = True
        self._stop_event.clear()

        # Start recognition thread
        self._recognition_thread = threading.Thread(
            target=self._recognition_loop,
            daemon=True,
        )
        self._recognition_thread.start()

    def stop_listening(self) -> None:
        """Stop listening for speech."""
        if not self._is_listening:
            return

        self._stop_event.set()
        self._is_listening = False

        # Disable grammars
        if self._dictation_grammar:
            self._dictation_grammar.DictationSetState(self.SPRS_INACTIVE)

        if self._grammar:
            self._grammar.CmdSetRuleState(None, self.SPRS_INACTIVE)

        # Wait for thread to finish
        if self._recognition_thread:
            self._recognition_thread.join(timeout=2.0)

    def _recognition_loop(self) -> None:
        """Main recognition loop running in background thread."""
        pythoncom.CoInitialize()

        try:
            while not self._stop_event.is_set():
                # Pump COM messages
                pythoncom.PumpWaitingMessages()

                # Check for recognition results
                try:
                    result = self._result_queue.get_nowait()
                    for callback in self._callbacks:
                        try:
                            callback(result)
                        except Exception:
                            pass
                except queue.Empty:
                    pass

                # Small sleep to prevent CPU spinning
                self._stop_event.wait(0.05)

        finally:
            pythoncom.CoUninitialize()

    def on_recognition(
        self,
        callback: Callable[[WindowsRecognitionResult], None],
    ) -> None:
        """
        Register a callback for recognition results.

        Args:
            callback: Function to call with recognition results.
        """
        self._callbacks.append(callback)

    def recognize_once(self, timeout: float = 10.0) -> Optional[WindowsRecognitionResult]:
        """
        Recognize a single utterance.

        Args:
            timeout: Maximum time to wait for speech.

        Returns:
            Recognition result or None if timeout.
        """
        result_container = {"result": None}
        event = threading.Event()

        def callback(result: WindowsRecognitionResult):
            result_container["result"] = result
            event.set()

        self._callbacks.append(callback)
        self.start_listening()

        event.wait(timeout)

        self.stop_listening()
        self._callbacks.remove(callback)

        return result_container["result"]

    def get_recognizer_status(self) -> Dict[str, Any]:
        """Get the current status of the recognizer."""
        if self._recognizer is None:
            return {"initialized": False}

        return {
            "initialized": True,
            "is_listening": self._is_listening,
            "has_grammar": self._grammar is not None,
            "has_dictation": self._dictation_grammar is not None,
            "language": self.language,
            "shared": self.use_shared_recognizer,
        }

    @staticmethod
    def get_installed_recognizers() -> List[Dict[str, str]]:
        """
        Get list of installed speech recognizers.

        Returns:
            List of recognizer info dictionaries.
        """
        if not SAPI_AVAILABLE:
            return []

        pythoncom.CoInitialize()
        try:
            recognizers = []
            tokens = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
            tokens.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Recognizers")

            for token in tokens.EnumerateTokens():
                recognizers.append({
                    "id": token.Id,
                    "description": token.GetDescription(),
                })

            return recognizers
        except Exception:
            return []
        finally:
            pythoncom.CoUninitialize()

    @staticmethod
    def get_installed_voices() -> List[Dict[str, str]]:
        """
        Get list of installed TTS voices.

        Returns:
            List of voice info dictionaries.
        """
        if not SAPI_AVAILABLE:
            return []

        pythoncom.CoInitialize()
        try:
            voices = []
            speaker = win32com.client.Dispatch("SAPI.SpVoice")

            for voice in speaker.GetVoices():
                voices.append({
                    "id": voice.Id,
                    "description": voice.GetDescription(),
                })

            return voices
        except Exception:
            return []
        finally:
            pythoncom.CoUninitialize()

    def cleanup(self) -> None:
        """Clean up SAPI resources."""
        self.stop_listening()

        self._grammar = None
        self._dictation_grammar = None
        self._context = None
        self._recognizer = None


class WindowsDictationGrammar:
    """
    Helper class for building SAPI dictation grammars.

    Supports creating custom command grammars that integrate
    with Windows Speech Recognition.
    """

    def __init__(self):
        """Initialize the grammar builder."""
        self.commands: Dict[str, List[str]] = {}
        self.semantic_mappings: Dict[str, str] = {}

    def add_command(
        self,
        name: str,
        phrases: List[str],
        semantic_value: Optional[str] = None,
    ) -> "WindowsDictationGrammar":
        """
        Add a command to the grammar.

        Args:
            name: Command name/identifier.
            phrases: List of phrases that trigger this command.
            semantic_value: Optional semantic value for the command.

        Returns:
            Self for chaining.
        """
        self.commands[name] = phrases
        if semantic_value:
            self.semantic_mappings[name] = semantic_value
        return self

    def add_mouse_commands(self) -> "WindowsDictationGrammar":
        """Add standard mouse control commands."""
        self.add_command("click", [
            "click", "tap", "select", "press", "click here",
            "left click", "single click"
        ])
        self.add_command("double_click", [
            "double click", "double tap", "click twice",
            "double press"
        ])
        self.add_command("right_click", [
            "right click", "right tap", "context menu",
            "secondary click", "show menu"
        ])
        self.add_command("middle_click", [
            "middle click", "middle tap", "wheel click"
        ])
        self.add_command("scroll_up", [
            "scroll up", "page up", "scroll upward"
        ])
        self.add_command("scroll_down", [
            "scroll down", "page down", "scroll downward"
        ])
        self.add_command("move_up", [
            "move up", "cursor up", "go up", "up"
        ])
        self.add_command("move_down", [
            "move down", "cursor down", "go down", "down"
        ])
        self.add_command("move_left", [
            "move left", "cursor left", "go left", "left"
        ])
        self.add_command("move_right", [
            "move right", "cursor right", "go right", "right"
        ])
        return self

    def add_keyboard_commands(self) -> "WindowsDictationGrammar":
        """Add standard keyboard control commands."""
        self.add_command("press_enter", [
            "press enter", "enter", "return", "submit"
        ])
        self.add_command("press_tab", [
            "press tab", "tab", "next field"
        ])
        self.add_command("press_escape", [
            "press escape", "escape", "cancel", "close"
        ])
        self.add_command("press_backspace", [
            "backspace", "delete back", "erase"
        ])
        self.add_command("press_delete", [
            "delete", "delete forward", "remove"
        ])
        self.add_command("copy", [
            "copy", "copy that", "copy selection"
        ])
        self.add_command("paste", [
            "paste", "paste that", "paste here"
        ])
        self.add_command("cut", [
            "cut", "cut that", "cut selection"
        ])
        self.add_command("undo", [
            "undo", "undo that", "reverse"
        ])
        self.add_command("redo", [
            "redo", "redo that", "repeat"
        ])
        self.add_command("select_all", [
            "select all", "select everything"
        ])
        return self

    def add_system_commands(self) -> "WindowsDictationGrammar":
        """Add system control commands."""
        self.add_command("screenshot", [
            "screenshot", "take screenshot", "capture screen",
            "screen capture", "print screen"
        ])
        self.add_command("stop", [
            "stop", "stop listening", "pause", "halt"
        ])
        self.add_command("help", [
            "help", "show help", "what can I say"
        ])
        self.add_command("start_dictation", [
            "start dictation", "begin dictation", "dictate"
        ])
        self.add_command("stop_dictation", [
            "stop dictation", "end dictation"
        ])
        return self

    def build_default(self) -> "WindowsDictationGrammar":
        """Build grammar with all default commands."""
        return (
            self.add_mouse_commands()
            .add_keyboard_commands()
            .add_system_commands()
        )

    def get_commands(self) -> Dict[str, List[str]]:
        """Get all registered commands."""
        return self.commands.copy()

    def to_xml_grammar(self) -> str:
        """
        Export grammar as SRGS XML format.

        Returns:
            SRGS XML grammar string.
        """
        xml_parts = [
            '<?xml version="1.0" encoding="utf-8"?>',
            '<grammar version="1.0" xml:lang="en-US" root="commands"',
            '  xmlns="http://www.w3.org/2001/06/grammar"',
            '  xmlns:sapi="http://schemas.microsoft.com/Speech/2002/06/SRGSExtensions">',
            '  <rule id="commands" scope="public">',
            '    <one-of>',
        ]

        for name, phrases in self.commands.items():
            semantic = self.semantic_mappings.get(name, name)
            for phrase in phrases:
                xml_parts.append(
                    f'      <item>{phrase}<tag>out="{semantic}";</tag></item>'
                )

        xml_parts.extend([
            '    </one-of>',
            '  </rule>',
            '</grammar>',
        ])

        return '\n'.join(xml_parts)
