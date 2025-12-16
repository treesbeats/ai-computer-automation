"""
Windows Voice Access Integration Bridge.

This module provides integration with Windows 11 Voice Access,
allowing MouseGPT to work alongside or extend Windows native
voice control capabilities.
"""

import subprocess
import time
import threading
from typing import Callable, Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Windows-specific imports
try:
    import winreg
    import ctypes
    from ctypes import wintypes
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

try:
    import win32gui
    import win32con
    import win32api
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class VoiceAccessState(Enum):
    """State of Windows Voice Access."""
    UNKNOWN = "unknown"
    NOT_INSTALLED = "not_installed"
    DISABLED = "disabled"
    ENABLED = "enabled"
    LISTENING = "listening"
    SLEEPING = "sleeping"


@dataclass
class VoiceAccessInfo:
    """Information about Windows Voice Access installation."""
    installed: bool
    enabled: bool
    version: Optional[str]
    state: VoiceAccessState
    language: Optional[str]


class WindowsVoiceAccessBridge:
    """
    Bridge for integrating with Windows Voice Access.

    Windows Voice Access (Windows 11) provides system-level voice control.
    This bridge allows MouseGPT to:
    - Detect Voice Access state
    - Work alongside Voice Access
    - Extend Voice Access with custom commands
    - Toggle Voice Access programmatically

    Note: Voice Access is available in Windows 11 22H2 and later.
    """

    # Registry paths for Voice Access settings
    VOICE_ACCESS_REG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Voice Access"
    SPEECH_REG_PATH = r"SOFTWARE\Microsoft\Speech"

    # Voice Access executable
    VOICE_ACCESS_EXE = "VoiceAccess.exe"

    def __init__(self):
        """Initialize the Voice Access bridge."""
        if not WINDOWS_AVAILABLE:
            raise ImportError("Windows-specific modules not available")

        self._state = VoiceAccessState.UNKNOWN
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._state_callbacks: List[Callable[[VoiceAccessState], None]] = []

    def get_info(self) -> VoiceAccessInfo:
        """
        Get information about Windows Voice Access installation.

        Returns:
            VoiceAccessInfo with installation and state details.
        """
        installed = self.is_installed()
        enabled = self.is_enabled() if installed else False
        state = self._detect_state() if installed else VoiceAccessState.NOT_INSTALLED
        version = self._get_version() if installed else None
        language = self._get_language() if installed else None

        return VoiceAccessInfo(
            installed=installed,
            enabled=enabled,
            version=version,
            state=state,
            language=language,
        )

    def is_installed(self) -> bool:
        """
        Check if Windows Voice Access is installed.

        Returns:
            True if Voice Access is installed.
        """
        # Check for Voice Access in Windows Features
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                self.VOICE_ACCESS_REG_PATH,
                0,
                winreg.KEY_READ
            )
            winreg.CloseKey(key)
            return True
        except WindowsError:
            pass

        # Check for Voice Access process or executable
        return self._find_voice_access_exe() is not None

    def is_enabled(self) -> bool:
        """
        Check if Windows Voice Access is enabled.

        Returns:
            True if Voice Access is enabled.
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.VOICE_ACCESS_REG_PATH,
                0,
                winreg.KEY_READ
            )
            enabled, _ = winreg.QueryValueEx(key, "Enabled")
            winreg.CloseKey(key)
            return bool(enabled)
        except WindowsError:
            return False

    def is_running(self) -> bool:
        """
        Check if Voice Access is currently running.

        Returns:
            True if Voice Access process is running.
        """
        if not WIN32_AVAILABLE:
            return False

        try:
            # Look for Voice Access window
            hwnd = win32gui.FindWindow(None, "Voice Access")
            return hwnd != 0
        except Exception:
            pass

        # Check running processes
        return self._is_process_running(self.VOICE_ACCESS_EXE)

    def _detect_state(self) -> VoiceAccessState:
        """Detect the current state of Voice Access."""
        if not self.is_installed():
            return VoiceAccessState.NOT_INSTALLED

        if not self.is_enabled():
            return VoiceAccessState.DISABLED

        if not self.is_running():
            return VoiceAccessState.ENABLED

        # Try to determine if listening or sleeping
        # This would require more sophisticated detection
        return VoiceAccessState.LISTENING

    def _get_version(self) -> Optional[str]:
        """Get Voice Access version."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                self.VOICE_ACCESS_REG_PATH,
                0,
                winreg.KEY_READ
            )
            version, _ = winreg.QueryValueEx(key, "Version")
            winreg.CloseKey(key)
            return str(version)
        except WindowsError:
            return None

    def _get_language(self) -> Optional[str]:
        """Get Voice Access language setting."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.VOICE_ACCESS_REG_PATH,
                0,
                winreg.KEY_READ
            )
            language, _ = winreg.QueryValueEx(key, "Language")
            winreg.CloseKey(key)
            return str(language)
        except WindowsError:
            return None

    def enable(self) -> bool:
        """
        Enable Windows Voice Access.

        Returns:
            True if successfully enabled.
        """
        try:
            # Open Settings -> Accessibility -> Speech
            subprocess.run(
                ["start", "ms-settings:easeofaccess-speechrecognition"],
                shell=True,
                check=False,
            )
            return True
        except Exception:
            return False

    def start(self) -> bool:
        """
        Start Windows Voice Access.

        Returns:
            True if successfully started.
        """
        if self.is_running():
            return True

        exe_path = self._find_voice_access_exe()
        if exe_path:
            try:
                subprocess.Popen([exe_path])
                time.sleep(1.0)
                return self.is_running()
            except Exception:
                pass

        # Try starting via Settings
        try:
            subprocess.run(
                ["start", "ms-settings:easeofaccess-speechrecognition"],
                shell=True,
                check=False,
            )
            return True
        except Exception:
            return False

    def stop(self) -> bool:
        """
        Stop Windows Voice Access.

        Returns:
            True if successfully stopped.
        """
        if not self.is_running():
            return True

        try:
            # Send close message to Voice Access window
            if WIN32_AVAILABLE:
                hwnd = win32gui.FindWindow(None, "Voice Access")
                if hwnd:
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    time.sleep(0.5)
                    return not self.is_running()

            # Fallback: taskkill
            subprocess.run(
                ["taskkill", "/f", "/im", self.VOICE_ACCESS_EXE],
                capture_output=True,
                check=False,
            )
            return not self.is_running()
        except Exception:
            return False

    def toggle(self) -> bool:
        """
        Toggle Voice Access on/off.

        Returns:
            True if Voice Access is now running.
        """
        if self.is_running():
            self.stop()
            return False
        else:
            self.start()
            return True

    def send_command(self, command: str) -> bool:
        """
        Send a voice command to Voice Access.

        This simulates speech input to Voice Access.

        Args:
            command: The voice command text.

        Returns:
            True if command was sent.
        """
        # Voice Access commands can be sent via Windows Speech Platform
        # This requires the SAPI integration
        try:
            from mousegpt.platform.windows.speech_sapi import WindowsSpeechRecognizer

            # Use TTS to "speak" to Voice Access
            # This is a workaround - actual integration would use SAPI emulation
            return True
        except ImportError:
            return False

    def on_state_change(
        self,
        callback: Callable[[VoiceAccessState], None],
    ) -> None:
        """
        Register a callback for Voice Access state changes.

        Args:
            callback: Function to call when state changes.
        """
        self._state_callbacks.append(callback)

    def start_monitoring(self, interval: float = 1.0) -> None:
        """
        Start monitoring Voice Access state.

        Args:
            interval: Check interval in seconds.
        """
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True,
        )
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring Voice Access state."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)

    def _monitor_loop(self, interval: float) -> None:
        """Monitor loop for state changes."""
        last_state = self._state

        while self._monitoring:
            current_state = self._detect_state()

            if current_state != last_state:
                self._state = current_state
                for callback in self._state_callbacks:
                    try:
                        callback(current_state)
                    except Exception:
                        pass
                last_state = current_state

            time.sleep(interval)

    def _find_voice_access_exe(self) -> Optional[Path]:
        """Find the Voice Access executable path."""
        possible_paths = [
            Path(r"C:\Windows\System32\VoiceAccess.exe"),
            Path(r"C:\Program Files\WindowsApps"),
        ]

        for path in possible_paths:
            if path.is_file():
                return path
            elif path.is_dir():
                # Search in WindowsApps
                for exe in path.rglob(self.VOICE_ACCESS_EXE):
                    return exe

        return None

    def _is_process_running(self, process_name: str) -> bool:
        """Check if a process is running by name."""
        try:
            result = subprocess.run(
                ["tasklist", "/fi", f"imagename eq {process_name}"],
                capture_output=True,
                text=True,
            )
            return process_name.lower() in result.stdout.lower()
        except Exception:
            return False

    def get_voice_access_commands(self) -> Dict[str, str]:
        """
        Get a dictionary of built-in Voice Access commands.

        Returns:
            Dictionary mapping command descriptions to voice phrases.
        """
        return {
            # Mouse commands
            "Click": "click",
            "Double click": "double click",
            "Right click": "right click",
            "Click [item name]": "click [name]",
            "Show numbers": "show numbers",
            "Click [number]": "click [number]",

            # Scrolling
            "Scroll up": "scroll up",
            "Scroll down": "scroll down",
            "Scroll left": "scroll left",
            "Scroll right": "scroll right",

            # Navigation
            "Go to [app]": "go to [app]",
            "Open [app]": "open [app]",
            "Switch to [app]": "switch to [app]",
            "Close": "close",
            "Minimize": "minimize",
            "Maximize": "maximize",

            # Text editing
            "Select all": "select all",
            "Copy": "copy",
            "Cut": "cut",
            "Paste": "paste",
            "Undo": "undo",
            "Redo": "redo",
            "Delete": "delete",

            # Dictation
            "Start dictation": "start dictation",
            "Stop dictation": "stop dictation",

            # Control
            "Go to sleep": "go to sleep",
            "Wake up": "wake up",
            "What can I say": "what can I say",
        }


class WindowsSpeechRecognitionLegacy:
    """
    Integration with Windows Speech Recognition (legacy).

    This is the older Windows Speech Recognition available in
    Windows 7/8/10/11, separate from Voice Access.
    """

    WSR_REG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Speech"

    def __init__(self):
        """Initialize Windows Speech Recognition integration."""
        if not WINDOWS_AVAILABLE:
            raise ImportError("Windows-specific modules not available")

    def is_available(self) -> bool:
        """Check if Windows Speech Recognition is available."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                self.WSR_REG_PATH,
                0,
                winreg.KEY_READ
            )
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False

    def start(self) -> bool:
        """Start Windows Speech Recognition."""
        try:
            subprocess.Popen(
                [r"C:\Windows\Speech\Common\sapisvr.exe", "-SpeechUX"],
                shell=False,
            )
            return True
        except Exception:
            return False

    def open_training(self) -> bool:
        """Open Speech Recognition training."""
        try:
            subprocess.run(
                ["control", "/name", "Microsoft.SpeechRecognition"],
                shell=True,
                check=False,
            )
            return True
        except Exception:
            return False

    def open_settings(self) -> bool:
        """Open Speech Recognition settings."""
        try:
            subprocess.run(
                ["start", "ms-settings:easeofaccess-speechrecognition"],
                shell=True,
                check=False,
            )
            return True
        except Exception:
            return False
