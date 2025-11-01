# ruff: noqa
# pyright: ignore
"""Module for testing element waiting functionality with custom parameters.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_element/test_waiting_integro_part_2.py
"""

import logging
import time
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
class TestElementWaitingPart2:
    """Test suite for element waiting functionality with custom parameters."""

    def test_wait_for_not_clickable_success(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test successful waiting for element to become non-clickable."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_for_not_clickable(timeout=2, return_bool=True)
        assert result is False

    def test_wait_with_custom_timeout_and_poll_frequency(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait method with custom timeout and poll frequency."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        start_time = time.time()
        result = el.wait(timeout=3, poll_frequency=0.1, return_bool=True)
        end_time = time.time()

        assert result is True
        # Should complete within reasonable time since element exists
        assert end_time - start_time < 5.0

    def test_wait_visible_with_custom_parameters(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait_visible with custom timeout and poll frequency."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_visible(timeout=3, poll_frequency=0.1, return_bool=True)
        assert result is True

    def test_wait_clickable_with_custom_parameters(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait_clickable with custom timeout and poll frequency."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_clickable(timeout=3, poll_frequency=0.1, return_bool=True)
        assert result is True

    def test_wait_for_not_with_custom_parameters(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait_for_not with custom timeout and poll frequency."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_for_not(timeout=2, poll_frequency=0.1, return_bool=True)
        assert result is False  # Element exists, so it should return False

    def test_wait_for_not_visible_with_custom_parameters(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait_for_not_visible with custom timeout and poll frequency."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_for_not_visible(timeout=2, poll_frequency=0.1, return_bool=True)
        assert result is False

    def test_wait_for_not_clickable_with_custom_parameters(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait_for_not_clickable with custom timeout and poll frequency."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_for_not_clickable(timeout=2, poll_frequency=0.1, return_bool=True)
        assert result is False

    def test_wait_with_none_locator(self, app: Shadowstep, android_settings_open_close: Any):
        """Test wait method behavior with generic locator."""

        # Create element with generic xpath locator
        el = app.get_element(("xpath", "//*"), timeout=5)  # Find any element
        result = el.wait(timeout=5, return_bool=True)
        assert result is True  # Generic xpath "//*" finds elements

    def test_wait_visible_with_none_locator(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait_visible method behavior with generic locator."""

        el = app.get_element(("xpath", "//*"), timeout=5)  # Find any element
        result = el.wait_visible(timeout=5, return_bool=True)
        assert result is True  # Generic xpath "//*" finds elements
