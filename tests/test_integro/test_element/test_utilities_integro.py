# ruff: noqa
# pyright: ignore
"""Integration tests for ElementUtilities class."""
import time

import pytest
from selenium.common import WebDriverException

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep


class TestElementUtilities:
    """Test class for ElementUtilities functionality."""

    def test_remove_null_value_with_tuple_locator(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test remove_null_value() with tuple locator containing null values.

        Steps:
        1. Find an element in Settings.
        2. Create a locator with null value in XPath.
        3. Use remove_null_value() to clean it.
        4. Verify null attributes are removed.
        """
        # Find an element
        element = app.get_element({"text": "Settings"})

        # Create locator with null value (note: remove_null_value looks for single quotes)
        locator_with_null = ("xpath", "//android.widget.TextView[@text='Settings'][@resource-id='null']")

        # Remove null values
        cleaned = element.utilities.remove_null_value(locator_with_null)

        # Verify null attribute is removed
        assert cleaned[0] == "xpath"  # noqa: S101
        assert "[@resource-id='null']" not in cleaned[1]  # noqa: S101
        assert "TextView[@text='Settings']" in cleaned[1]  # noqa: S101

    def test_remove_null_value_with_dict_locator(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test remove_null_value() with dict locator containing null values.

        Steps:
        1. Find an element.
        2. Create a dict locator with null values.
        3. Use remove_null_value() to clean it.
        4. Verify null key-value pairs are removed.
        """
        # Find an element
        element = app.get_element({"text": "Settings"})

        # Create dict with null value
        dict_locator = {"text": "Settings", "resource-id": "null", "enabled": "true"}

        # Remove null values
        cleaned = element.utilities.remove_null_value(dict_locator)

        # Verify null key is removed
        assert isinstance(cleaned, dict)  # noqa: S101
        assert "text" in cleaned  # noqa: S101
        assert "enabled" in cleaned  # noqa: S101
        assert "resource-id" not in cleaned  # noqa: S101

    def test_remove_null_value_with_element_locator(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test remove_null_value() with Element locator returns unchanged.

        Steps:
        1. Find an element.
        2. Pass the element itself to remove_null_value().
        3. Verify it returns the element unchanged.
        """
        # Find an element
        element = app.get_element({"text": "Settings"})

        # Pass element itself
        result = element.utilities.remove_null_value(element)

        # Should return element unchanged
        assert result is element  # noqa: S101

    def test_extract_el_attrs_from_source_with_valid_xpath(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test extract_el_attrs_from_source() extracts attributes correctly.

        Steps:
        1. Get page source.
        2. Define an XPath expression.
        3. Extract attributes using extract_el_attrs_from_source().
        4. Verify attributes are extracted correctly.
        """
        # Find an element to get utilities
        element = app.get_element({"text": "Settings"})

        # Get page source
        page_source = app.driver.page_source

        # Extract attributes for Settings TextView
        xpath_expr = '//android.widget.TextView[@text="Settings"]'
        attrs_list = element.utilities.extract_el_attrs_from_source(xpath_expr, page_source)

        # Verify we got results
        assert len(attrs_list) > 0  # noqa: S101
        # Verify first element has attributes
        first_attrs = attrs_list[0]
        assert isinstance(first_attrs, dict)  # noqa: S101
        assert "text" in first_attrs  # noqa: S101
        assert first_attrs["text"] == "Settings"  # noqa: S101

    def test_extract_el_attrs_from_source_with_no_match(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test extract_el_attrs_from_source() raises exception when no match.

        Steps:
        1. Get page source.
        2. Define an XPath that doesn't match anything.
        3. Try to extract attributes.
        4. Verify ShadowstepElementException is raised.
        """
        # Find an element to get utilities
        element = app.get_element({"text": "Settings"})

        # Get page source
        page_source = app.driver.page_source

        # Try to extract with non-matching XPath
        xpath_expr = '//android.widget.NonExistentElement[@text="DoesNotExist"]'

        # Should raise exception
        with pytest.raises(ShadowstepElementException) as exc_info:
            element.utilities.extract_el_attrs_from_source(xpath_expr, page_source)

        assert "No matches found for XPath" in str(exc_info.value)  # noqa: S101

    def test_extract_el_attrs_from_source_with_invalid_xpath(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test extract_el_attrs_from_source() with invalid XPath syntax.

        Steps:
        1. Get page source.
        2. Define an invalid XPath expression.
        3. Try to extract attributes.
        4. Verify ShadowstepElementException is raised.
        """
        # Find an element to get utilities
        element = app.get_element({"text": "Settings"})

        # Get page source
        page_source = app.driver.page_source

        # Invalid XPath syntax
        xpath_expr = '//android.widget.TextView[@text='  # Missing closing quote

        # Should raise exception
        with pytest.raises(ShadowstepElementException) as exc_info:
            element.utilities.extract_el_attrs_from_source(xpath_expr, page_source)

        assert "Parsing error" in str(exc_info.value)  # noqa: S101

    def test_get_xpath_with_tuple_locator(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test get_xpath() returns XPath when locator is tuple.

        Steps:
        1. Find an element with tuple locator.
        2. Call get_xpath().
        3. Verify it returns the XPath string.
        """
        # Find an element with dict locator first
        element = app.get_element({"text": "Settings"})

        # Change locator to tuple to test tuple path
        element.locator = ("xpath", '//android.widget.TextView[@text="Settings"]')

        # Get XPath
        xpath = element.utilities.get_xpath()

        # Should return the XPath string from tuple
        assert xpath is not None  # noqa: S101
        assert isinstance(xpath, str)  # noqa: S101
        assert len(xpath) > 0  # noqa: S101
        assert xpath == '//android.widget.TextView[@text="Settings"]'  # noqa: S101

    def test_get_xpath_with_non_tuple_locator(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test get_xpath() builds XPath when locator is not tuple.

        Steps:
        1. Find an element.
        2. Change locator to non-tuple type.
        3. Call get_xpath().
        4. Verify it builds XPath from element attributes.
        """
        # Find an element first
        element = app.get_element({"text": "Settings"})

        # Save original locator and change it to non-tuple
        original_locator = element.locator
        element.locator = {"text": "Settings"}  # Change to dict

        # Get XPath - should build from driver
        xpath = element.utilities.get_xpath()

        # Restore original locator
        element.locator = original_locator

        # Verify XPath was built
        assert xpath is not None  # noqa: S101
        assert isinstance(xpath, str)  # noqa: S101

    def test_build_xpath_from_attributes_basic(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test build_xpath_from_attributes() builds correct XPath.

        Steps:
        1. Find an element.
        2. Create attributes dict.
        3. Build XPath from attributes.
        4. Verify XPath structure is correct.
        """
        # Find an element to get utilities
        element = app.get_element({"text": "Settings"})

        # Create attributes dict
        attrs = {
            "class": "android.widget.TextView",
            "text": "Settings",
            "enabled": "true",
        }

        # Build XPath
        xpath = element.utilities.build_xpath_from_attributes(attrs)

        # Verify XPath structure
        assert xpath.startswith("//android.widget.TextView")  # noqa: S101
        assert "[@text='Settings']" in xpath  # noqa: S101
        assert "[@enabled='true']" in xpath  # noqa: S101

    def test_build_xpath_from_attributes_with_special_chars(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test build_xpath_from_attributes() handles special characters.

        Steps:
        1. Find an element.
        2. Create attributes with single quotes.
        3. Build XPath.
        4. Verify special chars are handled with double quotes.
        """
        # Find an element to get utilities
        element = app.get_element({"text": "Settings"})

        # Create attributes with single quote
        attrs = {
            "class": "android.widget.TextView",
            "text": "It's working",
        }

        # Build XPath
        xpath = element.utilities.build_xpath_from_attributes(attrs)

        # Should use double quotes for value with single quote
        assert xpath.startswith("//android.widget.TextView")  # noqa: S101
        assert '[@text="It\'s working"]' in xpath  # noqa: S101

    def test_build_xpath_from_attributes_with_both_quotes(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test build_xpath_from_attributes() handles both quote types.

        Steps:
        1. Find an element.
        2. Create attributes with both single and double quotes.
        3. Build XPath.
        4. Verify concat() is used.
        """
        # Find an element to get utilities
        element = app.get_element({"text": "Settings"})

        # Create attributes with both quotes
        attrs = {
            "class": "android.widget.TextView",
            "text": 'It\'s "working"',
        }

        # Build XPath
        xpath = element.utilities.build_xpath_from_attributes(attrs)

        # Should use concat for mixed quotes
        assert xpath.startswith("//android.widget.TextView")  # noqa: S101
        assert "concat(" in xpath  # noqa: S101

    def test_build_xpath_from_attributes_with_null_value(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test build_xpath_from_attributes() handles null values.

        Steps:
        1. Find an element.
        2. Create attributes with null value.
        3. Build XPath.
        4. Verify null value creates attribute-exists condition.
        """
        # Find an element to get utilities
        element = app.get_element({"text": "Settings"})

        # Create attributes with null value
        attrs = {
            "class": "android.widget.TextView",
            "resource-id": "null",
        }

        # Build XPath
        xpath = element.utilities.build_xpath_from_attributes(attrs)

        # Should create attribute-exists condition for null
        assert xpath.startswith("//android.widget.TextView")  # noqa: S101
        assert "[@resource-id]" in xpath  # noqa: S101

    def test_build_xpath_from_attributes_excludes_hint(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test build_xpath_from_attributes() excludes 'hint' attribute.

        Steps:
        1. Find an element.
        2. Create attributes with 'hint'.
        3. Build XPath.
        4. Verify 'hint' is excluded.
        """
        # Find an element to get utilities
        element = app.get_element({"text": "Settings"})

        # Create attributes with hint
        attrs = {
            "class": "android.widget.TextView",
            "text": "Settings",
            "hint": "Some hint",
        }

        # Build XPath
        xpath = element.utilities.build_xpath_from_attributes(attrs)

        # hint should be excluded
        assert xpath.startswith("//android.widget.TextView")  # noqa: S101
        assert "[@text='Settings']" in xpath  # noqa: S101
        assert "hint" not in xpath  # noqa: S101

    def test_build_xpath_from_attributes_without_class(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test build_xpath_from_attributes() uses wildcard without class.

        Steps:
        1. Find an element.
        2. Create attributes without 'class' key.
        3. Build XPath.
        4. Verify wildcard is used.
        """
        # Find an element to get utilities
        element = app.get_element({"text": "Settings"})

        # Create attributes without class
        attrs = {
            "text": "Settings",
            "enabled": "true",
        }

        # Build XPath
        xpath = element.utilities.build_xpath_from_attributes(attrs)

        # Should use wildcard
        assert xpath.startswith("//*")  # noqa: S101
        assert "[@text='Settings']" in xpath  # noqa: S101

    def test_handle_driver_error_reconnects(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test handle_driver_error() triggers reconnection.

        Steps:
        1. Find an element.
        2. Get initial session ID.
        3. Call handle_driver_error().
        4. Verify reconnection is attempted.
        5. Verify session is still valid after reconnection.
        """
        # Find an element
        element = app.get_element({"text": "Settings"})

        # Get initial session
        initial_session = app.driver.session_id
        assert initial_session is not None  # noqa: S101

        # Create a WebDriverException
        error = WebDriverException("Test error")

        # Call handle_driver_error
        element.utilities.handle_driver_error(error)

        # Wait a bit for reconnection
        time.sleep(1)

        # Verify app is still connected
        assert app.is_connected() is True  # noqa: S101
        assert app.driver is not None  # noqa: S101
        assert app.driver.session_id is not None  # noqa: S101

    def test_utilities_object_is_initialized(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test that utilities object is properly initialized.

        Steps:
        1. Find an element.
        2. Verify utilities object exists.
        3. Verify utilities has expected attributes.
        """
        # Find an element
        element = app.get_element({"text": "Settings"})

        # Verify utilities is initialized
        assert element.utilities is not None  # noqa: S101
        assert hasattr(element.utilities, "element")  # noqa: S101
        assert hasattr(element.utilities, "shadowstep")  # noqa: S101
        assert hasattr(element.utilities, "logger")  # noqa: S101

        # Verify references are correct
        assert element.utilities.element is element  # noqa: S101
        assert element.utilities.shadowstep is app  # noqa: S101

    def test_utilities_methods_are_callable(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test that all utilities methods are callable.

        Steps:
        1. Find an element.
        2. Verify all public methods are callable.
        """
        # Find an element
        element = app.get_element({"text": "Settings"})

        # Verify methods are callable
        assert callable(element.utilities.remove_null_value)  # noqa: S101
        assert callable(element.utilities.extract_el_attrs_from_source)  # noqa: S101
        assert callable(element.utilities.get_xpath)  # noqa: S101
        assert callable(element.utilities.handle_driver_error)  # noqa: S101
        assert callable(element.utilities.build_xpath_from_attributes)  # noqa: S101

    def test_extract_el_attrs_from_source_with_multiple_matches(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test extract_el_attrs_from_source() with multiple matching elements.

        Steps:
        1. Get page source.
        2. Use XPath that matches multiple elements.
        3. Extract attributes.
        4. Verify multiple results are returned.
        """
        # Find an element to get utilities
        element = app.get_element({"text": "Settings"})

        # Get page source
        page_source = app.driver.page_source

        # Extract all TextViews
        xpath_expr = "//android.widget.TextView"
        attrs_list = element.utilities.extract_el_attrs_from_source(xpath_expr, page_source)

        # Should return multiple elements
        assert len(attrs_list) > 1  # noqa: S101
        # Each should be a dict
        for attrs in attrs_list:
            assert isinstance(attrs, dict)  # noqa: S101
