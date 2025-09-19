# shadowstep/element/conditions.py
"""
This module doesn't do anything right now, but it's a reminder of the idea of introducing different conditions
(based on attributes) besides the existing ones
"""
from __future__ import annotations

from collections.abc import Callable

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as expected_conditions

Locator = tuple[str, str]


def visible(locator: Locator) -> Callable:
    """Wraps expected_conditions.visibility_of_element_located."""
    return expected_conditions.visibility_of_element_located(locator)


def not_visible(locator: Locator) -> Callable:
    """Wraps expected_conditions.invisibility_of_element_located."""
    return expected_conditions.invisibility_of_element_located(locator)


def clickable(locator: Locator | WebElement) -> Callable:
    """Wraps expected_conditions.element_to_be_clickable."""
    return expected_conditions.element_to_be_clickable(locator)


def not_clickable(locator: Locator | WebElement) -> Callable:
    """Returns negation of expected_conditions.element_to_be_clickable."""
    def _predicate(driver):
        result = expected_conditions.element_to_be_clickable(locator)(driver)
        return not bool(result)
    return _predicate


def present(locator: Locator) -> Callable:
    """Wraps expected_conditions.presence_of_element_located."""
    return expected_conditions.presence_of_element_located(locator)


def not_present(locator: Locator) -> Callable:
    """Returns negation of expected_conditions.presence_of_element_located."""
    def _predicate(driver):
        try:
            expected_conditions.presence_of_element_located(locator)(driver)
            return False
        except Exception:
            return True
    return _predicate
