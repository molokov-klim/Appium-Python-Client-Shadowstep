from typing import Any
from unittest.mock import Mock, patch

from selenium.common import TimeoutException, WebDriverException, InvalidSessionIdException, NoSuchDriverException, \
    StaleElementReferenceException

from shadowstep.shadowstep import Shadowstep

app = Shadowstep()

class TestElementWaiting:

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        app.driver = mock_driver
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element not found")
        mock_webdriver_wait.return_value = mock_wait_instance

        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        result = el.wait(timeout=1, return_bool=True)
        assert result is False

    @patch("shadowstep.element.waiting.WebDriverWait")
    @patch("shadowstep.element.base.WebDriverWait")
    def test_wait_handles_stale_element_reference(self, mock_base_webdriver_wait: Any, mock_webdriver_wait: Any):
        """Test that wait method handles StaleElementReferenceException properly."""
        # Mock driver
        mock_driver = Mock()
        app.driver = mock_driver
        
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

        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        result = el.wait(timeout=5, return_bool=True)
        assert result is True

    @patch("shadowstep.element.waiting.WebDriverWait")
    @patch("requests.delete")
    def test_wait_handles_no_such_driver_exception(self, mock_requests_delete: Any, mock_webdriver_wait: Any):
        """Test that wait method handles NoSuchDriverException properly."""
        # Mock driver
        mock_driver = Mock()
        app.driver = mock_driver
        
        # Mock WebDriverWait to raise NoSuchDriverException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = NoSuchDriverException("No driver")
        mock_webdriver_wait.return_value = mock_wait_instance

        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        # Should not raise exception, should handle gracefully
        result = el.wait(timeout=1, return_bool=True)
        assert result is False

    @patch("shadowstep.element.waiting.WebDriverWait")
    @patch("requests.delete")
    def test_wait_handles_invalid_session_id_exception(self, mock_requests_delete: Any, mock_webdriver_wait: Any):
        """Test that wait method handles InvalidSessionIdException properly."""
        # Mock driver
        mock_driver = Mock()
        app.driver = mock_driver
        
        # Mock WebDriverWait to raise InvalidSessionIdException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = InvalidSessionIdException("Invalid session")
        mock_webdriver_wait.return_value = mock_wait_instance

        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        # Should not raise exception, should handle gracefully
        result = el.wait(timeout=1, return_bool=True)
        assert result is False

    @patch("shadowstep.element.waiting.WebDriverWait")
    @patch("requests.delete")
    def test_wait_handles_webdriver_exception(self, mock_requests_delete: Any, mock_webdriver_wait: Any):
        """Test that wait method handles WebDriverException properly."""
        # Mock driver
        mock_driver = Mock()
        app.driver = mock_driver
        
        # Mock WebDriverWait to raise WebDriverException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = WebDriverException("WebDriver error")
        mock_webdriver_wait.return_value = mock_wait_instance

        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        # Should not raise exception, should handle gracefully
        result = el.wait(timeout=1, return_bool=True)
        assert result is False

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_visible_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait_visible method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        app.driver = mock_driver
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element not visible")
        mock_webdriver_wait.return_value = mock_wait_instance

        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        result = el.wait_visible(timeout=1, return_bool=True)
        assert result is True  # wait_visible returns True for non-existent elements

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_clickable_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait_clickable method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        app.driver = mock_driver
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element not clickable")
        mock_webdriver_wait.return_value = mock_wait_instance

        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        result = el.wait_clickable(timeout=1, return_bool=True)
        assert result is True  # wait_clickable returns True for non-existent elements

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait_for_not method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        app.driver = mock_driver
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element still present")
        mock_webdriver_wait.return_value = mock_wait_instance

        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        result = el.wait_for_not(timeout=1, return_bool=True)
        assert result is False  # wait_for_not returns False on timeout

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_visible_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait_for_not_visible method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        app.driver = mock_driver
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element still visible")
        mock_webdriver_wait.return_value = mock_wait_instance

        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        result = el.wait_for_not_visible(timeout=1, return_bool=True)
        assert result is True  # wait_for_not_visible returns True for non-existent elements

    @patch("shadowstep.element.waiting.WebDriverWait")
    def test_wait_for_not_clickable_handles_timeout_exception(self, mock_webdriver_wait: Any):
        """Test that wait_for_not_clickable method handles TimeoutException properly."""
        # Mock driver
        mock_driver = Mock()
        app.driver = mock_driver
        
        # Mock WebDriverWait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Element still clickable")
        mock_webdriver_wait.return_value = mock_wait_instance

        el = app.get_element({"resource-id": "com.android.quicksearchbox:id/search_widget_text"})
        result = el.wait_for_not_clickable(timeout=1, return_bool=True)
        assert result is True  # wait_for_not_clickable returns True for non-existent elements
