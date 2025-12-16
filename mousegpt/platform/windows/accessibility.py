"""
Windows Accessibility Integration for MouseGPT.

This module provides integration with Windows accessibility features,
including low-level input simulation and accessibility hooks.
"""

import time
import ctypes
from ctypes import wintypes
from typing import Optional, Tuple, List, Callable
from dataclasses import dataclass
from enum import IntFlag

# Windows constants and structures
try:
    import win32api
    import win32con
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


# Input types for SendInput
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

# Mouse event flags
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000

# Keyboard event flags
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_UNICODE = 0x0004


class MOUSEINPUT(ctypes.Structure):
    """Windows MOUSEINPUT structure."""
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class KEYBDINPUT(ctypes.Structure):
    """Windows KEYBDINPUT structure."""
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class HARDWAREINPUT(ctypes.Structure):
    """Windows HARDWAREINPUT structure."""
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUTUNION(ctypes.Union):
    """Union for INPUT structure."""
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    """Windows INPUT structure."""
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUTUNION),
    ]


@dataclass
class AccessibilityInfo:
    """Information about Windows accessibility settings."""
    screen_reader_active: bool
    high_contrast: bool
    narrator_running: bool
    magnifier_running: bool
    sticky_keys: bool
    filter_keys: bool
    toggle_keys: bool
    mouse_keys: bool


class WindowsAccessibility:
    """
    Windows Accessibility integration.

    Provides low-level input simulation and accessibility feature detection.
    Uses the Windows SendInput API for reliable input injection.
    """

    def __init__(self):
        """Initialize Windows Accessibility."""
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32

        # Get screen metrics
        self._screen_width = self.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        self._screen_height = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN

    def send_input(self, inputs: List[INPUT]) -> int:
        """
        Send input events to Windows.

        Args:
            inputs: List of INPUT structures.

        Returns:
            Number of events successfully sent.
        """
        n_inputs = len(inputs)
        input_array = (INPUT * n_inputs)(*inputs)
        return self.user32.SendInput(
            n_inputs,
            ctypes.pointer(input_array),
            ctypes.sizeof(INPUT)
        )

    def _create_mouse_input(
        self,
        dx: int = 0,
        dy: int = 0,
        flags: int = 0,
        mouse_data: int = 0,
    ) -> INPUT:
        """Create a mouse input structure."""
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.union.mi.dx = dx
        inp.union.mi.dy = dy
        inp.union.mi.mouseData = mouse_data
        inp.union.mi.dwFlags = flags
        inp.union.mi.time = 0
        inp.union.mi.dwExtraInfo = None
        return inp

    def _create_keyboard_input(
        self,
        vk: int = 0,
        scan: int = 0,
        flags: int = 0,
    ) -> INPUT:
        """Create a keyboard input structure."""
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.union.ki.wVk = vk
        inp.union.ki.wScan = scan
        inp.union.ki.dwFlags = flags
        inp.union.ki.time = 0
        inp.union.ki.dwExtraInfo = None
        return inp

    def _normalize_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Normalize coordinates to 0-65535 range for absolute positioning."""
        norm_x = int((x * 65535) / self._screen_width)
        norm_y = int((y * 65535) / self._screen_height)
        return norm_x, norm_y

    # Mouse operations

    def mouse_move(self, x: int, y: int, absolute: bool = True) -> None:
        """
        Move the mouse cursor.

        Args:
            x: X coordinate or offset.
            y: Y coordinate or offset.
            absolute: If True, move to absolute position.
        """
        if absolute:
            norm_x, norm_y = self._normalize_coords(x, y)
            flags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
            inp = self._create_mouse_input(norm_x, norm_y, flags)
        else:
            inp = self._create_mouse_input(x, y, MOUSEEVENTF_MOVE)

        self.send_input([inp])

    def mouse_click(
        self,
        button: str = "left",
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> None:
        """
        Perform a mouse click.

        Args:
            button: "left", "right", or "middle".
            x: Optional X coordinate.
            y: Optional Y coordinate.
        """
        inputs = []

        # Move to position if specified
        if x is not None and y is not None:
            norm_x, norm_y = self._normalize_coords(x, y)
            move_inp = self._create_mouse_input(
                norm_x, norm_y,
                MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
            )
            inputs.append(move_inp)

        # Button down/up flags
        button_flags = {
            "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
            "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
            "middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
        }

        down_flag, up_flag = button_flags.get(button, button_flags["left"])

        inputs.append(self._create_mouse_input(flags=down_flag))
        inputs.append(self._create_mouse_input(flags=up_flag))

        self.send_input(inputs)

    def mouse_double_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> None:
        """Perform a double click."""
        self.mouse_click("left", x, y)
        time.sleep(0.05)
        self.mouse_click("left", x, y)

    def mouse_scroll(self, amount: int, horizontal: bool = False) -> None:
        """
        Scroll the mouse wheel.

        Args:
            amount: Scroll amount (positive = up/right, negative = down/left).
            horizontal: If True, scroll horizontally.
        """
        # Wheel delta is 120 per "click"
        wheel_delta = amount * 120

        flag = MOUSEEVENTF_HWHEEL if horizontal else MOUSEEVENTF_WHEEL
        inp = self._create_mouse_input(flags=flag, mouse_data=wheel_delta)
        self.send_input([inp])

    def mouse_drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        button: str = "left",
        steps: int = 10,
    ) -> None:
        """
        Perform a mouse drag operation.

        Args:
            start_x: Starting X coordinate.
            start_y: Starting Y coordinate.
            end_x: Ending X coordinate.
            end_y: Ending Y coordinate.
            button: Mouse button to hold.
            steps: Number of intermediate steps.
        """
        # Move to start
        self.mouse_move(start_x, start_y)
        time.sleep(0.05)

        # Press button
        button_flags = {
            "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
            "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
            "middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
        }
        down_flag, up_flag = button_flags.get(button, button_flags["left"])

        inp = self._create_mouse_input(flags=down_flag)
        self.send_input([inp])

        # Drag in steps
        for i in range(1, steps + 1):
            x = start_x + (end_x - start_x) * i // steps
            y = start_y + (end_y - start_y) * i // steps
            self.mouse_move(x, y)
            time.sleep(0.01)

        # Release button
        inp = self._create_mouse_input(flags=up_flag)
        self.send_input([inp])

    # Keyboard operations

    def key_press(self, vk: int) -> None:
        """
        Press and release a key.

        Args:
            vk: Virtual key code.
        """
        down = self._create_keyboard_input(vk=vk)
        up = self._create_keyboard_input(vk=vk, flags=KEYEVENTF_KEYUP)
        self.send_input([down, up])

    def key_down(self, vk: int) -> None:
        """Press a key down."""
        inp = self._create_keyboard_input(vk=vk)
        self.send_input([inp])

    def key_up(self, vk: int) -> None:
        """Release a key."""
        inp = self._create_keyboard_input(vk=vk, flags=KEYEVENTF_KEYUP)
        self.send_input([inp])

    def type_text(self, text: str) -> None:
        """
        Type text using Unicode input.

        Args:
            text: Text to type.
        """
        inputs = []
        for char in text:
            # Unicode character input
            down = self._create_keyboard_input(
                scan=ord(char),
                flags=KEYEVENTF_UNICODE
            )
            up = self._create_keyboard_input(
                scan=ord(char),
                flags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
            )
            inputs.extend([down, up])

        self.send_input(inputs)

    def hotkey(self, *keys: int) -> None:
        """
        Press a key combination.

        Args:
            keys: Virtual key codes to press together.
        """
        inputs = []

        # Press all keys down
        for vk in keys:
            inputs.append(self._create_keyboard_input(vk=vk))

        # Release all keys up (in reverse order)
        for vk in reversed(keys):
            inputs.append(self._create_keyboard_input(vk=vk, flags=KEYEVENTF_KEYUP))

        self.send_input(inputs)

    # Accessibility information

    def get_accessibility_info(self) -> AccessibilityInfo:
        """Get information about accessibility settings."""
        return AccessibilityInfo(
            screen_reader_active=self._is_screen_reader_active(),
            high_contrast=self._is_high_contrast(),
            narrator_running=self._is_narrator_running(),
            magnifier_running=self._is_magnifier_running(),
            sticky_keys=self._is_sticky_keys_on(),
            filter_keys=self._is_filter_keys_on(),
            toggle_keys=self._is_toggle_keys_on(),
            mouse_keys=self._is_mouse_keys_on(),
        )

    def _is_screen_reader_active(self) -> bool:
        """Check if a screen reader is active."""
        # SPI_GETSCREENREADER = 0x0046
        result = wintypes.BOOL()
        self.user32.SystemParametersInfoW(0x0046, 0, ctypes.byref(result), 0)
        return bool(result.value)

    def _is_high_contrast(self) -> bool:
        """Check if high contrast mode is enabled."""
        # SPI_GETHIGHCONTRAST = 0x0042
        class HIGHCONTRAST(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("dwFlags", wintypes.DWORD),
                ("lpszDefaultScheme", wintypes.LPWSTR),
            ]

        hc = HIGHCONTRAST()
        hc.cbSize = ctypes.sizeof(HIGHCONTRAST)
        self.user32.SystemParametersInfoW(0x0042, hc.cbSize, ctypes.byref(hc), 0)
        # HCF_HIGHCONTRASTON = 0x00000001
        return bool(hc.dwFlags & 0x00000001)

    def _is_narrator_running(self) -> bool:
        """Check if Windows Narrator is running."""
        if WIN32_AVAILABLE:
            hwnd = win32gui.FindWindow(None, "Narrator")
            return hwnd != 0
        return False

    def _is_magnifier_running(self) -> bool:
        """Check if Windows Magnifier is running."""
        if WIN32_AVAILABLE:
            hwnd = win32gui.FindWindow("MagUIClass", None)
            return hwnd != 0
        return False

    def _is_sticky_keys_on(self) -> bool:
        """Check if Sticky Keys is enabled."""
        class STICKYKEYS(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("dwFlags", wintypes.DWORD),
            ]

        sk = STICKYKEYS()
        sk.cbSize = ctypes.sizeof(STICKYKEYS)
        # SPI_GETSTICKYKEYS = 0x003A
        self.user32.SystemParametersInfoW(0x003A, sk.cbSize, ctypes.byref(sk), 0)
        # SKF_STICKYKEYSON = 0x00000001
        return bool(sk.dwFlags & 0x00000001)

    def _is_filter_keys_on(self) -> bool:
        """Check if Filter Keys is enabled."""
        class FILTERKEYS(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("dwFlags", wintypes.DWORD),
                ("iWaitMSec", wintypes.DWORD),
                ("iDelayMSec", wintypes.DWORD),
                ("iRepeatMSec", wintypes.DWORD),
                ("iBounceMSec", wintypes.DWORD),
            ]

        fk = FILTERKEYS()
        fk.cbSize = ctypes.sizeof(FILTERKEYS)
        # SPI_GETFILTERKEYS = 0x0032
        self.user32.SystemParametersInfoW(0x0032, fk.cbSize, ctypes.byref(fk), 0)
        # FKF_FILTERKEYSON = 0x00000001
        return bool(fk.dwFlags & 0x00000001)

    def _is_toggle_keys_on(self) -> bool:
        """Check if Toggle Keys is enabled."""
        class TOGGLEKEYS(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("dwFlags", wintypes.DWORD),
            ]

        tk = TOGGLEKEYS()
        tk.cbSize = ctypes.sizeof(TOGGLEKEYS)
        # SPI_GETTOGGLEKEYS = 0x0034
        self.user32.SystemParametersInfoW(0x0034, tk.cbSize, ctypes.byref(tk), 0)
        # TKF_TOGGLEKEYSON = 0x00000001
        return bool(tk.dwFlags & 0x00000001)

    def _is_mouse_keys_on(self) -> bool:
        """Check if Mouse Keys is enabled."""
        class MOUSEKEYS(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("dwFlags", wintypes.DWORD),
                ("iMaxSpeed", wintypes.DWORD),
                ("iTimeToMaxSpeed", wintypes.DWORD),
                ("iCtrlSpeed", wintypes.DWORD),
                ("dwReserved1", wintypes.DWORD),
                ("dwReserved2", wintypes.DWORD),
            ]

        mk = MOUSEKEYS()
        mk.cbSize = ctypes.sizeof(MOUSEKEYS)
        # SPI_GETMOUSEKEYS = 0x0036
        self.user32.SystemParametersInfoW(0x0036, mk.cbSize, ctypes.byref(mk), 0)
        # MKF_MOUSEKEYSON = 0x00000001
        return bool(mk.dwFlags & 0x00000001)


# Virtual key code mappings
VK_CODES = {
    # Letters
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
    'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
    'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
    'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59,
    'z': 0x5A,

    # Numbers
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,

    # Function keys
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
    'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
    'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,

    # Special keys
    'backspace': 0x08, 'tab': 0x09, 'enter': 0x0D, 'return': 0x0D,
    'shift': 0x10, 'ctrl': 0x11, 'control': 0x11, 'alt': 0x12,
    'pause': 0x13, 'capslock': 0x14, 'escape': 0x1B, 'esc': 0x1B,
    'space': 0x20, 'pageup': 0x21, 'pagedown': 0x22,
    'end': 0x23, 'home': 0x24,
    'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
    'printscreen': 0x2C, 'insert': 0x2D, 'delete': 0x2E,
    'win': 0x5B, 'windows': 0x5B, 'apps': 0x5D,
    'numlock': 0x90, 'scrolllock': 0x91,

    # Modifier keys (left/right variants)
    'lshift': 0xA0, 'rshift': 0xA1,
    'lctrl': 0xA2, 'rctrl': 0xA3,
    'lalt': 0xA4, 'ralt': 0xA5,
}


def get_vk_code(key: str) -> int:
    """
    Get the virtual key code for a key name.

    Args:
        key: Key name (e.g., "a", "enter", "ctrl").

    Returns:
        Virtual key code.
    """
    return VK_CODES.get(key.lower(), 0)
