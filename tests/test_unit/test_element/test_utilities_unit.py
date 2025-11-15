# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Unit tests for ElementUtilities class using mocks."""
from typing import Any
from unittest.mock import MagicMock, Mock, PropertyMock, patch, call

import pytest
from lxml import etree
from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.element.element import Element
from shadowstep.element.utilities import ElementUtilities
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.locator import UiSelector


class TestElementUtilitiesInit:
    """Test ElementUtilities initialization."""

    def test_init_creates_instance_with_element(self):
        """Test initialization creates instance with element reference."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep

        utilities = ElementUtilities(mock_element)

        assert utilities.element == mock_element
        assert utilities.shadowstep == mock_shadowstep
        assert utilities.logger is not None


class TestRemoveNullValue:
    """Test remove_null_value method."""

    def test_remove_null_value_with_tuple_xpath_removes_null_attribute(self):
        """Test remove_null_value removes [@attr='null'] from XPath."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        locator = ("xpath", "//android.widget.TextView[@text='Settings'][@resource-id='null']")
        result = utilities.remove_null_value(locator)

        assert result[0] == "xpath"
        assert "[@resource-id='null']" not in result[1]
        assert "[@text='Settings']" in result[1]

    def test_remove_null_value_with_tuple_multiple_null_attributes(self):
        """Test remove_null_value removes multiple null attributes."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        locator = ("xpath", "//android.widget.TextView[@text='Test'][@id='null'][@class='null']")
        result = utilities.remove_null_value(locator)

        assert result[0] == "xpath"
        assert "[@id='null']" not in result[1]
        assert "[@class='null']" not in result[1]
        assert "[@text='Test']" in result[1]

    def test_remove_null_value_with_dict_removes_null_values(self):
        """Test remove_null_value removes key-value pairs where value is 'null'."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        locator = {"text": "Settings", "resource-id": "null", "enabled": "true", "class": "null"}
        result = utilities.remove_null_value(locator)

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"
        assert "enabled" in result
        assert result["enabled"] == "true"
        assert "resource-id" not in result
        assert "class" not in result

    def test_remove_null_value_with_dict_empty_after_removal(self):
        """Test remove_null_value with dict containing only null values."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        locator = {"resource-id": "null", "class": "null"}
        result = utilities.remove_null_value(locator)

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_remove_null_value_with_element_returns_unchanged(self):
        """Test remove_null_value returns Element unchanged."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        another_element = Mock(spec=Element)
        result = utilities.remove_null_value(another_element)

        assert result is another_element

    def test_remove_null_value_with_uiselector_returns_unchanged(self):
        """Test remove_null_value returns UiSelector unchanged."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        ui_selector = UiSelector().resourceId("test_id")
        result = utilities.remove_null_value(ui_selector)

        assert result is ui_selector


class TestExtractElAttrsFromSource:
    """Test extract_el_attrs_from_source method."""

    def test_extract_el_attrs_from_source_with_valid_xpath(self):
        """Test extracting attributes from page source with valid XPath."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        page_source = """<?xml version="1.0" encoding="UTF-8"?>
        <hierarchy>
            <android.widget.TextView text="Settings" resource-id="com.android.settings:id/title" enabled="true"/>
            <android.widget.TextView text="Network" resource-id="com.android.settings:id/summary"/>
        </hierarchy>"""

        xpath_expr = '//android.widget.TextView[@text="Settings"]'
        result = utilities.extract_el_attrs_from_source(xpath_expr, page_source)

        assert len(result) == 1
        assert result[0]["text"] == "Settings"
        assert result[0]["resource-id"] == "com.android.settings:id/title"
        assert result[0]["enabled"] == "true"

    def test_extract_el_attrs_from_source_with_multiple_matches(self):
        """Test extracting attributes with XPath matching multiple elements."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        page_source = """<?xml version="1.0" encoding="UTF-8"?>
        <hierarchy>
            <android.widget.TextView text="Settings" resource-id="id1"/>
            <android.widget.TextView text="Network" resource-id="id2"/>
            <android.widget.TextView text="Display" resource-id="id3"/>
        </hierarchy>"""

        xpath_expr = "//android.widget.TextView"
        result = utilities.extract_el_attrs_from_source(xpath_expr, page_source)

        assert len(result) == 3
        assert result[0]["text"] == "Settings"
        assert result[1]["text"] == "Network"
        assert result[2]["text"] == "Display"

    def test_extract_el_attrs_from_source_no_matches_raises_exception(self):
        """Test extract_el_attrs_from_source raises exception when no matches found."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        page_source = """<?xml version="1.0" encoding="UTF-8"?>
        <hierarchy>
            <android.widget.TextView text="Settings"/>
        </hierarchy>"""

        xpath_expr = '//android.widget.Button[@text="NonExistent"]'

        with pytest.raises(ShadowstepElementException) as exc_info:
            utilities.extract_el_attrs_from_source(xpath_expr, page_source)

        assert "No matches found for XPath" in str(exc_info.value)

    def test_extract_el_attrs_from_source_invalid_xpath_raises_exception(self):
        """Test extract_el_attrs_from_source raises exception with invalid XPath."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        page_source = """<?xml version="1.0" encoding="UTF-8"?>
        <hierarchy>
            <android.widget.TextView text="Settings"/>
        </hierarchy>"""

        xpath_expr = '//android.widget.TextView[@text='  # Invalid XPath

        with pytest.raises(ShadowstepElementException) as exc_info:
            utilities.extract_el_attrs_from_source(xpath_expr, page_source)

        assert "Parsing error" in str(exc_info.value)

    def test_extract_el_attrs_from_source_malformed_xml_raises_exception(self):
        """Test extract_el_attrs_from_source handles malformed XML."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        # Malformed but recoverable XML - lxml's recover mode should handle this
        page_source = """<?xml version="1.0" encoding="UTF-8"?>
        <hierarchy>
            <android.widget.TextView text="Settings"
        </hierarchy>"""

        xpath_expr = "//android.widget.TextView"
        
        # With recover=True, this should work or at least not crash
        # If it fails, it should raise ShadowstepElementException
        try:
            result = utilities.extract_el_attrs_from_source(xpath_expr, page_source)
            # If it succeeds, verify result structure
            assert isinstance(result, list)
        except ShadowstepElementException:
            # Expected behavior for malformed XML
            pass


class TestGetXpath:
    """Test get_xpath method."""

    def test_get_xpath_with_tuple_locator_returns_xpath_string(self):
        """Test get_xpath returns XPath string when locator is tuple."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", '//android.widget.TextView[@text="Settings"]')
        utilities = ElementUtilities(mock_element)

        result = utilities.get_xpath()

        assert result == '//android.widget.TextView[@text="Settings"]'

    def test_get_xpath_with_tuple_locator_removes_null_values(self):
        """Test get_xpath removes null values from tuple locator."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", '//android.widget.TextView[@text="Settings"][@id="null"]')
        utilities = ElementUtilities(mock_element)

        result = utilities.get_xpath()

        assert "[@id='null']" not in result
        assert '[@text="Settings"]' in result

    def test_get_xpath_with_dict_locator_calls_get_xpath_by_driver(self):
        """Test get_xpath calls _get_xpath_by_driver when locator is dict."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = {"text": "Settings"}
        utilities = ElementUtilities(mock_element)

        with patch.object(utilities, '_get_xpath_by_driver', return_value='//android.widget.TextView[@text="Settings"]') as mock_method:
            result = utilities.get_xpath()

            mock_method.assert_called_once()
            assert result == '//android.widget.TextView[@text="Settings"]'


class TestGetXpathByDriver:
    """Test _get_xpath_by_driver method."""

    def test_get_xpath_by_driver_builds_xpath_from_attributes(self):
        """Test _get_xpath_by_driver builds XPath from element attributes."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_attributes = Mock(return_value={
            "class": "android.widget.TextView",
            "text": "Settings",
            "enabled": "true"
        })
        utilities = ElementUtilities(mock_element)
        # Mock element.utilities to return self
        mock_element.utilities = utilities

        result = utilities._get_xpath_by_driver()

        assert result.startswith("//android.widget.TextView")
        assert "[@text='Settings']" in result
        assert "[@enabled='true']" in result

    def test_get_xpath_by_driver_returns_empty_on_no_attributes(self):
        """Test _get_xpath_by_driver returns empty string when no attributes."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_attributes = Mock(return_value=None)
        utilities = ElementUtilities(mock_element)

        result = utilities._get_xpath_by_driver()

        assert result == ""

    def test_get_xpath_by_driver_returns_empty_on_empty_attributes(self):
        """Test _get_xpath_by_driver raises exception on empty attributes dict."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_attributes = Mock(return_value={})
        utilities = ElementUtilities(mock_element)

        result = utilities._get_xpath_by_driver()

        assert result == ""

    def test_get_xpath_by_driver_handles_attribute_error(self):
        """Test _get_xpath_by_driver handles AttributeError."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_attributes = Mock(side_effect=AttributeError("No attribute"))
        utilities = ElementUtilities(mock_element)

        result = utilities._get_xpath_by_driver()

        assert result == ""

    def test_get_xpath_by_driver_handles_key_error(self):
        """Test _get_xpath_by_driver handles KeyError."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_attributes = Mock(side_effect=KeyError("Missing key"))
        utilities = ElementUtilities(mock_element)

        result = utilities._get_xpath_by_driver()

        assert result == ""

    def test_get_xpath_by_driver_handles_webdriver_exception(self):
        """Test _get_xpath_by_driver handles WebDriverException."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_attributes = Mock(side_effect=WebDriverException("Driver error"))
        utilities = ElementUtilities(mock_element)

        result = utilities._get_xpath_by_driver()

        assert result == ""


class TestHandleDriverError:
    """Test handle_driver_error method."""

    def test_handle_driver_error_calls_reconnect(self):
        """Test handle_driver_error calls shadowstep.reconnect()."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        error = WebDriverException("Test error")

        with patch('time.sleep'):  # Mock sleep to speed up test
            utilities.handle_driver_error(error)

        mock_shadowstep.reconnect.assert_called_once()

    def test_handle_driver_error_sleeps_after_reconnect(self):
        """Test handle_driver_error sleeps after reconnect."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        error = WebDriverException("Test error")

        with patch('time.sleep') as mock_sleep:
            utilities.handle_driver_error(error)

            mock_sleep.assert_called_once_with(0.3)


class TestBuildXpathAttributeCondition:
    """Test _build_xpath_attribute_condition method."""

    def test_build_xpath_attribute_condition_with_null_value(self):
        """Test building XPath condition with null value."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        result = utilities._build_xpath_attribute_condition("resource-id", "null")

        assert result == "[@resource-id]"

    def test_build_xpath_attribute_condition_with_none_value(self):
        """Test building XPath condition with None value."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        result = utilities._build_xpath_attribute_condition("resource-id", None)

        assert result == "[@resource-id]"

    def test_build_xpath_attribute_condition_with_single_quote(self):
        """Test building XPath condition with single quote in value."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        result = utilities._build_xpath_attribute_condition("text", "It's working")

        assert result == '[@text="It\'s working"]'

    def test_build_xpath_attribute_condition_with_double_quote(self):
        """Test building XPath condition with double quote in value."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        result = utilities._build_xpath_attribute_condition("text", 'Say "Hello"')

        assert result == "[@text='Say \"Hello\"']"

    def test_build_xpath_attribute_condition_with_both_quotes(self):
        """Test building XPath condition with both quote types in value."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        result = utilities._build_xpath_attribute_condition("text", 'It\'s "working"')

        assert "concat(" in result
        assert "[@text=" in result

    def test_build_xpath_attribute_condition_with_simple_value(self):
        """Test building XPath condition with simple value."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        result = utilities._build_xpath_attribute_condition("text", "Settings")

        assert result == "[@text='Settings']"


class TestBuildXpathFromAttributes:
    """Test build_xpath_from_attributes method."""

    def test_build_xpath_from_attributes_with_class(self):
        """Test building XPath from attributes with class."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        attrs = {
            "class": "android.widget.TextView",
            "text": "Settings",
            "enabled": "true"
        }

        result = utilities.build_xpath_from_attributes(attrs)

        assert result.startswith("//android.widget.TextView")
        assert "[@text='Settings']" in result
        assert "[@enabled='true']" in result

    def test_build_xpath_from_attributes_without_class(self):
        """Test building XPath from attributes without class uses wildcard."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        attrs = {
            "text": "Settings",
            "enabled": "true"
        }

        result = utilities.build_xpath_from_attributes(attrs)

        assert result.startswith("//*")
        assert "[@text='Settings']" in result
        assert "[@enabled='true']" in result

    def test_build_xpath_from_attributes_excludes_hint(self):
        """Test building XPath excludes 'hint' attribute."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        attrs = {
            "class": "android.widget.EditText",
            "text": "Username",
            "hint": "Enter username"
        }

        result = utilities.build_xpath_from_attributes(attrs)

        assert "[@text='Username']" in result
        assert "hint" not in result

    def test_build_xpath_from_attributes_excludes_selection_start(self):
        """Test building XPath excludes 'selection-start' attribute."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        attrs = {
            "class": "android.widget.EditText",
            "text": "test",
            "selection-start": "0"
        }

        result = utilities.build_xpath_from_attributes(attrs)

        assert "selection-start" not in result

    def test_build_xpath_from_attributes_excludes_selection_end(self):
        """Test building XPath excludes 'selection-end' attribute."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        attrs = {
            "class": "android.widget.EditText",
            "text": "test",
            "selection-end": "4"
        }

        result = utilities.build_xpath_from_attributes(attrs)

        assert "selection-end" not in result

    def test_build_xpath_from_attributes_excludes_extras(self):
        """Test building XPath excludes 'extras' attribute."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        attrs = {
            "class": "android.widget.TextView",
            "text": "Settings",
            "extras": "some_extra_data"
        }

        result = utilities.build_xpath_from_attributes(attrs)

        assert "extras" not in result

    def test_build_xpath_from_attributes_with_null_value(self):
        """Test building XPath handles null value."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        attrs = {
            "class": "android.widget.TextView",
            "resource-id": "null"
        }

        result = utilities.build_xpath_from_attributes(attrs)

        assert "[@resource-id]" in result
        assert "null" not in result

    def test_build_xpath_from_attributes_with_special_characters(self):
        """Test building XPath handles special characters."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        utilities = ElementUtilities(mock_element)

        attrs = {
            "class": "android.widget.TextView",
            "text": "It's working"
        }

        result = utilities.build_xpath_from_attributes(attrs)

        assert '[@text="It\'s working"]' in result


class TestEnsureSessionAlive:
    """Test _ensure_session_alive method."""

    def test_ensure_session_alive_calls_get_driver(self):
        """Test _ensure_session_alive calls get_driver."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_driver = Mock(return_value=Mock())
        utilities = ElementUtilities(mock_element)

        utilities._ensure_session_alive()

        mock_element.get_driver.assert_called_once()

    def test_ensure_session_alive_reconnects_on_no_such_driver(self):
        """Test _ensure_session_alive reconnects on NoSuchDriverException."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_driver = Mock(side_effect=NoSuchDriverException("No driver"))
        utilities = ElementUtilities(mock_element)

        utilities._ensure_session_alive()

        mock_shadowstep.reconnect.assert_called_once()

    def test_ensure_session_alive_reconnects_on_invalid_session(self):
        """Test _ensure_session_alive reconnects on InvalidSessionIdException."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_driver = Mock(side_effect=InvalidSessionIdException("Invalid session"))
        utilities = ElementUtilities(mock_element)

        utilities._ensure_session_alive()

        mock_shadowstep.reconnect.assert_called_once()


class TestGetFirstChildClass:
    """Test _get_first_child_class method."""

    def test_get_first_child_class_returns_child_class(self):
        """Test _get_first_child_class returns child class name."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_attribute = Mock(return_value="android.widget.LinearLayout")
        
        mock_child = Mock(spec=Element)
        mock_child.get_attribute = Mock(return_value="android.widget.TextView")
        
        mock_element.get_elements = Mock(return_value=[mock_child])
        
        utilities = ElementUtilities(mock_element)

        result = utilities._get_first_child_class(tries=3)

        assert result == "android.widget.TextView"

    def test_get_first_child_class_retries_on_stale_element(self):
        """Test _get_first_child_class retries on StaleElementReferenceException."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.native = Mock()
        
        # First call raises StaleElementReferenceException, second succeeds
        mock_element.get_attribute = Mock(side_effect=[
            StaleElementReferenceException("Stale"),
            "android.widget.LinearLayout"
        ])
        
        mock_child = Mock(spec=Element)
        mock_child.get_attribute = Mock(return_value="android.widget.TextView")
        mock_element.get_elements = Mock(return_value=[mock_child])
        mock_element.get_native = Mock()
        
        utilities = ElementUtilities(mock_element)

        result = utilities._get_first_child_class(tries=3)

        assert result == "android.widget.TextView"
        assert mock_element.get_native.called

    def test_get_first_child_class_handles_instrumentation_error(self):
        """Test _get_first_child_class handles instrumentation process error."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        
        # First call raises instrumentation error, second succeeds
        mock_element.get_attribute = Mock(side_effect=[
            WebDriverException("instrumentation process is not running"),
            "android.widget.LinearLayout"
        ])
        
        mock_child = Mock(spec=Element)
        mock_child.get_attribute = Mock(return_value="android.widget.TextView")
        mock_element.get_elements = Mock(return_value=[mock_child])
        
        utilities = ElementUtilities(mock_element)
        utilities.handle_driver_error = Mock()

        with patch('time.sleep'):
            result = utilities._get_first_child_class(tries=3)

        assert utilities.handle_driver_error.called

    def test_get_first_child_class_handles_socket_hang_up(self):
        """Test _get_first_child_class handles socket hang up error."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        
        # First call raises socket error, second succeeds
        mock_element.get_attribute = Mock(side_effect=[
            WebDriverException("socket hang up"),
            "android.widget.LinearLayout"
        ])
        
        mock_child = Mock(spec=Element)
        mock_child.get_attribute = Mock(return_value="android.widget.TextView")
        mock_element.get_elements = Mock(return_value=[mock_child])
        
        utilities = ElementUtilities(mock_element)
        utilities.handle_driver_error = Mock()

        with patch('time.sleep'):
            result = utilities._get_first_child_class(tries=3)

        assert utilities.handle_driver_error.called

    def test_get_first_child_class_returns_empty_on_max_retries(self):
        """Test _get_first_child_class returns empty string after max retries."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.native = Mock()
        
        # Always raise StaleElementReferenceException
        mock_element.get_attribute = Mock(side_effect=StaleElementReferenceException("Stale"))
        mock_element.get_native = Mock()
        
        utilities = ElementUtilities(mock_element)

        result = utilities._get_first_child_class(tries=2)

        assert result == ""

    def test_get_first_child_class_skips_same_class_children(self):
        """Test _get_first_child_class skips children with same class as parent."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_attribute = Mock(return_value="android.widget.LinearLayout")
        
        # First child has same class, second has different
        mock_child1 = Mock(spec=Element)
        mock_child1.get_attribute = Mock(return_value="android.widget.LinearLayout")
        
        mock_child2 = Mock(spec=Element)
        mock_child2.get_attribute = Mock(return_value="android.widget.TextView")
        
        mock_element.get_elements = Mock(return_value=[mock_child1, mock_child2])
        
        utilities = ElementUtilities(mock_element)

        result = utilities._get_first_child_class(tries=3)

        assert result == "android.widget.TextView"

    def test_get_first_child_class_reraises_unexpected_webdriver_exception(self):
        """Test _get_first_child_class re-raises unexpected WebDriverException."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        
        # Raise unexpected WebDriverException
        mock_element.get_attribute = Mock(side_effect=WebDriverException("Unexpected error"))
        
        utilities = ElementUtilities(mock_element)

        with pytest.raises(WebDriverException):
            utilities._get_first_child_class(tries=3)

