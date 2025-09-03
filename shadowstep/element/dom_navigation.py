# shadowstep/element/dom_navigation.py
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.types import WaitExcTypes
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from shadowstep.element.element import GeneralElementException
from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    from shadowstep.element.element import Element


class DomNavigation:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
