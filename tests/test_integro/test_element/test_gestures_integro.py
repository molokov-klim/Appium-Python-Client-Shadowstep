# ruff: noqa
# pyright: ignore
import time
from typing import Any

import pytest

from shadowstep.element.element import Element
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_element_gestures.py
"""
LOCATOR_CONNECTED_DEVICES = {
    "text": "Connected devices"
}
LOCATOR_CONNECTION_PREFERENCES = {
    "text": "Connection preferences"
}
LOCATOR_SEARCH_SETTINGS = {
    "text": "Search settings",
    "resource-id": "com.android.settings:id/search_action_bar_title",
    "class": "android.widget.TextView",
}
SEARCH_SETTINGS_EXPECTED_TEXT = "Search settings"
LOCATOR_SEARCH_EDIT_TEXT = {
    "resource-id": "android:id/search_src_text",
}
LOCATOR_PHONE = {"text": "Phone"}
LOCATOR_BUBBLE = {
    "text": "App info",
    "resource-id": "com.android.launcher3:id/bubble_text",
}


class TestElementGestures:
    def test_tap(self, app: Shadowstep, press_home: None, android_settings_open_close: None):
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.tap()
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101  # noqa: S101

    def test_tap_duration(self, app: Shadowstep, press_home: None, ):
        phone = app.get_element(locator=LOCATOR_PHONE)
        phone.tap(duration=3000)
        bubble = app.get_element(locator=LOCATOR_BUBBLE)
        assert bubble.is_visible()

    def test_tap_no_such_driver_exception(self, app: Shadowstep, press_home: None,
                                          android_settings_open_close: None):
        app.disconnect()
        assert not app.is_connected()  # noqa: S101  # noqa: S101
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.tap()
        assert app.is_connected()  # noqa: S101  # noqa: S101

    def test_tap_invalid_session_id_exception(
            self, app: Shadowstep, press_home: None, android_settings_open_close: None
    ):
        app.driver.session_id = "12345"
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.tap()
        assert app.is_connected()  # noqa: S101  # noqa: S101
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101  # noqa: S101

    def test_tap_no_such_element_exception(
            self, app: Shadowstep, press_home: None, android_settings_open_close: None
    ):
        try:
            element = app.get_element(locator={"content-desc": "no_such_element"})
            element.timeout = 3
            element.tap()
        except Exception as error:
            print(error)
            assert isinstance(error, ShadowstepElementException)  # noqa: S101, PT017  # noqa: S101

    @pytest.mark.parametrize(
        "params",
        [
            {"x": 100, "y": 500},  # Direct coordinates
            {
                "locator": LOCATOR_SEARCH_SETTINGS
            },  # Locator
            {"direction": 0, "distance": 1000},  # Up
        ],
    )
    def test_tap_and_move(self, app: Shadowstep, press_home: None, android_settings_open_close: None,
                          params: Any):
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        target_element = app.get_element(
            locator=LOCATOR_SEARCH_SETTINGS
        )
        element.tap_and_move(**params)
        time.sleep(5)
        assert target_element.text == SEARCH_SETTINGS_EXPECTED_TEXT  # noqa: S101  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101  # noqa: S101

    def test_click(self, app: Shadowstep, press_home: None, android_settings_open_close: None):
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.click()
        time.sleep(5)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101  # noqa: S101

    def test_click_duration(self, app: Shadowstep, press_home: None):
        phone = app.get_element(locator=LOCATOR_PHONE)
        phone.click(duration=3000)
        bubble = app.get_element(locator=LOCATOR_BUBBLE)
        assert bubble.is_visible()

    def test_click_double(self, app: Shadowstep, press_home: None, android_settings_open_close: None):
        search = app.get_element(
            locator=LOCATOR_SEARCH_SETTINGS
        )
        search.click_double()
        time.sleep(5)
        assert app.get_element(
            locator=LOCATOR_SEARCH_EDIT_TEXT
        ).is_visible()

    def test_drag(self, app: Shadowstep, press_home: None, android_settings_open_close: None):
        gallery = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        center_x1, center_y1 = gallery.get_center()
        gallery.drag(end_x=center_x1 - 500, end_y=center_y1 - 500)
        assert gallery.get_center() != center_x1, center_y1

    def test_fling(self, app: Shadowstep, press_home: None, android_settings_open_close: None):
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        bounds_1 = element.bounds
        element.fling_down(speed=3000)
        bounds_2 = element.bounds
        assert bounds_1 != bounds_2

    def test_scroll(self, app: Shadowstep, press_home: None, android_settings_open_close: None):
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/main_content_scrollable_container"}
        )
        settings_about_phone = app.get_element(
            locator={"text": "About phone", "resource-id": "android:id/title"}
        )

        while settings_recycler.scroll_down(percent=10, speed=2000, return_bool=True):
            time.sleep(1)
        assert "About phone" in settings_about_phone.get_attribute("text")  # noqa: S101  # noqa: S101

    def test_scroll_to_element_not_found(self, app: Shadowstep, press_home: Any,
                                         android_settings_open_close: None):
        container = app.get_element(
            {"resource-id": "com.android.settings:id/main_content_scrollable_container"}
        )
        with pytest.raises(ShadowstepElementException):
            container.scroll_to_element(locator={"text": "Element That Does Not Exist"})

    def test_scroll_to_bottom(
            self, app: Shadowstep, press_home: None, android_settings_open_close: None,
    ):
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/main_content_scrollable_container"}
        )
        settings_about_phone = app.get_element(
            locator={"text": "About phone", "resource-id": "android:id/title"}
        )
        settings_recycler.scroll_to_bottom()
        assert "About phone" in settings_about_phone.get_attribute("text")  # noqa: S101  # noqa: S101

    def test_scroll_to_top(
            self, app: Shadowstep, press_home: None, android_settings_open_close: None,
    ):
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/main_content_scrollable_container"}
        )
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_about_phone = app.get_element(
            locator={"text": "About phone", "resource-id": "android:id/title"}
        )
        settings_recycler.scroll_to_bottom()
        time.sleep(3)
        assert "About phone" in settings_about_phone.get_attribute("text")  # noqa: S101  # noqa: S101
        settings_recycler.scroll_to_top()
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101  # noqa: S101

    def test_scroll_to_element(
            self, app: Shadowstep, press_home: None, android_settings_open_close: None, 
    ):
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/settings_homepage_container"}
        )
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_about_phone = app.get_element(
            locator={"text": "About phone", "resource-id": "android:id/title"}
        )
        settings_recycler.scroll_to_element(locator=settings_about_phone.locator)  # type: ignore
        time.sleep(3)
        assert "About phone" in settings_about_phone.get_attribute("text")  # noqa: S101  # noqa: S101
        settings_recycler.scroll_to_element(locator=settings_network)
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101  # noqa: S101

    def test_zoom(
            self, app: Shadowstep, press_home: None, android_settings_open_close: None, 
    ):
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_network.zoom()
        time.sleep(3)

    def test_unzoom(
            self, app: Shadowstep, press_home: None, android_settings_open_close: None, 
    ):
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_network.unzoom()
        time.sleep(3)

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_swipe_directions(
            self, app: Shadowstep, press_home: None, direction: str, android_settings_open_close: None
    ):
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.swipe(direction=direction, percent=0.5, speed=3000)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_up(
            self, app: Shadowstep, press_home: None, android_settings_open_close: None, 
    ):
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_up(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_down(
            self, app: Shadowstep, press_home: None, android_settings_open_close: None, 
    ):
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_down(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_left(
            self, app: Shadowstep, press_home: None, android_settings_open_close: None, 
    ):
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_left(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_right(
            self, app: Shadowstep, press_home: None, android_settings_open_close: None, 
    ):
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_right(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_fling_directions(
            self, app: Shadowstep, press_home: None, direction: str, android_settings_open_close: None
    ):
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.fling(speed=3000, direction=direction)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101
