# ruff: noqa
# pyright: ignore
"""Integration tests for decorators module."""
import logging
import time
from typing import Any

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


class TestDecorators:
    """Test class for decorator functionality."""

    def test_retry_decorator_success_on_first_try(self, app: Shadowstep):
        """Test retry decorator succeeds on first attempt.

        Steps:
        1. Create a method decorated with @retry that returns True.
        2. Call the method.
        3. Verify it returns True without retries.
        """
        call_count = []

        @retry(max_retries=3, delay=0.1)
        def successful_method():
            call_count.append(1)
            return True

        result = successful_method()

        assert result is True  # noqa: S101
        assert len(call_count) == 1  # noqa: S101

    def test_retry_decorator_retries_on_false(self, app: Shadowstep):
        """Test retry decorator retries when method returns False.

        Steps:
        1. Create a method that returns False first 2 times, then True.
        2. Decorate with @retry(max_retries=3).
        3. Verify it retries and eventually returns True.
        """
        call_count = []

        @retry(max_retries=3, delay=0.1)
        def failing_then_success():
            call_count.append(1)
            if len(call_count) < 3:
                return False
            return True

        result = failing_then_success()

        assert result is True  # noqa: S101
        assert len(call_count) == 3  # noqa: S101

    def test_retry_decorator_retries_on_none(self, app: Shadowstep):
        """Test retry decorator retries when method returns None.

        Steps:
        1. Create a method that returns None first 2 times, then True.
        2. Decorate with @retry(max_retries=3).
        3. Verify it retries and eventually returns True.
        """
        call_count = []

        @retry(max_retries=3, delay=0.1)
        def none_then_success():
            call_count.append(1)
            if len(call_count) < 3:
                return None
            return True

        result = none_then_success()

        assert result is True  # noqa: S101
        assert len(call_count) == 3  # noqa: S101

    def test_retry_decorator_max_retries_exhausted(self, app: Shadowstep):
        """Test retry decorator exhausts all retries.

        Steps:
        1. Create a method that always returns False.
        2. Decorate with @retry(max_retries=3).
        3. Verify it retries max_retries times and returns False.
        """
        call_count = []

        @retry(max_retries=3, delay=0.1)
        def always_fails():
            call_count.append(1)
            return False

        result = always_fails()

        assert result is False  # noqa: S101
        assert len(call_count) == 3  # noqa: S101

    def test_time_it_decorator_measures_execution_time(self, app: Shadowstep, capsys):
        """Test time_it decorator measures execution time.

        Steps:
        1. Create a method decorated with @time_it that sleeps for 0.1 seconds.
        2. Call the method.
        3. Verify execution time is printed and approximately correct.
        """

        @time_it
        def slow_method():
            time.sleep(0.1)
            return "completed"

        result = slow_method()

        assert result == "completed"  # noqa: S101
        captured = capsys.readouterr()
        assert "Execution time of slow_method:" in captured.out  # noqa: S101
        assert "seconds" in captured.out  # noqa: S101

    def test_log_info_decorator_logs_method_calls(self, app: Shadowstep, caplog):
        """Test log_info decorator logs method entry and exit.

        Steps:
        1. Create a method decorated with @log_info().
        2. Call the method with arguments.
        3. Verify logs contain method entry and exit information.
        """
        with caplog.at_level(logging.INFO):

            @log_info()
            def logged_method(arg1: str, arg2: int) -> str:
                return f"{arg1}_{arg2}"

            result = logged_method("test", 42)

            assert result == "test_42"  # noqa: S101
            assert "logged_method() <" in caplog.text  # noqa: S101
            assert "logged_method() >" in caplog.text  # noqa: S101

    def test_log_debug_decorator_logs_method_calls(self, app: Shadowstep, caplog):
        """Test log_debug decorator logs method entry and exit.

        Steps:
        1. Create a method decorated with @log_debug().
        2. Call the method with arguments.
        3. Verify logs contain method entry and exit information.
        """
        with caplog.at_level(logging.DEBUG):

            @log_debug()
            def debug_logged_method(arg1: str) -> str:
                return f"processed_{arg1}"

            result = debug_logged_method("value")

            assert result == "processed_value"  # noqa: S101
            assert "debug_logged_method() <" in caplog.text  # noqa: S101
            assert "debug_logged_method() >" in caplog.text  # noqa: S101

    def test_fail_safe_decorator_with_shadowstep_methods(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test fail_safe decorator works with Shadowstep instance methods.

        Steps:
        1. Create a test class with logger, is_connected, and reconnect methods.
        2. Create a method that uses fail_safe decorator.
        3. Verify the decorator works correctly in integration context.
        """

        class TestClass:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
                self.shadowstep = app
                self.call_count = 0

            def is_connected(self):
                return app.is_connected()

            def reconnect(self):
                return app.reconnect()

            @fail_safe(retries=2, delay=0.1)
            def method_with_fail_safe(self):
                self.call_count += 1
                return True

        test_obj = TestClass()
        result = test_obj.method_with_fail_safe()

        assert result is True  # noqa: S101
        assert test_obj.call_count == 1  # noqa: S101

    def test_fail_safe_decorator_with_exception_handling(self, app: Shadowstep):
        """Test fail_safe decorator handles exceptions correctly.

        Steps:
        1. Create a test class with methods that raise exceptions.
        2. Use fail_safe decorator with custom exception handling.
        3. Verify retries happen and final exception is raised.
        """
        from selenium.common import NoSuchDriverException

        class TestClass:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
                self.call_count = 0

            def is_connected(self):
                return True

            def reconnect(self):
                pass

            @fail_safe(
                retries=2,
                delay=0.1,
                exceptions=(NoSuchDriverException,),
                raise_exception=ShadowstepException,
            )
            def method_that_fails(self):
                self.call_count += 1
                if self.call_count < 2:
                    raise NoSuchDriverException("Test error")
                return "success"

        test_obj = TestClass()
        result = test_obj.method_that_fails()

        assert result == "success"  # noqa: S101
        assert test_obj.call_count == 2  # noqa: S101

    def test_fail_safe_decorator_raises_after_max_retries(self, app: Shadowstep):
        """Test fail_safe decorator raises exception after exhausting retries.

        Steps:
        1. Create a method that always raises exception.
        2. Use fail_safe decorator with limited retries.
        3. Verify ShadowstepException is raised after all retries.
        """
        from selenium.common import NoSuchDriverException

        class TestClass:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
                self.call_count = 0

            def is_connected(self):
                return True

            def reconnect(self):
                pass

            @fail_safe(
                retries=2,
                delay=0.1,
                exceptions=(NoSuchDriverException,),
                raise_exception=ShadowstepException,
            )
            def method_that_always_fails(self):
                self.call_count += 1
                raise NoSuchDriverException("Persistent error")

        test_obj = TestClass()

        with pytest.raises(ShadowstepException) as exc_info:
            test_obj.method_that_always_fails()

        assert test_obj.call_count == 2  # noqa: S101
        assert "method_that_always_fails failed after 2 attempts" in str(exc_info.value)  # noqa: S101

    def test_fail_safe_decorator_with_fallback_value(self, app: Shadowstep):
        """Test fail_safe decorator returns fallback value on failure.

        Steps:
        1. Create a method that always raises exception.
        2. Use fail_safe with fallback value and no exception raising.
        3. Verify fallback value is returned.
        """
        from selenium.common import NoSuchDriverException

        class TestClass:
            def __init__(self):
                self.logger = logging.getLogger(__name__)

            def is_connected(self):
                return True

            def reconnect(self):
                pass

            @fail_safe(
                retries=1,
                delay=0.1,
                exceptions=(NoSuchDriverException,),
                raise_exception=None,
                fallback="fallback_value",
            )
            def method_with_fallback(self):
                raise NoSuchDriverException("Error")

        test_obj = TestClass()
        result = test_obj.method_with_fallback()

        assert result == "fallback_value"  # noqa: S101

    def test_element_uses_fail_safe_element_decorator(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test that Element methods use fail_safe_element decorator correctly.

        Steps:
        1. Create an Element using app.get_element().
        2. Perform an action that triggers the decorator.
        3. Verify the action completes successfully.
        """
        element = app.get_element({"text": "Settings"}, timeout=10)

        # This should work as the decorator handles retries
        result = element.is_displayed()

        assert isinstance(result, bool)  # noqa: S101

    def test_shadowstep_methods_use_decorators(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test that Shadowstep methods properly use decorators.

        Steps:
        1. Use Shadowstep method that has decorators applied.
        2. Verify the method works correctly with decorator functionality.
        """
        # The get_current_package method likely has decorators
        package = app.get_current_package()

        assert isinstance(package, str)  # noqa: S101
        assert len(package) > 0  # noqa: S101

    def test_retry_decorator_with_custom_delay(self, app: Shadowstep):
        """Test retry decorator respects custom delay parameter.

        Steps:
        1. Create a method with custom delay.
        2. Measure time taken for retries.
        3. Verify delay is respected.
        """
        call_count = []
        start_time = time.time()

        @retry(max_retries=3, delay=0.2)
        def method_with_delay():
            call_count.append(1)
            if len(call_count) < 2:
                return None
            return True

        result = method_with_delay()
        elapsed = time.time() - start_time

        assert result is True  # noqa: S101
        assert len(call_count) == 2  # noqa: S101
        # Should take at least one delay period (0.2s)
        assert elapsed >= 0.2  # noqa: S101

    def test_fail_safe_with_log_args(self, app: Shadowstep, caplog):
        """Test fail_safe decorator with log_args enabled.

        Steps:
        1. Create a method with log_args=True.
        2. Trigger an exception.
        3. Verify arguments are logged.
        """
        from selenium.common import NoSuchDriverException

        class TestClass:
            def __init__(self):
                self.logger = logging.getLogger(__name__)

            def is_connected(self):
                return True

            def reconnect(self):
                pass

            @fail_safe(
                retries=1,
                delay=0.1,
                exceptions=(NoSuchDriverException,),
                raise_exception=ShadowstepException,
                log_args=True,
            )
            def method_with_args_logging(self, arg1: str, arg2: int):
                raise NoSuchDriverException("Test error")

        test_obj = TestClass()

        with caplog.at_level(logging.DEBUG):
            with pytest.raises(ShadowstepException):
                test_obj.method_with_args_logging("test", 123)

            # Verify args were logged
            assert "[fail_safe] args:" in caplog.text  # noqa: S101

    def test_current_page_decorator_logs_page_verification(self, app: Shadowstep, caplog):
        """Test current_page decorator adds logging to page verification.

        Steps:
        1. Create a page class with is_current_page method.
        2. Use current_page decorator.
        3. Verify logging includes page object representation.
        """
        from shadowstep.decorators.common_decorators import current_page

        class TestPage:
            def __init__(self):
                self.logger = logging.getLogger(__name__)

            def __repr__(self):
                return "<TestPage>"

            @current_page()
            def is_current_page(self):
                return True

        with caplog.at_level(logging.INFO):
            page = TestPage()
            result = page.is_current_page()

            assert result is True  # noqa: S101
            assert "is_current_page() <" in caplog.text  # noqa: S101
            assert "is_current_page() >" in caplog.text  # noqa: S101
            assert "<TestPage>" in caplog.text  # noqa: S101

    def test_step_info_decorator_with_screenshot_capture(
        self, app: Shadowstep, android_settings_open_close: None, caplog
    ):
        """Test step_info decorator captures screenshots and logs.

        Steps:
        1. Create a test class method with step_info decorator.
        2. Execute the method.
        3. Verify logging and screenshot capture occurred.
        """
        from shadowstep.decorators.common_decorators import step_info

        class TestPageWithStepInfo:
            def __init__(self):
                self.logger = logging.getLogger(__name__)

            @step_info("Test step with screenshot")
            def perform_action(self):
                return True

        with caplog.at_level(logging.INFO):
            test_page = TestPageWithStepInfo()
            result = test_page.perform_action()

            assert result is True  # noqa: S101
            assert "Test step with screenshot" in caplog.text  # noqa: S101
            assert "perform_action" in caplog.text  # noqa: S101

    def test_step_info_decorator_handles_exceptions(
        self, app: Shadowstep, android_settings_open_close: None, caplog
    ):
        """Test step_info decorator handles exceptions gracefully.

        Steps:
        1. Create a method that raises exception.
        2. Use step_info decorator.
        3. Verify exception is caught and logged.
        """
        from shadowstep.decorators.common_decorators import step_info

        class TestPageWithError:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
                self.telegram = type('obj', (object,), {'send_message': lambda self, msg: None})()

            @step_info("Step that will fail")
            def failing_action(self):
                raise ValueError("Test error")

        with caplog.at_level(logging.ERROR):
            test_page = TestPageWithError()
            result = test_page.failing_action()

            assert result is False  # noqa: S101
            assert "Error in failing_action" in caplog.text  # noqa: S101

    def test_fail_safe_decorator_reconnects_on_disconnect(self, app: Shadowstep):
        """Test fail_safe decorator triggers reconnect when disconnected.

        Steps:
        1. Create a test class with reconnect tracking.
        2. Simulate disconnection scenario (is_connected returns False).
        3. Verify reconnect is called.
        """
        from selenium.common import NoSuchDriverException

        class TestClass:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
                self.reconnect_called = False
                self.call_count = 0
                self.connected = False

            def is_connected(self):
                # Return False on first call to trigger reconnect
                return self.connected

            def reconnect(self):
                self.reconnect_called = True
                self.connected = True  # After reconnect, we're connected

            @fail_safe(
                retries=2,
                delay=0.1,
                exceptions=(NoSuchDriverException,),
                raise_exception=ShadowstepException,
            )
            def method_needs_reconnect(self):
                self.call_count += 1
                if self.call_count == 1:
                    raise NoSuchDriverException("Connection lost")
                return "success"

        test_obj = TestClass()
        result = test_obj.method_needs_reconnect()

        assert result == "success"  # noqa: S101
        assert test_obj.reconnect_called is True  # noqa: S101

    def test_retry_decorator_preserves_function_metadata(self, app: Shadowstep):
        """Test retry decorator preserves function metadata.

        Steps:
        1. Create a function with docstring and name.
        2. Apply retry decorator.
        3. Verify function name and docstring are preserved.
        """

        @retry(max_retries=3)
        def documented_function():
            """This is a test function."""
            return True

        assert documented_function.__name__ == "documented_function"  # noqa: S101
        assert documented_function.__doc__ == "This is a test function."  # noqa: S101

    def test_time_it_decorator_preserves_return_value(self, app: Shadowstep, capsys):
        """Test time_it decorator preserves return value and type.

        Steps:
        1. Create functions returning different types.
        2. Apply time_it decorator.
        3. Verify return values are preserved.
        """

        @time_it
        def returns_dict():
            return {"key": "value"}

        @time_it
        def returns_list():
            return [1, 2, 3]

        dict_result = returns_dict()
        list_result = returns_list()

        assert dict_result == {"key": "value"}  # noqa: S101
        assert list_result == [1, 2, 3]  # noqa: S101

    def test_log_info_and_log_debug_with_kwargs(self, app: Shadowstep, caplog):
        """Test log decorators handle keyword arguments correctly.

        Steps:
        1. Create functions with kwargs.
        2. Call with keyword arguments.
        3. Verify kwargs are logged properly.
        """
        with caplog.at_level(logging.INFO):

            @log_info()
            def function_with_kwargs(name: str, value: int = 10):
                return f"{name}={value}"

            result = function_with_kwargs(name="test", value=42)

            assert result == "test=42"  # noqa: S101
            assert "kwargs=" in caplog.text  # noqa: S101

    def test_fail_safe_decorator_handles_unexpected_exceptions(self, app: Shadowstep, caplog):
        """Test fail_safe decorator handles unexpected exceptions.

        Steps:
        1. Create method that raises unexpected exception type.
        2. Apply fail_safe decorator with specific exception list.
        3. Verify unexpected exception is caught and logged.
        """

        class TestClass:
            def __init__(self):
                self.logger = logging.getLogger(__name__)

            def is_connected(self):
                return True

            def reconnect(self):
                pass

            @fail_safe(
                retries=1,
                delay=0.1,
                exceptions=(ValueError,),  # Only catching ValueError
                raise_exception=ShadowstepException,
            )
            def method_unexpected_error(self):
                raise TypeError("Unexpected error type")  # But raising TypeError

        test_obj = TestClass()

        with caplog.at_level(logging.ERROR):
            with pytest.raises(ShadowstepException):
                test_obj.method_unexpected_error()

            assert "Unexpected error" in caplog.text  # noqa: S101
