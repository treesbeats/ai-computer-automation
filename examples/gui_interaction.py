"""
GUI Interaction Example

This example demonstrates GUI automation capabilities.
Note: This requires pyautogui and should be used with caution.
"""

import sys
from pathlib import Path
import time

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_automation import AutomationTask

try:
    import pyautogui
except ImportError:
    print("This example requires pyautogui. Install with: pip install pyautogui")
    sys.exit(1)


class GUITask(AutomationTask):
    """A task that demonstrates GUI automation."""

    def _run(self) -> None:
        """Execute GUI automation."""
        print(f"Screen size: {pyautogui.size()}")
        print(f"Current mouse position: {pyautogui.position()}")

        # Safety settings
        pyautogui.PAUSE = 0.5
        pyautogui.FAILSAFE = True

        print("\nSafety features enabled:")
        print("- Pause between actions: 0.5s")
        print("- Failsafe: Move mouse to corner to abort")

        # Example: Get screenshot dimensions
        screenshot = pyautogui.screenshot()
        print(f"\nScreenshot captured: {screenshot.size}")


def main():
    """Run the GUI interaction example."""
    print("=" * 60)
    print("GUI Interaction Example")
    print("=" * 60)
    print("\nWARNING: This example demonstrates GUI automation.")
    print("Make sure you understand what it does before running.\n")

    response = input("Continue? (yes/no): ")
    if response.lower() != "yes":
        print("Aborted.")
        return

    task = GUITask("gui_task")
    task.execute()


if __name__ == "__main__":
    main()
