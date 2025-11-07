"""Entry point used by the packaged dashboard executable."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Optional

from .config import AppConfig


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the ChatGPT voice assistant dashboard")
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to a JSON configuration file overriding defaults",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Verbosity of log output inside the dashboard",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format=LOG_FORMAT)

    if args.config:
        config = AppConfig.from_file(args.config)
    else:
        config = AppConfig()

    from .dashboard import VoiceAssistantDashboard

    dashboard = VoiceAssistantDashboard(config)
    dashboard.run()


if __name__ == "__main__":  # pragma: no cover - executable entry point
    main()

