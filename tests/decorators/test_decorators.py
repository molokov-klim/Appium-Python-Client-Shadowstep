"""
Test cases for the shadowstep.decorators module.

This module contains comprehensive tests for all decorators including
fail_safe, retry, time_it, step_info, current_page, and log_info.
"""

import time
from typing import Any
from unittest.mock import Mock, patch

import pytest

from shadowstep.decorators.decorators import (
    DEFAULT_EXCEPTIONS,
    current_page,
    fail_safe,
    log_info,
    retry,
    step_info,
    time_it,
)


class MockClass:
    """Mock class for testing decorators."""

    def __init__(self) -> None:
        """Initialize mock class."""
        self.logger = Mock()
        self.shadowstep = Mock()
        self.driver = Mock()
        self.telegram = Mock()
        self.shadowstep.driver = self.driver
        self._connected = True

    def is_connected(self) -> bool:
        """Mock connection status."""
        return self._connected

    def reconnect(self) -> None:
        """Mock reconnection."""
        self._connected = True

    def get_screenshot(self) -> bytes:
        """Mock screenshot capture."""
        return b"mock_screenshot_data"


class TestFailSafe:
    """Test cases for fail_safe decorator."""

    def test_fail_safe_success_first_attempt(self) -> None:
        """Test fail_safe with successful first attempt."""
        mock_obj = MockClass()

        @fail_safe(retries=3, delay=0.1)
        def test_method(self: MockClass) -> str:
            return "success"

        result = test_method(mock_obj)
        assert result == "success"  # noqa: S101
        assert mock_obj.logger.warning.call_count == 0  # noqa: S101

    def test_fail_safe_retry_on_exception(self) -> None:
        """Test fail_safe with retry on exception."""
        mock_obj = MockClass()
        call_count = 0

        @fail_safe(retries=3, delay=0.1, exceptions=(Exception,))
        def test_method(self: MockClass) -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Test exception")
            return "success"

        result = test_method(mock_obj)
        assert result == "success"  # noqa: S101
        assert call_count == 3  # noqa: S101

    def test_fail_safe_max_retries_exceeded(self) -> None:
        """Test fail_safe when max retries exceeded."""
        mock_obj = MockClass()

        @fail_safe(retries=2, delay=0.1)
        def test_method(self: MockClass) -> str:
            raise Exception("Persistent error")

        with pytest.raises(Exception, match="Persistent error"):
            test_method(mock_obj)

    def test_fail_safe_with_fallback(self) -> None:
        """Test fail_safe with fallback value."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1, fallback="fallback_value")
        def test_method(self: MockClass) -> str:
            raise Exception("Test exception")

        result = test_method(mock_obj)
        assert result == "fallback_value"  # noqa: S101

    def test_fail_safe_with_custom_exception(self) -> None:
        """Test fail_safe with custom exception."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1, raise_exception=ValueError)
        def test_method(self: MockClass) -> str:
            raise Exception("Test exception")

        with pytest.raises(ValueError, match="failed after 1 attempts"):
            test_method(mock_obj)

    def test_fail_safe_reconnection_logic(self) -> None:
        """Test fail_safe reconnection logic."""
        mock_obj = MockClass()
        mock_obj._connected = False
        mock_obj.reconnect = Mock()

        @fail_safe(retries=2, delay=0.1)
        def test_method(self: MockClass) -> str:
            return "success"

        result = test_method(mock_obj)
        assert result == "success"  # noqa: S101
        mock_obj.reconnect.assert_called()

    def test_fail_safe_log_args(self) -> None:
        """Test fail_safe with argument logging."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1, log_args=True)
        def test_method(self: MockClass, arg1: str, arg2: int) -> str:
            raise Exception("Test exception")

        with pytest.raises(Exception, match="Test exception"):
            test_method(mock_obj, "test", 42)

        # Check that debug was called for args logging
        mock_obj.logger.debug.assert_called()


class TestRetry:
    """Test cases for retry decorator."""

    def test_retry_success_first_attempt(self) -> None:
        """Test retry with successful first attempt."""
        call_count = 0

        @retry(max_retries=3, delay=0.1)
        def test_function() -> bool:
            nonlocal call_count
            call_count += 1
            return True

        result = test_function()
        assert result is True  # noqa: S101
        assert call_count == 1  # noqa: S101

    def test_retry_retry_on_false(self) -> None:
        """Test retry when function returns False."""
        call_count = 0

        @retry(max_retries=3, delay=0.1)
        def test_function() -> bool:
            nonlocal call_count
            call_count += 1
            return not call_count < 3

        result = test_function()
        assert result is True  # noqa: S101
        assert call_count == 3  # noqa: S101

    def test_retry_retry_on_none(self) -> None:
        """Test retry when function returns None."""
        call_count = 0

        @retry(max_retries=2, delay=0.1)
        def test_function() -> Any:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return None
            return "success"

        result = test_function()
        assert result == "success"  # noqa: S101
        assert call_count == 2  # noqa: S101

    def test_retry_max_retries_exceeded(self) -> None:
        """Test retry when max retries exceeded."""
        call_count = 0

        @retry(max_retries=2, delay=0.1)
        def test_function() -> bool:
            nonlocal call_count
            call_count += 1
            return False

        result = test_function()
        assert result is False  # noqa: S101
        assert call_count == 2  # noqa: S101


class TestTimeIt:
    """Test cases for time_it decorator."""

    @patch("builtins.print")
    def test_time_it_execution_time(self, mock_print: Mock) -> None:
        """Test time_it decorator measures execution time."""
        @time_it
        def test_function() -> str:
            time.sleep(0.1)
            return "done"

        result = test_function()
        assert result == "done"  # noqa: S101
        mock_print.assert_called_once()
        print_call = mock_print.call_args[0][0]
        assert "Execution time of test_function:" in print_call  # noqa: S101
        assert "seconds" in print_call  # noqa: S101

    @patch("builtins.print")
    def test_time_it_with_arguments(self, mock_print: Mock) -> None:
        """Test time_it decorator with function arguments."""
        @time_it
        def test_function(arg1: str, arg2: int) -> str:
            return f"{arg1}_{arg2}"

        result = test_function("test", 42)
        assert result == "test_42"  # noqa: S101
        mock_print.assert_called_once()


class TestStepInfo:
    """Test cases for step_info decorator."""

    def test_step_info_success(self) -> None:
        """Test step_info decorator with successful execution."""
        mock_obj = MockClass()
        mock_obj.shadowstep.get_screenshot.return_value = b"screenshot_data"

        @step_info("Test step")
        def test_method(self: MockClass) -> str:
            return "success"

        result = test_method(mock_obj)
        assert result == "success"  # noqa: S101

        # Check that logging was called
        mock_obj.logger.info.assert_called()
        mock_obj.shadowstep.get_screenshot.assert_called()

    def test_step_info_with_exception(self) -> None:
        """Test step_info decorator with exception."""
        mock_obj = MockClass()
        mock_obj.shadowstep.get_screenshot.return_value = b"screenshot_data"

        @step_info("Test step")
        def test_method(self: MockClass) -> str:
            raise ValueError("Test error")

        result = test_method(mock_obj)
        assert result is False  # noqa: S101

        # Check that error logging was called
        mock_obj.logger.error.assert_called()

    def test_step_info_screen_recording(self) -> None:
        """Test step_info decorator with screen recording."""
        mock_obj = MockClass()
        mock_obj.shadowstep.get_screenshot.return_value = b"screenshot_data"
        mock_obj.driver.start_recording_screen.return_value = None
        mock_obj.driver.stop_recording_screen.return_value = b"video_data"

        @step_info("Test step")
        def test_method(self: MockClass) -> str:
            return "success"

        result = test_method(mock_obj)
        assert result == "success"  # noqa: S101

        # Check that screen recording was started
        mock_obj.driver.start_recording_screen.assert_called_once()
        # Note: stop_recording_screen is only called on exception, not on success


class TestCurrentPage:
    """Test cases for current_page decorator."""

    def test_current_page_success(self) -> None:
        """Test current_page decorator with successful execution."""
        mock_obj = MockClass()

        @current_page()
        def test_method(self: MockClass) -> bool:
            return True

        result = test_method(mock_obj)
        assert result is True  # noqa: S101

        # Check that logging was called
        mock_obj.logger.info.assert_called()

    def test_current_page_with_arguments(self) -> None:
        """Test current_page decorator with method arguments."""
        mock_obj = MockClass()

        @current_page()
        def test_method(self: MockClass, arg1: str, arg2: int) -> str:
            return f"{arg1}_{arg2}"

        result = test_method(mock_obj, "test", 42)
        assert result == "test_42"  # noqa: S101


class TestLogInfo:
    """Test cases for log_info decorator."""

    @patch("logging.getLogger")
    def test_log_info_success(self, mock_get_logger: Mock) -> None:
        """Test log_info decorator with successful execution."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_info()
        def test_function(arg1: str, arg2: int) -> str:
            return f"{arg1}_{arg2}"

        result = test_function("test", 42)
        assert result == "test_42"  # noqa: S101

        # Check that logging was called
        mock_logger.info.assert_called()

    @patch("logging.getLogger")
    def test_log_info_with_kwargs(self, mock_get_logger: Mock) -> None:
        """Test log_info decorator with keyword arguments."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_info()
        def test_function(**kwargs: Any) -> dict[str, Any]:
            return kwargs

        result = test_function(key1="value1", key2="value2")
        assert result == {"key1": "value1", "key2": "value2"}  # noqa: S101

        # Check that logging was called
        mock_logger.info.assert_called()


class TestDefaultExceptions:
    """Test cases for DEFAULT_EXCEPTIONS constant."""

    def test_default_exceptions_contains_expected_types(self) -> None:
        """Test that DEFAULT_EXCEPTIONS contains expected exception types."""
        from selenium.common import (
            InvalidSessionIdException,
            NoSuchDriverException,
            StaleElementReferenceException,
        )

        expected_exceptions = (
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        )

        assert expected_exceptions == DEFAULT_EXCEPTIONS  # noqa: S101

    def test_default_exceptions_are_exception_types(self) -> None:
        """Test that all items in DEFAULT_EXCEPTIONS are exception types."""
        for exc_type in DEFAULT_EXCEPTIONS:
            assert issubclass(exc_type, Exception)  # noqa: S101


class TestDecoratorIntegration:
    """Integration tests for decorators."""

    def test_multiple_decorators_combined(self) -> None:
        """Test combining multiple decorators."""
        mock_obj = MockClass()

        @fail_safe(retries=2, delay=0.1)
        @time_it
        def test_method(self: MockClass) -> str:
            return "success"

        result = test_method(mock_obj)
        assert result == "success"  # noqa: S101

    def test_decorator_preserves_function_metadata(self) -> None:
        """Test that decorators preserve function metadata."""
        @fail_safe(retries=1, delay=0.1)
        def test_function(arg1: str, arg2: int = 42) -> str:
            """Test function docstring."""
            return f"{arg1}_{arg2}"

        assert test_function.__name__ == "test_function"  # noqa: S101
        assert test_function.__doc__ == "Test function docstring."  # noqa: S101

    def test_decorator_type_hints_preserved(self) -> None:
        """Test that decorators preserve type hints."""
        @log_info()
        def test_function(arg1: str, arg2: int) -> str:
            return f"{arg1}_{arg2}"

        # The function should still be callable with correct types
        result = test_function("test", 42)
        assert result == "test_42"  # noqa: S101
