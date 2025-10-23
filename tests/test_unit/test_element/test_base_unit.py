# ruff: noqa
# pyright: ignore
"""Unit tests for ElementBase class using mocks."""
from unittest.mock import Mock, patch

import pytest

from shadowstep.element.base import ElementBase


class TestElementBaseInit:
    """Test ElementBase initialization."""

    def test_init_with_tuple_locator(self):
        """Test initialization with tuple locator."""
        mock_shadowstep = Mock()
        locator = ("xpath", "//test")

        base = ElementBase(locator, mock_shadowstep, timeout=15, poll_frequency=1.0)

        assert base.locator == locator
        assert base.shadowstep == mock_shadowstep
        assert base.timeout == 15
        assert base.poll_frequency == 1.0
        assert base.ignored_exceptions is None
        assert base.native is None
        assert base.converter is not None
        assert base.logger is not None

    def test_init_with_dict_locator(self):
        """Test initialization with dict locator."""
        mock_shadowstep = Mock()
        locator = {"text": "Button", "class": "android.widget.Button"}

        base = ElementBase(locator, mock_shadowstep)

        assert base.locator == locator
        assert base.timeout == 30  # default
        assert base.poll_frequency == 0.5  # default

    def test_init_with_native_element(self):
        """Test initialization with native WebElement."""
        mock_shadowstep = Mock()
        mock_native = Mock()
        locator = ("id", "test_id")

        base = ElementBase(locator, mock_shadowstep, native=mock_native)

        assert base.native == mock_native

    def test_init_with_ignored_exceptions(self):
        """Test initialization with ignored exceptions."""
        mock_shadowstep = Mock()
        locator = ("id", "test")
        ignored_exceptions = (ValueError, KeyError)

        base = ElementBase(locator, mock_shadowstep, ignored_exceptions=ignored_exceptions)

        assert base.ignored_exceptions == ignored_exceptions

    def test_init_with_custom_timeout_and_poll(self):
        """Test initialization with custom timeout and poll frequency."""
        mock_shadowstep = Mock()
        locator = ("id", "test")

        base = ElementBase(locator, mock_shadowstep, timeout=20, poll_frequency=0.25)

        assert base.timeout == 20
        assert base.poll_frequency == 0.25


class TestRemoveNullValue:
    """Test remove_null_value method."""

    def test_remove_null_value_with_tuple_removes_null_attributes(self):
        """Test remove_null_value removes [@attr='null'] from XPath tuple."""
        mock_shadowstep = Mock()
        base = ElementBase(("id", "test"), mock_shadowstep)

        locator = ("xpath", "//android.widget.TextView[@text='Test'][@resource-id='null']")
        result = base.remove_null_value(locator)

        assert result[0] == "xpath"
        assert "[@resource-id='null']" not in result[1]
        assert "[@text='Test']" in result[1]

    def test_remove_null_value_with_tuple_multiple_null_attrs(self):
        """Test remove_null_value removes multiple null attributes."""
        mock_shadowstep = Mock()
        base = ElementBase(("id", "test"), mock_shadowstep)

        locator = ("xpath", "//div[@id='null'][@class='null'][@name='valid']")
        result = base.remove_null_value(locator)

        assert "[@id='null']" not in result[1]
        assert "[@class='null']" not in result[1]
        assert "[@name='valid']" in result[1]

    def test_remove_null_value_with_dict_removes_null_values(self):
        """Test remove_null_value removes entries where value is 'null'."""
        mock_shadowstep = Mock()
        base = ElementBase(("id", "test"), mock_shadowstep)

        locator = {"text": "Button", "resource-id": "null", "enabled": "true", "class": "null"}
        result = base.remove_null_value(locator)

        assert isinstance(result, dict)
        assert result["text"] == "Button"
        assert result["enabled"] == "true"
        assert "resource-id" not in result
        assert "class" not in result

    def test_remove_null_value_with_dict_all_null(self):
        """Test remove_null_value with dict containing only null values."""
        mock_shadowstep = Mock()
        base = ElementBase(("id", "test"), mock_shadowstep)

        locator = {"resource-id": "null", "class": "null"}
        result = base.remove_null_value(locator)

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_remove_null_value_with_dict_no_null(self):
        """Test remove_null_value with dict containing no null values."""
        mock_shadowstep = Mock()
        base = ElementBase(("id", "test"), mock_shadowstep)

        locator = {"text": "Button", "enabled": "true"}
        result = base.remove_null_value(locator)

        assert result == locator

    def test_remove_null_value_with_element_returns_unchanged(self):
        """Test remove_null_value returns Element unchanged."""
        mock_shadowstep = Mock()
        base = ElementBase(("id", "test"), mock_shadowstep)

        from shadowstep.element.element import Element
        mock_element = Mock(spec=Element)
        result = base.remove_null_value(mock_element)

        assert result is mock_element

    def test_remove_null_value_with_uiselector_returns_unchanged(self):
        """Test remove_null_value returns UiSelector unchanged."""
        mock_shadowstep = Mock()
        base = ElementBase(("id", "test"), mock_shadowstep)

        from shadowstep.locator import UiSelector
        ui_selector = UiSelector().text("Test")
        result = base.remove_null_value(ui_selector)

        assert result is ui_selector

    def test_remove_null_value_with_tuple_no_null(self):
        """Test remove_null_value with tuple XPath without null values."""
        mock_shadowstep = Mock()
        base = ElementBase(("id", "test"), mock_shadowstep)

        locator = ("xpath", "//android.widget.TextView[@text='Test'][@enabled='true']")
        result = base.remove_null_value(locator)

        assert result == locator


class TestGetDriver:
    """Test get_driver method."""

    def test_get_driver_retrieves_driver_from_singleton(self):
        """Test get_driver retrieves driver from WebDriverSingleton."""
        mock_shadowstep = Mock()
        base = ElementBase(("id", "test"), mock_shadowstep)

        mock_driver = Mock()
        
        with patch('shadowstep.element.base.WebDriverSingleton.get_driver', return_value=mock_driver) as mock_get:
            base.get_driver()

            mock_get.assert_called_once()
            assert base.driver == mock_driver

    def test_get_driver_called_multiple_times(self):
        """Test get_driver can be called multiple times."""
        mock_shadowstep = Mock()
        base = ElementBase(("id", "test"), mock_shadowstep)

        mock_driver = Mock()
        
        with patch('shadowstep.element.base.WebDriverSingleton.get_driver', return_value=mock_driver):
            base.get_driver()
            first_driver = base.driver
            
            base.get_driver()
            second_driver = base.driver

            assert first_driver == mock_driver
            assert second_driver == mock_driver

    def test_get_driver_updates_driver_attribute(self):
        """Test get_driver updates the driver attribute."""
        mock_shadowstep = Mock()
        base = ElementBase(("id", "test"), mock_shadowstep)

        # Initially driver is None
        assert base.driver is None

        mock_driver = Mock()
        with patch('shadowstep.element.base.WebDriverSingleton.get_driver', return_value=mock_driver):
            base.get_driver()

        # After calling get_driver, driver should be set
        assert base.driver is not None
        assert base.driver == mock_driver

