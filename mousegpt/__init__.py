"""
MouseGPT - Voice-controlled computer automation engine.

A complete dictation engine that takes verbal commands and controls
mouse, keyboard, and other inputs on computers and mobile devices.
"""

__version__ = "0.1.0"
__author__ = "MouseGPT Team"

from mousegpt.engine import MouseGPTEngine
from mousegpt.config.settings import Settings

__all__ = ["MouseGPTEngine", "Settings", "__version__"]
