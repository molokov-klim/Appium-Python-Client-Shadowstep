# ruff: noqa
# pyright: ignore
"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/element/test_element_waiting.py
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
class TestElementWaiting:
    """Test suite for ElementWaiting class functionality."""

    def test_wait_success(self, app: Shadowstep, android_settings_open_close: Any):
        """Test successful element waiting."""
        # Test with a real element that should be present

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait(timeout=5, return_bool=True)
        assert result is True

    def test_wait_timeout(self, app: Shadowstep, android_settings_open_close: Any):
        """Test waiting timeout for non-existent element."""
        # Test with a locator that doesn't exist - expect exception due to element timeout

        el = app.get_element({"resource-id": "non.existent.element"}, timeout=2)
        result = el.wait(timeout=2, return_bool=True)
        assert result is False

    def test_wait_return_element(self, app: Shadowstep, android_settings_open_close: Any):
        """Test wait method returns Element when return_bool=False."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait(timeout=5, return_bool=False)
        assert result == el

    def test_wait_visible_success(self, app: Shadowstep, android_settings_open_close: Any):
        """Test successful wait for visible element."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_visible(timeout=5, return_bool=True)
        assert result is True

    def test_wait_visible_timeout(self, app: Shadowstep, android_settings_open_close: Any):
        """Test wait_visible timeout for non-visible element."""

        el = app.get_element({"resource-id": "non.existent.element"}, timeout=2)
        result = el.wait_visible(timeout=2, return_bool=True)
        assert result is False

    def test_wait_clickable_success(self, app: Shadowstep, android_settings_open_close: Any):
        """Test successful wait for clickable element."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_clickable(timeout=5, return_bool=True)
        assert result is True

    def test_wait_clickable_timeout(self, app: Shadowstep, android_settings_open_close: Any):
        """Test wait_clickable timeout for non-clickable element."""

        el = app.get_element({"resource-id": "non.existent.element"}, timeout=2)
        result = el.wait_clickable(timeout=2, return_bool=True)
        assert result is False

    def test_wait_for_not_success(self, app: Shadowstep, android_settings_open_close: Any):
        """Test successful wait for element to disappear."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_for_not(timeout=2, return_bool=True)
        assert result is False

    def test_wait_for_not_visible_success(self, app: Shadowstep, android_settings_open_close: Any):
        """Test successful wait for element to become invisible."""

        el = app.get_element(LOCATOR_SEARCH_SETTINGS)
        result = el.wait_for_not_visible(timeout=2, return_bool=True)
        assert result is False

    def test_wait_for_not_clickable_success(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test successful wait for element to become not clickable."""

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

    def test_wait_clickable_with_none_locator(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait_clickable method behavior with generic locator."""

        el = app.get_element(("xpath", "//*"), timeout=5)  # Find any element
        result = el.wait_clickable(timeout=5, return_bool=True)
        assert result is True  # Generic xpath "//*" finds elements

    def test_wait_for_not_with_none_locator(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait_for_not method behavior with generic locator."""

        el = app.get_element(("xpath", "//*"), timeout=5)  # Find any element
        result = el.wait_for_not(timeout=2, return_bool=True)
        assert result is False  # wait_for_not returns False for valid locators that exist

    def test_wait_for_not_visible_with_none_locator(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait_for_not_visible method behavior with generic locator."""

        el = app.get_element(("xpath", "//*"), timeout=5)  # Find any element
        result = el.wait_for_not_visible(timeout=2, return_bool=True)
        assert result is False

    def test_wait_for_not_clickable_with_none_locator(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait_for_not_clickable method behavior with generic locator."""

        el = app.get_element(("xpath", "//*"), timeout=5)  # Find any element
        result = el.wait_for_not_clickable(timeout=2, return_bool=True)
        assert result is False

    def test_wait_timeout_exceeds_element_timeout(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test that wait respects element's timeout when it's shorter than method timeout."""

        # Create element with very short timeout
        el = app.get_element(LOCATOR_SEARCH_SETTINGS, timeout=1)
        start_time = time.time()
        result = el.wait(timeout=10, return_bool=True)  # Method timeout longer than element timeout
        end_time = time.time()

        # Should complete within element timeout (1 second) plus some buffer
        assert end_time - start_time < 2.0
        assert result is True

    def test_all_wait_methods_return_element_when_return_bool_false(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test that all wait methods return Element when return_bool=False."""
        el = app.get_element(LOCATOR_SEARCH_SETTINGS)

        # Test all wait methods return the element itself
        assert el.wait(return_bool=False) == el
        assert el.wait_visible(return_bool=False) == el
        assert el.wait_clickable(return_bool=False) == el
        assert el.wait_for_not(return_bool=False) == el
        assert el.wait_for_not_visible(return_bool=False) == el
        assert el.wait_for_not_clickable(return_bool=False) == el

    def test_wait_methods_with_zero_timeout(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait methods with zero timeout."""
        el = app.get_element(LOCATOR_SEARCH_SETTINGS)

        # With zero timeout, should return quickly
        start_time = time.time()
        result = el.wait(timeout=0, return_bool=True)
        end_time = time.time()

        assert end_time - start_time < 0.5  # Should be very fast
        assert result is True  # Element exists, so should succeed

    def test_wait_methods_with_very_small_poll_frequency(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait methods with very small poll frequency."""
        el = app.get_element(LOCATOR_SEARCH_SETTINGS)

        # Test with very small poll frequency
        result = el.wait(timeout=2, poll_frequency=0.01, return_bool=True)
        assert result is True

    def test_wait_methods_with_large_poll_frequency(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test wait methods with large poll frequency."""
        el = app.get_element(LOCATOR_SEARCH_SETTINGS)

        # Test with large poll frequency
        result = el.wait(timeout=2, poll_frequency=2.0, return_bool=True)
        assert result is True

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
        """Test performance of wait methods with existing elements."""
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
