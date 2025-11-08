# ruff: noqa
# pyright: ignore
"""Test module for basic element waiting functionality.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_element/test_waiting_integro_part_1.py
"""

import logging
from typing import Any

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
LOCATOR_PHONE = {"text": "Phone"}
LOCATOR_BUBBLE = {
    "text": "App info",
    "resource-id": "com.android.launcher3:id/bubble_text",
}


# ruff: noqa: S101
class TestElementWaitingPart1:
    """Collection of tests for basic element waiting behavior."""

    def test_wait_success(self, app: Shadowstep, android_settings_open_close: Any):
        """Test successful waiting for an element to appear."""
        # Test with a real element that should be present

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait(timeout=5, return_bool=True)
        assert result is True

    def test_wait_timeout(self, app: Shadowstep, android_settings_open_close: Any):
        """Test wait timeout for a nonexistent element."""
        # Test with a locator that doesn't exist - expect exception due to element timeout

        el = app.get_element({"resource-id": "non.existent.element"}, timeout=2)
        result = el.wait(timeout=2, return_bool=True)
        assert result is False

    def test_wait_return_element(self, app: Shadowstep, android_settings_open_close: Any):
        """Test that ``wait`` returns the element when ``return_bool`` is False."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait(timeout=5, return_bool=False)
        assert result == el

    def test_wait_visible_success(self, app: Shadowstep, android_settings_open_close: Any):
        """Test successful wait for an element to become visible."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_visible(timeout=5, return_bool=True)
        assert result is True

    def test_wait_visible_timeout(self, app: Shadowstep, android_settings_open_close: Any):
        """Test ``wait_visible`` timeout for an invisible element."""

        el = app.get_element({"resource-id": "non.existent.element"}, timeout=2)
        result = el.wait_visible(timeout=2, return_bool=True)
        assert result is False

    def test_wait_clickable_success(self, app: Shadowstep, android_settings_open_close: Any):
        """Test successful wait for an element to become clickable."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_clickable(timeout=5, return_bool=True)
        assert result is True

    def test_wait_clickable_timeout(self, app: Shadowstep, android_settings_open_close: Any):
        """Test ``wait_clickable`` timeout for a non-clickable element."""

        el = app.get_element({"resource-id": "non.existent.element"}, timeout=2)
        result = el.wait_clickable(timeout=2, return_bool=True)
        assert result is False

    def test_wait_for_not_success(self, app: Shadowstep, android_settings_open_close: Any):
        """Test successful waiting for an element to disappear."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_for_not(timeout=2, return_bool=True)
        assert result is False

    def test_wait_for_not_visible_success(self, app: Shadowstep, android_settings_open_close: Any):
        """Test successful wait for an element to become invisible."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_for_not_visible(timeout=2, return_bool=True)
        assert result is False

