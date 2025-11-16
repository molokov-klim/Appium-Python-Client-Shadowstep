# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Action step definitions for scheduled actions.

This module provides the ActionStep class for defining
individual action steps that can be scheduled and executed
in the Shadowstep automation framework.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from shadowstep import UiSelector
    from shadowstep.element.element import Element


class ActionStep:
    """Represents a single action step in scheduled actions.

    This class provides static methods for creating various types of
    action steps that can be scheduled and executed in the Shadowstep
    automation framework.

    Each action step consists of:
    - type: The type of action (gesture, source, screenshot)
    - name: A descriptive name for tracking in history
    - payload: Type-specific configuration
    """

    def __init__(self, step_type: str, name: str, payload: dict[str, Any]) -> None:
        """Initialize an ActionStep.

        Args:
            step_type: Type of the step (gesture, source, screenshot).
            name: Name of the action step for tracking.
            payload: Configuration payload for the step.

        """
        self.type: str = step_type
        self.name: str = name
        self.payload: dict[str, Any] = payload

    def to_dict(self) -> dict[str, Any]:
        """Convert action step to dictionary format.

        Returns:
            dict[str, Any]: Dictionary representation of the action step.

        """
        return {
            "type": self.type,
            "name": self.name,
            "payload": self.payload,
        }

    @staticmethod
    def gesture_click(
        name: str,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
    ) -> ActionStep:
        """Create click gesture action step.

        Args:
            name: Name of the action.
            locator: Element locator as tuple (strategy, selector) or dict.

        Returns:
            ActionStep: Click action step.

        Raises:
            ValueError: If locator format is invalid.

        """
        from shadowstep.element.element import Element  # noqa: PLC0415

        # Convert Element to locator
        if isinstance(locator, Element):
            locator = locator.locator

        # Parse locator to strategy and selector
        if isinstance(locator, tuple) and len(locator) == 2:  # noqa: PLR2004
            strategy, selector = locator
        elif isinstance(locator, dict):
            strategy = locator.get("strategy")
            selector = locator.get("selector")
            if not strategy or not selector:
                error_msg = "Locator dict must contain 'strategy' and 'selector' keys"
                raise ValueError(error_msg)
        else:
            error_msg = "Locator must be a tuple or dict"
            raise ValueError(error_msg)

        payload = {
            "subtype": "click",
            "locator": {
                "strategy": strategy,
                "selector": selector,
            },
        }
        return ActionStep("gesture", name, payload)

    @staticmethod
    def gesture_long_click(
        name: str,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
    ) -> ActionStep:
        """Create long click gesture action step.

        Args:
            name: Name of the action.
            locator: Element locator as tuple (strategy, selector) or dict.

        Returns:
            ActionStep: Long click action step.

        Raises:
            ValueError: If locator format is invalid.

        """
        from shadowstep.element.element import Element  # noqa: PLC0415

        # Convert Element to locator
        if isinstance(locator, Element):
            locator = locator.locator

        # Parse locator to strategy and selector
        if isinstance(locator, tuple) and len(locator) == 2:  # noqa: PLR2004
            strategy, selector = locator
        elif isinstance(locator, dict):
            strategy = locator.get("strategy")
            selector = locator.get("selector")
            if not strategy or not selector:
                error_msg = "Locator dict must contain 'strategy' and 'selector' keys"
                raise ValueError(error_msg)
        else:
            error_msg = "Locator must be a tuple or dict"
            raise ValueError(error_msg)

        payload = {
            "subtype": "longClick",
            "locator": {
                "strategy": strategy,
                "selector": selector,
            },
        }
        return ActionStep("gesture", name, payload)

    @staticmethod
    def gesture_double_click(
        name: str,
        element_id: str,
        x: int,
        y: int,
    ) -> ActionStep:
        """Create double click gesture action step.

        Args:
            name: Name of the action.
            element_id: ID of the element.
            x: X coordinate.
            y: Y coordinate.

        Returns:
            ActionStep: Double click action step.

        """
        payload = {
            "subtype": "doubleClick",
            "elementId": element_id,
            "x": x,
            "y": y,
        }
        return ActionStep("gesture", name, payload)

    @staticmethod
    def source(name: str) -> ActionStep:
        """Create source action step.

        Args:
            name: Name of the action.

        Returns:
            ActionStep: Source action step.

        """
        payload = {
            "subtype": "xml",
        }
        return ActionStep("source", name, payload)

    @staticmethod
    def screenshot(name: str) -> ActionStep:
        """Create screenshot action step.

        Args:
            name: Name of the action.

        Returns:
            ActionStep: Screenshot action step.

        """
        payload = {
            "subtype": "png",
        }
        return ActionStep("screenshot", name, payload)
