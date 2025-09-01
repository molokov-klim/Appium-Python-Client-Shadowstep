# shadowstep/locator_converter/map/ui_to_dict.py
from collections.abc import Callable
from typing import Any

from shadowstep.locator_converter.types.shadowstep_dict import DictAttribute
from shadowstep.locator_converter.types.ui_selector import UiAttribute

UI_TO_SHADOWSTEP_DICT: dict[UiAttribute, Callable[[Any], dict[str, Any]]] = {
    # --- text-based ---
    UiAttribute.TEXT: lambda v: {DictAttribute.TEXT.value: v},
    UiAttribute.TEXT_CONTAINS: lambda v: {DictAttribute.TEXT_CONTAINS.value: v},
    UiAttribute.TEXT_STARTS_WITH: lambda v: {DictAttribute.TEXT_STARTS_WITH.value: v},
    UiAttribute.TEXT_MATCHES: lambda v: {DictAttribute.TEXT_MATCHES.value: v},

    # --- description ---
    UiAttribute.DESCRIPTION: lambda v: {DictAttribute.DESCRIPTION.value: v},
    UiAttribute.DESCRIPTION_CONTAINS: lambda v: {DictAttribute.DESCRIPTION_CONTAINS.value: v},
    UiAttribute.DESCRIPTION_STARTS_WITH: lambda v: {DictAttribute.DESCRIPTION_STARTS_WITH.value: v},
    UiAttribute.DESCRIPTION_MATCHES: lambda v: {DictAttribute.DESCRIPTION_MATCHES.value: v},

    # --- resource id / package ---
    UiAttribute.RESOURCE_ID: lambda v: {DictAttribute.RESOURCE_ID.value: v},
    UiAttribute.RESOURCE_ID_MATCHES: lambda v: {DictAttribute.RESOURCE_ID_MATCHES.value: v},
    UiAttribute.PACKAGE_NAME: lambda v: {DictAttribute.PACKAGE_NAME.value: v},
    UiAttribute.PACKAGE_NAME_MATCHES: lambda v: {DictAttribute.PACKAGE_NAME_MATCHES.value: v},

    # --- class ---
    UiAttribute.CLASS_NAME: lambda v: {DictAttribute.CLASS_NAME.value: v},
    UiAttribute.CLASS_NAME_MATCHES: lambda v: {DictAttribute.CLASS_NAME_MATCHES.value: v},

    # --- bool props ---
    UiAttribute.CHECKABLE: lambda v: {DictAttribute.CHECKABLE.value: v},
    UiAttribute.CHECKED: lambda v: {DictAttribute.CHECKED.value: v},
    UiAttribute.CLICKABLE: lambda v: {DictAttribute.CLICKABLE.value: v},
    UiAttribute.LONG_CLICKABLE: lambda v: {DictAttribute.LONG_CLICKABLE.value: v},
    UiAttribute.ENABLED: lambda v: {DictAttribute.ENABLED.value: v},
    UiAttribute.FOCUSABLE: lambda v: {DictAttribute.FOCUSABLE.value: v},
    UiAttribute.FOCUSED: lambda v: {DictAttribute.FOCUSED.value: v},
    UiAttribute.SCROLLABLE: lambda v: {DictAttribute.SCROLLABLE.value: v},
    UiAttribute.SELECTED: lambda v: {DictAttribute.SELECTED.value: v},
    UiAttribute.PASSWORD: lambda v: {DictAttribute.PASSWORD.value: v},

    # --- numeric ---
    UiAttribute.INDEX: lambda v: {DictAttribute.INDEX.value: v},
    UiAttribute.INSTANCE: lambda v: {DictAttribute.INSTANCE.value: v},

    # --- hierarchy ---
    UiAttribute.CHILD_SELECTOR: lambda v: {DictAttribute.CHILD_SELECTOR.value: v},
    UiAttribute.FROM_PARENT: lambda v: {DictAttribute.FROM_PARENT.value: v},
}
