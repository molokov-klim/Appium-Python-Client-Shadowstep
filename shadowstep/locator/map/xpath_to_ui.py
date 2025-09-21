# shadowstep/locator/map/xpath_to_ui.py
from collections.abc import Callable
from typing import Any

from shadowstep.locator.types.ui_selector import UiAttribute
from shadowstep.locator.types.xpath import XPathAttribute


def _handle_child_selector(child_ui: str) -> str:
    """
    Handle childSelector method by appending child UiSelector.

    Args:
        child_ui: The UiSelector string for the child selector

    Returns:
        UiSelector string with child appended
    """
    return f".childSelector({child_ui})"


def _handle_from_parent(parent_ui: str) -> str:
    """
    Handle fromParent method by going to parent and then to specified element.

    Args:
        parent_ui: The UiSelector string for the parent selector

    Returns:
        UiSelector string with parent dom
    """
    return f".fromParent({parent_ui})"


XPATH_TO_UI: dict[XPathAttribute, Callable[[str], str]] = {
    # --- text-based ---
    XPathAttribute.TEXT: lambda v: f"{UiAttribute.TEXT.value}({v})",
    XPathAttribute.TEXT_CONTAINS: lambda v: f"{UiAttribute.TEXT_CONTAINS.value}({v})",
    XPathAttribute.TEXT_STARTS_WITH: lambda v: f"{UiAttribute.TEXT_STARTS_WITH.value}({v})",
    XPathAttribute.TEXT_MATCHES: lambda v: f"{UiAttribute.TEXT_MATCHES.value}({v})",
    # --- description ---
    XPathAttribute.DESCRIPTION: lambda v: f"{UiAttribute.DESCRIPTION.value}({v})",
    XPathAttribute.DESCRIPTION_CONTAINS: lambda v: f"{UiAttribute.DESCRIPTION_CONTAINS.value}({v})",
    XPathAttribute.DESCRIPTION_STARTS_WITH: lambda v: f"{UiAttribute.DESCRIPTION_STARTS_WITH.value}({v})",
    XPathAttribute.DESCRIPTION_MATCHES: lambda v: f"{UiAttribute.DESCRIPTION_MATCHES.value}({v})",
    # --- resource id / package ---
    XPathAttribute.RESOURCE_ID: lambda v: f"{UiAttribute.RESOURCE_ID.value}({v})",
    XPathAttribute.RESOURCE_ID_MATCHES: lambda v: f"{UiAttribute.RESOURCE_ID_MATCHES.value}({v})",
    XPathAttribute.PACKAGE_NAME: lambda v: f"{UiAttribute.PACKAGE_NAME.value}({v})",
    XPathAttribute.PACKAGE_NAME_MATCHES: lambda v: f"{UiAttribute.PACKAGE_NAME_MATCHES.value}({v})",
    # --- class ---
    XPathAttribute.CLASS_NAME: lambda v: f"{UiAttribute.CLASS_NAME.value}({v})",
    XPathAttribute.CLASS_NAME_MATCHES: lambda v: f"{UiAttribute.CLASS_NAME_MATCHES.value}({v})",
    # --- bool props ---
    XPathAttribute.CHECKABLE: lambda v: f"{UiAttribute.CHECKABLE.value}({v})",
    XPathAttribute.CHECKED: lambda v: f"{UiAttribute.CHECKED.value}({v})",
    XPathAttribute.CLICKABLE: lambda v: f"{UiAttribute.CLICKABLE.value}({v})",
    XPathAttribute.ENABLED: lambda v: f"{UiAttribute.ENABLED.value}({v})",
    XPathAttribute.FOCUSABLE: lambda v: f"{UiAttribute.FOCUSABLE.value}({v})",
    XPathAttribute.FOCUSED: lambda v: f"{UiAttribute.FOCUSED.value}({v})",
    XPathAttribute.LONG_CLICKABLE: lambda v: f"{UiAttribute.CLICKABLE.value}({v})",
    XPathAttribute.SCROLLABLE: lambda v: f"{UiAttribute.SCROLLABLE.value}({v})",
    XPathAttribute.SELECTED: lambda v: f"{UiAttribute.SELECTED.value}({v})",
    XPathAttribute.PASSWORD: lambda v: f"{UiAttribute.PASSWORD.value}({v})",
    # --- numeric ---
    XPathAttribute.INDEX: lambda v: f"{UiAttribute.INDEX.value}({v})",
    XPathAttribute.INSTANCE: lambda v: f"{UiAttribute.INSTANCE.value}({v})",
    # --- hierarchy ---
    XPathAttribute.CHILD_SELECTOR: lambda v: _handle_child_selector(v),
    XPathAttribute.FROM_PARENT: lambda v: _handle_from_parent(v),
}


def get_ui_for_method(method: XPathAttribute, value: Any) -> str:
    """
    Get UiSelector method call for a specific XPath attribute and value.

    Args:
        method: The XPath attribute
        value: The value for the method

    Returns:
        UiSelector method call string

    Raises:
        KeyError: If method is not supported
    """
    if method not in XPATH_TO_UI:
        raise KeyError(f"Unsupported XPath attribute: {method}")

    return XPATH_TO_UI[method](value)


def is_hierarchical_xpath(method: XPathAttribute) -> bool:
    """
    Check if a method requires special hierarchical handling.

    Args:
        method: The XPath attribute to check

    Returns:
        True if method is hierarchical (childSelector, fromParent)
    """
    return method in (XPathAttribute.CHILD_SELECTOR, XPathAttribute.FROM_PARENT)


def get_supported_attributes() -> list[XPathAttribute]:
    """
    Get list of all supported XPath attributes.

    Returns:
        List of supported XPathAttribute enum values
    """
    return list(XPATH_TO_UI.keys())
