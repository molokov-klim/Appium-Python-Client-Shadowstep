# shadowstep/locator_converter/types/xpath.py
from enum import Enum
from typing import Any


class XPathAttribute(str, Enum):
    # --- text-based ---
    TEXT = "@text="
    TEXT_CONTAINS = "contains(@text, "
    TEXT_STARTS_WITH = "starts-with(@text, "
    TEXT_MATCHES = "matches(@text, "

    # --- description ---
    DESCRIPTION = "@content-desc="
    DESCRIPTION_CONTAINS = "contains(@content-desc, "
    DESCRIPTION_STARTS_WITH = "starts-with(@content-desc, "
    DESCRIPTION_MATCHES = "matches(@content-desc, "

    # --- resource id / package ---
    RESOURCE_ID = "@resource-id="
    RESOURCE_ID_MATCHES = "matches(@resource-id, "
    PACKAGE_NAME = "@package="
    PACKAGE_NAME_MATCHES = "matches(@package, "

    # --- class ---
    CLASS_NAME = "@class="
    CLASS_NAME_MATCHES = "matches(@class, "

    # --- bool props ---
    CHECKABLE = "@checkable="
    CHECKED = "@checked="
    CLICKABLE = "@clickable="
    ENABLED = "@enabled="
    FOCUSABLE = "@focusable="
    FOCUSED = "@focused="
    LONG_CLICKABLE = "@long-clickable="
    SCROLLABLE = "@scrollable="
    SELECTED = "@selected="
    PASSWORD = "@password="

    # --- numeric ---
    INDEX = "position()="
    INSTANCE = "instance"                       # use special logic

    # --- hierarchy ---
    CHILD_SELECTOR = "childSelector"            # use special logic
    FROM_PARENT = "fromParent"                  # use special logic
    SIBLING = "following-sibling"               # use special logic
    
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
