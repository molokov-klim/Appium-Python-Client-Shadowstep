# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Element conditions module for Shadowstep framework.

This module provides condition functions for element waiting and validation.
It serves as a reminder for introducing different conditions based on attributes
besides the existing ones.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement

Locator = tuple[str, str]
WebDriverPredicate = Callable[[WebDriver], Any]


def visible(locator: Locator) -> WebDriverPredicate:
    """Wrap expected_conditions.visibility_of_element_located."""
    return expected_conditions.visibility_of_element_located(locator)


def not_visible(locator: Locator) -> WebDriverPredicate:
    """Wrap expected_conditions.invisibility_of_element_located."""
    return expected_conditions.invisibility_of_element_located(locator)


def clickable(locator: Locator | WebElement) -> WebDriverPredicate:
    """Wrap expected_conditions.element_to_be_clickable."""
    return expected_conditions.element_to_be_clickable(locator)


def not_clickable(locator: Locator | WebElement) -> WebDriverPredicate:
    """Return negation of expected_conditions.element_to_be_clickable."""
    def _predicate(driver: WebDriver) -> bool:
        result = expected_conditions.element_to_be_clickable(locator)(driver)
        return not bool(result)
    return _predicate


def present(locator: Locator) -> WebDriverPredicate:
    """Wrap expected_conditions.presence_of_element_located."""
    return expected_conditions.presence_of_element_located(locator)


def not_present(locator: Locator) -> WebDriverPredicate:
    """Return negation of expected_conditions.presence_of_element_located."""
    def _predicate(driver: WebDriver) -> bool:
        try:
            expected_conditions.presence_of_element_located(locator)(driver)
        except (NoSuchElementException, TimeoutException):
            return True
        else:
            return False
    return _predicate
