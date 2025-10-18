"""Shadowstep - Appium Python Client with enhanced features.

This package provides a comprehensive Appium Python client with additional
functionality for mobile automation testing.

Public API:
    - Shadowstep: Main framework class for mobile automation
    - Element: Element interaction and assertion class
    - PageBaseShadowstep: Base class for Page Object Model
    - ShadowstepImage: Image processing and OCR capabilities
    - UiSelector: Android UiSelector locator builder
    - LocatorConverter: Convert between locator formats
    - ShadowstepException: Base exception for the framework
    - Decorators: Common decorators for test methods
"""
import logging
import sys
from typing import ClassVar


class LoguruStyleFormatter(logging.Formatter):
    """Custom logging formatter that mimics Loguru's colorful output style.

    This formatter provides colored output for different log levels,
    similar to the Loguru library's default formatting.
    """

    COLORS: ClassVar[dict[str, str]] = {
        "DEBUG": "\033[38;5;81m",      # Light blue (like loguru DEBUG)
        "INFO": "\033[38;5;34m",       # Green (like loguru INFO)
        "WARNING": "\033[38;5;220m",   # Yellow
        "ERROR": "\033[38;5;196m",     # Red
        "CRITICAL": "\033[1;41m",      # White on red background
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with colors and styling.

        Args:
            record: The log record to format.

        Returns:
            Formatted log message string with colors.

        """
        # Color for log level
        level_color = self.COLORS.get(record.levelname, "")
        levelname = f"{level_color}{record.levelname:<8}{self.RESET}"

        # Gray timestamp
        time = f"\033[38;5;240m{self.formatTime(record, self.datefmt)}{self.RESET}"

        # Color for logger name - purple
        name = f"\033[38;5;135m{record.name}{self.RESET}"

        # Message
        message = record.getMessage()

        return f"{time} | {levelname} | {name} | {message}"

def configure_logging() -> None:
    """Configure logging for the shadowstep package.

    Sets up a custom formatter with colors and configures both the
    shadowstep logger and root logger.
    """
    logger = logging.getLogger("shadowstep")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(LoguruStyleFormatter(datefmt="%Y-%m-%d %H:%M:%S"))

    if not logger.handlers:
        logger.addHandler(handler)

    # Apply to root logger as well
    logging.getLogger().handlers = logger.handlers
    logging.getLogger().setLevel(logger.level)
    logger.propagate = False

configure_logging()

# Public API exports
from shadowstep.decorators import (  # noqa: E402
    current_page,
    fail_safe,
    log_info,
    retry,
    step_info,
    time_it,
)
from shadowstep.element import Element  # noqa: E402
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException  # noqa: E402
from shadowstep.image.image import ShadowstepImage  # noqa: E402
from shadowstep.locator import LocatorConverter, UiSelector  # noqa: E402
from shadowstep.page_base import PageBaseShadowstep  # noqa: E402
from shadowstep.shadowstep import Shadowstep  # noqa: E402

__all__ = [
    # Core classes
    "Shadowstep",
    "Element",
    "PageBaseShadowstep",
    "ShadowstepImage",
    # Locators
    "UiSelector",
    "LocatorConverter",
    # Exceptions
    "ShadowstepException",
    # Decorators
    "current_page",
    "fail_safe",
    "log_info",
    "retry",
    "step_info",
    "time_it",
]
