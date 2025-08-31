from collections.abc import Callable
from typing import Any

from shadowstep.locator_converter.types.ui_selector import UiAttribute
from shadowstep.locator_converter.types.xpath import XPathAttribute

XPATH_TO_UI: dict[XPathAttribute, Callable[[Any], str]] = {
    # --- text-based ---
    XPathAttribute.TEXT: lambda v: f'{UiAttribute.TEXT.value}({v})',
    XPathAttribute.TEXT_CONTAINS: lambda v: f'{UiAttribute.TEXT_CONTAINS.value}({v})',
    XPathAttribute.TEXT_STARTS_WITH: lambda v: f'{UiAttribute.TEXT_STARTS_WITH.value}({v})',
    XPathAttribute.TEXT_MATCHES: lambda v: f'{UiAttribute.TEXT_MATCHES.value}({v})',

    # --- description ---
    XPathAttribute.DESCRIPTION: lambda v: f'{UiAttribute.DESCRIPTION.value}({v})',
    XPathAttribute.DESCRIPTION_CONTAINS: lambda v: f'{UiAttribute.DESCRIPTION_CONTAINS.value}({v})',
    XPathAttribute.DESCRIPTION_STARTS_WITH: lambda v: f'{UiAttribute.DESCRIPTION_STARTS_WITH.value}({v})',
    XPathAttribute.DESCRIPTION_MATCHES: lambda v: f'{UiAttribute.DESCRIPTION_MATCHES.value}({v})',

    # --- resource id / package ---
    XPathAttribute.RESOURCE_ID: lambda v: f'{UiAttribute.RESOURCE_ID.value}({v})',
    XPathAttribute.RESOURCE_ID_MATCHES: lambda v: f'{UiAttribute.RESOURCE_ID_MATCHES.value}({v})',
    XPathAttribute.PACKAGE_NAME: lambda v: f'{UiAttribute.PACKAGE_NAME.value}({v})',
    XPathAttribute.PACKAGE_NAME_MATCHES: lambda v: f'{UiAttribute.PACKAGE_NAME_MATCHES.value}({v})',

    # --- class ---
    XPathAttribute.CLASS_NAME: lambda v: f'{UiAttribute.CLASS_NAME.value}({v})',
    XPathAttribute.CLASS_NAME_MATCHES: lambda v: f'{UiAttribute.CLASS_NAME_MATCHES.value}({v})',

    # --- bool props ---
    XPathAttribute.CHECKABLE: lambda v: f'{UiAttribute.CHECKABLE.value}({v})',
    XPathAttribute.CHECKED: lambda v: f'{UiAttribute.CHECKED.value}({v})',
    XPathAttribute.CLICKABLE: lambda v: f'{UiAttribute.CLICKABLE.value}({v})',
    XPathAttribute.ENABLED: lambda v: f'{UiAttribute.ENABLED.value}({v})',
    XPathAttribute.FOCUSABLE: lambda v: f'{UiAttribute.FOCUSABLE.value}({v})',
    XPathAttribute.FOCUSED: lambda v: f'{UiAttribute.FOCUSED.value}({v})',
    XPathAttribute.LONG_CLICKABLE: lambda v: f'{UiAttribute.CLICKABLE.value}({v})',
    XPathAttribute.SCROLLABLE: lambda v: f'{UiAttribute.SCROLLABLE.value}({v})',
    XPathAttribute.SELECTED: lambda v: f'{UiAttribute.SELECTED.value}({v})',
    XPathAttribute.PASSWORD: lambda v: f'{UiAttribute.PASSWORD.value}({v})',

    # --- numeric ---
    XPathAttribute.INDEX: lambda v: f'{UiAttribute.INDEX.value}({v})',
    XPathAttribute.INSTANCE: lambda v: f'{UiAttribute.INSTANCE.value}({v})',

    # --- hierarchy ---
    XPathAttribute.CHILD_SELECTOR: lambda v: f'{UiAttribute.CHILD_SELECTOR.value}({v})',
    XPathAttribute.FROM_PARENT: lambda v: f'{UiAttribute.FROM_PARENT.value}({v})',
}
