"""Element coordinates module for Shadowstep framework.

This module provides coordinate-related functionality for elements,
including getting bounds, center coordinates, and view locations.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from shadowstep.decorators.common_decorators import log_debug

if TYPE_CHECKING:
    from appium.webdriver.webelement import WebElement

    from shadowstep.element.element import Element
    from shadowstep.element.utilities import ElementUtilities
    from shadowstep.locator import LocatorConverter
    from shadowstep.shadowstep import Shadowstep


class ElementCoordinates:
    """Element coordinates handler for Shadowstep framework."""

    def __init__(self, element: Element) -> None:
        """Initialize ElementCoordinates.

        Args:
            element: The element to get coordinates for.

        """
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    @log_debug()
    def get_coordinates(self) -> tuple[int, int, int, int]:
        """Get the bounding box coordinates of the element.

        Returns:
            (left, top, right, bottom) or None.

        """
        self.element.get_driver()
        element = self.element.get_native()
        return self._get_coordinates_from_native(element)

    @log_debug()
    def get_center(self) -> tuple[int, int]:
        """Get the center coordinates of the element.

        Returns:
            (x, y) center point or None if element not found.

        """
        self.element.get_driver()
        element = self.element.get_native()
        return self._get_center_from_native(element)

    # Override
    @log_debug()
    def location_in_view(self) -> dict[str, Any]:
        """Get the location of an element relative to the view.

        Returns:
            Dictionary with keys 'x' and 'y', or None on failure.

        """
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.location_in_view  # type: ignore[attr-defined]  # Appium WebElement property

    @log_debug()
    def location_once_scrolled_into_view(self) -> dict[str, Any]:
        """Get the top-left corner location of the element after scrolling it into view.

        NOT IMPLEMENTED

        Returns:
            Dictionary with keys 'x' and 'y' indicating location on screen.

        Raises:
            ShadowstepElementException: If element could not be scrolled into view or
                location determined.

        """
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.location_once_scrolled_into_view  # type: ignore[attr-defined]

    @log_debug()
    def _get_coordinates_from_native(self, web_element: WebElement) -> tuple[int, int, int, int]:
        """Get the bounding box coordinates of the element.

        Returns:
            (left, top, right, bottom) or None.

        """
        bounds: Any = web_element.get_attribute("bounds")  # type: ignore[attr-defined]
        left, top, right, bottom = map(
            int,
            bounds.strip("[]").replace("][", ",").split(","),
        )
        return left, top, right, bottom

    @log_debug()
    def _get_center_from_native(self, web_element: WebElement) -> tuple[int, int]:
        """Get the center coordinates of the element.

        Returns:
            (x, y) center point or None if element not found.

        """
        coordinates = self._get_coordinates_from_native(web_element)
        left, top, right, bottom = coordinates
        x = int((left + right) / 2)
        y = int((top + bottom) / 2)
        return x, y
