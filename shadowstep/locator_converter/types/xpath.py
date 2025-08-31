from enum import Enum


class XPathAttribute(str, Enum):
    # --- text-based ---
    TEXT = '@text="{value}"'
    TEXT_CONTAINS = 'contains(@text, "{value}")'
    TEXT_STARTS_WITH = 'starts-with(@text, "{value}")'
    TEXT_MATCHES = 'matches(@text, "{value}")'  # Appium >= 2

    # --- description ---
    DESCRIPTION = '@content-desc="{value}"'
    DESCRIPTION_CONTAINS = 'contains(@content-desc, "{value}")'
    DESCRIPTION_STARTS_WITH = 'starts-with(@content-desc, "{value}")'
    DESCRIPTION_MATCHES = 'matches(@content-desc, "{value}")'

    # --- resource id / package ---
    RESOURCE_ID = '@resource-id="{value}"'
    RESOURCE_ID_MATCHES = 'matches(@resource-id, "{value}")'
    PACKAGE_NAME = '@package="{value}"'
    PACKAGE_NAME_MATCHES = 'matches(@package, "{value}")'

    # --- class ---
    CLASS_NAME = '@class="{value}"'
    CLASS_NAME_MATCHES = 'matches(@class, "{value}")'

    # --- bool props ---
    CHECKABLE = '@checkable="{value}"'
    CHECKED = '@checked="{value}"'
    CLICKABLE = '@clickable="{value}"'
    ENABLED = '@enabled="{value}"'
    FOCUSABLE = '@focusable="{value}"'
    FOCUSED = '@focused="{value}"'
    LONG_CLICKABLE = '@long-clickable="{value}"'
    SCROLLABLE = '@scrollable="{value}"'
    SELECTED = '@selected="{value}"'
    PASSWORD = '@password="{value}"'

    # --- numeric ---
    INDEX = 'position()={value}'        # NB: тут +1 можно обрабатывать отдельно
    INSTANCE = '{value}'                # NB: требует доп. логики

    # --- hierarchy ---
    CHILD_SELECTOR = '{value}'          # подставляется отдельным конвертером
    FROM_PARENT = '{value}'

    # --- logic ---
    OR = '{left} | {right}'
    AND = '{left} and {right}'
