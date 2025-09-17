import time
from typing import Any

import pytest
from selenium.common import NoSuchElementException

from shadowstep.element.element import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_element.py
"""


class TestElement:

    def test_get_attributes(self, app: Shadowstep, stability: None):
        element = app.get_element(locator={"package": "com.android.launcher3",
                                           "class": "android.view.ViewGroup",
                                           "resource-id": "com.android.launcher3:id/hotseat",
                                           })
        attrs = element.get_attributes()
        assert isinstance(attrs, dict)  # noqa: S101  # noqa: S101
        assert "bounds" in attrs  # noqa: S101  # noqa: S101

    def test_is_within_screen(self, app: Shadowstep, stability: None):
        phone = app.get_element(locator={"content-desc": "Phone"}, timeout=5)
        search = app.get_element(locator={"resource-id": "com.android.quicksearchbox:id/search_widget_text"}, timeout=5)
        assert search.is_visible() is True  # noqa: S101  # noqa: S101
        assert phone.is_visible() is True  # noqa: S101  # noqa: S101
        phone.tap()
        time.sleep(3)
        assert phone.is_visible() is False  # noqa: S101  # noqa: S101
        assert search.is_visible() is False  # noqa: S101  # noqa: S101

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
        with pytest.raises(ShadowstepElementException):
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
