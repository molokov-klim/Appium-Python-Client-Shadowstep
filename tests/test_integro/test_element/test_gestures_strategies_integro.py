# ruff: noqa
# pyright: ignore
"""Integration tests covering different gesture execution strategies.

This module verifies gesture behavior when the strategy is explicitly set
to ``W3C_ACTIONS`` or ``MOBILE_COMMANDS``.
"""
import logging
import time

import pytest

from shadowstep.element.element import Element
from shadowstep.enums import GestureStrategy
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_element/test_gestures_strategies_integro.py
"""

LOCATOR_CONNECTED_DEVICES = {"text": "Connected devices"}
LOCATOR_CONNECTION_PREFERENCES = {"text": "Connection preferences"}
LOCATOR_RECYCLER = {"resource-id": "com.android.settings:id/main_content_scrollable_container"}
LOCATOR_NETWORK = {"text": "Network & internet", "resource-id": "android:id/title"}
LOCATOR_BOTTOM_ELEMENT = {"textContains": "About"}

logger = logging.getLogger(__name__)


class TestGestureStrategies:
    """Test various gesture execution strategies.

    Verifies correctness when the strategy is explicitly set to:
    - ``W3C_ACTIONS``: uses the W3C WebDriver Actions API
    - ``MOBILE_COMMANDS``: uses Appium mobile commands (UiAutomator2)
    """

    def test_click_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test a click using the ``W3C_ACTIONS`` strategy.

        Verifies that clicking an element succeeds when the strategy is
        explicitly set to ``W3C_ACTIONS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.click(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_click_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test a click using the ``MOBILE_COMMANDS`` strategy.

        Verifies that clicking an element succeeds when the strategy is
        explicitly set to ``MOBILE_COMMANDS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.click(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_click_auto_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test a click with the default ``AUTO`` strategy.

        Verifies that clicking an element succeeds when the strategy is
        selected automatically.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.click(strategy=GestureStrategy.AUTO)
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_double_click_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test a double click using the ``W3C_ACTIONS`` strategy.

        Verifies that double clicking succeeds when the strategy is
        explicitly set to ``W3C_ACTIONS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        search = app.get_element(
            locator={
                "text": "Search settings",
                "resource-id": "com.android.settings:id/search_action_bar_title",
            }
        )
        search.double_click(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(3)
        assert app.get_element(locator={"class": "android.widget.EditText"}).is_visible()  # noqa: S101

    def test_double_click_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test a double click using the ``MOBILE_COMMANDS`` strategy.

        Verifies that double clicking succeeds when the strategy is
        explicitly set to ``MOBILE_COMMANDS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        search = app.get_element(
            locator={
                "text": "Search settings",
                "resource-id": "com.android.settings:id/search_action_bar_title",
            }
        )
        search.double_click(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(3)
        assert app.get_element(locator={"class": "android.widget.EditText"}).is_visible()  # noqa: S101

    def test_drag_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test dragging with the ``W3C_ACTIONS`` strategy.

        Verifies that the drag operation succeeds when the strategy is
        explicitly set to ``W3C_ACTIONS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        center_x1, center_y1 = element.get_center()
        element.drag(
            end_x=center_x1 - 500, end_y=center_y1 - 500, strategy=GestureStrategy.W3C_ACTIONS
        )
        time.sleep(2)
        assert element.get_center() != (center_x1, center_y1)  # noqa: S101

    def test_drag_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test dragging with the ``MOBILE_COMMANDS`` strategy.

        Verifies that the drag operation succeeds when the strategy is
        explicitly set to ``MOBILE_COMMANDS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        center_x1, center_y1 = element.get_center()
        element.drag(
            end_x=center_x1 - 500,
            end_y=center_y1 - 500,
            strategy=GestureStrategy.MOBILE_COMMANDS,
        )
        time.sleep(2)
        assert element.get_center() != (center_x1, center_y1)  # noqa: S101

    def test_fling_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test a fling with the ``W3C_ACTIONS`` strategy.

        Verifies that a fast swipe succeeds when the strategy is
        explicitly set to ``W3C_ACTIONS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_RECYCLER)
        bounds_1 = element.bounds
        element.fling_down(speed=3000, strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        bounds_2 = element.bounds
        assert bounds_1 != bounds_2  # noqa: S101

    def test_fling_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test a fling with the ``MOBILE_COMMANDS`` strategy.

        Verifies that a fast swipe succeeds when the strategy is
        explicitly set to ``MOBILE_COMMANDS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_RECYCLER)
        bounds_1 = element.bounds
        element.fling_down(speed=3000, strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        bounds_2 = element.bounds
        assert bounds_1 != bounds_2  # noqa: S101

    def test_scroll_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test scrolling with the ``W3C_ACTIONS`` strategy.

        Verifies that scrolling succeeds when the strategy is
        explicitly set to ``W3C_ACTIONS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        result = settings_recycler.scroll_down(
            percent=0.5, speed=2000, return_bool=True, strategy=GestureStrategy.W3C_ACTIONS
        )
        time.sleep(2)
        assert isinstance(result, bool)  # noqa: S101

    def test_scroll_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test scrolling with the ``MOBILE_COMMANDS`` strategy.

        Verifies that scrolling succeeds when the strategy is
        explicitly set to ``MOBILE_COMMANDS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        result = settings_recycler.scroll_down(
            percent=0.5, speed=2000, return_bool=True, strategy=GestureStrategy.MOBILE_COMMANDS
        )
        time.sleep(2)
        assert isinstance(result, bool)  # noqa: S101

    def test_scroll_to_bottom_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test scrolling to the bottom with the ``W3C_ACTIONS`` strategy.

        Verifies that scrolling to the end of a container succeeds when the
        strategy is explicitly set to ``W3C_ACTIONS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_bottom(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    def test_scroll_to_bottom_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test scrolling to the bottom with the ``MOBILE_COMMANDS`` strategy.

        Verifies that scrolling to the end of a container succeeds when the
        strategy is explicitly set to ``MOBILE_COMMANDS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_bottom(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    def test_scroll_to_top_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test scrolling to the top with the ``W3C_ACTIONS`` strategy.

        Verifies that scrolling upward succeeds when the strategy is
        explicitly set to ``W3C_ACTIONS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        
        settings_recycler.scroll_to_bottom(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101
        
        settings_recycler.scroll_to_top(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101

    def test_scroll_to_top_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test scrolling to the top with the ``MOBILE_COMMANDS`` strategy.

        Verifies that scrolling upward succeeds when the strategy is
        explicitly set to ``MOBILE_COMMANDS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        
        settings_recycler.scroll_to_bottom(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101
        
        settings_recycler.scroll_to_top(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101

    def test_scroll_to_element_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test scrolling to an element with the ``W3C_ACTIONS`` strategy.

        Verifies that scrolling to a specific element succeeds when the
        strategy is explicitly set to ``W3C_ACTIONS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/settings_homepage_container"}
        )
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_element(
            locator=settings_about_phone.locator, strategy=GestureStrategy.W3C_ACTIONS  # type: ignore
        )
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    def test_scroll_to_element_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test scrolling to an element with the ``MOBILE_COMMANDS`` strategy.

        Verifies that scrolling to a specific element succeeds when the
        strategy is explicitly set to ``MOBILE_COMMANDS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/settings_homepage_container"}
        )
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_element(
            locator=settings_about_phone.locator, strategy=GestureStrategy.MOBILE_COMMANDS  # type: ignore
        )
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_swipe_w3c_actions_strategy(
        self, app: Shadowstep, direction: str, android_settings_open_close: None
    ):
        """Test swiping with the ``W3C_ACTIONS`` strategy.

        Verifies that swiping in a specified direction succeeds when the
        strategy is explicitly set to ``W3C_ACTIONS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            direction: Swipe direction (``up``, ``down``, ``left``, ``right``).
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_RECYCLER)
        element.swipe(
            direction=direction, percent=0.5, speed=3000, strategy=GestureStrategy.W3C_ACTIONS
        )
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_swipe_mobile_commands_strategy(
        self, app: Shadowstep, direction: str, android_settings_open_close: None
    ):
        """Test swiping with the ``MOBILE_COMMANDS`` strategy.

        Verifies that swiping in a specified direction succeeds when the
        strategy is explicitly set to ``MOBILE_COMMANDS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            direction: Swipe direction (``up``, ``down``, ``left``, ``right``).
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_RECYCLER)
        element.swipe(
            direction=direction,
            percent=0.5,
            speed=3000,
            strategy=GestureStrategy.MOBILE_COMMANDS,
        )
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_zoom_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test zooming with the ``W3C_ACTIONS`` strategy.

        Verifies that the zoom gesture succeeds when the strategy is
        explicitly set to ``W3C_ACTIONS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_network.zoom(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        assert isinstance(settings_network, Element)  # noqa: S101

    def test_zoom_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test zooming with the ``MOBILE_COMMANDS`` strategy.

        Verifies that the zoom gesture succeeds when the strategy is
        explicitly set to ``MOBILE_COMMANDS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_network.zoom(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        assert isinstance(settings_network, Element)  # noqa: S101

    def test_unzoom_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test unzooming with the ``W3C_ACTIONS`` strategy.

        Verifies that the unzoom gesture succeeds when the strategy is
        explicitly set to ``W3C_ACTIONS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_network.unzoom(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        assert isinstance(settings_network, Element)  # noqa: S101

    def test_unzoom_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test unzooming with the ``MOBILE_COMMANDS`` strategy.

        Verifies that the unzoom gesture succeeds when the strategy is
        explicitly set to ``MOBILE_COMMANDS``.

        Args:
            app: Shadowstep instance for interacting with the app.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_network.unzoom(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        assert isinstance(settings_network, Element)  # noqa: S101

