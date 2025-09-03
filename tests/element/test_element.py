import time
from collections.abc import Generator
from typing import Any

import pytest
from selenium.common import NoSuchElementException

from shadowstep.element.element import Element, GeneralElementException
from shadowstep.shadowstep import Shadowstep


class TestElement:

    def test_get_element_positive(self, app: Shadowstep, stability: None,
                                  android_settings_open_close: None,
                                  android_settings_recycler: Element):
        inner_element = android_settings_recycler.get_element(locator={"text": "Network & internet"})
        assert isinstance(inner_element, Element)  # noqa: S101  # noqa: S101
        assert inner_element.package == "com.android.settings"  # noqa: S101  # noqa: S101
        assert inner_element.class_ == "android.widget.TextView"  # noqa: S101  # noqa: S101
        assert inner_element.resource_id == "android:id/title"  # noqa: S101  # noqa: S101

    def test_get_element_contains(self, app: Shadowstep, stability: None, android_settings_open_close: None,
                                  android_settings_recycler: Element):
        inner_element = android_settings_recycler.get_element(locator={"text": "ork & int"},
                                                              contains=True)
        assert inner_element.contains  # noqa: S101  # noqa: S101
        assert inner_element.text == "Network & internet"   # noqa: S101  # noqa: S101

    def test_get_element_repeated_search(self, app: Shadowstep, stability: None):
        element1 = app.get_element(locator={"content-desc": "Phone"})
        element2 = app.get_element(locator={"content-desc": "Phone"})
        assert element1 is not None  # noqa: S101  # noqa: S101
        assert element2 is not None  # noqa: S101  # noqa: S101
        assert element1.locator == element2.locator  # noqa: S101  # noqa: S101

    def test_get_element_disconnected(self, app: Shadowstep, stability: None):
        app.disconnect()
        assert not app.is_connected()  # noqa: S101  # noqa: S101
        element = app.get_element(locator={"content-desc": "Phone"})
        app.reconnect()
        assert app.is_connected()  # noqa: S101  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101  # noqa: S101
        assert element.locator == {"content-desc": "Phone"}  # noqa: S101  # noqa: S101

    def test_get_elements(self, app: Shadowstep, stability: None, android_settings_open_close: None,
                          android_settings_recycler: Element):
        inner_elements = android_settings_recycler.get_elements(locator={"resource-id": "android:id/title"})
        assert isinstance(inner_elements, list)  # noqa: S101  # noqa: S101
        for inner_element in inner_elements:
            app.logger.info(f"{inner_element.text=}")
            assert isinstance(inner_element, Element)  # noqa: S101  # noqa: S101
            assert inner_element.get_attribute("resource-id") == "android:id/title"  # noqa: S101  # noqa: S101

    def test_get_attributes(self, app: Shadowstep, stability: None):
        element = app.get_element(locator={"package": "com.android.launcher3",
                                           "class": "android.view.ViewGroup",
                                           "resource-id": "com.android.launcher3:id/hotseat",
                                           })
        attrs = element.get_attributes()
        assert isinstance(attrs, dict)  # noqa: S101  # noqa: S101
        assert "bounds" in attrs  # noqa: S101  # noqa: S101

    def test_get_parent(self, app: Shadowstep, stability: None):
        child = app.get_element(locator={"content-desc": "Phone"})
        parent = child.get_parent()
        assert isinstance(parent, Element)  # noqa: S101  # noqa: S101
        assert "ViewGroup" in parent.get_attribute("class")  # noqa: S101  # noqa: S101
        child = app.get_element(locator={"resource-id": "com.android.launcher3:id/drag_layer"})
        parent = child.get_parent()
        assert "com.android.launcher3:id/launcher" in parent.get_attribute("resource-id")  # noqa: S101  # noqa: S101

    def test_get_parents(self, app: Shadowstep, stability: None):
        element = app.get_element(locator={"content-desc": "Phone"})
        parents = element.get_parents()
        assert isinstance(parents, Generator)  # noqa: S101  # noqa: S101
        count = 0
        for parent in parents:
            assert isinstance(parent, Element)  # noqa: S101  # noqa: S101
            count += 1
        assert count > 0  # noqa: S101  # noqa: S101
        app.adb.press_home()

    def test_get_sibling(self, app: Shadowstep, stability: None, android_settings_open_close: None):
        el = app.get_element({"text": "Network & internet"})
        sibling = el.get_sibling({"resource-id": "android:id/summary"})
        assert isinstance(sibling, Element)  # noqa: S101  # noqa: S101
        assert "Mobile, Wi‑Fi, hotspot" in sibling.get_attribute("text")  # noqa: S101  # noqa: S101

    def test_get_siblings(self, app: Shadowstep, stability: None, android_settings_open_close: None,
                          android_settings_recycler: Element):
        el = android_settings_recycler.get_element(
            {"resource-id": "com.android.settings:id/recycler_view"}).get_element(
            {"class": "android.widget.LinearLayout"})
        siblings = el.get_siblings()
        assert isinstance(siblings, Generator)  # noqa: S101  # noqa: S101
        count = 0
        bounds: list[str] = []
        for sibling in siblings:
            assert isinstance(sibling, Element)  # noqa: S101  # noqa: S101
            assert sibling.get_attribute("bounds") is not None  # noqa: S101  # noqa: S101
            bounds.append(sibling.get_attribute("bounds"))
            count += 1
        bounds_unique = set(bounds)
        assert len(bounds_unique) > 3  # noqa: S101  # noqa: S101
        assert count > 0  # noqa: S101  # noqa: S101

    def test_tap(self, app: Shadowstep, stability: None):
        element = app.get_element(locator={"content-desc": "Phone"})
        element.tap()
        time.sleep(3)
        expect_element = app.get_element({"package": "com.android.dialer"})
        assert expect_element.is_visible()  # noqa: S101  # noqa: S101

    def test_tap_duration(self, app: Shadowstep, stability: None):
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

    def test_tap_no_such_driver_exception(self, app: Shadowstep, stability: None):
        app.disconnect()
        assert not app.is_connected()  # noqa: S101  # noqa: S101
        element = app.get_element(locator={"content-desc": "Phone"})
        element.tap()
        assert app.is_connected()  # noqa: S101  # noqa: S101

    def test_tap_invalid_session_id_exception(self, app: Shadowstep, stability: None):
        app.driver.session_id = "12345"
        element = app.get_element(locator={"content-desc": "Phone"})
        element.tap()
        assert app.is_connected()  # noqa: S101  # noqa: S101
        time.sleep(3)
        expect_element = app.get_element({"package": "com.android.dialer"})
        assert expect_element.is_visible()  # noqa: S101  # noqa: S101

    def test_tap_no_such_element_exception(self, app: Shadowstep, stability: None):
        try:
            element = app.get_element(locator={"content-desc": "no_such_element"})
            element.tap()
        except Exception as error:
            assert isinstance(error, NoSuchElementException)  # noqa: S101, PT017  # noqa: S101

    def test_tap_stale_element_reference_exception(self, app: Shadowstep, stability: None):
        pass  # don't know how to catch

    def test_tap_invalid_element_state_exception(self, app: Shadowstep, stability: None):
        pass  # don't know how to catch

    @pytest.mark.parametrize("params", [
        {"x": 100, "y": 500},  # Прямые координаты
        {"locator": {"package": "com.android.quicksearchbox",
                     "class": "android.widget.TextView",
                     "resource-id": "com.android.quicksearchbox:id/search_widget_text"}},  # Локатор
        {"direction": 0, "distance": 1000},  # Вверх
    ])
    def test_tap_and_move(self, app: Shadowstep, stability: None, params: Any):
        element = app.get_element(locator={"content-desc": "Phone"})
        target_element = app.get_element(locator={"resource-id": "com.android.launcher3:id/search_container_all_apps"})
        element.tap_and_move(**params)
        time.sleep(5)
        assert "Search apps" in target_element.get_attribute(name="text")  # noqa: S101  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101  # noqa: S101

    def test_click(self, app: Shadowstep, stability: None):
        element = app.get_element(locator={"content-desc": "Phone"})
        element.click()
        time.sleep(5)
        expect_element = app.get_element({"package": "com.android.dialer"})
        assert expect_element.is_visible()  # noqa: S101  # noqa: S101

    def test_click_duration(self, app: Shadowstep, stability: None):
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

    def test_click_double(self, app: Shadowstep, stability: None):
        search = app.get_element(locator={"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        search.click_double()
        time.sleep(5)
        search_src_text = app.get_element(locator={"resource-id": "com.android.quicksearchbox:id/search_src_text"})
        app.terminal.past_text(text="some_text")
        assert "some_text" in search_src_text.get_attribute("text")  # noqa: S101  # noqa: S101

    def test_drag(self, app: Shadowstep, stability: None):
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

    def test_is_within_screen(self, app: Shadowstep, stability: None):
        phone = app.get_element(locator={"content-desc": "Phone"}, timeout=5)
        search = app.get_element(locator={"resource-id": "com.android.quicksearchbox:id/search_widget_text"}, timeout=5)
        assert search.is_visible() is True  # noqa: S101  # noqa: S101
        assert phone.is_visible() is True  # noqa: S101  # noqa: S101
        phone.tap()
        time.sleep(3)
        assert phone.is_visible() is False  # noqa: S101  # noqa: S101
        assert search.is_visible() is False  # noqa: S101  # noqa: S101

    def test_fling(self, app: Shadowstep, stability: None):
        element = app.get_element(locator={"content-desc": "Phone"})
        target_element = app.get_element(locator={"content-desc": "Do Not Disturb."})
        element.fling_up(speed=2000)
        time.sleep(5)
        assert "Off" in target_element.get_attribute(name="text")  # noqa: S101  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101  # noqa: S101

    def test_scroll(self, app: Shadowstep, stability: None):
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

    def test_scroll_to_bottom(self, app: Shadowstep, stability: None, android_settings_open_close: None):
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

    def test_scroll_to_top(self, app: Shadowstep, stability: None, android_settings_open_close: None):
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

    def test_scroll_to_element(self, app: Shadowstep, stability: None, android_settings_open_close: None):
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/main_content_scrollable_container"})
        settings_network = app.get_element(locator={"text": "Network & internet",
                                                    "resource-id": "android:id/title"})
        settings_about_phone = app.get_element(locator={"text": "About phone",
                                                        "resource-id": "android:id/title"})
        app.terminal.start_activity(package="com.android.settings", activity="com.android.settings.Settings")
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101  # noqa: S101
        settings_recycler.scroll_to_element(locator=settings_about_phone.locator)
        time.sleep(3)
        assert "About phone" in settings_about_phone.get_attribute("text")  # noqa: S101  # noqa: S101
        settings_recycler.scroll_to_element(locator=settings_network)
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101  # noqa: S101
        app.terminal.close_app(package="com.android.settings")

    def test_get_center(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        center = el.get_center()
        left, top, right, bottom = map(int, el.bounds.strip("[]").replace("][", ",").split(","))
        x = int((left + right) / 2)
        y = int((top + bottom) / 2)
        assert isinstance(center, tuple) and len(center) == 2  # noqa: S101, PT018
        assert center == (x, y)  # noqa: S101  # noqa: S101

    def test_get_coordinates(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        coords = el.get_coordinates()
        left, top, right, bottom = map(int, el.bounds.strip("[]").replace("][", ",").split(","))
        assert isinstance(coords, tuple) and len(coords) == 4  # noqa: S101, PT018
        assert coords == (left, top, right, bottom)  # noqa: S101

    def test_get_attribute(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        assert el.get_attribute("content-desc") == "Phone"  # noqa: S101  # noqa: S101

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_get_property(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        prop = el.get_property("enabled")
        assert isinstance(prop, (str, bool, dict, type(None)))  # noqa: UP038, S101  # noqa: S101

    def test_get_dom_attribute(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        assert el.get_dom_attribute("class") == "android.widget.TextView"  # noqa: S101  # noqa: S101

    def test_is_displayed(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        assert isinstance(el.is_displayed(), bool)  # noqa: S101  # noqa: S101
        assert el.is_displayed()  # noqa: S101  # noqa: S101

    def test_is_selected(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        assert isinstance(el.is_selected(), bool)  # noqa: S101  # noqa: S101
        assert not el.is_selected()  # noqa: S101  # noqa: S101

    def test_is_enabled(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        assert isinstance(el.is_enabled(), bool)  # noqa: S101  # noqa: S101
        assert el.is_enabled()  # noqa: S101  # noqa: S101

    def test_is_contains(self, app: Shadowstep, stability: None):
        el = app.get_element({"resource-id": "com.android.launcher3:id/hotseat"})
        assert el.is_contains({"content-desc": "Phone"}) is True  # noqa: S101  # noqa: S101

    def test_tag_name(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        assert isinstance(el.tag_name, str)  # noqa: S101  # noqa: S101
        assert el.tag_name == "Phone"  # noqa: S101  # noqa: S101

    def test_text(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        assert isinstance(el.text, str)  # noqa: S101  # noqa: S101
        assert el.text == "Phone"  # noqa: S101  # noqa: S101

    def test_clear(self, app: Shadowstep, stability: None):
        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        el.tap()
        time.sleep(3)
        app.terminal.past_text("some_text")
        time.sleep(3)
        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_src_text"})
        assert el.text == "some_text"  # noqa: S101  # noqa: S101
        el.clear()
        assert el.text == ""  # noqa: S101  # noqa: S101

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_set_value(self, app: Shadowstep, stability: None):
        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        el.tap()
        time.sleep(3)
        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_src_text"})
        el.set_value("test123")
        assert "test123" in el.text  # noqa: S101  # noqa: S101
        el.clear()

    def test_send_keys(self, app: Shadowstep, stability: None):
        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        el.tap()
        time.sleep(3)
        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_src_text"})
        el.send_keys("abc")
        assert "abc" in el.text  # noqa: S101  # noqa: S101
        el.clear()

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_submit(self, app: Shadowstep, stability: None):
        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        el.submit()  # Не всегда валидно, но для теста вызова достаточно

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_shadow_root(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        try:
            sr = el.shadow_root
            assert sr is not None  # noqa: S101  # noqa: S101
        except Exception as e:
            assert isinstance(e, (NoSuchElementException, AttributeError))  # noqa: UP038, S101, PT017

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_location_once_scrolled_into_view(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        loc = el.location_once_scrolled_into_view
        assert "x" in loc and "y" in loc  # noqa: S101, PT018

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_size_location_rect(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        assert "width" in el.size and "height" in el.size  # noqa: S101, PT018
        assert "x" in el.location and "y" in el.location  # noqa: S101, PT018
        assert all(k in el.rect for k in ("x", "y", "width", "height"))  # noqa: S101  # noqa: S101

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_value_of_css_property(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        value = el.value_of_css_property("display")
        assert isinstance(value, str)  # noqa: S101  # noqa: S101

    def test_screenshot_as_base64(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        ss = el.screenshot_as_base64
        assert isinstance(ss, str)  # noqa: S101  # noqa: S101

    def test_screenshot_as_png(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        ss = el.screenshot_as_png
        assert isinstance(ss, bytes)  # noqa: S101  # noqa: S101

    def test_save_screenshot(self, tmp_path: Any, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        filepath = tmp_path / "test_element.png"
        assert el.save_screenshot(str(filepath)) is True  # noqa: S101  # noqa: S101
        assert filepath.exists()  # noqa: S101  # noqa: S101
        filepath.unlink()
        assert not filepath.exists()  # noqa: S101  # noqa: S101

    def test_shadow_root_error(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "non_existing"})
        with pytest.raises(GeneralElementException):
            _ = el.shadow_root

    def test_get_attribute_no_such_element(self, app: Shadowstep, stability: None):
        el = app.get_element({"content-desc": "non_existing"})
        with pytest.raises(NoSuchElementException):
            el.get_attribute("text")

    def test_scroll_to_element_not_found(self, app: Shadowstep, stability: None):
        app.terminal.start_activity(package="com.android.settings", activity=".Settings")
        container = app.get_element({"resource-id": "com.android.settings:id/main_content_scrollable_container"})
        with pytest.raises(NoSuchElementException):
            container.scroll_to_element(locator={"text": "Element That Does Not Exist"})

    def test_get_cousin(self, app: Shadowstep, stability: None, android_settings_open_close: None):
        app.get_element({"text": "Network & internet"}).tap()
        switcher = app.get_element({"text": "Airplane mode"}).get_cousin({"resource-id": "android:id/switch_widget"})
        assert switcher.get_attribute("class") == "android.widget.Switch"  # noqa: S101  # noqa: S101

    def test_get_cousin_depth(self, app: Shadowstep, stability: None, android_settings_open_close: None):
        app.get_element({"text": "Network & internet"}).tap()
        switcher = app.get_element({"text": "Airplane mode"}).get_cousin({"resource-id": "android:id/switch_widget"}, 5)
        assert switcher.get_attribute("class") == "android.widget.Switch"  # noqa: S101  # noqa: S101
