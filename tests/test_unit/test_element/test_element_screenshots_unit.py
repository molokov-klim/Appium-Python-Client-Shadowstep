# ruff: noqa
# pyright: ignore
"""Unit tests for shadowstep/element/screenshots.py module."""
from typing import Any
from unittest.mock import Mock, patch
import pytest

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.element.screenshots import ElementScreenshots
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep


class TestElementScreenshots:
    """Test suite for ElementScreenshots class."""

    def _create_test_element(self, mock_driver: Mock, timeout: float = 1.0) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        el.timeout = timeout
        return app, el

    # Tests for __init__ method
    @pytest.mark.unit
    def test_element_screenshots_initialization(self):
        """Test ElementScreenshots initialization."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        screenshots = ElementScreenshots(el)
        
        assert screenshots.element is el
        assert screenshots.shadowstep is el.shadowstep
        assert screenshots.converter is el.converter
        assert screenshots.utilities is el.utilities
        assert screenshots.logger is not None

    # Tests for screenshot_as_base64 method
    @pytest.mark.unit
    def test_screenshot_as_base64_success(self):
        """Test successful screenshot_as_base64 operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.screenshot_as_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.screenshots.screenshot_as_base64()
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert result == mock_native_element.screenshot_as_base64

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_screenshot_as_base64_handles_no_such_driver_exception(self, mock_handle_error):
        """Test screenshot_as_base64 handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=NoSuchDriverException("No driver")):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.screenshots.screenshot_as_base64()
        
        assert "Failed to get screenshot_as_base64" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_screenshot_as_base64_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test screenshot_as_base64 handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=InvalidSessionIdException("Invalid session")):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.screenshots.screenshot_as_base64()
        
        assert "Failed to get screenshot_as_base64" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_screenshot_as_base64_handles_attribute_error(self, mock_handle_error):
        """Test screenshot_as_base64 handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=AttributeError("Attribute error")):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.screenshots.screenshot_as_base64()
        
        assert "Failed to get screenshot_as_base64" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_screenshot_as_base64_handles_stale_element_reference_exception(self):
        """Test screenshot_as_base64 handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.screenshot_as_base64 = "base64string"
        
        app, el = self._create_test_element(mock_driver)
        
        get_native_calls = [
            StaleElementReferenceException("Stale"),
            mock_native_element,
            mock_native_element
        ]
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=get_native_calls):
                result = el.screenshots.screenshot_as_base64()
        
        assert result == "base64string"

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_screenshot_as_base64_handles_webdriver_exception(self, mock_handle_error):
        """Test screenshot_as_base64 handles WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=WebDriverException("Error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.screenshots.screenshot_as_base64()
        
        assert "Failed to get screenshot_as_base64" in str(exc_info.value)
        mock_handle_error.assert_called()

    # Tests for screenshot_as_png method
    @pytest.mark.unit
    def test_screenshot_as_png_success(self):
        """Test successful screenshot_as_png operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.screenshot_as_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.screenshots.screenshot_as_png()
        
        assert isinstance(result, bytes)
        assert result == mock_native_element.screenshot_as_png

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_screenshot_as_png_handles_no_such_driver_exception(self, mock_handle_error):
        """Test screenshot_as_png handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=NoSuchDriverException("No driver")):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.screenshots.screenshot_as_png()
        
        assert "Failed to get screenshot_as_png" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_screenshot_as_png_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test screenshot_as_png handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=InvalidSessionIdException("Invalid session")):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.screenshots.screenshot_as_png()
        
        assert "Failed to get screenshot_as_png" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_screenshot_as_png_handles_attribute_error(self, mock_handle_error):
        """Test screenshot_as_png handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=AttributeError("Attribute error")):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.screenshots.screenshot_as_png()
        
        assert "Failed to get screenshot_as_png" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_screenshot_as_png_handles_stale_element_reference_exception(self):
        """Test screenshot_as_png handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.screenshot_as_png = b'\x89PNG'
        
        app, el = self._create_test_element(mock_driver)
        
        get_native_calls = [
            StaleElementReferenceException("Stale"),
            mock_native_element,
            mock_native_element
        ]
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=get_native_calls):
                result = el.screenshots.screenshot_as_png()
        
        assert result == b'\x89PNG'

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_screenshot_as_png_handles_webdriver_exception(self, mock_handle_error):
        """Test screenshot_as_png handles WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=WebDriverException("Error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.screenshots.screenshot_as_png()
        
        assert "Failed to get screenshot_as_png" in str(exc_info.value)
        mock_handle_error.assert_called()

    # Tests for save_screenshot method
    @pytest.mark.unit
    def test_save_screenshot_success(self):
        """Test successful save_screenshot operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.screenshot.return_value = True
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.screenshots.save_screenshot("/tmp/test.png")
        
        assert result is True
        mock_native_element.screenshot.assert_called_once_with("/tmp/test.png")

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_save_screenshot_handles_no_such_driver_exception(self, mock_handle_error):
        """Test save_screenshot handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=NoSuchDriverException("No driver")):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.screenshots.save_screenshot("/tmp/test.png")
        
        assert "Failed to save screenshot" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_save_screenshot_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test save_screenshot handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=InvalidSessionIdException("Invalid session")):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.screenshots.save_screenshot("/tmp/test.png")
        
        assert "Failed to save screenshot" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_save_screenshot_handles_attribute_error(self, mock_handle_error):
        """Test save_screenshot handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=AttributeError("Attribute error")):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.screenshots.save_screenshot("/tmp/test.png")
        
        assert "Failed to save screenshot" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_save_screenshot_handles_stale_element_reference_exception(self):
        """Test save_screenshot handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.screenshot.return_value = True
        
        app, el = self._create_test_element(mock_driver)
        
        get_native_calls = [
            StaleElementReferenceException("Stale"),
            mock_native_element,
            mock_native_element
        ]
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=get_native_calls):
                result = el.screenshots.save_screenshot("/tmp/test.png")
        
        assert result is True

    @pytest.mark.unit
    def test_save_screenshot_handles_oserror(self):
        """Test save_screenshot handles OSError and returns False."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.screenshot.side_effect = OSError("Permission denied")
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.screenshots.save_screenshot("/invalid/path/test.png")
        
        assert result is False

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_save_screenshot_handles_webdriver_exception(self, mock_handle_error):
        """Test save_screenshot handles WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=WebDriverException("Error")):
                with pytest.raises(ShadowstepElementException) as exc_info:
                    el.screenshots.save_screenshot("/tmp/test.png")
        
        assert "Failed to save screenshot" in str(exc_info.value)
        mock_handle_error.assert_called()

    # Additional edge case tests
    @pytest.mark.unit
    def test_screenshot_as_base64_returns_empty_string_value(self):
        """Test screenshot_as_base64 can return empty string if element has no screenshot."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.screenshot_as_base64 = ""
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.screenshots.screenshot_as_base64()
        
        assert result == ""

    @pytest.mark.unit
    def test_screenshot_as_png_returns_empty_bytes(self):
        """Test screenshot_as_png can return empty bytes."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.screenshot_as_png = b''
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.screenshots.screenshot_as_png()
        
        assert result == b''

    @pytest.mark.unit
    def test_save_screenshot_returns_false_on_failure(self):
        """Test save_screenshot returns False when screenshot method returns False."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.screenshot.return_value = False
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.screenshots.save_screenshot("/tmp/test.png")
        
        assert result is False

    @pytest.mark.unit
    def test_save_screenshot_with_different_filename_formats(self):
        """Test save_screenshot with different filename formats."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.screenshot.return_value = True
        
        app, el = self._create_test_element(mock_driver)
        
        test_filenames = [
            "/tmp/screenshot.png",
            "screenshot.png",
            "./screenshots/test.png",
            "/home/user/images/element.png"
        ]
        
        for filename in test_filenames:
            with patch.object(el, 'get_driver', return_value=mock_driver):
                with patch.object(el, 'get_native', return_value=mock_native_element):
                    result = el.screenshots.save_screenshot(filename)
            
            assert result is True
            # Verify the filename was passed correctly
            assert mock_native_element.screenshot.call_args[0][0] == filename

    @pytest.mark.unit
    def test_save_screenshot_handles_ioerror_subclass(self):
        """Test save_screenshot handles IOError (OSError subclass)."""
        mock_driver = Mock()
        mock_native_element = Mock()
        # IOError is OSError in Python 3
        mock_native_element.screenshot.side_effect = IOError("Disk full")
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.screenshots.save_screenshot("/tmp/test.png")
        
        assert result is False

