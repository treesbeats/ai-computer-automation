"""Command-line interface for the voice automation app."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Optional

from .app import VoiceAutomationApp
from .config import AppConfig


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Voice-controlled Windows automation using ChatGPT")
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to a JSON configuration file overriding defaults",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Verbosity of console logging",
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Launch the graphical dashboard instead of the console loop",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format=LOG_FORMAT)

    if args.config:
        config = AppConfig.from_file(args.config)
    else:
        config = AppConfig()

    if args.dashboard:
        from .dashboard import VoiceAssistantDashboard

        dashboard = VoiceAssistantDashboard(config)
        dashboard.run()
    else:
        app = VoiceAutomationApp(config)
        app.run()


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
