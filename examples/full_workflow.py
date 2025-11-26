"""
Full Workflow Example

This example demonstrates a complete automation workflow using multiple
components of the AI Computer Automation framework.
"""

import sys
from pathlib import Path
import os

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_automation import AutomationTask
from ai_automation.utils import setup_logger, load_config, retry, timer


class WorkflowTask(AutomationTask):
    """A comprehensive workflow automation task."""

    def __init__(self, name: str, config: dict = None):
        """Initialize workflow task."""
        super().__init__(name, config)
        self.logger = setup_logger("workflow_task", level="INFO")

    @retry(max_attempts=3, delay=1.0)
    def _fetch_data(self):
        """Simulate fetching data with retry logic."""
        self.logger.info("Fetching data...")
        # In a real scenario, this would fetch from an API or file
        return {"status": "success", "data": [1, 2, 3, 4, 5]}

    @timer
    def _process_data(self, data):
        """Process the fetched data."""
        self.logger.info(f"Processing data: {len(data['data'])} items")
        # Simulate processing
        processed = [x * 2 for x in data["data"]]
        return processed

    def _run(self) -> None:
        """Execute the workflow."""
        self.logger.info(f"Starting workflow: {self.name}")

        try:
            # Step 1: Fetch data
            data = self._fetch_data()
            self.logger.info(f"Data fetched: {data['status']}")

            # Step 2: Process data
            processed = self._process_data(data)
            self.logger.info(f"Data processed: {processed}")

            # Step 3: Generate report
            self._generate_report(processed)

            self.logger.info("Workflow completed successfully")

        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            raise

    def _generate_report(self, data):
        """Generate a simple report."""
        self.logger.info("Generating report...")
        report = f"""
        ========================================
        Workflow Report: {self.name}
        ========================================
        Total items processed: {len(data)}
        Sum: {sum(data)}
        Average: {sum(data) / len(data):.2f}
        Min: {min(data)}
        Max: {max(data)}
        ========================================
        """
        print(report)


class AIEnhancedWorkflow(AutomationTask):
    """Workflow with AI decision making."""

    def __init__(self, name: str, config: dict = None):
        """Initialize AI-enhanced workflow."""
        super().__init__(name, config)
        self.logger = setup_logger("ai_workflow", level="INFO")

    def _run(self) -> None:
        """Execute AI-enhanced workflow."""
        self.logger.info(f"Starting AI-enhanced workflow: {self.name}")

        # Check if we have AI credentials
        openai_key = os.getenv("OPENAI_API_KEY")

        if not openai_key:
            self.logger.warning("OpenAI API key not found. Running without AI.")
            print("Note: Set OPENAI_API_KEY in .env for AI features")
            self._run_without_ai()
            return

        try:
            from ai_automation.ai import create_ai_client, AIDecisionMaker

            # Create AI client
            client = create_ai_client("openai", api_key=openai_key, model="gpt-3.5-turbo")
            decision_maker = AIDecisionMaker(client)

            # Use AI to generate action plan
            goal = self.config.get("goal", "Process and analyze data efficiently")
            constraints = self.config.get("constraints", ["Time limit: 5 minutes", "Budget: Low cost"])

            self.logger.info(f"Asking AI to generate plan for: {goal}")
            plan = decision_maker.generate_action_plan(goal, constraints)

            print("\n" + "=" * 60)
            print("AI-Generated Action Plan:")
            print("=" * 60)
            for i, step in enumerate(plan, 1):
                print(f"{i}. {step}")
            print("=" * 60 + "\n")

            # Ask AI whether to proceed
            context = f"We have a plan with {len(plan)} steps"
            should_proceed = decision_maker.should_proceed(context)

            if should_proceed:
                self.logger.info("AI approved - executing plan")
                print("✓ AI recommends proceeding with the plan\n")
            else:
                self.logger.warning("AI suggested caution")
                print("⚠ AI suggests reviewing the plan before proceeding\n")

        except Exception as e:
            self.logger.error(f"AI workflow error: {e}")
            print(f"Error in AI workflow: {e}")
            print("Falling back to non-AI workflow...")
            self._run_without_ai()

    def _run_without_ai(self):
        """Run workflow without AI features."""
        print("\nRunning standard workflow...")
        print("1. Initialize")
        print("2. Process data")
        print("3. Generate output")
        print("4. Complete")


def main():
    """Run the full workflow examples."""
    print("=" * 60)
    print("Full Workflow Example")
    print("=" * 60)
    print()

    # Example 1: Basic workflow with retry and timing
    print("Example 1: Basic Workflow with Retry and Timing")
    print("-" * 60)
    task1 = WorkflowTask("data_processing")
    task1.execute()
    print()

    # Example 2: AI-enhanced workflow
    print("\nExample 2: AI-Enhanced Workflow")
    print("-" * 60)
    task2 = AIEnhancedWorkflow(
        "ai_workflow",
        config={
            "goal": "Automate data analysis and report generation",
            "constraints": [
                "Must complete within 10 minutes",
                "Use minimal computational resources",
                "Provide clear, actionable insights",
            ],
        },
    )
    task2.execute()

    print("\n" + "=" * 60)
    print("All workflows completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
