# shadowstep/locator/map/dict_to_ui.py
"""
Mapping from Shadowstep Dict format to UiSelector expressions.

This module provides functions to convert Shadowstep dictionary locators
to UiSelector method calls with proper attribute mapping and hierarchy handling.
"""

from typing import Any

from shadowstep.locator.types.shadowstep_dict import DictAttribute
from shadowstep.locator.types.ui_selector import UiAttribute


def dict_to_ui_attribute(attr: DictAttribute, value: Any) -> str:
    """
    Convert a single dictionary attribute to UiSelector method call.
    
    Args:
        attr: Dictionary attribute enum
        value: Attribute value
        
    Returns:
        UiSelector method call string
        
    Raises:
        ValueError: If attribute is not supported
    """
    if attr in DICT_TO_UI_MAPPING:
        return DICT_TO_UI_MAPPING[attr](value)
    raise ValueError(f"Unsupported attribute for UiSelector conversion: {attr}")


def is_hierarchical_attribute(attr: DictAttribute) -> bool:
    """
    Check if attribute represents hierarchical relationship.
    
    Args:
        attr: Dictionary attribute enum
        
    Returns:
        True if attribute is hierarchical
    """
    return attr in (DictAttribute.CHILD_SELECTOR, DictAttribute.FROM_PARENT, DictAttribute.SIBLING)


def get_ui_method_for_hierarchical_attribute(attr: DictAttribute) -> str:
    """
    Get UiSelector method name for hierarchical attributes.
    
    Args:
        attr: Hierarchical attribute enum
        
    Returns:
        UiSelector method name
    """
    if attr == DictAttribute.CHILD_SELECTOR:
        return UiAttribute.CHILD_SELECTOR.value
    if attr == DictAttribute.FROM_PARENT:
        return UiAttribute.FROM_PARENT.value
    if attr == DictAttribute.SIBLING:
        return UiAttribute.SIBLING.value
    raise ValueError(f"Unsupported hierarchical attribute: {attr}")


# Mapping dictionary for quick lookup
DICT_TO_UI_MAPPING = {  # type: ignore
    DictAttribute.TEXT: lambda v: f'.{UiAttribute.TEXT.value}("{v}")',
    DictAttribute.TEXT_CONTAINS: lambda v: f'.{UiAttribute.TEXT_CONTAINS.value}("{v}")',
    DictAttribute.TEXT_STARTS_WITH: lambda v: f'.{UiAttribute.TEXT_STARTS_WITH.value}("{v}")',
    DictAttribute.TEXT_MATCHES: lambda v: f'.{UiAttribute.TEXT_MATCHES.value}("{v}")',
    
    DictAttribute.DESCRIPTION: lambda v: f'.{UiAttribute.DESCRIPTION.value}("{v}")',
    DictAttribute.DESCRIPTION_CONTAINS: lambda v: f'.{UiAttribute.DESCRIPTION_CONTAINS.value}("{v}")',
    DictAttribute.DESCRIPTION_STARTS_WITH: lambda v: f'.{UiAttribute.DESCRIPTION_STARTS_WITH.value}("{v}")',
    DictAttribute.DESCRIPTION_MATCHES: lambda v: f'.{UiAttribute.DESCRIPTION_MATCHES.value}("{v}")',
    
    DictAttribute.RESOURCE_ID: lambda v: f'.{UiAttribute.RESOURCE_ID.value}("{v}")',
    DictAttribute.RESOURCE_ID_MATCHES: lambda v: f'.{UiAttribute.RESOURCE_ID_MATCHES.value}("{v}")',
    DictAttribute.PACKAGE_NAME: lambda v: f'.{UiAttribute.PACKAGE_NAME.value}("{v}")',
    DictAttribute.PACKAGE_NAME_MATCHES: lambda v: f'.{UiAttribute.PACKAGE_NAME_MATCHES.value}("{v}")',
    
    DictAttribute.CLASS_NAME: lambda v: f'.{UiAttribute.CLASS_NAME.value}("{v}")',
    DictAttribute.CLASS_NAME_MATCHES: lambda v: f'.{UiAttribute.CLASS_NAME_MATCHES.value}("{v}")',
    
    DictAttribute.CHECKABLE: lambda v: f".{UiAttribute.CHECKABLE.value}({str(v).lower()})",
    DictAttribute.CHECKED: lambda v: f".{UiAttribute.CHECKED.value}({str(v).lower()})",
    DictAttribute.CLICKABLE: lambda v: f".{UiAttribute.CLICKABLE.value}({str(v).lower()})",
    DictAttribute.ENABLED: lambda v: f".{UiAttribute.ENABLED.value}({str(v).lower()})",
    DictAttribute.FOCUSABLE: lambda v: f".{UiAttribute.FOCUSABLE.value}({str(v).lower()})",
    DictAttribute.FOCUSED: lambda v: f".{UiAttribute.FOCUSED.value}({str(v).lower()})",
    DictAttribute.LONG_CLICKABLE: lambda v: f".{UiAttribute.LONG_CLICKABLE.value}({str(v).lower()})",
    DictAttribute.SCROLLABLE: lambda v: f".{UiAttribute.SCROLLABLE.value}({str(v).lower()})",
    DictAttribute.SELECTED: lambda v: f".{UiAttribute.SELECTED.value}({str(v).lower()})",
    DictAttribute.PASSWORD: lambda v: f".{UiAttribute.PASSWORD.value}({str(v).lower()})",
    
    DictAttribute.INDEX: lambda v: f".{UiAttribute.INDEX.value}({int(v)})",
    DictAttribute.INSTANCE: lambda v: f".{UiAttribute.INSTANCE.value}({int(v)})",
}
