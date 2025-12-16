"""Keyboard controller for MouseGPT."""

from typing import Optional, List, Union
from enum import Enum

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from pynput import keyboard as pynput_keyboard
except ImportError:
    pynput_keyboard = None

from mousegpt.config.settings import Settings, get_settings
from mousegpt.utils.helpers import get_platform


class ModifierKey(str, Enum):
    """Modifier keys."""
    CTRL = "ctrl"
    ALT = "alt"
    SHIFT = "shift"
    CMD = "cmd"  # Command on macOS, Windows key on Windows


class KeyboardController:
    """
    Controller for keyboard operations.

    Provides methods for:
    - Typing text
    - Pressing keys
    - Key combinations (hotkeys)
    - Holding and releasing keys
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the keyboard controller."""
        if pyautogui is None:
            raise ImportError(
                "pyautogui package not installed. "
                "Install with: pip install pyautogui"
            )

        self.settings = settings or get_settings()
        self._platform = get_platform()

        # Map platform-specific keys
        self._key_map = self._build_key_map()

    def _build_key_map(self) -> dict:
        """Build platform-specific key mappings."""
        # Base mappings work on all platforms
        key_map = {
            'enter': 'enter',
            'return': 'enter',
            'tab': 'tab',
            'space': 'space',
            'backspace': 'backspace',
            'delete': 'delete',
            'escape': 'escape',
            'esc': 'escape',
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
            'home': 'home',
            'end': 'end',
            'pageup': 'pageup',
            'pagedown': 'pagedown',
            'capslock': 'capslock',
            'numlock': 'numlock',
            'scrolllock': 'scrolllock',
            'printscreen': 'printscreen',
            'insert': 'insert',
            'pause': 'pause',
        }

        # Add function keys
        for i in range(1, 13):
            key_map[f'f{i}'] = f'f{i}'

        # Platform-specific modifier mappings
        if self._platform == 'macos':
            key_map.update({
                'ctrl': 'ctrl',
                'control': 'ctrl',
                'alt': 'option',
                'option': 'option',
                'shift': 'shift',
                'cmd': 'command',
                'command': 'command',
                'super': 'command',
                'meta': 'command',
                'win': 'command',
                'windows': 'command',
            })
        else:
            key_map.update({
                'ctrl': 'ctrl',
                'control': 'ctrl',
                'alt': 'alt',
                'option': 'alt',
                'shift': 'shift',
                'cmd': 'win',
                'command': 'win',
                'super': 'win',
                'meta': 'win',
                'win': 'win',
                'windows': 'win',
            })

        return key_map

    def _normalize_key(self, key: str) -> str:
        """Normalize a key name to pyautogui format."""
        key_lower = key.lower().strip()
        return self._key_map.get(key_lower, key_lower)

    def type_text(
        self,
        text: str,
        interval: Optional[float] = None,
    ) -> None:
        """
        Type text using the keyboard.

        Args:
            text: Text to type.
            interval: Delay between keypresses in seconds.
        """
        interval = interval if interval is not None else self.settings.keyboard_typing_speed
        pyautogui.write(text, interval=interval)

    def type_with_clipboard(self, text: str) -> None:
        """
        Type text using clipboard (faster for long text).

        This method copies text to clipboard and pastes it,
        which is faster for long strings but may not work in all contexts.

        Args:
            text: Text to type.
        """
        import pyperclip
        pyperclip.copy(text)

        if self._platform == 'macos':
            self.hotkey('command', 'v')
        else:
            self.hotkey('ctrl', 'v')

    def press(
        self,
        key: str,
        presses: int = 1,
        interval: float = 0.1,
    ) -> None:
        """
        Press a key.

        Args:
            key: Key to press.
            presses: Number of times to press.
            interval: Interval between presses.
        """
        key = self._normalize_key(key)
        pyautogui.press(key, presses=presses, interval=interval)

    def press_enter(self) -> None:
        """Press the Enter key."""
        self.press('enter')

    def press_tab(self) -> None:
        """Press the Tab key."""
        self.press('tab')

    def press_escape(self) -> None:
        """Press the Escape key."""
        self.press('escape')

    def press_backspace(self, times: int = 1) -> None:
        """Press backspace one or more times."""
        self.press('backspace', presses=times)

    def press_delete(self, times: int = 1) -> None:
        """Press delete one or more times."""
        self.press('delete', presses=times)

    def press_space(self) -> None:
        """Press the Space key."""
        self.press('space')

    def press_arrow(self, direction: str, times: int = 1) -> None:
        """
        Press an arrow key.

        Args:
            direction: One of 'up', 'down', 'left', 'right'.
            times: Number of times to press.
        """
        self.press(direction, presses=times)

    def hotkey(self, *keys: str) -> None:
        """
        Press a key combination.

        Args:
            keys: Keys to press together.
        """
        normalized_keys = [self._normalize_key(k) for k in keys]
        pyautogui.hotkey(*normalized_keys)

    def key_down(self, key: str) -> None:
        """
        Press and hold a key.

        Args:
            key: Key to hold.
        """
        key = self._normalize_key(key)
        pyautogui.keyDown(key)

    def key_up(self, key: str) -> None:
        """
        Release a key.

        Args:
            key: Key to release.
        """
        key = self._normalize_key(key)
        pyautogui.keyUp(key)

    # Common keyboard shortcuts

    def copy(self) -> None:
        """Perform copy (Ctrl+C / Cmd+C)."""
        if self._platform == 'macos':
            self.hotkey('command', 'c')
        else:
            self.hotkey('ctrl', 'c')

    def paste(self) -> None:
        """Perform paste (Ctrl+V / Cmd+V)."""
        if self._platform == 'macos':
            self.hotkey('command', 'v')
        else:
            self.hotkey('ctrl', 'v')

    def cut(self) -> None:
        """Perform cut (Ctrl+X / Cmd+X)."""
        if self._platform == 'macos':
            self.hotkey('command', 'x')
        else:
            self.hotkey('ctrl', 'x')

    def undo(self) -> None:
        """Perform undo (Ctrl+Z / Cmd+Z)."""
        if self._platform == 'macos':
            self.hotkey('command', 'z')
        else:
            self.hotkey('ctrl', 'z')

    def redo(self) -> None:
        """Perform redo (Ctrl+Y / Cmd+Shift+Z)."""
        if self._platform == 'macos':
            self.hotkey('command', 'shift', 'z')
        else:
            self.hotkey('ctrl', 'y')

    def select_all(self) -> None:
        """Select all (Ctrl+A / Cmd+A)."""
        if self._platform == 'macos':
            self.hotkey('command', 'a')
        else:
            self.hotkey('ctrl', 'a')

    def save(self) -> None:
        """Save (Ctrl+S / Cmd+S)."""
        if self._platform == 'macos':
            self.hotkey('command', 's')
        else:
            self.hotkey('ctrl', 's')

    def find(self) -> None:
        """Open find dialog (Ctrl+F / Cmd+F)."""
        if self._platform == 'macos':
            self.hotkey('command', 'f')
        else:
            self.hotkey('ctrl', 'f')

    def new_tab(self) -> None:
        """Open new tab (Ctrl+T / Cmd+T)."""
        if self._platform == 'macos':
            self.hotkey('command', 't')
        else:
            self.hotkey('ctrl', 't')

    def close_tab(self) -> None:
        """Close tab (Ctrl+W / Cmd+W)."""
        if self._platform == 'macos':
            self.hotkey('command', 'w')
        else:
            self.hotkey('ctrl', 'w')

    def new_window(self) -> None:
        """Open new window (Ctrl+N / Cmd+N)."""
        if self._platform == 'macos':
            self.hotkey('command', 'n')
        else:
            self.hotkey('ctrl', 'n')

    def close_window(self) -> None:
        """Close window."""
        if self._platform == 'macos':
            self.hotkey('command', 'w')
        else:
            self.hotkey('alt', 'f4')

    def switch_app(self) -> None:
        """Switch application (Alt+Tab / Cmd+Tab)."""
        if self._platform == 'macos':
            self.hotkey('command', 'tab')
        else:
            self.hotkey('alt', 'tab')

    def switch_window(self) -> None:
        """Switch window within app."""
        if self._platform == 'macos':
            self.hotkey('command', '`')
        else:
            self.hotkey('alt', 'escape')

    def screenshot_shortcut(self) -> None:
        """Take screenshot using system shortcut."""
        if self._platform == 'macos':
            self.hotkey('command', 'shift', '3')
        elif self._platform == 'windows':
            self.hotkey('win', 'shift', 's')
        else:
            self.press('printscreen')

    def lock_screen(self) -> None:
        """Lock the screen."""
        if self._platform == 'macos':
            self.hotkey('command', 'ctrl', 'q')
        elif self._platform == 'windows':
            self.hotkey('win', 'l')
        else:
            self.hotkey('super', 'l')

    def open_spotlight(self) -> None:
        """Open spotlight/search (macOS Spotlight, Windows Search)."""
        if self._platform == 'macos':
            self.hotkey('command', 'space')
        else:
            self.press('win')

    def on_key_press(self, callback) -> None:
        """
        Register a callback for key press events.

        Args:
            callback: Function to call on key press.
        """
        if pynput_keyboard is None:
            raise ImportError("pynput not installed for keyboard event listening")

        def on_press(key):
            try:
                callback(key.char)
            except AttributeError:
                callback(str(key))

        listener = pynput_keyboard.Listener(on_press=on_press)
        listener.start()
