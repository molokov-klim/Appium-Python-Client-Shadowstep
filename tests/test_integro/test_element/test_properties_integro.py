# ruff: noqa
# pyright: ignore
import logging
import re
import time
from typing import Any

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep


logger = logging.getLogger(__name__)

LOCATOR_CONNECTED_DEVICES = {"text": "Connected devices"}
LOCATOR_CONNECTION_PREFERENCES = {"text": "Connection preferences"}
LOCATOR_SEARCH_SETTINGS = {
    "text": "Search settings",
    "resource-id": "com.android.settings:id/search_action_bar_title",
    "class": "android.widget.TextView",
}
SEARCH_SETTINGS_EXPECTED_TEXT = "Search settings"
LOCATOR_SEARCH_EDIT_TEXT = {
    "resource-id": "android:id/search_src_text",
}


# ruff: noqa: S101
class TestElementProperties:
    def test_get_attribute(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert el.get_attribute("resource-id") == "android:id/title"

    def test_get_attribute_no_such_element(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element({"content-desc": "non_existing"})
        el.timeout = 3
        with pytest.raises(ShadowstepElementException):
            el.get_attribute("text")

    def test_get_attributes(self, app: Shadowstep, android_settings_open_close: Any):
        element = app.get_element(LOCATOR_CONNECTED_DEVICES)
        attrs = element.get_attributes()
        assert isinstance(attrs, dict)  # noqa: S101  # noqa: S101
        assert "bounds" in attrs  # noqa: S101  # noqa: S101

    def test_get_property(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        with pytest.raises(ShadowstepElementException):
            el.get_property("enabled")

    def test_get_dom_attribute(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert el.get_dom_attribute("class") == "android.widget.TextView"  # noqa: S101  # noqa: S101

    def test_is_displayed(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.is_displayed(), bool)  # noqa: S101  # noqa: S101
        assert el.is_displayed()  # noqa: S101  # noqa: S101

    def test_is_visible(self, app: Shadowstep, android_settings_open_close: Any):
        phone = app.get_element(locator=LOCATOR_CONNECTED_DEVICES, timeout=5)
        search = app.get_element(locator=LOCATOR_SEARCH_SETTINGS, timeout=5)
        phone.wait(timeout=5)
        assert search.is_visible() is True  # noqa: S101  # noqa: S101
        assert phone.is_visible() is True  # noqa: S101  # noqa: S101
        phone.tap()
        time.sleep(3)
        assert not phone.is_visible()  # noqa: S101  # noqa: S101
        assert not search.is_visible()  # noqa: S101  # noqa: S101

    def test_is_selected(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.is_selected(), bool)  # noqa: S101  # noqa: S101
        assert not el.is_selected()  # noqa: S101  # noqa: S101

    def test_is_enabled(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.is_enabled(), bool)  # noqa: S101  # noqa: S101
        assert el.is_enabled()  # noqa: S101  # noqa: S101

    def test_is_contains(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element({"class": "android.widget.FrameLayout"})
        assert el.is_contains(LOCATOR_CONNECTED_DEVICES) is True  # noqa: S101  # noqa: S101

    def test_text(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.text, str)  # noqa: S101  # noqa: S101
        assert el.text == "Connected devices"  # noqa: S101  # noqa: S101

    def test_resource_id(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.resource_id, str)  # noqa: S101  # noqa: S101
        assert el.resource_id == "android:id/title"  # noqa: S101  # noqa: S101

    def test_class_(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.class_, str)  # noqa: S101  # noqa: S101
        assert el.class_ == "android.widget.TextView"  # noqa: S101  # noqa: S101

    def test_class_name(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.class_name, str)  # noqa: S101  # noqa: S101
        assert el.class_name == "android.widget.TextView"  # noqa: S101  # noqa: S101

    def test_index(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        with pytest.raises(ShadowstepElementException):
            assert isinstance(el.index, str)  # noqa: S101  # noqa: S101

    def test_package(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.package, str)  # noqa: S101  # noqa: S101
        assert el.package == "com.android.settings"  # noqa: S101  # noqa: S101

    def test_bounds(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.bounds, str)
        assert re.fullmatch(r"\[\d+,\d+\]\[\d+,\d+\]", el.bounds), (
            f"Invalid bounds format: {el.bounds}"
        )

    def test_checked(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.checked, str)  # noqa: S101  # noqa: S101
        assert el.checked == "false"  # noqa: S101  # noqa: S101

    def test_checkable(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.checkable, str)  # noqa: S101  # noqa: S101
        assert el.checkable == "false"  # noqa: S101  # noqa: S101

    def test_enabled(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.enabled, str)  # noqa: S101  # noqa: S101
        assert el.enabled == "true"  # noqa: S101  # noqa: S101

    def test_focusable(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.focusable, str)  # noqa: S101  # noqa: S101
        assert el.focusable == "false"  # noqa: S101  # noqa: S101

    def test_focused(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.focused, str)  # noqa: S101  # noqa: S101
        assert el.focused == "false"  # noqa: S101  # noqa: S101

    def test_long_clickable(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.long_clickable, str)  # noqa: S101  # noqa: S101
        assert el.long_clickable == "false"  # noqa: S101  # noqa: S101

    def test_password(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.password, str)  # noqa: S101  # noqa: S101
        assert el.password == "false"  # noqa: S101, S105

    def test_scrollable(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.scrollable, str)  # noqa: S101  # noqa: S101
        assert el.scrollable == "false"  # noqa: S101  # noqa: S101

    def test_selected(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.selected, str)  # noqa: S101  # noqa: S101
        assert el.selected == "false"  # noqa: S101  # noqa: S101

    def test_displayed(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.displayed, str)  # noqa: S101  # noqa: S101
        assert el.displayed == "true"  # noqa: S101  # noqa: S101

    def test_shadow_root_error(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element({"content-desc": "non_existing"})
        with pytest.raises(ShadowstepElementException):
            _ = el.shadow_root

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_size_location_rect(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert "width" in el.size and "height" in el.size  # noqa: S101, PT018
        assert "x" in el.location and "y" in el.location  # noqa: S101, PT018
        assert all(k in el.rect for k in ("x", "y", "width", "height"))  # noqa: S101  # noqa: S101

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_value_of_css_property(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        value = el.value_of_css_property("display")
        assert isinstance(value, str)  # noqa: S101  # noqa: S101

    def test_location(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.location, dict)  # noqa: S101  # noqa: S101
        assert isinstance(el.location.get("x"), int)  # noqa: S101
        assert isinstance(el.location.get("y"), int)  # noqa: S101

    def test_rect(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.rect, dict)  # noqa: S101  # noqa: S101
        assert isinstance(el.location.get("x"), int)  # noqa: S101
        assert isinstance(el.location.get("y"), int)  # noqa: S101

    @pytest.mark.skip(
        reason="UnknownCommandError. "
        "The requested resource could not be found, or a request was received using an HTTP method "
        "that is not supported by the mapped resource"
    )
    def test_aria_role(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.aria_role, str)  # noqa: S101  # noqa: S101
        assert el.aria_role == ""  # noqa: S101  # noqa: S101

    @pytest.mark.skip(
        reason="UnknownCommandError. "
        "The requested resource could not be found, or a request was received using an HTTP method "
        "that is not supported by the mapped resource"
    )
    def test_accessible_name(self, app: Shadowstep, android_settings_open_close: Any):
        el = app.get_element(LOCATOR_CONNECTED_DEVICES)
        assert isinstance(el.accessible_name, str)  # noqa: S101  # noqa: S101
        assert el.accessible_name == ""  # noqa: S101  # noqa: S101
