"""Element actions module for Shadowstep framework.

This module provides action methods for interacting with UI elements,
including sending keys, clearing fields, setting values, and submitting forms.
"""

from __future__ import annotations

import inspect
import logging
from typing import TYPE_CHECKING

from shadowstep.decorators.common_decorators import log_debug

if TYPE_CHECKING:
    from shadowstep.element import Element
    from shadowstep.element.utilities import ElementUtilities
    from shadowstep.locator import LocatorConverter
    from shadowstep.shadowstep import Shadowstep


class ElementActions:
    """Element actions handler for UI interactions.

    This class provides methods for performing actions on UI elements
    such as sending keys, clearing fields, setting values, and submitting forms.
    """

    def __init__(self, element: Element) -> None:
        """Initialize ElementActions with an element.

        Args:
            element: The Element instance to perform actions on.

        """
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    # Override
    @log_debug()
    def send_keys(self, *value: str) -> Element:
        """Send keys to the element.

        Args:
            *value: Variable number of string values to send to the element.

        Returns:
            Element: The current element instance for method chaining.

        Raises:
            ShadowstepElementException: If sending keys fails within timeout.

        """
        text = "".join(value)
        self.element.get_driver()
        element = self.element.get_native()
        element.send_keys(text)
        return self.element

    # Override
    @log_debug()
    def clear(self) -> Element:
        """Clear the element's text content.

        Returns:
            Element: The current element instance for method chaining.

        Raises:
            ShadowstepElementException: If clearing the element fails within timeout.

        """
        self.element.get_driver()
        current_element = self.element.get_native()
        current_element.clear()
        return self.element

    # Override
    @log_debug()
    def set_value(self, value: str) -> Element:
        """Set value for the element.

        Note: NOT IMPLEMENTED in UiAutomator2!

        Args:
            value: The value to set for the element.

        Returns:
            Element: The current element instance for method chaining.

        Raises:
            ShadowstepElementException: If setting value fails within timeout.

        """
        current_frame = inspect.currentframe()
        method_name = current_frame.f_code.co_name if current_frame else "unknown"
        self.logger.warning("Method %s is not implemented in UiAutomator2", method_name)
        self.element.get_driver()
        element = self.element.get_native()
        element.set_value(value)  # type: ignore[attr-defined]
        return self.element

    # Override
    @log_debug()
    def submit(self) -> Element:
        """Submit the element (typically a form).

        Returns:
            Element: The current element instance for method chaining.

        Raises:
            ShadowstepElementException: If submitting the element fails within timeout.

        """
        current_frame = inspect.currentframe()
        method_name = current_frame.f_code.co_name if current_frame else "unknown"
        self.logger.warning("Method %s is not implemented in UiAutomator2", method_name)
        self.element.get_driver()
        element = self.element.get_native()
        element.submit()
        return self.element
