"""Voice-controlled automation toolkit for Windows."""

from .app import VoiceAutomationApp

try:  # pragma: no cover - optional dependency on Tk
    from .dashboard import VoiceAssistantDashboard
except Exception:  # noqa: BLE001 - importing tkinter can fail on headless systems
    VoiceAssistantDashboard = None  # type: ignore[assignment]

__all__ = ["VoiceAutomationApp", "VoiceAssistantDashboard"]
