import time
from typing import Any

import pytest

from shadowstep.element.element import Element
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_element_gestures.py
"""


class TestElementGestures:

    def test_tap(self, app: Shadowstep, press_home: None, stability: None):
        element = app.get_element(locator={"content-desc": "Phone"})
        element.tap()
        time.sleep(3)
        expect_element = app.get_element({"package": "com.android.dialer"})
        assert expect_element.is_visible()  # noqa: S101  # noqa: S101

    def test_tap_duration(self, app: Shadowstep, press_home: None, stability: None):
        phone = app.get_element(locator={"content-desc": "Phone"})
        phone.tap(duration=3000)
        bubble = app.get_element(locator={"package": "com.android.launcher3",
                                          "class": "android.widget.TextView",
                                          "text": "App info",
                                          "resource-id": "com.android.launcher3:id/bubble_text"})
        bubble.tap()
        time.sleep(3)
        phone_info_title = app.get_element(locator={"text": "App info"})
        phone_info_storage = app.get_element(locator={"text": "Storage & cache"})
        assert phone_info_title.get_attribute("text") == "App info"  # noqa: S101  # noqa: S101
        assert phone_info_storage.get_attribute("text") == "Storage & cache"  # noqa: S101  # noqa: S101

    def test_tap_no_such_driver_exception(self, app: Shadowstep, press_home: None, stability: None):
        app.disconnect()
        assert not app.is_connected()  # noqa: S101  # noqa: S101
        element = app.get_element(locator={"content-desc": "Phone"})
        element.tap()
        assert app.is_connected()  # noqa: S101  # noqa: S101

    def test_tap_invalid_session_id_exception(self, app: Shadowstep, press_home: None, stability: None):
        app.driver.session_id = "12345"
        element = app.get_element(locator={"content-desc": "Phone"})
        element.tap()
        assert app.is_connected()  # noqa: S101  # noqa: S101
        time.sleep(3)
        expect_element = app.get_element({"package": "com.android.dialer"})
        assert expect_element.is_visible()  # noqa: S101  # noqa: S101

    def test_tap_no_such_element_exception(self, app: Shadowstep, press_home: None, stability: None):
        try:
            element = app.get_element(locator={"content-desc": "no_such_element"})
            element.timeout = 3
            element.tap()
        except Exception as error:
            print(error)
            assert isinstance(error, ShadowstepElementException)  # noqa: S101, PT017  # noqa: S101

    def test_tap_stale_element_reference_exception(self, app: Shadowstep, press_home: None, stability: None):
        pass  # don't know how to catch

    def test_tap_invalid_element_state_exception(self, app: Shadowstep, press_home: None, stability: None):
        pass  # don't know how to catch

    @pytest.mark.parametrize("params", [
        {"x": 100, "y": 500},  # Direct coordinates
        {"locator": {"package": "com.android.quicksearchbox",
                     "class": "android.widget.TextView",
                     "resource-id": "com.android.quicksearchbox:id/search_widget_text"}},  # Locator
        {"direction": 0, "distance": 1000},  # Up
    ])
    def test_tap_and_move(self, app: Shadowstep, press_home: None, stability: None, params: Any):
        element = app.get_element(locator={"content-desc": "Phone"})
        target_element = app.get_element(locator={"resource-id": "com.android.launcher3:id/search_container_all_apps"})
        element.tap_and_move(**params)
        time.sleep(5)
        assert "Search apps" in target_element.get_attribute(name="text")  # noqa: S101  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101  # noqa: S101

    def test_click(self, app: Shadowstep, press_home: None, stability: None):
        element = app.get_element(locator={"content-desc": "Phone"})
        element.click()
        time.sleep(5)
        expect_element = app.get_element({"package": "com.android.dialer"})
        assert expect_element.is_visible()  # noqa: S101  # noqa: S101

    def test_click_duration(self, app: Shadowstep, press_home: None, stability: None):
        phone = app.get_element(locator={"content-desc": "Phone"})
        phone.click(duration=3000)
        bubble = app.get_element(locator={"package": "com.android.launcher3",
                                          "class": "android.widget.TextView",
                                          "text": "App info",
                                          "resource-id": "com.android.launcher3:id/bubble_text"})
        bubble.click()
        time.sleep(3)
        phone_info_title = app.get_element(locator={"text": "App info"})
        phone_info_storage = app.get_element(locator={"text": "Storage & cache"})
        assert phone_info_title.get_attribute("text") == "App info"  # noqa: S101  # noqa: S101
        assert phone_info_storage.get_attribute("text") == "Storage & cache"  # noqa: S101  # noqa: S101

    def test_click_double(self, app: Shadowstep, press_home: None, stability: None):
        search = app.get_element(locator={"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        search.click_double()
        time.sleep(5)
        search_src_text = app.get_element(locator={"resource-id": "com.android.quicksearchbox:id/search_src_text"})
        app.terminal.past_text(text="some_text")
        assert "some_text" in search_src_text.get_attribute("text")  # noqa: S101  # noqa: S101

    def test_drag(self, app: Shadowstep, press_home: None, stability: None):
        app.terminal.press_home()
        time.sleep(10)
        messaging_1 = app.get_element(locator={"content-desc": "Messaging"})
        messaging_1.timeout = 1
        m1_center_x, m1_center_y, = messaging_1.get_center()
        search = app.get_element(locator={"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        assert "com.android.quicksearchbox" in search.get_attribute("package")  # noqa: S101  # noqa: S101
        end_x, end_y = search.get_center()
        app.get_element(locator={"content-desc": "Phone"}).tap_and_move(x=100, y=500)
        time.sleep(1)
        messaging_1.drag(end_x=100, end_y=500)
        time.sleep(1)
        messaging_1.drag(end_x=end_x, end_y=end_y)
        messaging_1.timeout = 5
        time.sleep(1)
        assert not messaging_1.is_visible()  # noqa: S101  # noqa: S101
        app.get_element(locator={"content-desc": "Phone"}).tap_and_move(x=100, y=500)
        messaging_2 = app.get_element(locator={"content-desc": "Messaging"})
        messaging_2.drag(end_x=m1_center_x, end_y=m1_center_y)

    def test_fling(self, app: Shadowstep, press_home: None, stability: None):
        element = app.get_element(locator={"content-desc": "Phone"})
        target_element = app.get_element(locator={"content-desc": "Do Not Disturb."})
        element.fling_up(speed=2000)
        time.sleep(5)
        assert "Off" in target_element.get_attribute(name="text")  # noqa: S101  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101  # noqa: S101

    def test_scroll(self, app: Shadowstep, press_home: None, stability: None):
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/main_content_scrollable_container"})
        settings_network = app.get_element(locator={"text": "Network & internet",
                                                    "resource-id": "android:id/title"})
        settings_about_phone = app.get_element(locator={"text": "About phone",
                                                        "resource-id": "android:id/title"})
        app.terminal.start_activity(package="com.android.settings", activity="com.android.settings.Settings")
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101  # noqa: S101
        settings_recycler.scroll_down(percent=10, speed=2000)
        time.sleep(3)
        assert "About phone" in settings_about_phone.get_attribute("text")  # noqa: S101  # noqa: S101
        app.terminal.close_app(package="com.android.settings")

    def test_scroll_to_element_not_found(self, app: Shadowstep, press_home: Any, stability: None):
        app.terminal.start_activity(package="com.android.settings", activity=".Settings")
        container = app.get_element({"resource-id": "com.android.settings:id/main_content_scrollable_container"})
        with pytest.raises(ShadowstepElementException):
            container.scroll_to_element(locator={"text": "Element That Does Not Exist"})

    def test_scroll_to_bottom(self, app: Shadowstep, press_home: None,
                              android_settings_open_close: None, stability: None):
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/main_content_scrollable_container"})
        settings_network = app.get_element(locator={"text": "Network & internet",
                                                    "resource-id": "android:id/title"})
        settings_about_phone = app.get_element(locator={"text": "About phone",
                                                        "resource-id": "android:id/title"})
        app.terminal.start_activity(package="com.android.settings", activity="com.android.settings.Settings")
        time.sleep(3)
        app.logger.info(f"{settings_recycler.get_attributes()=}")
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101  # noqa: S101
        app.logger.info(f"{settings_network.get_attributes()=}")
        settings_recycler.scroll_to_bottom()
        time.sleep(3)
        assert "About phone" in settings_about_phone.get_attribute("text")  # noqa: S101  # noqa: S101
        app.logger.info(f"{settings_about_phone.get_attributes()=}")
        app.terminal.close_app(package="com.android.settings")

    def test_scroll_to_top(self, app: Shadowstep, press_home: None, android_settings_open_close: None, stability: None):
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/main_content_scrollable_container"})
        settings_network = app.get_element(locator={"text": "Network & internet",
                                                    "resource-id": "android:id/title"})
        settings_about_phone = app.get_element(locator={"text": "About phone",
                                                        "resource-id": "android:id/title"})
        app.terminal.start_activity(package="com.android.settings", activity="com.android.settings.Settings")
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101  # noqa: S101
        settings_recycler.scroll_to_bottom()
        time.sleep(3)
        assert "About phone" in settings_about_phone.get_attribute("text")  # noqa: S101  # noqa: S101
        settings_recycler.scroll_to_top()
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101  # noqa: S101
        app.terminal.close_app(package="com.android.settings")

    def test_scroll_to_element(self, app: Shadowstep, press_home: None,
                               android_settings_open_close: None, stability: None):
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/settings_homepage_container"})
        settings_network = app.get_element(locator={"text": "Network & internet",
                                                    "resource-id": "android:id/title"})
        settings_about_phone = app.get_element(locator={"text": "About phone",
                                                        "resource-id": "android:id/title"})
        app.terminal.start_activity(package="com.android.settings", activity="com.android.settings.Settings")
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101  # noqa: S101
        settings_recycler.scroll_to_element(locator=settings_about_phone.locator)  # type: ignore
        time.sleep(3)
        assert "About phone" in settings_about_phone.get_attribute("text")  # noqa: S101  # noqa: S101
        settings_recycler.scroll_to_element(locator=settings_network)
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101  # noqa: S101
        app.terminal.close_app(package="com.android.settings")

    def test_zoom(self, app: Shadowstep, press_home: None, android_settings_open_close: None, stability: None):
        settings_network = app.get_element(locator={"text": "Network & internet",
                                                    "resource-id": "android:id/title"})
        settings_network.zoom()
        time.sleep(3)

    def test_unzoom(self, app: Shadowstep, press_home: None, android_settings_open_close: None, stability: None):
        settings_network = app.get_element(locator={"text": "Network & internet",
                                                    "resource-id": "android:id/title"})
        settings_network.unzoom()
        time.sleep(3)

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_swipe_directions(self, app: Shadowstep, press_home: None, stability: None, direction: str):
        element = app.get_element(locator={"content-desc": "Phone"})
        element.swipe(direction=direction, percent=0.5, speed=3000)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_up(self, app: Shadowstep, press_home: None, android_settings_open_close: None, stability: None):
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_up(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_down(self, app: Shadowstep, press_home: None, android_settings_open_close: None, stability: None):
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_down(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_left(self, app: Shadowstep, press_home: None, android_settings_open_close: None, stability: None):
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_left(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_right(self, app: Shadowstep, press_home: None, android_settings_open_close: None, stability: None):
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_right(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_fling_directions(self, app: Shadowstep, press_home: None, stability: None, direction: str):
        element = app.get_element(locator={"content-desc": "Phone"})
        element.fling(speed=3000, direction=direction)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101
