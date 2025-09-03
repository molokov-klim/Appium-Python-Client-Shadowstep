# shadowstep/locator/map/dict_to_xpath.py
"""
Mapping from Shadowstep Dict format to XPath expressions.

This module provides functions to convert Shadowstep dictionary locators
to XPath expressions with proper attribute mapping and hierarchy handling.
"""

from typing import Any

from shadowstep.locator.types.shadowstep_dict import DictAttribute


def dict_to_xpath_attribute(attr: DictAttribute, value: Any) -> str:
    """
    Convert a single dictionary attribute to XPath expression.
    
    Args:
        attr: Dictionary attribute enum
        value: Attribute value
        
    Returns:
        XPath expression for the attribute
        
    Raises:
        ValueError: If attribute is not supported
    """
    if attr in DICT_TO_XPATH_MAPPING:
        return DICT_TO_XPATH_MAPPING[attr](value)
    raise ValueError(f"Unsupported attribute for XPath conversion: {attr}")


def is_hierarchical_attribute(attr: DictAttribute) -> bool:
    """
    Check if attribute represents hierarchical relationship.
    
    Args:
        attr: Dictionary attribute enum
        
    Returns:
        True if attribute is hierarchical
    """
    return attr in (DictAttribute.CHILD_SELECTOR, DictAttribute.FROM_PARENT, DictAttribute.SIBLING)


def get_xpath_for_hierarchical_attribute(attr: DictAttribute, nested_xpath: str) -> str:
    """
    Get XPath expression for hierarchical attributes.
    
    Args:
        attr: Hierarchical attribute enum
        nested_xpath: XPath expression for nested selector
        
    Returns:
        XPath expression with hierarchy
    """
    if attr == DictAttribute.CHILD_SELECTOR:
        return f"/{nested_xpath.lstrip('/')}"
    if attr == DictAttribute.FROM_PARENT:
        return f"/..//{nested_xpath.lstrip('/')}"
    if attr == DictAttribute.SIBLING:
        return f"/following-sibling::{nested_xpath.lstrip('/')}"
    raise ValueError(f"Unsupported hierarchical attribute: {attr}")


# Mapping dictionary for quick lookup
DICT_TO_XPATH_MAPPING = {  # type: ignore
    DictAttribute.TEXT: lambda v: f'@text="{v}"',
    DictAttribute.TEXT_CONTAINS: lambda v: f'contains(@text, "{v}")',
    DictAttribute.TEXT_STARTS_WITH: lambda v: f'starts-with(@text, "{v}")',
    DictAttribute.TEXT_MATCHES: lambda v: f'matches(@text, "{v}")',
    
    DictAttribute.DESCRIPTION: lambda v: f'@content-desc="{v}"',
    DictAttribute.DESCRIPTION_CONTAINS: lambda v: f'contains(@content-desc, "{v}")',
    DictAttribute.DESCRIPTION_STARTS_WITH: lambda v: f'starts-with(@content-desc, "{v}")',
    DictAttribute.DESCRIPTION_MATCHES: lambda v: f'matches(@content-desc, "{v}")',
    
    DictAttribute.RESOURCE_ID: lambda v: f'@resource-id="{v}"',
    DictAttribute.RESOURCE_ID_MATCHES: lambda v: f'matches(@resource-id, "{v}")',
    DictAttribute.PACKAGE_NAME: lambda v: f'@package="{v}"',
    DictAttribute.PACKAGE_NAME_MATCHES: lambda v: f'matches(@package, "{v}")',
    
    DictAttribute.CLASS_NAME: lambda v: f'@class="{v}"',
    DictAttribute.CLASS_NAME_MATCHES: lambda v: f'matches(@class, "{v}")',
    
    DictAttribute.CHECKABLE: lambda v: f'@checkable="{str(v).lower()}"',
    DictAttribute.CHECKED: lambda v: f'@checked="{str(v).lower()}"',
    DictAttribute.CLICKABLE: lambda v: f'@clickable="{str(v).lower()}"',
    DictAttribute.ENABLED: lambda v: f'@enabled="{str(v).lower()}"',
    DictAttribute.FOCUSABLE: lambda v: f'@focusable="{str(v).lower()}"',
    DictAttribute.FOCUSED: lambda v: f'@focused="{str(v).lower()}"',
    DictAttribute.LONG_CLICKABLE: lambda v: f'@long-clickable="{str(v).lower()}"',
    DictAttribute.SCROLLABLE: lambda v: f'@scrollable="{str(v).lower()}"',
    DictAttribute.SELECTED: lambda v: f'@selected="{str(v).lower()}"',
    DictAttribute.PASSWORD: lambda v: f'@password="{str(v).lower()}"',
    
    DictAttribute.INDEX: lambda v: f"position()={int(v) + 1}",
    DictAttribute.INSTANCE: lambda v: f"[{int(v) + 1}]",
}
