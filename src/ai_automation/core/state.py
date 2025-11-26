"""Task state management."""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaskState(Enum):
    """Task execution states."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskHistory:
    """Track task execution history."""

    def __init__(self):
        """Initialize task history."""
        self.executions = []

    def record_execution(
        self,
        state: TaskState,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        error: Optional[Exception] = None,
        result: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a task execution.

        Args:
            state: Final state of execution
            start_time: When execution started
            end_time: When execution ended
            error: Exception if failed
            result: Result if successful
            metadata: Additional metadata
        """
        execution = {
            "state": state,
            "start_time": start_time,
            "end_time": end_time,
            "duration": (end_time - start_time).total_seconds() if end_time else None,
            "error": str(error) if error else None,
            "error_type": type(error).__name__ if error else None,
            "result": result,
            "metadata": metadata or {},
        }
        self.executions.append(execution)
        logger.debug(f"Recorded execution: {state.value}")

    def get_last_execution(self) -> Optional[Dict[str, Any]]:
        """
        Get the last execution record.

        Returns:
            Last execution dictionary or None
        """
        return self.executions[-1] if self.executions else None

    def get_execution_count(self) -> int:
        """
        Get total number of executions.

        Returns:
            Execution count
        """
        return len(self.executions)

    def get_successful_count(self) -> int:
        """
        Get number of successful executions.

        Returns:
            Success count
        """
        return sum(1 for e in self.executions if e["state"] == TaskState.COMPLETED)

    def get_failed_count(self) -> int:
        """
        Get number of failed executions.

        Returns:
            Failure count
        """
        return sum(1 for e in self.executions if e["state"] == TaskState.FAILED)

    def get_average_duration(self) -> Optional[float]:
        """
        Get average execution duration.

        Returns:
            Average duration in seconds or None
        """
        durations = [e["duration"] for e in self.executions if e["duration"] is not None]
        return sum(durations) / len(durations) if durations else None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert history to dictionary.

        Returns:
            History as dictionary
        """
        return {
            "total_executions": self.get_execution_count(),
            "successful": self.get_successful_count(),
            "failed": self.get_failed_count(),
            "average_duration": self.get_average_duration(),
            "executions": [
                {
                    "state": e["state"].value if isinstance(e["state"], TaskState) else e["state"],
                    "start_time": e["start_time"].isoformat() if e["start_time"] else None,
                    "end_time": e["end_time"].isoformat() if e["end_time"] else None,
                    "duration": e["duration"],
                    "error": e["error"],
                    "error_type": e["error_type"],
                }
                for e in self.executions
            ],
        }


class StateManager:
    """Manage task states."""

    def __init__(self):
        """Initialize state manager."""
        self.tasks = {}

    def set_state(self, task_id: str, state: TaskState, metadata: Optional[Dict] = None) -> None:
        """
        Set task state.

        Args:
            task_id: Task identifier
            state: New state
            metadata: Optional metadata
        """
        if task_id not in self.tasks:
            self.tasks[task_id] = {
                "current_state": state,
                "history": TaskHistory(),
                "metadata": metadata or {},
            }
        else:
            self.tasks[task_id]["current_state"] = state
            if metadata:
                self.tasks[task_id]["metadata"].update(metadata)

        logger.debug(f"Task {task_id} state changed to {state.value}")

    def get_state(self, task_id: str) -> Optional[TaskState]:
        """
        Get current task state.

        Args:
            task_id: Task identifier

        Returns:
            Current state or None
        """
        task = self.tasks.get(task_id)
        return task["current_state"] if task else None

    def get_history(self, task_id: str) -> Optional[TaskHistory]:
        """
        Get task history.

        Args:
            task_id: Task identifier

        Returns:
            TaskHistory object or None
        """
        task = self.tasks.get(task_id)
        return task["history"] if task else None

    def clear_task(self, task_id: str) -> None:
        """
        Clear task from state manager.

        Args:
            task_id: Task identifier
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.debug(f"Cleared task {task_id}")

    def get_all_tasks(self) -> Dict[str, Dict]:
        """
        Get all tasks and their states.

        Returns:
            Dictionary of all tasks
        """
        return {
            task_id: {
                "state": task["current_state"].value,
                "metadata": task["metadata"],
            }
            for task_id, task in self.tasks.items()
        }
