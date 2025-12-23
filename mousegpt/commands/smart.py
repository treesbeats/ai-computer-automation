"""
Smart command handling for MouseGPT.

Provides intelligent, natural language command understanding including:
- Fuzzy application name matching
- Natural language aliases
- Context-aware commands
- Common folder/location shortcuts
"""

import os
import re
import subprocess
import platform
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass, field
from difflib import SequenceMatcher


@dataclass
class AppInfo:
    """Information about an application."""
    name: str
    aliases: List[str]
    executable: Optional[str] = None
    windows_name: Optional[str] = None  # Window title pattern


# Common application aliases
APP_ALIASES: Dict[str, AppInfo] = {
    # Browsers
    "chrome": AppInfo(
        name="Google Chrome",
        aliases=["chrome", "google chrome", "google", "browser", "the browser", "web browser", "internet"],
        executable="chrome",
        windows_name="Chrome",
    ),
    "firefox": AppInfo(
        name="Firefox",
        aliases=["firefox", "mozilla", "mozilla firefox", "browser", "the browser"],
        executable="firefox",
        windows_name="Firefox",
    ),
    "edge": AppInfo(
        name="Microsoft Edge",
        aliases=["edge", "microsoft edge", "msedge", "browser", "the browser"],
        executable="msedge",
        windows_name="Edge",
    ),
    "ie": AppInfo(
        name="Internet Explorer",
        aliases=["internet explorer", "ie", "explorer", "internet", "the internet"],
        executable="iexplore",
        windows_name="Internet Explorer",
    ),
    "safari": AppInfo(
        name="Safari",
        aliases=["safari", "browser", "the browser"],
        executable="safari",
        windows_name="Safari",
    ),
    "brave": AppInfo(
        name="Brave",
        aliases=["brave", "brave browser"],
        executable="brave",
        windows_name="Brave",
    ),

    # Office
    "word": AppInfo(
        name="Microsoft Word",
        aliases=["word", "microsoft word", "ms word", "document", "word processor"],
        executable="winword",
        windows_name="Word",
    ),
    "excel": AppInfo(
        name="Microsoft Excel",
        aliases=["excel", "microsoft excel", "ms excel", "spreadsheet", "sheets"],
        executable="excel",
        windows_name="Excel",
    ),
    "powerpoint": AppInfo(
        name="Microsoft PowerPoint",
        aliases=["powerpoint", "microsoft powerpoint", "ms powerpoint", "ppt", "slides", "presentation"],
        executable="powerpnt",
        windows_name="PowerPoint",
    ),
    "outlook": AppInfo(
        name="Microsoft Outlook",
        aliases=["outlook", "microsoft outlook", "email", "mail", "my email"],
        executable="outlook",
        windows_name="Outlook",
    ),
    "teams": AppInfo(
        name="Microsoft Teams",
        aliases=["teams", "microsoft teams", "ms teams"],
        executable="teams",
        windows_name="Teams",
    ),

    # System
    "notepad": AppInfo(
        name="Notepad",
        aliases=["notepad", "text editor", "note pad"],
        executable="notepad",
        windows_name="Notepad",
    ),
    "calculator": AppInfo(
        name="Calculator",
        aliases=["calculator", "calc", "the calculator"],
        executable="calc",
        windows_name="Calculator",
    ),
    "explorer": AppInfo(
        name="File Explorer",
        aliases=["file explorer", "explorer", "files", "my files", "file manager", "folders", "my computer", "this pc"],
        executable="explorer",
        windows_name="File Explorer",
    ),
    "settings": AppInfo(
        name="Settings",
        aliases=["settings", "the settings", "system settings", "preferences", "control panel", "options"],
        executable="ms-settings:",
        windows_name="Settings",
    ),
    "terminal": AppInfo(
        name="Terminal",
        aliases=["terminal", "command prompt", "cmd", "powershell", "console", "command line", "shell"],
        executable="cmd",
        windows_name="Command Prompt",
    ),
    "task_manager": AppInfo(
        name="Task Manager",
        aliases=["task manager", "taskmgr", "processes", "running programs"],
        executable="taskmgr",
        windows_name="Task Manager",
    ),

    # Media
    "spotify": AppInfo(
        name="Spotify",
        aliases=["spotify", "music", "my music"],
        executable="spotify",
        windows_name="Spotify",
    ),
    "vlc": AppInfo(
        name="VLC",
        aliases=["vlc", "vlc player", "media player", "video player"],
        executable="vlc",
        windows_name="VLC",
    ),
    "photos": AppInfo(
        name="Photos",
        aliases=["photos", "my photos", "pictures", "gallery", "photo viewer"],
        executable="ms-photos:",
        windows_name="Photos",
    ),

    # Communication
    "discord": AppInfo(
        name="Discord",
        aliases=["discord", "chat"],
        executable="discord",
        windows_name="Discord",
    ),
    "slack": AppInfo(
        name="Slack",
        aliases=["slack", "work chat"],
        executable="slack",
        windows_name="Slack",
    ),
    "zoom": AppInfo(
        name="Zoom",
        aliases=["zoom", "video call", "meeting"],
        executable="zoom",
        windows_name="Zoom",
    ),
    "skype": AppInfo(
        name="Skype",
        aliases=["skype", "video call"],
        executable="skype",
        windows_name="Skype",
    ),

    # Development
    "vscode": AppInfo(
        name="Visual Studio Code",
        aliases=["vscode", "vs code", "visual studio code", "code", "code editor", "editor"],
        executable="code",
        windows_name="Visual Studio Code",
    ),
    "visual_studio": AppInfo(
        name="Visual Studio",
        aliases=["visual studio", "vs", "ide"],
        executable="devenv",
        windows_name="Visual Studio",
    ),
}


# Common folder locations
FOLDER_ALIASES: Dict[str, str] = {
    # User folders
    "documents": "~/Documents",
    "my documents": "~/Documents",
    "downloads": "~/Downloads",
    "my downloads": "~/Downloads",
    "desktop": "~/Desktop",
    "my desktop": "~/Desktop",
    "pictures": "~/Pictures",
    "my pictures": "~/Pictures",
    "photos": "~/Pictures",
    "music": "~/Music",
    "my music": "~/Music",
    "videos": "~/Videos",
    "my videos": "~/Videos",
    "home": "~",
    "my home": "~",
    "home folder": "~",
    "user folder": "~",

    # System folders
    "program files": "C:/Program Files",
    "programs": "C:/Program Files",
    "windows": "C:/Windows",
    "system": "C:/Windows/System32",
    "temp": "~/AppData/Local/Temp",
    "temporary files": "~/AppData/Local/Temp",
    "recycle bin": "shell:RecycleBinFolder",
    "trash": "shell:RecycleBinFolder",

    # Common locations
    "root": "C:/",
    "c drive": "C:/",
    "d drive": "D:/",
}


# Context-aware command aliases
CONTEXT_ALIASES: Dict[str, List[str]] = {
    "close_current": [
        "close this", "close this window", "close it", "close the window",
        "exit this", "quit this", "shut this", "get rid of this"
    ],
    "minimize_current": [
        "minimize this", "minimize this window", "minimize it", "hide this",
        "put this away", "shrink this"
    ],
    "maximize_current": [
        "maximize this", "maximize this window", "maximize it", "full screen",
        "make it bigger", "enlarge this", "expand this"
    ],
    "switch_window": [
        "next window", "switch window", "other window", "alt tab",
        "switch app", "next app"
    ],
    "go_back": [
        "go back", "back", "previous", "previous page", "back button"
    ],
    "go_forward": [
        "go forward", "forward", "next page", "forward button"
    ],
    "refresh": [
        "refresh", "reload", "refresh page", "reload page", "refresh this"
    ],
    "new_tab": [
        "new tab", "open new tab", "open a new tab", "another tab"
    ],
    "close_tab": [
        "close tab", "close this tab", "close the tab"
    ],
    "search": [
        "search for", "look up", "find", "google", "search the web for",
        "look for", "search"
    ],
}


# Action word synonyms
ACTION_SYNONYMS: Dict[str, List[str]] = {
    "open": ["open", "launch", "start", "run", "show", "bring up", "pull up", "fire up", "load"],
    "close": ["close", "quit", "exit", "shut", "kill", "terminate", "end", "stop", "shut down"],
    "minimize": ["minimize", "hide", "shrink", "put away"],
    "maximize": ["maximize", "enlarge", "expand", "full screen", "fullscreen", "make bigger"],
    "switch": ["switch to", "go to", "focus", "bring up", "show me", "take me to"],
    "click": ["click", "tap", "press", "select", "hit", "push"],
    "type": ["type", "write", "enter", "input", "put in", "spell out"],
    "scroll": ["scroll", "move down", "move up", "page"],
}


def fuzzy_match(text: str, pattern: str, threshold: float = 0.6) -> float:
    """
    Calculate fuzzy match score between text and pattern.

    Returns score from 0.0 to 1.0.
    """
    text = text.lower().strip()
    pattern = pattern.lower().strip()

    # Exact match
    if text == pattern:
        return 1.0

    # Contains match
    if pattern in text or text in pattern:
        return 0.9

    # Sequence matching
    return SequenceMatcher(None, text, pattern).ratio()


def find_best_app_match(query: str) -> Optional[Tuple[str, AppInfo, float]]:
    """
    Find the best matching application for a query.

    Returns (app_key, app_info, confidence) or None.
    """
    query = query.lower().strip()
    best_match = None
    best_score = 0.0

    for app_key, app_info in APP_ALIASES.items():
        # Check direct name match
        score = fuzzy_match(query, app_info.name)
        if score > best_score:
            best_score = score
            best_match = (app_key, app_info)

        # Check aliases
        for alias in app_info.aliases:
            score = fuzzy_match(query, alias)
            if score > best_score:
                best_score = score
                best_match = (app_key, app_info)

    if best_match and best_score >= 0.6:
        return (best_match[0], best_match[1], best_score)

    return None


def find_folder_path(query: str) -> Optional[str]:
    """
    Find folder path from natural language query.

    Returns expanded path or None.
    """
    query = query.lower().strip()

    # Remove common prefixes
    for prefix in ["go to", "open", "show", "navigate to", "take me to", "my"]:
        if query.startswith(prefix):
            query = query[len(prefix):].strip()

    # Remove common suffixes
    for suffix in ["folder", "directory"]:
        if query.endswith(suffix):
            query = query[:-len(suffix)].strip()

    # Check direct match
    if query in FOLDER_ALIASES:
        path = FOLDER_ALIASES[query]
        return os.path.expanduser(path)

    # Fuzzy match
    best_match = None
    best_score = 0.0

    for alias, path in FOLDER_ALIASES.items():
        score = fuzzy_match(query, alias)
        if score > best_score:
            best_score = score
            best_match = path

    if best_match and best_score >= 0.7:
        return os.path.expanduser(best_match)

    return None


def find_context_action(query: str) -> Optional[str]:
    """
    Find context-aware action from query.

    Returns action key or None.
    """
    query = query.lower().strip()

    for action_key, phrases in CONTEXT_ALIASES.items():
        for phrase in phrases:
            if phrase in query or fuzzy_match(query, phrase) >= 0.8:
                return action_key

    return None


def extract_action_and_target(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract the action and target from a command.

    Examples:
        "open chrome" -> ("open", "chrome")
        "close the browser" -> ("close", "the browser")
        "go to my documents" -> ("go_to", "my documents")

    Returns (action, target) tuple.
    """
    text = text.lower().strip()

    # Check for action words
    for action, synonyms in ACTION_SYNONYMS.items():
        for synonym in synonyms:
            if text.startswith(synonym + " "):
                target = text[len(synonym):].strip()
                # Remove articles
                for article in ["the", "a", "an", "my"]:
                    if target.startswith(article + " "):
                        target = target[len(article):].strip()
                        break
                return (action, target)
            elif text.startswith(synonym):
                return (action, text[len(synonym):].strip() or None)

    return (None, text)


def normalize_target(target: str) -> str:
    """
    Normalize a target string by removing common words.
    """
    target = target.lower().strip()

    # Remove common filler words
    remove_words = [
        "the", "a", "an", "my", "this", "that",
        "please", "now", "app", "application", "program",
        "window", "page"
    ]

    words = target.split()
    words = [w for w in words if w not in remove_words]

    return " ".join(words)


class SmartCommandProcessor:
    """
    Intelligent command processor with natural language understanding.
    """

    def __init__(self):
        """Initialize the smart command processor."""
        self._system = platform.system().lower()

    def process(self, text: str) -> Dict[str, Any]:
        """
        Process a natural language command.

        Returns a dictionary with:
            - action: The action to perform
            - target: The target of the action
            - params: Additional parameters
            - confidence: Confidence score
            - original: Original text
        """
        text = text.strip()
        result = {
            "action": None,
            "target": None,
            "params": {},
            "confidence": 0.0,
            "original": text,
            "understood": False,
        }

        # Check for context-aware commands first
        context_action = find_context_action(text)
        if context_action:
            result["action"] = context_action
            result["confidence"] = 0.9
            result["understood"] = True
            return result

        # Extract action and target
        action, target = extract_action_and_target(text)

        if action and target:
            result["action"] = action

            # Check if target is an application
            app_match = find_best_app_match(target)
            if app_match:
                app_key, app_info, confidence = app_match
                result["target"] = app_key
                result["params"]["app_info"] = app_info
                result["confidence"] = confidence
                result["understood"] = True
                return result

            # Check if target is a folder
            folder_path = find_folder_path(target)
            if folder_path:
                result["target"] = folder_path
                result["params"]["is_folder"] = True
                result["confidence"] = 0.85
                result["understood"] = True
                return result

            # Use the raw target
            result["target"] = normalize_target(target)
            result["confidence"] = 0.6
            result["understood"] = True

        return result

    def get_executable(self, app_key: str) -> Optional[str]:
        """Get the executable for an application."""
        if app_key in APP_ALIASES:
            return APP_ALIASES[app_key].executable
        return None

    def get_window_pattern(self, app_key: str) -> Optional[str]:
        """Get the window title pattern for an application."""
        if app_key in APP_ALIASES:
            return APP_ALIASES[app_key].windows_name
        return None

    def open_folder(self, path: str) -> bool:
        """Open a folder in the file manager."""
        try:
            path = os.path.expanduser(path)

            if self._system == "windows":
                os.startfile(path)
            elif self._system == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])

            return True
        except Exception:
            return False

    def open_application(self, app_key: str) -> bool:
        """Open an application by key."""
        if app_key not in APP_ALIASES:
            return False

        app_info = APP_ALIASES[app_key]
        executable = app_info.executable

        if not executable:
            return False

        try:
            if self._system == "windows":
                # Handle special URIs
                if executable.endswith(":"):
                    os.startfile(executable)
                else:
                    subprocess.Popen(executable, shell=True)
            elif self._system == "darwin":
                subprocess.Popen(["open", "-a", app_info.name])
            else:
                subprocess.Popen([executable])

            return True
        except Exception:
            return False

    def search_web(self, query: str) -> bool:
        """Search the web for a query."""
        import urllib.parse

        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"

        try:
            if self._system == "windows":
                os.startfile(search_url)
            elif self._system == "darwin":
                subprocess.run(["open", search_url])
            else:
                subprocess.run(["xdg-open", search_url])

            return True
        except Exception:
            return False


# Convenience functions

def understand_command(text: str) -> Dict[str, Any]:
    """
    Convenience function to understand a natural language command.
    """
    processor = SmartCommandProcessor()
    return processor.process(text)


def get_app_suggestions(partial: str) -> List[str]:
    """
    Get application name suggestions for partial input.
    """
    partial = partial.lower()
    suggestions = []

    for app_key, app_info in APP_ALIASES.items():
        if partial in app_info.name.lower():
            suggestions.append(app_info.name)
        else:
            for alias in app_info.aliases:
                if partial in alias:
                    suggestions.append(app_info.name)
                    break

    return list(set(suggestions))[:5]
