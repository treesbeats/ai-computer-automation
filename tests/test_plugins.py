"""Tests for plugin system."""

import pytest
from ai_automation.plugins import Plugin, PluginRegistry, PluginLoader
from ai_automation.exceptions import PluginError


class TestPlugin(Plugin):
    """Test plugin implementation."""

    def initialize(self, config=None):
        """Initialize plugin."""
        self.config = config or {}
        self.initialized = True

    def execute(self, *args, **kwargs):
        """Execute plugin."""
        return f"Executed with args={args}, kwargs={kwargs}"


class TestPluginRegistry:
    """Tests for PluginRegistry."""

    def test_create_registry(self):
        """Test registry creation."""
        registry = PluginRegistry()
        assert isinstance(registry, PluginRegistry)

    def test_register_plugin(self):
        """Test plugin registration."""
        registry = PluginRegistry()
        plugin = TestPlugin("test_plugin")
        registry.register(plugin)

        assert "test_plugin" in registry.list_plugins()

    def test_get_plugin(self):
        """Test getting plugin."""
        registry = PluginRegistry()
        plugin = TestPlugin("test_plugin")
        registry.register(plugin)

        retrieved = registry.get("test_plugin")
        assert retrieved == plugin

    def test_execute_plugin(self):
        """Test plugin execution."""
        registry = PluginRegistry()
        plugin = TestPlugin("test_plugin")
        registry.register(plugin)

        result = registry.execute_plugin("test_plugin", "arg1", key="value")
        assert "arg1" in result
        assert "key" in result

    def test_unregister_plugin(self):
        """Test plugin unregistration."""
        registry = PluginRegistry()
        plugin = TestPlugin("test_plugin")
        registry.register(plugin)

        registry.unregister("test_plugin")
        assert "test_plugin" not in registry.list_plugins()

    def test_enable_disable_plugin(self):
        """Test enabling/disabling plugins."""
        registry = PluginRegistry()
        plugin = TestPlugin("test_plugin")
        registry.register(plugin)

        registry.disable_plugin("test_plugin")
        assert not plugin.enabled

        registry.enable_plugin("test_plugin")
        assert plugin.enabled

    def test_hooks(self):
        """Test hook system."""
        registry = PluginRegistry()
        results = []

        def callback(value):
            results.append(value)

        registry.register_hook("test_hook", callback)
        registry.trigger_hook("test_hook", "test_value")

        assert "test_value" in results
