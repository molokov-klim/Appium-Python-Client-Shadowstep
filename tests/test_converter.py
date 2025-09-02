# tests/test_converter.py
"""
Tests for the unified LocatorConverter.

This module tests the new LocatorConverter that replaces the deprecated
DeprecatedLocatorConverter with a modern, well-architected solution.
"""

import logging

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ConversionError
from shadowstep.locator.converter.locator_converter import LocatorConverter
from shadowstep.locator.types.shadowstep_dict import DictAttribute

logger = logging.getLogger(__name__)


class TestUnifiedLocatorConverter:
    """Test cases for the unified LocatorConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = LocatorConverter()

    def test_to_dict_from_dict(self):
        """Test converting dict to dict (should return unchanged)."""
        selector_dict = {DictAttribute.TEXT: "OK"}
        result = self.converter.to_dict(selector_dict)
        assert result == selector_dict

    def test_to_dict_from_xpath_tuple(self):
        """Test converting XPath tuple to dict."""
        xpath_tuple = ("xpath", "//*[@text='OK']")
        result = self.converter.to_dict(xpath_tuple)
        assert DictAttribute.TEXT in result
        assert result[DictAttribute.TEXT] == "OK"

    def test_to_dict_from_xpath_string(self):
        """Test converting XPath string to dict."""
        xpath_string = "//*[@text='OK']"
        result = self.converter.to_dict(xpath_string)
        assert DictAttribute.TEXT in result
        assert result[DictAttribute.TEXT] == "OK"

    def test_to_dict_from_uiselector_string(self):
        """Test converting UiSelector string to dict."""
        ui_string = 'new UiSelector().text("OK");'
        result = self.converter.to_dict(ui_string)
        assert DictAttribute.TEXT in result
        assert result[DictAttribute.TEXT] == "OK"

    def test_to_xpath_from_dict(self):
        """Test converting dict to XPath tuple."""
        selector_dict = {DictAttribute.TEXT: "OK"}
        result = self.converter.to_xpath(selector_dict)
        assert result[0] == "xpath"
        assert 'text="OK"' in result[1]

    def test_to_xpath_from_xpath_tuple(self):
        """Test converting XPath tuple to XPath tuple (should return unchanged)."""
        xpath_tuple = ("xpath", "//*[@text='OK']")
        result = self.converter.to_xpath(xpath_tuple)
        assert result == xpath_tuple

    def test_to_xpath_from_xpath_string(self):
        """Test converting XPath string to XPath tuple."""
        xpath_string = "//*[@text='OK']"
        result = self.converter.to_xpath(xpath_string)
        assert result[0] == "xpath"
        assert result[1] == xpath_string

    def test_to_xpath_from_uiselector_string(self):
        """Test converting UiSelector string to XPath tuple."""
        ui_string = 'new UiSelector().text("OK");'
        result = self.converter.to_xpath(ui_string)
        assert result[0] == "xpath"
        assert 'text="OK"' in result[1]

    def test_to_uiselector_from_dict(self):
        """Test converting dict to UiSelector string."""
        selector_dict = {DictAttribute.TEXT: "OK"}
        result = self.converter.to_uiselector(selector_dict)
        assert result.startswith("new UiSelector()")
        assert 'text("OK")' in result

    def test_to_uiselector_from_xpath_tuple(self):
        """Test converting XPath tuple to UiSelector string."""
        xpath_tuple = ("xpath", "//*[@text='OK']")
        result = self.converter.to_uiselector(xpath_tuple)
        assert result.startswith("new UiSelector()")
        assert 'text("OK")' in result

    def test_to_uiselector_from_xpath_string(self):
        """Test converting XPath string to UiSelector string."""
        xpath_string = "//*[@text='OK']"
        result = self.converter.to_uiselector(xpath_string)
        assert result.startswith("new UiSelector()")
        assert 'text("OK")' in result

    def test_to_uiselector_from_uiselector_string(self):
        """Test converting UiSelector string to UiSelector string (should return unchanged)."""
        ui_string = 'new UiSelector().text("OK");'
        result = self.converter.to_uiselector(ui_string)
        assert result == ui_string

    def test_direct_conversion_methods(self):
        """Test direct conversion methods between specific formats."""
        selector_dict = {DictAttribute.TEXT: "OK", DictAttribute.CLICKABLE: True}
        
        # Dict to XPath
        xpath = self.converter.dict_to_xpath(selector_dict)
        assert 'text="OK"' in xpath
        assert 'clickable="true"' in xpath
        
        # Dict to UiSelector
        ui_selector = self.converter.dict_to_uiselector(selector_dict)
        assert 'text("OK")' in ui_selector
        assert 'clickable(true)' in ui_selector
        
        # XPath to Dict
        dict_from_xpath = self.converter.xpath_to_dict(xpath)
        assert DictAttribute.TEXT in dict_from_xpath
        assert DictAttribute.CLICKABLE in dict_from_xpath
        
        # XPath to UiSelector
        ui_from_xpath = self.converter.xpath_to_uiselector(xpath)
        assert 'text("OK")' in ui_from_xpath
        assert 'clickable(true)' in ui_from_xpath
        
        # UiSelector to Dict
        dict_from_ui = self.converter.uiselector_to_dict(ui_selector)
        assert DictAttribute.TEXT in dict_from_ui
        assert DictAttribute.CLICKABLE in dict_from_ui
        
        # UiSelector to XPath
        xpath_from_ui = self.converter.uiselector_to_xpath(ui_selector)
        assert 'text="OK"' in xpath_from_ui
        assert 'clickable="true"' in xpath_from_ui

    def test_validate_selector_valid_dict(self):
        """Test validation of valid dictionary selector."""
        selector_dict = {DictAttribute.TEXT: "OK"}
        # Should not raise any exception
        self.converter.validate_selector(selector_dict)

    def test_validate_selector_valid_xpath_tuple(self):
        """Test validation of valid XPath tuple."""
        xpath_tuple = ("xpath", "//*[@text='OK']")
        # Should not raise any exception
        self.converter.validate_selector(xpath_tuple)

    def test_validate_selector_valid_string(self):
        """Test validation of valid string selector."""
        ui_string = 'new UiSelector().text("OK");'
        # Should not raise any exception
        self.converter.validate_selector(ui_string)

    def test_validate_selector_invalid_tuple(self):
        """Test validation of invalid tuple format."""
        invalid_tuple = ("invalid", "//*[@text='OK']")
        with pytest.raises(ValueError, match="Unsupported tuple format"):
            self.converter.validate_selector(invalid_tuple)

    def test_validate_selector_empty_string(self):
        """Test validation of empty string."""
        with pytest.raises(ValueError, match="Selector string cannot be empty"):
            self.converter.validate_selector("")

    def test_validate_selector_invalid_type(self):
        """Test validation of invalid selector type."""
        with pytest.raises(ValueError, match="Unsupported selector type"):
            self.converter.validate_selector(123)

    def test_conversion_error_handling(self):
        """Test proper error handling during conversion."""
        # Test with invalid XPath tuple format
        invalid_tuple = ("invalid", "//*[@text='OK']")
        with pytest.raises(ConversionError):
            self.converter.to_dict(invalid_tuple)

    def test_roundtrip_conversions(self):
        """Test roundtrip conversions to ensure consistency."""
        original_dict = {
            DictAttribute.TEXT: "Test Button",
            DictAttribute.CLICKABLE: True,
            DictAttribute.CLASS_NAME: "android.widget.Button"
        }
        
        # Dict -> XPath -> Dict
        xpath_tuple = self.converter.to_xpath(original_dict)
        dict_from_xpath = self.converter.to_dict(xpath_tuple)
        assert dict_from_xpath == original_dict
        
        # Dict -> UiSelector -> Dict
        ui_selector = self.converter.to_uiselector(original_dict)
        dict_from_ui = self.converter.to_dict(ui_selector)
        assert dict_from_ui == original_dict
        
        # XPath -> UiSelector -> XPath
        ui_from_xpath = self.converter.to_uiselector(xpath_tuple)
        xpath_from_ui = self.converter.to_xpath(ui_from_xpath)
        assert xpath_from_ui == xpath_tuple

    def test_complex_selector_conversion(self):
        """Test conversion of complex selectors with hierarchical relationships."""
        complex_dict = {
            DictAttribute.CLASS_NAME: "android.widget.LinearLayout",
            DictAttribute.CHILD_SELECTOR: {
                DictAttribute.TEXT: "OK",
                DictAttribute.CLICKABLE: True
            }
        }
        
        # Convert to all formats
        xpath_tuple = self.converter.to_xpath(complex_dict)
        ui_selector = self.converter.to_uiselector(complex_dict)
        
        # Verify XPath contains hierarchical structure
        assert "LinearLayout" in xpath_tuple[1]
        assert "OK" in xpath_tuple[1]
        
        # Verify UiSelector contains hierarchical structure
        assert "LinearLayout" in ui_selector
        assert "OK" in ui_selector
        assert "childSelector" in ui_selector

    def test_unicode_and_special_characters(self):
        """Test conversion with unicode and special characters."""
        unicode_dict = {
            DictAttribute.TEXT: "Привет мир! 🌍",
            DictAttribute.DESCRIPTION: "Special chars: @#$%^&*()"
        }
        
        xpath_tuple = self.converter.to_xpath(unicode_dict)
        ui_selector = self.converter.to_uiselector(unicode_dict)
        
        assert "Привет мир! 🌍" in xpath_tuple[1]
        assert "Привет мир! 🌍" in ui_selector
        assert "Special chars: @#$%^&*()" in xpath_tuple[1]
        assert "Special chars: @#$%^&*()" in ui_selector
