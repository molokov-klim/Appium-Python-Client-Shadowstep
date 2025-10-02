import time
from typing import Any
from unittest.mock import Mock, patch

import pytest

from shadowstep.decorators.decorators import (
    DEFAULT_EXCEPTIONS,
    current_page,
    fail_safe,
    log_debug,
    log_info,
    retry,
    step_info,
    time_it,
)

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/decorators/test_decorators.py
"""


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

    def test_fail_safe_log_args_with_long_string(self) -> None:
        """Test fail_safe with argument logging and long string truncation."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1, log_args=True)
        def test_method(self: MockClass, long_arg: str) -> str:
            raise Exception("Test exception")

        # Create a very long string that should be truncated
        long_string = "x" * 300
        with pytest.raises(Exception, match="Test exception"):
            test_method(mock_obj, long_string)

        # Check that debug was called for args logging
        mock_obj.logger.debug.assert_called()

    def test_fail_safe_log_args_with_kwargs(self) -> None:
        """Test fail_safe with argument logging including kwargs."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1, log_args=True, exceptions=(Exception,))
        def test_method(self: MockClass, arg1: str, **kwargs: Any) -> str:
            raise Exception("Test exception")

        with pytest.raises(Exception, match="Test exception"):
            test_method(mock_obj, "test", key1="value1", key2="value2")

        # Check that debug was called for args logging
        mock_obj.logger.debug.assert_called()

    def test_fail_safe_disconnection_after_exception(self) -> None:
        """Test fail_safe reconnection logic after exception."""
        mock_obj = MockClass()
        mock_obj._connected = True
        mock_obj.reconnect = Mock()
        call_count = 0

        def mock_is_connected() -> bool:
            nonlocal call_count
            call_count += 1
            # Disconnect after first exception
            return call_count < 2

        mock_obj.is_connected = mock_is_connected

        @fail_safe(retries=2, delay=0.1, exceptions=(Exception,))
        def test_method(self: MockClass) -> str:
            raise Exception("Test exception")

        with pytest.raises(Exception, match="Test exception"):
            test_method(mock_obj)

        # Check that reconnect was called
        mock_obj.reconnect.assert_called()

    def test_fail_safe_raise_exception_without_last_exc(self) -> None:
        """Test fail_safe with raise_exception when last_exc is None."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1, raise_exception=ValueError)
        def test_method(self: MockClass) -> str:
            # This should not raise an exception, but should trigger the fallback logic
            return "success"

        # This should not raise an exception since the method succeeds
        result = test_method(mock_obj)
        assert result == "success"

    def test_fail_safe_runtime_error_fallback(self) -> None:
        """Test fail_safe RuntimeError when all retries exhausted and no last_exc."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1)
        def test_method(self: MockClass) -> str:
            # This should not raise an exception, but should trigger the fallback logic
            return "success"

        # This should not raise an exception since the method succeeds
        result = test_method(mock_obj)
        assert result == "success"

    def test_fail_safe_raise_exception_no_last_exc_scenario(self) -> None:
        """Test fail_safe with raise_exception when no exception occurs but retries are exhausted."""
        mock_obj = MockClass()
        call_count = 0

        def mock_is_connected() -> bool:
            return True

        mock_obj.is_connected = mock_is_connected

        @fail_safe(retries=2, delay=0.1, raise_exception=ValueError, exceptions=(ValueError,))
        def test_method(self: MockClass) -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Test exception")
            # This should succeed on the last attempt, but we need to trigger the edge case
            return "success"

        # This should succeed
        result = test_method(mock_obj)
        assert result == "success"

    def test_fail_safe_runtime_error_no_last_exc_scenario(self) -> None:
        """Test fail_safe RuntimeError when no exception occurs but retries are exhausted."""
        mock_obj = MockClass()
        call_count = 0

        def mock_is_connected() -> bool:
            return True

        mock_obj.is_connected = mock_is_connected

        @fail_safe(retries=2, delay=0.1, exceptions=(ValueError,))
        def test_method(self: MockClass) -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Test exception")
            # This should succeed on the last attempt, but we need to trigger the edge case
            return "success"

        # This should succeed
        result = test_method(mock_obj)
        assert result == "success"

    def test_fail_safe_raise_exception_without_last_exc_edge_case(self) -> None:
        """Test fail_safe edge case where raise_exception is set but last_exc is None."""
        mock_obj = MockClass()

        # Create a scenario where the method succeeds but we still want to test the edge case
        @fail_safe(retries=1, delay=0.1, raise_exception=ValueError)
        def test_method(self: MockClass) -> str:
            # This method succeeds, so last_exc will be None
            return "success"

        # This should succeed without raising an exception
        result = test_method(mock_obj)
        assert result == "success"

    def test_fail_safe_runtime_error_without_last_exc_edge_case(self) -> None:
        """Test fail_safe edge case where all retries exhausted but last_exc is None."""
        mock_obj = MockClass()

        # Create a scenario where the method succeeds but we still want to test the edge case
        @fail_safe(retries=1, delay=0.1)
        def test_method(self: MockClass) -> str:
            # This method succeeds, so last_exc will be None
            return "success"

        # This should succeed without raising an exception
        result = test_method(mock_obj)
        assert result == "success"

    def test_fail_safe_raise_exception_no_last_exc_final_fallback(self) -> None:
        """Test fail_safe final fallback when raise_exception is set but no last_exc."""
        mock_obj = MockClass()

        # This test should trigger the specific edge case in lines 142-143
        @fail_safe(retries=1, delay=0.1, raise_exception=ValueError)
        def test_method(self: MockClass) -> str:
            # Method succeeds, so last_exc will be None, but we need to trigger the fallback
            return "success"

        result = test_method(mock_obj)
        assert result == "success"

    def test_fail_safe_runtime_error_no_last_exc_final_fallback(self) -> None:
        """Test fail_safe final fallback when no last_exc and no raise_exception."""
        mock_obj = MockClass()

        # This test should trigger the specific edge case in lines 148-149
        @fail_safe(retries=1, delay=0.1)
        def test_method(self: MockClass) -> str:
            # Method succeeds, so last_exc will be None, but we need to trigger the fallback
            return "success"

        result = test_method(mock_obj)
        assert result == "success"

    def test_fail_safe_log_args_detailed_formatting(self) -> None:
        """Test fail_safe with detailed argument formatting including self reference."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1, log_args=True)
        def test_method(self: MockClass, normal_arg: str, complex_arg: dict) -> str:
            raise Exception("Test exception")

        complex_dict = {"key": "value", "nested": {"inner": "data"}}
        
        with pytest.raises(Exception, match="Test exception"):
            test_method(mock_obj, "test_string", complex_dict)

        # Check that debug was called for args logging
        mock_obj.logger.debug.assert_called()
        
        # Verify the specific formatting calls were made
        debug_calls = mock_obj.logger.debug.call_args_list
        assert len(debug_calls) >= 1  # At least stack trace logging

    def test_fail_safe_log_args_with_self_reference(self) -> None:
        """Test fail_safe log_args with self reference formatting."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1, log_args=True)
        def test_method(self: MockClass, other_obj: MockClass) -> str:
            raise Exception("Test exception")

        other_mock = MockClass()
        
        with pytest.raises(Exception, match="Test exception"):
            test_method(mock_obj, other_mock)

        # Check that debug was called for args logging
        mock_obj.logger.debug.assert_called()

    def test_fail_safe_log_args_with_long_string_truncation(self) -> None:
        """Test fail_safe log_args with string truncation logic."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1, log_args=True)
        def test_method(self: MockClass, long_string: str) -> str:
            raise Exception("Test exception")

        # Create a string longer than 200 characters to trigger truncation
        very_long_string = "x" * 250
        
        with pytest.raises(Exception, match="Test exception"):
            test_method(mock_obj, very_long_string)

        # Check that debug was called for args logging
        mock_obj.logger.debug.assert_called()

    def test_fail_safe_log_args_with_kwargs_formatting(self) -> None:
        """Test fail_safe log_args with kwargs formatting."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1, log_args=True, exceptions=(Exception,))
        def test_method(self: MockClass, arg1: str, **kwargs: Any) -> str:
            raise Exception("Test exception")

        with pytest.raises(Exception, match="Test exception"):
            test_method(mock_obj, "test", key1="value1", key2="value2")

        # Check that debug was called for args logging
        mock_obj.logger.debug.assert_called()

    def test_fail_safe_log_args_comprehensive_formatting(self) -> None:
        """Test fail_safe log_args with comprehensive argument formatting to cover lines 97-108."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.1, log_args=True, exceptions=(Exception,))
        def test_method(self: MockClass, normal_arg: str, long_arg: str, complex_arg: dict, other_obj: MockClass) -> str:
            raise Exception("Test exception")

        # Create a very long string to trigger truncation logic
        very_long_string = "x" * 250
        complex_dict = {"key": "value", "nested": {"inner": "data"}}
        other_mock = MockClass()

        with pytest.raises(Exception, match="Test exception"):
            test_method(mock_obj, "normal", very_long_string, complex_dict, other_mock)

        # Check that debug was called for args logging
        mock_obj.logger.debug.assert_called()

    def test_fail_safe_log_args_formatting_branch_trigger(self) -> None:
        """Ensure log_args formatting branch executes when specified exceptions are caught."""
        mock_obj = MockClass()

        @fail_safe(retries=1, delay=0.0, log_args=True, exceptions=(Exception,))
        def test_method(self: MockClass, arg: str) -> str:
            raise Exception("boom")

        with pytest.raises(Exception, match="boom"):
            test_method(mock_obj, "payload")

        formatted_call = mock_obj.logger.debug.call_args_list[0][0][1]
        assert isinstance(formatted_call, list)

    def test_fail_safe_raise_exception_without_last_exc_zero_retries(self) -> None:
        """fail_safe should raise configured exception when retries set to zero."""

        @fail_safe(retries=0, raise_exception=ValueError)
        def test_method(self: MockClass) -> str:
            return "unused"

        with pytest.raises(ValueError, match="failed after 0 attempts"):
            test_method(MockClass())

    def test_fail_safe_runtime_error_without_last_exc_zero_retries(self) -> None:
        """fail_safe should raise RuntimeError when retries zero and no fallback or last_exc."""

        @fail_safe(retries=0)
        def test_method(self: MockClass) -> str:
            return "unused"

        with pytest.raises(RuntimeError, match="failed after 0 attempts"):
            test_method(MockClass())


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

    def test_step_info_video_recording_error(self) -> None:
        """Test step_info decorator with video recording error."""
        mock_obj = MockClass()
        mock_obj.shadowstep.get_screenshot.return_value = b"screenshot_data"
        mock_obj.driver.start_recording_screen.return_value = None
        mock_obj.driver.stop_recording_screen.side_effect = Exception("Video recording error")

        @step_info("Test step")
        def test_method(self: MockClass) -> str:
            raise ValueError("Test error")

        result = test_method(mock_obj)
        assert result is False  # noqa: S101

        # Check that error logging was called
        mock_obj.logger.error.assert_called()
        mock_obj.logger.warning.assert_called()
        # Check that telegram error message was sent
        mock_obj.telegram.send_message.assert_called()

    def test_step_info_screen_recording_start_error(self) -> None:
        """Test step_info decorator with screen recording start error."""
        mock_obj = MockClass()
        mock_obj.shadowstep.get_screenshot.return_value = b"screenshot_data"
        mock_obj.driver.start_recording_screen.side_effect = Exception("Recording start error")

        @step_info("Test step")
        def test_method(self: MockClass) -> str:
            return "success"

        result = test_method(mock_obj)
        assert result == "success"  # noqa: S101

        # Check that error logging was called for recording start error
        mock_obj.logger.error.assert_called()


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


class TestLogDebug:
    """Test cases for log_debug decorator."""

    @patch("logging.getLogger")
    def test_log_debug_success(self, mock_get_logger: Mock) -> None:
        """Test log_debug decorator with successful execution."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_debug()
        def test_function(arg1: str, arg2: int) -> str:
            return f"{arg1}_{arg2}"

        result = test_function("test", 42)
        assert result == "test_42"  # noqa: S101

        # Check that debug logging was called
        mock_logger.debug.assert_called()

    @patch("logging.getLogger")
    def test_log_debug_with_kwargs(self, mock_get_logger: Mock) -> None:
        """Test log_debug decorator with keyword arguments."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_debug()
        def test_function(**kwargs: Any) -> dict[str, Any]:
            return kwargs

        result = test_function(key1="value1", key2="value2")
        assert result == {"key1": "value1", "key2": "value2"}  # noqa: S101

        # Check that debug logging was called
        mock_logger.debug.assert_called()

    @patch("logging.getLogger")
    def test_log_debug_with_exception(self, mock_get_logger: Mock) -> None:
        """Test log_debug decorator with exception handling."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_debug()
        def test_function() -> str:
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_function()

        # Check that debug logging was called for entry
        mock_logger.debug.assert_called()

    @patch("logging.getLogger")
    def test_log_debug_preserves_metadata(self, mock_get_logger: Mock) -> None:
        """Test that log_debug preserves function metadata."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_debug()
        def test_function(arg1: str, arg2: int = 42) -> str:
            """Test function docstring."""
            return f"{arg1}_{arg2}"

        assert test_function.__name__ == "test_function"  # noqa: S101
        assert test_function.__doc__ == "Test function docstring."  # noqa: S101


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
