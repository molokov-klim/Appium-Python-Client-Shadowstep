# shadowstep/locator_converter/map/ui_to_xpath.py
from collections.abc import Callable
from typing import Any

from shadowstep.locator_converter.types.ui_selector import UiMethod


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


UI_TO_XPATH: dict[UiMethod, Callable[[Any], str]] = {
    # --- text-based ---
    UiMethod.TEXT: lambda v: f'[@text="{v}"]',
    UiMethod.TEXT_CONTAINS: lambda v: f'[contains(@text, "{v}")]',
    UiMethod.TEXT_STARTS_WITH: lambda v: f'[starts-with(@text, "{v}")]',
    UiMethod.TEXT_MATCHES: lambda v: f'[matches(@text, "{v}")]',  # Appium >= 2

    # --- description ---
    UiMethod.DESCRIPTION: lambda v: f'[@content-desc="{v}"]',
    UiMethod.DESCRIPTION_CONTAINS: lambda v: f'[contains(@content-desc, "{v}")]',
    UiMethod.DESCRIPTION_STARTS_WITH: lambda v: f'[starts-with(@content-desc, "{v}")]',
    UiMethod.DESCRIPTION_MATCHES: lambda v: f'[matches(@content-desc, "{v}")]',

    # --- resource id / package ---
    UiMethod.RESOURCE_ID: lambda v: f'[@resource-id="{v}"]',
    UiMethod.RESOURCE_ID_MATCHES: lambda v: f'[matches(@resource-id, "{v}")]',
    UiMethod.PACKAGE_NAME: lambda v: f'[@package="{v}"]',
    UiMethod.PACKAGE_NAME_MATCHES: lambda v: f'[matches(@package, "{v}")]',

    # --- class ---
    UiMethod.CLASS_NAME: lambda v: f'[@class="{v}"]',
    UiMethod.CLASS_NAME_MATCHES: lambda v: f'[matches(@class, "{v}")]',

    # --- bool props ---
    UiMethod.CHECKABLE: lambda v: f'[@checkable="{str(v).lower()}"]',
    UiMethod.CHECKED: lambda v: f'[@checked="{str(v).lower()}"]',
    UiMethod.CLICKABLE: lambda v: f'[@clickable="{str(v).lower()}"]',
    UiMethod.ENABLED: lambda v: f'[@enabled="{str(v).lower()}"]',
    UiMethod.FOCUSABLE: lambda v: f'[@focusable="{str(v).lower()}"]',
    UiMethod.FOCUSED: lambda v: f'[@focused="{str(v).lower()}"]',
    UiMethod.LONG_CLICKABLE: lambda v: f'[@long-clickable="{str(v).lower()}"]',
    UiMethod.SCROLLABLE: lambda v: f'[@scrollable="{str(v).lower()}"]',
    UiMethod.SELECTED: lambda v: f'[@selected="{str(v).lower()}"]',
    UiMethod.PASSWORD: lambda v: f'[@password="{str(v).lower()}"]',

    # --- numeric ---
    UiMethod.INDEX: lambda v: f'[position()={int(v) + 1}]',
    UiMethod.INSTANCE: lambda v: f'[{int(v) + 1}]',

    # --- hierarchy ---
    # These are handled specially in the converter logic
    UiMethod.CHILD_SELECTOR: lambda v: _handle_child_selector(v),
    UiMethod.FROM_PARENT: lambda v: _handle_from_parent(v),
}


def get_xpath_for_method(method: UiMethod, value: Any) -> str:
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


def is_hierarchical_method(method: UiMethod) -> bool:
    """
    Check if a method requires special hierarchical handling.

    Args:
        method: The UiSelector method to check

    Returns:
        True if method is hierarchical (childSelector, fromParent)
    """
    return method in (UiMethod.CHILD_SELECTOR, UiMethod.FROM_PARENT)

def is_logic_method(method: UiMethod) -> bool:
    return method in (UiMethod.OR, UiMethod.AND)

def get_supported_methods() -> list[UiMethod]:
    """
    Get list of all supported UiSelector methods.

    Returns:
        List of supported UiMethod enum values
    """
    return list(UI_TO_XPATH.keys())
