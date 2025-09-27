"""Shadowstep dictionary attribute types.

This module defines the ShadowstepDictAttribute enum that represents
all supported attribute types for Shadowstep dictionary locators,
including text-based, description, resource ID, class, boolean,
numeric, and hierarchical attributes.
"""
# shadowstep/locator/types/shadowstep_dict.py
from enum import Enum
from typing import Any


class ShadowstepDictAttribute(str, Enum):
    """Enumeration of supported attribute types for Shadowstep dictionary locators.

    This enum defines all supported attribute types that can be used
    in Shadowstep dictionary locators, including text-based, description,
    resource ID, class, boolean, numeric, and hierarchical attributes.
    """

    # --- text-based ---
    TEXT = "text"
    TEXT_CONTAINS = "textContains"
    TEXT_STARTS_WITH = "textStartsWith"
    TEXT_MATCHES = "textMatches"

    # --- description ---
    DESCRIPTION = "content-desc"
    DESCRIPTION_CONTAINS = "content-descContains"
    DESCRIPTION_STARTS_WITH = "content-descStartsWith"
    DESCRIPTION_MATCHES = "content-descMatches"

    # --- resource id / package ---
    RESOURCE_ID = "resource-id"
    RESOURCE_ID_MATCHES = "resource-idMatches"
    PACKAGE_NAME = "package"
    PACKAGE_NAME_MATCHES = "packageMatches"

    # --- class ---
    CLASS_NAME = "class"
    CLASS_NAME_MATCHES = "classMatches"

    # --- bool props ---
    CHECKABLE = "checkable"
    CHECKED = "checked"
    CLICKABLE = "clickable"
    ENABLED = "enabled"
    FOCUSABLE = "focusable"
    FOCUSED = "focused"
    LONG_CLICKABLE = "long-clickable"
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
        """Return the string value of the attribute.

        Returns:
            str: The string value of the enum attribute.

        """
        return self.value

    def __repr__(self) -> str:
        """Return the official string representation of the enum attribute.

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
