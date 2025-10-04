"""Unit tests for shadowstep/element/base.py module."""
from unittest.mock import Mock, patch, MagicMock
import pytest
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    InvalidSessionIdException,
    WebDriverException,
)
from appium.webdriver.webelement import WebElement

from shadowstep.element.base import ElementBase
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepNoSuchElementException,
    ShadowstepTimeoutException,
)


class TestElementBase:
    """Test suite for ElementBase class."""

    @pytest.mark.unit
    def test_init_with_all_parameters(self):
        """Test ElementBase initialization with all parameters."""
        mock_shadowstep = Mock()
        mock_native = Mock(spec=WebElement)
        locator = ("xpath", "//test")
        timeout = 25.0
        poll_frequency = 0.3
        ignored_exceptions = (NoSuchElementException,)
        
        element_base = ElementBase(
            locator=locator,
            shadowstep=mock_shadowstep,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
            native=mock_native
        )
        
        assert element_base.locator == locator
        assert element_base.shadowstep == mock_shadowstep
        assert element_base.timeout == timeout
        assert element_base.poll_frequency == poll_frequency
        assert element_base.ignored_exceptions == ignored_exceptions
        assert element_base.native == mock_native
        assert element_base.converter is not None

    @pytest.mark.unit
    def test_remove_null_value_with_tuple_xpath(self):
        """Test remove_null_value with tuple locator containing null attribute."""
        mock_shadowstep = Mock()
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        
        locator = ("xpath", "//div[@class='test'][@attr='null'][@id='123']")
        result = element_base.remove_null_value(locator)
        
        assert result == ("xpath", "//div[@class='test'][@id='123']")

    @pytest.mark.unit
    def test_remove_null_value_with_dict(self):
        """Test remove_null_value with dict locator containing null values."""
        mock_shadowstep = Mock()
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        
        locator = {"class": "test", "text": "null", "id": "123"}
        result = element_base.remove_null_value(locator)
        
        assert result == {"class": "test", "id": "123"}
        assert "text" not in result

    @pytest.mark.unit
    def test_remove_null_value_with_other_types(self):
        """Test remove_null_value with non-tuple, non-dict locators."""
        mock_shadowstep = Mock()
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        
        # Test with string (should return unchanged)
        locator = "some_locator_string"
        result = element_base.remove_null_value(locator)
        assert result == locator

    @pytest.mark.unit
    @patch("shadowstep.element.base.WebDriverSingleton.get_driver")
    def test_get_driver(self, mock_get_driver):
        """Test get_driver method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        mock_shadowstep = Mock()
        
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        element_base.get_driver()
        
        assert element_base.driver == mock_driver
        mock_get_driver.assert_called_once()

    @pytest.mark.unit
    @patch("shadowstep.element.base.WebDriverSingleton.get_driver")
    @patch("shadowstep.element.base.WebDriverWait")
    def test_get_web_element_with_web_element_locator(self, mock_wait, mock_get_driver):
        """Test _get_web_element when locator is already a WebElement."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        mock_shadowstep = Mock()
        mock_web_element = Mock(spec=WebElement)
        
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        result = element_base._get_web_element(mock_web_element)
        
        assert result == mock_web_element
        mock_wait.assert_not_called()

    @pytest.mark.unit
    @patch("shadowstep.element.base.WebDriverSingleton.get_driver")
    @patch("shadowstep.element.base.WebDriverWait")
    @patch("shadowstep.element.base.LocatorConverter")
    def test_get_web_element_raises_error_on_empty_locator(
        self, mock_converter_class, mock_wait, mock_get_driver
    ):
        """Test _get_web_element raises error when locator is empty after remove_null_value."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        mock_shadowstep = Mock()
        
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        # Make remove_null_value return empty dict
        with patch.object(element_base, "remove_null_value", return_value={}):
            with pytest.raises(ShadowstepNoSuchElementException, match="Failed to resolve locator"):
                element_base._get_web_element({"text": "null"})

    @pytest.mark.unit
    @patch("shadowstep.element.base.WebDriverSingleton.get_driver")
    @patch("shadowstep.element.base.WebDriverWait")
    @patch("shadowstep.element.base.LocatorConverter")
    def test_get_web_element_no_such_element_exception(
        self, mock_converter_class, mock_wait, mock_get_driver
    ):
        """Test _get_web_element handles NoSuchElementException."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        mock_shadowstep = Mock()
        
        # Setup converter
        mock_converter = Mock()
        mock_converter.to_xpath.return_value = ("xpath", "//test")
        mock_converter_class.return_value = mock_converter
        
        # Setup wait to raise NoSuchElementException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = NoSuchElementException(
            msg="Element not found",
            screen="screenshot.png",
            stacktrace=["trace1", "trace2"]
        )
        mock_wait.return_value = mock_wait_instance
        
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        
        with pytest.raises(ShadowstepNoSuchElementException) as exc_info:
            element_base._get_web_element(("xpath", "//test"))
        
        assert "Element not found" in exc_info.value.msg
        assert exc_info.value.locator == ("xpath", "//test")

    @pytest.mark.unit
    @patch("shadowstep.element.base.WebDriverSingleton.get_driver")
    @patch("shadowstep.element.base.WebDriverWait")
    @patch("shadowstep.element.base.LocatorConverter")
    def test_get_web_element_timeout_exception_with_no_such_element_in_stacktrace(
        self, mock_converter_class, mock_wait, mock_get_driver
    ):
        """Test _get_web_element handles TimeoutException with NoSuchElementError in stacktrace."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        mock_shadowstep = Mock()
        
        # Setup converter
        mock_converter = Mock()
        mock_converter.to_xpath.return_value = ("xpath", "//test")
        mock_converter_class.return_value = mock_converter
        
        # Setup wait to raise TimeoutException with NoSuchElementError in stacktrace
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException(
            msg="Timeout",
            screen="screenshot.png",
            stacktrace=["trace1", "NoSuchElementError: element not found", "trace2"]
        )
        mock_wait.return_value = mock_wait_instance
        
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        
        with pytest.raises(ShadowstepNoSuchElementException) as exc_info:
            element_base._get_web_element(("xpath", "//test"))
        
        assert exc_info.value.msg == "Timeout"

    @pytest.mark.unit
    @patch("shadowstep.element.base.WebDriverSingleton.get_driver")
    @patch("shadowstep.element.base.WebDriverWait")
    @patch("shadowstep.element.base.LocatorConverter")
    def test_get_web_element_timeout_exception_without_no_such_element(
        self, mock_converter_class, mock_wait, mock_get_driver
    ):
        """Test _get_web_element handles TimeoutException without NoSuchElementError."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        mock_shadowstep = Mock()
        
        # Setup converter
        mock_converter = Mock()
        mock_converter.to_xpath.return_value = ("xpath", "//test")
        mock_converter_class.return_value = mock_converter
        
        # Setup wait to raise TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException(
            msg="Timeout waiting",
            screen="screenshot.png",
            stacktrace=["trace1", "trace2"]
        )
        mock_wait.return_value = mock_wait_instance
        
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        
        with pytest.raises(ShadowstepTimeoutException) as exc_info:
            element_base._get_web_element(("xpath", "//test"))
        
        assert "Timeout waiting for element" in exc_info.value.msg
        assert exc_info.value.locator == ("xpath", "//test")

    @pytest.mark.unit
    @patch("shadowstep.element.base.WebDriverSingleton.get_driver")
    @patch("shadowstep.element.base.WebDriverWait")
    @patch("shadowstep.element.base.LocatorConverter")
    def test_get_web_element_invalid_session_id_exception(
        self, mock_converter_class, mock_wait, mock_get_driver
    ):
        """Test _get_web_element handles InvalidSessionIdException."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        mock_shadowstep = Mock()
        
        # Setup converter
        mock_converter = Mock()
        mock_converter.to_xpath.return_value = ("xpath", "//test")
        mock_converter_class.return_value = mock_converter
        
        # Setup wait to raise InvalidSessionIdException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = InvalidSessionIdException("Invalid session")
        mock_wait.return_value = mock_wait_instance
        
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        
        with pytest.raises(InvalidSessionIdException):
            element_base._get_web_element(("xpath", "//test"))

    @pytest.mark.unit
    @patch("shadowstep.element.base.WebDriverSingleton.get_driver")
    @patch("shadowstep.element.base.WebDriverWait")
    @patch("shadowstep.element.base.LocatorConverter")
    def test_get_web_element_webdriver_exception(
        self, mock_converter_class, mock_wait, mock_get_driver
    ):
        """Test _get_web_element handles WebDriverException."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        mock_shadowstep = Mock()
        
        # Setup converter
        mock_converter = Mock()
        mock_converter.to_xpath.return_value = ("xpath", "//test")
        mock_converter_class.return_value = mock_converter
        
        # Setup wait to raise WebDriverException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = WebDriverException("WebDriver error")
        mock_wait.return_value = mock_wait_instance
        
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        
        with pytest.raises(WebDriverException):
            element_base._get_web_element(("xpath", "//test"))

    @pytest.mark.unit
    @patch("shadowstep.element.base.WebDriverSingleton.get_driver")
    @patch("shadowstep.element.base.WebDriverWait")
    @patch("shadowstep.element.base.LocatorConverter")
    def test_get_web_element_success(
        self, mock_converter_class, mock_wait, mock_get_driver
    ):
        """Test _get_web_element successful element retrieval."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        mock_shadowstep = Mock()
        
        # Setup converter
        mock_converter = Mock()
        mock_converter.to_xpath.return_value = ("xpath", "//test")
        mock_converter_class.return_value = mock_converter
        
        # Setup wait to return element
        mock_element = Mock(spec=WebElement)
        mock_element.id = "element_123"
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = mock_element
        mock_wait.return_value = mock_wait_instance
        
        element_base = ElementBase(("xpath", "//test"), mock_shadowstep)
        result = element_base._get_web_element(("xpath", "//test"))
        
        assert result == mock_element
        assert element_base.id == "element_123"

