# ruff: noqa
# pyright: ignore
from typing import Any
from unittest.mock import Mock, patch

from selenium.common import TimeoutException, WebDriverException, InvalidSessionIdException, NoSuchDriverException, \
    StaleElementReferenceException

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
