# shadowstep/locator/ui_selector.py
"""UiSelector DSL for fluent API locator building.

This module provides a fluent DSL for building UiSelector locators in a more
readable and maintainable way, similar to the original UiSelector API but with
Python syntax.
"""
# ruff: noqa: N802

from __future__ import annotations

import logging
from typing import Any

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepInvalidUiSelectorStringFormatError
from shadowstep.locator.types.ui_selector import UiAttribute


class UiSelector:
    """Fluent DSL for building UiSelector locators.

    This class provides a fluent API for building UiSelector locators in a
    more readable way than string concatenation. It supports all UiAttribute
    methods and hierarchical relationships.

    Example:
        selector = UiSelector().text("OK").clickable(True).className("Button")
        selector_str = str(selector)  # "new UiSelector().text("OK").clickable(true).className("Button");"

    """

    def __init__(self):
        """Initialize the UiSelector with empty state."""
        self.logger = logging.getLogger(__name__)
        self._methods: list[tuple[str, Any]] = []
        self._hierarchical_methods: list[tuple[str, UiSelector]] = []

    # Text-based methods
    def text(self, value: str) -> UiSelector:
        """Set text attribute."""
        return self._add_method(UiAttribute.TEXT, value)

    def textContains(self, value: str) -> UiSelector:
        """Set textContains attribute."""
        return self._add_method(UiAttribute.TEXT_CONTAINS, value)

    def textStartsWith(self, value: str) -> UiSelector:
        """Set textStartsWith attribute."""
        return self._add_method(UiAttribute.TEXT_STARTS_WITH, value)

    def textMatches(self, value: str) -> UiSelector:
        """Set textMatches attribute."""
        return self._add_method(UiAttribute.TEXT_MATCHES, value)

    # Description methods
    def description(self, value: str) -> UiSelector:
        """Set description attribute."""
        return self._add_method(UiAttribute.DESCRIPTION, value)

    def descriptionContains(self, value: str) -> UiSelector:
        """Set descriptionContains attribute."""
        return self._add_method(UiAttribute.DESCRIPTION_CONTAINS, value)

    def descriptionStartsWith(self, value: str) -> UiSelector:
        """Set descriptionStartsWith attribute."""
        return self._add_method(UiAttribute.DESCRIPTION_STARTS_WITH, value)

    def descriptionMatches(self, value: str) -> UiSelector:
        """Set descriptionMatches attribute."""
        return self._add_method(UiAttribute.DESCRIPTION_MATCHES, value)

    # Resource ID and Package methods
    def resourceId(self, value: str) -> UiSelector:
        """Set resourceId attribute."""
        return self._add_method(UiAttribute.RESOURCE_ID, value)

    def resourceIdMatches(self, value: str) -> UiSelector:
        """Set resourceIdMatches attribute."""
        return self._add_method(UiAttribute.RESOURCE_ID_MATCHES, value)

    def packageName(self, value: str) -> UiSelector:
        """Set packageName attribute."""
        return self._add_method(UiAttribute.PACKAGE_NAME, value)

    def packageNameMatches(self, value: str) -> UiSelector:
        """Set packageNameMatches attribute."""
        return self._add_method(UiAttribute.PACKAGE_NAME_MATCHES, value)

    # Class methods
    def className(self, value: str) -> UiSelector:
        """Set className attribute."""
        return self._add_method(UiAttribute.CLASS_NAME, value)

    def classNameMatches(self, value: str) -> UiSelector:
        """Set classNameMatches attribute."""
        return self._add_method(UiAttribute.CLASS_NAME_MATCHES, value)

    # Boolean property methods
    def checkable(self, value: bool = True) -> UiSelector:
        """Set checkable attribute."""
        return self._add_method(UiAttribute.CHECKABLE, value)

    def checked(self, value: bool = True) -> UiSelector:
        """Set checked attribute."""
        return self._add_method(UiAttribute.CHECKED, value)

    def clickable(self, value: bool = True) -> UiSelector:
        """Set clickable attribute."""
        return self._add_method(UiAttribute.CLICKABLE, value)

    def enabled(self, value: bool = True) -> UiSelector:
        """Set enabled attribute."""
        return self._add_method(UiAttribute.ENABLED, value)

    def focusable(self, value: bool = True) -> UiSelector:
        """Set focusable attribute."""
        return self._add_method(UiAttribute.FOCUSABLE, value)

    def focused(self, value: bool = True) -> UiSelector:
        """Set focused attribute."""
        return self._add_method(UiAttribute.FOCUSED, value)

    def longClickable(self, value: bool = True) -> UiSelector:
        """Set longClickable attribute."""
        return self._add_method(UiAttribute.LONG_CLICKABLE, value)

    def scrollable(self, value: bool = True) -> UiSelector:
        """Set scrollable attribute."""
        return self._add_method(UiAttribute.SCROLLABLE, value)

    def selected(self, value: bool = True) -> UiSelector:
        """Set selected attribute."""
        return self._add_method(UiAttribute.SELECTED, value)

    def password(self, value: bool = True) -> UiSelector:
        """Set password attribute."""
        return self._add_method(UiAttribute.PASSWORD, value)

    # Numeric methods
    def index(self, value: int) -> UiSelector:
        """Set index attribute."""
        return self._add_method(UiAttribute.INDEX, value)

    def instance(self, value: int) -> UiSelector:
        """Set instance attribute."""
        return self._add_method(UiAttribute.INSTANCE, value)

    # Hierarchical methods
    def childSelector(self, child: UiSelector) -> UiSelector:
        """Set childSelector with another UiSelector."""
        return self._add_hierarchical_method(UiAttribute.CHILD_SELECTOR, child)

    def fromParent(self, parent: UiSelector) -> UiSelector:
        """Set fromParent with another UiSelector."""
        return self._add_hierarchical_method(UiAttribute.FROM_PARENT, parent)

    def sibling(self, sibling: UiSelector) -> UiSelector:
        """Set sibling with another UiSelector."""
        return self._add_hierarchical_method(UiAttribute.SIBLING, sibling)

    def _add_method(self, attribute: UiAttribute, value: Any) -> UiSelector:
        """Add a method call to the selector."""
        self._methods.append((attribute.value, value))
        return self

    def _add_hierarchical_method(self, attribute: UiAttribute, child: UiSelector) -> UiSelector:
        """Add a hierarchical method call to the selector."""
        self._hierarchical_methods.append((attribute.value, child))
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert UiSelector to dictionary format."""
        result = {}

        # Add regular methods
        for method_name, value in self._methods:
            result[method_name] = value

        # Add hierarchical methods
        for method_name, child_selector in self._hierarchical_methods:
            result[method_name] = child_selector.to_dict()

        return result

    def __str__(self) -> str:
        """Convert UiSelector to string representation."""
        return self._build_selector_string()

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"UiSelector({self._build_selector_string()})"

    def _build_selector_string(self, is_nested: bool = False) -> str:
        """Build the final UiSelector string."""
        parts = ["new UiSelector()"]

        # Add regular methods
        for method_name, value in self._methods:
            if isinstance(value, str):
                # Escape quotes and backslashes in string values
                escaped_value = value.replace("\\", "\\\\").replace('"', '\\"')
                parts.append(f'.{method_name}("{escaped_value}")')
            elif isinstance(value, bool):
                parts.append(f".{method_name}({str(value).lower()})")
            else:
                parts.append(f".{method_name}({value})")

        # Add hierarchical methods
        for method_name, child_selector in self._hierarchical_methods:
            child_str = child_selector._build_selector_string(is_nested=True)
            parts.append(f".{method_name}({child_str})")

        result = "".join(parts)

        # Only add semicolon if not nested
        if not is_nested:
            result += ";"

        return result

    def __eq__(self, other: object) -> bool:
        """Check equality with another UiSelector."""
        if not isinstance(other, UiSelector):
            return False
        return (self._methods == other._methods and
                self._hierarchical_methods == other._hierarchical_methods)

    def __hash__(self) -> int:
        """Return hash of the UiSelector."""
        return hash((tuple(self._methods), tuple(self._hierarchical_methods)))

    def copy(self) -> UiSelector:
        """Create a copy of this UiSelector."""
        new_selector = UiSelector()
        new_selector._methods = self._methods.copy()
        new_selector._hierarchical_methods = [(name, child.copy()) for name, child in self._hierarchical_methods]
        return new_selector

    @classmethod
    def from_string(cls, selector_str: str) -> UiSelector:
        """Create UiSelector from string representation.

        Args:
            selector_str: UiSelector string like "new UiSelector().text('OK');"

        Returns:
            UiSelector instance

        Raises:
            ValueError: If string format is invalid

        """
        # This is a simplified parser - in a real implementation you might want
        # to use the existing UiSelectorConverter to parse the string
        if not selector_str.strip().startswith("new UiSelector()"):
            raise ShadowstepInvalidUiSelectorStringFormatError

        # For now, we'll create an empty selector and let the user build it
        # In a full implementation, you'd parse the string and extract methods
        return cls()

    @classmethod
    def from_dict(cls, selector_dict: dict[str, Any]) -> UiSelector:
        """Create UiSelector from dictionary representation.

        Args:
            selector_dict: Dictionary with selector attributes

        Returns:
            UiSelector instance

        """
        selector = cls()

        for key, value in selector_dict.items():
            if key in [UiAttribute.CHILD_SELECTOR, UiAttribute.FROM_PARENT, UiAttribute.SIBLING]:
                # Handle hierarchical attributes
                if isinstance(value, dict):
                    child_selector = cls.from_dict(value) # type: ignore[return-any]
                    if key == UiAttribute.CHILD_SELECTOR:
                        selector.childSelector(child_selector)
                    elif key == UiAttribute.FROM_PARENT:
                        selector.fromParent(child_selector)
                    elif key == UiAttribute.SIBLING:
                        selector.sibling(child_selector)
            else:
                # Handle regular attributes
                method_name = key
                if hasattr(selector, method_name):
                    method = getattr(selector, method_name)
                    method(value)
                else:
                    selector.logger.warning(f"Unknown method: {method_name}")

        return selector
