"""Element screenshots module for Shadowstep framework.

This module provides screenshot functionality for elements,
including base64 encoding, PNG format, and file saving capabilities.
"""

import logging
from typing import TYPE_CHECKING

from shadowstep.decorators.decorators import log_debug

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.element.utilities import ElementUtilities
    from shadowstep.locator import LocatorConverter
    from shadowstep.shadowstep import Shadowstep


class ElementScreenshots:
    """Element screenshots handler for Shadowstep framework."""

    def __init__(self, element: "Element") -> None:
        """Initialize ElementScreenshots.

        Args:
            element: The element to take screenshots from.

        """
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    @log_debug()
    def screenshot_as_base64(self) -> str:
        """Get the screenshot of the current element as a base64 encoded string.

        Returns:
            str: Base64-encoded screenshot string.

        """
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.screenshot_as_base64

    @log_debug()
    def screenshot_as_png(self) -> bytes:
        """Get the screenshot of the current element as binary data.

        Returns:
            bytes: PNG-encoded screenshot bytes.

        """
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.screenshot_as_png

    @log_debug()
    def save_screenshot(self, filename: str = "screenshot.png") -> bool:
        """Save a screenshot of the current element to a PNG image file.

        Args:
            filename: The full path to save the screenshot. Should end with `.png`.

        Returns:
            True if successful, False otherwise.

        """
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.screenshot(filename)  # type: ignore[reportUnknownMemberType]
