"""
Computer Vision Example

This example demonstrates basic computer vision capabilities for automation.
Requires opencv-python and pillow.
"""

import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_automation import AutomationTask

try:
    import cv2
    from PIL import Image
    import pyautogui
except ImportError:
    print("This example requires opencv-python, pillow, and pyautogui.")
    print("Install with: pip install opencv-python pillow pyautogui")
    sys.exit(1)


class VisionTask(AutomationTask):
    """A task that demonstrates computer vision capabilities."""

    def _run(self) -> None:
        """Execute computer vision operations."""
        # Take a screenshot
        screenshot = pyautogui.screenshot()
        print(f"Screenshot captured: {screenshot.size}")

        # Convert to OpenCV format
        import numpy as np

        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        print(f"Converted to OpenCV format: {screenshot_cv.shape}")

        # Basic image analysis
        height, width, channels = screenshot_cv.shape
        print(f"\nImage Analysis:")
        print(f"- Dimensions: {width}x{height}")
        print(f"- Channels: {channels}")
        print(f"- Total pixels: {width * height:,}")

        # Color analysis
        avg_color = screenshot_cv.mean(axis=(0, 1))
        print(f"\nAverage color (BGR): {avg_color}")

        # Convert to grayscale for analysis
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        avg_brightness = gray.mean()
        print(f"Average brightness: {avg_brightness:.2f}")

        # Detect edges (simple edge detection)
        edges = cv2.Canny(gray, 100, 200)
        edge_pixels = cv2.countNonZero(edges)
        edge_percentage = (edge_pixels / (width * height)) * 100

        print(f"\nEdge Detection:")
        print(f"- Edge pixels: {edge_pixels:,}")
        print(f"- Edge percentage: {edge_percentage:.2f}%")

        print("\nVision analysis complete!")


def main():
    """Run the computer vision example."""
    print("=" * 60)
    print("Computer Vision Example")
    print("=" * 60)
    print("\nThis example captures and analyzes your screen.")
    print("No files will be saved.\n")

    response = input("Continue? (yes/no): ")
    if response.lower() != "yes":
        print("Aborted.")
        return

    task = VisionTask("vision_task")
    task.execute()


if __name__ == "__main__":
    main()
