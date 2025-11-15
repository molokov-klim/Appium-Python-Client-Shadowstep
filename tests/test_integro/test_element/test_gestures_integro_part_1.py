# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
import logging
import time
from typing import Any

import pytest

from shadowstep.element.element import Element
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_gestures_integro_part_1.py
"""
LOCATOR_CONNECTED_DEVICES = {"text": "Connected devices"}
LOCATOR_CONNECTION_PREFERENCES = {"text": "Connection preferences"}
LOCATOR_SEARCH_SETTINGS = {
    "text": "Search settings",
    "resource-id": "com.android.settings:id/search_action_bar_title",
    "class": "android.widget.TextView",
}
SEARCH_SETTINGS_EXPECTED_TEXT = "Search settings"
LOCATOR_SEARCH_EDIT_TEXT = {
    "class": "android.widget.EditText",
}
LOCATOR_PHONE = {"text": "Phone"}
LOCATOR_BUBBLE = {
    "text": "App info",
}

logger = logging.getLogger(__name__)


class TestElementGesturesPart1:
    """Tests for basic element interaction gestures.

    This class contains suites for basic gestures such as tap and click with
    different parameters and exception handling scenarios.
    """

    def test_tap(self, app: Shadowstep, android_settings_open_close: None):
        """Test a basic tap on an element.

        Verifies that tapping ``Connected devices`` shows ``Connection preferences``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.tap()
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_tap_duration(self, app: Shadowstep, press_home: None, stability: None):
        """Test a tap with a custom duration.

        Ensures a 3000 ms tap on ``Phone`` reveals the ``App info`` element.

        Args:
            app: Shadowstep instance for interacting with the app.
            press_home: Fixture that presses the Home button.
            stability: Fixture that stabilizes the test run.
        """
        phone = app.get_element(locator=LOCATOR_PHONE)
        phone.tap(duration=3000)
        bubble = app.get_element(locator=LOCATOR_BUBBLE)
        logger.info(app.driver.page_source)
        assert bubble.is_visible()

    def test_tap_no_such_driver_exception(self, app: Shadowstep, android_settings_open_close: None):
        """Test handling the missing driver exception.

        Ensures a tap reconnects and handles ``NoSuchDriverException`` after disconnect.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        app.disconnect()
        assert not app.is_connected()  # noqa: S101
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.tap()
        assert app.is_connected()  # noqa: S101

    def test_tap_invalid_session_id_exception(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test handling an invalid session identifier.

        Verifies ``InvalidSessionIdException`` is handled when tapping with a bad session id.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        app.driver.session_id = "12345"
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.tap()
        assert app.is_connected()  # noqa: S101
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_tap_no_such_element_exception(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test handling a missing element exception.

        Ensures ``NoSuchElementException`` is handled when tapping a non-existent element.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        try:
            element = app.get_element(locator={"content-desc": "no_such_element"})
            element.timeout = 3
            element.tap()
        except Exception as error:
            print(error)
            assert isinstance(error, ShadowstepElementException)  # noqa: S101, PT017

    @pytest.mark.parametrize(
        "params",
        [
            {"x": 100, "y": 500},  # Direct coordinates
            {"locator": LOCATOR_SEARCH_SETTINGS},  # Locator
            {"direction": 0, "distance": 1000},  # Up
        ],
    )
    def test_tap_and_move(self, app: Shadowstep, android_settings_open_close: None, params: Any):
        """Test tap-and-move in multiple directions.

        Verifies tap followed by movement using coordinates, locators, or direction values.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
            params: Parameters controlling tap-and-move behavior.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        target_element = app.get_element(locator=LOCATOR_SEARCH_SETTINGS)
        element.tap_and_move(**params)
        time.sleep(5)
        assert target_element.text == SEARCH_SETTINGS_EXPECTED_TEXT  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101

    def test_click(self, app: Shadowstep, android_settings_open_close: None):
        """Test a basic click on an element.

        Ensures clicking ``Connected devices`` reveals ``Connection preferences``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.click()
        time.sleep(5)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_click_duration(self, app: Shadowstep, press_home: None):
        """Test a click with a specified duration.

        Verifies a 3000 ms click on ``Phone`` reveals the ``App info`` element.

        Args:
            app: Shadowstep instance for interacting with the app.
            press_home: Fixture that presses the Home button.
        """
        phone = app.get_element(locator=LOCATOR_PHONE)
        phone.click(duration=3000)
        bubble = app.get_element(locator=LOCATOR_BUBBLE)
        assert bubble.is_visible()

    def test_click_double(self, app: Shadowstep, android_settings_open_close: None):
        """Test a double click on an element.

        Ensures double clicking ``Search settings`` reveals the search input field.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        search = app.get_element(locator=LOCATOR_SEARCH_SETTINGS)
        search.double_click()
        time.sleep(5)
        logger.info(app.driver.page_source)
        assert app.get_element(locator=LOCATOR_SEARCH_EDIT_TEXT).is_visible()
