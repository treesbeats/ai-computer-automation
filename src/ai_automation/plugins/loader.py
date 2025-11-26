"""Plugin loader for dynamic plugin loading."""

import importlib
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import sys

from ai_automation.plugins.registry import Plugin, PluginRegistry
from ai_automation.exceptions import PluginError

logger = logging.getLogger(__name__)


class PluginLoader:
    """Load plugins dynamically from directories."""

    def __init__(self, registry: PluginRegistry):
        """
        Initialize plugin loader.

        Args:
            registry: PluginRegistry instance
        """
        self.registry = registry
        logger.info("Plugin loader initialized")

    def load_from_directory(
        self,
        directory: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Load all plugins from a directory.

        Args:
            directory: Directory path containing plugins
            config: Optional configuration for plugins

        Returns:
            List of loaded plugin names
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            raise PluginError(
                f"Plugin directory not found: {directory}",
                details={"directory": directory},
            )

        if not dir_path.is_dir():
            raise PluginError(
                f"Path is not a directory: {directory}",
                details={"directory": directory},
            )

        loaded_plugins = []

        # Add directory to Python path
        if str(dir_path) not in sys.path:
            sys.path.insert(0, str(dir_path))

        # Find all Python files
        for py_file in dir_path.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                plugin_name = self.load_from_file(str(py_file), config)
                if plugin_name:
                    loaded_plugins.append(plugin_name)
            except Exception as e:
                logger.error(f"Failed to load plugin from {py_file}: {e}")

        logger.info(f"Loaded {len(loaded_plugins)} plugins from {directory}")
        return loaded_plugins

    def load_from_file(
        self,
        filepath: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Load a plugin from a Python file.

        Args:
            filepath: Path to Python file
            config: Optional configuration for plugin

        Returns:
            Plugin name if loaded, None otherwise
        """
        file_path = Path(filepath)

        if not file_path.exists():
            raise PluginError(
                f"Plugin file not found: {filepath}",
                details={"filepath": filepath},
            )

        # Get module name from filename
        module_name = file_path.stem

        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise PluginError(f"Cannot load module from {filepath}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find Plugin subclasses in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                # Check if it's a Plugin subclass (but not Plugin itself)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, Plugin)
                    and attr is not Plugin
                ):
                    # Instantiate and register the plugin
                    plugin = attr()
                    self.registry.register(plugin, config)

                    logger.info(f"Loaded plugin: {plugin.name} from {filepath}")
                    return plugin.name

            logger.warning(f"No Plugin subclass found in {filepath}")
            return None

        except Exception as e:
            logger.error(f"Error loading plugin from {filepath}: {e}")
            raise PluginError(
                f"Failed to load plugin from {filepath}: {e}",
                details={"filepath": filepath, "error": str(e)},
            )

    def load_from_module(
        self,
        module_name: str,
        plugin_class_name: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Load a plugin from a module.

        Args:
            module_name: Module name to import
            plugin_class_name: Plugin class name
            config: Optional configuration for plugin

        Returns:
            Plugin name
        """
        try:
            # Import the module
            module = importlib.import_module(module_name)

            # Get the plugin class
            plugin_class = getattr(module, plugin_class_name)

            if not issubclass(plugin_class, Plugin):
                raise PluginError(
                    f"{plugin_class_name} is not a Plugin subclass",
                    details={"module": module_name, "class": plugin_class_name},
                )

            # Instantiate and register
            plugin = plugin_class()
            self.registry.register(plugin, config)

            logger.info(f"Loaded plugin: {plugin.name} from {module_name}")
            return plugin.name

        except Exception as e:
            logger.error(f"Error loading plugin from module {module_name}: {e}")
            raise PluginError(
                f"Failed to load plugin from module {module_name}: {e}",
                details={"module": module_name, "error": str(e)},
            )
