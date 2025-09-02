# shadowstep/locator_converter/__init__.py
"""
Locator converter module for converting between different locator formats.

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

from shadowstep.locator_converter.dict_converter import DictConverter
from shadowstep.locator_converter.ui_selector_converter import UiSelectorConverter
from shadowstep.locator_converter.xpath_converter import XPathConverter

__all__ = [
    "DictConverter",
        "UiSelectorConverter",
    "XPathConverter",
]
