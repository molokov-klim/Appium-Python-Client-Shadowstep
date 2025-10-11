# ruff: noqa
# pyright: ignore
"""Unit tests for shadowstep/element/utilities.py module."""
from typing import Any
from unittest.mock import Mock, patch
import pytest

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.element.utilities import ElementUtilities
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep


class TestElementUtilities:
    """Test suite for ElementUtilities class."""

    def _create_test_element(self, mock_driver: Mock) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        return app, el

    # Tests for __init__ method
    @pytest.mark.unit
    def test_element_utilities_initialization(self):
        """Test ElementUtilities initialization."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        utilities = ElementUtilities(el)
        
        assert utilities.element is el
        assert utilities.shadowstep is el.shadowstep
        assert utilities.logger is not None

    # Tests for remove_null_value method
    @pytest.mark.unit
    def test_remove_null_value_with_tuple_xpath(self):
        """Test remove_null_value with tuple locator containing null attribute."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        locator = ("xpath", "//div[@class='test'][@attr='null'][@id='123']")
        result = el.utilities.remove_null_value(locator)
        
        assert result == ("xpath", "//div[@class='test'][@id='123']")

    @pytest.mark.unit
    def test_remove_null_value_with_dict(self):
        """Test remove_null_value with dict locator containing null values."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        locator = {"class": "test", "text": "null", "id": "123", "name": "null"}
        result = el.utilities.remove_null_value(locator)
        
        assert result == {"class": "test", "id": "123"}
        assert "text" not in result
        assert "name" not in result

    @pytest.mark.unit
    def test_remove_null_value_with_dict_no_nulls(self):
        """Test remove_null_value with dict locator without null values."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        locator = {"class": "test", "id": "123"}
        result = el.utilities.remove_null_value(locator)
        
        assert result == {"class": "test", "id": "123"}

    @pytest.mark.unit
    def test_remove_null_value_with_other_types(self):
        """Test remove_null_value with non-tuple, non-dict locators."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        # Test with string (should return unchanged)
        locator = "some_locator_string"
        result = el.utilities.remove_null_value(locator)
        assert result == locator

    # Tests for extract_el_attrs_from_source method
    @pytest.mark.unit
    def test_extract_el_attrs_from_source_success(self):
        """Test successful extract_el_attrs_from_source operation."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        page_source = '''
        <root>
            <element class="Button" text="Click me" id="btn1"/>
            <element class="Text" text="Label" id="lbl1"/>
        </root>
        '''
        
        result = el.utilities.extract_el_attrs_from_source("//element", page_source)
        
        assert len(result) == 2
        assert result[0]["class"] == "Button"
        assert result[0]["text"] == "Click me"
        assert result[1]["class"] == "Text"

    @pytest.mark.unit
    def test_extract_el_attrs_from_source_with_single_element(self):
        """Test extract_el_attrs_from_source with single matching element."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        page_source = '''<root><button id="submit" class="btn"/></root>'''
        
        result = el.utilities.extract_el_attrs_from_source("//button", page_source)
        
        assert len(result) == 1
        assert result[0]["id"] == "submit"
        assert result[0]["class"] == "btn"

    @pytest.mark.unit
    def test_extract_el_attrs_from_source_no_matches(self):
        """Test extract_el_attrs_from_source raises exception when no matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        page_source = '''<root><element/></root>'''
        
        with pytest.raises(ShadowstepElementException) as exc_info:
            el.utilities.extract_el_attrs_from_source("//nonexistent", page_source)
        
        assert "No matches found" in str(exc_info.value)

    @pytest.mark.unit
    def test_extract_el_attrs_from_source_handles_xpath_eval_error(self):
        """Test extract_el_attrs_from_source handles XPathEvalError."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        page_source = '''<root><element/></root>'''
        invalid_xpath = "//[@@@invalid"
        
        with pytest.raises(ShadowstepElementException) as exc_info:
            el.utilities.extract_el_attrs_from_source(invalid_xpath, page_source)
        
        assert "Parsing error" in str(exc_info.value)

    @pytest.mark.unit
    def test_extract_el_attrs_from_source_handles_xml_syntax_error(self):
        """Test extract_el_attrs_from_source handles XMLSyntaxError with recover=True parser."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        # Invalid XML - but parser has recover=True, so it may parse partially
        # and then find no matches, raising "No matches found" instead
        page_source = '''<root><unclosed'''
        
        with pytest.raises(ShadowstepElementException) as exc_info:
            el.utilities.extract_el_attrs_from_source("//element", page_source)
        
        # With recover=True parser, it may parse and find no matches
        assert "No matches found" in str(exc_info.value) or "Parsing error" in str(exc_info.value)

    # Tests for get_xpath method
    @pytest.mark.unit
    def test_get_xpath_with_tuple_locator(self):
        """Test get_xpath with tuple locator."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//button[@id='submit']")
        
        result = el.utilities.get_xpath()
        
        assert result == "//button[@id='submit']"

    @pytest.mark.unit
    def test_get_xpath_with_dict_locator(self):
        """Test get_xpath with dict locator calls _get_xpath_by_driver."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = {"class": "Button"}
        
        with patch.object(el.utilities, '_get_xpath_by_driver', return_value="//Button[@class='Button']"):
            result = el.utilities.get_xpath()
        
        assert result == "//Button[@class='Button']"

    # Tests for _get_xpath_by_driver method
    @pytest.mark.unit
    def test_get_xpath_by_driver_success(self):
        """Test successful _get_xpath_by_driver operation."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        attrs = {"class": "Button", "id": "submit", "text": "Click"}
        
        with patch.object(el, 'get_attributes', return_value=attrs):
            with patch.object(el.utilities, 'build_xpath_from_attributes', return_value="//Button[@id='submit']"):
                result = el.utilities._get_xpath_by_driver()
        
        assert result == "//Button[@id='submit']"

    @pytest.mark.unit
    def test_get_xpath_by_driver_returns_empty_when_no_attrs(self):
        """Test _get_xpath_by_driver returns empty string when no attributes."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        # When get_attributes returns empty dict, ShadowstepElementException is raised,
        # but caught in except block and empty string is returned
        with patch.object(el, 'get_attributes', return_value={}):
            result = el.utilities._get_xpath_by_driver()
        
        assert result == ""

    @pytest.mark.unit
    def test_get_xpath_by_driver_handles_exception(self):
        """Test _get_xpath_by_driver handles exceptions."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attributes', side_effect=AttributeError("Error")):
            result = el.utilities._get_xpath_by_driver()
        
        assert result == ""

    # Tests for handle_driver_error method
    @pytest.mark.unit
    def test_handle_driver_error(self):
        """Test handle_driver_error calls reconnect."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        error = WebDriverException("Test error")
        
        with patch.object(el.shadowstep, 'reconnect') as mock_reconnect:
            with patch('time.sleep'):
                el.utilities.handle_driver_error(error)
        
        mock_reconnect.assert_called_once()

    # Tests for _build_xpath_attribute_condition method
    @pytest.mark.unit
    def test_build_xpath_attribute_condition_with_simple_value(self):
        """Test _build_xpath_attribute_condition with simple value."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        result = el.utilities._build_xpath_attribute_condition("id", "submit")
        
        assert result == "[@id='submit']"

    @pytest.mark.unit
    def test_build_xpath_attribute_condition_with_null_value(self):
        """Test _build_xpath_attribute_condition with null value."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        result = el.utilities._build_xpath_attribute_condition("attr", "null")
        
        assert result == "[@attr]"

    @pytest.mark.unit
    def test_build_xpath_attribute_condition_with_none_value(self):
        """Test _build_xpath_attribute_condition with None value."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        result = el.utilities._build_xpath_attribute_condition("attr", None)
        
        assert result == "[@attr]"

    @pytest.mark.unit
    def test_build_xpath_attribute_condition_with_single_quote(self):
        """Test _build_xpath_attribute_condition with single quote in value."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        result = el.utilities._build_xpath_attribute_condition("text", "John's Book")
        
        assert result == '[@text="John\'s Book"]'

    @pytest.mark.unit
    def test_build_xpath_attribute_condition_with_double_quote(self):
        """Test _build_xpath_attribute_condition with double quote in value."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        result = el.utilities._build_xpath_attribute_condition("text", 'Say "Hello"')
        
        assert result == "[@text='Say \"Hello\"']"

    @pytest.mark.unit
    def test_build_xpath_attribute_condition_with_both_quotes(self):
        """Test _build_xpath_attribute_condition with both quotes in value."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        result = el.utilities._build_xpath_attribute_condition("text", 'John\'s "Book"')
        
        # Should use concat() for values with both quote types
        assert "concat(" in result
        assert "[@text=" in result

    # Tests for build_xpath_from_attributes method
    @pytest.mark.unit
    def test_build_xpath_from_attributes_with_class(self):
        """Test build_xpath_from_attributes with class attribute."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        attrs = {"class": "Button", "id": "submit"}
        
        result = el.utilities.build_xpath_from_attributes(attrs)
        
        assert result.startswith("//Button")
        assert "[@id='submit']" in result

    @pytest.mark.unit
    def test_build_xpath_from_attributes_without_class(self):
        """Test build_xpath_from_attributes without class attribute."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        attrs = {"id": "submit", "text": "Click"}
        
        result = el.utilities.build_xpath_from_attributes(attrs)
        
        assert result.startswith("//*")
        assert "[@id='submit']" in result
        assert "[@text='Click']" in result

    @pytest.mark.unit
    def test_build_xpath_from_attributes_excludes_except_attrs(self):
        """Test build_xpath_from_attributes excludes except_attrs."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        attrs = {
            "class": "Button",
            "id": "submit",
            "hint": "Enter text",
            "selection-start": "0",
            "selection-end": "5",
            "extras": "data"
        }
        
        result = el.utilities.build_xpath_from_attributes(attrs)
        
        assert "[@id='submit']" in result
        # Should NOT contain except_attrs
        assert "hint" not in result
        assert "selection-start" not in result
        assert "selection-end" not in result
        assert "extras" not in result

    @pytest.mark.unit
    def test_build_xpath_from_attributes_with_complex_values(self):
        """Test build_xpath_from_attributes with values containing quotes."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        attrs = {"class": "Text", "text": "John's Book"}
        
        result = el.utilities.build_xpath_from_attributes(attrs)
        
        assert result.startswith("//Text")
        # Should handle quote properly
        assert "[@text=" in result

    # Tests for _ensure_session_alive method
    @pytest.mark.unit
    def test_ensure_session_alive_with_active_session(self):
        """Test _ensure_session_alive with active session."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            # Should not raise
            el.utilities._ensure_session_alive()

    @pytest.mark.unit
    def test_ensure_session_alive_handles_no_such_driver_exception(self):
        """Test _ensure_session_alive handles NoSuchDriverException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', side_effect=NoSuchDriverException("No driver")):
            with patch.object(el.shadowstep, 'reconnect') as mock_reconnect:
                el.utilities._ensure_session_alive()
        
        mock_reconnect.assert_called_once()

    @pytest.mark.unit
    def test_ensure_session_alive_handles_invalid_session_id_exception(self):
        """Test _ensure_session_alive handles InvalidSessionIdException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', side_effect=InvalidSessionIdException("Invalid session")):
            with patch.object(el.shadowstep, 'reconnect') as mock_reconnect:
                el.utilities._ensure_session_alive()
        
        mock_reconnect.assert_called_once()

    # Tests for _get_first_child_class method
    @pytest.mark.unit
    def test_get_first_child_class_success(self):
        """Test successful _get_first_child_class operation."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_child1 = Mock()
        mock_child1.get_attribute.return_value = "ChildClass"
        
        with patch.object(el, 'get_attribute', return_value="ParentClass"):
            with patch.object(el, 'get_elements', return_value=[mock_child1]):
                result = el.utilities._get_first_child_class()
        
        assert result == "ChildClass"

    @pytest.mark.unit
    def test_get_first_child_class_returns_empty_when_same_class(self):
        """Test _get_first_child_class returns empty when child has same class as parent."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_child1 = Mock()
        mock_child1.get_attribute.return_value = "SameClass"
        
        with patch.object(el, 'get_attribute', return_value="SameClass"):
            with patch.object(el, 'get_elements', return_value=[mock_child1]):
                result = el.utilities._get_first_child_class()
        
        assert result == ""

    @pytest.mark.unit
    def test_get_first_child_class_handles_stale_element_reference_exception(self):
        """Test _get_first_child_class handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_child = Mock()
        mock_child.get_attribute.return_value = "ChildClass"
        
        call_count = [0]
        def mock_get_attribute(name):
            call_count[0] += 1
            if call_count[0] == 1:
                raise StaleElementReferenceException("Stale")
            return "ParentClass"
        
        with patch.object(el, 'get_attribute', side_effect=mock_get_attribute):
            with patch.object(el, 'get_elements', return_value=[mock_child]):
                with patch.object(el, 'get_native', return_value=Mock()):
                    result = el.utilities._get_first_child_class()
        
        assert result == "ChildClass"

    @pytest.mark.unit
    def test_get_first_child_class_handles_webdriver_exception_instrumentation(self):
        """Test _get_first_child_class handles WebDriverException with instrumentation error."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        call_count = [0]
        def mock_get_attribute(name):
            call_count[0] += 1
            if call_count[0] == 1:
                raise WebDriverException("Instrumentation process is not running")
            return "ParentClass"
        
        mock_child = Mock()
        mock_child.get_attribute.return_value = "ChildClass"
        
        with patch.object(el, 'get_attribute', side_effect=mock_get_attribute):
            with patch.object(el, 'get_elements', return_value=[mock_child]):
                with patch.object(el.utilities, 'handle_driver_error'):
                    result = el.utilities._get_first_child_class()
        
        assert result == "ChildClass"

    @pytest.mark.unit
    def test_get_first_child_class_raises_other_webdriver_exceptions(self):
        """Test _get_first_child_class raises other WebDriverException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', side_effect=WebDriverException("Some other error")):
            with pytest.raises(WebDriverException):
                el.utilities._get_first_child_class()

    @pytest.mark.unit
    def test_get_first_child_class_returns_empty_after_max_tries(self):
        """Test _get_first_child_class returns empty string after max tries."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_child = Mock()
        mock_child.get_attribute.return_value = "ParentClass"
        
        # All children have same class as parent
        with patch.object(el, 'get_attribute', return_value="ParentClass"):
            with patch.object(el, 'get_elements', return_value=[mock_child]):
                result = el.utilities._get_first_child_class(tries=3)
        
        assert result == ""

    # Additional edge case tests
    @pytest.mark.unit
    def test_remove_null_value_with_multiple_null_attrs_in_xpath(self):
        """Test remove_null_value with multiple null attributes in xpath."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        locator = ("xpath", "//div[@a='null'][@b='valid'][@c='null'][@d='value']")
        result = el.utilities.remove_null_value(locator)
        
        assert result == ("xpath", "//div[@b='valid'][@d='value']")

    @pytest.mark.unit
    def test_extract_el_attrs_from_source_with_special_characters(self):
        """Test extract_el_attrs_from_source with special characters in attributes."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        page_source = '''<root><element text="Test &amp; Value" id="test-123"/></root>'''
        
        result = el.utilities.extract_el_attrs_from_source("//element", page_source)
        
        assert len(result) == 1
        assert "text" in result[0]
        assert result[0]["id"] == "test-123"

    @pytest.mark.unit
    def test_build_xpath_from_attributes_with_empty_dict(self):
        """Test build_xpath_from_attributes with empty attributes dict."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        attrs = {}
        
        result = el.utilities.build_xpath_from_attributes(attrs)
        
        assert result == "//*"

    @pytest.mark.unit
    def test_build_xpath_from_attributes_preserves_attribute_order(self):
        """Test build_xpath_from_attributes includes all non-excluded attributes."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        attrs = {
            "class": "Button",
            "resource-id": "com.example:id/btn",
            "text": "Submit",
            "enabled": "true"
        }
        
        result = el.utilities.build_xpath_from_attributes(attrs)
        
        assert result.startswith("//Button")
        assert "[@resource-id=" in result
        assert "[@text=" in result
        assert "[@enabled=" in result

    @pytest.mark.unit
    def test_get_first_child_class_with_multiple_children(self):
        """Test _get_first_child_class with multiple children."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        mock_child1 = Mock()
        mock_child1.get_attribute.return_value = "ParentClass"  # Same as parent
        mock_child2 = Mock()
        mock_child2.get_attribute.return_value = "DifferentClass"  # Different
        
        with patch.object(el, 'get_attribute', return_value="ParentClass"):
            with patch.object(el, 'get_elements', return_value=[mock_child1, mock_child2]):
                result = el.utilities._get_first_child_class()
        
        assert result == "DifferentClass"

    @pytest.mark.unit
    def test_extract_el_attrs_from_source_with_namespaces(self):
        """Test extract_el_attrs_from_source handles XML with namespaces."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        page_source = '''
        <root xmlns:android="http://schemas.android.com/apk/res/android">
            <element android:id="test" class="Button"/>
        </root>
        '''
        
        # Should handle namespaced attributes
        result = el.utilities.extract_el_attrs_from_source("//element", page_source)
        
        assert len(result) == 1
        assert result[0]["class"] == "Button"

