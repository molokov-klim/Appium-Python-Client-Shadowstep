# ruff: noqa
# pyright: ignore
import re
import time
from typing import Any

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep


# ruff: noqa: S101
class TestElementProperties:
    def test_get_attribute(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert el.get_attribute("content-desc") == "Phone"

    def test_get_attribute_no_such_element(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"content-desc": "non_existing"})
        el.timeout = 3
        with pytest.raises(ShadowstepElementException):
            el.get_attribute("text")

    def test_get_attributes(self, app: Shadowstep, stability: None):
        element = app.get_element(
            locator={
                "package": "com.android.launcher3",
                "class": "android.view.ViewGroup",
                "resource-id": "com.android.launcher3:id/hotseat",
            }
        )
        attrs = element.get_attributes()
        assert isinstance(attrs, dict)  # noqa: S101  # noqa: S101
        assert "bounds" in attrs  # noqa: S101  # noqa: S101

    def test_get_property(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        with pytest.raises(ShadowstepElementException):
            el.get_property("enabled")

    def test_get_dom_attribute(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert el.get_dom_attribute("class") == "android.widget.TextView"  # noqa: S101  # noqa: S101

    def test_is_displayed(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.is_displayed(), bool)  # noqa: S101  # noqa: S101
        assert el.is_displayed()  # noqa: S101  # noqa: S101

    def test_is_visible(self, app: Shadowstep, press_home: Any, stability: None):
        phone = app.get_element(locator={"text": "Phone"}, timeout=5)
        search = app.get_element(
            locator={"resource-id": "com.android.quicksearchbox:id/search_widget_text"}, timeout=5
        )
        phone.wait(timeout=5)
        assert search.is_visible() is True  # noqa: S101  # noqa: S101
        assert phone.is_visible() is True  # noqa: S101  # noqa: S101
        phone.tap()
        time.sleep(3)
        assert not phone.is_visible()  # noqa: S101  # noqa: S101
        assert not search.is_visible()  # noqa: S101  # noqa: S101

    def test_is_selected(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.is_selected(), bool)  # noqa: S101  # noqa: S101
        assert not el.is_selected()  # noqa: S101  # noqa: S101

    def test_is_enabled(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.is_enabled(), bool)  # noqa: S101  # noqa: S101
        assert el.is_enabled()  # noqa: S101  # noqa: S101

    def test_is_contains(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"resource-id": "com.android.launcher3:id/hotseat"})
        assert el.is_contains({"text": "Phone"}) is True  # noqa: S101  # noqa: S101

    def test_tag_name(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.tag_name, str)  # noqa: S101  # noqa: S101
        assert el.tag_name == "Phone"  # noqa: S101  # noqa: S101

    def test_text(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.text, str)  # noqa: S101  # noqa: S101
        assert el.text == "Phone"  # noqa: S101  # noqa: S101

    def test_resource_id(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"resource-id": "com.android.launcher3:id/launcher"})
        assert isinstance(el.resource_id, str)  # noqa: S101  # noqa: S101
        assert el.resource_id == "com.android.launcher3:id/launcher"  # noqa: S101  # noqa: S101

    def test_class_(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.class_, str)  # noqa: S101  # noqa: S101
        assert el.class_ == "android.widget.TextView"  # noqa: S101  # noqa: S101

    def test_class_name(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.class_name, str)  # noqa: S101  # noqa: S101
        assert el.class_name == "android.widget.TextView"  # noqa: S101  # noqa: S101

    def test_index(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        with pytest.raises(ShadowstepElementException):
            assert isinstance(el.index, str)  # noqa: S101  # noqa: S101

    def test_package(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.package, str)  # noqa: S101  # noqa: S101
        try:
            assert el.package == "com.android.launcher3"  # noqa: S101  # noqa: S101
        except ShadowstepElementException:
            assert el.package == "com.google.android.apps.nexuslauncher"  # noqa: S101  # noqa: S101

    def test_bounds(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.bounds, str)
        assert re.fullmatch(r"\[\d+,\d+\]\[\d+,\d+\]", el.bounds), (
            f"Invalid bounds format: {el.bounds}"
        )

    def test_checked(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.checked, str)  # noqa: S101  # noqa: S101
        assert el.checked == "false"  # noqa: S101  # noqa: S101

    def test_checkable(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.checkable, str)  # noqa: S101  # noqa: S101
        assert el.checkable == "false"  # noqa: S101  # noqa: S101

    def test_enabled(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.enabled, str)  # noqa: S101  # noqa: S101
        assert el.enabled == "true"  # noqa: S101  # noqa: S101

    def test_focusable(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.focusable, str)  # noqa: S101  # noqa: S101
        assert el.focusable == "true"  # noqa: S101  # noqa: S101

    def test_focused(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.focused, str)  # noqa: S101  # noqa: S101
        assert el.focused == "false"  # noqa: S101  # noqa: S101

    def test_long_clickable(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.long_clickable, str)  # noqa: S101  # noqa: S101
        assert el.long_clickable == "true"  # noqa: S101  # noqa: S101

    def test_password(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.password, str)  # noqa: S101  # noqa: S101
        assert el.password == "false"  # noqa: S101, S105

    def test_scrollable(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.scrollable, str)  # noqa: S101  # noqa: S101
        assert el.scrollable == "false"  # noqa: S101  # noqa: S101

    def test_selected(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.selected, str)  # noqa: S101  # noqa: S101
        assert el.selected == "false"  # noqa: S101  # noqa: S101

    def test_displayed(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.displayed, str)  # noqa: S101  # noqa: S101
        assert el.displayed == "true"  # noqa: S101  # noqa: S101

    def test_shadow_root_error(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"content-desc": "non_existing"})
        with pytest.raises(ShadowstepElementException):
            _ = el.shadow_root

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_size_location_rect(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert "width" in el.size and "height" in el.size  # noqa: S101, PT018
        assert "x" in el.location and "y" in el.location  # noqa: S101, PT018
        assert all(k in el.rect for k in ("x", "y", "width", "height"))  # noqa: S101  # noqa: S101

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_value_of_css_property(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        value = el.value_of_css_property("display")
        assert isinstance(value, str)  # noqa: S101  # noqa: S101

    def test_location(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.location, dict)  # noqa: S101  # noqa: S101
        assert isinstance(el.location.get("x"), int)  # noqa: S101
        assert isinstance(el.location.get("y"), int)  # noqa: S101

    def test_rect(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.rect, dict)  # noqa: S101  # noqa: S101
        assert isinstance(el.location.get("x"), int)  # noqa: S101
        assert isinstance(el.location.get("y"), int)  # noqa: S101

    @pytest.mark.skip(
        reason="UnknownCommandError. "
        "The requested resource could not be found, or a request was received using an HTTP method "
        "that is not supported by the mapped resource"
    )
    def test_aria_role(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.aria_role, str)  # noqa: S101  # noqa: S101
        assert el.aria_role == ""  # noqa: S101  # noqa: S101

    @pytest.mark.skip(
        reason="UnknownCommandError. "
        "The requested resource could not be found, or a request was received using an HTTP method "
        "that is not supported by the mapped resource"
    )
    def test_accessible_name(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"text": "Phone"})
        assert isinstance(el.accessible_name, str)  # noqa: S101  # noqa: S101
        assert el.accessible_name == ""  # noqa: S101  # noqa: S101
