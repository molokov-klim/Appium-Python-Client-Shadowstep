# ruff: noqa
# pyright: ignore
import time
from typing import Any
from unittest.mock import Mock, patch

import pytest

from shadowstep.decorators.decorators import (
    DEFAULT_EXCEPTIONS,
    current_page,
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


class TestRetry:
    """Test cases for retry decorator."""

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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
    @pytest.mark.unit
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
    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_step_info_success(self) -> None:
        """Test step_info decorator with successful execution."""
        mock_obj = MockClass()
        mock_shadowstep = Mock()
        mock_shadowstep.get_screenshot.return_value = b"screenshot_data"
        mock_shadowstep.driver = Mock()
        mock_shadowstep.driver.start_recording_screen.return_value = None
        mock_shadowstep.driver.stop_recording_screen.return_value = b"video_data"

        with patch('shadowstep.shadowstep.Shadowstep.get_instance', return_value=mock_shadowstep):
            @step_info("Test step")
            def test_method(self: MockClass) -> str:
                return "success"

            result = test_method(mock_obj)
            assert result == "success"  # noqa: S101

        # Check that logging was called
        mock_obj.logger.info.assert_called()
        mock_shadowstep.get_screenshot.assert_called()

    @pytest.mark.unit
    def test_step_info_with_exception(self) -> None:
        """Test step_info decorator with exception."""
        mock_obj = MockClass()
        mock_shadowstep = Mock()
        mock_shadowstep.get_screenshot.return_value = b"screenshot_data"
        mock_shadowstep.driver = Mock()
        mock_shadowstep.driver.start_recording_screen.return_value = None
        mock_shadowstep.driver.stop_recording_screen.return_value = b"video_data"

        with patch('shadowstep.shadowstep.Shadowstep.get_instance', return_value=mock_shadowstep):
            @step_info("Test step")
            def test_method(self: MockClass) -> str:
                raise ValueError("Test error")

            result = test_method(mock_obj)
            assert result is False  # noqa: S101

        # Check that error logging was called
        mock_obj.logger.error.assert_called()

    @pytest.mark.unit
    def test_step_info_screen_recording(self) -> None:
        """Test step_info decorator with screen recording."""
        mock_obj = MockClass()
        mock_shadowstep = Mock()
        mock_shadowstep.get_screenshot.return_value = b"screenshot_data"
        mock_shadowstep.driver = Mock()
        mock_shadowstep.driver.start_recording_screen.return_value = None
        mock_shadowstep.driver.stop_recording_screen.return_value = b"video_data"

        with patch('shadowstep.shadowstep.Shadowstep.get_instance', return_value=mock_shadowstep):
            @step_info("Test step")
            def test_method(self: MockClass) -> str:
                return "success"

            result = test_method(mock_obj)
            assert result == "success"  # noqa: S101

        # Check that screen recording was started
        mock_shadowstep.driver.start_recording_screen.assert_called_once()
        # Note: stop_recording_screen is only called on exception, not on success

    @pytest.mark.unit
    def test_step_info_video_recording_error(self) -> None:
        """Test step_info decorator with video recording error."""
        mock_obj = MockClass()
        mock_shadowstep = Mock()
        mock_shadowstep.get_screenshot.return_value = b"screenshot_data"
        mock_shadowstep.driver = Mock()
        mock_shadowstep.driver.start_recording_screen.return_value = None
        mock_shadowstep.driver.stop_recording_screen.side_effect = Exception("Video recording error")

        with patch('shadowstep.shadowstep.Shadowstep.get_instance', return_value=mock_shadowstep):
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

    @pytest.mark.unit
    def test_step_info_screen_recording_start_error(self) -> None:
        """Test step_info decorator with screen recording start error."""
        mock_obj = MockClass()
        mock_shadowstep = Mock()
        mock_shadowstep.get_screenshot.return_value = b"screenshot_data"
        mock_shadowstep.driver = Mock()
        mock_shadowstep.driver.start_recording_screen.side_effect = Exception("Recording start error")
        mock_shadowstep.driver.stop_recording_screen.return_value = b"video_data"

        with patch('shadowstep.shadowstep.Shadowstep.get_instance', return_value=mock_shadowstep):
            @step_info("Test step")
            def test_method(self: MockClass) -> str:
                return "success"

            result = test_method(mock_obj)
            assert result == "success"  # noqa: S101

        # Check that error logging was called for recording start error
        mock_obj.logger.error.assert_called()


class TestCurrentPage:
    """Test cases for current_page decorator."""

    @pytest.mark.unit
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

    @pytest.mark.unit
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
    @pytest.mark.unit
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
    @pytest.mark.unit
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
    @pytest.mark.unit
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
    @pytest.mark.unit
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
    @pytest.mark.unit
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
    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_default_exceptions_are_exception_types(self) -> None:
        """Test that all items in DEFAULT_EXCEPTIONS are exception types."""
        for exc_type in DEFAULT_EXCEPTIONS:
            assert issubclass(exc_type, Exception)  # noqa: S101


class TestDecoratorIntegration:
    """Integration tests for decorators."""

    @pytest.mark.unit
    def test_decorator_type_hints_preserved(self) -> None:
        """Test that decorators preserve type hints."""

        @log_info()
        def test_function(arg1: str, arg2: int) -> str:
            return f"{arg1}_{arg2}"

        # The function should still be callable with correct types
        result = test_function("test", 42)
        assert result == "test_42"  # noqa: S101
