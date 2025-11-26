"""
AI Decision Making Example

This example demonstrates how to integrate AI for decision-making in automation.
Requires OPENAI_API_KEY environment variable to be set.
"""

import sys
from pathlib import Path
import os
from typing import Optional

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_automation import AutomationTask

try:
    from openai import OpenAI
except ImportError:
    print("This example requires openai. Install with: pip install openai")
    sys.exit(1)


class AIDecisionTask(AutomationTask):
    """A task that uses AI to make decisions."""

    def __init__(self, name: str, config: Optional[dict] = None):
        """Initialize with AI client."""
        super().__init__(name, config)
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in your .env file."
            )

        self.client = OpenAI(api_key=api_key)

    def _run(self) -> None:
        """Execute task with AI decision making."""
        prompt = self.config.get(
            "prompt", "Should I proceed with the automation task? Answer yes or no."
        )

        print(f"Asking AI: {prompt}")

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.7,
            )

            answer = response.choices[0].message.content
            print(f"AI Response: {answer}")

            # Make decision based on AI response
            if "yes" in answer.lower():
                print("AI approved - proceeding with automation")
            else:
                print("AI suggested caution - review before proceeding")

        except Exception as e:
            print(f"Error communicating with AI: {e}")
            raise


def main():
    """Run the AI decision making example."""
    print("=" * 60)
    print("AI Decision Making Example")
    print("=" * 60)

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nError: OPENAI_API_KEY not found in environment.")
        print("Please set it in your .env file.")
        return

    print("\nThis example uses OpenAI's API to make automation decisions.")
    print("Note: This will use API credits.\n")

    response = input("Continue? (yes/no): ")
    if response.lower() != "yes":
        print("Aborted.")
        return

    # Example 1: Simple yes/no decision
    task1 = AIDecisionTask(
        "decision_task",
        config={"prompt": "Is it a good idea to automate repetitive tasks?"},
    )
    task1.execute()

    print("\n" + "-" * 60 + "\n")

    # Example 2: Task-specific decision
    task2 = AIDecisionTask(
        "file_organization_task",
        config={
            "prompt": "Should I organize files by date or by type? Give a brief recommendation."
        },
    )
    task2.execute()


if __name__ == "__main__":
    main()
