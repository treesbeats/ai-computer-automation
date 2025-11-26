"""GUI automation utilities."""

import time
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class GUIAutomation:
    """Handles GUI automation tasks."""

    def __init__(
        self,
        click_delay: float = 0.1,
        type_delay: float = 0.05,
        failsafe: bool = True,
    ):
        """
        Initialize GUI automation.

        Args:
            click_delay: Delay between clicks (seconds)
            type_delay: Delay between keystrokes (seconds)
            failsafe: Enable failsafe (move mouse to corner to abort)
        """
        try:
            import pyautogui
            self.pyautogui = pyautogui
        except ImportError:
            raise ImportError(
                "PyAutoGUI not installed. Install with: pip install pyautogui"
            )

        self.click_delay = click_delay
        self.type_delay = type_delay

        # Configure PyAutoGUI
        self.pyautogui.PAUSE = click_delay
        self.pyautogui.FAILSAFE = failsafe

        logger.info(
            f"GUI automation initialized (click_delay={click_delay}s, "
            f"type_delay={type_delay}s, failsafe={failsafe})"
        )

    def click(self, x: int, y: int, clicks: int = 1, button: str = "left") -> None:
        """
        Click at specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            clicks: Number of clicks
            button: Mouse button ('left', 'right', 'middle')
        """
        try:
            self.pyautogui.click(x, y, clicks=clicks, button=button)
            logger.debug(f"Clicked at ({x}, {y}) with {button} button, {clicks} times")
        except Exception as e:
            logger.error(f"Click failed: {e}")
            raise

    def move_to(self, x: int, y: int, duration: float = 0.5) -> None:
        """
        Move mouse to coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration of movement (seconds)
        """
        try:
            self.pyautogui.moveTo(x, y, duration=duration)
            logger.debug(f"Moved mouse to ({x}, {y})")
        except Exception as e:
            logger.error(f"Move failed: {e}")
            raise

    def type_text(self, text: str, interval: Optional[float] = None) -> None:
        """
        Type text with keyboard.

        Args:
            text: Text to type
            interval: Interval between keystrokes (uses type_delay if None)
        """
        interval = interval or self.type_delay
        try:
            self.pyautogui.write(text, interval=interval)
            logger.debug(f"Typed text (length={len(text)})")
        except Exception as e:
            logger.error(f"Type failed: {e}")
            raise

    def press_key(self, key: str) -> None:
        """
        Press a single key.

        Args:
            key: Key name (e.g., 'enter', 'esc', 'tab')
        """
        try:
            self.pyautogui.press(key)
            logger.debug(f"Pressed key: {key}")
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            raise

    def hotkey(self, *keys: str) -> None:
        """
        Press a hotkey combination.

        Args:
            *keys: Keys to press together (e.g., 'ctrl', 'c')
        """
        try:
            self.pyautogui.hotkey(*keys)
            logger.debug(f"Pressed hotkey: {'+'.join(keys)}")
        except Exception as e:
            logger.error(f"Hotkey failed: {e}")
            raise

    def screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> "Image":
        """
        Take a screenshot.

        Args:
            region: Optional region tuple (left, top, width, height)

        Returns:
            PIL Image object
        """
        try:
            if region:
                img = self.pyautogui.screenshot(region=region)
            else:
                img = self.pyautogui.screenshot()
            logger.debug("Screenshot captured")
            return img
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            raise

    def locate_on_screen(
        self, image_path: str, confidence: float = 0.8
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Locate an image on screen.

        Args:
            image_path: Path to image to find
            confidence: Confidence threshold (0-1)

        Returns:
            Tuple of (left, top, width, height) or None if not found
        """
        try:
            location = self.pyautogui.locateOnScreen(
                image_path, confidence=confidence
            )
            if location:
                logger.debug(f"Located image at {location}")
            else:
                logger.debug(f"Image not found: {image_path}")
            return location
        except Exception as e:
            logger.error(f"Locate failed: {e}")
            return None

    def locate_and_click(
        self, image_path: str, confidence: float = 0.8
    ) -> bool:
        """
        Locate an image and click its center.

        Args:
            image_path: Path to image to find and click
            confidence: Confidence threshold (0-1)

        Returns:
            True if found and clicked, False otherwise
        """
        location = self.locate_on_screen(image_path, confidence)
        if location:
            center_x = location[0] + location[2] // 2
            center_y = location[1] + location[3] // 2
            self.click(center_x, center_y)
            return True
        return False

    def get_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.

        Returns:
            Tuple of (x, y) coordinates
        """
        pos = self.pyautogui.position()
        return (pos.x, pos.y)

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen size.

        Returns:
            Tuple of (width, height)
        """
        size = self.pyautogui.size()
        return (size.width, size.height)

    def wait(self, seconds: float) -> None:
        """
        Wait for specified duration.

        Args:
            seconds: Duration to wait
        """
        time.sleep(seconds)
        logger.debug(f"Waited {seconds}s")
