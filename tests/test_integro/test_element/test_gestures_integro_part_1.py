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

    This class contains tests for basic element interaction gestures,
    including tap and click operations with various parameters and exception handling.
    """

    def test_tap(self, app: Shadowstep, android_settings_open_close: None):
        """Test basic element tap.

        Verifies correct execution of tap on "Connected devices" element
        and expected appearance of "Connection preferences" element.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.tap()
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_tap_duration(self, app: Shadowstep, press_home: None, stability: None):
        """Test tap with specified duration.

        Verifies correct execution of tap with 3000ms duration
        on "Phone" element and expected appearance of "App info" element.

        Args:
            app: Shadowstep instance for application interaction.
            press_home: Fixture for pressing Home button.
            stability: Fixture for ensuring test stability.
        """
        phone = app.get_element(locator=LOCATOR_PHONE)
        phone.tap(duration=3000)
        bubble = app.get_element(locator=LOCATOR_BUBBLE)
        logger.info(app.driver.page_source)
        assert bubble.is_visible()

    def test_tap_no_such_driver_exception(self, app: Shadowstep, android_settings_open_close: None):
        """Test handling exception when driver is not present.

        Verifies correct handling of NoSuchDriverException
        when performing tap after disconnecting from driver.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        app.disconnect()
        assert not app.is_connected()  # noqa: S101
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.tap()
        assert app.is_connected()  # noqa: S101

    def test_tap_invalid_session_id_exception(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test handling exception when session ID is invalid.

        Verifies correct handling of InvalidSessionIdException
        when performing tap with invalid session ID.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
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
        """Test handling exception when element is not present.

        Verifies correct handling of NoSuchElementException
        when attempting to tap non-existent element.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
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
        """Test tap with movement in various directions.

        Verifies correct execution of tap with subsequent movement
        using various parameters (coordinates, locator, direction).

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
            params: Parameters for tap and move execution.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        target_element = app.get_element(locator=LOCATOR_SEARCH_SETTINGS)
        element.tap_and_move(**params)
        time.sleep(5)
        assert target_element.text == SEARCH_SETTINGS_EXPECTED_TEXT  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101

    def test_click(self, app: Shadowstep, android_settings_open_close: None):
        """Test basic element click.

        Verifies correct execution of click on "Connected devices" element
        and expected appearance of "Connection preferences" element.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.click()
        time.sleep(5)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_click_duration(self, app: Shadowstep, press_home: None):
        """Test click with specified duration.

        Verifies correct execution of click with 3000ms duration
        on "Phone" element and expected appearance of "App info" element.

        Args:
            app: Shadowstep instance for application interaction.
            press_home: Fixture for pressing Home button.
        """
        phone = app.get_element(locator=LOCATOR_PHONE)
        phone.click(duration=3000)
        bubble = app.get_element(locator=LOCATOR_BUBBLE)
        assert bubble.is_visible()

    def test_click_double(self, app: Shadowstep, android_settings_open_close: None):
        """Test double click on element.

        Verifies correct execution of double click on
        "Search settings" element and expected appearance of search input field.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        search = app.get_element(locator=LOCATOR_SEARCH_SETTINGS)
        search.double_click()
        time.sleep(5)
        logger.info(app.driver.page_source)
        assert app.get_element(locator=LOCATOR_SEARCH_EDIT_TEXT).is_visible()
