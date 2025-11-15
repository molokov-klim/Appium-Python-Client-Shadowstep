# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Mapping from UiSelector attributes to Shadowstep dictionary format.

This module provides the mapping dictionary that converts UiSelector
attributes to their corresponding Shadowstep dictionary representation
with appropriate value conversion functions.
"""
from collections.abc import Callable
from typing import Any

from shadowstep.locator.locator_types.shadowstep_dict import ShadowstepDictAttribute
from shadowstep.locator.locator_types.ui_selector import UiAttribute

UI_TO_SHADOWSTEP_DICT: dict[UiAttribute, Callable[[str], dict[str, Any]]] = {
    # --- text-based ---
    UiAttribute.TEXT: lambda v: {ShadowstepDictAttribute.TEXT.value: v},
    UiAttribute.TEXT_CONTAINS: lambda v: {ShadowstepDictAttribute.TEXT_CONTAINS.value: v},
    UiAttribute.TEXT_STARTS_WITH: lambda v: {ShadowstepDictAttribute.TEXT_STARTS_WITH.value: v},
    UiAttribute.TEXT_MATCHES: lambda v: {ShadowstepDictAttribute.TEXT_MATCHES.value: v},

    # --- description ---
    UiAttribute.DESCRIPTION: lambda v: {ShadowstepDictAttribute.DESCRIPTION.value: v},
    UiAttribute.DESCRIPTION_CONTAINS: lambda v: {ShadowstepDictAttribute.DESCRIPTION_CONTAINS.value: v},
    UiAttribute.DESCRIPTION_STARTS_WITH: lambda v: {ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH.value: v},
    UiAttribute.DESCRIPTION_MATCHES: lambda v: {ShadowstepDictAttribute.DESCRIPTION_MATCHES.value: v},

    # --- resource id / package ---
    UiAttribute.RESOURCE_ID: lambda v: {ShadowstepDictAttribute.RESOURCE_ID.value: v},
    UiAttribute.RESOURCE_ID_MATCHES: lambda v: {ShadowstepDictAttribute.RESOURCE_ID_MATCHES.value: v},
    UiAttribute.PACKAGE_NAME: lambda v: {ShadowstepDictAttribute.PACKAGE_NAME.value: v},
    UiAttribute.PACKAGE_NAME_MATCHES: lambda v: {ShadowstepDictAttribute.PACKAGE_NAME_MATCHES.value: v},

    # --- class ---
    UiAttribute.CLASS_NAME: lambda v: {ShadowstepDictAttribute.CLASS_NAME.value: v},
    UiAttribute.CLASS_NAME_MATCHES: lambda v: {ShadowstepDictAttribute.CLASS_NAME_MATCHES.value: v},

    # --- bool props ---
    UiAttribute.CHECKABLE: lambda v: {ShadowstepDictAttribute.CHECKABLE.value: v},
    UiAttribute.CHECKED: lambda v: {ShadowstepDictAttribute.CHECKED.value: v},
    UiAttribute.CLICKABLE: lambda v: {ShadowstepDictAttribute.CLICKABLE.value: v},
    UiAttribute.LONG_CLICKABLE: lambda v: {ShadowstepDictAttribute.LONG_CLICKABLE.value: v},
    UiAttribute.ENABLED: lambda v: {ShadowstepDictAttribute.ENABLED.value: v},
    UiAttribute.FOCUSABLE: lambda v: {ShadowstepDictAttribute.FOCUSABLE.value: v},
    UiAttribute.FOCUSED: lambda v: {ShadowstepDictAttribute.FOCUSED.value: v},
    UiAttribute.SCROLLABLE: lambda v: {ShadowstepDictAttribute.SCROLLABLE.value: v},
    UiAttribute.SELECTED: lambda v: {ShadowstepDictAttribute.SELECTED.value: v},
    UiAttribute.PASSWORD: lambda v: {ShadowstepDictAttribute.PASSWORD.value: v},

    # --- numeric ---
    UiAttribute.INDEX: lambda v: {ShadowstepDictAttribute.INDEX.value: v},
    UiAttribute.INSTANCE: lambda v: {ShadowstepDictAttribute.INSTANCE.value: v},

    # --- hierarchy ---
    UiAttribute.CHILD_SELECTOR: lambda v: {ShadowstepDictAttribute.CHILD_SELECTOR.value: v},
    UiAttribute.FROM_PARENT: lambda v: {ShadowstepDictAttribute.FROM_PARENT.value: v},
}
