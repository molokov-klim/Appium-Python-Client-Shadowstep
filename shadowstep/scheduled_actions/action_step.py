"""Action step definitions for scheduled actions.

This module provides the ActionStep class for defining
individual action steps that can be scheduled and executed
in the Shadowstep automation framework.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from shadowstep.element.element import Element


class ActionStep:
    """Represents a single action step in scheduled actions.

    This class provides static methods for creating various types of
    action steps that can be scheduled and executed in the Shadowstep
    automation framework.
    """

    @staticmethod
    def gesture_click(name: str, locator: tuple[str, str] | dict[str, Any] | Element) -> ActionStep:
        """Create click gesture action step.

        Args:
            name: Name of the action.
            locator: Element locator.

        Returns:
            ActionStep: Click action step.

        """
        raise NotImplementedError

    @staticmethod
    def gesture_long_click(name: str, locator: tuple[str, str] | dict[str, Any] | Element) -> ActionStep:
        """Create long click gesture action step.

        Args:
            name: Name of the action.
            locator: Element locator.

        Returns:
            ActionStep: Long click action step.

        """
        raise NotImplementedError

    @staticmethod
    def gesture_double_click(name: str, element_id: str, x: int, y: int) -> ActionStep:
        """Create double click gesture action step.

        Args:
            name: Name of the action.
            element_id: ID of the element.
            x: X coordinate.
            y: Y coordinate.

        Returns:
            ActionStep: Double click action step.

        """
        raise NotImplementedError

    @staticmethod
    def source(name: str) -> ActionStep:
        """Create source action step.

        Args:
            name: Name of the action.

        Returns:
            ActionStep: Source action step.

        """
        raise NotImplementedError

    @staticmethod
    def screenshot(name: str) -> ActionStep:
        """Create screenshot action step.

        Args:
            name: Name of the action.

        Returns:
            ActionStep: Screenshot action step.

        """
        raise NotImplementedError
