"""
Workflow Example

Demonstrates using the workflow engine with DAG-based task execution.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_automation.core.enhanced_task import EnhancedTask
from ai_automation.workflow import Workflow, WorkflowEngine
from ai_automation.utils import setup_logger


# Define some example tasks
class DataFetchTask(EnhancedTask):
    """Task that simulates fetching data."""

    def _run(self):
        print(f"[{self.name}] Fetching data...")
        import time
        time.sleep(0.5)
        self.result = {"data": [1, 2, 3, 4, 5]}
        print(f"[{self.name}] Data fetched: {self.result}")


class DataProcessTask(EnhancedTask):
    """Task that processes data."""

    def _run(self):
        print(f"[{self.name}] Processing data...")
        import time
        time.sleep(0.3)
        # In a real scenario, would get data from previous task
        self.result = {"processed": True}
        print(f"[{self.name}] Data processed")


class DataValidateTask(EnhancedTask):
    """Task that validates data."""

    def _run(self):
        print(f"[{self.name}] Validating data...")
        import time
        time.sleep(0.2)
        self.result = {"valid": True}
        print(f"[{self.name}] Data validated")


class ReportGenerateTask(EnhancedTask):
    """Task that generates a report."""

    def _run(self):
        print(f"[{self.name}] Generating report...")
        import time
        time.sleep(0.4)
        self.result = {"report": "report.pdf"}
        print(f"[{self.name}] Report generated")


class NotificationTask(EnhancedTask):
    """Task that sends a notification."""

    def _run(self):
        print(f"[{self.name}] Sending notification...")
        import time
        time.sleep(0.1)
        self.result = {"sent": True}
        print(f"[{self.name}] Notification sent")


def example_sequential_workflow():
    """Example of sequential workflow execution."""
    print("=" * 70)
    print("Sequential Workflow Example")
    print("=" * 70)
    print()

    # Create workflow
    workflow = Workflow(
        name="data_pipeline",
        description="Sequential data processing pipeline"
    )

    # Create tasks
    fetch_task = DataFetchTask("fetch_data")
    process_task = DataProcessTask("process_data")
    report_task = ReportGenerateTask("generate_report")
    notify_task = NotificationTask("send_notification")

    # Add tasks with dependencies
    workflow.add_task(fetch_task)
    workflow.add_task(process_task, depends_on=[fetch_task.task_id])
    workflow.add_task(report_task, depends_on=[process_task.task_id])
    workflow.add_task(notify_task, depends_on=[report_task.task_id])

    # Validate workflow
    print("Validating workflow...")
    workflow.validate()
    print("✓ Workflow is valid\n")

    # Show execution order
    print("Execution order:")
    for i, task_id in enumerate(workflow.get_execution_order(), 1):
        task = workflow.tasks[task_id]
        print(f"  {i}. {task.name}")
    print()

    # Execute workflow
    engine = WorkflowEngine(max_workers=2)
    results = engine.execute(workflow, parallel=False)

    # Print results
    print("\n" + "=" * 70)
    print("Workflow Results:")
    print("=" * 70)
    print(f"Success: {results['success']}")
    print(f"Completed: {results['completed_tasks']}/{results['total_tasks']} tasks")
    print()


def example_parallel_workflow():
    """Example of parallel workflow execution."""
    print("\n" + "=" * 70)
    print("Parallel Workflow Example")
    print("=" * 70)
    print()

    # Create workflow with parallel tasks
    workflow = Workflow(
        name="parallel_pipeline",
        description="Data processing with parallel validation"
    )

    # Create tasks
    fetch_task = DataFetchTask("fetch_data")
    process_task = DataProcessTask("process_data")
    validate_task = DataValidateTask("validate_data")
    report_task = ReportGenerateTask("generate_report")
    notify_task = NotificationTask("send_notification")

    # Add tasks with dependencies
    # Fetch first
    workflow.add_task(fetch_task)

    # Process and validate can run in parallel (both depend on fetch)
    workflow.add_task(process_task, depends_on=[fetch_task.task_id])
    workflow.add_task(validate_task, depends_on=[fetch_task.task_id])

    # Report depends on both process and validate
    workflow.add_task(
        report_task,
        depends_on=[process_task.task_id, validate_task.task_id]
    )

    # Notify at the end
    workflow.add_task(notify_task, depends_on=[report_task.task_id])

    # Validate workflow
    print("Validating workflow...")
    workflow.validate()
    print("✓ Workflow is valid\n")

    # Show execution levels (for parallel execution)
    print("Execution levels (tasks in same level run in parallel):")
    for i, level in enumerate(workflow.get_execution_levels(), 1):
        tasks = [workflow.tasks[tid].name for tid in level]
        print(f"  Level {i}: {', '.join(tasks)}")
    print()

    # Execute workflow with parallelization
    engine = WorkflowEngine(max_workers=4)

    def on_task_complete(task_id, task, success):
        """Callback after each task completes."""
        status = "✓" if success else "✗"
        print(f"    {status} Task '{task.name}' completed")

    print("Executing workflow with parallelization:\n")
    results = engine.execute(workflow, parallel=True, on_task_complete=on_task_complete)

    # Print results
    print("\n" + "=" * 70)
    print("Workflow Results:")
    print("=" * 70)
    print(f"Success: {results['success']}")
    print(f"Completed: {results['completed_tasks']}/{results['total_tasks']} tasks")

    if results['failed_tasks']:
        print(f"Failed tasks: {', '.join(results['failed_tasks'])}")
    print()


def main():
    """Run workflow examples."""
    # Setup logging
    setup_logger("workflow_example", level="INFO")

    # Run examples
    example_sequential_workflow()
    example_parallel_workflow()

    print("\n" + "=" * 70)
    print("All workflow examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
