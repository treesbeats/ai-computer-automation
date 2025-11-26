"""AI Computer Automation - Main package."""

__version__ = "0.2.0"
__author__ = "AI Computer Automation Team"
__license__ = "MIT"

# Core
from ai_automation.core.task import AutomationTask
from ai_automation.core.enhanced_task import EnhancedTask
from ai_automation.core.state import TaskState, TaskHistory, StateManager

# Workflow
from ai_automation.workflow import Workflow, WorkflowEngine, DAG, DAGNode

# AI
from ai_automation.ai import (
    AIClient,
    OpenAIClient,
    AnthropicClient,
    create_ai_client,
    AIDecisionMaker,
)

# GUI
from ai_automation.gui import GUIAutomation

# Vision
from ai_automation.vision import VisionDetector, OCRReader

# Web
from ai_automation.web import BrowserAutomation

# Plugins
from ai_automation.plugins import Plugin, PluginRegistry, PluginLoader

# Utils
from ai_automation.utils import (
    setup_logger,
    get_logger,
    Config,
    load_config,
    retry,
    timer,
    RateLimiter,
)

# Exceptions
from ai_automation.exceptions import (
    AutomationError,
    TaskError,
    AIError,
    GUIError,
    VisionError,
    WorkflowError,
    PluginError,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "AutomationTask",
    "EnhancedTask",
    "TaskState",
    "TaskHistory",
    "StateManager",
    # Workflow
    "Workflow",
    "WorkflowEngine",
    "DAG",
    "DAGNode",
    # AI
    "AIClient",
    "OpenAIClient",
    "AnthropicClient",
    "create_ai_client",
    "AIDecisionMaker",
    # GUI
    "GUIAutomation",
    # Vision
    "VisionDetector",
    "OCRReader",
    # Web
    "BrowserAutomation",
    # Plugins
    "Plugin",
    "PluginRegistry",
    "PluginLoader",
    # Utils
    "setup_logger",
    "get_logger",
    "Config",
    "load_config",
    "retry",
    "timer",
    "RateLimiter",
    # Exceptions
    "AutomationError",
    "TaskError",
    "AIError",
    "GUIError",
    "VisionError",
    "WorkflowError",
    "PluginError",
]
