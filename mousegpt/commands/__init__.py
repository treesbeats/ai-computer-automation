"""Command parsing and registry modules."""

from mousegpt.commands.parser import CommandParser
from mousegpt.commands.registry import CommandRegistry, Command
from mousegpt.commands.smart import (
    SmartCommandProcessor,
    understand_command,
    find_best_app_match,
    find_folder_path,
    APP_ALIASES,
    FOLDER_ALIASES,
)

__all__ = [
    "CommandParser",
    "CommandRegistry",
    "Command",
    "SmartCommandProcessor",
    "understand_command",
    "find_best_app_match",
    "find_folder_path",
    "APP_ALIASES",
    "FOLDER_ALIASES",
]
