# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Integration tests for element conditions module."""
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from shadowstep.element.conditions import (
    clickable,
    not_clickable,
    not_present,
    not_visible,
    present,
    visible,
)
from shadowstep.shadowstep import Shadowstep


class TestConditions:
    """Test class for element condition functions."""

    def test_visible_condition_returns_element_when_visible(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test visible() condition returns element when it is visible.

        Steps:
        1. Open Settings app.
        2. Find a visible element locator.
        3. Use visible() condition with WebDriverWait.
        4. Verify element is returned.
        """
        # Settings text should be visible
        locator = ("xpath", '//android.widget.TextView[@text="Settings"]')

        # Use visible condition
        wait = WebDriverWait(app.driver, 10)
        element = wait.until(visible(locator))

        # Verify element is returned and displayed
        assert element is not None  # noqa: S101
        assert element.is_displayed()  # noqa: S101

    def test_not_visible_condition_returns_true_when_element_not_visible(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test not_visible() condition returns True when element is not visible.

        Steps:
        1. Use a locator for non-existent element.
        2. Apply not_visible() condition.
        3. Verify condition returns True.
        """
        # Use a locator that doesn't exist
        locator = ("xpath", '//android.widget.TextView[@text="NonExistentElement12345"]')

        # Use not_visible condition
        wait = WebDriverWait(app.driver, 5)
        result = wait.until(not_visible(locator))

        # not_visible returns True when element is not visible
        assert result is True  # noqa: S101

    def test_clickable_condition_returns_element_when_clickable(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test clickable() condition returns element when it is clickable.

        Steps:
        1. Find a clickable element in Settings.
        2. Use clickable() condition with WebDriverWait.
        3. Verify element is returned and clickable.
        """
        # Settings text should be clickable
        locator = ("xpath", '//android.widget.TextView[@text="Settings"]')

        # Use clickable condition
        wait = WebDriverWait(app.driver, 10)
        element = wait.until(clickable(locator))

        # Verify element is returned
        assert element is not None  # noqa: S101
        assert element.is_displayed()  # noqa: S101
        assert element.is_enabled()  # noqa: S101

    def test_not_clickable_condition_with_callable(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test not_clickable() condition is a callable predicate.

        Steps:
        1. Create not_clickable condition with a locator.
        2. Verify it returns a callable.
        3. Call it with driver to verify behavior.
        """
        # Use an existing locator
        locator = ("xpath", '//android.widget.TextView[@text="Settings"]')

        # Create not_clickable condition
        condition = not_clickable(locator)

        # Verify it's callable
        assert callable(condition)  # noqa: S101

        # Call with driver - existing clickable element should return False (negation)
        # Since Settings is clickable, not_clickable should return False
        result = condition(app.driver)

        # not_clickable returns False when element IS clickable (negation works)
        assert result is False  # noqa: S101

    def test_present_condition_returns_element_when_present(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test present() condition returns element when it is present in DOM.

        Steps:
        1. Find an element that is present in DOM.
        2. Use present() condition with WebDriverWait.
        3. Verify element is returned.
        """
        # Settings element should be present in DOM
        locator = ("xpath", '//android.widget.TextView[@text="Settings"]')

        # Use present condition
        wait = WebDriverWait(app.driver, 10)
        element = wait.until(present(locator))

        # Verify element is returned
        assert element is not None  # noqa: S101

    def test_not_present_condition_returns_true_when_not_in_dom(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test not_present() condition returns True when element is not in DOM.

        Steps:
        1. Use a locator for element that doesn't exist in DOM.
        2. Apply not_present() condition.
        3. Verify condition returns True.
        """
        # Use a locator that doesn't exist in DOM
        locator = ("xpath", '//android.widget.TextView[@text="ThisElementDoesNotExist123"]')

        # Use not_present condition
        wait = WebDriverWait(app.driver, 5)
        result = wait.until(not_present(locator))

        # not_present returns True when element is not in DOM
        assert result is True  # noqa: S101

    def test_visible_condition_works_with_driver(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test that visible() condition is callable with driver.

        Steps:
        1. Get visible() condition predicate.
        2. Call it directly with driver.
        3. Verify it returns element or False.
        """
        locator = ("xpath", '//android.widget.TextView[@text="Settings"]')

        # Get condition predicate
        condition = visible(locator)

        # Call with driver
        result = condition(app.driver)

        # Should return element (truthy) if visible
        assert result is not None  # noqa: S101

    def test_clickable_condition_works_with_webelement(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test that clickable() condition works with WebElement.

        Steps:
        1. Get a WebElement.
        2. Create clickable() condition with the element.
        3. Verify condition works.
        """
        # First find element
        locator = ("xpath", '//android.widget.TextView[@text="Settings"]')
        element = app.driver.find_element(*locator)

        # Create clickable condition with WebElement
        condition = clickable(element)

        # Call with driver
        result = condition(app.driver)

        # Should return element if clickable
        assert result is not None  # noqa: S101

    def test_present_condition_finds_multiple_elements(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test that present() works when multiple elements match.

        Steps:
        1. Use a locator that matches multiple elements.
        2. Apply present() condition.
        3. Verify it returns the first matching element.
        """
        # Locator that matches multiple TextViews
        locator = ("xpath", "//android.widget.TextView")

        # Use present condition
        wait = WebDriverWait(app.driver, 10)
        element = wait.until(present(locator))

        # Should return first matching element
        assert element is not None  # noqa: S101

    def test_conditions_are_callables(self, app: Shadowstep):
        """Test that all condition functions return callables.

        Steps:
        1. Create conditions with dummy locators.
        2. Verify each returns a callable.
        """
        locator = ("xpath", "//dummy")

        # Create all conditions
        conditions_list = [
            visible(locator),
            not_visible(locator),
            clickable(locator),
            not_clickable(locator),
            present(locator),
            not_present(locator),
        ]

        # Verify all are callables
        for condition in conditions_list:
            assert callable(condition)  # noqa: S101

    def test_visible_and_not_visible_are_complementary(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test that visible() and not_visible() work as complements.

        Steps:
        1. Find element that exists and is visible.
        2. Verify visible() returns element.
        3. Find element that doesn't exist.
        4. Verify not_visible() returns True.
        """
        # Visible element
        visible_locator = ("xpath", '//android.widget.TextView[@text="Settings"]')
        wait = WebDriverWait(app.driver, 10)
        visible_element = wait.until(visible(visible_locator))
        assert visible_element is not None  # noqa: S101

        # Non-existent element (not visible)
        invisible_locator = ("xpath", '//android.widget.TextView[@text="InvisibleElement999"]')
        wait2 = WebDriverWait(app.driver, 5)
        not_visible_result = wait2.until(not_visible(invisible_locator))
        assert not_visible_result is True  # noqa: S101

    def test_present_and_not_present_are_complementary(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test that present() and not_present() work as complements.

        Steps:
        1. Find element that is present in DOM.
        2. Verify present() returns element.
        3. Find element that is not present.
        4. Verify not_present() returns True.
        """
        # Present element
        present_locator = ("xpath", '//android.widget.TextView[@text="Settings"]')
        wait = WebDriverWait(app.driver, 10)
        present_element = wait.until(present(present_locator))
        assert present_element is not None  # noqa: S101

        # Non-existent element (not present)
        not_present_locator = ("xpath", '//android.widget.TextView[@text="NotPresentElement999"]')
        wait2 = WebDriverWait(app.driver, 5)
        not_present_result = wait2.until(not_present(not_present_locator))
        assert not_present_result is True  # noqa: S101
