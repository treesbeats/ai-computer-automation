"""Plugin system for extensibility."""

from ai_automation.plugins.registry import PluginRegistry, Plugin
from ai_automation.plugins.loader import PluginLoader

__all__ = ["PluginRegistry", "Plugin", "PluginLoader"]
