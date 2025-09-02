# shadowstep/locator/types/ui_selector.py
from enum import Enum
from typing import Any


class UiAttribute(str, Enum):
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
    PASSWORD = "password"

    # --- numeric ---
    INDEX = "index"
    INSTANCE = "instance"

    # --- hierarchy ---
    CHILD_SELECTOR = "childSelector"
    FROM_PARENT = "fromParent"
    SIBLING = "sibling"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.value)
