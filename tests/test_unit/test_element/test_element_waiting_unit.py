# ruff: noqa
# pyright: ignore
"""Unit tests for shadowstep/element/waiting.py module."""
from typing import Any
from unittest.mock import Mock, patch
import pytest

from selenium.common import TimeoutException, WebDriverException, InvalidSessionIdException, NoSuchDriverException, \
    StaleElementReferenceException

from shadowstep.element.waiting import ElementWaiting
from shadowstep.shadowstep import Shadowstep

class TestElementWaiting:

    def _create_test_element(self, mock_driver: Mock) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        return app, el

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element not found")
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait(timeout=1, return_bool=True)
        assert result is False

    @patch("shadowstep.element.waiting.WebDriverWait")
    @patch("shadowstep.element.base.WebDriverWait")
    def test_wait_handles_stale_element_reference(self, mock_base_webdriver_wait: Any, mock_webdriver_wait: Any):
        """Test that wait method handles StaleElementReferenceException properly."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to raise StaleElementReferenceException first, then succeed
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = [
            StaleElementReferenceException("Stale element"),
            Mock()  # Success on second call
        ]
        mock_webdriver_wait.return_value = mock_wait_instance
        
        # Mock the base WebDriverWait for get_native method
        mock_base_wait_instance = Mock()
        mock_base_wait_instance.until.return_value = Mock()
        mock_base_webdriver_wait.return_value = mock_base_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait(timeout=5, return_bool=True)
        assert result is True

    @patch("shadowstep.element.waiting.WebDriverWait")
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_wait_handles_no_such_driver_exception(self, mock_handle_driver_error: Any, mock_webdriver_wait: Any):
        """Test that wait method handles NoSuchDriverException properly."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to raise NoSuchDriverException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = NoSuchDriverException("No driver")
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        # Should not raise exception, should handle gracefully
        result = el.wait(timeout=1, return_bool=True)
        assert result is False
        # Verify that handle_driver_error was called
        mock_handle_driver_error.assert_called()

    @patch("shadowstep.element.waiting.WebDriverWait")
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_wait_handles_invalid_session_id_exception(self, mock_handle_driver_error: Any, mock_webdriver_wait: Any):
        """Test that wait method handles InvalidSessionIdException properly."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to raise InvalidSessionIdException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = InvalidSessionIdException("Invalid session")
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        # Should not raise exception, should handle gracefully
        result = el.wait(timeout=1, return_bool=True)
        assert result is False
        # Verify that handle_driver_error was called
        mock_handle_driver_error.assert_called()

    @patch("shadowstep.element.waiting.WebDriverWait")
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_wait_handles_webdriver_exception(self, mock_handle_driver_error: Any, mock_webdriver_wait: Any):
        """Test that wait method handles WebDriverException properly."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to raise WebDriverException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = WebDriverException("WebDriver error")
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        # Should not raise exception, should handle gracefully
        result = el.wait(timeout=1, return_bool=True)
        assert result is False
        # Verify that handle_driver_error was called
        mock_handle_driver_error.assert_called()

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_visible_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait_visible method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element not visible")
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait_visible(timeout=1, return_bool=True)
        assert result is False  # wait_visible returns False on timeout

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_clickable_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait_clickable method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element not clickable")
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait_clickable(timeout=1, return_bool=True)
        assert result is False  # wait_clickable returns False on timeout

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait_for_not method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element still present")
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait_for_not(timeout=1, return_bool=True)
        assert result is False  # wait_for_not returns False on timeout

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_visible_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait_for_not_visible method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element still visible")
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait_for_not_visible(timeout=1, return_bool=True)
        assert result is False  # wait_for_not_visible returns False on timeout

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_clickable_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait_for_not_clickable method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element still clickable")
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait_for_not_clickable(timeout=1, return_bool=True)
        assert result is False  # wait_for_not_clickable returns False on timeout

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_successful_scenario(self, mock_webdriver_wait: Any):
        """Test that wait method returns True when element is found."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to succeed
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()  # Success
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait(timeout=5, return_bool=True)
        assert result is True

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_visible_successful_scenario(self, mock_webdriver_wait: Any):
        """Test that wait_visible method returns True when element is visible."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to succeed
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()  # Success
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait_visible(timeout=5, return_bool=True)
        assert result is True

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_clickable_successful_scenario(self, mock_webdriver_wait: Any):
        """Test that wait_clickable method returns True when element is clickable."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to succeed
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()  # Success
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait_clickable(timeout=5, return_bool=True)
        assert result is True

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_successful_scenario(self, mock_webdriver_wait: Any):
        """Test that wait_for_not method returns True when element disappears."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to succeed
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()  # Success
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait_for_not(timeout=5, return_bool=True)
        assert result is True

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_visible_successful_scenario(self, mock_webdriver_wait: Any):
        """Test that wait_for_not_visible method returns True when element becomes invisible."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to succeed
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()  # Success
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait_for_not_visible(timeout=5, return_bool=True)
        assert result is True

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_clickable_successful_scenario(self, mock_webdriver_wait: Any):
        """Test that wait_for_not_clickable method returns True when element becomes not clickable."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to succeed
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()  # Success
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait_for_not_clickable(timeout=5, return_bool=True)
        assert result is True

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_returns_element_when_return_bool_false(self, mock_webdriver_wait: Any):
        """Test that wait method returns Element when return_bool=False."""
        # Mock driver
        mock_driver = Mock()
        
        # Mock WebDriverWait to succeed
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()  # Success
        mock_webdriver_wait.return_value = mock_wait_instance

        app, el = self._create_test_element(mock_driver)
        result = el.wait(timeout=5, return_bool=False)
        assert result is el  # Should return the element itself

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_handles_resolved_locator_none(self, mock_webdriver_wait: Any):
        """Test that wait method handles case when resolved_locator is None."""
        # Mock driver
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        # Mock converter to return None
        with patch.object(el.converter, 'to_xpath', return_value=None):
            result = el.wait(timeout=1, return_bool=True)
            assert result is False  # Should return False when locator is None

    # Tests for initialization
    @pytest.mark.unit
    def test_element_waiting_initialization(self):
        """Test ElementWaiting initialization."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        waiting = ElementWaiting(el)
        
        assert waiting.element is el
        assert waiting.shadowstep is el.shadowstep
        assert waiting.converter is el.converter
        assert waiting.utilities is el.utilities
        assert waiting.logger is not None

    # Additional tests for wait_visible
    @pytest.mark.unit
    def test_wait_visible_returns_element_when_return_bool_false(self):
        """Test wait_visible returns Element when return_bool=False."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.waiting, '_wait_for_visibility_with_locator', return_value=True):
            result = el.wait_visible(timeout=5, return_bool=False)
        
        assert result is el

    @pytest.mark.unit
    def test_wait_visible_handles_resolved_locator_none(self):
        """Test wait_visible handles resolved_locator None."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.converter, 'to_xpath', return_value=None):
            result = el.wait_visible(timeout=1, return_bool=True)
        
        assert result is True  # Returns True when locator is None

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_wait_visible_handles_exception(self, mock_handle_error):
        """Test wait_visible handles exception through error handler."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.waiting, '_wait_for_visibility_with_locator', 
                         side_effect=NoSuchDriverException("No driver")):
            result = el.wait_visible(timeout=1, return_bool=True)
        
        assert result is False
        mock_handle_error.assert_called()

    # Additional tests for wait_clickable
    @pytest.mark.unit
    def test_wait_clickable_returns_element_when_return_bool_false(self):
        """Test wait_clickable returns Element when return_bool=False."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.waiting, '_wait_for_clickability_with_locator', return_value=True):
            result = el.wait_clickable(timeout=5, return_bool=False)
        
        assert result is el

    @pytest.mark.unit
    def test_wait_clickable_handles_resolved_locator_none(self):
        """Test wait_clickable handles resolved_locator None."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.converter, 'to_xpath', return_value=None):
            result = el.wait_clickable(timeout=1, return_bool=True)
        
        assert result is True  # Returns True when locator is None

    # Additional tests for wait_for_not
    @pytest.mark.unit
    def test_wait_for_not_returns_element_when_return_bool_false(self):
        """Test wait_for_not returns Element when return_bool=False."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.waiting, '_wait_for_not_present_with_locator', return_value=True):
            result = el.wait_for_not(timeout=5, return_bool=False)
        
        assert result is el

    @pytest.mark.unit
    def test_wait_for_not_handles_resolved_locator_none(self):
        """Test wait_for_not handles resolved_locator None."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.converter, 'to_xpath', return_value=None):
            result = el.wait_for_not(timeout=1, return_bool=True)
        
        assert result is True  # Returns True when locator is None

    # Additional tests for wait_for_not_visible
    @pytest.mark.unit
    def test_wait_for_not_visible_returns_element_when_return_bool_false(self):
        """Test wait_for_not_visible returns Element when return_bool=False."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.waiting, '_wait_for_not_visible_with_locator', return_value=True):
            result = el.wait_for_not_visible(timeout=5, return_bool=False)
        
        assert result is el

    @pytest.mark.unit
    def test_wait_for_not_visible_handles_resolved_locator_none(self):
        """Test wait_for_not_visible handles resolved_locator None."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.converter, 'to_xpath', return_value=None):
            result = el.wait_for_not_visible(timeout=1, return_bool=True)
        
        assert result is True  # Returns True when locator is None

    # Additional tests for wait_for_not_clickable
    @pytest.mark.unit
    def test_wait_for_not_clickable_returns_element_when_return_bool_false(self):
        """Test wait_for_not_clickable returns Element when return_bool=False."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.waiting, '_wait_for_not_clickable_with_locator', return_value=True):
            result = el.wait_for_not_clickable(timeout=5, return_bool=False)
        
        assert result is el

    @pytest.mark.unit
    def test_wait_for_not_clickable_handles_resolved_locator_none(self):
        """Test wait_for_not_clickable handles resolved_locator None."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.converter, 'to_xpath', return_value=None):
            result = el.wait_for_not_clickable(timeout=1, return_bool=True)
        
        assert result is True  # Returns True when locator is None

    # Tests for _wait_for_visibility_with_locator
    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_visibility_with_locator_returns_true(self, mock_wait):
        """Test _wait_for_visibility_with_locator returns True on success."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()
        mock_wait.return_value = mock_wait_instance
        
        result = el.waiting._wait_for_visibility_with_locator(("xpath", "//test"), 5, 0.5)
        
        assert result is True

    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_visibility_with_locator_returns_false_on_timeout(self, mock_wait):
        """Test _wait_for_visibility_with_locator returns False on TimeoutException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Timeout")
        mock_wait.return_value = mock_wait_instance
        
        result = el.waiting._wait_for_visibility_with_locator(("xpath", "//test"), 5, 0.5)
        
        assert result is False

    # Tests for _wait_for_clickability_with_locator
    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_clickability_with_locator_returns_true(self, mock_wait):
        """Test _wait_for_clickability_with_locator returns True on success."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()
        mock_wait.return_value = mock_wait_instance
        
        result = el.waiting._wait_for_clickability_with_locator(("xpath", "//test"), 5, 0.5)
        
        assert result is True

    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_clickability_with_locator_returns_false_on_timeout(self, mock_wait):
        """Test _wait_for_clickability_with_locator returns False on TimeoutException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Timeout")
        mock_wait.return_value = mock_wait_instance
        
        result = el.waiting._wait_for_clickability_with_locator(("xpath", "//test"), 5, 0.5)
        
        assert result is False

    # Tests for _wait_for_not_present_with_locator
    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_present_with_locator_returns_true(self, mock_wait):
        """Test _wait_for_not_present_with_locator returns True on success."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()
        mock_wait.return_value = mock_wait_instance
        
        result = el.waiting._wait_for_not_present_with_locator(("xpath", "//test"), 5, 0.5)
        
        assert result is True

    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_present_with_locator_returns_false_on_timeout(self, mock_wait):
        """Test _wait_for_not_present_with_locator returns False on TimeoutException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Timeout")
        mock_wait.return_value = mock_wait_instance
        
        result = el.waiting._wait_for_not_present_with_locator(("xpath", "//test"), 5, 0.5)
        
        assert result is False

    # Tests for _wait_for_not_visible_with_locator
    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_visible_with_locator_returns_true(self, mock_wait):
        """Test _wait_for_not_visible_with_locator returns True on success."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()
        mock_wait.return_value = mock_wait_instance
        
        result = el.waiting._wait_for_not_visible_with_locator(("xpath", "//test"), 5, 0.5)
        
        assert result is True

    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_visible_with_locator_returns_false_on_timeout(self, mock_wait):
        """Test _wait_for_not_visible_with_locator returns False on TimeoutException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Timeout")
        mock_wait.return_value = mock_wait_instance
        
        result = el.waiting._wait_for_not_visible_with_locator(("xpath", "//test"), 5, 0.5)
        
        assert result is False

    # Tests for _wait_for_not_clickable_with_locator
    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_clickable_with_locator_returns_true(self, mock_wait):
        """Test _wait_for_not_clickable_with_locator returns True on success."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()
        mock_wait.return_value = mock_wait_instance
        
        result = el.waiting._wait_for_not_clickable_with_locator(("xpath", "//test"), 5, 0.5)
        
        assert result is True

    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_clickable_with_locator_returns_false_on_timeout(self, mock_wait):
        """Test _wait_for_not_clickable_with_locator returns False on TimeoutException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Timeout")
        mock_wait.return_value = mock_wait_instance
        
        result = el.waiting._wait_for_not_clickable_with_locator(("xpath", "//test"), 5, 0.5)
        
        assert result is False

    # Tests for error handlers
    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_handle_wait_visibility_errors_with_no_such_driver(self, mock_handle_error):
        """Test _handle_wait_visibility_errors with NoSuchDriverException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        error = NoSuchDriverException("No driver")
        el.waiting._handle_wait_visibility_errors(error)
        
        mock_handle_error.assert_called_once_with(error)

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_handle_wait_visibility_errors_with_stale_element(self, mock_handle_error):
        """Test _handle_wait_visibility_errors with StaleElementReferenceException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        error = StaleElementReferenceException("Stale")
        
        with patch.object(el, 'get_native', return_value=Mock()):
            el.waiting._handle_wait_visibility_errors(error)
        
        # StaleElementReferenceException is subclass of WebDriverException,
        # so it will be caught by first isinstance check
        mock_handle_error.assert_called_once_with(error)

    @pytest.mark.unit
    def test_handle_wait_visibility_errors_with_other_exception(self):
        """Test _handle_wait_visibility_errors with other exception."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        error = ValueError("Some error")
        
        # Should log error but not raise
        el.waiting._handle_wait_visibility_errors(error)

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_handle_wait_clickability_errors_with_webdriver_exception(self, mock_handle_error):
        """Test _handle_wait_clickability_errors with WebDriverException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        error = WebDriverException("Error")
        el.waiting._handle_wait_clickability_errors(error)
        
        mock_handle_error.assert_called_once_with(error)

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_handle_wait_for_not_errors_with_invalid_session(self, mock_handle_error):
        """Test _handle_wait_for_not_errors with InvalidSessionIdException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        error = InvalidSessionIdException("Invalid")
        el.waiting._handle_wait_for_not_errors(error)
        
        mock_handle_error.assert_called_once_with(error)

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_handle_wait_for_not_visible_errors_with_driver_error(self, mock_handle_error):
        """Test _handle_wait_for_not_visible_errors with driver error."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        error = NoSuchDriverException("No driver")
        el.waiting._handle_wait_for_not_visible_errors(error)
        
        mock_handle_error.assert_called_once_with(error)

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_handle_wait_for_not_clickable_errors_with_webdriver_error(self, mock_handle_error):
        """Test _handle_wait_for_not_clickable_errors with WebDriverException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        error = WebDriverException("Error")
        el.waiting._handle_wait_for_not_clickable_errors(error)
        
        mock_handle_error.assert_called_once_with(error)

    # Tests for timeout parameter handling
    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_uses_minimum_timeout_of_1(self, mock_wait):
        """Test wait uses minimum timeout of 1 second."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = Mock()
        mock_wait.return_value = mock_wait_instance
        
        # Try to set timeout=0, should use 1
        result = el.wait(timeout=0, return_bool=True)
        
        # Check that WebDriverWait was called with at least 1
        assert mock_wait.call_args[0][1] >= 1

    @pytest.mark.unit
    def test_wait_visible_uses_minimum_timeout_of_1(self):
        """Test wait_visible uses minimum timeout of 1 second."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.waiting, '_wait_for_visibility_with_locator', return_value=True):
            # Try to set timeout=0, should use 1
            result = el.wait_visible(timeout=0, return_bool=True)
        
        assert result is True

    # Test for generic Exception handling in wait
    @pytest.mark.unit
    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_handles_generic_exception(self, mock_wait):
        """Test wait handles generic Exception."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        # First call raises generic exception, second succeeds
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = [
            ValueError("Some error"),
            Mock()
        ]
        mock_wait.return_value = mock_wait_instance
        
        result = el.wait(timeout=5, return_bool=True)
        
        assert result is True

    # Test stale element handling in wait_visible
    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_wait_visible_handles_stale_element_and_continues(self, mock_handle_error):
        """Test wait_visible handles StaleElementReferenceException and continues."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        call_count = [0]
        def mock_wait_visibility(locator, timeout, poll):
            call_count[0] += 1
            if call_count[0] == 1:
                raise StaleElementReferenceException("Stale")
            return True
        
        with patch.object(el.waiting, '_wait_for_visibility_with_locator', side_effect=mock_wait_visibility):
            with patch.object(el, 'get_native', return_value=Mock()):
                result = el.wait_visible(timeout=5, return_bool=True)
        
        assert result is True
        assert call_count[0] == 2  # Should retry after stale element

    # Test return_bool False returns element on timeout
    @pytest.mark.unit
    def test_wait_visible_returns_element_on_timeout_when_return_bool_false(self):
        """Test wait_visible returns Element on timeout when return_bool=False."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.waiting, '_wait_for_visibility_with_locator', return_value=False):
            result = el.wait_visible(timeout=1, return_bool=False)
        
        assert result is el
