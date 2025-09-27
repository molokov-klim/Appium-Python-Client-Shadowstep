"""Unified LocatorConverter for converting between different locator formats.

This module provides a unified interface for converting between:
- UiSelector strings
- XPath expressions
- Shadowstep dictionary format

This replaces the deprecated DeprecatedLocatorConverter with a modern,
well-architected solution.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepConversionFailedError,
    ShadowstepEmptySelectorStringError,
    ShadowstepEmptyXPathError,
    ShadowstepUnsupportedSelectorFormatError,
    ShadowstepUnsupportedSelectorTypeError,
    ShadowstepUnsupportedTupleFormatError,
)
from shadowstep.locator.converter.dict_converter import DictConverter
from shadowstep.locator.converter.ui_selector_converter import UiSelectorConverter
from shadowstep.locator.converter.xpath_converter import XPathConverter
from shadowstep.locator.ui_selector import UiSelector
from shadowstep.utils.utils import get_current_func_name

logger = logging.getLogger(__name__)

# Constants
TUPLE_SELECTOR_LENGTH = 2

if TYPE_CHECKING:
    from shadowstep.element.element import Element


class LocatorConverter:
    """Unified converter for all locator formats.

    This class provides a single interface for converting between different
    locator formats, replacing the deprecated DeprecatedLocatorConverter.
    """

    def __init__(self):
        """Initialize the converter with all sub-converters."""
        self.logger = logger
        self.dict_converter = DictConverter()
        self.ui_selector_converter = UiSelectorConverter()
        self.xpath_converter = XPathConverter()

    def _raise_unsupported_selector_format_error(self, selector: Any) -> None:
        """Raise ShadowstepUnsupportedSelectorFormatError for unsupported selector format.
        
        Args:
            selector: The unsupported selector
            
        Raises:
            ShadowstepUnsupportedSelectorFormatError: Always raised

        """
        raise ShadowstepUnsupportedSelectorFormatError(selector)

    def to_dict(self, selector: tuple[str, str] | dict[str, Any] | Element | UiSelector | str) -> dict[str, Any]:
        """Convert any selector format to dictionary format.

        Args:
            selector: Selector in any supported format

        Returns:
            Dictionary representation of the selector

        Raises:
            ShadowstepConversionError: If conversion fails

        """
        try:
            from shadowstep.element.element import Element
            if isinstance(selector, Element):
                selector = cast("Element", selector.locator)
            if isinstance(selector, dict):
                return selector
            if isinstance(selector, tuple):
                return self.xpath_to_dict(selector[1])
            if isinstance(selector, str):
                if selector.startswith("new UiSelector"):
                    return self.uiselector_to_dict(selector)
                return self.xpath_to_dict(selector)
            if isinstance(selector, UiSelector):
                return self.uiselector_to_dict(selector.__str__())
            self._raise_unsupported_selector_format_error(selector)
        except Exception as e:
            raise ShadowstepConversionFailedError(get_current_func_name(), selector, str(e)) from e

    def to_xpath(self, selector: tuple[str, str] | dict[str, Any] | Element | UiSelector) -> tuple[str, str]:
        """Convert any selector format to XPath tuple format.

        Args:
            selector: Selector in any supported format

        Returns:
            Tuple in format ("xpath", "//*[@text='OK']")

        Raises:
            ShadowstepConversionError: If conversion fails

        """
        try:
            from shadowstep.element.element import Element
            if isinstance(selector, Element):
                selector = cast("Element", selector.locator)
            if isinstance(selector, dict):
                return "xpath", self.dict_to_xpath(selector)
            if isinstance(selector, tuple):
                return selector
            if isinstance(selector, str):
                if selector.startswith("new UiSelector"):
                    return "xpath", self.ui_selector_converter.selector_to_xpath(selector)
                return "xpath", selector
            if isinstance(selector, UiSelector):
                return "xpath", self.uiselector_to_xpath(selector.__str__())
            self._raise_unsupported_selector_format_error(selector)
        except Exception as e:
            raise ShadowstepConversionFailedError(get_current_func_name(), selector, str(e)) from e

    def to_uiselector(self, selector: tuple[str, str] | dict[str, Any] | Element | UiSelector) -> str:
        """Convert any selector format to UiSelector string.

        Args:
            selector: Selector in any supported format

        Returns:
            UiSelector string in format "new UiSelector().text('OK');"

        Raises:
            ShadowstepConversionError: If conversion fails

        """
        try:
            from shadowstep.element.element import Element
            if isinstance(selector, Element):
                selector = cast("Element", selector.locator)
            if isinstance(selector, dict):
                return self.dict_to_uiselector(selector)
            if isinstance(selector, UiSelector):
                return selector.__str__()
            if isinstance(selector, tuple):
                return self.xpath_to_uiselector(selector[1])
            if isinstance(selector, str):
                if selector.startswith("new UiSelector"):
                    return selector
                return self.xpath_to_uiselector(selector)
            if isinstance(selector, UiSelector):
                return selector.__str__()
            self._raise_unsupported_selector_format_error(selector)
        except Exception as e:
            raise ShadowstepConversionFailedError(get_current_func_name(), selector, str(e)) from e

    # Convenience methods for direct conversion between specific formats
    def dict_to_xpath(self, selector_dict: dict[str, Any]) -> str:
        """Convert dictionary to XPath string."""
        return self.dict_converter.dict_to_xpath(selector_dict)

    def dict_to_uiselector(self, selector_dict: dict[str, Any]) -> str:
        """Convert dictionary to UiSelector string."""
        return self.dict_converter.dict_to_ui_selector(selector_dict)

    def xpath_to_dict(self, xpath: str) -> dict[str, Any]:
        """Convert XPath string to dictionary."""
        return self.xpath_converter.xpath_to_dict(xpath)

    def xpath_to_uiselector(self, xpath: str) -> str:
        """Convert XPath string to UiSelector string."""
        selector_dict = self.xpath_converter.xpath_to_dict(xpath)
        return self.dict_converter.dict_to_ui_selector(selector_dict)

    def uiselector_to_dict(self, uiselector: str) -> dict[str, Any]:
        """Convert UiSelector string to dictionary."""
        return self.ui_selector_converter.selector_to_dict(uiselector)

    def uiselector_to_xpath(self, uiselector: str) -> str:
        """Convert UiSelector string to XPath string."""
        selector_dict = self.ui_selector_converter.selector_to_dict(uiselector)
        return self.dict_converter.dict_to_xpath(selector_dict)

    def validate_selector(self, selector: dict[str, Any] | tuple[str, str] | str | UiSelector) -> None:
        """Validate selector format and content.

        Args:
            selector: Selector to validate

        Raises:
            ValueError: If selector is invalid

        """
        if isinstance(selector, dict):
            self.dict_converter.validate_dict_selector(selector)
        elif isinstance(selector, UiSelector):
            # UiSelector DSL validation - convert to dict and validate
            selector_dict = selector.to_dict()
            self.dict_converter.validate_dict_selector(selector_dict)
        elif isinstance(selector, tuple) and len(selector) == TUPLE_SELECTOR_LENGTH:
            if selector[0] != "xpath":
                raise ShadowstepUnsupportedTupleFormatError(selector[0])
            # Basic XPath validation
            if not selector[1]:
                raise ShadowstepEmptyXPathError
        elif isinstance(selector, str):  # type: ignore[arg-type]
            if not selector.strip():
                raise ShadowstepEmptySelectorStringError
        else:
            raise ShadowstepUnsupportedSelectorTypeError(type(selector))
