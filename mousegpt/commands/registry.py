"""Command registry for MouseGPT."""

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum


class CommandCategory(str, Enum):
    """Categories of commands."""
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    SCREEN = "screen"
    SYSTEM = "system"
    APPLICATION = "application"
    CUSTOM = "custom"


@dataclass
class CommandParameter:
    """Parameter definition for a command."""
    name: str
    type: type
    required: bool = True
    default: Any = None
    description: str = ""


@dataclass
class Command:
    """Definition of a voice command."""
    name: str
    patterns: list[str]
    handler: Callable[..., Any]
    category: CommandCategory
    description: str = ""
    parameters: list[CommandParameter] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)

    def matches(self, text: str) -> Optional[dict]:
        """
        Check if the text matches this command.

        Args:
            text: Text to match against patterns.

        Returns:
            Dictionary of extracted parameters or None if no match.
        """
        text_lower = text.lower().strip()

        for pattern in self.patterns:
            match = re.match(pattern, text_lower, re.IGNORECASE)
            if match:
                return match.groupdict()

        # Check aliases
        for alias in self.aliases:
            if alias.lower() in text_lower:
                return {}

        return None


class CommandRegistry:
    """
    Registry for voice commands.

    Manages command registration and lookup for the dictation engine.
    """

    def __init__(self):
        """Initialize the command registry."""
        self._commands: dict[str, Command] = {}
        self._categories: dict[CommandCategory, list[str]] = {
            cat: [] for cat in CommandCategory
        }

    def register(self, command: Command) -> None:
        """
        Register a command.

        Args:
            command: Command to register.
        """
        if command.name in self._commands:
            raise ValueError(f"Command '{command.name}' already registered")

        self._commands[command.name] = command
        self._categories[command.category].append(command.name)

    def unregister(self, name: str) -> None:
        """
        Unregister a command by name.

        Args:
            name: Name of the command to unregister.
        """
        if name not in self._commands:
            return

        command = self._commands[name]
        self._categories[command.category].remove(name)
        del self._commands[name]

    def get(self, name: str) -> Optional[Command]:
        """
        Get a command by name.

        Args:
            name: Name of the command.

        Returns:
            Command or None if not found.
        """
        return self._commands.get(name)

    def find_match(self, text: str) -> Optional[tuple[Command, dict]]:
        """
        Find a command that matches the given text.

        Args:
            text: Text to match against commands.

        Returns:
            Tuple of (Command, parameters) or None if no match.
        """
        for command in self._commands.values():
            params = command.matches(text)
            if params is not None:
                return command, params

        return None

    def list_commands(
        self,
        category: Optional[CommandCategory] = None,
    ) -> list[Command]:
        """
        List all registered commands.

        Args:
            category: Optional category to filter by.

        Returns:
            List of commands.
        """
        if category is not None:
            return [
                self._commands[name]
                for name in self._categories[category]
            ]

        return list(self._commands.values())

    def command(
        self,
        name: str,
        patterns: list[str],
        category: CommandCategory = CommandCategory.CUSTOM,
        description: str = "",
        parameters: Optional[list[CommandParameter]] = None,
        examples: Optional[list[str]] = None,
        aliases: Optional[list[str]] = None,
    ) -> Callable:
        """
        Decorator to register a command handler.

        Args:
            name: Command name.
            patterns: Regex patterns to match.
            category: Command category.
            description: Command description.
            parameters: Parameter definitions.
            examples: Example usages.
            aliases: Alternative names.

        Returns:
            Decorator function.
        """
        def decorator(func: Callable) -> Callable:
            cmd = Command(
                name=name,
                patterns=patterns,
                handler=func,
                category=category,
                description=description,
                parameters=parameters or [],
                examples=examples or [],
                aliases=aliases or [],
            )
            self.register(cmd)
            return func

        return decorator


# Global command registry instance
_registry: Optional[CommandRegistry] = None


def get_registry() -> CommandRegistry:
    """Get the global command registry."""
    global _registry
    if _registry is None:
        _registry = CommandRegistry()
    return _registry
