"""Mapping from Shadowstep Dict format to UiSelector expressions.

This module provides functions to convert Shadowstep dictionary locators
to UiSelector method calls with proper attribute mapping and hierarchy handling.
"""
from __future__ import annotations

from collections.abc import Callable

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepUnsupportedAttributeForUiSelectorError,
    ShadowstepUnsupportedHierarchicalAttributeError,
)
from shadowstep.locator.types.shadowstep_dict import ShadowstepDictAttribute
from shadowstep.locator.types.ui_selector import UiAttribute


def dict_to_ui_attribute(attr: ShadowstepDictAttribute, value: str | float | bool | dict) -> str:  # noqa: FBT001
    """Convert a single dictionary attribute to UiSelector method call.

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
    raise ShadowstepUnsupportedAttributeForUiSelectorError(attr)


def is_hierarchical_attribute(attr: ShadowstepDictAttribute) -> bool:
    """Check if attribute represents hierarchical relationship.

    Args:
        attr: Dictionary attribute enum

    Returns:
        True if attribute is hierarchical

    """
    return attr in (ShadowstepDictAttribute.CHILD_SELECTOR, ShadowstepDictAttribute.FROM_PARENT,
                    ShadowstepDictAttribute.SIBLING)


def get_ui_method_for_hierarchical_attribute(attr: ShadowstepDictAttribute) -> str:
    """Get UiSelector method name for hierarchical attributes.

    Args:
        attr: Hierarchical attribute enum

    Returns:
        UiSelector method name

    """
    if attr == ShadowstepDictAttribute.CHILD_SELECTOR:
        return UiAttribute.CHILD_SELECTOR.value
    if attr == ShadowstepDictAttribute.FROM_PARENT:
        return UiAttribute.FROM_PARENT.value
    if attr == ShadowstepDictAttribute.SIBLING:
        return UiAttribute.SIBLING.value
    raise ShadowstepUnsupportedHierarchicalAttributeError(attr)


# Mapping dictionary for quick lookup
DICT_TO_UI_MAPPING: dict[ShadowstepDictAttribute, Callable[[str], str]] = {
    ShadowstepDictAttribute.TEXT: lambda v: f'.{UiAttribute.TEXT.value}("{v}")',
    ShadowstepDictAttribute.TEXT_CONTAINS: lambda v: f'.{UiAttribute.TEXT_CONTAINS.value}("{v}")',
    ShadowstepDictAttribute.TEXT_STARTS_WITH: lambda v: f'.{UiAttribute.TEXT_STARTS_WITH.value}("{v}")',
    ShadowstepDictAttribute.TEXT_MATCHES: lambda v: f'.{UiAttribute.TEXT_MATCHES.value}("{v}")',
    ShadowstepDictAttribute.DESCRIPTION: lambda v: f'.{UiAttribute.DESCRIPTION.value}("{v}")',
    ShadowstepDictAttribute.DESCRIPTION_CONTAINS: lambda v: f'.{UiAttribute.DESCRIPTION_CONTAINS.value}("{v}")',
    ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH: lambda v: f'.{UiAttribute.DESCRIPTION_STARTS_WITH.value}("{v}")',
    ShadowstepDictAttribute.DESCRIPTION_MATCHES: lambda v: f'.{UiAttribute.DESCRIPTION_MATCHES.value}("{v}")',
    ShadowstepDictAttribute.RESOURCE_ID: lambda v: f'.{UiAttribute.RESOURCE_ID.value}("{v}")',
    ShadowstepDictAttribute.RESOURCE_ID_MATCHES: lambda v: f'.{UiAttribute.RESOURCE_ID_MATCHES.value}("{v}")',
    ShadowstepDictAttribute.PACKAGE_NAME: lambda v: f'.{UiAttribute.PACKAGE_NAME.value}("{v}")',
    ShadowstepDictAttribute.PACKAGE_NAME_MATCHES: lambda v: f'.{UiAttribute.PACKAGE_NAME_MATCHES.value}("{v}")',
    ShadowstepDictAttribute.CLASS_NAME: lambda v: f'.{UiAttribute.CLASS_NAME.value}("{v}")',
    ShadowstepDictAttribute.CLASS_NAME_MATCHES: lambda v: f'.{UiAttribute.CLASS_NAME_MATCHES.value}("{v}")',
    ShadowstepDictAttribute.CHECKABLE: lambda v: f".{UiAttribute.CHECKABLE.value}({str(v).lower()})",
    ShadowstepDictAttribute.CHECKED: lambda v: f".{UiAttribute.CHECKED.value}({str(v).lower()})",
    ShadowstepDictAttribute.CLICKABLE: lambda v: f".{UiAttribute.CLICKABLE.value}({str(v).lower()})",
    ShadowstepDictAttribute.ENABLED: lambda v: f".{UiAttribute.ENABLED.value}({str(v).lower()})",
    ShadowstepDictAttribute.FOCUSABLE: lambda v: f".{UiAttribute.FOCUSABLE.value}({str(v).lower()})",
    ShadowstepDictAttribute.FOCUSED: lambda v: f".{UiAttribute.FOCUSED.value}({str(v).lower()})",
    ShadowstepDictAttribute.LONG_CLICKABLE: lambda v: f".{UiAttribute.LONG_CLICKABLE.value}({str(v).lower()})",
    ShadowstepDictAttribute.SCROLLABLE: lambda v: f".{UiAttribute.SCROLLABLE.value}({str(v).lower()})",
    ShadowstepDictAttribute.SELECTED: lambda v: f".{UiAttribute.SELECTED.value}({str(v).lower()})",
    ShadowstepDictAttribute.PASSWORD: lambda v: f".{UiAttribute.PASSWORD.value}({str(v).lower()})",
    ShadowstepDictAttribute.INDEX: lambda v: f".{UiAttribute.INDEX.value}({int(v)})",
    ShadowstepDictAttribute.INSTANCE: lambda v: f".{UiAttribute.INSTANCE.value}({int(v)})",
}
