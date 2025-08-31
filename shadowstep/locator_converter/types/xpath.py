from enum import Enum


class XPathAttribute(Enum):
    # --- text-based ---
    TEXT = '@text='
    TEXT_CONTAINS = 'contains(@text, '
    TEXT_STARTS_WITH = "starts-with(@text, "
    TEXT_MATCHES = 'matches(@text, '  # Appium >= 2

    # --- description ---
    DESCRIPTION = '@content-desc='
    DESCRIPTION_CONTAINS = 'contains(@content-desc, '
    DESCRIPTION_STARTS_WITH = 'starts-with(@content-desc, '
    DESCRIPTION_MATCHES = 'matches(@content-desc, '

    # --- resource id / package ---
    RESOURCE_ID = '@resource-id='
    RESOURCE_ID_MATCHES = 'matches(@resource-id, '
    PACKAGE_NAME = '@package='
    PACKAGE_NAME_MATCHES = 'matches(@package, '

    # --- class ---
    CLASS_NAME = '@class='
    CLASS_NAME_MATCHES = 'matches(@class, '

    # --- bool props ---
    CHECKABLE = '@checkable='
    CHECKED = '@checked='
    CLICKABLE = '@clickable='
    ENABLED = '@enabled='
    FOCUSABLE = '@focusable='
    FOCUSED = '@focused='
    LONG_CLICKABLE = '@long-clickable='
    SCROLLABLE = '@scrollable='
    SELECTED = '@selected='
    PASSWORD = '@password='

    # --- numeric ---
    INDEX = 'position()='
    INSTANCE = ''                # use logic

    # --- hierarchy ---
    CHILD_SELECTOR = ''          # use logic
    FROM_PARENT = ''             # use logic
