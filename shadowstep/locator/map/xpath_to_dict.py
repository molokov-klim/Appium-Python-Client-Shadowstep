# shadowstep/locator/map/xpath_to_dict.py
from collections.abc import Callable
from typing import Any

from shadowstep.locator.types.shadowstep_dict import DictAttribute
from shadowstep.locator.types.xpath import XPathAttribute

XPATH_TO_SHADOWSTEP_DICT: dict[XPathAttribute, Callable[[Any], dict[str, Any]]] = {
    # --- text-based ---
    XPathAttribute.TEXT: lambda v: {DictAttribute.TEXT.value: v},
    XPathAttribute.TEXT_CONTAINS: lambda v: {DictAttribute.TEXT_CONTAINS.value: v},
    XPathAttribute.TEXT_STARTS_WITH: lambda v: {DictAttribute.TEXT_STARTS_WITH.value: v},
    XPathAttribute.TEXT_MATCHES: lambda v: {DictAttribute.TEXT_MATCHES.value: v},

    # --- description ---
    XPathAttribute.DESCRIPTION: lambda v: {DictAttribute.DESCRIPTION.value: v},
    XPathAttribute.DESCRIPTION_CONTAINS: lambda v: {DictAttribute.DESCRIPTION_CONTAINS.value: v},
    XPathAttribute.DESCRIPTION_STARTS_WITH: lambda v: {DictAttribute.DESCRIPTION_STARTS_WITH.value: v},
    XPathAttribute.DESCRIPTION_MATCHES: lambda v: {DictAttribute.DESCRIPTION_MATCHES.value: v},

    # --- resource id / package ---
    XPathAttribute.RESOURCE_ID: lambda v: {DictAttribute.RESOURCE_ID.value: v},
    XPathAttribute.RESOURCE_ID_MATCHES: lambda v: {DictAttribute.RESOURCE_ID_MATCHES.value: v},
    XPathAttribute.PACKAGE_NAME: lambda v: {DictAttribute.PACKAGE_NAME.value: v},
    XPathAttribute.PACKAGE_NAME_MATCHES: lambda v: {DictAttribute.PACKAGE_NAME_MATCHES.value: v},

    # --- class ---
    XPathAttribute.CLASS_NAME: lambda v: {DictAttribute.CLASS_NAME.value: v},
    XPathAttribute.CLASS_NAME_MATCHES: lambda v: {DictAttribute.CLASS_NAME_MATCHES.value: v},

    # --- bool props ---
    XPathAttribute.CHECKABLE: lambda v: {DictAttribute.CHECKABLE.value: v},
    XPathAttribute.CHECKED: lambda v: {DictAttribute.CHECKED.value: v},
    XPathAttribute.CLICKABLE: lambda v: {DictAttribute.CLICKABLE.value: v},
    XPathAttribute.LONG_CLICKABLE: lambda v: {DictAttribute.LONG_CLICKABLE.value: v},
    XPathAttribute.ENABLED: lambda v: {DictAttribute.ENABLED.value: v},
    XPathAttribute.FOCUSABLE: lambda v: {DictAttribute.FOCUSABLE.value: v},
    XPathAttribute.FOCUSED: lambda v: {DictAttribute.FOCUSED.value: v},
    XPathAttribute.SCROLLABLE: lambda v: {DictAttribute.SCROLLABLE.value: v},
    XPathAttribute.SELECTED: lambda v: {DictAttribute.SELECTED.value: v},
    XPathAttribute.PASSWORD: lambda v: {DictAttribute.PASSWORD.value: v},

    # --- numeric ---
    XPathAttribute.INDEX: lambda v: {DictAttribute.INDEX.value: v},
    XPathAttribute.INSTANCE: lambda v: {DictAttribute.INSTANCE.value: v},

    # --- hierarchy ---
    XPathAttribute.CHILD_SELECTOR: lambda v: {DictAttribute.CHILD_SELECTOR.value: v},
    XPathAttribute.FROM_PARENT: lambda v: {DictAttribute.FROM_PARENT.value: v},
}
