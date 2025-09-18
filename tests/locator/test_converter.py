# tests/test_converter.py
"""
Tests for the unified LocatorConverter.

This module tests the new LocatorConverter that replaces the deprecated
DeprecatedLocatorConverter with a modern, well-architected solution.
"""

import logging
from typing import Any

import pytest

from shadowstep.locator.converter.locator_converter import LocatorConverter

logger = logging.getLogger(__name__)


class TestUnifiedLocatorConverter:
    """Test cases for the unified LocatorConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = LocatorConverter()

    def test_to_dict_from_dict(self):
        """Test converting dict to dict (should return unchanged)."""
        selector_dict: dict[str, Any] = {"text": "OK"}
        result = self.converter.to_dict(selector_dict)
        assert result == selector_dict  # noqa: S101

    def test_to_dict_from_xpath_tuple(self):
        """Test converting XPath tuple to dict."""
        xpath_tuple = ("xpath", "//*[@text='OK']")
        result = self.converter.to_dict(xpath_tuple)
        assert "text" in result  # noqa: S101
        assert result["text"] == "OK"  # noqa: S101

    def test_to_dict_from_xpath_string(self):
        """Test converting XPath string to dict."""
        xpath_string = "//*[@text='OK']"
        result = self.converter.to_dict(xpath_string)
        assert "text" in result  # noqa: S101
        assert result["text"] == "OK"  # noqa: S101

    def test_to_dict_from_uiselector_string(self):
        """Test converting UiSelector string to dict."""
        ui_string = 'new UiSelector().text("OK");'
        result = self.converter.to_dict(ui_string)
        assert "text" in result  # noqa: S101
        assert result["text"] == "OK"  # noqa: S101

    def test_to_xpath_from_dict(self):
        """Test converting dict to XPath tuple."""
        selector_dict: dict[str, Any] = {"text": "OK"}
        result = self.converter.to_xpath(selector_dict)
        assert result[0] == "xpath"  # noqa: S101
        assert "text='OK'" in result[1]  # noqa: S101

    def test_to_xpath_from_xpath_tuple(self):
        """Test converting XPath tuple to XPath tuple (should return unchanged)."""
        xpath_tuple = ("xpath", "//*[@text='OK']")
        result = self.converter.to_xpath(xpath_tuple)
        assert result == xpath_tuple  # noqa: S101

    def test_to_xpath_from_xpath_string(self):
        """Test converting XPath string to XPath tuple."""
        xpath_string = "//*[@text='OK']"
        result = self.converter.to_xpath(xpath_string)
        assert result[0] == "xpath"  # noqa: S101
        assert result[1] == xpath_string  # noqa: S101

    def test_to_xpath_from_uiselector_string(self):
        """Test converting UiSelector string to XPath tuple."""
        ui_string = 'new UiSelector().text("OK");'
        result = self.converter.to_xpath(ui_string)
        assert result[0] == "xpath"  # noqa: S101
        assert "text='OK'" in result[1]  # noqa: S101

    def test_to_uiselector_from_dict(self):
        """Test converting dict to UiSelector string."""
        selector_dict: dict[str, Any] = {"text": "OK"}
        result = self.converter.to_uiselector(selector_dict)
        assert result.startswith("new UiSelector()")  # noqa: S101
        assert 'text("OK")' in result  # noqa: S101

    def test_to_uiselector_from_xpath_tuple(self):
        """Test converting XPath tuple to UiSelector string."""
        xpath_tuple = ("xpath", "//*[@text='OK']")
        result = self.converter.to_uiselector(xpath_tuple)
        assert result.startswith("new UiSelector()")  # noqa: S101
        assert 'text("OK")' in result  # noqa: S101

    def test_to_uiselector_from_xpath_string(self):
        """Test converting XPath string to UiSelector string."""
        xpath_string = "//*[@text='OK']"
        result = self.converter.to_uiselector(xpath_string)
        assert result.startswith("new UiSelector()")  # noqa: S101
        assert 'text("OK")' in result  # noqa: S101

    def test_to_uiselector_from_uiselector_string(self):
        """Test converting UiSelector string to UiSelector string (should return unchanged)."""
        ui_string = 'new UiSelector().text("OK");'
        result = self.converter.to_uiselector(ui_string)
        assert result == ui_string  # noqa: S101

    def test_direct_conversion_methods(self):
        """Test direct conversion methods between specific formats."""
        selector_dict: dict[str, Any] = {"text": "OK", "clickable": True}
        
        # Dict to XPath
        xpath = self.converter.dict_to_xpath(selector_dict)
        assert "text='OK'" in xpath  # noqa: S101
        assert "clickable='true'" in xpath  # noqa: S101
        
        # Dict to UiSelector
        ui_selector = self.converter.dict_to_uiselector(selector_dict)
        assert 'text("OK")' in ui_selector  # noqa: S101
        assert "clickable(true)" in ui_selector  # noqa: S101
        
        # XPath to Dict
        dict_from_xpath = self.converter.xpath_to_dict(xpath)
        assert "text" in dict_from_xpath  # noqa: S101
        assert "clickable" in dict_from_xpath  # noqa: S101
        
        # XPath to UiSelector
        ui_from_xpath = self.converter.xpath_to_uiselector(xpath)
        assert 'text("OK")' in ui_from_xpath  # noqa: S101
        assert "clickable(true)" in ui_from_xpath  # noqa: S101
        
        # UiSelector to Dict
        dict_from_ui = self.converter.uiselector_to_dict(ui_selector)
        assert "text" in dict_from_ui  # noqa: S101
        assert "clickable" in dict_from_ui  # noqa: S101
        
        # UiSelector to XPath
        xpath_from_ui = self.converter.uiselector_to_xpath(ui_selector)
        assert "text='OK'" in xpath_from_ui  # noqa: S101
        assert "clickable='true'" in xpath_from_ui  # noqa: S101

    def test_validate_selector_valid_dict(self):
        """Test validation of valid dictionary selector."""
        selector_dict: dict[str, Any] = {"text": "OK"}
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
            self.converter.validate_selector(123)  # type: ignore

    def test_roundtrip_conversions(self):
        """Test roundtrip conversions to ensure consistency."""
        original_dict: dict[str, Any] = {
            "text": "Test Button",
            "clickable": True,
            "class": "android.widget.Button"
        }
        
        # Dict -> XPath -> Dict
        xpath_tuple = self.converter.to_xpath(original_dict)
        dict_from_xpath = self.converter.to_dict(xpath_tuple)
        assert dict_from_xpath == original_dict  # noqa: S101
        
        # Dict -> UiSelector -> Dict
        ui_selector = self.converter.to_uiselector(original_dict)
        dict_from_ui = self.converter.to_dict(ui_selector)
        assert dict_from_ui == original_dict  # noqa: S101
        
        # XPath -> UiSelector -> XPath
        ui_from_xpath = self.converter.to_uiselector(xpath_tuple)
        xpath_from_ui = self.converter.to_xpath(ui_from_xpath)
        assert xpath_from_ui == xpath_tuple  # noqa: S101

    def test_complex_selector_conversion(self):
        """Test conversion of complex selectors with hierarchical relationships."""
        complex_dict: dict[str, Any] = {
            "class": "android.widget.LinearLayout",
            "childSelector": {
                "text": "OK",
                "clickable": True
            }
        }
        
        # Convert to all formats
        xpath_tuple = self.converter.to_xpath(complex_dict)
        ui_selector = self.converter.to_uiselector(complex_dict)
        
        # Verify XPath contains hierarchical structure
        assert "LinearLayout" in xpath_tuple[1]  # noqa: S101
        assert "OK" in xpath_tuple[1]  # noqa: S101
        
        # Verify UiSelector contains hierarchical structure
        assert "LinearLayout" in ui_selector  # noqa: S101
        assert "OK" in ui_selector  # noqa: S101
        assert "childSelector" in ui_selector  # noqa: S101

    def test_unicode_and_special_characters(self):
        """Test conversion with unicode and special characters."""
        unicode_dict: dict[str, Any] = {
            "text": "Привет мир! 🌍",
            "content-desc": "Special chars: @#$%^&*()"
        }
        
        xpath_tuple = self.converter.to_xpath(unicode_dict)
        ui_selector = self.converter.to_uiselector(unicode_dict)
        
        assert "Привет мир! 🌍" in xpath_tuple[1]  # noqa: S101
        assert "Привет мир! 🌍" in ui_selector  # noqa: S101
        assert "Special chars: @#$%^&*()" in xpath_tuple[1]  # noqa: S101
        assert "Special chars: @#$%^&*()" in ui_selector  # noqa: S101
