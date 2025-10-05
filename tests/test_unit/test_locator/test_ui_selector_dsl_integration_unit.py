# ruff: noqa
# pyright: ignore
"""
Tests for UiSelector DSL integration with LocatorConverter.

This module tests the integration between the new UiSelector DSL and the
unified LocatorConverter to ensure seamless conversion between all formats.
"""
# ruff: noqa: S101

import logging

import pytest

from shadowstep.locator.converter.locator_converter import LocatorConverter
from shadowstep.locator.ui_selector import UiSelector

logger = logging.getLogger(__name__)


class TestUiSelectorDSLIntegration:
    """Test cases for UiSelector DSL integration with LocatorConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = LocatorConverter()

    @pytest.mark.unit
    def test_ui_selector_to_dict_conversion(self):
        """Test conversion from UiSelector DSL to dictionary."""
        selector = UiSelector().text("OK").clickable(True)
        result = self.converter.to_dict(selector)
        expected = {"text": "OK", "clickable": True}
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_ui_selector_to_xpath_conversion(self):
        """Test conversion from UiSelector DSL to XPath."""
        selector = UiSelector().text("OK").clickable(True)
        result = self.converter.to_xpath(selector)
        expected = ("xpath", "//*[@text='OK'][@clickable='true']")
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_ui_selector_to_uiselector_conversion(self):
        """Test conversion from UiSelector DSL to UiSelector string."""
        selector = UiSelector().text("OK").clickable(True)
        result = self.converter.to_uiselector(selector)
        expected = 'new UiSelector().text("OK").clickable(true);'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_ui_selector_hierarchical_to_dict(self):
        """Test conversion of hierarchical UiSelector to dictionary."""
        child = UiSelector().text("Item")
        selector = UiSelector().className("android.widget.LinearLayout").childSelector(child)
        result = self.converter.to_dict(selector)
        expected = {
            "class": "android.widget.LinearLayout",
            "childSelector": {
                "text": "Item"
            }
        }
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_ui_selector_hierarchical_to_xpath(self):
        """Test conversion of hierarchical UiSelector to XPath."""
        child = UiSelector().text("Item")
        selector = UiSelector().className("android.widget.LinearLayout").childSelector(child)
        result = self.converter.to_xpath(selector)
        expected = ("xpath", "//*[@class='android.widget.LinearLayout']//*[@text='Item']")
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_ui_selector_hierarchical_to_uiselector(self):
        """Test conversion of hierarchical UiSelector to UiSelector string."""
        child = UiSelector().text("Item")
        selector = UiSelector().className("android.widget.LinearLayout").childSelector(child)
        result = self.converter.to_uiselector(selector)
        expected = 'new UiSelector().className("android.widget.LinearLayout").childSelector(new UiSelector().text("Item"));'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_ui_selector_validation(self):
        """Test validation of UiSelector DSL."""
        # Valid selector
        valid_selector = UiSelector().text("OK").clickable(True)
        self.converter.validate_selector(valid_selector)  # Should not raise
        
        # Invalid selector (empty)
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepEmptySelectorError
        
        empty_selector = UiSelector()
        with pytest.raises(ShadowstepEmptySelectorError):
            self.converter.validate_selector(empty_selector)

    @pytest.mark.unit
    def test_roundtrip_conversion_ui_selector_to_dict_and_back(self):
        """Test roundtrip conversion: UiSelector -> dict -> UiSelector."""
        original = UiSelector().text("OK").clickable(True)
        
        # Convert to dict
        selector_dict = self.converter.to_dict(original)
        
        # Convert back to UiSelector
        restored = UiSelector.from_dict(selector_dict)
        
        # Should be equivalent
        assert str(original) == str(restored)  # noqa: S101

    @pytest.mark.unit
    def test_roundtrip_conversion_ui_selector_to_xpath_and_back(self):
        """Test roundtrip conversion: UiSelector -> XPath -> dict -> UiSelector."""
        original = UiSelector().text("OK").clickable(True)
        
        # Convert to XPath
        xpath_tuple = self.converter.to_xpath(original)
        
        # Convert back to dict
        selector_dict = self.converter.to_dict(xpath_tuple)
        
        # Convert back to UiSelector
        restored = UiSelector.from_dict(selector_dict)
        
        # Should be equivalent
        assert str(original) == str(restored)  # noqa: S101

    @pytest.mark.unit
    def test_roundtrip_conversion_ui_selector_to_uiselector_string_and_back(self):
        """Test roundtrip conversion: UiSelector -> string -> dict -> UiSelector."""
        original = UiSelector().text("OK").clickable(True)
        
        # Convert to UiSelector string
        uiselector_string = self.converter.to_uiselector(original)
        
        # Convert back to dict
        selector_dict = self.converter.to_dict(uiselector_string)
        
        # Convert back to UiSelector
        restored = UiSelector.from_dict(selector_dict)
        
        # Should be equivalent
        assert str(original) == str(restored)  # noqa: S101

    @pytest.mark.unit
    def test_complex_ui_selector_conversion(self):
        """Test conversion of complex UiSelector with multiple attributes."""
        child = UiSelector().text("Menu")
        parent = UiSelector().className("android.widget.LinearLayout").childSelector(child)
        selector = (UiSelector()
                   .text("Settings")
                   .clickable(True)
                   .fromParent(parent))
        
        # Test all conversion directions
        selector_dict = self.converter.to_dict(selector)
        xpath_tuple = self.converter.to_xpath(selector)
        uiselector_string = self.converter.to_uiselector(selector)
        
        # Verify conversions
        assert "text" in selector_dict  # noqa: S101
        assert "clickable" in selector_dict  # noqa: S101
        assert "fromParent" in selector_dict  # noqa: S101
        assert xpath_tuple[0] == "xpath"  # noqa: S101
        assert uiselector_string.startswith("new UiSelector()")  # noqa: S101

    @pytest.mark.unit
    def test_ui_selector_with_all_attribute_types(self):
        """Test UiSelector with all types of attributes."""
        selector = (UiSelector()
                   .text("Submit")
                   .description("Submit button")
                   .resourceId("com.example:id/button")
                   .packageName("com.example.app")
                   .className("android.widget.Button")
                   .checkable(True)
                   .checked(False)
                   .clickable(True)
                   .enabled(False)
                   .focusable(True)
                   .focused(False)
                   .longClickable(True)
                   .scrollable(False)
                   .selected(True)
                   .password(False)
                   .index(1)
                   .instance(2))
        
        # Test conversion to all formats
        selector_dict = self.converter.to_dict(selector)
        xpath_tuple = self.converter.to_xpath(selector)
        uiselector_string = self.converter.to_uiselector(selector)
        
        # Verify all attributes are present in dict
        expected_attributes = [
            "text", "content-desc", "resource-id", "package", "class",
            "checkable", "checked", "clickable", "enabled", "focusable", "focused",
            "long-clickable", "scrollable", "selected", "password",
            "index", "instance"
        ]
        
        for attr in expected_attributes:
            assert attr in selector_dict  # noqa: S101
        
        # Verify other conversions work
        assert xpath_tuple[0] == "xpath"  # noqa: S101
        assert uiselector_string.startswith("new UiSelector()")  # noqa: S101

    @pytest.mark.unit
    def test_ui_selector_unicode_support(self):
        """Test UiSelector with unicode characters."""
        selector = UiSelector().text("Hello world! 🌍").description("Special chars: @#$%^&*()")
        
        # Test all conversions
        selector_dict = self.converter.to_dict(selector)
        self.converter.to_xpath(selector)  # Test conversion
        uiselector_string = self.converter.to_uiselector(selector)
        
        # Verify unicode is preserved
        assert selector_dict["text"] == "Hello world! 🌍"  # noqa: S101
        assert selector_dict["content-desc"] == "Special chars: @#$%^&*()"  # noqa: S101
        assert "Hello world! 🌍" in uiselector_string  # noqa: S101

    @pytest.mark.unit
    def test_ui_selector_regex_patterns(self):
        """Test UiSelector with regex patterns."""
        selector = (UiSelector()
                   .textMatches("^[A-Z][a-z]+\\s+\\d{2,4}$")
                   .resourceIdMatches("com\\.example\\..*\\.id\\..*")
                   .classNameMatches(".*Button.*|.*TextView.*"))
        
        # Test conversions
        selector_dict = self.converter.to_dict(selector)
        xpath_tuple = self.converter.to_xpath(selector)
        uiselector_string = self.converter.to_uiselector(selector)
        
        # Verify regex patterns are preserved
        assert selector_dict["textMatches"] == "^[A-Z][a-z]+\\s+\\d{2,4}$"  # noqa: S101
        assert selector_dict["resource-idMatches"] == "com\\.example\\..*\\.id\\..*"  # noqa: S101
        assert selector_dict["classMatches"] == ".*Button.*|.*TextView.*"  # noqa: S101
        
        # Verify other conversions work
        assert xpath_tuple[0] == "xpath"  # noqa: S101
        assert uiselector_string.startswith("new UiSelector()")  # noqa: S101

    @pytest.mark.unit
    def test_ui_selector_performance(self):
        """Test performance of UiSelector conversions."""
        import time
        
        # Create a complex selector
        child = UiSelector().text("Item").clickable(True)
        parent = UiSelector().className("android.widget.LinearLayout").childSelector(child)
        selector = (UiSelector()
                   .text("Settings")
                   .clickable(True)
                   .fromParent(parent))
        
        # Measure conversion time
        start_time = time.time()
        for _ in range(1000):
            self.converter.to_dict(selector)
            self.converter.to_xpath(selector)
            self.converter.to_uiselector(selector)
        end_time = time.time()
        
        # Should complete in reasonable time (less than 5 seconds for 1000 iterations)
        assert (end_time - start_time) < 5.0  # noqa: S101

    @pytest.mark.unit
    def test_ui_selector_edge_cases(self):
        """Test UiSelector edge cases."""
        # Empty selector - should return empty dict
        empty_selector = UiSelector()
        empty_dict = self.converter.to_dict(empty_selector)
        assert empty_dict == {}  # noqa: S101   # type: ignore
        
        # Selector with only boolean attributes
        bool_selector = UiSelector().clickable(True).enabled(False)
        bool_dict = self.converter.to_dict(bool_selector)
        assert bool_dict == {"clickable": True, "enabled": False}  # noqa: S101
        
        # Selector with only numeric attributes
        numeric_selector = UiSelector().index(1).instance(2)
        numeric_dict = self.converter.to_dict(numeric_selector)
        assert numeric_dict == {"index": 1, "instance": 2}  # noqa: S101
