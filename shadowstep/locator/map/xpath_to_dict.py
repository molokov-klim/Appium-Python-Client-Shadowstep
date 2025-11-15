# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Mapping from XPath attributes to Shadowstep dictionary format.

This module provides the mapping dictionary that converts XPath
attributes to their corresponding Shadowstep dictionary representation
with appropriate value conversion functions.
"""
from collections.abc import Callable
from typing import Any

from shadowstep.locator.locator_types.shadowstep_dict import ShadowstepDictAttribute
from shadowstep.locator.locator_types.xpath import XPathAttribute

XPATH_TO_SHADOWSTEP_DICT: dict[XPathAttribute, Callable[[str], dict[str, Any]]] = {
    # --- text-based ---
    XPathAttribute.TEXT: lambda v: {ShadowstepDictAttribute.TEXT.value: v},
    XPathAttribute.TEXT_CONTAINS: lambda v: {ShadowstepDictAttribute.TEXT_CONTAINS.value: v},
    XPathAttribute.TEXT_STARTS_WITH: lambda v: {ShadowstepDictAttribute.TEXT_STARTS_WITH.value: v},
    XPathAttribute.TEXT_MATCHES: lambda v: {ShadowstepDictAttribute.TEXT_MATCHES.value: v},

    # --- description ---
    XPathAttribute.DESCRIPTION: lambda v: {ShadowstepDictAttribute.DESCRIPTION.value: v},
    XPathAttribute.DESCRIPTION_CONTAINS: lambda v: {ShadowstepDictAttribute.DESCRIPTION_CONTAINS.value: v},
    XPathAttribute.DESCRIPTION_STARTS_WITH: lambda v: {ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH.value: v},
    XPathAttribute.DESCRIPTION_MATCHES: lambda v: {ShadowstepDictAttribute.DESCRIPTION_MATCHES.value: v},

    # --- resource id / package ---
    XPathAttribute.RESOURCE_ID: lambda v: {ShadowstepDictAttribute.RESOURCE_ID.value: v},
    XPathAttribute.RESOURCE_ID_MATCHES: lambda v: {ShadowstepDictAttribute.RESOURCE_ID_MATCHES.value: v},
    XPathAttribute.PACKAGE_NAME: lambda v: {ShadowstepDictAttribute.PACKAGE_NAME.value: v},
    XPathAttribute.PACKAGE_NAME_MATCHES: lambda v: {ShadowstepDictAttribute.PACKAGE_NAME_MATCHES.value: v},

    # --- class ---
    XPathAttribute.CLASS_NAME: lambda v: {ShadowstepDictAttribute.CLASS_NAME.value: v},
    XPathAttribute.CLASS_NAME_MATCHES: lambda v: {ShadowstepDictAttribute.CLASS_NAME_MATCHES.value: v},

    # --- bool props ---
    XPathAttribute.CHECKABLE: lambda v: {ShadowstepDictAttribute.CHECKABLE.value: v},
    XPathAttribute.CHECKED: lambda v: {ShadowstepDictAttribute.CHECKED.value: v},
    XPathAttribute.CLICKABLE: lambda v: {ShadowstepDictAttribute.CLICKABLE.value: v},
    XPathAttribute.LONG_CLICKABLE: lambda v: {ShadowstepDictAttribute.LONG_CLICKABLE.value: v},
    XPathAttribute.ENABLED: lambda v: {ShadowstepDictAttribute.ENABLED.value: v},
    XPathAttribute.FOCUSABLE: lambda v: {ShadowstepDictAttribute.FOCUSABLE.value: v},
    XPathAttribute.FOCUSED: lambda v: {ShadowstepDictAttribute.FOCUSED.value: v},
    XPathAttribute.SCROLLABLE: lambda v: {ShadowstepDictAttribute.SCROLLABLE.value: v},
    XPathAttribute.SELECTED: lambda v: {ShadowstepDictAttribute.SELECTED.value: v},
    XPathAttribute.PASSWORD: lambda v: {ShadowstepDictAttribute.PASSWORD.value: v},

    # --- numeric ---
    XPathAttribute.INDEX: lambda v: {ShadowstepDictAttribute.INDEX.value: v},
    XPathAttribute.INSTANCE: lambda v: {ShadowstepDictAttribute.INSTANCE.value: v},

    # --- hierarchy ---
    XPathAttribute.CHILD_SELECTOR: lambda v: {ShadowstepDictAttribute.CHILD_SELECTOR.value: v},
    XPathAttribute.FROM_PARENT: lambda v: {ShadowstepDictAttribute.FROM_PARENT.value: v},
}
