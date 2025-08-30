from collections.abc import Callable
from typing import Any

from shadowstep.locator_converter.types.ui_selector import UiMethod

UI_TO_SHADOWSTEP_DICT: dict[UiMethod, Callable[[Any], dict[str, Any]]] = {
    # --- text-based ---
    UiMethod.TEXT: lambda v: {"text": v},
    UiMethod.TEXT_CONTAINS: lambda v: {"textContains": v},
    UiMethod.TEXT_STARTS_WITH: lambda v: {"textStartsWith": v},
    UiMethod.TEXT_MATCHES: lambda v: {"textMatches": v},

    # --- description ---
    UiMethod.DESCRIPTION: lambda v: {"content-desc": v},
    UiMethod.DESCRIPTION_CONTAINS: lambda v: {"content-descContains": v},
    UiMethod.DESCRIPTION_STARTS_WITH: lambda v: {"content-descStartsWith": v},
    UiMethod.DESCRIPTION_MATCHES: lambda v: {"content-descMatches": v},

    # --- resource id / package ---
    UiMethod.RESOURCE_ID: lambda v: {"resource-id": v},
    UiMethod.RESOURCE_ID_MATCHES: lambda v: {"resource-idMatches": v},
    UiMethod.PACKAGE_NAME: lambda v: {"package": v},
    UiMethod.PACKAGE_NAME_MATCHES: lambda v: {"packageMatches": v},

    # --- class ---
    UiMethod.CLASS_NAME: lambda v: {"class": v},
    UiMethod.CLASS_NAME_MATCHES: lambda v: {"classNameMatches": v},

    # --- bool props ---
    UiMethod.CHECKABLE: lambda v: {"checkable": v},
    UiMethod.CHECKED: lambda v: {"checked": v},
    UiMethod.CLICKABLE: lambda v: {"clickable": v},
    UiMethod.LONG_CLICKABLE: lambda v: {"long-clickable": v},
    UiMethod.ENABLED: lambda v: {"enabled": v},
    UiMethod.FOCUSABLE: lambda v: {"focusable": v},
    UiMethod.FOCUSED: lambda v: {"focused": v},
    UiMethod.SCROLLABLE: lambda v: {"scrollable": v},
    UiMethod.SELECTED: lambda v: {"selected": v},
    UiMethod.PASSWORD: lambda v: {"password": v},

    # --- numeric ---
    UiMethod.INDEX: lambda v: {"index": v},
    UiMethod.INSTANCE: lambda v: {"instance": v},

    # --- hierarchy ---
    UiMethod.CHILD_SELECTOR: lambda v: {"childSelector": v},
    UiMethod.FROM_PARENT: lambda v: {"fromParent": v},
}
