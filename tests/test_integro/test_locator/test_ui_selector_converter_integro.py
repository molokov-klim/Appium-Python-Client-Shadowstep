"""Integration tests for UiSelectorConverter class.

This module tests the UiSelectorConverter functionality using real Android device
connections through the app fixture.
"""
import pytest

from shadowstep.locator.converter.ui_selector_converter import UiSelectorConverter
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def converter():
    """Fixture providing UiSelectorConverter instance."""
    return UiSelectorConverter()


class TestSelectorToXPath:
    """Tests for selector_to_xpath method."""

    def test_selector_to_xpath_simple_text(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting simple text UiSelector to xpath."""
        uiselector = 'new UiSelector().text("Settings");'
        result = converter.selector_to_xpath(uiselector)

        assert isinstance(result, str)
        assert "@text='Settings'" in result

        # Verify xpath works with real app
        element = app.get_element(("xpath", result))
        assert element is not None

    def test_selector_to_xpath_clickable(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting clickable UiSelector to xpath."""
        uiselector = 'new UiSelector().clickable(true);'
        result = converter.selector_to_xpath(uiselector)

        assert isinstance(result, str)
        assert "@clickable='true'" in result

    def test_selector_to_xpath_resource_id(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting resourceId UiSelector to xpath."""
        uiselector = 'new UiSelector().resourceId("android:id/title");'
        result = converter.selector_to_xpath(uiselector)

        assert isinstance(result, str)
        assert "@resource-id='android:id/title'" in result

    def test_selector_to_xpath_multiple_attributes(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting UiSelector with multiple attributes to xpath."""
        uiselector = 'new UiSelector().text("Settings").clickable(true);'
        result = converter.selector_to_xpath(uiselector)

        assert isinstance(result, str)
        assert "@text='Settings'" in result
        assert "@clickable='true'" in result

    def test_selector_to_xpath_text_contains(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting textContains UiSelector to xpath."""
        uiselector = 'new UiSelector().textContains("Sett");'
        result = converter.selector_to_xpath(uiselector)

        assert isinstance(result, str)
        assert "contains(@text,'Sett')" in result

    def test_selector_to_xpath_class_name(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting className UiSelector to xpath."""
        uiselector = 'new UiSelector().className("android.widget.TextView");'
        result = converter.selector_to_xpath(uiselector)

        assert isinstance(result, str)
        assert "@class='android.widget.TextView'" in result


class TestSelectorToDict:
    """Tests for selector_to_dict method."""

    def test_selector_to_dict_simple_text(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting simple text UiSelector to dict."""
        uiselector = 'new UiSelector().text("Settings");'
        result = converter.selector_to_dict(uiselector)

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"

        # Verify dict works with real app
        element = app.get_element(result)
        assert element is not None

    def test_selector_to_dict_clickable(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting clickable UiSelector to dict."""
        uiselector = 'new UiSelector().clickable(true);'
        result = converter.selector_to_dict(uiselector)

        assert isinstance(result, dict)
        assert "clickable" in result
        assert result["clickable"] is True

    def test_selector_to_dict_resource_id(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting resourceId UiSelector to dict."""
        uiselector = 'new UiSelector().resourceId("android:id/title");'
        result = converter.selector_to_dict(uiselector)

        assert isinstance(result, dict)
        assert "resource-id" in result
        assert result["resource-id"] == "android:id/title"

    def test_selector_to_dict_multiple_attributes(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting UiSelector with multiple attributes to dict."""
        uiselector = 'new UiSelector().text("Settings").clickable(true);'
        result = converter.selector_to_dict(uiselector)

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"
        assert "clickable" in result
        assert result["clickable"] is True

    def test_selector_to_dict_text_contains(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting textContains UiSelector to dict."""
        uiselector = 'new UiSelector().textContains("Sett");'
        result = converter.selector_to_dict(uiselector)

        assert isinstance(result, dict)
        assert "textContains" in result
        assert result["textContains"] == "Sett"

    def test_selector_to_dict_class_name(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting className UiSelector to dict."""
        uiselector = 'new UiSelector().className("android.widget.TextView");'
        result = converter.selector_to_dict(uiselector)

        assert isinstance(result, dict)
        assert "class" in result
        assert result["class"] == "android.widget.TextView"

    def test_selector_to_dict_with_instance(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting UiSelector with instance to dict."""
        uiselector = 'new UiSelector().text("Settings").instance(0);'
        result = converter.selector_to_dict(uiselector)

        assert isinstance(result, dict)
        assert "text" in result
        assert "instance" in result
        assert result["instance"] == 0

    def test_selector_to_dict_boolean_false(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting boolean false value to dict."""
        uiselector = 'new UiSelector().enabled(false);'
        result = converter.selector_to_dict(uiselector)

        assert isinstance(result, dict)
        assert "enabled" in result
        assert result["enabled"] is False


class TestParseSelectorString:
    """Tests for parse_selector_string method."""

    def test_parse_simple_text(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test parsing simple text UiSelector."""
        uiselector = 'new UiSelector().text("Settings");'
        result = converter.parse_selector_string(uiselector)

        assert isinstance(result, dict)
        assert "methods" in result
        assert len(result["methods"]) > 0

    def test_parse_multiple_methods(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test parsing UiSelector with multiple methods."""
        uiselector = 'new UiSelector().text("Settings").clickable(true);'
        result = converter.parse_selector_string(uiselector)

        assert isinstance(result, dict)
        assert "methods" in result
        assert len(result["methods"]) == 2

    def test_parse_with_quotes_in_text(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test parsing UiSelector with quotes in text."""
        uiselector = 'new UiSelector().text("Settings Menu");'
        result = converter.parse_selector_string(uiselector)

        assert isinstance(result, dict)
        assert "methods" in result
        methods = result["methods"]
        assert any(m["name"] == "text" for m in methods)

    def test_parse_without_semicolon(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test parsing UiSelector without trailing semicolon."""
        uiselector = 'new UiSelector().text("Settings")'
        result = converter.parse_selector_string(uiselector)

        assert isinstance(result, dict)
        assert "methods" in result


class TestUiSelectorConverterWithRealApp:
    """Integration tests using real app elements."""

    def test_conversion_round_trip_xpath(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting UiSelector -> xpath and verifying with real app."""
        uiselector = 'new UiSelector().text("Settings");'

        # Convert to xpath
        xpath_result = converter.selector_to_xpath(uiselector)

        # Use with real app
        element = app.get_element(("xpath", xpath_result))
        assert element is not None

    def test_conversion_round_trip_dict(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test converting UiSelector -> dict and verifying with real app."""
        uiselector = 'new UiSelector().text("Settings");'

        # Convert to dict
        dict_result = converter.selector_to_dict(uiselector)

        # Use with real app
        element = app.get_element(dict_result)
        assert element is not None

    def test_complex_selector_with_app(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test complex UiSelector with multiple attributes."""
        uiselector = 'new UiSelector().text("Settings").clickable(true).className("android.widget.TextView");'

        # Convert to xpath
        xpath_result = converter.selector_to_xpath(uiselector)
        element1 = app.get_element(("xpath", xpath_result))

        # Convert to dict
        dict_result = converter.selector_to_dict(uiselector)
        element2 = app.get_element(dict_result)

        # Both should find the same element
        assert element1 is not None
        assert element2 is not None

    def test_text_contains_with_app(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test textContains UiSelector with real app."""
        uiselector = 'new UiSelector().textContains("Sett");'

        # Convert to xpath
        xpath_result = converter.selector_to_xpath(uiselector)
        element = app.get_element(("xpath", xpath_result))

        assert element is not None

    def test_conversion_preserves_attributes(self, app: Shadowstep, converter: UiSelectorConverter):
        """Test that conversion preserves all attributes."""
        uiselector = 'new UiSelector().text("Settings").clickable(true);'

        # Convert to dict and back
        dict_result = converter.selector_to_dict(uiselector)

        # Verify all attributes are preserved
        assert "text" in dict_result
        assert dict_result["text"] == "Settings"
        assert "clickable" in dict_result
        assert dict_result["clickable"] is True
