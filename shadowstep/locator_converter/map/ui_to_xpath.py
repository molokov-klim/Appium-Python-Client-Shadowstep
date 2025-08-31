# shadowstep/locator_converter/map/ui_to_xpath.py
from collections.abc import Callable
from typing import Any

from shadowstep.locator_converter.types.ui_selector import UiAttribute


def _handle_child_selector(child_xpath: str) -> str:
    """
    Handle childSelector method by appending child XPath.

    Args:
        child_xpath: The XPath string for the child selector

    Returns:
        XPath string with child appended
    """
    return f'/{child_xpath}'


def _handle_from_parent(parent_xpath: str) -> str:
    """
    Handle fromParent method by going to parent and then to specified element.

    Args:
        parent_xpath: The XPath string for the parent selector

    Returns:
        XPath string with parent navigation
    """
    return f'/..{parent_xpath}'


UI_TO_XPATH: dict[UiAttribute, Callable[[Any], str]] = {
    # --- text-based ---
    UiAttribute.TEXT: lambda v: f'[@text="{v}"]',
    UiAttribute.TEXT_CONTAINS: lambda v: f'[contains(@text, "{v}")]',
    UiAttribute.TEXT_STARTS_WITH: lambda v: f'[starts-with(@text, "{v}")]',
    UiAttribute.TEXT_MATCHES: lambda v: f'[matches(@text, "{v}")]',  # Appium >= 2

    # --- description ---
    UiAttribute.DESCRIPTION: lambda v: f'[@content-desc="{v}"]',
    UiAttribute.DESCRIPTION_CONTAINS: lambda v: f'[contains(@content-desc, "{v}")]',
    UiAttribute.DESCRIPTION_STARTS_WITH: lambda v: f'[starts-with(@content-desc, "{v}")]',
    UiAttribute.DESCRIPTION_MATCHES: lambda v: f'[matches(@content-desc, "{v}")]',

    # --- resource id / package ---
    UiAttribute.RESOURCE_ID: lambda v: f'[@resource-id="{v}"]',
    UiAttribute.RESOURCE_ID_MATCHES: lambda v: f'[matches(@resource-id, "{v}")]',
    UiAttribute.PACKAGE_NAME: lambda v: f'[@package="{v}"]',
    UiAttribute.PACKAGE_NAME_MATCHES: lambda v: f'[matches(@package, "{v}")]',

    # --- class ---
    UiAttribute.CLASS_NAME: lambda v: f'[@class="{v}"]',
    UiAttribute.CLASS_NAME_MATCHES: lambda v: f'[matches(@class, "{v}")]',

    # --- bool props ---
    UiAttribute.CHECKABLE: lambda v: f'[@checkable="{str(v).lower()}"]',
    UiAttribute.CHECKED: lambda v: f'[@checked="{str(v).lower()}"]',
    UiAttribute.CLICKABLE: lambda v: f'[@clickable="{str(v).lower()}"]',
    UiAttribute.ENABLED: lambda v: f'[@enabled="{str(v).lower()}"]',
    UiAttribute.FOCUSABLE: lambda v: f'[@focusable="{str(v).lower()}"]',
    UiAttribute.FOCUSED: lambda v: f'[@focused="{str(v).lower()}"]',
    UiAttribute.LONG_CLICKABLE: lambda v: f'[@long-clickable="{str(v).lower()}"]',
    UiAttribute.SCROLLABLE: lambda v: f'[@scrollable="{str(v).lower()}"]',
    UiAttribute.SELECTED: lambda v: f'[@selected="{str(v).lower()}"]',
    UiAttribute.PASSWORD: lambda v: f'[@password="{str(v).lower()}"]',

    # --- numeric ---
    UiAttribute.INDEX: lambda v: f'[position()={int(v) + 1}]',
    UiAttribute.INSTANCE: lambda v: f'[{int(v) + 1}]',

    # --- hierarchy ---
    UiAttribute.CHILD_SELECTOR: lambda v: _handle_child_selector(v),
    UiAttribute.FROM_PARENT: lambda v: _handle_from_parent(v),
}


def get_xpath_for_method(method: UiAttribute, value: Any) -> str:
    """
    Get XPath predicate for a specific UiSelector method and value.

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
    """
    Check if a method requires special hierarchical handling.

    Args:
        method: The UiSelector method to check

    Returns:
        True if method is hierarchical (childSelector, fromParent)
    """
    return method in (UiAttribute.CHILD_SELECTOR, UiAttribute.FROM_PARENT)

def is_logic_method(method: UiAttribute) -> bool:
    return method in (UiAttribute.OR, UiAttribute.AND)

def get_supported_methods() -> list[UiAttribute]:
    """
    Get list of all supported UiSelector methods.

    Returns:
        List of supported UiMethod enum values
    """
    return list(UI_TO_XPATH.keys())
