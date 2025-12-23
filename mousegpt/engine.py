"""Main MouseGPT engine that orchestrates all components."""

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from mousegpt.config.settings import Settings, get_settings
from mousegpt.speech.recognizer import SpeechRecognizer, RecognitionResult
from mousegpt.speech.tts import TextToSpeech
from mousegpt.commands.parser import CommandParser, ParseResult, ActionType, ParsedAction
from mousegpt.commands.registry import CommandRegistry, get_registry
from mousegpt.controllers.mouse import MouseController
from mousegpt.controllers.keyboard import KeyboardController
from mousegpt.controllers.screen import ScreenController


class EngineState(str, Enum):
    """State of the MouseGPT engine."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    LISTENING = "listening"
    PROCESSING = "processing"
    EXECUTING = "executing"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class ExecutionResult:
    """Result of executing a command."""
    success: bool
    action_type: ActionType
    message: str = ""
    data: Any = None
    error: Optional[str] = None


@dataclass
class EngineStats:
    """Statistics for the engine."""
    commands_executed: int = 0
    commands_failed: int = 0
    total_runtime: float = 0.0
    last_command: Optional[str] = None
    last_command_time: Optional[float] = None


class MouseGPTEngine:
    """
    Main orchestration engine for MouseGPT.

    Combines speech recognition, command parsing, and input controllers
    to provide voice-controlled computer automation.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        registry: Optional[CommandRegistry] = None,
    ):
        """Initialize the MouseGPT engine."""
        self.settings = settings or get_settings()
        self.registry = registry or get_registry()

        # Setup logging
        self._setup_logging()

        # State
        self.state = EngineState.STOPPED
        self.stats = EngineStats()
        self._start_time: Optional[float] = None
        self._stop_event = threading.Event()

        # Components (initialized lazily)
        self._speech_recognizer: Optional[SpeechRecognizer] = None
        self._tts: Optional[TextToSpeech] = None
        self._command_parser: Optional[CommandParser] = None
        self._mouse: Optional[MouseController] = None
        self._keyboard: Optional[KeyboardController] = None
        self._screen: Optional[ScreenController] = None

        # Callbacks
        self._on_command_callbacks: list[Callable[[str], None]] = []
        self._on_action_callbacks: list[Callable[[ExecutionResult], None]] = []
        self._on_error_callbacks: list[Callable[[str], None]] = []
        self._on_state_change_callbacks: list[Callable[[EngineState], None]] = []

        # Register default commands
        self._register_default_commands()

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        level = logging.DEBUG if self.settings.debug else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger("MouseGPT")

    @property
    def speech_recognizer(self) -> SpeechRecognizer:
        """Get or create speech recognizer."""
        if self._speech_recognizer is None:
            self._speech_recognizer = SpeechRecognizer(self.settings)
        return self._speech_recognizer

    @property
    def tts(self) -> TextToSpeech:
        """Get or create text-to-speech engine."""
        if self._tts is None:
            self._tts = TextToSpeech(self.settings)
        return self._tts

    @property
    def command_parser(self) -> CommandParser:
        """Get or create command parser."""
        if self._command_parser is None:
            self._command_parser = CommandParser(self.settings, self.registry)
        return self._command_parser

    @property
    def mouse(self) -> MouseController:
        """Get or create mouse controller."""
        if self._mouse is None:
            self._mouse = MouseController(self.settings)
        return self._mouse

    @property
    def keyboard(self) -> KeyboardController:
        """Get or create keyboard controller."""
        if self._keyboard is None:
            self._keyboard = KeyboardController(self.settings)
        return self._keyboard

    @property
    def screen(self) -> ScreenController:
        """Get or create screen controller."""
        if self._screen is None:
            self._screen = ScreenController(self.settings)
        return self._screen

    def _set_state(self, state: EngineState) -> None:
        """Update engine state and notify callbacks."""
        self.state = state
        for callback in self._on_state_change_callbacks:
            try:
                callback(state)
            except Exception as e:
                self.logger.error(f"State change callback error: {e}")

    def start(self) -> None:
        """Start the engine and begin listening for commands."""
        if self.state != EngineState.STOPPED:
            raise RuntimeError(f"Cannot start engine in state: {self.state}")

        self._set_state(EngineState.STARTING)
        self._start_time = time.time()
        self._stop_event.clear()

        self.logger.info("Starting MouseGPT engine...")

        # Calibrate speech recognizer
        try:
            self.logger.info("Calibrating for ambient noise...")
            self.speech_recognizer.calibrate()
        except Exception as e:
            self.logger.warning(f"Calibration warning: {e}")

        self._set_state(EngineState.RUNNING)
        self.tts.ready()

        self.logger.info("MouseGPT engine started successfully")

    def stop(self) -> None:
        """Stop the engine."""
        if self.state == EngineState.STOPPED:
            return

        self.logger.info("Stopping MouseGPT engine...")
        self._stop_event.set()

        # Stop speech recognizer
        if self._speech_recognizer:
            self._speech_recognizer.stop_continuous_listening()

        # Stop TTS
        if self._tts:
            self._tts.stop()

        # Update stats
        if self._start_time:
            self.stats.total_runtime += time.time() - self._start_time

        self._set_state(EngineState.STOPPED)
        self.logger.info("MouseGPT engine stopped")

    def pause(self) -> None:
        """Pause command listening."""
        if self.state == EngineState.RUNNING or self.state == EngineState.LISTENING:
            self._set_state(EngineState.PAUSED)
            self.tts.speak("Paused")
            self.logger.info("Engine paused")

    def resume(self) -> None:
        """Resume command listening."""
        if self.state == EngineState.PAUSED:
            self._set_state(EngineState.RUNNING)
            self.tts.speak("Resumed")
            self.logger.info("Engine resumed")

    def listen_once(self) -> Optional[ExecutionResult]:
        """
        Listen for a single command and execute it.

        Returns:
            ExecutionResult or None if no command recognized.
        """
        if self.state == EngineState.PAUSED:
            return None

        self._set_state(EngineState.LISTENING)

        try:
            # Listen for speech
            result = self.speech_recognizer.listen_once()

            if result is None:
                self._set_state(EngineState.RUNNING)
                return None

            # Process the command
            return self.process_command(result.text)

        except Exception as e:
            self.logger.error(f"Listen error: {e}")
            self._set_state(EngineState.ERROR)
            for callback in self._on_error_callbacks:
                callback(str(e))
            return ExecutionResult(
                success=False,
                action_type=ActionType.UNKNOWN,
                error=str(e),
            )

    def listen_continuous(self) -> None:
        """Listen continuously for commands."""
        self.logger.info("Starting continuous listening...")

        def on_recognition(result: RecognitionResult):
            # Check for wake word if enabled
            if self.settings.wake_word_enabled:
                if not self.speech_recognizer.check_wake_word(result.text):
                    return
                command_text = self.speech_recognizer.extract_command_after_wake_word(result.text)
            else:
                command_text = result.text

            if command_text:
                self.process_command(command_text)

        self.speech_recognizer.start_continuous_listening(on_recognition)

    def process_command(self, text: str) -> ExecutionResult:
        """
        Process a text command.

        Args:
            text: The command text to process.

        Returns:
            ExecutionResult with execution outcome.
        """
        self.logger.info(f"Processing command: {text}")
        self._set_state(EngineState.PROCESSING)

        # Notify callbacks
        for callback in self._on_command_callbacks:
            try:
                callback(text)
            except Exception as e:
                self.logger.error(f"Command callback error: {e}")

        # Parse the command
        parse_result = self.command_parser.parse(text)

        if not parse_result.success:
            self.logger.warning(f"Failed to parse command: {parse_result.error}")
            self.tts.speak("Sorry, I didn't understand that command")
            self._set_state(EngineState.RUNNING)
            return ExecutionResult(
                success=False,
                action_type=ActionType.UNKNOWN,
                error=parse_result.error,
            )

        # Execute all actions
        results = []
        for action in parse_result.actions:
            result = self.execute_action(action)
            results.append(result)

            # Notify callbacks
            for callback in self._on_action_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    self.logger.error(f"Action callback error: {e}")

            if not result.success:
                break

        # Update stats
        self.stats.last_command = text
        self.stats.last_command_time = time.time()

        if all(r.success for r in results):
            self.stats.commands_executed += 1
            self._set_state(EngineState.RUNNING)
            return ExecutionResult(
                success=True,
                action_type=results[-1].action_type if results else ActionType.UNKNOWN,
                message="Command executed successfully",
            )
        else:
            self.stats.commands_failed += 1
            self._set_state(EngineState.RUNNING)
            failed = next((r for r in results if not r.success), results[-1])
            return failed

    def execute_action(self, action: ParsedAction) -> ExecutionResult:
        """
        Execute a single parsed action.

        Args:
            action: The action to execute.

        Returns:
            ExecutionResult with outcome.
        """
        self._set_state(EngineState.EXECUTING)
        self.logger.debug(f"Executing action: {action.action_type} with params: {action.parameters}")

        try:
            # Route to appropriate handler
            handlers = {
                ActionType.CLICK: self._execute_click,
                ActionType.DOUBLE_CLICK: self._execute_double_click,
                ActionType.RIGHT_CLICK: self._execute_right_click,
                ActionType.MIDDLE_CLICK: self._execute_middle_click,
                ActionType.MOUSE_MOVE: self._execute_mouse_move,
                ActionType.MOUSE_DRAG: self._execute_mouse_drag,
                ActionType.SCROLL: self._execute_scroll,
                ActionType.TYPE_TEXT: self._execute_type_text,
                ActionType.PRESS_KEY: self._execute_press_key,
                ActionType.HOTKEY: self._execute_hotkey,
                ActionType.SCREENSHOT: self._execute_screenshot,
                ActionType.OPEN_APP: self._execute_open_app,
                ActionType.CLOSE_APP: self._execute_close_app,
                ActionType.SWITCH_APP: self._execute_switch_app,
                ActionType.OPEN_FOLDER: self._execute_open_folder,
                ActionType.SEARCH_WEB: self._execute_search_web,
                # Context-aware actions
                ActionType.CLOSE_CURRENT: self._execute_close_current,
                ActionType.MINIMIZE_CURRENT: self._execute_minimize_current,
                ActionType.MAXIMIZE_CURRENT: self._execute_maximize_current,
                ActionType.SWITCH_WINDOW: self._execute_switch_window,
                ActionType.GO_BACK: self._execute_go_back,
                ActionType.GO_FORWARD: self._execute_go_forward,
                ActionType.REFRESH: self._execute_refresh,
                ActionType.NEW_TAB: self._execute_new_tab,
                ActionType.CLOSE_TAB: self._execute_close_tab,
                ActionType.STOP: self._execute_stop,
                ActionType.HELP: self._execute_help,
            }

            handler = handlers.get(action.action_type)
            if handler:
                return handler(action.parameters)
            else:
                return ExecutionResult(
                    success=False,
                    action_type=action.action_type,
                    error=f"Unknown action type: {action.action_type}",
                )

        except Exception as e:
            self.logger.error(f"Action execution error: {e}")
            return ExecutionResult(
                success=False,
                action_type=action.action_type,
                error=str(e),
            )

    # Action handlers

    def _execute_click(self, params: dict) -> ExecutionResult:
        """Execute click action."""
        x = params.get('x')
        y = params.get('y')
        count = params.get('count', 1)

        if x is not None and y is not None:
            self.mouse.move_to(x, y)

        self.mouse.click(clicks=count)
        self.tts.acknowledged()

        return ExecutionResult(
            success=True,
            action_type=ActionType.CLICK,
            message=f"Clicked at ({x}, {y})" if x else "Clicked",
        )

    def _execute_double_click(self, params: dict) -> ExecutionResult:
        """Execute double click action."""
        x = params.get('x')
        y = params.get('y')

        if x is not None and y is not None:
            self.mouse.move_to(x, y)

        self.mouse.double_click()
        self.tts.acknowledged()

        return ExecutionResult(
            success=True,
            action_type=ActionType.DOUBLE_CLICK,
            message="Double clicked",
        )

    def _execute_right_click(self, params: dict) -> ExecutionResult:
        """Execute right click action."""
        x = params.get('x')
        y = params.get('y')

        if x is not None and y is not None:
            self.mouse.move_to(x, y)

        self.mouse.right_click()
        self.tts.acknowledged()

        return ExecutionResult(
            success=True,
            action_type=ActionType.RIGHT_CLICK,
            message="Right clicked",
        )

    def _execute_middle_click(self, params: dict) -> ExecutionResult:
        """Execute middle click action."""
        x = params.get('x')
        y = params.get('y')

        if x is not None and y is not None:
            self.mouse.move_to(x, y)

        self.mouse.middle_click()
        self.tts.acknowledged()

        return ExecutionResult(
            success=True,
            action_type=ActionType.MIDDLE_CLICK,
            message="Middle clicked",
        )

    def _execute_mouse_move(self, params: dict) -> ExecutionResult:
        """Execute mouse move action."""
        x = params.get('x')
        y = params.get('y')
        direction = params.get('direction')
        distance = params.get('distance', 100)
        relative_x = params.get('relative_x')
        relative_y = params.get('relative_y')

        if x is not None and y is not None:
            self.mouse.move_to(x, y)
            message = f"Moved to ({x}, {y})"
        elif relative_x is not None and relative_y is not None:
            self.mouse.move_to_relative_position(relative_x, relative_y)
            message = f"Moved to relative position"
        elif direction:
            self.mouse.move_direction(direction, distance)
            message = f"Moved {direction} {distance} pixels"
        else:
            return ExecutionResult(
                success=False,
                action_type=ActionType.MOUSE_MOVE,
                error="No position specified",
            )

        return ExecutionResult(
            success=True,
            action_type=ActionType.MOUSE_MOVE,
            message=message,
        )

    def _execute_mouse_drag(self, params: dict) -> ExecutionResult:
        """Execute mouse drag action."""
        x = params.get('x')
        y = params.get('y')

        if x is not None and y is not None:
            self.mouse.drag_to(x, y)
            return ExecutionResult(
                success=True,
                action_type=ActionType.MOUSE_DRAG,
                message=f"Dragged to ({x}, {y})",
            )

        return ExecutionResult(
            success=False,
            action_type=ActionType.MOUSE_DRAG,
            error="No destination specified",
        )

    def _execute_scroll(self, params: dict) -> ExecutionResult:
        """Execute scroll action."""
        direction = params.get('direction', 'down')
        amount = params.get('amount', 3)

        self.mouse.scroll_direction(direction, amount)

        return ExecutionResult(
            success=True,
            action_type=ActionType.SCROLL,
            message=f"Scrolled {direction} {amount} units",
        )

    def _execute_type_text(self, params: dict) -> ExecutionResult:
        """Execute type text action."""
        text = params.get('text', '')

        if not text:
            return ExecutionResult(
                success=False,
                action_type=ActionType.TYPE_TEXT,
                error="No text to type",
            )

        self.keyboard.type_text(text)

        return ExecutionResult(
            success=True,
            action_type=ActionType.TYPE_TEXT,
            message=f"Typed: {text[:50]}..." if len(text) > 50 else f"Typed: {text}",
        )

    def _execute_press_key(self, params: dict) -> ExecutionResult:
        """Execute press key action."""
        key = params.get('key')
        count = params.get('count', 1)

        if not key:
            return ExecutionResult(
                success=False,
                action_type=ActionType.PRESS_KEY,
                error="No key specified",
            )

        self.keyboard.press(key, presses=count)

        return ExecutionResult(
            success=True,
            action_type=ActionType.PRESS_KEY,
            message=f"Pressed {key}" + (f" {count} times" if count > 1 else ""),
        )

    def _execute_hotkey(self, params: dict) -> ExecutionResult:
        """Execute hotkey action."""
        keys = params.get('keys', [])

        if not keys:
            return ExecutionResult(
                success=False,
                action_type=ActionType.HOTKEY,
                error="No keys specified",
            )

        self.keyboard.hotkey(*keys)

        return ExecutionResult(
            success=True,
            action_type=ActionType.HOTKEY,
            message=f"Pressed {'+'.join(keys)}",
        )

    def _execute_screenshot(self, params: dict) -> ExecutionResult:
        """Execute screenshot action."""
        filepath = self.screen.screenshot_to_file()

        return ExecutionResult(
            success=True,
            action_type=ActionType.SCREENSHOT,
            message=f"Screenshot saved to {filepath}",
            data={'path': str(filepath)},
        )

    def _execute_open_app(self, params: dict) -> ExecutionResult:
        """Execute open application action."""
        import subprocess
        import platform

        app_name = params.get('app_name', '')
        executable = params.get('executable')
        display_name = params.get('app_display_name', app_name)

        if not app_name:
            return ExecutionResult(
                success=False,
                action_type=ActionType.OPEN_APP,
                error="No application specified",
            )

        system = platform.system().lower()

        try:
            # Try smart app opening first
            from mousegpt.commands.smart import SmartCommandProcessor
            processor = SmartCommandProcessor()

            if processor.open_application(app_name):
                self.tts.speak(f"Opening {display_name}")
                return ExecutionResult(
                    success=True,
                    action_type=ActionType.OPEN_APP,
                    message=f"Opened {display_name}",
                )

            # Fallback to direct opening
            if executable:
                if system == 'windows':
                    if executable.endswith(':'):
                        import os
                        os.startfile(executable)
                    else:
                        subprocess.Popen(executable, shell=True)
                elif system == 'darwin':
                    subprocess.Popen(['open', '-a', display_name])
                else:
                    subprocess.Popen([executable])
            else:
                if system == 'darwin':
                    subprocess.Popen(['open', '-a', app_name])
                elif system == 'windows':
                    subprocess.Popen(['start', '', app_name], shell=True)
                else:
                    subprocess.Popen([app_name])

            self.tts.speak(f"Opening {display_name}")

            return ExecutionResult(
                success=True,
                action_type=ActionType.OPEN_APP,
                message=f"Opened {display_name}",
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                action_type=ActionType.OPEN_APP,
                error=f"Failed to open {display_name}: {e}",
            )

    def _execute_close_app(self, params: dict) -> ExecutionResult:
        """Execute close application action."""
        app_name = params.get('app_name', '')

        if not app_name:
            # Close current window
            self.keyboard.close_window()
            return ExecutionResult(
                success=True,
                action_type=ActionType.CLOSE_APP,
                message="Closed current window",
            )

        # Try to find and close the window
        if self.screen.activate_window(app_name):
            self.keyboard.close_window()
            return ExecutionResult(
                success=True,
                action_type=ActionType.CLOSE_APP,
                message=f"Closed {app_name}",
            )

        return ExecutionResult(
            success=False,
            action_type=ActionType.CLOSE_APP,
            error=f"Could not find window: {app_name}",
        )

    def _execute_switch_app(self, params: dict) -> ExecutionResult:
        """Execute switch application action."""
        app_name = params.get('app_name', '')

        if not app_name:
            self.keyboard.switch_app()
            return ExecutionResult(
                success=True,
                action_type=ActionType.SWITCH_APP,
                message="Switched application",
            )

        if self.screen.activate_window(app_name):
            return ExecutionResult(
                success=True,
                action_type=ActionType.SWITCH_APP,
                message=f"Switched to {app_name}",
            )

        return ExecutionResult(
            success=False,
            action_type=ActionType.SWITCH_APP,
            error=f"Could not find window: {app_name}",
        )

    def _execute_stop(self, params: dict) -> ExecutionResult:
        """Execute stop action."""
        self.pause()
        return ExecutionResult(
            success=True,
            action_type=ActionType.STOP,
            message="Stopped",
        )

    def _execute_help(self, params: dict) -> ExecutionResult:
        """Execute help action."""
        help_text = """
Available commands:
- Click, double click, right click
- Move mouse to [position/direction]
- Scroll up/down
- Type [text]
- Press [key]
- Open/close/switch to [application]
- Go to [folder] (documents, downloads, desktop)
- Search for [query]
- Close this / minimize this / maximize this
- Go back / go forward / refresh
- New tab / close tab
- Screenshot
- Stop/pause
- Help
"""
        self.tts.speak("Here are some commands you can use")
        return ExecutionResult(
            success=True,
            action_type=ActionType.HELP,
            message=help_text,
            data={'help_text': help_text},
        )

    def _execute_open_folder(self, params: dict) -> ExecutionResult:
        """Execute open folder action."""
        import os

        path = params.get('path', '')

        if not path:
            return ExecutionResult(
                success=False,
                action_type=ActionType.OPEN_FOLDER,
                error="No folder specified",
            )

        try:
            path = os.path.expanduser(path)
            from mousegpt.commands.smart import SmartCommandProcessor
            processor = SmartCommandProcessor()
            processor.open_folder(path)

            self.tts.speak(f"Opening folder")
            return ExecutionResult(
                success=True,
                action_type=ActionType.OPEN_FOLDER,
                message=f"Opened {path}",
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                action_type=ActionType.OPEN_FOLDER,
                error=f"Failed to open folder: {e}",
            )

    def _execute_search_web(self, params: dict) -> ExecutionResult:
        """Execute web search action."""
        query = params.get('query', '')

        if not query:
            return ExecutionResult(
                success=False,
                action_type=ActionType.SEARCH_WEB,
                error="No search query specified",
            )

        try:
            from mousegpt.commands.smart import SmartCommandProcessor
            processor = SmartCommandProcessor()
            processor.search_web(query)

            self.tts.speak(f"Searching for {query}")
            return ExecutionResult(
                success=True,
                action_type=ActionType.SEARCH_WEB,
                message=f"Searched for: {query}",
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                action_type=ActionType.SEARCH_WEB,
                error=f"Failed to search: {e}",
            )

    def _execute_close_current(self, params: dict) -> ExecutionResult:
        """Execute close current window action."""
        self.keyboard.close_window()
        return ExecutionResult(
            success=True,
            action_type=ActionType.CLOSE_CURRENT,
            message="Closed current window",
        )

    def _execute_minimize_current(self, params: dict) -> ExecutionResult:
        """Execute minimize current window action."""
        self.keyboard.hotkey('win', 'down')  # Windows minimize
        return ExecutionResult(
            success=True,
            action_type=ActionType.MINIMIZE_CURRENT,
            message="Minimized current window",
        )

    def _execute_maximize_current(self, params: dict) -> ExecutionResult:
        """Execute maximize current window action."""
        self.keyboard.hotkey('win', 'up')  # Windows maximize
        return ExecutionResult(
            success=True,
            action_type=ActionType.MAXIMIZE_CURRENT,
            message="Maximized current window",
        )

    def _execute_switch_window(self, params: dict) -> ExecutionResult:
        """Execute switch window action."""
        self.keyboard.switch_app()
        return ExecutionResult(
            success=True,
            action_type=ActionType.SWITCH_WINDOW,
            message="Switched window",
        )

    def _execute_go_back(self, params: dict) -> ExecutionResult:
        """Execute go back action."""
        self.keyboard.hotkey('alt', 'left')
        return ExecutionResult(
            success=True,
            action_type=ActionType.GO_BACK,
            message="Went back",
        )

    def _execute_go_forward(self, params: dict) -> ExecutionResult:
        """Execute go forward action."""
        self.keyboard.hotkey('alt', 'right')
        return ExecutionResult(
            success=True,
            action_type=ActionType.GO_FORWARD,
            message="Went forward",
        )

    def _execute_refresh(self, params: dict) -> ExecutionResult:
        """Execute refresh action."""
        self.keyboard.press('f5')
        return ExecutionResult(
            success=True,
            action_type=ActionType.REFRESH,
            message="Refreshed",
        )

    def _execute_new_tab(self, params: dict) -> ExecutionResult:
        """Execute new tab action."""
        self.keyboard.new_tab()
        return ExecutionResult(
            success=True,
            action_type=ActionType.NEW_TAB,
            message="Opened new tab",
        )

    def _execute_close_tab(self, params: dict) -> ExecutionResult:
        """Execute close tab action."""
        self.keyboard.close_tab()
        return ExecutionResult(
            success=True,
            action_type=ActionType.CLOSE_TAB,
            message="Closed tab",
        )

    def _register_default_commands(self) -> None:
        """Register default built-in commands."""
        # Commands can be registered here or via the registry decorator
        pass

    # Callback registration

    def on_command(self, callback: Callable[[str], None]) -> None:
        """Register a callback for when commands are received."""
        self._on_command_callbacks.append(callback)

    def on_action(self, callback: Callable[[ExecutionResult], None]) -> None:
        """Register a callback for when actions are executed."""
        self._on_action_callbacks.append(callback)

    def on_error(self, callback: Callable[[str], None]) -> None:
        """Register a callback for errors."""
        self._on_error_callbacks.append(callback)

    def on_state_change(self, callback: Callable[[EngineState], None]) -> None:
        """Register a callback for state changes."""
        self._on_state_change_callbacks.append(callback)

    # Utility methods

    def get_stats(self) -> dict:
        """Get engine statistics."""
        return {
            'commands_executed': self.stats.commands_executed,
            'commands_failed': self.stats.commands_failed,
            'total_runtime': self.stats.total_runtime,
            'last_command': self.stats.last_command,
            'last_command_time': self.stats.last_command_time,
            'state': self.state.value,
        }
