"""Integration tests for XPathConverter class.

This module tests the XPathConverter functionality using real Android device
connections through the app fixture.
"""
import pytest

from shadowstep.locator.converter.xpath_converter import XPathConverter
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def converter():
    """Fixture providing XPathConverter instance."""
    return XPathConverter()


class TestXPathToDict:
    """Tests for xpath_to_dict method."""

    def test_xpath_to_dict_simple_text(self, app: Shadowstep, converter: XPathConverter):
        """Test converting simple text xpath to dict."""
        xpath = "//*[@text='Settings']"
        result = converter.xpath_to_dict(xpath)

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"

        # Verify dict works with real app
        element = app.get_element(result)
        assert element is not None

    def test_xpath_to_dict_clickable(self, app: Shadowstep, converter: XPathConverter):
        """Test converting clickable xpath to dict."""
        xpath = "//*[@clickable='true']"
        result = converter.xpath_to_dict(xpath)

        assert isinstance(result, dict)
        assert "clickable" in result
        assert result["clickable"] is True

    def test_xpath_to_dict_resource_id(self, app: Shadowstep, converter: XPathConverter):
        """Test converting resource-id xpath to dict."""
        xpath = "//*[@resource-id='android:id/title']"
        result = converter.xpath_to_dict(xpath)

        assert isinstance(result, dict)
        assert "resource-id" in result
        assert result["resource-id"] == "android:id/title"

    def test_xpath_to_dict_multiple_attributes(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with multiple attributes to dict."""
        xpath = "//*[@text='Settings'][@clickable='true']"
        result = converter.xpath_to_dict(xpath)

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"
        assert "clickable" in result
        assert result["clickable"] is True

    def test_xpath_to_dict_contains(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with contains() to dict."""
        xpath = "//*[contains(@text,'Sett')]"
        result = converter.xpath_to_dict(xpath)

        assert isinstance(result, dict)
        assert "textContains" in result
        assert result["textContains"] == "Sett"

    def test_xpath_to_dict_starts_with(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with starts-with() to dict."""
        xpath = "//*[starts-with(@text,'Sett')]"
        result = converter.xpath_to_dict(xpath)

        assert isinstance(result, dict)
        assert "textStartsWith" in result
        assert result["textStartsWith"] == "Sett"

    def test_xpath_to_dict_class_name(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with class attribute to dict."""
        xpath = "//*[@class='android.widget.TextView']"
        result = converter.xpath_to_dict(xpath)

        assert isinstance(result, dict)
        assert "class" in result
        assert result["class"] == "android.widget.TextView"

    def test_xpath_to_dict_with_index(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with positional index to dict."""
        xpath = "//*[@text='Settings'][1]"
        result = converter.xpath_to_dict(xpath)

        assert isinstance(result, dict)
        assert "text" in result
        assert "instance" in result
        assert result["instance"] == 0  # XPath uses 1-based, dict uses 0-based

    def test_xpath_to_dict_boolean_false(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with false boolean to dict."""
        xpath = "//*[@enabled='false']"
        result = converter.xpath_to_dict(xpath)

        assert isinstance(result, dict)
        assert "enabled" in result
        assert result["enabled"] is False


class TestXPathToUiSelector:
    """Tests for xpath_to_ui_selector method."""

    def test_xpath_to_uiselector_simple_text(self, app: Shadowstep, converter: XPathConverter):
        """Test converting simple text xpath to UiSelector."""
        xpath = "//*[@text='Settings']"
        result = converter.xpath_to_ui_selector(xpath)

        assert isinstance(result, str)
        assert result.startswith("new UiSelector()")
        assert '.text("Settings")' in result
        assert result.endswith(";")

        # Verify UiSelector works with real app
        element = app.get_element(result)
        assert element is not None

    def test_xpath_to_uiselector_clickable(self, app: Shadowstep, converter: XPathConverter):
        """Test converting clickable xpath to UiSelector."""
        xpath = "//*[@clickable='true']"
        result = converter.xpath_to_ui_selector(xpath)

        assert isinstance(result, str)
        assert ".clickable(true)" in result

    def test_xpath_to_uiselector_resource_id(self, app: Shadowstep, converter: XPathConverter):
        """Test converting resource-id xpath to UiSelector."""
        xpath = "//*[@resource-id='android:id/title']"
        result = converter.xpath_to_ui_selector(xpath)

        assert isinstance(result, str)
        assert '.resourceId("android:id/title")' in result

    def test_xpath_to_uiselector_multiple_attributes(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with multiple attributes to UiSelector."""
        xpath = "//*[@text='Settings'][@clickable='true']"
        result = converter.xpath_to_ui_selector(xpath)

        assert isinstance(result, str)
        assert '.text("Settings")' in result
        assert ".clickable(true)" in result

    def test_xpath_to_uiselector_contains(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with contains() to UiSelector."""
        xpath = "//*[contains(@text,'Sett')]"
        result = converter.xpath_to_ui_selector(xpath)

        assert isinstance(result, str)
        assert '.textContains("Sett")' in result

    def test_xpath_to_uiselector_starts_with(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with starts-with() to UiSelector."""
        xpath = "//*[starts-with(@text,'Sett')]"
        result = converter.xpath_to_ui_selector(xpath)

        assert isinstance(result, str)
        assert '.textStartsWith("Sett")' in result

    def test_xpath_to_uiselector_class_name(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with class attribute to UiSelector."""
        xpath = "//*[@class='android.widget.TextView']"
        result = converter.xpath_to_ui_selector(xpath)

        assert isinstance(result, str)
        assert '.className("android.widget.TextView")' in result

    def test_xpath_to_uiselector_with_index(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with positional index to UiSelector."""
        xpath = "//*[@text='Settings'][1]"
        result = converter.xpath_to_ui_selector(xpath)

        assert isinstance(result, str)
        assert '.text("Settings")' in result
        assert ".instance(0)" in result  # XPath uses 1-based, UiSelector uses 0-based

    def test_xpath_to_uiselector_boolean_false(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath with false boolean to UiSelector."""
        xpath = "//*[@enabled='false']"
        result = converter.xpath_to_ui_selector(xpath)

        assert isinstance(result, str)
        assert ".enabled(false)" in result


class TestXPathConverterWithRealApp:
    """Integration tests using real app elements."""

    def test_conversion_round_trip_dict(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath -> dict and verifying with real app."""
        xpath = "//*[@text='Settings']"

        # Convert to dict
        dict_result = converter.xpath_to_dict(xpath)

        # Use with real app
        element = app.get_element(dict_result)
        assert element is not None

    def test_conversion_round_trip_uiselector(self, app: Shadowstep, converter: XPathConverter):
        """Test converting xpath -> uiselector and verifying with real app."""
        xpath = "//*[@text='Settings']"

        # Convert to UiSelector
        uiselector_result = converter.xpath_to_ui_selector(xpath)

        # Use with real app
        element = app.get_element(uiselector_result)
        assert element is not None

    def test_complex_xpath_with_app(self, app: Shadowstep, converter: XPathConverter):
        """Test complex xpath with multiple attributes."""
        xpath = "//*[@text='Settings'][@clickable='true'][@class='android.widget.TextView']"

        # Convert to dict
        dict_result = converter.xpath_to_dict(xpath)
        element1 = app.get_element(dict_result)

        # Convert to UiSelector
        uiselector_result = converter.xpath_to_ui_selector(xpath)
        element2 = app.get_element(uiselector_result)

        # Both should find the same element
        assert element1 is not None
        assert element2 is not None

    def test_contains_xpath_with_app(self, app: Shadowstep, converter: XPathConverter):
        """Test xpath with contains() function with real app."""
        xpath = "//*[contains(@text,'Sett')]"

        # Convert to dict
        dict_result = converter.xpath_to_dict(xpath)
        element = app.get_element(dict_result)

        assert element is not None

    def test_conversion_preserves_attributes(self, app: Shadowstep, converter: XPathConverter):
        """Test that conversion preserves all attributes."""
        xpath = "//*[@text='Settings'][@clickable='true']"

        # Convert to dict
        dict_result = converter.xpath_to_dict(xpath)

        # Verify all attributes are preserved
        assert "text" in dict_result
        assert dict_result["text"] == "Settings"
        assert "clickable" in dict_result
        assert dict_result["clickable"] is True

    def test_xpath_validation_with_invalid_xpath(self, app: Shadowstep, converter: XPathConverter):
        """Test that invalid xpath raises appropriate error."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepInvalidXPathError

        invalid_xpath = "//[invalid"
        with pytest.raises(ShadowstepInvalidXPathError):
            converter.xpath_to_dict(invalid_xpath)

    def test_xpath_with_logical_operators_raises_error(self, app: Shadowstep, converter: XPathConverter):
        """Test that xpath with logical operators raises error."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepLogicalOperatorsNotSupportedError

        xpath_with_and = "//*[@text='Settings' and @clickable='true']"
        with pytest.raises(ShadowstepLogicalOperatorsNotSupportedError):
            converter.xpath_to_dict(xpath_with_and)

        xpath_with_or = "//*[@text='Settings' or @clickable='true']"
        with pytest.raises(ShadowstepLogicalOperatorsNotSupportedError):
            converter.xpath_to_dict(xpath_with_or)
