"""Element properties module for Shadowstep framework.

This module provides property access functionality for elements,
including attributes, CSS properties, dimensions, and visibility checks.
"""

from __future__ import annotations

import inspect
import logging
import time
import traceback
from typing import TYPE_CHECKING, Any, cast

from selenium.common import NoSuchElementException

from shadowstep.decorators.decorators import log_debug
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepElementException,
    ShadowstepNoSuchElementException,
)

if TYPE_CHECKING:
    from selenium.webdriver.remote.shadowroot import ShadowRoot

    from shadowstep.element.element import Element
    from shadowstep.element.utilities import ElementUtilities
    from shadowstep.locator import LocatorConverter, UiSelector
    from shadowstep.shadowstep import Shadowstep


class ElementProperties:
    """Element properties handler for Shadowstep framework."""

    def __init__(self, element: Element) -> None:
        """Initialize ElementProperties.

        Args:
            element: The element to get properties from.

        """
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    # Override
    @log_debug()
    def get_attribute(self, name: str) -> str:  # type: ignore[override]
        """Get element attribute value."""
        self.element.get_driver()
        current_element = self.element.get_native()
        return cast("str", current_element.get_attribute(name))  # type: ignore[reportUnknownMemberType]  # never seen not str

    @log_debug()
    def get_attributes(self) -> dict[str, Any]:
        """Get all attributes of the element.

        Returns:
            dict[str, Any]: Dictionary containing all element attributes.

        """
        xpath_expr = self._resolve_xpath_for_attributes()
        if not xpath_expr:
            return {}
        extracted_attributes = self.utilities.extract_el_attrs_from_source(
            xpath_expr,
            self.shadowstep.driver.page_source,
        )
        if any(extracted_attributes):
            return extracted_attributes[0]
        return {}

    @log_debug()
    def get_property(self, name: str) -> Any:
        """Get element property value."""
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.get_property(name)  # type: ignore[reportUnknownMemberType]

    @log_debug()
    def get_dom_attribute(self, name: str) -> str:
        """Get element DOM attribute value."""
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.get_dom_attribute(name)  # type: ignore[reportUnknownMemberType]

    # Override
    @log_debug()
    def is_displayed(self) -> bool:
        """Check if element is displayed."""
        self.element.get_driver()
        element = self.element.get_native()
        return element.is_displayed()

    #################################################################################3

    @log_debug()
    def is_visible(self) -> bool:
        """Check if element is visible."""
        try:
            result = self._check_element_visibility()
        except NoSuchElementException:
            return False
        except ShadowstepNoSuchElementException:
            return False
        except ShadowstepElementException:
            return False
        if result is not None:
            return result
        time.sleep(0.1)
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def is_selected(self) -> bool:
        """Check if element is selected."""
        self.element.get_driver()
        element = self.element.get_native()
        return element.is_selected()

    @log_debug()
    def is_enabled(self) -> bool:
        """Check if element is enabled."""
        self.element.get_driver()
        element = self.element.get_native()
        return element.is_enabled()

    @log_debug()
    def is_contains(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
    ) -> bool:
        """Check if element contains another element."""
        from shadowstep.element.element import Element  # noqa: PLC0415

        if isinstance(locator, Element):
            locator = locator.locator
        try:
            child_element = self.element._get_web_element(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
                locator=locator,
            )
        except (NoSuchElementException, ShadowstepNoSuchElementException):
            return False
        else:
            return child_element is not None  # type: ignore[reportUnnecessaryComparison]

    @log_debug()
    def tag_name(self) -> str:
        """Get element tag name."""
        self.element.get_driver()
        element = self.element.get_native()
        return element.tag_name

    @log_debug()
    def attributes(self) -> dict[str, Any]:
        """Get element attributes."""
        return self.get_attributes()

    @log_debug()
    def text(self) -> str:
        """Get element text."""
        self.element.get_driver()
        element = self.element.get_native()
        return element.text

    @log_debug()
    def resource_id(self) -> str:
        """Get element resource ID."""
        self.element.get_driver()
        return self.get_attribute("resource-id")

    @log_debug()
    def class_(self) -> str:
        """Get element class."""
        self.element.get_driver()
        return self.get_attribute("class")

    @log_debug()
    def index(self) -> str:
        """Get element index."""
        self.element.get_driver()
        return self.get_attribute("index")

    @log_debug()
    def package(self) -> str:
        """Get element package."""
        self.element.get_driver()
        return self.get_attribute("package")

    @log_debug()
    def class_name(self) -> str:  # 'class' is a reserved word, so class_name is better
        """Get element class name."""
        self.element.get_driver()
        return self.get_attribute("class")

    @log_debug()
    def bounds(self) -> str:
        """Get element bounds."""
        self.element.get_driver()
        return self.get_attribute("bounds")

    @log_debug()
    def checked(self) -> str:
        """Get element checked state."""
        self.element.get_driver()
        return self.get_attribute("checked")

    @log_debug()
    def checkable(self) -> str:
        """Get element checkable state."""
        self.element.get_driver()
        return self.get_attribute("checkable")

    @log_debug()
    def enabled(self) -> str:
        """Get element enabled state."""
        self.element.get_driver()
        return self.get_attribute("enabled")

    @log_debug()
    def focusable(self) -> str:
        """Get element focusable state."""
        self.element.get_driver()
        return self.get_attribute("focusable")

    @log_debug()
    def focused(self) -> str:
        """Get element focused state."""
        self.element.get_driver()
        return self.get_attribute("focused")

    @log_debug()
    def long_clickable(self) -> str:
        """Get element long clickable state."""
        self.element.get_driver()
        return self.get_attribute("long-clickable")

    @log_debug()
    def password(self) -> str:
        """Get element password attribute."""
        self.element.get_driver()
        return self.get_attribute("password")

    @log_debug()
    def scrollable(self) -> str:
        """Get element scrollable attribute."""
        self.element.get_driver()
        return self.get_attribute("scrollable")

    @log_debug()
    def selected(self) -> str:
        """Get element selected attribute."""
        self.element.get_driver()
        return self.get_attribute("selected")

    @log_debug()
    def displayed(self) -> str:
        """Get element displayed attribute."""
        self.element.get_driver()
        return self.get_attribute("displayed")

    @log_debug()
    def shadow_root(self) -> ShadowRoot:
        """Get element shadow root."""
        self.element.get_driver()
        element = self.element.get_native()
        return element.shadow_root

    @log_debug()
    def size(self) -> dict[str, Any]:
        """Get element size."""
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.size  # type: ignore[reportUnknownMemberType]

    @log_debug()
    def value_of_css_property(self, property_name: str) -> str:
        """Get element CSS property value."""
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.value_of_css_property(property_name)  # type: ignore[reportUnknownMemberType]

    @log_debug()
    def location(self) -> dict[str, Any]:
        """Get element location."""
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.location  # type: ignore[reportUnknownMemberType]

    @log_debug()
    def rect(self) -> dict[str, Any]:
        """Get element rectangle."""
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.rect  # type: ignore[reportUnknownMemberType]

    @log_debug()
    def aria_role(self) -> str:
        """Get element ARIA role."""
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.aria_role

    @log_debug()
    def accessible_name(self) -> str:
        """Get element accessible name."""
        self.element.get_driver()
        current_element = self.element.get_native()
        return current_element.accessible_name

    def _resolve_xpath_for_attributes(self) -> str | None:
        """Resolve XPath expression from locator for attributes fetching."""
        xpath_expr = self.converter.to_xpath(self.element.locator)[1]
        if not xpath_expr:
            self.logger.error("Failed to resolve XPath from locator: %s", self.element.locator)
            return None
        self.logger.debug("Resolved XPath: %s", xpath_expr)
        return xpath_expr

    def _check_element_visibility(self) -> bool | None:
        """Check if element is visible, handling exceptions."""
        screen_size = self.shadowstep.terminal.get_screen_resolution()  # type: ignore[reportOptionalMemberAccess]
        screen_width = screen_size[0]
        screen_height = screen_size[1]
        current_element = self.element.get_native()

        if current_element is None:  # type: ignore[reportUnnecessaryComparison]
            return False
        if current_element.get_attribute("displayed") != "true":  # type: ignore[reportUnknownMemberType]
            return False

        element_location = cast("dict[str, Any]", current_element.location)  # type: ignore[reportUnknownMemberType]
        element_size = cast("dict[str, Any]", current_element.size)  # type: ignore[reportUnknownMemberType]
        return self._check_element_bounds(
            element_location,
            element_size,
            screen_width,
            screen_height,
        )

    def _check_element_bounds(
        self,
        element_location: dict[str, Any],
        element_size: dict[str, Any],
        screen_width: int,
        screen_height: int,
    ) -> bool:
        """Check if element is within screen bounds."""
        return not (
            element_location["y"] + element_size["height"] > screen_height
            or element_location["x"] + element_size["width"] > screen_width
            or element_location["y"] < 0
            or element_location["x"] < 0
        )
