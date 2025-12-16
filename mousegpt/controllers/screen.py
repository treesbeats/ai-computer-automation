"""Screen controller for MouseGPT."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import numpy as np
except ImportError:
    np = None

from mousegpt.config.settings import Settings, get_settings


class ScreenController:
    """
    Controller for screen operations.

    Provides methods for:
    - Taking screenshots
    - Finding elements on screen
    - Getting screen information
    - Image recognition and matching
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the screen controller."""
        if pyautogui is None:
            raise ImportError(
                "pyautogui package not installed. "
                "Install with: pip install pyautogui"
            )

        self.settings = settings or get_settings()
        self._screen_width, self._screen_height = pyautogui.size()

    @property
    def screen_size(self) -> Tuple[int, int]:
        """Get the screen size."""
        return self._screen_width, self._screen_height

    @property
    def screen_width(self) -> int:
        """Get the screen width."""
        return self._screen_width

    @property
    def screen_height(self) -> int:
        """Get the screen height."""
        return self._screen_height

    def screenshot(
        self,
        path: Optional[Union[str, Path]] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Image.Image:
        """
        Take a screenshot.

        Args:
            path: Optional path to save the screenshot.
            region: Optional region (x, y, width, height) to capture.

        Returns:
            PIL Image object.
        """
        if region:
            img = pyautogui.screenshot(region=region)
        else:
            img = pyautogui.screenshot()

        if path:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            img.save(str(path))

        return img

    def screenshot_to_file(
        self,
        directory: Optional[Union[str, Path]] = None,
        prefix: str = "screenshot",
    ) -> Path:
        """
        Take a screenshot and save to a timestamped file.

        Args:
            directory: Directory to save screenshots.
            prefix: Filename prefix.

        Returns:
            Path to the saved screenshot.
        """
        if directory is None:
            directory = Path.home() / "Pictures" / "MouseGPT"

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.{self.settings.screen_capture_format}"
        filepath = directory / filename

        self.screenshot(path=filepath)
        return filepath

    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """
        Get the color of a pixel at the specified coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            Tuple of (R, G, B) values.
        """
        return pyautogui.pixel(x, y)

    def pixel_matches_color(
        self,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        tolerance: int = 0,
    ) -> bool:
        """
        Check if a pixel matches a color.

        Args:
            x: X coordinate.
            y: Y coordinate.
            color: Expected RGB color.
            tolerance: Color matching tolerance.

        Returns:
            True if pixel matches color within tolerance.
        """
        return pyautogui.pixelMatchesColor(x, y, color, tolerance=tolerance)

    def locate_on_screen(
        self,
        image: Union[str, Path, Image.Image],
        confidence: float = 0.9,
        grayscale: bool = False,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Locate an image on the screen.

        Args:
            image: Image to find (path or PIL Image).
            confidence: Matching confidence (0.0 to 1.0).
            grayscale: Use grayscale matching (faster).
            region: Region to search within.

        Returns:
            Bounding box (x, y, width, height) or None if not found.
        """
        try:
            location = pyautogui.locateOnScreen(
                image,
                confidence=confidence,
                grayscale=grayscale,
                region=region,
            )
            if location:
                return (location.left, location.top, location.width, location.height)
            return None
        except Exception:
            return None

    def locate_all_on_screen(
        self,
        image: Union[str, Path, Image.Image],
        confidence: float = 0.9,
        grayscale: bool = False,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> list[Tuple[int, int, int, int]]:
        """
        Locate all instances of an image on the screen.

        Args:
            image: Image to find.
            confidence: Matching confidence.
            grayscale: Use grayscale matching.
            region: Region to search within.

        Returns:
            List of bounding boxes.
        """
        try:
            locations = pyautogui.locateAllOnScreen(
                image,
                confidence=confidence,
                grayscale=grayscale,
                region=region,
            )
            return [
                (loc.left, loc.top, loc.width, loc.height)
                for loc in locations
            ]
        except Exception:
            return []

    def locate_center_on_screen(
        self,
        image: Union[str, Path, Image.Image],
        confidence: float = 0.9,
        grayscale: bool = False,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Optional[Tuple[int, int]]:
        """
        Locate the center of an image on screen.

        Args:
            image: Image to find.
            confidence: Matching confidence.
            grayscale: Use grayscale matching.
            region: Region to search within.

        Returns:
            Center coordinates (x, y) or None if not found.
        """
        location = self.locate_on_screen(image, confidence, grayscale, region)
        if location:
            x, y, w, h = location
            return (x + w // 2, y + h // 2)
        return None

    def wait_for_image(
        self,
        image: Union[str, Path, Image.Image],
        timeout: float = 10.0,
        interval: float = 0.5,
        confidence: float = 0.9,
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Wait for an image to appear on screen.

        Args:
            image: Image to wait for.
            timeout: Maximum time to wait in seconds.
            interval: Check interval in seconds.
            confidence: Matching confidence.

        Returns:
            Bounding box or None if timeout.
        """
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            location = self.locate_on_screen(image, confidence=confidence)
            if location:
                return location
            time.sleep(interval)

        return None

    def wait_for_image_to_disappear(
        self,
        image: Union[str, Path, Image.Image],
        timeout: float = 10.0,
        interval: float = 0.5,
        confidence: float = 0.9,
    ) -> bool:
        """
        Wait for an image to disappear from screen.

        Args:
            image: Image to wait for disappearance.
            timeout: Maximum time to wait in seconds.
            interval: Check interval in seconds.
            confidence: Matching confidence.

        Returns:
            True if image disappeared, False if timeout.
        """
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            location = self.locate_on_screen(image, confidence=confidence)
            if location is None:
                return True
            time.sleep(interval)

        return False

    def get_window_list(self) -> list[dict]:
        """
        Get a list of open windows.

        Returns:
            List of window information dictionaries.

        Note: This requires additional platform-specific libraries.
        """
        windows = []

        try:
            all_windows = pyautogui.getAllWindows()
            for window in all_windows:
                windows.append({
                    'title': window.title,
                    'left': window.left,
                    'top': window.top,
                    'width': window.width,
                    'height': window.height,
                    'visible': window.visible,
                    'minimized': window.isMinimized,
                    'maximized': window.isMaximized,
                    'active': window.isActive,
                })
        except Exception:
            pass

        return windows

    def get_active_window(self) -> Optional[dict]:
        """
        Get information about the active window.

        Returns:
            Window information dictionary or None.
        """
        try:
            window = pyautogui.getActiveWindow()
            if window:
                return {
                    'title': window.title,
                    'left': window.left,
                    'top': window.top,
                    'width': window.width,
                    'height': window.height,
                }
        except Exception:
            pass
        return None

    def find_window(self, title: str) -> Optional[dict]:
        """
        Find a window by title.

        Args:
            title: Window title to search for (partial match).

        Returns:
            Window information or None if not found.
        """
        try:
            windows = pyautogui.getWindowsWithTitle(title)
            if windows:
                window = windows[0]
                return {
                    'title': window.title,
                    'left': window.left,
                    'top': window.top,
                    'width': window.width,
                    'height': window.height,
                }
        except Exception:
            pass
        return None

    def activate_window(self, title: str) -> bool:
        """
        Activate (focus) a window by title.

        Args:
            title: Window title to activate.

        Returns:
            True if window was activated, False otherwise.
        """
        try:
            windows = pyautogui.getWindowsWithTitle(title)
            if windows:
                windows[0].activate()
                return True
        except Exception:
            pass
        return False

    def screenshot_region_around_cursor(
        self,
        width: int = 200,
        height: int = 200,
    ) -> Image.Image:
        """
        Take a screenshot of the region around the cursor.

        Args:
            width: Width of the region.
            height: Height of the region.

        Returns:
            PIL Image of the region.
        """
        x, y = pyautogui.position()
        left = max(0, x - width // 2)
        top = max(0, y - height // 2)

        return self.screenshot(region=(left, top, width, height))

    def get_screen_resolution(self) -> Tuple[int, int]:
        """Get the screen resolution."""
        return self._screen_width, self._screen_height

    def is_retina(self) -> bool:
        """Check if running on a retina/HiDPI display."""
        if Image is None:
            return False

        img = self.screenshot()
        actual_width = img.size[0]

        return actual_width > self._screen_width
