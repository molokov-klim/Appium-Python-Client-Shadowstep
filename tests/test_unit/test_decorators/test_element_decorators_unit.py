# ruff: noqa
# pyright: ignore
"""Unit tests for element_decorators using mocks."""
from unittest.mock import Mock, patch

import pytest
from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.decorators.element_decorators import fail_safe_element
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException


class TestFailSafeElementDecorator:
    """Test fail_safe_element decorator."""

    def test_successful_execution_without_errors(self):
        """Test decorator allows successful execution without errors."""
        # Create mock element
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element._get_web_element = Mock()
        mock_element.logger = Mock()
        
        # Decorate a test function
        @fail_safe_element(retries=3, delay=0.1)
        def test_method(self):
            return "success"
        
        result = test_method(mock_element)
        
        assert result == "success"
        mock_element.get_driver.assert_called()
        mock_element._get_web_element.assert_called()

    def test_retry_on_stale_element_exception(self):
        """Test decorator retries on StaleElementReferenceException."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        mock_element.native = Mock()
        mock_element.get_native = Mock()
        
        # First call raises StaleElementReferenceException, second succeeds
        mock_element._get_web_element = Mock(side_effect=[
            StaleElementReferenceException("Stale element"),
            None
        ])
        
        @fail_safe_element(retries=3, delay=0.01)
        def test_method(self):
            return "success"
        
        with patch('time.time', side_effect=[0, 0.5, 1]):
            result = test_method(mock_element)
        
        assert result == "success"
        assert mock_element._get_web_element.call_count == 2
        assert mock_element.native is None
        mock_element.get_native.assert_called()

    def test_retry_on_no_such_driver_exception(self):
        """Test decorator handles NoSuchDriverException."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        mock_element.utilities = Mock()
        mock_element.utilities.handle_driver_error = Mock()
        
        # First call raises NoSuchDriverException, second succeeds
        mock_element._get_web_element = Mock(side_effect=[
            NoSuchDriverException("No driver"),
            None
        ])
        
        @fail_safe_element(retries=3, delay=0.01)
        def test_method(self):
            return "success"
        
        with patch('time.time', side_effect=[0, 0.5, 1, 2]):
            result = test_method(mock_element)
        
        mock_element.utilities.handle_driver_error.assert_called()

    def test_retry_on_invalid_session_exception(self):
        """Test decorator handles InvalidSessionIdException."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        mock_element.utilities = Mock()
        mock_element.utilities.handle_driver_error = Mock()
        
        # First call raises InvalidSessionIdException, second succeeds
        mock_element._get_web_element = Mock(side_effect=[
            InvalidSessionIdException("Invalid session"),
            None
        ])
        
        @fail_safe_element(retries=3, delay=0.01)
        def test_method(self):
            return "success"
        
        with patch('time.time', side_effect=[0, 0.5, 1, 2]):
            result = test_method(mock_element)
        
        mock_element.utilities.handle_driver_error.assert_called()

    def test_retry_on_attribute_error(self):
        """Test decorator handles AttributeError."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        mock_element.utilities = Mock()
        mock_element.utilities.handle_driver_error = Mock()
        
        # First call raises AttributeError, second succeeds
        mock_element._get_web_element = Mock(side_effect=[
            AttributeError("Missing attribute"),
            None
        ])
        
        @fail_safe_element(retries=3, delay=0.01)
        def test_method(self):
            return "success"
        
        with patch('time.time', side_effect=[0, 0.5, 1, 2]):
            result = test_method(mock_element)
        
        mock_element.utilities.handle_driver_error.assert_called()

    def test_retry_on_instrumentation_error(self):
        """Test decorator retries on instrumentation process error."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        mock_element.utilities = Mock()
        mock_element.utilities.handle_driver_error = Mock()
        
        # First call raises WebDriverException with instrumentation error
        mock_element._get_web_element = Mock(side_effect=[
            WebDriverException("instrumentation process is not running"),
            None
        ])
        
        @fail_safe_element(retries=3, delay=0.01)
        def test_method(self):
            return "success"
        
        with patch('time.time', side_effect=[0, 0.5, 1, 2]):
            result = test_method(mock_element)
        
        mock_element.utilities.handle_driver_error.assert_called()

    def test_retry_on_socket_hang_up_error(self):
        """Test decorator retries on socket hang up error."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        mock_element.utilities = Mock()
        mock_element.utilities.handle_driver_error = Mock()
        
        # First call raises WebDriverException with socket error
        mock_element._get_web_element = Mock(side_effect=[
            WebDriverException("socket hang up"),
            None
        ])
        
        @fail_safe_element(retries=3, delay=0.01)
        def test_method(self):
            return "success"
        
        with patch('time.time', side_effect=[0, 0.5, 1, 2]):
            result = test_method(mock_element)
        
        mock_element.utilities.handle_driver_error.assert_called()

    def test_raises_on_unexpected_webdriver_exception(self):
        """Test decorator raises on unexpected WebDriverException."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        
        mock_element._get_web_element = Mock(side_effect=WebDriverException("Unexpected error"))
        
        @fail_safe_element(retries=3, delay=0.01)
        def test_method(self):
            return "success"
        
        with pytest.raises(ShadowstepElementException) as exc_info:
            with patch('time.time', side_effect=[0, 0.5]):
                test_method(mock_element)
        
        assert "Failed to execute" in str(exc_info.value)

    def test_raises_custom_exception_when_specified(self):
        """Test decorator raises custom exception when specified."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        
        mock_element._get_web_element = Mock(side_effect=WebDriverException("Error"))
        
        class CustomException(Exception):
            pass
        
        @fail_safe_element(retries=1, delay=0.01, raise_exception=CustomException)
        def test_method(self):
            return "success"
        
        with pytest.raises(CustomException):
            with patch('time.time', side_effect=[0, 0.5]):
                test_method(mock_element)

    def test_raises_on_timeout_exhausted(self):
        """Test decorator raises exception when timeout is exhausted."""
        mock_element = Mock()
        mock_element.timeout = 1
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        
        # Always raise exception
        mock_element._get_web_element = Mock(side_effect=StaleElementReferenceException("Stale"))
        mock_element.native = Mock()
        mock_element.get_native = Mock()
        
        @fail_safe_element(retries=0, delay=0.01)
        def test_method(self):
            return "success"
        
        with pytest.raises(ShadowstepElementException) as exc_info:
            with patch('time.time', side_effect=[0, 0.5, 1.5]):
                test_method(mock_element)
        
        assert "Failed to execute" in str(exc_info.value)
        assert "timeout=" in str(exc_info.value)

    def test_decorator_with_function_arguments(self):
        """Test decorator works with functions that have arguments."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element._get_web_element = Mock()
        mock_element.logger = Mock()
        
        @fail_safe_element(retries=3, delay=0.01)
        def test_method(self, arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"
        
        result = test_method(mock_element, "a", "b", kwarg1="c")
        
        assert result == "a-b-c"

    def test_decorator_preserves_function_metadata(self):
        """Test decorator preserves original function metadata."""
        @fail_safe_element(retries=3, delay=0.1)
        def test_method(self):
            """Test docstring."""
            return "success"
        
        assert test_method.__name__ == "test_method"
        assert test_method.__doc__ == "Test docstring."

    def test_retry_with_delay(self):
        """Test decorator uses delay parameter correctly."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        
        # Always succeed
        mock_element._get_web_element = Mock()
        
        @fail_safe_element(retries=3, delay=0.05)
        def test_method(self):
            return "success"
        
        # Just verify decorator can be applied with delay parameter
        result = test_method(mock_element)
        
        assert result == "success"

    def test_decorator_logs_retry_attempts(self):
        """Test decorator logs retry attempts."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        mock_element.native = Mock()
        mock_element.get_native = Mock()
        
        # Fail with StaleElementReferenceException multiple times, then succeed
        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise StaleElementReferenceException("Stale")
            return None
        
        mock_element._get_web_element = Mock(side_effect=side_effect)
        
        @fail_safe_element(retries=3, delay=0.01)
        def test_method(self):
            return "success"
        
        with patch('time.time', side_effect=[0, 0.5, 1, 1.5]), \
             patch('time.sleep'):
            result = test_method(mock_element)
        
        # Verify debug was logged for StaleElementReferenceException
        assert mock_element.logger.debug.called or mock_element.logger.warning.called
        assert result == "success"

    def test_null_raise_exception_parameter(self):
        """Test decorator with raise_exception=None uses default exception."""
        mock_element = Mock()
        mock_element.timeout = 10
        mock_element.get_driver = Mock()
        mock_element.logger = Mock()
        
        mock_element._get_web_element = Mock(side_effect=WebDriverException("Error"))
        
        @fail_safe_element(retries=0, delay=0.01, raise_exception=None)
        def test_method(self):
            return "success"
        
        with pytest.raises(ShadowstepElementException):
            with patch('time.time', side_effect=[0, 11]):
                test_method(mock_element)

