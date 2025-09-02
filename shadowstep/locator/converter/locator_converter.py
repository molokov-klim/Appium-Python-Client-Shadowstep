# shadowstep/locator/locator.py
"""
Unified LocatorConverter for converting between different locator formats.

This module provides a unified interface for converting between:
- UiSelector strings
- XPath expressions  
- Shadowstep dictionary format

This replaces the deprecated DeprecatedLocatorConverter with a modern,
well-architected solution.
"""

from __future__ import annotations

import logging
from typing import Any

from shadowstep.exceptions.shadowstep_exceptions import ConversionError
from shadowstep.locator.converter.dict_converter import DictConverter
from shadowstep.locator.converter.ui_selector_converter import UiSelectorConverter
from shadowstep.locator.ui_selector import UiSelector
from shadowstep.locator.converter.xpath_converter import XPathConverter

logger = logging.getLogger(__name__)


class LocatorConverter:
    """
    Unified converter for all locator formats.
    
    This class provides a single interface for converting between different
    locator formats, replacing the deprecated DeprecatedLocatorConverter.
    """

    def __init__(self):
        """Initialize the converter with all sub-converters."""
        self.logger = logger
        self.dict_converter = DictConverter()
        self.ui_selector_converter = UiSelectorConverter()
        self.xpath_converter = XPathConverter()

    def to_dict(self, selector: dict[str, Any] | tuple[str, str] | str | UiSelector) -> dict[str, Any]:
        """
        Convert any selector format to dictionary format.
        
        Args:
            selector: Selector in any supported format
            
        Returns:
            Dictionary representation of the selector
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            if isinstance(selector, dict):
                return selector
            elif isinstance(selector, UiSelector):
                return selector.to_dict()
            elif isinstance(selector, tuple) and len(selector) == 2:
                # XPath tuple format: ("xpath", "//*[@text='OK']")
                if selector[0] == "xpath":
                    return self.xpath_converter.xpath_to_dict(selector[1])
                else:
                    raise ValueError(f"Unsupported tuple format: {selector[0]}")
            elif isinstance(selector, str):
                if selector.strip().startswith("new UiSelector()"):
                    # UiSelector string
                    return self.ui_selector_converter.selector_to_dict(selector)
                else:
                    # Assume it's an XPath string
                    return self.xpath_converter.xpath_to_dict(selector)
            else:
                raise ValueError(f"Unsupported selector type: {type(selector)}")
        except Exception as e:
            raise ConversionError(f"Failed to convert to dict: {e}") from e

    def to_xpath(self, selector: dict[str, Any] | tuple[str, str] | str | UiSelector) -> tuple[str, str]:
        """
        Convert any selector format to XPath tuple format.
        
        Args:
            selector: Selector in any supported format
            
        Returns:
            Tuple in format ("xpath", "//*[@text='OK']")
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            if isinstance(selector, dict):
                xpath_str = self.dict_converter.dict_to_xpath(selector)
                return ("xpath", xpath_str)
            elif isinstance(selector, UiSelector):
                # UiSelector DSL -> dict -> xpath
                selector_dict = selector.to_dict()
                xpath_str = self.dict_converter.dict_to_xpath(selector_dict)
                return ("xpath", xpath_str)
            elif isinstance(selector, tuple) and len(selector) == 2:
                if selector[0] == "xpath":
                    return selector
                else:
                    raise ValueError(f"Unsupported tuple format: {selector[0]}")
            elif isinstance(selector, str):
                if selector.strip().startswith("new UiSelector()"):
                    # UiSelector string -> dict -> xpath
                    selector_dict = self.ui_selector_converter.selector_to_dict(selector)
                    xpath_str = self.dict_converter.dict_to_xpath(selector_dict)
                    return ("xpath", xpath_str)
                else:
                    # Assume it's already an XPath string
                    return ("xpath", selector)
            else:
                raise ValueError(f"Unsupported selector type: {type(selector)}")
        except Exception as e:
            raise ConversionError(f"Failed to convert to xpath: {e}") from e

    def to_uiselector(self, selector: dict[str, Any] | tuple[str, str] | str | UiSelector) -> str:
        """
        Convert any selector format to UiSelector string.
        
        Args:
            selector: Selector in any supported format
            
        Returns:
            UiSelector string in format "new UiSelector().text('OK');"
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            if isinstance(selector, dict):
                return self.dict_converter.dict_to_ui_selector(selector)
            elif isinstance(selector, UiSelector):
                # UiSelector DSL -> string
                return str(selector)
            elif isinstance(selector, tuple) and len(selector) == 2:
                if selector[0] == "xpath":
                    # XPath tuple -> dict -> uiselector
                    selector_dict = self.xpath_converter.xpath_to_dict(selector[1])
                    return self.dict_converter.dict_to_ui_selector(selector_dict)
                else:
                    raise ValueError(f"Unsupported tuple format: {selector[0]}")
            elif isinstance(selector, str):
                if selector.strip().startswith("new UiSelector()"):
                    return selector
                else:
                    # XPath string -> dict -> uiselector
                    selector_dict = self.xpath_converter.xpath_to_dict(selector)
                    return self.dict_converter.dict_to_ui_selector(selector_dict)
            else:
                raise ValueError(f"Unsupported selector type: {type(selector)}")
        except Exception as e:
            raise ConversionError(f"Failed to convert to uiselector: {e}") from e

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
        """
        Validate selector format and content.
        
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
        elif isinstance(selector, tuple) and len(selector) == 2:
            if selector[0] != "xpath":
                raise ValueError(f"Unsupported tuple format: {selector[0]}")
            # Basic XPath validation
            if not selector[1] or not isinstance(selector[1], str):
                raise ValueError("XPath string cannot be empty")
        elif isinstance(selector, str):
            if not selector.strip():
                raise ValueError("Selector string cannot be empty")
        else:
            raise ValueError(f"Unsupported selector type: {type(selector)}")
