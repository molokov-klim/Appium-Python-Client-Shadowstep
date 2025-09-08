# shadowstep/locator/map/dict_to_xpath.py
"""
Mapping from Shadowstep Dict format to XPath expressions.

This module provides functions to convert Shadowstep dictionary locators
to XPath expressions with proper attribute mapping and hierarchy handling.
"""

from typing import Any

from shadowstep.locator.types.shadowstep_dict import ShadowstepDictAttribute


def dict_to_xpath_attribute(attr: ShadowstepDictAttribute, value: Any) -> str:
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


def is_hierarchical_attribute(attr: ShadowstepDictAttribute) -> bool:
    """
    Check if attribute represents hierarchical relationship.
    
    Args:
        attr: Dictionary attribute enum
        
    Returns:
        True if attribute is hierarchical
    """
    return attr in (ShadowstepDictAttribute.CHILD_SELECTOR, ShadowstepDictAttribute.FROM_PARENT, ShadowstepDictAttribute.SIBLING)


def get_xpath_for_hierarchical_attribute(attr: ShadowstepDictAttribute, nested_xpath: str) -> str:
    """
    Get XPath expression for hierarchical attributes.
    
    Args:
        attr: Hierarchical attribute enum
        nested_xpath: XPath expression for nested selector
        
    Returns:
        XPath expression with hierarchy
    """
    if attr == ShadowstepDictAttribute.CHILD_SELECTOR:
        return f"/{nested_xpath.lstrip('/')}"
    if attr == ShadowstepDictAttribute.FROM_PARENT:
        return f"/..//{nested_xpath.lstrip('/')}"
    if attr == ShadowstepDictAttribute.SIBLING:
        return f"/following-sibling::{nested_xpath.lstrip('/')}"
    raise ValueError(f"Unsupported hierarchical attribute: {attr}")


# Mapping dictionary for quick lookup
DICT_TO_XPATH_MAPPING = {  # type: ignore
    ShadowstepDictAttribute.TEXT: lambda v: f'@text="{v}"',
    ShadowstepDictAttribute.TEXT_CONTAINS: lambda v: f'contains(@text, "{v}")',
    ShadowstepDictAttribute.TEXT_STARTS_WITH: lambda v: f'starts-with(@text, "{v}")',
    ShadowstepDictAttribute.TEXT_MATCHES: lambda v: f'matches(@text, "{v}")',
    
    ShadowstepDictAttribute.DESCRIPTION: lambda v: f'@content-desc="{v}"',
    ShadowstepDictAttribute.DESCRIPTION_CONTAINS: lambda v: f'contains(@content-desc, "{v}")',
    ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH: lambda v: f'starts-with(@content-desc, "{v}")',
    ShadowstepDictAttribute.DESCRIPTION_MATCHES: lambda v: f'matches(@content-desc, "{v}")',
    
    ShadowstepDictAttribute.RESOURCE_ID: lambda v: f'@resource-id="{v}"',
    ShadowstepDictAttribute.RESOURCE_ID_MATCHES: lambda v: f'matches(@resource-id, "{v}")',
    ShadowstepDictAttribute.PACKAGE_NAME: lambda v: f'@package="{v}"',
    ShadowstepDictAttribute.PACKAGE_NAME_MATCHES: lambda v: f'matches(@package, "{v}")',
    
    ShadowstepDictAttribute.CLASS_NAME: lambda v: f'@class="{v}"',
    ShadowstepDictAttribute.CLASS_NAME_MATCHES: lambda v: f'matches(@class, "{v}")',
    
    ShadowstepDictAttribute.CHECKABLE: lambda v: f'@checkable="{str(v).lower()}"',
    ShadowstepDictAttribute.CHECKED: lambda v: f'@checked="{str(v).lower()}"',
    ShadowstepDictAttribute.CLICKABLE: lambda v: f'@clickable="{str(v).lower()}"',
    ShadowstepDictAttribute.ENABLED: lambda v: f'@enabled="{str(v).lower()}"',
    ShadowstepDictAttribute.FOCUSABLE: lambda v: f'@focusable="{str(v).lower()}"',
    ShadowstepDictAttribute.FOCUSED: lambda v: f'@focused="{str(v).lower()}"',
    ShadowstepDictAttribute.LONG_CLICKABLE: lambda v: f'@long-clickable="{str(v).lower()}"',
    ShadowstepDictAttribute.SCROLLABLE: lambda v: f'@scrollable="{str(v).lower()}"',
    ShadowstepDictAttribute.SELECTED: lambda v: f'@selected="{str(v).lower()}"',
    ShadowstepDictAttribute.PASSWORD: lambda v: f'@password="{str(v).lower()}"',
    
    ShadowstepDictAttribute.INDEX: lambda v: f"position()={int(v) + 1}",
    ShadowstepDictAttribute.INSTANCE: lambda v: f"[{int(v) + 1}]",
}
