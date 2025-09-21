"""Element utilities module for Shadowstep framework.

This module provides utility functions for element operations,
including XPath generation, attribute extraction, and error handling.
"""
from __future__ import annotations

import logging
import re
import time
from typing import TYPE_CHECKING, Any

from lxml import etree  # type: ignore[import]
from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.locator import UiSelector
    from shadowstep.shadowstep import Shadowstep


class ElementUtilities:
    """Element utilities for Shadowstep framework."""

    def __init__(self, element: Element) -> None:
        """Initialize ElementUtilities.

        Args:
            element: The element to provide utilities for.

        """
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.logger: logging.Logger = logging.getLogger(get_current_func_name())

    def remove_null_value(self,
                          locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                          ) -> tuple[str, str] | dict[str, Any] | Element | UiSelector:
        """Remove null values from locator.

        Args:
            locator: The locator to clean.

        Returns:
            The cleaned locator.

        """
        self.logger.debug("%s", get_current_func_name())
        if isinstance(locator, tuple):
            by, value = locator
            # Remove parts like [@attr='null']
            value = re.sub(r"\[@[\w\-]+='null']", "", value)
            return by, value
        if isinstance(locator, dict):
            # Remove keys where value == 'null'
            return {k: v for k, v in locator.items() if v != "null"}
        return locator

    def extract_el_attrs_from_source(
            self, xpath_expr: str, page_source: str,
    ) -> list[dict[str, Any]]:
        """Parse page source and extract attributes of all elements matching XPath."""
        try:
            parser = etree.XMLParser(recover=True)  # type: ignore[attr-defined]
            root = etree.fromstring(page_source.encode("utf-8"), parser=parser)  # type: ignore[attr-defined]
            matches = root.xpath(self.remove_null_value(("xpath", xpath_expr)[1]))  # type: ignore[attr-defined]
            if not matches:
                self.logger.warning("No matches found for XPath: %s", xpath_expr)
                return []
            result: list[dict[str, Any]] = [
                {**{k: str(v) for k, v in el.attrib.items()}}  # type: ignore[attr-defined]
                for el in matches  # type: ignore[reportUnknownVariableType]
            ]
            self.logger.debug("Matched %d elements: %s", len(result), result)  # type: ignore[reportUnknownArgumentType]
            return result  # type: ignore[reportUnknownVariableType]  # noqa: TRY300
        except (etree.XPathEvalError, etree.XMLSyntaxError, UnicodeEncodeError) as error:  # type: ignore[attr-defined]
            self.logger.exception("Parsing error")  # type: ignore[reportUnknownArgumentType]
            if isinstance(error, etree.XPathEvalError):  # type: ignore[attr-defined]
                self.logger.exception("XPath: %s", xpath_expr)
            msg = f"Parsing error: {xpath_expr}"
            raise ShadowstepElementException(msg) from error

    def get_xpath(self) -> str:
        """Get XPath for the element.

        Returns:
            The XPath string.

        """
        self.logger.debug("%s", get_current_func_name())
        locator = self.remove_null_value(self.element.locator)
        if isinstance(locator, tuple):
            return locator[1]
        return self._get_xpath_by_driver()

    def _get_xpath_by_driver(self) -> str:
        """Get XPath by driver.

        Returns:
            The XPath string.

        """
        self.logger.debug("%s", get_current_func_name())
        try:
            attrs = self.element.get_attributes()
            if not attrs:
                msg = "Failed to retrieve attributes for XPath construction."
                raise ShadowstepElementException(msg)
            return self.element.utilities.build_xpath_from_attributes(attrs)
        except (AttributeError, KeyError, WebDriverException):
            self.logger.exception("Error forming XPath")
        return ""

    def handle_driver_error(self, error: Exception) -> None:
        """Handle driver errors.

        Args:
            error: The error to handle.

        """
        self.logger.warning("%s %s", get_current_func_name(), error)
        self.shadowstep.reconnect()
        time.sleep(0.3)

    def _build_xpath_attribute_condition(self, key: str, value: str) -> str:
        """Build XPath attribute condition based on value content."""
        if value is None or value == "null":  # type: ignore[reportUnnecessaryComparison]
            return f"[@{key}]"
        if "'" in value and '"' not in value:
            return f'[@{key}="{value}"]'
        if '"' in value and "'" not in value:
            return f"[@{key}='{value}']"
        if "'" in value and '"' in value:
            parts = value.split('"')
            escaped = "concat(" + ", ".join(
                f'"{part}"' if i % 2 == 0 else "'\"'" for i, part in enumerate(parts)) + ")"
            return f"[@{key}={escaped}]"
        return f"[@{key}='{value}']"

    def build_xpath_from_attributes(self, attrs: dict[str, Any]) -> str:
        """Build XPath from element attributes."""
        xpath = "//"
        element_type = attrs.get("class")
        except_attrs = ["hint", "selection-start", "selection-end", "extras"]

        # Start XPath with element class or wildcard
        if element_type:
            xpath += element_type
        else:
            xpath += "*"

        for key, value in attrs.items():
            if key in except_attrs:
                continue
            xpath += self._build_xpath_attribute_condition(key, value)
        return xpath

    def _ensure_session_alive(self) -> None:
        """Ensure session is alive."""
        self.logger.debug("%s", get_current_func_name())
        try:
            self.element.get_driver()
        except NoSuchDriverException:
            self.logger.warning("Reconnecting driver due to session issue")
            self.shadowstep.reconnect()
        except InvalidSessionIdException:
            self.logger.warning("Reconnecting driver due to session issue")
            self.shadowstep.reconnect()

    def _get_first_child_class(self, tries: int = 3) -> str:
        """Get first child class.

        Args:
            tries: Number of tries.

        Returns:
            The child class string.

        """
        self.logger.debug("%s", get_current_func_name())
        for _ in range(tries):
            try:
                parent_element = self
                parent_class = parent_element.element.get_attribute("class")
                child_elements = parent_element.element.get_elements(("xpath", "//*[1]"))
                for _i, child_element in enumerate(child_elements):
                    child_class = child_element.get_attribute("class")
                    if parent_class != child_class:
                        return str(child_class)
            except StaleElementReferenceException as error:  # noqa: PERF203
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.handle_driver_error(error)
                    continue
                raise
        return ""  # Return empty string if no child class found
