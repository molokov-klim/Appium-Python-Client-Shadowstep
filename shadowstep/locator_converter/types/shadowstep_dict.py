# shadowstep/locator_converter/types/shadowstep_dict.py
from enum import Enum


class DictAttribute(str, Enum):
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
