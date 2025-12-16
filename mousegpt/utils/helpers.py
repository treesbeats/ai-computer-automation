"""Utility functions and helpers for MouseGPT."""

import platform
import re
from typing import Optional, Tuple


def get_platform() -> str:
    """Get the current platform name."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system


def normalize_text(text: str) -> str:
    """Normalize text by converting to lowercase and stripping whitespace."""
    return text.lower().strip()


def parse_coordinates(text: str) -> Optional[Tuple[int, int]]:
    """
    Parse coordinates from text.

    Supports formats:
    - "100, 200" or "100,200"
    - "100 200"
    - "x 100 y 200"
    - "position 100 200"

    Returns:
        Tuple of (x, y) coordinates or None if parsing fails.
    """
    text = normalize_text(text)

    # Try "x 100 y 200" format
    match = re.search(r'x\s*(\d+)\s*y\s*(\d+)', text)
    if match:
        return int(match.group(1)), int(match.group(2))

    # Try "100, 200" or "100,200" format
    match = re.search(r'(\d+)\s*,\s*(\d+)', text)
    if match:
        return int(match.group(1)), int(match.group(2))

    # Try "100 200" format (two numbers separated by space)
    match = re.search(r'(\d+)\s+(\d+)', text)
    if match:
        return int(match.group(1)), int(match.group(2))

    return None


def parse_direction(text: str) -> Optional[str]:
    """
    Parse direction from text.

    Returns:
        One of: 'up', 'down', 'left', 'right', or None.
    """
    text = normalize_text(text)

    direction_map = {
        'up': ['up', 'upward', 'upwards', 'north', 'top'],
        'down': ['down', 'downward', 'downwards', 'south', 'bottom'],
        'left': ['left', 'leftward', 'leftwards', 'west'],
        'right': ['right', 'rightward', 'rightwards', 'east'],
    }

    for direction, aliases in direction_map.items():
        for alias in aliases:
            if alias in text:
                return direction

    return None


def parse_number(text: str, default: int = 1) -> int:
    """
    Parse a number from text, handling both digits and words.

    Returns:
        The parsed number or the default value.
    """
    text = normalize_text(text)

    # Word to number mapping
    word_numbers = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
        'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
        'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
        'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
        'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000,
        'once': 1, 'twice': 2, 'thrice': 3,
        'single': 1, 'double': 2, 'triple': 3,
    }

    # Check for word numbers
    for word, num in word_numbers.items():
        if word in text:
            return num

    # Try to find a digit number
    match = re.search(r'\d+', text)
    if match:
        return int(match.group())

    return default


def parse_key_name(text: str) -> Optional[str]:
    """
    Parse a key name from text for keyboard operations.

    Returns:
        The standardized key name or None.
    """
    text = normalize_text(text)

    # Common key name mappings
    key_map = {
        # Special keys
        'enter': 'enter', 'return': 'enter',
        'space': 'space', 'spacebar': 'space',
        'tab': 'tab',
        'escape': 'escape', 'esc': 'escape',
        'backspace': 'backspace', 'back space': 'backspace',
        'delete': 'delete', 'del': 'delete',
        'insert': 'insert', 'ins': 'insert',
        'home': 'home',
        'end': 'end',
        'page up': 'pageup', 'pageup': 'pageup',
        'page down': 'pagedown', 'pagedown': 'pagedown',

        # Arrow keys
        'up arrow': 'up', 'arrow up': 'up', 'up': 'up',
        'down arrow': 'down', 'arrow down': 'down', 'down': 'down',
        'left arrow': 'left', 'arrow left': 'left', 'left': 'left',
        'right arrow': 'right', 'arrow right': 'right', 'right': 'right',

        # Modifier keys
        'control': 'ctrl', 'ctrl': 'ctrl',
        'alt': 'alt', 'option': 'alt',
        'shift': 'shift',
        'command': 'cmd', 'cmd': 'cmd', 'super': 'cmd', 'windows': 'cmd', 'win': 'cmd',
        'meta': 'cmd',

        # Function keys
        'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
        'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
        'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12',

        # Other
        'caps lock': 'capslock', 'capslock': 'capslock',
        'num lock': 'numlock', 'numlock': 'numlock',
        'print screen': 'printscreen', 'printscreen': 'printscreen',
        'scroll lock': 'scrolllock', 'scrolllock': 'scrolllock',
    }

    for pattern, key in key_map.items():
        if pattern in text:
            return key

    # Single character
    match = re.search(r'\b([a-z0-9])\b', text)
    if match:
        return match.group(1)

    return None


def extract_text_content(text: str, prefix_patterns: list[str]) -> Optional[str]:
    """
    Extract text content after a prefix pattern.

    Args:
        text: The input text to search.
        prefix_patterns: List of prefix patterns to look for.

    Returns:
        The text content after the prefix or None.
    """
    text = normalize_text(text)

    for pattern in prefix_patterns:
        if pattern in text:
            idx = text.find(pattern) + len(pattern)
            result = text[idx:].strip()
            if result:
                return result

    return None
