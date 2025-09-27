"""Mapping from UiSelector attributes to XPath format.

This module provides the mapping dictionary and utility functions
for converting UiSelector attributes to their corresponding XPath
predicates with proper value formatting and hierarchical handling.
"""
# shadowstep/locator/map/ui_to_xpath.py
from collections.abc import Callable
from typing import Any

from shadowstep.locator.types.ui_selector import UiAttribute
from shadowstep.locator.types.xpath import XPathAttribute


def _handle_child_selector(child_xpath: str) -> str:
    """Handle childSelector method by appending child XPath.

    Args:
        child_xpath: The XPath string for the child selector

    Returns:
        XPath string with child appended

    """
    return f"/{child_xpath}"


def _handle_from_parent(parent_xpath: str) -> str:
    """Handle fromParent method by going to parent and then to specified element.

    Args:
        parent_xpath: The XPath string for the parent selector

    Returns:
        XPath string with parent dom

    """
    return f"/..{parent_xpath}"


UI_TO_XPATH: dict[UiAttribute, Callable[[str], str]] = {
    # --- text-based ---
    UiAttribute.TEXT: lambda v: f"[{XPathAttribute.TEXT.value}'{v}']",
    UiAttribute.TEXT_CONTAINS: lambda v: f"[{XPathAttribute.TEXT_CONTAINS.value}'{v}')]",
    UiAttribute.TEXT_STARTS_WITH: lambda v: f"[{XPathAttribute.TEXT_STARTS_WITH.value}'{v}')]",
    UiAttribute.TEXT_MATCHES: lambda v: f"[{XPathAttribute.TEXT_MATCHES.value}'{v}')]",  # Appium >= 2

    # --- description ---
    UiAttribute.DESCRIPTION: lambda v: f"[{XPathAttribute.DESCRIPTION.value}'{v}']",
    UiAttribute.DESCRIPTION_CONTAINS: lambda v: f"[{XPathAttribute.DESCRIPTION_CONTAINS.value}'{v}')]",
    UiAttribute.DESCRIPTION_STARTS_WITH: lambda v: f"[{XPathAttribute.DESCRIPTION_STARTS_WITH.value}'{v}')]",
    UiAttribute.DESCRIPTION_MATCHES: lambda v: f"[{XPathAttribute.DESCRIPTION_MATCHES.value}'{v}')]",

    # --- resource id / package ---
    UiAttribute.RESOURCE_ID: lambda v: f"[{XPathAttribute.RESOURCE_ID.value}'{v}']",
    UiAttribute.RESOURCE_ID_MATCHES: lambda v: f"[{XPathAttribute.RESOURCE_ID_MATCHES.value}'{v}')]",
    UiAttribute.PACKAGE_NAME: lambda v: f"[{XPathAttribute.PACKAGE_NAME.value}'{v}']",
    UiAttribute.PACKAGE_NAME_MATCHES: lambda v: f"[{XPathAttribute.PACKAGE_NAME_MATCHES.value}'{v}')]",

    # --- class ---
    UiAttribute.CLASS_NAME: lambda v: f"[{XPathAttribute.CLASS_NAME.value}'{v}']",
    UiAttribute.CLASS_NAME_MATCHES: lambda v: f"[{XPathAttribute.CLASS_NAME_MATCHES.value}'{v}')]",

    # --- bool props ---
    UiAttribute.CHECKABLE: lambda v: f"[{XPathAttribute.CHECKABLE.value}'{str(v).lower()}']",
    UiAttribute.CHECKED: lambda v: f"[{XPathAttribute.CHECKED.value}'{str(v).lower()}']",
    UiAttribute.CLICKABLE: lambda v: f"[{XPathAttribute.CLICKABLE.value}'{str(v).lower()}']",
    UiAttribute.ENABLED: lambda v: f"[{XPathAttribute.ENABLED.value}'{str(v).lower()}']",
    UiAttribute.FOCUSABLE: lambda v: f"[{XPathAttribute.FOCUSABLE.value}'{str(v).lower()}']",
    UiAttribute.FOCUSED: lambda v: f"[{XPathAttribute.FOCUSED.value}'{str(v).lower()}']",
    UiAttribute.LONG_CLICKABLE: lambda v: f"[{XPathAttribute.LONG_CLICKABLE.value}'{str(v).lower()}']",
    UiAttribute.SCROLLABLE: lambda v: f"[{XPathAttribute.SCROLLABLE.value}'{str(v).lower()}']",
    UiAttribute.SELECTED: lambda v: f"[{XPathAttribute.SELECTED.value}'{str(v).lower()}']",
    UiAttribute.PASSWORD: lambda v: f"[{XPathAttribute.PASSWORD.value}'{str(v).lower()}']",

    # --- numeric ---
    UiAttribute.INDEX: lambda v: f"[{XPathAttribute.INDEX.value}{int(v) + 1}]",
    UiAttribute.INSTANCE: lambda v: f"[{int(v) + 1}]",

    # --- hierarchy ---
    UiAttribute.CHILD_SELECTOR: lambda v: _handle_child_selector(v),
    UiAttribute.FROM_PARENT: lambda v: _handle_from_parent(v),
}


def get_xpath_for_method(method: UiAttribute, value: Any) -> str:
    """Get XPath predicate for a specific UiSelector method and value.

    Args:
        method: The UiSelector method
        value: The value for the method

    Returns:
        XPath predicate string

    Raises:
        KeyError: If method is not supported

    """
    if method not in UI_TO_XPATH:
        raise KeyError(f"Unsupported UiSelector method: {method}")

    return UI_TO_XPATH[method](value)


def is_hierarchical_method(method: UiAttribute) -> bool:
    """Check if a method requires special hierarchical handling.

    Args:
        method: The UiSelector method to check

    Returns:
        True if method is hierarchical (childSelector, fromParent)

    """
    return method in (UiAttribute.CHILD_SELECTOR, UiAttribute.FROM_PARENT)

def get_supported_methods() -> list[UiAttribute]:
    """Get list of all supported UiSelector methods.

    Returns:
        List of supported UiMethod enum values

    """
    return list(UI_TO_XPATH.keys())
