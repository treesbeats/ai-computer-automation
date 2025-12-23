"""Command parser for MouseGPT."""

import json
import re
from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum

from mousegpt.config.settings import Settings, AIBackend, get_settings
from mousegpt.commands.registry import CommandRegistry, get_registry, CommandCategory
from mousegpt.utils.helpers import (
    normalize_text,
    parse_coordinates,
    parse_direction,
    parse_number,
    parse_key_name,
)


class ActionType(str, Enum):
    """Types of actions that can be performed."""
    # Mouse actions
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    MIDDLE_CLICK = "middle_click"
    MOUSE_MOVE = "mouse_move"
    MOUSE_DRAG = "mouse_drag"
    SCROLL = "scroll"

    # Keyboard actions
    TYPE_TEXT = "type_text"
    PRESS_KEY = "press_key"
    HOTKEY = "hotkey"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"

    # Screen actions
    SCREENSHOT = "screenshot"
    FIND_ELEMENT = "find_element"

    # System actions
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    SWITCH_APP = "switch_app"
    OPEN_FOLDER = "open_folder"
    SEARCH_WEB = "search_web"

    # Context-aware actions
    CLOSE_CURRENT = "close_current"
    MINIMIZE_CURRENT = "minimize_current"
    MAXIMIZE_CURRENT = "maximize_current"
    SWITCH_WINDOW = "switch_window"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    REFRESH = "refresh"
    NEW_TAB = "new_tab"
    CLOSE_TAB = "close_tab"

    # Control actions
    STOP = "stop"
    CANCEL = "cancel"
    UNDO = "undo"
    REPEAT = "repeat"
    HELP = "help"

    # Compound actions
    SEQUENCE = "sequence"
    UNKNOWN = "unknown"


@dataclass
class ParsedAction:
    """A parsed action from a voice command."""
    action_type: ActionType
    parameters: dict[str, Any]
    raw_text: str
    confidence: float = 1.0


@dataclass
class ParseResult:
    """Result of parsing a command."""
    success: bool
    actions: list[ParsedAction]
    error: Optional[str] = None
    raw_text: str = ""


class CommandParser:
    """
    Parser for natural language voice commands.

    Converts spoken commands into structured actions that can be executed.
    Supports both rule-based parsing and AI-powered parsing.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        registry: Optional[CommandRegistry] = None,
    ):
        """Initialize the command parser."""
        self.settings = settings or get_settings()
        self.registry = registry or get_registry()
        self._openai_client = None
        self._smart_processor = None

    @property
    def smart_processor(self):
        """Get the smart command processor."""
        if self._smart_processor is None:
            from mousegpt.commands.smart import SmartCommandProcessor
            self._smart_processor = SmartCommandProcessor()
        return self._smart_processor

    def parse(self, text: str) -> ParseResult:
        """
        Parse a text command into actions.

        Args:
            text: The text command to parse.

        Returns:
            ParseResult with parsed actions.
        """
        text = normalize_text(text)

        if not text:
            return ParseResult(
                success=False,
                actions=[],
                error="Empty command",
                raw_text=text,
            )

        # First try rule-based parsing
        result = self._parse_rule_based(text)

        # If rule-based fails, try smart parsing
        if not result.success:
            result = self._parse_smart(text)

        # If smart parsing fails and AI is enabled, try AI parsing
        if not result.success and self.settings.ai_backend == AIBackend.OPENAI:
            result = self._parse_with_ai(text)

        return result

    def _parse_rule_based(self, text: str) -> ParseResult:
        """Parse using rule-based pattern matching."""
        actions = []

        # Check registry first
        match = self.registry.find_match(text)
        if match:
            command, params = match
            action = ParsedAction(
                action_type=self._get_action_type_for_command(command.name),
                parameters=params,
                raw_text=text,
            )
            return ParseResult(success=True, actions=[action], raw_text=text)

        # Try built-in patterns
        action = self._match_builtin_patterns(text)
        if action:
            return ParseResult(success=True, actions=[action], raw_text=text)

        return ParseResult(
            success=False,
            actions=[],
            error="Could not understand command",
            raw_text=text,
        )

    def _parse_smart(self, text: str) -> ParseResult:
        """Parse using smart natural language understanding."""
        from mousegpt.commands.smart import (
            understand_command,
            find_context_action,
            APP_ALIASES,
        )

        result = understand_command(text)

        if not result["understood"]:
            return ParseResult(
                success=False,
                actions=[],
                error="Could not understand command",
                raw_text=text,
            )

        action = result["action"]
        target = result["target"]
        params = result.get("params", {})

        # Map smart actions to ActionTypes
        action_mapping = {
            # Context-aware actions
            "close_current": ActionType.CLOSE_CURRENT,
            "minimize_current": ActionType.MINIMIZE_CURRENT,
            "maximize_current": ActionType.MAXIMIZE_CURRENT,
            "switch_window": ActionType.SWITCH_WINDOW,
            "go_back": ActionType.GO_BACK,
            "go_forward": ActionType.GO_FORWARD,
            "refresh": ActionType.REFRESH,
            "new_tab": ActionType.NEW_TAB,
            "close_tab": ActionType.CLOSE_TAB,
            "search": ActionType.SEARCH_WEB,

            # Standard actions
            "open": ActionType.OPEN_APP,
            "close": ActionType.CLOSE_APP,
            "switch": ActionType.SWITCH_APP,
            "click": ActionType.CLICK,
            "type": ActionType.TYPE_TEXT,
            "scroll": ActionType.SCROLL,
        }

        # Handle folder navigation
        if params.get("is_folder"):
            parsed_action = ParsedAction(
                action_type=ActionType.OPEN_FOLDER,
                parameters={"path": target},
                raw_text=text,
                confidence=result["confidence"],
            )
            return ParseResult(success=True, actions=[parsed_action], raw_text=text)

        # Handle search
        if action == "search":
            # Extract search query
            text_lower = text.lower()
            for prefix in ["search for", "look up", "google", "search the web for", "search"]:
                if prefix in text_lower:
                    query = text_lower.split(prefix, 1)[-1].strip()
                    parsed_action = ParsedAction(
                        action_type=ActionType.SEARCH_WEB,
                        parameters={"query": query},
                        raw_text=text,
                        confidence=0.9,
                    )
                    return ParseResult(success=True, actions=[parsed_action], raw_text=text)

        # Get action type
        action_type = action_mapping.get(action, ActionType.UNKNOWN)

        if action_type == ActionType.UNKNOWN:
            return ParseResult(
                success=False,
                actions=[],
                error=f"Unknown action: {action}",
                raw_text=text,
            )

        # Build parameters
        action_params = {}

        if target:
            # Check if target is an app
            app_info = params.get("app_info")
            if app_info:
                action_params["app_name"] = target
                action_params["app_display_name"] = app_info.name
                if app_info.executable:
                    action_params["executable"] = app_info.executable
                if app_info.windows_name:
                    action_params["window_pattern"] = app_info.windows_name
            else:
                action_params["target"] = target

        parsed_action = ParsedAction(
            action_type=action_type,
            parameters=action_params,
            raw_text=text,
            confidence=result["confidence"],
        )

        return ParseResult(success=True, actions=[parsed_action], raw_text=text)

    def _match_builtin_patterns(self, text: str) -> Optional[ParsedAction]:
        """Match against built-in command patterns."""
        text_lower = text.lower()

        # Stop/Cancel commands
        if any(word in text_lower for word in ['stop', 'cancel', 'abort', 'halt']):
            return ParsedAction(
                action_type=ActionType.STOP,
                parameters={},
                raw_text=text,
            )

        # Help command
        if 'help' in text_lower:
            return ParsedAction(
                action_type=ActionType.HELP,
                parameters={},
                raw_text=text,
            )

        # Click commands
        click_action = self._parse_click_command(text)
        if click_action:
            return click_action

        # Mouse movement commands
        move_action = self._parse_move_command(text)
        if move_action:
            return move_action

        # Scroll commands
        scroll_action = self._parse_scroll_command(text)
        if scroll_action:
            return scroll_action

        # Keyboard commands
        key_action = self._parse_keyboard_command(text)
        if key_action:
            return key_action

        # Type text commands
        type_action = self._parse_type_command(text)
        if type_action:
            return type_action

        # Application commands
        app_action = self._parse_app_command(text)
        if app_action:
            return app_action

        # Screenshot commands
        if any(word in text_lower for word in ['screenshot', 'screen shot', 'capture screen', 'take a picture']):
            return ParsedAction(
                action_type=ActionType.SCREENSHOT,
                parameters={},
                raw_text=text,
            )

        return None

    def _parse_click_command(self, text: str) -> Optional[ParsedAction]:
        """Parse click-related commands."""
        text_lower = text.lower()

        # Determine click type
        if 'double' in text_lower or 'twice' in text_lower:
            action_type = ActionType.DOUBLE_CLICK
        elif 'right' in text_lower:
            action_type = ActionType.RIGHT_CLICK
        elif 'middle' in text_lower:
            action_type = ActionType.MIDDLE_CLICK
        elif any(word in text_lower for word in ['click', 'tap', 'press', 'select']):
            action_type = ActionType.CLICK
        else:
            return None

        params = {}

        # Try to extract coordinates
        coords = parse_coordinates(text)
        if coords:
            params['x'], params['y'] = coords

        # Try to extract target (e.g., "click on the button")
        target_patterns = [
            r'(?:click|tap|press|select)\s+(?:on\s+)?(?:the\s+)?(.+)',
            r'(.+)\s+(?:button|link|icon)',
        ]
        for pattern in target_patterns:
            match = re.search(pattern, text_lower)
            if match:
                params['target'] = match.group(1).strip()
                break

        # Extract click count
        count = parse_number(text)
        if count > 1 and action_type == ActionType.CLICK:
            params['count'] = count

        return ParsedAction(
            action_type=action_type,
            parameters=params,
            raw_text=text,
        )

    def _parse_move_command(self, text: str) -> Optional[ParsedAction]:
        """Parse mouse movement commands."""
        text_lower = text.lower()

        if not any(word in text_lower for word in ['move', 'go to', 'goto', 'position', 'cursor']):
            return None

        params = {}

        # Check for coordinates
        coords = parse_coordinates(text)
        if coords:
            params['x'], params['y'] = coords
            return ParsedAction(
                action_type=ActionType.MOUSE_MOVE,
                parameters=params,
                raw_text=text,
            )

        # Check for direction-based movement
        direction = parse_direction(text)
        if direction:
            params['direction'] = direction
            params['distance'] = parse_number(text, default=100)
            return ParsedAction(
                action_type=ActionType.MOUSE_MOVE,
                parameters=params,
                raw_text=text,
            )

        # Check for relative positions
        position_keywords = {
            'center': (0.5, 0.5),
            'middle': (0.5, 0.5),
            'top left': (0.1, 0.1),
            'top right': (0.9, 0.1),
            'bottom left': (0.1, 0.9),
            'bottom right': (0.9, 0.9),
            'top': (0.5, 0.1),
            'bottom': (0.5, 0.9),
            'left': (0.1, 0.5),
            'right': (0.9, 0.5),
        }
        for keyword, (rel_x, rel_y) in position_keywords.items():
            if keyword in text_lower:
                params['relative_x'] = rel_x
                params['relative_y'] = rel_y
                return ParsedAction(
                    action_type=ActionType.MOUSE_MOVE,
                    parameters=params,
                    raw_text=text,
                )

        return None

    def _parse_scroll_command(self, text: str) -> Optional[ParsedAction]:
        """Parse scroll commands."""
        text_lower = text.lower()

        if not any(word in text_lower for word in ['scroll', 'wheel']):
            return None

        params = {}

        # Determine direction
        direction = parse_direction(text)
        if direction:
            params['direction'] = direction
        elif 'down' in text_lower:
            params['direction'] = 'down'
        else:
            params['direction'] = 'up'

        # Get amount
        params['amount'] = parse_number(text, default=3)

        return ParsedAction(
            action_type=ActionType.SCROLL,
            parameters=params,
            raw_text=text,
        )

    def _parse_keyboard_command(self, text: str) -> Optional[ParsedAction]:
        """Parse keyboard commands."""
        text_lower = text.lower()

        # Hotkey/shortcut patterns
        hotkey_patterns = [
            r'press\s+(?:ctrl|control|command|cmd)\s*[+\s]\s*([a-z])',
            r'(?:ctrl|control|command|cmd)\s*[+\s]\s*([a-z])',
            r'(?:copy|paste|cut|undo|redo|save|select all|find)',
        ]

        # Check for common hotkeys by name
        hotkey_map = {
            'copy': ['ctrl', 'c'],
            'paste': ['ctrl', 'v'],
            'cut': ['ctrl', 'x'],
            'undo': ['ctrl', 'z'],
            'redo': ['ctrl', 'y'],
            'save': ['ctrl', 's'],
            'select all': ['ctrl', 'a'],
            'find': ['ctrl', 'f'],
            'new tab': ['ctrl', 't'],
            'close tab': ['ctrl', 'w'],
            'new window': ['ctrl', 'n'],
        }

        for hotkey_name, keys in hotkey_map.items():
            if hotkey_name in text_lower:
                return ParsedAction(
                    action_type=ActionType.HOTKEY,
                    parameters={'keys': keys},
                    raw_text=text,
                )

        # Check for ctrl+key pattern
        match = re.search(r'(?:ctrl|control|command|cmd)\s*[+\s]\s*([a-z])', text_lower)
        if match:
            return ParsedAction(
                action_type=ActionType.HOTKEY,
                parameters={'keys': ['ctrl', match.group(1)]},
                raw_text=text,
            )

        # Check for alt+key pattern
        match = re.search(r'(?:alt|option)\s*[+\s]\s*([a-z])', text_lower)
        if match:
            return ParsedAction(
                action_type=ActionType.HOTKEY,
                parameters={'keys': ['alt', match.group(1)]},
                raw_text=text,
            )

        # Single key press
        if any(word in text_lower for word in ['press', 'hit', 'tap']):
            key = parse_key_name(text)
            if key:
                return ParsedAction(
                    action_type=ActionType.PRESS_KEY,
                    parameters={'key': key, 'count': parse_number(text, default=1)},
                    raw_text=text,
                )

        return None

    def _parse_type_command(self, text: str) -> Optional[ParsedAction]:
        """Parse text typing commands."""
        text_lower = text.lower()

        type_triggers = ['type', 'write', 'enter text', 'input']

        for trigger in type_triggers:
            if trigger in text_lower:
                # Extract the text to type
                idx = text_lower.find(trigger) + len(trigger)
                content = text[idx:].strip()

                # Remove quotes if present
                if content.startswith('"') and content.endswith('"'):
                    content = content[1:-1]
                elif content.startswith("'") and content.endswith("'"):
                    content = content[1:-1]

                if content:
                    return ParsedAction(
                        action_type=ActionType.TYPE_TEXT,
                        parameters={'text': content},
                        raw_text=text,
                    )

        return None

    def _parse_app_command(self, text: str) -> Optional[ParsedAction]:
        """Parse application control commands."""
        text_lower = text.lower()

        # Open application
        if any(word in text_lower for word in ['open', 'launch', 'start', 'run']):
            # Extract app name
            patterns = [
                r'(?:open|launch|start|run)\s+(?:the\s+)?(.+?)(?:\s+app(?:lication)?)?$',
            ]
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    app_name = match.group(1).strip()
                    return ParsedAction(
                        action_type=ActionType.OPEN_APP,
                        parameters={'app_name': app_name},
                        raw_text=text,
                    )

        # Close application
        if any(word in text_lower for word in ['close', 'quit', 'exit', 'terminate']):
            patterns = [
                r'(?:close|quit|exit|terminate)\s+(?:the\s+)?(.+?)(?:\s+app(?:lication)?)?$',
            ]
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    app_name = match.group(1).strip()
                    return ParsedAction(
                        action_type=ActionType.CLOSE_APP,
                        parameters={'app_name': app_name},
                        raw_text=text,
                    )

        # Switch application
        if any(phrase in text_lower for phrase in ['switch to', 'go to', 'focus']):
            patterns = [
                r'(?:switch to|go to|focus)\s+(?:the\s+)?(.+?)(?:\s+app(?:lication)?)?$',
            ]
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    app_name = match.group(1).strip()
                    return ParsedAction(
                        action_type=ActionType.SWITCH_APP,
                        parameters={'app_name': app_name},
                        raw_text=text,
                    )

        return None

    def _parse_with_ai(self, text: str) -> ParseResult:
        """Parse using AI (OpenAI GPT)."""
        try:
            client = self._get_openai_client()

            system_prompt = """You are a command parser for a voice-controlled computer automation system called MouseGPT.

Your task is to parse natural language commands and output structured JSON actions.

Available action types:
- click: Click at a position or on an element
- double_click: Double click
- right_click: Right click
- mouse_move: Move mouse to position
- scroll: Scroll up/down/left/right
- type_text: Type text using keyboard
- press_key: Press a single key
- hotkey: Press a key combination (e.g., Ctrl+C)
- open_app: Open an application
- close_app: Close an application
- screenshot: Take a screenshot

Output format:
{
    "actions": [
        {
            "type": "action_type",
            "params": {
                "key": "value"
            }
        }
    ]
}

Parameters for each action:
- click/double_click/right_click: x, y (coordinates), or target (element description)
- mouse_move: x, y (coordinates), or direction (up/down/left/right) + distance
- scroll: direction (up/down), amount (number of scroll units)
- type_text: text (the text to type)
- press_key: key (key name like "enter", "tab", "escape")
- hotkey: keys (array of keys like ["ctrl", "c"])
- open_app/close_app: app_name (application name)
"""

            response = client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this command: {text}"},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)

            actions = []
            for action_data in result_json.get("actions", []):
                action_type = ActionType(action_data.get("type", "unknown"))
                params = action_data.get("params", {})
                actions.append(ParsedAction(
                    action_type=action_type,
                    parameters=params,
                    raw_text=text,
                    confidence=0.8,
                ))

            return ParseResult(
                success=len(actions) > 0,
                actions=actions,
                raw_text=text,
            )

        except Exception as e:
            return ParseResult(
                success=False,
                actions=[],
                error=f"AI parsing failed: {e}",
                raw_text=text,
            )

    def _get_openai_client(self):
        """Get or create OpenAI client."""
        if self._openai_client is None:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=self.settings.openai_api_key)
            except ImportError:
                raise ImportError("openai package not installed")
        return self._openai_client

    def _get_action_type_for_command(self, command_name: str) -> ActionType:
        """Map command name to action type."""
        mapping = {
            'click': ActionType.CLICK,
            'double_click': ActionType.DOUBLE_CLICK,
            'right_click': ActionType.RIGHT_CLICK,
            'move': ActionType.MOUSE_MOVE,
            'scroll': ActionType.SCROLL,
            'type': ActionType.TYPE_TEXT,
            'press': ActionType.PRESS_KEY,
            'hotkey': ActionType.HOTKEY,
        }
        return mapping.get(command_name, ActionType.UNKNOWN)
