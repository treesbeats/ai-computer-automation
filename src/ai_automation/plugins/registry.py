"""Plugin registry for managing plugins."""

import logging
from typing import Dict, Optional, Callable, Any, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Plugin(ABC):
    """Base class for plugins."""

    def __init__(self, name: str, version: str = "1.0.0"):
        """
        Initialize plugin.

        Args:
            name: Plugin name
            version: Plugin version
        """
        self.name = name
        self.version = version
        self.enabled = True

    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the plugin.

        Args:
            config: Optional configuration dictionary
        """
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the plugin's main functionality.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Plugin execution result
        """
        pass

    def shutdown(self) -> None:
        """Clean up plugin resources."""
        pass

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name={self.name}, version={self.version})"


class PluginRegistry:
    """Registry for managing plugins."""

    def __init__(self):
        """Initialize plugin registry."""
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        logger.info("Plugin registry initialized")

    def register(self, plugin: Plugin, config: Optional[Dict] = None) -> None:
        """
        Register a plugin.

        Args:
            plugin: Plugin instance
            config: Optional configuration for plugin initialization
        """
        if plugin.name in self.plugins:
            logger.warning(f"Plugin {plugin.name} already registered, replacing")

        self.plugins[plugin.name] = plugin

        try:
            plugin.initialize(config)
            logger.info(f"Registered plugin: {plugin.name} v{plugin.version}")
        except Exception as e:
            logger.error(f"Failed to initialize plugin {plugin.name}: {e}")
            del self.plugins[plugin.name]
            raise

    def unregister(self, plugin_name: str) -> None:
        """
        Unregister a plugin.

        Args:
            plugin_name: Name of plugin to unregister
        """
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            try:
                plugin.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down plugin {plugin_name}: {e}")

            del self.plugins[plugin_name]
            logger.info(f"Unregistered plugin: {plugin_name}")
        else:
            logger.warning(f"Plugin {plugin_name} not found")

    def get(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_name)

    def list_plugins(self) -> List[str]:
        """
        List all registered plugins.

        Returns:
            List of plugin names
        """
        return list(self.plugins.keys())

    def execute_plugin(self, plugin_name: str, *args, **kwargs) -> Any:
        """
        Execute a plugin.

        Args:
            plugin_name: Plugin name
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Plugin execution result
        """
        plugin = self.get(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin {plugin_name} not found")

        if not plugin.enabled:
            logger.warning(f"Plugin {plugin_name} is disabled")
            return None

        logger.debug(f"Executing plugin: {plugin_name}")
        return plugin.execute(*args, **kwargs)

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """
        Register a hook callback.

        Args:
            hook_name: Name of the hook
            callback: Callback function
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []

        self.hooks[hook_name].append(callback)
        logger.debug(f"Registered hook: {hook_name}")

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Trigger all callbacks for a hook.

        Args:
            hook_name: Hook name
            *args: Positional arguments for callbacks
            **kwargs: Keyword arguments for callbacks

        Returns:
            List of callback results
        """
        if hook_name not in self.hooks:
            return []

        results = []
        logger.debug(f"Triggering hook: {hook_name}")

        for callback in self.hooks[hook_name]:
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Hook callback failed: {e}")

        return results

    def enable_plugin(self, plugin_name: str) -> None:
        """
        Enable a plugin.

        Args:
            plugin_name: Plugin name
        """
        plugin = self.get(plugin_name)
        if plugin:
            plugin.enabled = True
            logger.info(f"Enabled plugin: {plugin_name}")

    def disable_plugin(self, plugin_name: str) -> None:
        """
        Disable a plugin.

        Args:
            plugin_name: Plugin name
        """
        plugin = self.get(plugin_name)
        if plugin:
            plugin.enabled = False
            logger.info(f"Disabled plugin: {plugin_name}")

    def shutdown_all(self) -> None:
        """Shutdown all plugins."""
        for plugin_name in list(self.plugins.keys()):
            self.unregister(plugin_name)
        logger.info("All plugins shut down")
