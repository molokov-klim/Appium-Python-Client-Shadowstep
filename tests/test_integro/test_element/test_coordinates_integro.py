# ruff: noqa
# pyright: ignore

import pytest
from icecream import ic

from shadowstep.shadowstep import Shadowstep

LOCATOR = {
        "text": "Search settings",
                "resource-id": "com.android.settings:id/search_action_bar_title",
                "class": "android.widget.TextView",
            }

class TestCoordinates:
    def test_get_coordinates(self, app: Shadowstep, android_settings_open_close: None):
        el = app.get_element(LOCATOR)
        coords = el.get_coordinates()
        ic(coords)
        left, top, right, bottom = map(int, el.bounds.strip("[]").replace("][", ",").split(","))
        assert isinstance(coords, tuple) and len(coords) == 4  # noqa: S101, PT018
        assert coords == (left, top, right, bottom)  # noqa: S101

    def test_get_center(self, app: Shadowstep, android_settings_open_close: None):
        el = app.get_element(LOCATOR)
        center = el.get_center()
        left, top, right, bottom = map(int, el.bounds.strip("[]").replace("][", ",").split(","))
        x = int((left + right) / 2)
        y = int((top + bottom) / 2)
        assert isinstance(center, tuple) and len(center) == 2  # noqa: S101, PT018
        assert center == (x, y)  # noqa: S101  # noqa: S101

    def test_location_in_view(self, app: Shadowstep, android_settings_open_close: None):
        el = app.get_element(LOCATOR)
        assert isinstance(el.location_in_view, dict)  # noqa: S101
        assert isinstance(el.location_in_view.get("x"), int)  # noqa: S101
        assert isinstance(el.location_in_view.get("y"), int)  # noqa: S101

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_location_once_scrolled_into_view(self, app: Shadowstep, android_settings_open_close: None):
        el = app.get_element(LOCATOR)
        loc = el.location_once_scrolled_into_view
        assert "x" in loc and "y" in loc  # noqa: S101, PT018
