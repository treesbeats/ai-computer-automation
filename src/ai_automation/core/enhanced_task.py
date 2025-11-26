"""Enhanced automation task with advanced features."""

import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from ai_automation.core.task import AutomationTask
from ai_automation.core.state import TaskState, TaskHistory, StateManager
from ai_automation.exceptions import (
    TaskExecutionError,
    TaskTimeoutError,
    TaskDependencyError,
    TaskValidationError,
)
import signal

logger = logging.getLogger(__name__)


class EnhancedTask(AutomationTask):
    """Enhanced automation task with state management, dependencies, and callbacks."""

    # Global state manager shared across all tasks
    _state_manager = StateManager()

    def __init__(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        retry_attempts: int = 0,
        retry_delay: float = 1.0,
        dependencies: Optional[List[str]] = None,
        on_success: Optional[Callable] = None,
        on_failure: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
    ):
        """
        Initialize enhanced task.

        Args:
            name: Task name
            config: Configuration dictionary
            timeout: Maximum execution time in seconds
            retry_attempts: Number of retry attempts on failure
            retry_delay: Delay between retries in seconds
            dependencies: List of task IDs that must complete first
            on_success: Callback function on success
            on_failure: Callback function on failure
            on_complete: Callback function on completion (success or failure)
        """
        super().__init__(name, config)
        self.task_id = str(uuid.uuid4())
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.dependencies = dependencies or []
        self.on_success = on_success
        self.on_failure = on_failure
        self.on_complete = on_complete
        self.history = TaskHistory()
        self.result = None
        self.error = None

        # Initialize state
        EnhancedTask._state_manager.set_state(
            self.task_id,
            TaskState.PENDING,
            metadata={"name": self.name, "created_at": datetime.now().isoformat()},
        )

        logger.info(f"Created enhanced task: {self.name} (ID: {self.task_id})")

    def validate(self) -> bool:
        """
        Validate task configuration.

        Returns:
            True if valid

        Raises:
            TaskValidationError: If validation fails
        """
        # Override in subclass for custom validation
        return True

    def check_dependencies(self) -> bool:
        """
        Check if all dependencies are satisfied.

        Returns:
            True if all dependencies completed successfully

        Raises:
            TaskDependencyError: If dependencies not met
        """
        if not self.dependencies:
            return True

        for dep_id in self.dependencies:
            state = EnhancedTask._state_manager.get_state(dep_id)
            if state != TaskState.COMPLETED:
                raise TaskDependencyError(
                    f"Dependency {dep_id} not completed (current state: {state})",
                    details={"dependency_id": dep_id, "state": state},
                )

        logger.debug(f"All dependencies satisfied for task {self.task_id}")
        return True

    def _timeout_handler(self, signum, frame):
        """Handle timeout signal."""
        raise TaskTimeoutError(
            f"Task {self.name} exceeded timeout of {self.timeout}s",
            details={"task_id": self.task_id, "timeout": self.timeout},
        )

    def execute(self) -> bool:
        """
        Execute the task with enhanced features.

        Returns:
            True if successful, False otherwise
        """
        start_time = datetime.now()

        try:
            # Validate task
            self.validate()

            # Check dependencies
            self.check_dependencies()

            # Set state to running
            EnhancedTask._state_manager.set_state(self.task_id, TaskState.RUNNING)

            # Execute with retry logic
            attempt = 0
            last_error = None

            while attempt <= self.retry_attempts:
                try:
                    if attempt > 0:
                        EnhancedTask._state_manager.set_state(
                            self.task_id, TaskState.RETRYING
                        )
                        logger.info(
                            f"Retrying task {self.name} (attempt {attempt}/{self.retry_attempts})"
                        )
                        import time
                        time.sleep(self.retry_delay * (2 ** (attempt - 1)))  # Exponential backoff

                    # Set timeout if specified
                    if self.timeout:
                        signal.signal(signal.SIGALRM, self._timeout_handler)
                        signal.alarm(self.timeout)

                    # Execute the task
                    self._run()

                    # Cancel timeout
                    if self.timeout:
                        signal.alarm(0)

                    # Success
                    end_time = datetime.now()
                    EnhancedTask._state_manager.set_state(
                        self.task_id, TaskState.COMPLETED
                    )
                    self.history.record_execution(
                        TaskState.COMPLETED,
                        start_time,
                        end_time,
                        result=self.result,
                    )

                    logger.info(
                        f"Task {self.name} completed successfully in {(end_time - start_time).total_seconds():.2f}s"
                    )

                    # Call success callback
                    if self.on_success:
                        try:
                            self.on_success(self)
                        except Exception as e:
                            logger.error(f"Success callback failed: {e}")

                    return True

                except Exception as e:
                    last_error = e
                    attempt += 1

                    if attempt > self.retry_attempts:
                        raise
                    else:
                        logger.warning(f"Task {self.name} failed, will retry: {e}")

        except Exception as e:
            # Failure
            end_time = datetime.now()
            self.error = e
            EnhancedTask._state_manager.set_state(self.task_id, TaskState.FAILED)
            self.history.record_execution(
                TaskState.FAILED, start_time, end_time, error=e
            )

            logger.error(f"Task {self.name} failed: {e}")

            # Call failure callback
            if self.on_failure:
                try:
                    self.on_failure(self, e)
                except Exception as callback_error:
                    logger.error(f"Failure callback failed: {callback_error}")

            return False

        finally:
            # Call complete callback
            if self.on_complete:
                try:
                    self.on_complete(self)
                except Exception as e:
                    logger.error(f"Complete callback failed: {e}")

            # Cancel any remaining timeout
            if self.timeout:
                signal.alarm(0)

    def get_state(self) -> Optional[TaskState]:
        """
        Get current task state.

        Returns:
            Current TaskState
        """
        return EnhancedTask._state_manager.get_state(self.task_id)

    def get_history(self) -> TaskHistory:
        """
        Get task execution history.

        Returns:
            TaskHistory object
        """
        return self.history

    def cancel(self) -> None:
        """Cancel the task."""
        EnhancedTask._state_manager.set_state(self.task_id, TaskState.CANCELLED)
        logger.info(f"Task {self.name} cancelled")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary representation.

        Returns:
            Task as dictionary
        """
        return {
            "task_id": self.task_id,
            "name": self.name,
            "state": self.get_state().value if self.get_state() else None,
            "config": self.config,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "dependencies": self.dependencies,
            "history": self.history.to_dict(),
            "result": str(self.result) if self.result else None,
            "error": str(self.error) if self.error else None,
        }

    @classmethod
    def get_state_manager(cls) -> StateManager:
        """
        Get the global state manager.

        Returns:
            StateManager instance
        """
        return cls._state_manager
