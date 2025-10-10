# ruff: noqa
# pyright: ignore
"""Unit tests for shadowstep/element/actions.py module."""
from typing import Any
from unittest.mock import Mock, patch, MagicMock
import pytest
import time

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.element.actions import ElementActions
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep


class TestElementActions:
    """Test suite for ElementActions class."""

    def _create_test_element(self, mock_driver: Mock, timeout: float = 1.0) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        el.timeout = timeout
        return app, el

    # Tests for send_keys method
    @pytest.mark.unit
    def test_send_keys_success(self):
        """Test successful send_keys operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.send_keys = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.actions.send_keys("test", "text")
        
        mock_native_element.send_keys.assert_called_once_with("testtext")
        assert result is el

    @pytest.mark.unit
    def test_send_keys_with_single_value(self):
        """Test send_keys with single string value."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.send_keys = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.actions.send_keys("single")
        
        mock_native_element.send_keys.assert_called_once_with("single")
        assert result is el

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_send_keys_handles_no_such_driver_exception(self, mock_handle_error):
        """Test send_keys handles NoSuchDriverException."""
        mock_driver = Mock()
        mock_native_element = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=NoSuchDriverException("No driver")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.send_keys("test")
        
        assert "Failed to send_keys(test)" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_send_keys_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test send_keys handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=InvalidSessionIdException("Invalid session")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.send_keys("test")
        
        assert "Failed to send_keys(test)" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_send_keys_handles_attribute_error(self, mock_handle_error):
        """Test send_keys handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=AttributeError("Attribute error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.send_keys("test")
        
        assert "Failed to send_keys(test)" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_send_keys_handles_stale_element_reference_exception(self):
        """Test send_keys handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.send_keys = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        # First call raises StaleElementReferenceException
        # Second call is in except block (re-acquire element)
        # Third call is after continue in loop
        get_native_calls = [
            StaleElementReferenceException("Stale element"),
            mock_native_element,
            mock_native_element
        ]
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=get_native_calls):
                result = el.actions.send_keys("test")
        
        assert result is el
        mock_native_element.send_keys.assert_called_once_with("test")

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_send_keys_handles_webdriver_exception_instrumentation_not_running(self, mock_handle_error):
        """Test send_keys handles WebDriverException with 'instrumentation process is not running'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Instrumentation process is not running")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.send_keys.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.send_keys("test")
        
        assert "Failed to send_keys(test)" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_send_keys_handles_webdriver_exception_socket_hang_up(self, mock_handle_error):
        """Test send_keys handles WebDriverException with 'socket hang up'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Socket hang up error occurred")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.send_keys.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.send_keys("test")
        
        assert "Failed to send_keys(test)" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_send_keys_handles_webdriver_exception_other_error(self):
        """Test send_keys raises ShadowstepElementException for other WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Some other error")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.send_keys.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.send_keys("test")
        
        assert "Failed to send_keys(test)" in str(exc_info.value)

    @pytest.mark.unit
    @patch('time.time')
    def test_send_keys_timeout_exception(self, mock_time):
        """Test send_keys raises ShadowstepElementException on timeout."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        # Mock time.time() to simulate timeout
        mock_time.side_effect = [0, 0.2]  # First call: 0, second call: 0.2 (exceeds 0.1 timeout)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.send_keys.side_effect = WebDriverException("Test error")
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.send_keys("test")
        
        assert "Failed to send_keys(test)" in str(exc_info.value)

    # Tests for clear method
    @pytest.mark.unit
    def test_clear_success(self):
        """Test successful clear operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.clear = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.actions.clear()
        
        mock_native_element.clear.assert_called_once()
        assert result is el

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_clear_handles_no_such_driver_exception(self, mock_handle_error):
        """Test clear handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=NoSuchDriverException("No driver")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.clear()
        
        assert "Failed to clear element" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_clear_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test clear handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=InvalidSessionIdException("Invalid session")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.clear()
        
        assert "Failed to clear element" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_clear_handles_attribute_error(self, mock_handle_error):
        """Test clear handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=AttributeError("Attribute error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.clear()
        
        assert "Failed to clear element" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_clear_handles_stale_element_reference_exception(self):
        """Test clear handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.clear = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        # First call raises StaleElementReferenceException
        # Second call is in except block (re-acquire element)
        # Third call is after continue in loop
        get_native_calls = [
            StaleElementReferenceException("Stale element"),
            mock_native_element,
            mock_native_element
        ]
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=get_native_calls):
                result = el.actions.clear()
        
        assert result is el
        mock_native_element.clear.assert_called_once()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_clear_handles_webdriver_exception_instrumentation_not_running(self, mock_handle_error):
        """Test clear handles WebDriverException with 'instrumentation process is not running'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Instrumentation process is not running")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.clear.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.clear()
        
        assert "Failed to clear element" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_clear_handles_webdriver_exception_socket_hang_up(self, mock_handle_error):
        """Test clear handles WebDriverException with 'socket hang up'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Socket hang up error occurred")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.clear.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.clear()
        
        assert "Failed to clear element" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_clear_handles_webdriver_exception_other_error(self):
        """Test clear raises ShadowstepElementException for other WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Some other error")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.clear.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.clear()
        
        assert "Failed to clear element" in str(exc_info.value)

    @pytest.mark.unit
    @patch('time.time')
    def test_clear_timeout_exception(self, mock_time):
        """Test clear raises ShadowstepElementException on timeout."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        # Mock time.time() to simulate timeout
        mock_time.side_effect = [0, 0.2]  # First call: 0, second call: 0.2 (exceeds 0.1 timeout)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.clear.side_effect = WebDriverException("Test error")
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.clear()
        
        assert "Failed to clear element" in str(exc_info.value)

    # Tests for set_value method
    @pytest.mark.unit
    def test_set_value_success(self):
        """Test successful set_value operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.set_value = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.actions.set_value("test_value")
        
        mock_native_element.set_value.assert_called_once_with("test_value")
        assert result is el

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_set_value_handles_no_such_driver_exception(self, mock_handle_error):
        """Test set_value handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=NoSuchDriverException("No driver")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.set_value("test")
        
        assert "Failed to set_value(test)" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_set_value_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test set_value handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=InvalidSessionIdException("Invalid session")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.set_value("test")
        
        assert "Failed to set_value(test)" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_set_value_handles_attribute_error(self, mock_handle_error):
        """Test set_value handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=AttributeError("Attribute error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.set_value("test")
        
        assert "Failed to set_value(test)" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_set_value_handles_stale_element_reference_exception(self):
        """Test set_value handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.set_value = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        # First call raises StaleElementReferenceException
        # Second call is in except block (re-acquire element)
        # Third call is after continue in loop
        get_native_calls = [
            StaleElementReferenceException("Stale element"),
            mock_native_element,
            mock_native_element
        ]
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=get_native_calls):
                result = el.actions.set_value("test")
        
        assert result is el
        mock_native_element.set_value.assert_called_once_with("test")

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_set_value_handles_webdriver_exception_instrumentation_not_running(self, mock_handle_error):
        """Test set_value handles WebDriverException with 'instrumentation process is not running'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Instrumentation process is not running")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.set_value.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.set_value("test")
        
        assert "Failed to set_value(test)" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_set_value_handles_webdriver_exception_socket_hang_up(self, mock_handle_error):
        """Test set_value handles WebDriverException with 'socket hang up'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Socket hang up error occurred")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.set_value.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.set_value("test")
        
        assert "Failed to set_value(test)" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_set_value_handles_webdriver_exception_other_error(self):
        """Test set_value raises ShadowstepElementException for other WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Some other error")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.set_value.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.set_value("test")
        
        assert "Failed to set_value(test)" in str(exc_info.value)

    @pytest.mark.unit
    @patch('time.time')
    def test_set_value_timeout_exception(self, mock_time):
        """Test set_value raises ShadowstepElementException on timeout."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        # Mock time.time() to simulate timeout
        # set_value has additional time.time() call for start_time
        mock_time.side_effect = [0, 0.2, 0.3]  # start_time, first while check, second iteration
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.set_value.side_effect = WebDriverException("Test error")
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.set_value("test")
        
        assert "Failed to set_value(test)" in str(exc_info.value)

    # Tests for submit method
    @pytest.mark.unit
    def test_submit_success(self):
        """Test successful submit operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.submit = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.actions.submit()
        
        mock_native_element.submit.assert_called_once()
        assert result is el

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_submit_handles_no_such_driver_exception(self, mock_handle_error):
        """Test submit handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=NoSuchDriverException("No driver")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.submit()
        
        assert "Failed to submit element" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_submit_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test submit handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=InvalidSessionIdException("Invalid session")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.submit()
        
        assert "Failed to submit element" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_submit_handles_attribute_error(self, mock_handle_error):
        """Test submit handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=AttributeError("Attribute error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.submit()
        
        assert "Failed to submit element" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_submit_handles_stale_element_reference_exception(self):
        """Test submit handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.submit = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        # First call raises StaleElementReferenceException
        # Second call is in except block (re-acquire element)
        # Third call is after continue in loop
        get_native_calls = [
            StaleElementReferenceException("Stale element"),
            mock_native_element,
            mock_native_element
        ]
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=get_native_calls):
                result = el.actions.submit()
        
        assert result is el
        mock_native_element.submit.assert_called_once()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_submit_handles_webdriver_exception_instrumentation_not_running(self, mock_handle_error):
        """Test submit handles WebDriverException with 'instrumentation process is not running'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Instrumentation process is not running")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.submit.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.submit()
        
        assert "Failed to submit element" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_submit_handles_webdriver_exception_socket_hang_up(self, mock_handle_error):
        """Test submit handles WebDriverException with 'socket hang up'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Socket hang up error occurred")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.submit.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.submit()
        
        assert "Failed to submit element" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_submit_handles_webdriver_exception_other_error(self):
        """Test submit raises ShadowstepElementException for other WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Some other error")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.submit.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.submit()
        
        assert "Failed to submit element" in str(exc_info.value)

    @pytest.mark.unit
    @patch('time.time')
    def test_submit_timeout_exception(self, mock_time):
        """Test submit raises ShadowstepElementException on timeout."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        # Mock time.time() to simulate timeout
        # submit has additional time.time() call for start_time
        mock_time.side_effect = [0, 0.2, 0.3]  # start_time, first while check, second iteration
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.submit.side_effect = WebDriverException("Test error")
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.actions.submit()
        
        assert "Failed to submit element" in str(exc_info.value)

    # Tests for ElementActions initialization
    @pytest.mark.unit
    def test_element_actions_initialization(self):
        """Test ElementActions initialization."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        actions = ElementActions(el)
        
        assert actions.element is el
        assert actions.shadowstep is el.shadowstep
        assert actions.converter is el.converter
        assert actions.utilities is el.utilities
        assert actions.logger is not None

