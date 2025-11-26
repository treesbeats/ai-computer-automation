"""Workflow execution engine."""

import logging
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from ai_automation.workflow.dag import DAG, DAGNode
from ai_automation.core.enhanced_task import EnhancedTask
from ai_automation.exceptions import WorkflowError, WorkflowValidationError

logger = logging.getLogger(__name__)


class Workflow:
    """Represents a workflow of connected tasks."""

    def __init__(self, name: str, description: str = ""):
        """
        Initialize workflow.

        Args:
            name: Workflow name
            description: Optional description
        """
        self.name = name
        self.description = description
        self.dag = DAG()
        self.tasks: Dict[str, EnhancedTask] = {}

    def add_task(
        self,
        task: EnhancedTask,
        task_id: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
    ) -> str:
        """
        Add a task to the workflow.

        Args:
            task: EnhancedTask instance
            task_id: Optional task ID (uses task.task_id if not provided)
            depends_on: Optional list of task IDs this task depends on

        Returns:
            Task ID
        """
        task_id = task_id or task.task_id
        self.tasks[task_id] = task

        # Create DAG node
        node = DAGNode(task_id, task)
        self.dag.add_node(node)

        # Add dependencies
        if depends_on:
            for dep_id in depends_on:
                if dep_id not in self.tasks:
                    raise WorkflowValidationError(
                        f"Dependency {dep_id} not found in workflow",
                        details={"task_id": task_id, "dependency": dep_id},
                    )
                self.dag.add_edge(dep_id, task_id)

            # Update task dependencies
            task.dependencies = depends_on

        logger.info(f"Added task {task.name} to workflow {self.name}")
        return task_id

    def validate(self) -> bool:
        """
        Validate the workflow.

        Returns:
            True if valid

        Raises:
            WorkflowValidationError: If validation fails
        """
        return self.dag.validate()

    def get_execution_order(self) -> List[str]:
        """
        Get task execution order.

        Returns:
            List of task IDs in execution order
        """
        return self.dag.topological_sort()

    def get_execution_levels(self) -> List[List[str]]:
        """
        Get tasks grouped by execution level.

        Returns:
            List of lists of task IDs
        """
        return self.dag.get_execution_levels()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert workflow to dictionary.

        Returns:
            Workflow as dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "tasks": {
                task_id: {
                    "name": task.name,
                    "dependencies": task.dependencies,
                }
                for task_id, task in self.tasks.items()
            },
            "execution_order": self.get_execution_order(),
        }


class WorkflowEngine:
    """Execute workflows with support for parallel execution."""

    def __init__(self, max_workers: int = 4):
        """
        Initialize workflow engine.

        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        logger.info(f"Initialized workflow engine with {max_workers} workers")

    def execute_sequential(
        self,
        workflow: Workflow,
        on_task_complete: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Execute workflow sequentially.

        Args:
            workflow: Workflow to execute
            on_task_complete: Optional callback after each task

        Returns:
            Dictionary with execution results

        Raises:
            WorkflowError: If workflow execution fails
        """
        logger.info(f"Executing workflow '{workflow.name}' sequentially")

        # Validate workflow
        workflow.validate()

        # Get execution order
        order = workflow.get_execution_order()

        results = {}
        failed_tasks = []

        for task_id in order:
            task = workflow.tasks[task_id]
            logger.info(f"Executing task: {task.name}")

            success = task.execute()

            results[task_id] = {
                "task_name": task.name,
                "success": success,
                "result": task.result,
                "error": str(task.error) if task.error else None,
            }

            if not success:
                failed_tasks.append(task_id)
                logger.error(f"Task {task.name} failed, stopping workflow")
                break

            if on_task_complete:
                on_task_complete(task_id, task, success)

        return {
            "workflow_name": workflow.name,
            "total_tasks": len(order),
            "completed_tasks": len(results),
            "failed_tasks": failed_tasks,
            "success": len(failed_tasks) == 0,
            "results": results,
        }

    def execute_parallel(
        self,
        workflow: Workflow,
        on_task_complete: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Execute workflow with parallel execution where possible.

        Args:
            workflow: Workflow to execute
            on_task_complete: Optional callback after each task

        Returns:
            Dictionary with execution results

        Raises:
            WorkflowError: If workflow execution fails
        """
        logger.info(f"Executing workflow '{workflow.name}' with parallelization")

        # Validate workflow
        workflow.validate()

        # Get execution levels
        levels = workflow.get_execution_levels()

        results = {}
        failed_tasks = []

        # Execute each level
        for level_num, level_tasks in enumerate(levels, 1):
            logger.info(
                f"Executing level {level_num}/{len(levels)} with {len(level_tasks)} task(s)"
            )

            # Submit all tasks in this level
            futures = {}
            for task_id in level_tasks:
                task = workflow.tasks[task_id]
                future = self.executor.submit(task.execute)
                futures[future] = (task_id, task)

            # Wait for all tasks in this level to complete
            level_failed = False
            for future in as_completed(futures):
                task_id, task = futures[future]

                try:
                    success = future.result()
                except Exception as e:
                    logger.error(f"Task {task.name} raised exception: {e}")
                    success = False
                    task.error = e

                results[task_id] = {
                    "task_name": task.name,
                    "success": success,
                    "result": task.result,
                    "error": str(task.error) if task.error else None,
                }

                if not success:
                    failed_tasks.append(task_id)
                    level_failed = True

                if on_task_complete:
                    on_task_complete(task_id, task, success)

            # Stop if any task in this level failed
            if level_failed:
                logger.error("Tasks failed in level, stopping workflow")
                break

        return {
            "workflow_name": workflow.name,
            "total_tasks": len(workflow.tasks),
            "completed_tasks": len(results),
            "failed_tasks": failed_tasks,
            "success": len(failed_tasks) == 0,
            "results": results,
        }

    def execute(
        self,
        workflow: Workflow,
        parallel: bool = False,
        on_task_complete: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            workflow: Workflow to execute
            parallel: Whether to use parallel execution
            on_task_complete: Optional callback after each task

        Returns:
            Dictionary with execution results
        """
        if parallel:
            return self.execute_parallel(workflow, on_task_complete)
        else:
            return self.execute_sequential(workflow, on_task_complete)

    def shutdown(self):
        """Shutdown the workflow engine."""
        self.executor.shutdown(wait=True)
        logger.info("Workflow engine shut down")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
