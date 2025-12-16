"""Windows-specific platform modules for MouseGPT."""

from mousegpt.platform import IS_WINDOWS

if IS_WINDOWS:
    from mousegpt.platform.windows.speech_sapi import WindowsSpeechRecognizer
    from mousegpt.platform.windows.voice_access import WindowsVoiceAccessBridge
    from mousegpt.platform.windows.ui_automation import WindowsUIAutomation
    from mousegpt.platform.windows.accessibility import WindowsAccessibility

    __all__ = [
        "WindowsSpeechRecognizer",
        "WindowsVoiceAccessBridge",
        "WindowsUIAutomation",
        "WindowsAccessibility",
    ]
else:
    __all__ = []
