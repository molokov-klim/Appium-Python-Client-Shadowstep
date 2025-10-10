# ruff: noqa
# pyright: ignore
"""Unit tests for shadowstep/element/coordinates.py module."""
from typing import Any
from unittest.mock import Mock, patch
import pytest

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.element.coordinates import ElementCoordinates
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep


class TestElementCoordinates:
    """Test suite for ElementCoordinates class."""

    def _create_test_element(self, mock_driver: Mock, timeout: float = 1.0) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        el.timeout = timeout
        return app, el

    # Tests for __init__ method
    @pytest.mark.unit
    def test_element_coordinates_initialization(self):
        """Test ElementCoordinates initialization."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        coordinates = ElementCoordinates(el)
        
        assert coordinates.element is el
        assert coordinates.shadowstep is el.shadowstep
        assert coordinates.converter is el.converter
        assert coordinates.utilities is el.utilities
        assert coordinates.logger is not None

    # Tests for get_coordinates method
    @pytest.mark.unit
    def test_get_coordinates_success(self):
        """Test successful get_coordinates operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.get_attribute.return_value = "[100,200][300,400]"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.coordinates.get_coordinates()
        
        assert result == (100, 200, 300, 400)
        mock_native_element.get_attribute.assert_called_once_with("bounds")

    @pytest.mark.unit
    def test_get_coordinates_with_provided_element(self):
        """Test get_coordinates with provided element parameter."""
        mock_driver = Mock()
        mock_provided_element = Mock()
        mock_provided_element.get_attribute.return_value = "[50,60][150,160]"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            result = el.coordinates.get_coordinates(mock_provided_element)
        
        assert result == (50, 60, 150, 160)
        mock_provided_element.get_attribute.assert_called_once_with("bounds")

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_get_coordinates_handles_no_such_driver_exception(self, mock_handle_error):
        """Test get_coordinates handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=NoSuchDriverException("No driver")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_coordinates()
        
        assert "Failed to get_coordinates" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_get_coordinates_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test get_coordinates handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=InvalidSessionIdException("Invalid session")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_coordinates()
        
        assert "Failed to get_coordinates" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_get_coordinates_handles_attribute_error(self, mock_handle_error):
        """Test get_coordinates handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=AttributeError("Attribute error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_coordinates()
        
        assert "Failed to get_coordinates" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_get_coordinates_handles_stale_element_reference_exception(self):
        """Test get_coordinates handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.get_attribute.return_value = "[10,20][30,40]"
        
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
                result = el.coordinates.get_coordinates()
        
        assert result == (10, 20, 30, 40)

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_get_coordinates_handles_webdriver_exception_instrumentation_not_running(self, mock_handle_error):
        """Test get_coordinates handles WebDriverException with 'instrumentation process is not running'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Instrumentation process is not running")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.get_attribute.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_coordinates()
        
        assert "Failed to get_coordinates" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_get_coordinates_handles_webdriver_exception_socket_hang_up(self, mock_handle_error):
        """Test get_coordinates handles WebDriverException with 'socket hang up'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Socket hang up error occurred")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.get_attribute.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_coordinates()
        
        assert "Failed to get_coordinates" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_get_coordinates_handles_webdriver_exception_other_error(self):
        """Test get_coordinates raises WebDriverException for other errors."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Some other error")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.get_attribute.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(WebDriverException):
                    el.coordinates.get_coordinates()

    @pytest.mark.unit
    @patch('time.time')
    def test_get_coordinates_timeout_exception(self, mock_time):
        """Test get_coordinates raises ShadowstepElementException on timeout."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        # Mock time.time() to simulate timeout
        mock_time.side_effect = [0, 0.2]
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.get_attribute.return_value = None  # Returns None to trigger continue
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_coordinates()
        
        assert "Failed to get_coordinates" in str(exc_info.value)

    # Tests for get_center method
    @pytest.mark.unit
    def test_get_center_success(self):
        """Test successful get_center operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.get_attribute.return_value = "[100,200][300,400]"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.coordinates.get_center()
        
        # Center: x = (100 + 300) / 2 = 200, y = (200 + 400) / 2 = 300
        assert result == (200, 300)

    @pytest.mark.unit
    def test_get_center_with_provided_element(self):
        """Test get_center with provided element parameter."""
        mock_driver = Mock()
        mock_provided_element = Mock()
        mock_provided_element.get_attribute.return_value = "[0,0][100,100]"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            result = el.coordinates.get_center(mock_provided_element)
        
        # Center: x = (0 + 100) / 2 = 50, y = (0 + 100) / 2 = 50
        assert result == (50, 50)

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_get_center_handles_no_such_driver_exception(self, mock_handle_error):
        """Test get_center handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=NoSuchDriverException("No driver")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_center()
        
        assert "Failed to get_center" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_get_center_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test get_center handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=InvalidSessionIdException("Invalid session")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_center()
        
        assert "Failed to get_center" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_get_center_handles_attribute_error(self, mock_handle_error):
        """Test get_center handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=AttributeError("Attribute error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_center()
        
        assert "Failed to get_center" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_get_center_handles_stale_element_reference_exception(self):
        """Test get_center handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.get_attribute.return_value = "[0,0][200,200]"
        
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
                result = el.coordinates.get_center()
        
        # Center: x = (0 + 200) / 2 = 100, y = (0 + 200) / 2 = 100
        assert result == (100, 100)

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_get_center_handles_webdriver_exception_instrumentation_not_running(self, mock_handle_error):
        """Test get_center handles WebDriverException with 'instrumentation process is not running'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Instrumentation process is not running")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.get_attribute.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_center()
        
        # get_center calls get_coordinates internally, so error message can be from get_coordinates
        assert "Failed to get_coordinates" in str(exc_info.value) or "Failed to get_center" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_get_center_handles_webdriver_exception_socket_hang_up(self, mock_handle_error):
        """Test get_center handles WebDriverException with 'socket hang up'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Socket hang up error occurred")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.get_attribute.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_center()
        
        # get_center calls get_coordinates internally, so error message can be from get_coordinates
        assert "Failed to get_coordinates" in str(exc_info.value) or "Failed to get_center" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_get_center_handles_webdriver_exception_other_error(self):
        """Test get_center raises WebDriverException for other errors."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Some other error")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.get_attribute.side_effect = error
                mock_get_native.return_value = mock_native
                
                with pytest.raises(WebDriverException):
                    el.coordinates.get_center()

    @pytest.mark.unit
    @patch('time.time')
    def test_get_center_timeout_exception(self, mock_time):
        """Test get_center raises ShadowstepElementException on timeout."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        # Mock time.time() to simulate timeout
        mock_time.side_effect = [0, 0.2]
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native') as mock_get_native:
                mock_native = Mock()
                mock_native.get_attribute.return_value = None  # Returns None to trigger continue
                mock_get_native.return_value = mock_native
                
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.get_center()
        
        assert "Failed to get_center" in str(exc_info.value)

    # Tests for location_in_view method
    @pytest.mark.unit
    def test_location_in_view_success(self):
        """Test successful location_in_view operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.location_in_view = {"x": 100, "y": 200}
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.coordinates.location_in_view()
        
        assert result == {"x": 100, "y": 200}

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_location_in_view_handles_no_such_driver_exception(self, mock_handle_error):
        """Test location_in_view handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=NoSuchDriverException("No driver")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.location_in_view()
        
        assert "Failed to get location_in_view" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_location_in_view_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test location_in_view handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=InvalidSessionIdException("Invalid session")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.location_in_view()
        
        assert "Failed to get location_in_view" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_location_in_view_handles_attribute_error(self, mock_handle_error):
        """Test location_in_view handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=AttributeError("Attribute error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.location_in_view()
        
        assert "Failed to get location_in_view" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_location_in_view_handles_stale_element_reference_exception(self):
        """Test location_in_view handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.location_in_view = {"x": 50, "y": 75}
        
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
                result = el.coordinates.location_in_view()
        
        assert result == {"x": 50, "y": 75}

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_location_in_view_handles_webdriver_exception_instrumentation_not_running(self, mock_handle_error):
        """Test location_in_view handles WebDriverException with 'instrumentation process is not running'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Instrumentation process is not running")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=error):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.location_in_view()
        
        assert "Failed to get location_in_view" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_location_in_view_handles_webdriver_exception_socket_hang_up(self, mock_handle_error):
        """Test location_in_view handles WebDriverException with 'socket hang up'."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Socket hang up error occurred")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=error):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.location_in_view()
        
        assert "Failed to get location_in_view" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_location_in_view_handles_webdriver_exception_other_error(self):
        """Test location_in_view raises WebDriverException for other errors."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Some other error")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=error):
                with pytest.raises(WebDriverException):
                    el.coordinates.location_in_view()

    @pytest.mark.unit
    @patch('time.time')
    def test_location_in_view_timeout_exception(self, mock_time):
        """Test location_in_view raises ShadowstepElementException on timeout."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        # Mock time.time() to simulate timeout
        mock_time.side_effect = [0, 0.2]
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=WebDriverException("Timeout")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.location_in_view()
        
        assert "Failed to get location_in_view" in str(exc_info.value)

    # Tests for location_once_scrolled_into_view method
    @pytest.mark.unit
    def test_location_once_scrolled_into_view_success(self):
        """Test successful location_once_scrolled_into_view operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.location_once_scrolled_into_view = {"x": 150, "y": 250}
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.coordinates.location_once_scrolled_into_view()
        
        assert result == {"x": 150, "y": 250}

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_location_once_scrolled_into_view_handles_no_such_driver_exception(self, mock_handle_error):
        """Test location_once_scrolled_into_view handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=NoSuchDriverException("No driver")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.location_once_scrolled_into_view()
        
        assert "Failed to get location_once_scrolled_into_view" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_location_once_scrolled_into_view_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test location_once_scrolled_into_view handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=InvalidSessionIdException("Invalid session")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.location_once_scrolled_into_view()
        
        assert "Failed to get location_once_scrolled_into_view" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_location_once_scrolled_into_view_handles_attribute_error(self, mock_handle_error):
        """Test location_once_scrolled_into_view handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=AttributeError("Attribute error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.location_once_scrolled_into_view()
        
        assert "Failed to get location_once_scrolled_into_view" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_location_once_scrolled_into_view_handles_webdriver_exception(self, mock_handle_error):
        """Test location_once_scrolled_into_view handles WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=WebDriverException("WebDriver error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.coordinates.location_once_scrolled_into_view()
        
        assert "Failed to get location_once_scrolled_into_view" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_location_once_scrolled_into_view_timeout_exception(self, mock_handle_error):
        """Test location_once_scrolled_into_view raises ShadowstepElementException on timeout."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        # Create a counter for time.time() that increases each call to simulate timeout
        time_counter = [0]
        def mock_time_func():
            result = time_counter[0]
            time_counter[0] += 0.1
            return result
        
        with patch('time.time', side_effect=mock_time_func):
            with patch.object(el, 'get_driver', return_value=mock_driver):
                with patch.object(el, 'get_native', side_effect=WebDriverException("Timeout")):
                    with pytest.raises(ShadowstepElementException) as exc_info:
                        el.coordinates.location_once_scrolled_into_view()
        
        assert "Failed to get location_once_scrolled_into_view" in str(exc_info.value)

