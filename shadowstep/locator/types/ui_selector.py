"""UiSelector attribute types.

This module defines the UiAttribute enum that represents
all supported attribute types for UiSelector locators,
including text-based, description, resource ID, class, boolean,
numeric, and hierarchical attributes based on Android UiAutomator.
"""
# shadowstep/locator/types/ui_selector.py
from enum import Enum
from typing import Any


class UiAttribute(str, Enum):
    """Enumeration of supported attribute types for UiSelector locators.

    This enum defines all supported attribute types that can be used
    in UiSelector locators based on Android UiAutomator, including
    text-based, description, resource ID, class, boolean, numeric,
    and hierarchical attributes.
    """

    # https://developer.android.com/reference/androidx/test/uiautomator/UiSelector
    # --- text-based ---
    TEXT = "text"
    TEXT_CONTAINS = "textContains"
    TEXT_STARTS_WITH = "textStartsWith"
    TEXT_MATCHES = "textMatches"

    # --- description ---
    DESCRIPTION = "description"
    DESCRIPTION_CONTAINS = "descriptionContains"
    DESCRIPTION_STARTS_WITH = "descriptionStartsWith"
    DESCRIPTION_MATCHES = "descriptionMatches"

    # --- resource id / package ---
    RESOURCE_ID = "resourceId"
    RESOURCE_ID_MATCHES = "resourceIdMatches"
    PACKAGE_NAME = "packageName"
    PACKAGE_NAME_MATCHES = "packageNameMatches"

    # --- class ---
    CLASS_NAME = "className"
    CLASS_NAME_MATCHES = "classNameMatches"

    # --- bool props ---
    CHECKABLE = "checkable"
    CHECKED = "checked"
    CLICKABLE = "clickable"
    ENABLED = "enabled"
    FOCUSABLE = "focusable"
    FOCUSED = "focused"
    LONG_CLICKABLE = "longClickable"
    SCROLLABLE = "scrollable"
    SELECTED = "selected"
    PASSWORD = "password"  # noqa: S105

    # --- numeric ---
    INDEX = "index"
    INSTANCE = "instance"

    # --- hierarchy ---
    CHILD_SELECTOR = "childSelector"
    FROM_PARENT = "fromParent"
    SIBLING = "sibling"

    def __str__(self) -> str:
        """Return the string value of the UiAttribute.
        
        Returns:
            str: The string value of the enum attribute.

        """
        return self.value

    def __repr__(self) -> str:
        """Return the official string representation of the UiAttribute.
        
        Returns:
            str: String representation in format 'ClassName.ATTRIBUTE_NAME'.

        """
        return f"{self.__class__.__name__}.{self.name}"

    def __eq__(self, other: Any) -> bool:
        """Check equality with string or other enum values.
        
        Args:
            other: Object to compare with.
            
        Returns:
            bool: True if equal, False otherwise.

        """
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

    def __hash__(self):
        """Return hash value based on the enum value.
        
        Returns:
            int: Hash value of the enum's string value.

        """
        return hash(self.value)
