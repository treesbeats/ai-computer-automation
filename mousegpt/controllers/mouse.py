"""Mouse controller for MouseGPT."""

from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from pynput import mouse as pynput_mouse
except ImportError:
    pynput_mouse = None

from mousegpt.config.settings import Settings, get_settings


class MouseButton(str, Enum):
    """Mouse buttons."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


@dataclass
class MousePosition:
    """Current mouse position."""
    x: int
    y: int


class MouseController:
    """
    Controller for mouse operations.

    Provides methods for:
    - Moving the mouse cursor
    - Clicking (single, double, right, middle)
    - Dragging
    - Scrolling
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the mouse controller."""
        if pyautogui is None:
            raise ImportError(
                "pyautogui package not installed. "
                "Install with: pip install pyautogui"
            )

        self.settings = settings or get_settings()

        # Configure pyautogui
        pyautogui.FAILSAFE = self.settings.failsafe_enabled
        pyautogui.PAUSE = 0.1  # Small pause between actions

        # Get screen size
        self._screen_width, self._screen_height = pyautogui.size()

    @property
    def screen_size(self) -> Tuple[int, int]:
        """Get the screen size."""
        return self._screen_width, self._screen_height

    def get_position(self) -> MousePosition:
        """Get the current mouse position."""
        x, y = pyautogui.position()
        return MousePosition(x=x, y=y)

    def move_to(
        self,
        x: int,
        y: int,
        duration: Optional[float] = None,
        smooth: Optional[bool] = None,
    ) -> MousePosition:
        """
        Move the mouse to absolute coordinates.

        Args:
            x: Target X coordinate.
            y: Target Y coordinate.
            duration: Movement duration in seconds.
            smooth: Whether to use smooth movement.

        Returns:
            The new mouse position.
        """
        duration = duration if duration is not None else self.settings.mouse_movement_duration
        smooth = smooth if smooth is not None else self.settings.mouse_smooth_movement

        # Clamp to screen bounds
        x = max(0, min(x, self._screen_width - 1))
        y = max(0, min(y, self._screen_height - 1))

        if smooth and duration > 0:
            pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeOutQuad)
        else:
            pyautogui.moveTo(x, y, duration=0)

        return self.get_position()

    def move_relative(
        self,
        dx: int = 0,
        dy: int = 0,
        duration: Optional[float] = None,
    ) -> MousePosition:
        """
        Move the mouse relative to current position.

        Args:
            dx: Horizontal offset (positive = right).
            dy: Vertical offset (positive = down).
            duration: Movement duration in seconds.

        Returns:
            The new mouse position.
        """
        duration = duration if duration is not None else self.settings.mouse_movement_duration

        # Apply speed multiplier
        dx = int(dx * self.settings.mouse_speed)
        dy = int(dy * self.settings.mouse_speed)

        pyautogui.move(dx, dy, duration=duration)
        return self.get_position()

    def move_direction(
        self,
        direction: str,
        distance: int = 100,
        duration: Optional[float] = None,
    ) -> MousePosition:
        """
        Move the mouse in a direction.

        Args:
            direction: One of 'up', 'down', 'left', 'right'.
            distance: Distance to move in pixels.
            duration: Movement duration in seconds.

        Returns:
            The new mouse position.
        """
        direction_map = {
            'up': (0, -distance),
            'down': (0, distance),
            'left': (-distance, 0),
            'right': (distance, 0),
        }

        dx, dy = direction_map.get(direction.lower(), (0, 0))
        return self.move_relative(dx, dy, duration)

    def move_to_relative_position(
        self,
        rel_x: float,
        rel_y: float,
        duration: Optional[float] = None,
    ) -> MousePosition:
        """
        Move to a position relative to screen size.

        Args:
            rel_x: X position as fraction of screen width (0.0 to 1.0).
            rel_y: Y position as fraction of screen height (0.0 to 1.0).
            duration: Movement duration in seconds.

        Returns:
            The new mouse position.
        """
        x = int(self._screen_width * rel_x)
        y = int(self._screen_height * rel_y)
        return self.move_to(x, y, duration)

    def click(
        self,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval: float = 0.1,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> None:
        """
        Click the mouse.

        Args:
            button: Which mouse button to click.
            clicks: Number of clicks.
            interval: Interval between clicks.
            x: Optional X coordinate to click at.
            y: Optional Y coordinate to click at.
        """
        kwargs = {
            'button': button.value,
            'clicks': clicks,
            'interval': interval,
        }

        if x is not None and y is not None:
            kwargs['x'] = x
            kwargs['y'] = y

        pyautogui.click(**kwargs)

    def left_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> None:
        """Perform a left click."""
        self.click(MouseButton.LEFT, x=x, y=y)

    def right_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> None:
        """Perform a right click."""
        self.click(MouseButton.RIGHT, x=x, y=y)

    def middle_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> None:
        """Perform a middle click."""
        self.click(MouseButton.MIDDLE, x=x, y=y)

    def double_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> None:
        """Perform a double click."""
        self.click(MouseButton.LEFT, clicks=2, x=x, y=y)

    def triple_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> None:
        """Perform a triple click (often selects a line)."""
        self.click(MouseButton.LEFT, clicks=3, x=x, y=y)

    def drag_to(
        self,
        x: int,
        y: int,
        duration: Optional[float] = None,
        button: MouseButton = MouseButton.LEFT,
    ) -> None:
        """
        Drag the mouse to a position.

        Args:
            x: Target X coordinate.
            y: Target Y coordinate.
            duration: Drag duration in seconds.
            button: Which button to hold while dragging.
        """
        duration = duration if duration is not None else self.settings.mouse_movement_duration
        pyautogui.drag(x - pyautogui.position()[0], y - pyautogui.position()[1],
                       duration=duration, button=button.value)

    def drag_relative(
        self,
        dx: int,
        dy: int,
        duration: Optional[float] = None,
        button: MouseButton = MouseButton.LEFT,
    ) -> None:
        """
        Drag the mouse relative to current position.

        Args:
            dx: Horizontal distance.
            dy: Vertical distance.
            duration: Drag duration in seconds.
            button: Which button to hold while dragging.
        """
        duration = duration if duration is not None else self.settings.mouse_movement_duration
        pyautogui.drag(dx, dy, duration=duration, button=button.value)

    def scroll(
        self,
        clicks: int,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> None:
        """
        Scroll the mouse wheel.

        Args:
            clicks: Number of scroll "clicks" (positive = up, negative = down).
            x: Optional X coordinate to scroll at.
            y: Optional Y coordinate to scroll at.
        """
        if x is not None and y is not None:
            pyautogui.scroll(clicks, x=x, y=y)
        else:
            pyautogui.scroll(clicks)

    def scroll_up(self, amount: int = 3) -> None:
        """Scroll up."""
        self.scroll(amount)

    def scroll_down(self, amount: int = 3) -> None:
        """Scroll down."""
        self.scroll(-amount)

    def scroll_direction(self, direction: str, amount: int = 3) -> None:
        """
        Scroll in a direction.

        Args:
            direction: One of 'up', 'down'.
            amount: Number of scroll units.
        """
        if direction.lower() == 'up':
            self.scroll_up(amount)
        elif direction.lower() == 'down':
            self.scroll_down(amount)

    def mouse_down(self, button: MouseButton = MouseButton.LEFT) -> None:
        """Press and hold a mouse button."""
        pyautogui.mouseDown(button=button.value)

    def mouse_up(self, button: MouseButton = MouseButton.LEFT) -> None:
        """Release a mouse button."""
        pyautogui.mouseUp(button=button.value)

    def center_screen(self) -> MousePosition:
        """Move mouse to center of screen."""
        return self.move_to(self._screen_width // 2, self._screen_height // 2)

    def on_click(self, callback) -> None:
        """
        Register a callback for mouse click events.

        Args:
            callback: Function to call on click events.
        """
        if pynput_mouse is None:
            raise ImportError("pynput not installed for mouse event listening")

        def on_click_wrapper(x, y, button, pressed):
            callback(x, y, str(button), pressed)

        listener = pynput_mouse.Listener(on_click=on_click_wrapper)
        listener.start()
