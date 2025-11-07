"""Graphical dashboard for controlling the voice automation assistant."""
from __future__ import annotations

import logging
import queue
import threading
from dataclasses import dataclass
from tkinter import BOTH, DISABLED, END, NORMAL, Tk
from tkinter import messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Optional

from .app import VoiceAutomationApp
from .config import AppConfig


LOGGER = logging.getLogger(__name__)


class TkQueueHandler(logging.Handler):
    """Send log records to a thread-safe queue for UI consumption."""

    def __init__(self, output_queue: "queue.Queue[str]") -> None:
        super().__init__()
        self.output_queue = output_queue

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D401 - inherited
        try:
            msg = self.format(record)
            self.output_queue.put_nowait(msg)
        except Exception:  # noqa: BLE001 - logging handlers must never raise
            self.handleError(record)


@dataclass
class VoiceAssistantDashboard:
    """Minimalist Tkinter dashboard that wraps :class:`VoiceAutomationApp`."""

    config: AppConfig
    app: VoiceAutomationApp = None  # type: ignore[assignment]
    root: Optional[Tk] = None

    def __post_init__(self) -> None:
        self.app = VoiceAutomationApp(self.config)
        self._thread: Optional[threading.Thread] = None
        self._log_queue: "queue.Queue[str]" = queue.Queue()
        self._status_message = "Idle"
        self._handler: Optional[TkQueueHandler] = None

    # ------------------------------------------------------------------ UI SETUP
    def _init_ui(self) -> None:
        self.root = Tk()
        self.root.title("Voice Control Assistant")
        self.root.geometry("520x360")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TLabel", background="#f5f5f5", foreground="#1f1f1f", font=("Segoe UI", 11))
        style.configure(
            "Status.TLabel",
            font=("Segoe UI Semibold", 12),
            padding=4,
        )
        style.configure(
            "Action.TButton",
            font=("Segoe UI", 11),
            padding=(14, 8),
        )

        container = ttk.Frame(self.root, padding=20, style="TFrame")
        container.pack(fill=BOTH, expand=True)

        header = ttk.Label(
            container,
            text="ChatGPT Voice Automation",
            font=("Segoe UI Semibold", 16),
        )
        header.pack(anchor="w", pady=(0, 10))

        self.status_label = ttk.Label(
            container,
            text=self._status_message,
            style="Status.TLabel",
        )
        self.status_label.pack(anchor="w", pady=(0, 12))

        button_row = ttk.Frame(container, style="TFrame")
        button_row.pack(fill=BOTH, expand=False, pady=(0, 10))

        self.start_button = ttk.Button(
            button_row,
            text="Start Listening",
            command=self._start_assistant,
            style="Action.TButton",
        )
        self.start_button.pack(side="left", padx=(0, 10))

        self.stop_button = ttk.Button(
            button_row,
            text="Stop",
            command=self._stop_assistant,
            style="Action.TButton",
            state=DISABLED,
        )
        self.stop_button.pack(side="left")

        self.log_output = ScrolledText(
            container,
            height=10,
            font=("Consolas", 10),
            state=DISABLED,
            background="#ffffff",
            borderwidth=0,
            relief="flat",
        )
        self.log_output.pack(fill=BOTH, expand=True, pady=(10, 0))

        # Hook logging so the user can see what's happening without watching a console.
        handler = TkQueueHandler(self._log_queue)
        handler.setFormatter(logging.Formatter("%(asctime)s — %(levelname)s — %(message)s"))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)
        self._handler = handler

        # Update UI periodically with log messages and status events.
        if self.root is not None and self.root.winfo_exists():
            self.root.after(150, self._poll_queues)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ----------------------------------------------------------------- UI EVENTS
    def _start_assistant(self) -> None:
        if self.app.is_running:
            return

        LOGGER.info("Starting assistant from dashboard…")
        self._update_status("Connecting to microphone…")
        self.start_button.configure(state=DISABLED)
        self.stop_button.configure(state=NORMAL)

        def runner() -> None:
            try:
                self.app.run(status_callback=self._update_status)
            except Exception as exc:  # noqa: BLE001 - surface error to UI and logs
                LOGGER.exception("Assistant crashed: %s", exc)
                self._update_status("Assistant crashed; see logs.")
                if self.root is not None:
                    error_message = str(exc)
                    self.root.after(
                        0, lambda msg=error_message: messagebox.showerror("Assistant Error", msg)
                    )
            finally:
                if self.root is not None:
                    self.root.after(0, self._on_assistant_stopped)

        self._thread = threading.Thread(target=runner, name="voice-assistant", daemon=True)
        self._thread.start()

    def _stop_assistant(self) -> None:
        LOGGER.info("Stop requested from dashboard.")
        self.app.stop()
        self._update_status("Stopping…")
        self.stop_button.configure(state=DISABLED)

    def _on_assistant_stopped(self) -> None:
        self.start_button.configure(state=NORMAL)
        self.stop_button.configure(state=DISABLED)
        self._update_status("Assistant stopped.")

    def _on_close(self) -> None:
        if self.app.is_running:
            if not messagebox.askyesno(
                "Close dashboard",
                "The assistant is still listening. Stop it and close?",
            ):
                return
            self._stop_assistant()
        if self.root is not None:
            self.root.destroy()
        if self._handler is not None:
            logging.getLogger().removeHandler(self._handler)
            self._handler = None

    # ------------------------------------------------------------------ UTILITIES
    def _poll_queues(self) -> None:
        if self.root is None:
            return

        while True:
            try:
                message = self._log_queue.get_nowait()
            except queue.Empty:
                break
            else:
                self._append_log(message)

        if self.root is not None and self.root.winfo_exists():
            self.root.after(150, self._poll_queues)

    def _append_log(self, message: str) -> None:
        self.log_output.configure(state=NORMAL)
        self.log_output.insert(END, message + "\n")
        self.log_output.configure(state=DISABLED)
        self.log_output.yview_moveto(1.0)

    def _update_status(self, message: str) -> None:
        self._status_message = message
        if self.root is not None:
            self.status_label.configure(text=message)

    # ---------------------------------------------------------------------- API
    def run(self) -> None:
        """Launch the dashboard event loop."""

        if self.root is None:
            self._init_ui()
        if self.root is not None:
            self.root.mainloop()


__all__ = ["VoiceAssistantDashboard"]

