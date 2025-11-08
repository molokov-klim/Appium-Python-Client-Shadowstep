"""Element DOM module for Shadowstep framework.

This module provides DOM-related functionality for elements,
including getting child elements, parents, siblings, and cousins.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from shadowstep.decorators.decorators import log_debug
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepElementException,
    ShadowstepResolvingLocatorError,
)
from shadowstep.locator import UiSelector
from shadowstep.locator.locator_types.shadowstep_dict import ShadowstepDictAttribute

if TYPE_CHECKING:
    from selenium.types import WaitExcTypes

    from shadowstep.element.element import Element
    from shadowstep.element.utilities import ElementUtilities
    from shadowstep.locator import LocatorConverter
    from shadowstep.shadowstep import Shadowstep


class ElementDOM:
    """Element DOM handler for Shadowstep framework."""

    def __init__(self, element: Element) -> None:
        """Initialize ElementDOM.

        Args:
            element: The element to get DOM relationships for.

        """
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    @log_debug()
    def get_element(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        timeout: int = 30,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> Element:
        """Get a child element relative to the current element.

        Args:
            locator: Locator for the child element.
            timeout: Maximum time to wait for element.
            poll_frequency: How often to check for element.
            ignored_exceptions: Exceptions to ignore during wait.

        Returns:
            The found child element.

        Raises:
            ShadowstepResolvingLocatorError: If locator resolution fails.

        """
        from shadowstep.element.element import Element  # noqa: PLC0415

        resolved_locator = None
        if isinstance(locator, Element):  # type: ignore[arg-type]
            locator = locator.locator

        parent_locator = self.utilities.remove_null_value(self.element.locator)
        child_locator = self.utilities.remove_null_value(locator)

        if not parent_locator:
            msg = "Failed to resolve parent locator"
            raise ShadowstepResolvingLocatorError(msg)
        if not child_locator:
            msg = "Failed to resolve child locator"
            raise ShadowstepResolvingLocatorError(msg)

        if isinstance(parent_locator, tuple):
            child_locator = self.converter.to_xpath(child_locator)
            inner_path = child_locator[1].lstrip("/")  # Remove accidental `/` in front

            # Guaranteed nesting: parent//child
            if not inner_path.startswith("//"):
                inner_path = f"//{inner_path}"

            resolved_locator = ("xpath", f"{parent_locator[1]}{inner_path}")
        elif isinstance(parent_locator, dict):
            child_locator = self.converter.to_dict(child_locator)
            resolved_child_locator = {ShadowstepDictAttribute.CHILD_SELECTOR.value: child_locator}
            parent_locator.update(resolved_child_locator)
            resolved_locator = parent_locator

        elif isinstance(parent_locator, UiSelector):
            child_locator = self.converter.to_uiselector(child_locator)
            resolved_locator = parent_locator.childSelector(UiSelector.from_string(child_locator))

        if resolved_locator is None:
            msg = "Failed to resolve locator"
            raise ShadowstepResolvingLocatorError(msg)

        return Element(
            locator=resolved_locator,  # type: ignore[return-value]
            shadowstep=self.shadowstep,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
        )

    @log_debug()
    def get_elements(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        timeout: float = 30,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> list[Element]:
        """Get multiple child elements relative to the current element.

        Args:
            locator: Locator for the child elements.
            timeout: Maximum time to wait for elements.
            poll_frequency: How often to check for elements.
            ignored_exceptions: Exceptions to ignore during wait.

        Returns:
            List of found child elements.

        Raises:
            ShadowstepElementException: If xpath resolution fails or any element not found.

        """
        from shadowstep.element.element import Element  # noqa: PLC0415

        if isinstance(locator, Element):  # type: ignore[arg-type]
            locator = locator.locator

        base_xpath = self.utilities.get_xpath()
        if not base_xpath:
            msg = "Unable to resolve shadowstep xpath"
            raise ShadowstepElementException(msg)

        locator = self.utilities.remove_null_value(locator)
        locator = self.converter.to_xpath(locator)

        self.element.get_driver()
        wait = WebDriverWait(
            driver=self.element.driver,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
        )
        wait.until(expected_conditions.presence_of_element_located(locator))
        attributes_list = self.utilities.extract_el_attrs_from_source(
            xpath_expr=locator[1],
            page_source=self.shadowstep.driver.page_source,  # type: ignore[attr-defined]
        )
        elements: list[Element] = []
        for attributes in attributes_list:
            element = Element(  # type: ignore[return-value]
                locator=attributes,
                shadowstep=self.shadowstep,
                timeout=timeout,
                poll_frequency=poll_frequency,
                ignored_exceptions=ignored_exceptions,
            )
            elements.append(element)  # type: ignore[arg-type]
        return elements

    @log_debug()
    def get_parent(
        self,
        timeout: float = 30.0,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> Element:
        """Get the parent element of the current element.

        Args:
            timeout: Maximum time to wait for element.
            poll_frequency: How often to check for element.
            ignored_exceptions: Exceptions to ignore during wait.

        Returns:
            The parent element.

        """
        from shadowstep.element.element import Element  # noqa: PLC0415

        clean_locator = self.utilities.remove_null_value(self.element.locator)
        xpath = self.converter.to_xpath(clean_locator)
        xpath = (xpath[0], xpath[1] + "/..")
        return Element(
            locator=xpath,  # type: ignore[return-value]
            shadowstep=self.shadowstep,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
        )

    @log_debug()
    def get_parents(
        self,
        timeout: float = 30.0,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> list[Element]:
        """Get all ancestor elements of the current element.

        Args:
            timeout: Maximum time to wait for elements.
            poll_frequency: How often to check for elements.
            ignored_exceptions: Exceptions to ignore during wait.

        Returns:
            List of ancestor elements.

        """
        clean_locator = self.utilities.remove_null_value(self.element.locator)
        xpath = self.converter.to_xpath(clean_locator)
        xpath = (xpath[0], xpath[1] + "/ancestor::*")
        parents = self.get_elements(xpath, timeout, poll_frequency, ignored_exceptions)
        if parents and parents[0].locator.get("class") == "hierarchy":  # type: ignore[union-attr]
            parents.pop(0)
        return parents

    @log_debug()
    def get_sibling(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        timeout: float = 30.0,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
        strategy: Literal["following", "preceding"] = "following",
    ) -> Element:
        """Get a sibling element of the current element.

        Args:
            locator: Locator for the sibling element.
            timeout: Maximum time to wait for element.
            poll_frequency: How often to check for element.
            ignored_exceptions: Exceptions to ignore during wait.
            strategy: Strategy to search for. Following - after, preceding - before current element.

        Returns:
            The found sibling element.

        """
        from shadowstep.element.element import Element  # noqa: PLC0415

        clean_locator = self.utilities.remove_null_value(self.element.locator)
        base_xpath = self.converter.to_xpath(clean_locator)[1]
        sibling_locator = self.utilities.remove_null_value(locator)
        sibling_xpath = self.converter.to_xpath(sibling_locator)
        sibling_path = sibling_xpath[1].lstrip("/")
        xpath = f"{base_xpath}/{strategy}-sibling::{sibling_path}[1]"
        return Element(  # type: ignore[return-value]
            locator=("xpath", xpath),
            shadowstep=self.shadowstep,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
        )

    @log_debug()
    def get_siblings(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        timeout: float = 30.0,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
        strategy: Literal["following", "preceding"] = "following",
    ) -> list[Element]:
        """Get all sibling elements of the current element.

        Args:
            locator: Locator for the sibling elements.
            timeout: Maximum time to wait for elements.
            poll_frequency: How often to check for elements.
            ignored_exceptions: Exceptions to ignore during wait.
            strategy: Strategy to search for. Following - after, preceding - before current element.

        Returns:
            List of found sibling elements.

        """
        clean_locator = self.utilities.remove_null_value(self.element.locator)
        base_xpath = self.converter.to_xpath(clean_locator)[1]
        sibling_locator = self.utilities.remove_null_value(locator)
        sibling_xpath = self.converter.to_xpath(sibling_locator)
        sibling_path = sibling_xpath[1].lstrip("/")
        xpath = f"{base_xpath}/{strategy}-sibling::{sibling_path}"
        return self.get_elements(("xpath", xpath), timeout, poll_frequency, ignored_exceptions)

    @log_debug()
    def get_cousin(
        self,
        cousin_locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        depth_to_parent: int = 1,
        timeout: float = 30.0,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> Element:
        """Get a cousin element of the current element.

        Args:
            cousin_locator: Locator for the cousin element.
            depth_to_parent: How many levels up to go before finding cousin.
            timeout: Maximum time to wait for element.
            poll_frequency: How often to check for element.
            ignored_exceptions: Exceptions to ignore during wait.

        Returns:
            The found cousin element.

        """
        from shadowstep.element.element import Element  # noqa: PLC0415

        depth_to_parent += 1
        clean_base_locator = self.utilities.remove_null_value(self.element.locator)
        current_xpath = self.converter.to_xpath(clean_base_locator)[1]
        up_xpath = "/".join([".."] * depth_to_parent)
        base_xpath = f"{current_xpath}/{up_xpath}" if up_xpath else current_xpath

        clean_cousin_locator = self.utilities.remove_null_value(cousin_locator)
        cousin_xpath = self.converter.to_xpath(clean_cousin_locator)[1]

        full_xpath = f"{base_xpath}{cousin_xpath}"
        return Element(  # type: ignore[return-value]
            locator=("xpath", full_xpath),
            shadowstep=self.shadowstep,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
        )

    @log_debug()
    def get_cousins(
        self,
        cousin_locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        depth_to_parent: int = 1,
        timeout: float = 30.0,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> list[Element]:
        """Get all cousin elements of the current element.

        Args:
            cousin_locator: Locator for the cousin elements.
            depth_to_parent: How many levels up to go before finding cousins.
            timeout: Maximum time to wait for elements.
            poll_frequency: How often to check for elements.
            ignored_exceptions: Exceptions to ignore during wait.

        Returns:
            List of found cousin elements.

        """
        depth_to_parent += 1
        clean_base_locator = self.utilities.remove_null_value(self.element.locator)
        current_xpath = self.converter.to_xpath(clean_base_locator)[1]
        up_xpath = "/".join([".."] * depth_to_parent)
        base_xpath = f"{current_xpath}/{up_xpath}" if up_xpath else current_xpath

        clean_cousin_locator = self.utilities.remove_null_value(cousin_locator)
        cousin_xpath = self.converter.to_xpath(clean_cousin_locator)[1]

        full_xpath = f"{base_xpath}{cousin_xpath}"
        return self.get_elements(("xpath", full_xpath), timeout, poll_frequency, ignored_exceptions)
