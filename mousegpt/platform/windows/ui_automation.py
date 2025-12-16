"""
Windows UI Automation Integration for MouseGPT.

This module provides integration with Windows UI Automation,
enabling MouseGPT to interact with UI elements by name, type, or role.
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import IntEnum

# Windows UI Automation imports
try:
    import comtypes.client
    from comtypes import GUID
    COMTYPES_AVAILABLE = True
except ImportError:
    COMTYPES_AVAILABLE = False

try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class ControlType(IntEnum):
    """UI Automation control types."""
    BUTTON = 50000
    CALENDAR = 50001
    CHECKBOX = 50002
    COMBOBOX = 50003
    EDIT = 50004
    HYPERLINK = 50005
    IMAGE = 50006
    LISTITEM = 50007
    LIST = 50008
    MENU = 50009
    MENUBAR = 50010
    MENUITEM = 50011
    PANE = 50012
    PROGRESSBAR = 50013
    RADIOBUTTON = 50014
    SCROLLBAR = 50015
    SLIDER = 50016
    SPINNER = 50017
    STATUSBAR = 50018
    TAB = 50019
    TABITEM = 50020
    TEXT = 50021
    TOOLBAR = 50022
    TOOLTIP = 50023
    TREE = 50024
    TREEITEM = 50025
    CUSTOM = 50026
    GROUP = 50027
    THUMB = 50028
    DATAGRID = 50029
    DATAITEM = 50030
    DOCUMENT = 50031
    SPLITBUTTON = 50032
    WINDOW = 50033
    HEADER = 50034
    HEADERITEM = 50035
    TABLE = 50036
    TITLEBAR = 50037
    SEPARATOR = 50038


@dataclass
class UIElement:
    """Represents a UI element."""
    name: str
    control_type: str
    class_name: str
    automation_id: str
    bounding_rect: Tuple[int, int, int, int]  # left, top, right, bottom
    is_enabled: bool
    is_visible: bool
    value: Optional[str] = None
    hwnd: Optional[int] = None

    @property
    def center(self) -> Tuple[int, int]:
        """Get the center point of the element."""
        left, top, right, bottom = self.bounding_rect
        return ((left + right) // 2, (top + bottom) // 2)

    @property
    def width(self) -> int:
        """Get element width."""
        return self.bounding_rect[2] - self.bounding_rect[0]

    @property
    def height(self) -> int:
        """Get element height."""
        return self.bounding_rect[3] - self.bounding_rect[1]


class WindowsUIAutomation:
    """
    Windows UI Automation integration.

    Provides methods to:
    - Find UI elements by name, type, or automation ID
    - Click on elements
    - Get element properties
    - Interact with controls
    """

    def __init__(self):
        """Initialize UI Automation."""
        if not COMTYPES_AVAILABLE:
            raise ImportError(
                "comtypes is required for UI Automation. "
                "Install with: pip install comtypes"
            )

        self._uia = None
        self._root = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the UI Automation client."""
        try:
            # Create UI Automation instance
            clsid = GUID("{FF48DBA4-60EF-4201-AA87-54103EEF594E}")
            self._uia = comtypes.client.CreateObject(clsid)
            self._root = self._uia.GetRootElement()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize UI Automation: {e}")

    def get_root_element(self) -> UIElement:
        """Get the root (desktop) element."""
        return self._element_to_ui_element(self._root)

    def get_focused_element(self) -> Optional[UIElement]:
        """Get the currently focused element."""
        try:
            element = self._uia.GetFocusedElement()
            return self._element_to_ui_element(element)
        except Exception:
            return None

    def find_element_by_name(
        self,
        name: str,
        exact_match: bool = True,
        root: Optional[Any] = None,
    ) -> Optional[UIElement]:
        """
        Find an element by name.

        Args:
            name: Element name to search for.
            exact_match: If True, require exact name match.
            root: Root element to search from (default: desktop).

        Returns:
            UIElement or None if not found.
        """
        root = root or self._root

        try:
            # Create name condition
            condition = self._uia.CreatePropertyCondition(
                30005,  # UIA_NamePropertyId
                name
            )

            element = root.FindFirst(
                4,  # TreeScope_Descendants
                condition
            )

            if element:
                return self._element_to_ui_element(element)

            # If not exact match, try substring search
            if not exact_match:
                return self._find_element_by_name_substring(name, root)

            return None
        except Exception:
            return None

    def _find_element_by_name_substring(
        self,
        substring: str,
        root: Optional[Any] = None,
    ) -> Optional[UIElement]:
        """Find element with name containing substring."""
        root = root or self._root
        substring_lower = substring.lower()

        try:
            # Get all elements
            true_condition = self._uia.CreateTrueCondition()
            elements = root.FindAll(4, true_condition)

            for i in range(elements.Length):
                element = elements.GetElement(i)
                try:
                    name = element.CurrentName
                    if name and substring_lower in name.lower():
                        return self._element_to_ui_element(element)
                except Exception:
                    continue

            return None
        except Exception:
            return None

    def find_elements_by_control_type(
        self,
        control_type: ControlType,
        root: Optional[Any] = None,
    ) -> List[UIElement]:
        """
        Find all elements of a specific control type.

        Args:
            control_type: The control type to find.
            root: Root element to search from.

        Returns:
            List of matching UIElements.
        """
        root = root or self._root
        elements = []

        try:
            condition = self._uia.CreatePropertyCondition(
                30003,  # UIA_ControlTypePropertyId
                int(control_type)
            )

            found = root.FindAll(4, condition)

            for i in range(found.Length):
                element = found.GetElement(i)
                ui_element = self._element_to_ui_element(element)
                if ui_element:
                    elements.append(ui_element)

        except Exception:
            pass

        return elements

    def find_element_by_automation_id(
        self,
        automation_id: str,
        root: Optional[Any] = None,
    ) -> Optional[UIElement]:
        """
        Find element by automation ID.

        Args:
            automation_id: The automation ID to find.
            root: Root element to search from.

        Returns:
            UIElement or None.
        """
        root = root or self._root

        try:
            condition = self._uia.CreatePropertyCondition(
                30011,  # UIA_AutomationIdPropertyId
                automation_id
            )

            element = root.FindFirst(4, condition)

            if element:
                return self._element_to_ui_element(element)

            return None
        except Exception:
            return None

    def find_buttons(self, root: Optional[Any] = None) -> List[UIElement]:
        """Find all buttons."""
        return self.find_elements_by_control_type(ControlType.BUTTON, root)

    def find_edit_boxes(self, root: Optional[Any] = None) -> List[UIElement]:
        """Find all edit boxes (text inputs)."""
        return self.find_elements_by_control_type(ControlType.EDIT, root)

    def find_checkboxes(self, root: Optional[Any] = None) -> List[UIElement]:
        """Find all checkboxes."""
        return self.find_elements_by_control_type(ControlType.CHECKBOX, root)

    def find_links(self, root: Optional[Any] = None) -> List[UIElement]:
        """Find all hyperlinks."""
        return self.find_elements_by_control_type(ControlType.HYPERLINK, root)

    def _element_to_ui_element(self, element) -> Optional[UIElement]:
        """Convert a COM element to UIElement dataclass."""
        try:
            rect = element.CurrentBoundingRectangle
            return UIElement(
                name=element.CurrentName or "",
                control_type=self._get_control_type_name(element.CurrentControlType),
                class_name=element.CurrentClassName or "",
                automation_id=element.CurrentAutomationId or "",
                bounding_rect=(rect.left, rect.top, rect.right, rect.bottom),
                is_enabled=element.CurrentIsEnabled,
                is_visible=not element.CurrentIsOffscreen,
                hwnd=element.CurrentNativeWindowHandle,
            )
        except Exception:
            return None

    def _get_control_type_name(self, control_type_id: int) -> str:
        """Get the name for a control type ID."""
        try:
            return ControlType(control_type_id).name
        except ValueError:
            return f"Unknown({control_type_id})"

    def click_element(self, element: UIElement) -> bool:
        """
        Click on a UI element.

        Args:
            element: The element to click.

        Returns:
            True if click was successful.
        """
        if not element.is_enabled or not element.is_visible:
            return False

        from mousegpt.platform.windows.accessibility import WindowsAccessibility

        accessibility = WindowsAccessibility()
        center_x, center_y = element.center
        accessibility.mouse_click("left", center_x, center_y)
        return True

    def focus_element(self, element: UIElement) -> bool:
        """
        Focus a UI element.

        Args:
            element: The element to focus.

        Returns:
            True if focus was successful.
        """
        if element.hwnd and WIN32_AVAILABLE:
            try:
                win32gui.SetForegroundWindow(element.hwnd)
                return True
            except Exception:
                pass
        return False


class WindowEnumerator:
    """
    Helper class to enumerate windows.

    Provides methods to find and list windows by title, class, or other criteria.
    """

    def __init__(self):
        """Initialize window enumerator."""
        if not WIN32_AVAILABLE:
            raise ImportError("pywin32 is required for window enumeration")

    def get_all_windows(self) -> List[Dict[str, Any]]:
        """
        Get all top-level windows.

        Returns:
            List of window information dictionaries.
        """
        windows = []

        def enum_callback(hwnd, param):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                rect = win32gui.GetWindowRect(hwnd)

                windows.append({
                    'hwnd': hwnd,
                    'title': title,
                    'class_name': class_name,
                    'rect': rect,
                    'visible': True,
                })
            return True

        win32gui.EnumWindows(enum_callback, None)
        return windows

    def find_window_by_title(
        self,
        title: str,
        exact_match: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Find a window by title.

        Args:
            title: Window title to search for.
            exact_match: If True, require exact title match.

        Returns:
            Window info dictionary or None.
        """
        title_lower = title.lower()

        for window in self.get_all_windows():
            window_title = window['title'].lower()

            if exact_match:
                if window_title == title_lower:
                    return window
            else:
                if title_lower in window_title:
                    return window

        return None

    def find_windows_by_class(self, class_name: str) -> List[Dict[str, Any]]:
        """
        Find windows by class name.

        Args:
            class_name: Window class name.

        Returns:
            List of matching window info dictionaries.
        """
        class_lower = class_name.lower()
        return [
            w for w in self.get_all_windows()
            if w['class_name'].lower() == class_lower
        ]

    def get_foreground_window(self) -> Optional[Dict[str, Any]]:
        """
        Get the current foreground window.

        Returns:
            Window info dictionary or None.
        """
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            try:
                return {
                    'hwnd': hwnd,
                    'title': win32gui.GetWindowText(hwnd),
                    'class_name': win32gui.GetClassName(hwnd),
                    'rect': win32gui.GetWindowRect(hwnd),
                    'visible': win32gui.IsWindowVisible(hwnd),
                }
            except Exception:
                pass
        return None

    def activate_window(self, hwnd: int) -> bool:
        """
        Activate a window by handle.

        Args:
            hwnd: Window handle.

        Returns:
            True if successful.
        """
        try:
            # Restore if minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False

    def activate_window_by_title(self, title: str) -> bool:
        """
        Activate a window by title.

        Args:
            title: Window title (partial match).

        Returns:
            True if successful.
        """
        window = self.find_window_by_title(title)
        if window:
            return self.activate_window(window['hwnd'])
        return False

    def minimize_window(self, hwnd: int) -> bool:
        """Minimize a window."""
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception:
            return False

    def maximize_window(self, hwnd: int) -> bool:
        """Maximize a window."""
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        except Exception:
            return False

    def close_window(self, hwnd: int) -> bool:
        """Close a window."""
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        except Exception:
            return False

    def move_window(
        self,
        hwnd: int,
        x: int,
        y: int,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> bool:
        """
        Move and optionally resize a window.

        Args:
            hwnd: Window handle.
            x: New X position.
            y: New Y position.
            width: New width (optional).
            height: New height (optional).

        Returns:
            True if successful.
        """
        try:
            if width is None or height is None:
                rect = win32gui.GetWindowRect(hwnd)
                if width is None:
                    width = rect[2] - rect[0]
                if height is None:
                    height = rect[3] - rect[1]

            win32gui.MoveWindow(hwnd, x, y, width, height, True)
            return True
        except Exception:
            return False
