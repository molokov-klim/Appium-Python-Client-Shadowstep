# shadowstep/element/actions.py
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from shadowstep.decorators.decorators import log_debug
from shadowstep.element.utilities import ElementUtilities

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.locator import LocatorConverter, UiSelector
    from shadowstep.shadowstep import Shadowstep
    
class ElementActions:
    def __init__(self, element: Element):
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities
