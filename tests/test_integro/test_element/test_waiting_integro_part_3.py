# ruff: noqa
# pyright: ignore
"""
Модуль тестирования функциональности ожидания элементов с общими локаторами и таймаутами.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_element/test_waiting_integro_part_3.py
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
class TestElementWaitingPart3:
    """Набор тестов для функциональности ожидания элементов с общими локаторами и таймаутами."""

    def test_wait_clickable_with_none_locator(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Тест поведения метода wait_clickable с общим локатором."""

        el = app.get_element(("xpath", "//*"), timeout=5)  # Find any element
        result = el.wait_clickable(timeout=5, return_bool=True)
        assert result is True  # Generic xpath "//*" finds elements

    def test_wait_for_not_with_none_locator(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Тест поведения метода wait_for_not с общим локатором."""

        el = app.get_element(("xpath", "//*"), timeout=5)  # Find any element
        result = el.wait_for_not(timeout=2, return_bool=True)
        assert result is False  # wait_for_not returns False for valid locators that exist

    def test_wait_for_not_visible_with_none_locator(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Тест поведения метода wait_for_not_visible с общим локатором."""

        el = app.get_element(("xpath", "//*"), timeout=5)  # Find any element
        result = el.wait_for_not_visible(timeout=2, return_bool=True)
        assert result is False

    def test_wait_for_not_clickable_with_none_locator(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Тест поведения метода wait_for_not_clickable с общим локатором."""

        el = app.get_element(("xpath", "//*"), timeout=5)  # Find any element
        result = el.wait_for_not_clickable(timeout=2, return_bool=True)
        assert result is False

    def test_wait_timeout_exceeds_element_timeout(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Тест, что wait учитывает таймаут элемента, когда он короче таймаута метода."""

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
        """Тест, что все методы wait возвращают Element при return_bool=False."""
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
        """Тест методов wait с нулевым таймаутом."""
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
        """Тест методов wait с очень маленькой частотой опроса."""
        el = app.get_element(LOCATOR_SEARCH_SETTINGS)

        # Test with very small poll frequency
        result = el.wait(timeout=2, poll_frequency=0.01, return_bool=True)
        assert result is True

    def test_wait_methods_with_large_poll_frequency(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Тест методов wait с большой частотой опроса."""
        el = app.get_element(LOCATOR_SEARCH_SETTINGS)

        # Test with large poll frequency
        result = el.wait(timeout=2, poll_frequency=2.0, return_bool=True)
        assert result is True

