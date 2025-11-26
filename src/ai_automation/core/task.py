"""Core automation task implementation."""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AutomationTask:
    """Base class for automation tasks."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize an automation task.

        Args:
            name: The name of the task
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        logger.info(f"Created automation task: {name}")

    def execute(self) -> bool:
        """
        Execute the automation task.

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Executing task: {self.name}")
        try:
            self._run()
            logger.info(f"Task {self.name} completed successfully")
            return True
        except Exception as e:
            logger.error(f"Task {self.name} failed: {e}")
            return False

    def _run(self) -> None:
        """
        Internal method to be overridden by subclasses.

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _run method")
