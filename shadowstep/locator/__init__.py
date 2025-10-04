"""Locator converter module for converting between different locator formats.

This module provides converters for:
- UiSelector strings
- XPath expressions
- Shadowstep dictionary format

Supported conversions:
- UiSelector ↔ XPath
- UiSelector ↔ Dict
- XPath ↔ Dict
- Dict → XPath (new)
- Dict → UiSelector (new)
"""

from shadowstep.locator.converter.dict_converter import DictConverter
from shadowstep.locator.converter.locator_converter import LocatorConverter
from shadowstep.locator.converter.ui_selector_converter import UiSelectorConverter
from shadowstep.locator.converter.xpath_converter import XPathConverter
from shadowstep.locator.ui_selector import UiSelector

__all__ = [
    "DictConverter",
    "LocatorConverter",
    "UiSelector",
    "UiSelectorConverter",
    "XPathConverter",
]
