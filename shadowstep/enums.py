"""Enums for Shadowstep framework.

This module contains enumerations used throughout the framework.
"""

from __future__ import annotations

from enum import Enum


class GestureStrategy(str, Enum):
    """Gesture execution strategy.

    Defines which underlying implementation to use for gesture execution.
    """

    W3C_ACTIONS = "w3c_actions"
    """Use W3C WebDriver Actions API (most stable, cross-platform)."""

    MOBILE_COMMANDS = "mobile_commands"
    """Use Appium mobile: commands (UiAutomator2-specific)."""

    AUTO = "auto"
    """Automatic fallback: try W3C Actions first, fall back to mobile commands on failure."""
