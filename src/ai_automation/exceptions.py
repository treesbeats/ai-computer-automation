"""Custom exceptions for AI Computer Automation."""


class AutomationError(Exception):
    """Base exception for all automation errors."""

    def __init__(self, message: str, details: dict = None):
        """
        Initialize automation error.

        Args:
            message: Error message
            details: Optional dictionary with error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        """String representation with details."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class TaskError(AutomationError):
    """Base exception for task-related errors."""

    pass


class TaskExecutionError(TaskError):
    """Error during task execution."""

    pass


class TaskTimeoutError(TaskError):
    """Task execution timeout."""

    pass


class TaskDependencyError(TaskError):
    """Task dependency not satisfied."""

    pass


class TaskValidationError(TaskError):
    """Task configuration validation error."""

    pass


class AIError(AutomationError):
    """Base exception for AI-related errors."""

    pass


class AIClientError(AIError):
    """AI client initialization or configuration error."""

    pass


class AIResponseError(AIError):
    """Unexpected or invalid AI response."""

    pass


class AIRateLimitError(AIError):
    """AI API rate limit exceeded."""

    pass


class GUIError(AutomationError):
    """Base exception for GUI automation errors."""

    pass


class ElementNotFoundError(GUIError):
    """GUI element not found on screen."""

    pass


class GUIOperationError(GUIError):
    """GUI operation failed."""

    pass


class VisionError(AutomationError):
    """Base exception for computer vision errors."""

    pass


class ImageNotFoundError(VisionError):
    """Image file not found."""

    pass


class TemplateMatchError(VisionError):
    """Template matching failed."""

    pass


class OCRError(VisionError):
    """OCR operation failed."""

    pass


class ConfigurationError(AutomationError):
    """Configuration error."""

    pass


class PluginError(AutomationError):
    """Plugin loading or execution error."""

    pass


class WorkflowError(AutomationError):
    """Workflow execution error."""

    pass


class WorkflowValidationError(WorkflowError):
    """Workflow validation error (e.g., circular dependencies)."""

    pass


class RetryExhaustedError(AutomationError):
    """All retry attempts exhausted."""

    def __init__(self, message: str, attempts: int, last_error: Exception):
        """
        Initialize retry exhausted error.

        Args:
            message: Error message
            attempts: Number of attempts made
            last_error: The last exception that occurred
        """
        super().__init__(message, {"attempts": attempts})
        self.attempts = attempts
        self.last_error = last_error

    def __str__(self):
        """String representation."""
        return f"{self.message} after {self.attempts} attempts. Last error: {self.last_error}"
