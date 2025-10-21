# ruff: noqa
# pyright: ignore
import time

import pytest

from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_element_actions.py
"""

class TestElementActions:

    def test_send_keys(self, app: Shadowstep, android_settings_open_close: None):
        el = app.get_element(
            {
                "text": "Search settings",
                "resource-id": "com.android.settings:id/search_action_bar_title",
                "class": "android.widget.TextView",
            }
        )
        el.tap()
        time.sleep(3)
        app.terminal.past_text("some_text")
        time.sleep(3)
        el = app.get_element(
            {
                "class": "android.widget.EditText",
            }
        )
        assert el.text == "some_text"  # noqa: S101  # noqa: S101
        el.clear()

    def test_clear(self, app: Shadowstep, android_settings_open_close: None):
        el = app.get_element({
                "text": "Search settings",
                "resource-id": "com.android.settings:id/search_action_bar_title",
                "class": "android.widget.TextView",
            })
        el.tap()
        time.sleep(3)
        app.terminal.past_text("some_text")
        time.sleep(3)
        el = app.get_element({
                "class": "android.widget.EditText",
            })
        assert el.text == "some_text"  # noqa: S101  # noqa: S101
        el.clear()
        assert el.text == "Search…"  # noqa: S101  # noqa: S101

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_submit(self, app: Shadowstep, android_settings_open_close: None):
        el = app.get_element({
                "text": "Search settings",
                "resource-id": "com.android.settings:id/search_action_bar_title",
                "class": "android.widget.TextView",
            })
        el.submit()  # Not always valid, but sufficient for test call

    @pytest.mark.skip(reason="Method is not implemented in UiAutomator2")
    def test_set_value(self, app: Shadowstep, android_settings_open_close: None):
        el = app.get_element({
                "text": "Search settings",
                "resource-id": "com.android.settings:id/search_action_bar_title",
                "class": "android.widget.TextView",
            })
        el.tap()
        time.sleep(3)
        el = app.get_element({
                "text": "Search settings",
                "resource-id": "com.android.settings:id/search_action_bar_title",
                "class": "android.widget.TextView",
            })
        el.set_value("test123")
        assert "test123" in el.text  # noqa: S101  # noqa: S101
        el.clear()
