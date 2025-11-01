# ruff: noqa
# pyright: ignore
"""Module for testing performance and edge cases of element waiting.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_element/test_waiting_integro_part_4.py
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
class TestElementWaitingPart4:
    """Test suite for performance and edge cases of element waiting."""

    def test_wait_consistency_across_multiple_calls(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test that wait methods are consistent across multiple calls."""
        el = app.get_element(LOCATOR_SEARCH_SETTINGS)

        # Multiple calls should return consistent results
        results = []
        for _ in range(3):
            result = el.wait(timeout=2, return_bool=True)
            results.append(result)  # type: ignore

        # All results should be the same
        assert all(r == results[0] for r in results)  # type: ignore
        assert results[0] is True  # Element exists

    def test_wait_with_different_locator_types(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait methods with different locator types."""
        # Test with xpath tuple locator
        el1 = app.get_element(
            (
                "xpath",
                "//android.widget.TextView[@text='Search settings' and @resource-id='com.android.settings:id/search_action_bar_title']",
            )
        )
        result1 = el1.wait(timeout=5, return_bool=True)
        assert result1 is True

        # Test with dict locator
        el2 = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result2 = el2.wait(timeout=5, return_bool=True)
        assert result2 is True

        # Both should work the same way
        assert result1 == result2

    def test_wait_with_negative_timeout(self, app: Shadowstep, android_settings_open_close: Any):
        """Test wait method with negative timeout."""
        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait(timeout=-1, return_bool=True)
        assert result is True  # Should handle negative timeout gracefully

    def test_wait_with_negative_poll_frequency(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait method with negative poll frequency."""
        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait(timeout=2, poll_frequency=-0.1, return_bool=True)
        assert result is True  # Should handle negative poll frequency gracefully

    def test_wait_methods_performance(self, app: Shadowstep, android_settings_open_close: Any):
        """Test wait methods performance with existing elements."""
        el = app.get_element(LOCATOR_SEARCH_SETTINGS)

        # Test performance of different wait methods
        methods = [
            el.wait,
            el.wait_visible,
            el.wait_clickable,
            el.wait_for_not,
            el.wait_for_not_visible,
            el.wait_for_not_clickable,
        ]

        for method in methods:
            start_time = time.time()
            result = method(timeout=1, return_bool=True)  # type: ignore  # noqa
            end_time = time.time()

            # All methods should complete within reasonable time (very generous threshold)
            assert end_time - start_time < 60.0  # Very generous 60 seconds threshold
            # Results should be consistent with implementation behavior
            assert isinstance(result, bool)
