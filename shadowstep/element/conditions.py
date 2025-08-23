# shadowstep/utils/conditions.py
from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import WebDriverOrWebElement

Locator = tuple[str, str]


def visible(locator: Locator) -> Callable[[WebDriverOrWebElement], Literal[False] | WebElement]:
    """Wraps EC.visibility_of_element_located."""
    return EC.visibility_of_element_located(locator)


def not_visible(locator: Locator) -> Callable[[WebDriverOrWebElement], WebElement | bool]:
    """Wraps EC.invisibility_of_element_located."""
    return EC.invisibility_of_element_located(locator)


def clickable(locator: Locator | WebElement) -> Callable[[WebDriverOrWebElement], Literal[False] | WebElement]:
    """Wraps EC.element_to_be_clickable."""
    return EC.element_to_be_clickable(locator)

# FIXME логика неверна
def not_clickable(locator: Locator | WebElement) -> Callable[[WebDriverOrWebElement], Literal[False] | WebElement]:
    """Returns negation of EC.element_to_be_clickable."""
    def _predicate(driver: Any):
        result = EC.element_to_be_clickable(locator)(driver)
        return not bool(result)
    return _predicate


def present(locator: Locator) -> Callable[[WebDriverOrWebElement], WebElement]:
    """Wraps EC.presence_of_element_located."""
    return EC.presence_of_element_located(locator)


def not_present(locator: Locator) -> Callable:
    """Returns negation of EC.presence_of_element_located."""
    def _predicate(driver):
        try:
            EC.presence_of_element_located(locator)(driver)
            return False
        except Exception:
            return True
    return _predicate
