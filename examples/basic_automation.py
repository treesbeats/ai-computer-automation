"""
Basic Automation Example

This example demonstrates a simple automation task using the AI Computer Automation framework.
"""

import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_automation import AutomationTask


class SimpleTask(AutomationTask):
    """A simple automation task that prints a message."""

    def _run(self) -> None:
        """Execute the simple task."""
        message = self.config.get("message", "Hello from AI Computer Automation!")
        print(f"Task '{self.name}' is running...")
        print(f"Message: {message}")
        print("Task completed successfully!")


def main():
    """Run the basic automation example."""
    print("=" * 60)
    print("Basic Automation Example")
    print("=" * 60)

    # Create a task with default message
    task1 = SimpleTask("greeting_task")
    task1.execute()

    print()

    # Create a task with custom message
    task2 = SimpleTask("custom_task", config={"message": "Custom automation message!"})
    task2.execute()


if __name__ == "__main__":
    main()
