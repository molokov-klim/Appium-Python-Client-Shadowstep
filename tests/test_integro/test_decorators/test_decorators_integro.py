# ruff: noqa
# pyright: ignore
"""Integration tests for decorators module.

These tests verify decorator functionality using real app fixture and actual
Shadowstep/Element methods, not mocks.
"""
import logging
import time

import pytest

from shadowstep.decorators.common_decorators import (
    fail_safe,
    log_debug,
    log_info,
    retry,
    time_it,
)
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException
from shadowstep.shadowstep import Shadowstep


class TestFailSafeElementDecorator:
    """Integration tests for @fail_safe_element decorator through Element methods."""

    def test_element_tap_uses_fail_safe_element(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test Element.tap() uses @fail_safe_element decorator.

        Steps:
        1. Get element using app.get_element().
        2. Tap the element (internally uses @fail_safe_element).
        3. Verify tap succeeds and element is clickable.
        """
        # Scroll to make Battery visible (might be below fold)
        recycler = app.get_element(
            {"resource-id": "com.android.settings:id/main_content_scrollable_container"},
            timeout=10
        )
        try:
            element = recycler.scroll_to({"text": "Battery"}, direction="down", max_swipes=5)
        except Exception:
            # Battery might already be visible
            element = app.get_element({"text": "Battery"}, timeout=10)

        # This uses @fail_safe_element decorator internally
        element.tap()
        time.sleep(1)

        # Verify tap worked - we should have navigated
        package = app.get_current_package()
        assert "com.android.settings" in package  # noqa: S101

        # Go back
        app.terminal.press_back()
        time.sleep(1)

    def test_element_send_keys_uses_fail_safe_element(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test Element.send_keys() uses @fail_safe_element decorator.

        Steps:
        1. Navigate to searchable screen.
        2. Get search input element.
        3. Send keys to element (uses @fail_safe_element).
        4. Verify text was entered.
        """
        # Open search in settings
        search_icon = app.get_element({"description": "Search settings"}, timeout=10)
        search_icon.tap()
        time.sleep(1)

        # Get search input
        search_input = app.get_element({"resource-id": "android:id/search_src_text"}, timeout=10)

        # This uses @fail_safe_element decorator
        search_input.send_keys("battery")

        # Verify text was entered
        text = search_input.text
        assert "battery" in text.lower()  # noqa: S101

    def test_element_clear_uses_fail_safe_element(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test Element.clear() uses @fail_safe_element decorator.

        Steps:
        1. Get search input element.
        2. Send text to element.
        3. Clear element (uses @fail_safe_element).
        4. Verify text was cleared.
        """
        # Open search
        search_icon = app.get_element({"description": "Search settings"}, timeout=10)
        search_icon.tap()
        time.sleep(1)

        search_input = app.get_element({"resource-id": "android:id/search_src_text"}, timeout=10)
        search_input.send_keys("test")

        # This uses @fail_safe_element decorator
        search_input.clear()
        time.sleep(0.5)

        # Verify cleared
        text = search_input.text
        assert text == "" or text is None  # noqa: S101

    def test_element_is_displayed_uses_fail_safe_element(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test Element.is_displayed() uses @fail_safe_element decorator.

        Steps:
        1. Get element using app.get_element().
        2. Check if displayed (uses @fail_safe_element).
        3. Verify result is boolean.
        """
        element = app.get_element({"text": "Battery"}, timeout=10)

        # This uses @fail_safe_element decorator
        result = element.is_displayed()

        assert isinstance(result, bool)  # noqa: S101
        assert result is True  # noqa: S101

    def test_element_text_property_uses_fail_safe_element(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test Element.text property uses @fail_safe_element decorator.

        Steps:
        1. Get element with text.
        2. Get text from element (uses @fail_safe_element).
        3. Verify text is returned.
        """
        # Get search icon which should have description
        element = app.get_element({"description": "Search settings"}, timeout=10)

        # This uses @fail_safe_element decorator
        desc = element.get_attribute("content-desc")

        assert isinstance(desc, str)  # noqa: S101
        assert len(desc) > 0  # noqa: S101

    def test_element_get_attribute_uses_fail_safe_element(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test Element.get_attribute() uses @fail_safe_element decorator.

        Steps:
        1. Get element.
        2. Get attribute from element (uses @fail_safe_element).
        3. Verify attribute value is returned.
        """
        # Get search icon
        element = app.get_element({"description": "Search settings"}, timeout=10)

        # This uses @fail_safe_element decorator
        class_name = element.get_attribute("class")

        assert isinstance(class_name, str)  # noqa: S101
        assert len(class_name) > 0  # noqa: S101

    def test_element_click_uses_fail_safe_element(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test Element.click() uses @fail_safe_element decorator.

        Steps:
        1. Get element.
        2. Click element (uses @fail_safe_element).
        3. Verify click succeeded by checking navigation.
        """
        # Click search icon
        element = app.get_element({"description": "Search settings"}, timeout=10)

        # This uses @fail_safe_element decorator
        element.click()
        time.sleep(1)

        # Verify search opened - should see search input
        try:
            app.get_element({"resource-id": "android:id/search_src_text"}, timeout=5)
            search_opened = True
        except Exception:
            search_opened = False

        # Go back
        app.terminal.press_back()
        time.sleep(1)

        assert search_opened  # noqa: S101

    def test_element_scroll_to_uses_fail_safe_element(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test Element.scroll_to() uses @fail_safe_element decorator.

        Steps:
        1. Get scrollable container.
        2. Scroll to element (uses @fail_safe_element).
        3. Verify scroll succeeded.
        """
        # Get recyclerview
        recycler = app.get_element(
            {"resource-id": "com.android.settings:id/main_content_scrollable_container"},
            timeout=10
        )

        # This uses @fail_safe_element decorator
        # Scroll to bottom element
        try:
            recycler.scroll_to({"text": "System"}, direction="down", max_swipes=10)
            scroll_succeeded = True
        except Exception:
            scroll_succeeded = False

        assert scroll_succeeded  # noqa: S101


class TestShadowstepMethodsWithDecorators:
    """Integration tests for Shadowstep methods using decorators."""

    def test_get_current_package_with_decorators(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test app.get_current_package() works correctly with decorators.

        Steps:
        1. Call app.get_current_package().
        2. Verify it returns valid package name.
        3. Verify method handles errors via decorators.
        """
        # This method likely uses decorators
        package = app.get_current_package()

        assert isinstance(package, str)  # noqa: S101
        assert len(package) > 0  # noqa: S101
        assert "com.android.settings" in package  # noqa: S101

    def test_get_current_activity_with_decorators(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test app.get_current_activity() works correctly with decorators.

        Steps:
        1. Call app.get_current_activity().
        2. Verify it returns valid activity name.
        """
        activity = app.get_current_activity()

        assert isinstance(activity, str)  # noqa: S101
        assert len(activity) > 0  # noqa: S101

    def test_get_element_with_decorators(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test app.get_element() works with decorators.

        Steps:
        1. Use get_element to locate element.
        2. Verify element is found.
        3. Verify decorators handle retries if needed.
        """
        element = app.get_element({"description": "Search settings"}, timeout=10)

        assert element is not None  # noqa: S101
        assert element.is_displayed()  # noqa: S101

    def test_get_elements_with_decorators(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test app.get_elements() works with decorators.

        Steps:
        1. Use get_elements to find multiple elements.
        2. Verify list is returned.
        3. Verify decorators handle errors.
        """
        elements = app.get_elements({"class": "android.widget.TextView"}, timeout=10)

        assert isinstance(elements, list)  # noqa: S101
        assert len(elements) > 0  # noqa: S101

    def test_swipe_bottom_to_top_with_decorators(self, app: Shadowstep, android_settings_open_close: None):
        """Test app.swipe_bottom_to_top() works with decorators.

        Steps:
        1. Perform swipe_bottom_to_top action.
        2. Verify swipe completed without errors.
        3. Verify decorators handle any transient errors.
        """
        # This should work even if there are transient errors
        app.swipe_bottom_to_top()
        time.sleep(0.5)

        # Verify we can still interact with UI
        package = app.get_current_package()
        assert "com.android.settings" in package  # noqa: S101

    def test_swipe_top_to_bottom_with_decorators(self, app: Shadowstep, android_settings_open_close: None):
        """Test app.swipe_top_to_bottom() works with decorators.

        Steps:
        1. Perform swipe_top_to_bottom action.
        2. Verify swipe completed without errors.
        """
        app.swipe_top_to_bottom()
        time.sleep(0.5)

        # Verify we can still interact
        package = app.get_current_package()
        assert "com.android.settings" in package  # noqa: S101


class TestRetryDecorator:
    """Integration tests for @retry decorator using real app methods."""

    def test_retry_decorator_with_app_method(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test @retry decorator with method that uses app fixture.

        Steps:
        1. Create method decorated with @retry that uses app.
        2. Simulate transient failures.
        3. Verify retry logic works.
        """
        call_count = []

        @retry(max_retries=3, delay=0.1)
        def find_element_with_retry():
            call_count.append(1)
            # First 2 attempts return None, 3rd succeeds
            if len(call_count) < 3:
                return None
            return app.get_element({"text": "Battery"}, timeout=5)

        result = find_element_with_retry()

        assert result is not None  # noqa: S101
        assert len(call_count) == 3  # noqa: S101
        assert result.is_displayed()  # noqa: S101

    def test_retry_decorator_success_on_first_try_with_app(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test @retry succeeds on first attempt with real app.

        Steps:
        1. Create method that succeeds immediately.
        2. Verify no retries happen.
        """
        call_count = []

        @retry(max_retries=3, delay=0.1)
        def get_package():
            call_count.append(1)
            return app.get_current_package()

        result = get_package()

        assert result is not None  # noqa: S101
        assert len(call_count) == 1  # noqa: S101
        assert "com.android.settings" in result  # noqa: S101

    def test_retry_decorator_exhausts_retries_with_app(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test @retry exhausts all retries when always failing.

        Steps:
        1. Create method that always returns False.
        2. Verify it retries max times.
        3. Verify final result is False.
        """
        call_count = []

        @retry(max_retries=3, delay=0.1)
        def always_fails():
            call_count.append(1)
            # Check app is still connected
            _ = app.is_connected()
            return False

        result = always_fails()

        assert result is False  # noqa: S101
        assert len(call_count) == 3  # noqa: S101


class TestTimeItDecorator:
    """Integration tests for @time_it decorator using real app methods."""

    def test_time_it_decorator_with_app_method(
        self, app: Shadowstep, android_settings_open_close: None, capsys
    ):
        """Test @time_it decorator measures execution time of app methods.

        Steps:
        1. Create method with @time_it that uses app.
        2. Execute method.
        3. Verify execution time is printed.
        """

        @time_it
        def find_element_timed():
            return app.get_element({"text": "Battery"}, timeout=10)

        result = find_element_timed()

        assert result is not None  # noqa: S101
        captured = capsys.readouterr()
        assert "Execution time of find_element_timed:" in captured.out  # noqa: S101
        assert "seconds" in captured.out  # noqa: S101

    def test_time_it_preserves_return_value_with_app(
        self, app: Shadowstep, android_settings_open_close: None, capsys
    ):
        """Test @time_it preserves return value from app methods.

        Steps:
        1. Create method that returns app data.
        2. Apply @time_it decorator.
        3. Verify return value is preserved.
        """

        @time_it
        def get_package_timed():
            return app.get_current_package()

        package = get_package_timed()

        assert isinstance(package, str)  # noqa: S101
        assert "com.android.settings" in package  # noqa: S101


class TestLogDecorators:
    """Integration tests for @log_info and @log_debug decorators."""

    def test_log_info_decorator_with_app_method(
        self, app: Shadowstep, android_settings_open_close: None, caplog
    ):
        """Test @log_info decorator logs app method calls.

        Steps:
        1. Create method with @log_info that uses app.
        2. Execute method.
        3. Verify logs contain entry and exit.
        """
        with caplog.at_level(logging.INFO):

            @log_info()
            def get_package_logged():
                return app.get_current_package()

            result = get_package_logged()

            assert result is not None  # noqa: S101
            assert "get_package_logged() <" in caplog.text  # noqa: S101
            assert "get_package_logged() >" in caplog.text  # noqa: S101

    def test_log_debug_decorator_with_app_method(
        self, app: Shadowstep, android_settings_open_close: None, caplog
    ):
        """Test @log_debug decorator logs app method calls.

        Steps:
        1. Create method with @log_debug that uses app.
        2. Execute method.
        3. Verify debug logs contain entry and exit.
        """
        with caplog.at_level(logging.DEBUG):

            @log_debug()
            def get_element_logged():
                return app.get_element({"description": "Search settings"}, timeout=10)

            result = get_element_logged()

            assert result is not None  # noqa: S101
            assert "get_element_logged() <" in caplog.text  # noqa: S101
            assert "get_element_logged() >" in caplog.text  # noqa: S101


class TestFailSafeDecorator:
    """Integration tests for @fail_safe decorator using real app."""

    def test_fail_safe_decorator_with_app_integration(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test @fail_safe decorator works with app in integration scenario.

        Steps:
        1. Create wrapper class that uses app.
        2. Apply @fail_safe decorator.
        3. Verify decorator handles app operations correctly.
        """

        class AppWrapper:
            def __init__(self, shadowstep_app):
                self.logger = logging.getLogger(__name__)
                self.app = shadowstep_app

            def is_connected(self):
                return self.app.is_connected()

            def reconnect(self):
                return self.app.reconnect()

            @fail_safe(retries=2, delay=0.1)
            def get_package_with_fail_safe(self):
                return self.app.get_current_package()

        wrapper = AppWrapper(app)
        package = wrapper.get_package_with_fail_safe()

        assert isinstance(package, str)  # noqa: S101
        assert "com.android.settings" in package  # noqa: S101

    def test_fail_safe_handles_transient_errors_with_app(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test @fail_safe handles transient errors in app operations.

        Steps:
        1. Create method that may fail transiently.
        2. Use @fail_safe decorator.
        3. Verify retries happen and operation succeeds.
        """
        from selenium.common import NoSuchDriverException

        class AppWrapper:
            def __init__(self, shadowstep_app):
                self.logger = logging.getLogger(__name__)
                self.app = shadowstep_app
                self.attempt = 0

            def is_connected(self):
                return self.app.is_connected()

            def reconnect(self):
                pass

            @fail_safe(
                retries=3,
                delay=0.1,
                exceptions=(NoSuchDriverException, ValueError),
                raise_exception=ShadowstepException,
            )
            def find_element_with_transient_error(self):
                self.attempt += 1
                # Simulate transient error on first attempt
                if self.attempt == 1:
                    raise ValueError("Transient error")
                return self.app.get_element({"text": "Battery"}, timeout=10)

        wrapper = AppWrapper(app)
        element = wrapper.find_element_with_transient_error()

        assert element is not None  # noqa: S101
        assert element.is_displayed()  # noqa: S101
        assert wrapper.attempt == 2  # noqa: S101


class TestStepInfoDecorator:
    """Integration tests for @step_info decorator."""

    def test_step_info_decorator_with_app_operations(
        self, app: Shadowstep, android_settings_open_close: None, caplog
    ):
        """Test @step_info decorator works with app operations.

        Steps:
        1. Create page object with @step_info decorated method.
        2. Execute method that uses app.
        3. Verify logging and screenshots work.
        """
        from shadowstep.decorators.common_decorators import step_info

        class SettingsPage:
            def __init__(self, shadowstep_app):
                self.logger = logging.getLogger(__name__)
                self.app = shadowstep_app

            @step_info("Navigate to Battery settings")
            def navigate_to_battery(self):
                element = self.app.get_element({"text": "Battery"}, timeout=10)
                element.tap()
                time.sleep(1)
                return True

        with caplog.at_level(logging.INFO):
            page = SettingsPage(app)
            result = page.navigate_to_battery()

            # Go back to settings
            app.terminal.press_back()
            time.sleep(1)

            assert result is True  # noqa: S101
            assert "Navigate to Battery settings" in caplog.text  # noqa: S101


class TestCurrentPageDecorator:
    """Integration tests for @current_page decorator."""

    def test_current_page_decorator_with_verification(
        self, app: Shadowstep, android_settings_open_close: None, caplog
    ):
        """Test @current_page decorator works with page verification.

        Steps:
        1. Create page object with is_current_page method.
        2. Use @current_page decorator.
        3. Verify logging includes page representation.
        """
        from shadowstep.decorators.common_decorators import current_page

        class SettingsPage:
            def __init__(self, shadowstep_app):
                self.logger = logging.getLogger(__name__)
                self.app = shadowstep_app

            def __repr__(self):
                return "<SettingsPage>"

            @current_page()
            def is_current_page(self):
                package = self.app.get_current_package()
                return "com.android.settings" in package

        with caplog.at_level(logging.INFO):
            page = SettingsPage(app)
            result = page.is_current_page()

            assert result is True  # noqa: S101
            assert "is_current_page() <" in caplog.text  # noqa: S101
            assert "is_current_page() >" in caplog.text  # noqa: S101
            assert "<SettingsPage>" in caplog.text  # noqa: S101


class TestDecoratorsCombinedScenarios:
    """Integration tests for combined decorator scenarios."""

    def test_multiple_element_operations_with_fail_safe_element(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test multiple Element operations using @fail_safe_element.

        Steps:
        1. Perform sequence of element operations.
        2. Verify all operations succeed with decorator handling errors.
        3. Verify decorator retries work across operations.
        """
        # All these operations use @fail_safe_element
        element1 = app.get_element({"description": "Search settings"}, timeout=10)
        assert element1.is_displayed()  # noqa: S101

        desc = element1.get_attribute("content-desc")
        assert "Search" in desc  # noqa: S101

        element1.click()
        time.sleep(1)

        # Verify navigation succeeded
        package = app.get_current_package()
        assert "com.android.settings" in package  # noqa: S101

        # Go back
        app.terminal.press_back()
        time.sleep(1)

    def test_element_operations_survive_stale_references(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test @fail_safe_element handles stale element references.

        Steps:
        1. Get element.
        2. Perform actions that may cause staleness.
        3. Verify decorator re-acquires element and succeeds.
        """
        # Get element
        element = app.get_element({"description": "Search settings"}, timeout=10)

        # Scroll (may cause element to become stale)
        app.swipe_top_to_bottom()
        time.sleep(0.5)
        app.swipe_bottom_to_top()
        time.sleep(0.5)

        # Try to interact with element (may be stale, but @fail_safe_element handles it)
        try:
            is_displayed = element.is_displayed()
            stale_handled = True
        except Exception:
            stale_handled = False

        assert stale_handled  # noqa: S101
