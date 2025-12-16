"""Platform-specific modules for MouseGPT."""

import platform

_system = platform.system().lower()

IS_WINDOWS = _system == "windows"
IS_MACOS = _system == "darwin"
IS_LINUX = _system == "linux"


def get_platform_name() -> str:
    """Get the current platform name."""
    if IS_WINDOWS:
        return "windows"
    elif IS_MACOS:
        return "macos"
    elif IS_LINUX:
        return "linux"
    return "unknown"
