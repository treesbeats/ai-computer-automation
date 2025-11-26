"""Tests for core automation functionality."""

import pytest
from ai_automation.core.task import AutomationTask


class TestAutomationTask:
    """Tests for AutomationTask class."""

    def test_task_initialization(self):
        """Test that a task can be initialized."""
        task = AutomationTask("test_task")
        assert task.name == "test_task"
        assert task.config == {}

    def test_task_initialization_with_config(self):
        """Test task initialization with configuration."""
        config = {"key": "value"}
        task = AutomationTask("test_task", config=config)
        assert task.name == "test_task"
        assert task.config == config

    def test_task_execute_not_implemented(self):
        """Test that execute fails when _run is not implemented."""
        task = AutomationTask("test_task")
        result = task.execute()
        assert result is False

    def test_custom_task_execution(self):
        """Test execution of a custom task."""

        class CustomTask(AutomationTask):
            def _run(self):
                self.executed = True

        task = CustomTask("custom_task")
        result = task.execute()
        assert result is True
        assert hasattr(task, "executed")
        assert task.executed is True

    def test_task_execution_error_handling(self):
        """Test that task execution handles errors gracefully."""

        class FailingTask(AutomationTask):
            def _run(self):
                raise ValueError("Test error")

        task = FailingTask("failing_task")
        result = task.execute()
        assert result is False
