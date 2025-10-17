"""Integration tests for LocatorConverter class.

This module tests the LocatorConverter functionality using real Android device
connections through the app fixture.
"""
import pytest

from shadowstep.locator.converter.locator_converter import LocatorConverter
from shadowstep.locator.ui_selector import UiSelector
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def converter():
    """Fixture providing LocatorConverter instance."""
    return LocatorConverter()


class TestLocatorConverterToDict:
    """Tests for to_dict method."""

    def test_to_dict_from_dict(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting dictionary to dictionary (should return same dict)."""
        selector_dict = {"text": "Settings"}
        result = converter.to_dict(selector_dict)
        assert result == selector_dict

        # Verify it can be used with real app
        element = app.get_element(result)
        assert element is not None

    def test_to_dict_from_xpath_tuple(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting xpath tuple to dictionary."""
        xpath_tuple = ("xpath", "//*[@text='Settings']")
        result = converter.to_dict(xpath_tuple)

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"

        # Verify it can be used with real app
        element = app.get_element(result)
        assert element is not None

    def test_to_dict_from_xpath_string(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting xpath string to dictionary."""
        xpath_str = "//*[@text='Settings']"
        result = converter.to_dict(xpath_str)

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"

    def test_to_dict_from_uiselector_string(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting UiSelector string to dictionary."""
        uiselector_str = 'new UiSelector().text("Settings");'
        result = converter.to_dict(uiselector_str)

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"

    def test_to_dict_from_uiselector_object(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting UiSelector object to dictionary."""
        uiselector = UiSelector().text("Settings")
        result = converter.to_dict(uiselector)

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"

    def test_to_dict_complex_selector(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting complex selector to dictionary."""
        selector = {"text": "Settings", "clickable": True}
        result = converter.to_dict(selector)

        assert result["text"] == "Settings"
        assert result["clickable"] is True


class TestLocatorConverterToXPath:
    """Tests for to_xpath method."""

    def test_to_xpath_from_dict(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting dictionary to xpath tuple."""
        selector_dict = {"text": "Settings"}
        result = converter.to_xpath(selector_dict)

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == "xpath"
        assert "@text='Settings'" in result[1]

        # Verify it can be used with real app
        element = app.get_element(result)
        assert element is not None

    def test_to_xpath_from_xpath_tuple(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting xpath tuple to xpath tuple (should return same)."""
        xpath_tuple = ("xpath", "//*[@text='Settings']")
        result = converter.to_xpath(xpath_tuple)

        assert result == xpath_tuple

        # Verify it can be used with real app
        element = app.get_element(result)
        assert element is not None

    def test_to_xpath_from_xpath_string(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting xpath string to xpath tuple."""
        xpath_str = "//*[@text='Settings']"
        result = converter.to_xpath(xpath_str)

        assert isinstance(result, tuple)
        assert result[0] == "xpath"
        assert result[1] == xpath_str

    def test_to_xpath_from_uiselector_string(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting UiSelector string to xpath tuple."""
        uiselector_str = 'new UiSelector().text("Settings");'
        result = converter.to_xpath(uiselector_str)

        assert isinstance(result, tuple)
        assert result[0] == "xpath"
        assert "@text='Settings'" in result[1]

    def test_to_xpath_from_uiselector_object(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting UiSelector object to xpath tuple."""
        uiselector = UiSelector().text("Settings")
        result = converter.to_xpath(uiselector)

        assert isinstance(result, tuple)
        assert result[0] == "xpath"
        assert "@text='Settings'" in result[1]


class TestLocatorConverterToUiSelector:
    """Tests for to_uiselector method."""

    def test_to_uiselector_from_dict(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting dictionary to UiSelector string."""
        selector_dict = {"text": "Settings"}
        result = converter.to_uiselector(selector_dict)

        assert isinstance(result, str)
        assert result.startswith("new UiSelector()")
        assert '.text("Settings")' in result
        assert result.endswith(";")

    def test_to_uiselector_from_xpath_tuple(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting xpath tuple to UiSelector string."""
        xpath_tuple = ("xpath", "//*[@text='Settings']")
        result = converter.to_uiselector(xpath_tuple)

        assert isinstance(result, str)
        assert result.startswith("new UiSelector()")
        assert '.text("Settings")' in result

    def test_to_uiselector_from_xpath_string(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting xpath string to UiSelector string."""
        xpath_str = "//*[@text='Settings']"
        result = converter.to_uiselector(xpath_str)

        assert isinstance(result, str)
        assert result.startswith("new UiSelector()")
        assert '.text("Settings")' in result

    def test_to_uiselector_from_uiselector_string(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting UiSelector string to UiSelector string (should return same)."""
        uiselector_str = 'new UiSelector().text("Settings");'
        result = converter.to_uiselector(uiselector_str)

        assert result == uiselector_str

    def test_to_uiselector_from_uiselector_object(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting UiSelector object to UiSelector string."""
        uiselector = UiSelector().text("Settings")
        result = converter.to_uiselector(uiselector)

        assert isinstance(result, str)
        assert result.startswith("new UiSelector()")
        assert '.text("Settings")' in result


class TestLocatorConverterDirectConversions:
    """Tests for direct conversion methods."""

    def test_dict_to_xpath(self, app: Shadowstep, converter: LocatorConverter):
        """Test direct dictionary to xpath conversion."""
        selector_dict = {"text": "Settings"}
        result = converter.dict_to_xpath(selector_dict)

        assert isinstance(result, str)
        assert "@text='Settings'" in result

    def test_dict_to_uiselector(self, app: Shadowstep, converter: LocatorConverter):
        """Test direct dictionary to UiSelector conversion."""
        selector_dict = {"text": "Settings"}
        result = converter.dict_to_uiselector(selector_dict)

        assert isinstance(result, str)
        assert result.startswith("new UiSelector()")
        assert '.text("Settings")' in result

    def test_xpath_to_dict(self, app: Shadowstep, converter: LocatorConverter):
        """Test direct xpath to dictionary conversion."""
        xpath = "//*[@text='Settings']"
        result = converter.xpath_to_dict(xpath)

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"

    def test_xpath_to_uiselector(self, app: Shadowstep, converter: LocatorConverter):
        """Test direct xpath to UiSelector conversion."""
        xpath = "//*[@text='Settings']"
        result = converter.xpath_to_uiselector(xpath)

        assert isinstance(result, str)
        assert result.startswith("new UiSelector()")
        assert '.text("Settings")' in result

    def test_uiselector_to_dict(self, app: Shadowstep, converter: LocatorConverter):
        """Test direct UiSelector to dictionary conversion."""
        uiselector = 'new UiSelector().text("Settings");'
        result = converter.uiselector_to_dict(uiselector)

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"

    def test_uiselector_to_xpath(self, app: Shadowstep, converter: LocatorConverter):
        """Test direct UiSelector to xpath conversion."""
        uiselector = 'new UiSelector().text("Settings");'
        result = converter.uiselector_to_xpath(uiselector)

        assert isinstance(result, str)
        assert "@text='Settings'" in result


class TestLocatorConverterValidation:
    """Tests for validate_selector method."""

    def test_validate_dict_selector(self, app: Shadowstep, converter: LocatorConverter):
        """Test validating dictionary selector."""
        selector = {"text": "Settings"}
        # Should not raise any exception
        converter.validate_selector(selector)

    def test_validate_xpath_tuple(self, app: Shadowstep, converter: LocatorConverter):
        """Test validating xpath tuple selector."""
        selector = ("xpath", "//*[@text='Settings']")
        # Should not raise any exception
        converter.validate_selector(selector)

    def test_validate_xpath_string(self, app: Shadowstep, converter: LocatorConverter):
        """Test validating xpath string selector."""
        selector = "//*[@text='Settings']"
        # Should not raise any exception
        converter.validate_selector(selector)

    def test_validate_uiselector_object(self, app: Shadowstep, converter: LocatorConverter):
        """Test validating UiSelector object."""
        selector = UiSelector().text("Settings")
        # Should not raise any exception
        converter.validate_selector(selector)


class TestLocatorConverterWithRealApp:
    """Integration tests using real app elements."""

    def test_conversion_chain_dict_xpath_uiselector(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting through dict -> xpath -> uiselector chain."""
        # Start with dict
        original_dict = {"text": "Settings"}

        # Convert to xpath
        xpath_result = converter.to_xpath(original_dict)

        # Convert xpath to uiselector
        uiselector_result = converter.to_uiselector(xpath_result)

        # Convert back to dict
        final_dict = converter.to_dict(uiselector_result)

        # Verify all formats work with real app
        element1 = app.get_element(original_dict)
        element2 = app.get_element(xpath_result)
        element3 = app.get_element(uiselector_result)

        assert element1 is not None
        assert element2 is not None
        assert element3 is not None

    def test_complex_selector_conversion(self, app: Shadowstep, converter: LocatorConverter):
        """Test converting complex selector with multiple attributes."""
        selector = {"text": "Settings", "clickable": True}

        # Convert to all formats
        xpath_result = converter.to_xpath(selector)
        uiselector_result = converter.to_uiselector(selector)

        # Verify xpath works
        element1 = app.get_element(xpath_result)
        assert element1 is not None

        # Verify converted selector preserves attributes
        converted_dict = converter.to_dict(uiselector_result)
        assert "text" in converted_dict
        assert converted_dict["text"] == "Settings"
