# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Tests for the locator module.

This module contains comprehensive tests for the locator conversion functionality,
including UiSelector DSL, LocatorConverter, and various mapping functions.
"""

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepConversionError
from shadowstep.locator.converter.dict_converter import DictConverter
from shadowstep.locator.converter.locator_converter import LocatorConverter
from shadowstep.locator.map.dict_to_ui import dict_to_ui_attribute, is_hierarchical_attribute
from shadowstep.locator.map.dict_to_xpath import dict_to_xpath_attribute
from shadowstep.locator.locator_types.shadowstep_dict import ShadowstepDictAttribute
from shadowstep.locator.ui_selector import UiSelector


class TestUiSelector:
    """Test cases for UiSelector DSL class."""

    @pytest.mark.unit
    def test_init(self) -> None:
        """Test UiSelector initialization."""
        selector = UiSelector()

        assert selector._methods == []  # noqa: S101
        assert selector._hierarchical_methods == []  # noqa: S101

    @pytest.mark.unit
    def test_text_method(self) -> None:
        """Test text method."""
        selector = UiSelector().text("OK")

        assert len(selector._methods) == 1  # noqa: S101
        assert selector._methods[0] == ("text", "OK")  # noqa: S101

    @pytest.mark.unit
    def test_text_contains_method(self) -> None:
        """Test textContains method."""
        selector = UiSelector().textContains("Hello")

        assert len(selector._methods) == 1  # noqa: S101
        assert selector._methods[0] == ("textContains", "Hello")  # noqa: S101

    @pytest.mark.unit
    def test_resource_id_method(self) -> None:
        """Test resourceId method."""
        selector = UiSelector().resourceId("com.example:id/button")

        assert len(selector._methods) == 1  # noqa: S101
        assert selector._methods[0] == ("resourceId", "com.example:id/button")  # noqa: S101

    @pytest.mark.unit
    def test_class_name_method(self) -> None:
        """Test className method."""
        selector = UiSelector().className("android.widget.Button")

        assert len(selector._methods) == 1  # noqa: S101
        assert selector._methods[0] == ("className", "android.widget.Button")  # noqa: S101

    @pytest.mark.unit
    def test_boolean_methods(self) -> None:
        """Test boolean property methods."""
        selector = UiSelector().clickable(True).enabled(False)

        assert len(selector._methods) == 2  # noqa: S101
        assert selector._methods[0] == ("clickable", True)  # noqa: S101
        assert selector._methods[1] == ("enabled", False)  # noqa: S101

    @pytest.mark.unit
    def test_numeric_methods(self) -> None:
        """Test numeric methods."""
        selector = UiSelector().index(0).instance(1)

        assert len(selector._methods) == 2  # noqa: S101
        assert selector._methods[0] == ("index", 0)  # noqa: S101
        assert selector._methods[1] == ("instance", 1)  # noqa: S101

    @pytest.mark.unit
    def test_chaining_methods(self) -> None:
        """Test method chaining."""
        selector = UiSelector().text("OK").clickable(True).className("Button")

        assert len(selector._methods) == 3  # noqa: S101
        assert selector._methods[0] == ("text", "OK")  # noqa: S101
        assert selector._methods[1] == ("clickable", True)  # noqa: S101
        assert selector._methods[2] == ("className", "Button")  # noqa: S101

    @pytest.mark.unit
    def test_hierarchical_methods(self) -> None:
        """Test hierarchical methods."""
        child = UiSelector().text("Child")
        parent = UiSelector().text("Parent").childSelector(child)

        assert len(parent._methods) == 1  # noqa: S101
        assert len(parent._hierarchical_methods) == 1  # noqa: S101
        assert parent._hierarchical_methods[0] == ("childSelector", child)  # noqa: S101

    @pytest.mark.unit
    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        selector = UiSelector().text("OK").clickable(True)
        result = selector.to_dict()

        expected = {"text": "OK", "clickable": True}
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_to_dict_with_hierarchy(self) -> None:
        """Test conversion to dictionary with hierarchy."""
        child = UiSelector().text("Child")
        parent = UiSelector().text("Parent").childSelector(child)
        result = parent.to_dict()

        expected = {"text": "Parent", "childSelector": {"text": "Child"}}
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_str_representation(self) -> None:
        """Test string representation."""
        selector = UiSelector().text("OK").clickable(True)
        result = str(selector)

        expected = 'new UiSelector().text("OK").clickable(true);'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_str_with_escaped_quotes(self) -> None:
        """Test string representation with escaped quotes."""
        selector = UiSelector().text('He said "Hello"')
        result = str(selector)

        expected = 'new UiSelector().text("He said \\"Hello\\"");'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_str_with_backslashes(self) -> None:
        """Test string representation with backslashes."""
        selector = UiSelector().text("Path\\to\\file")
        result = str(selector)

        expected = 'new UiSelector().text("Path\\\\to\\\\file");'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_equality(self) -> None:
        """Test equality comparison."""
        selector1 = UiSelector().text("OK").clickable(True)
        selector2 = UiSelector().text("OK").clickable(True)
        selector3 = UiSelector().text("Cancel").clickable(True)

        assert selector1 == selector2  # noqa: S101
        assert selector1 != selector3  # noqa: S101
        assert selector1 != "not a selector"  # noqa: S101

    @pytest.mark.unit
    def test_hash(self) -> None:
        """Test hash functionality."""
        selector1 = UiSelector().text("OK")
        selector2 = UiSelector().text("OK")
        selector3 = UiSelector().text("Cancel")

        assert hash(selector1) == hash(selector2)  # noqa: S101
        assert hash(selector1) != hash(selector3)  # noqa: S101

    @pytest.mark.unit
    def test_copy(self) -> None:
        """Test copying functionality."""
        original = UiSelector().text("OK").clickable(True)
        copy_selector = original.copy()

        assert original == copy_selector  # noqa: S101
        assert original is not copy_selector  # noqa: S101

        # Modify copy and ensure original is unchanged
        copy_selector.text("Modified")
        assert original != copy_selector  # noqa: S101

    @pytest.mark.unit
    def test_from_dict(self) -> None:
        """Test creation from dictionary."""
        selector_dict = {"text": "OK", "clickable": True}
        selector = UiSelector.from_dict(selector_dict)

        assert selector._methods[0] == ("text", "OK")  # noqa: S101
        assert selector._methods[1] == ("clickable", True)  # noqa: S101

    @pytest.mark.unit
    def test_from_dict_with_hierarchy(self) -> None:
        """Test creation from dictionary with hierarchy."""
        selector_dict = {
            "text": "Parent",
            "childSelector": {"text": "Child"}
        }
        selector = UiSelector.from_dict(selector_dict)

        assert selector._methods[0] == ("text", "Parent")  # noqa: S101
        assert len(selector._hierarchical_methods) == 1  # noqa: S101
        child = selector._hierarchical_methods[0][1]
        assert child._methods[0] == ("text", "Child")  # noqa: S101


class TestLocatorConverter:
    """Test cases for LocatorConverter class."""

    @pytest.fixture
    def converter(self) -> LocatorConverter:
        """Create a LocatorConverter instance."""
        return LocatorConverter()

    @pytest.mark.unit
    def test_init(self, converter: LocatorConverter) -> None:
        """Test LocatorConverter initialization."""
        assert converter.dict_converter is not None  # noqa: S101
        assert converter.ui_selector_converter is not None  # noqa: S101
        assert converter.xpath_converter is not None  # noqa: S101

    @pytest.mark.unit
    def test_to_dict_from_dict(self, converter: LocatorConverter) -> None:
        """Test conversion to dict from dict."""
        selector_dict = {"text": "OK", "clickable": True}
        result = converter.to_dict(selector_dict)

        assert result == selector_dict  # noqa: S101

    @pytest.mark.unit
    def test_to_dict_from_uiselector(self, converter: LocatorConverter) -> None:
        """Test conversion to dict from UiSelector."""
        selector = UiSelector().text("OK").clickable(True)
        result = converter.to_dict(selector)

        expected = {"text": "OK", "clickable": True}
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_to_dict_from_xpath_tuple(self, converter: LocatorConverter) -> None:
        """Test conversion to dict from XPath tuple."""
        xpath_tuple = ("xpath", "//*[@text='OK']")
        result = converter.to_dict(xpath_tuple)

        # The exact result depends on XPathConverter implementation
        assert isinstance(result, dict)  # noqa: S101

    @pytest.mark.unit
    def test_to_dict_from_uiselector_string(self, converter: LocatorConverter) -> None:
        """Test conversion to dict from UiSelector string."""
        selector_str = 'new UiSelector().text("OK").clickable(true);'
        result = converter.to_dict(selector_str)

        # The exact result depends on UiSelectorConverter implementation
        assert isinstance(result, dict)  # noqa: S101

    @pytest.mark.unit
    def test_to_dict_from_xpath_string(self, converter: LocatorConverter) -> None:
        """Test conversion to dict from XPath string."""
        xpath_str = "//*[@text='OK']"
        result = converter.to_dict(xpath_str)

        # The exact result depends on XPathConverter implementation
        assert isinstance(result, dict)  # noqa: S101

    @pytest.mark.unit
    def test_to_dict_unsupported_type(self, converter: LocatorConverter) -> None:
        """Test conversion to dict with unsupported type."""
        with pytest.raises(ShadowstepConversionError):
            converter.to_dict(123)  # type: ignore

    @pytest.mark.unit
    def test_to_xpath_from_dict(self, converter: LocatorConverter) -> None:
        """Test conversion to XPath from dict."""
        selector_dict = {"text": "OK", "clickable": True}
        result = converter.to_xpath(selector_dict)

        assert isinstance(result, tuple)  # noqa: S101
        assert len(result) == 2  # noqa: S101
        assert result[0] == "xpath"  # noqa: S101
        assert isinstance(result[1], str)  # noqa: S101

    @pytest.mark.unit
    def test_to_xpath_from_uiselector(self, converter: LocatorConverter) -> None:
        """Test conversion to XPath from UiSelector."""
        selector = UiSelector().text("OK").clickable(True)
        result = converter.to_xpath(selector)

        assert isinstance(result, tuple)  # noqa: S101
        assert len(result) == 2  # noqa: S101
        assert result[0] == "xpath"  # noqa: S101
        assert isinstance(result[1], str)  # noqa: S101

    @pytest.mark.unit
    def test_to_xpath_from_xpath_tuple(self, converter: LocatorConverter) -> None:
        """Test conversion to XPath from XPath tuple."""
        xpath_tuple = ("xpath", "//*[@text='OK']")
        result = converter.to_xpath(xpath_tuple)

        assert result == xpath_tuple  # noqa: S101

    @pytest.mark.unit
    def test_to_uiselector_from_dict(self, converter: LocatorConverter) -> None:
        """Test conversion to UiSelector from dict."""
        selector_dict = {"text": "OK", "clickable": True}
        result = converter.to_uiselector(selector_dict)

        assert isinstance(result, str)  # noqa: S101
        assert "new UiSelector()" in result  # noqa: S101

    @pytest.mark.unit
    def test_to_uiselector_from_uiselector(self, converter: LocatorConverter) -> None:
        """Test conversion to UiSelector from UiSelector."""
        selector = UiSelector().text("OK").clickable(True)
        result = converter.to_uiselector(selector)

        expected = 'new UiSelector().text("OK").clickable(true);'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_to_uiselector_from_uiselector_string(self, converter: LocatorConverter) -> None:
        """Test conversion to UiSelector from UiSelector string."""
        selector_str = 'new UiSelector().text("OK").clickable(true);'
        result = converter.to_uiselector(selector_str)

        assert result == selector_str  # noqa: S101

    @pytest.mark.unit
    def test_validate_selector_dict(self, converter: LocatorConverter) -> None:
        """Test validation of dict selector."""
        selector_dict = {"text": "OK", "clickable": True}
        # Should not raise any exception
        converter.validate_selector(selector_dict)

    @pytest.mark.unit
    def test_validate_selector_uiselector(self, converter: LocatorConverter) -> None:
        """Test validation of UiSelector."""
        selector = UiSelector().text("OK").clickable(True)
        # Should not raise any exception
        converter.validate_selector(selector)

    @pytest.mark.unit
    def test_validate_selector_xpath_tuple(self, converter: LocatorConverter) -> None:
        """Test validation of XPath tuple."""
        xpath_tuple = ("xpath", "//*[@text='OK']")
        # Should not raise any exception
        converter.validate_selector(xpath_tuple)

    @pytest.mark.unit
    def test_validate_selector_string(self, converter: LocatorConverter) -> None:
        """Test validation of string selector."""
        selector_str = "//*[@text='OK']"
        # Should not raise any exception
        converter.validate_selector(selector_str)

    @pytest.mark.unit
    def test_validate_selector_empty_string(self, converter: LocatorConverter) -> None:
        """Test validation of empty string selector."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepEmptySelectorStringError
        
        with pytest.raises(ShadowstepEmptySelectorStringError):
            converter.validate_selector("")

    @pytest.mark.unit
    def test_validate_selector_unsupported_type(self, converter: LocatorConverter) -> None:
        """Test validation of unsupported selector type."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedSelectorTypeError
        
        with pytest.raises(ShadowstepUnsupportedSelectorTypeError):
            converter.validate_selector(123)  # type: ignore


class TestDictConverter:
    """Test cases for DictConverter class."""

    @pytest.fixture
    def dict_converter(self) -> DictConverter:
        """Create a DictConverter instance."""
        return DictConverter()

    @pytest.mark.unit
    def test_init(self, dict_converter: DictConverter) -> None:
        """Test DictConverter initialization."""
        assert dict_converter.logger is not None  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_xpath_simple(self, dict_converter: DictConverter) -> None:
        """Test simple dict to XPath conversion."""
        selector_dict = {"text": "OK", "clickable": True}
        result = dict_converter.dict_to_xpath(selector_dict)

        assert isinstance(result, str)  # noqa: S101
        assert "//*" in result  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_ui_selector_simple(self, dict_converter: DictConverter) -> None:
        """Test simple dict to UiSelector conversion."""
        selector_dict = {"text": "OK", "clickable": True}
        result = dict_converter.dict_to_ui_selector(selector_dict)

        assert isinstance(result, str)  # noqa: S101
        assert "new UiSelector()" in result  # noqa: S101

    @pytest.mark.unit
    def test_validate_dict_selector_valid(self, dict_converter: DictConverter) -> None:
        """Test validation of valid dict selector."""
        selector_dict = {"text": "OK", "clickable": True}
        # Should not raise any exception
        dict_converter.validate_dict_selector(selector_dict)

    @pytest.mark.unit
    def test_validate_dict_selector_empty(self, dict_converter: DictConverter) -> None:
        """Test validation of empty dict selector."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepEmptySelectorError
        
        selector_dict = {}
        # Should raise ShadowstepEmptySelectorError for empty selector
        with pytest.raises(ShadowstepEmptySelectorError):
            dict_converter.validate_dict_selector(selector_dict)  # type: ignore


class TestDictToUiMapping:
    """Test cases for dict to UiSelector mapping functions."""

    @pytest.mark.unit
    def test_dict_to_ui_attribute_text(self) -> None:
        """Test text attribute conversion."""
        result = dict_to_ui_attribute(ShadowstepDictAttribute.TEXT, "OK")
        expected = '.text("OK")'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_ui_attribute_text_contains(self) -> None:
        """Test textContains attribute conversion."""
        result = dict_to_ui_attribute(ShadowstepDictAttribute.TEXT_CONTAINS, "Hello")
        expected = '.textContains("Hello")'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_ui_attribute_resource_id(self) -> None:
        """Test resourceId attribute conversion."""
        result = dict_to_ui_attribute(ShadowstepDictAttribute.RESOURCE_ID, "com.example:id/button")
        expected = '.resourceId("com.example:id/button")'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_ui_attribute_clickable(self) -> None:
        """Test clickable attribute conversion."""
        result = dict_to_ui_attribute(ShadowstepDictAttribute.CLICKABLE, True)
        expected = ".clickable(true)"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_ui_attribute_clickable_false(self) -> None:
        """Test clickable attribute conversion with False."""
        result = dict_to_ui_attribute(ShadowstepDictAttribute.CLICKABLE, False)
        expected = ".clickable(false)"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_ui_attribute_index(self) -> None:
        """Test index attribute conversion."""
        result = dict_to_ui_attribute(ShadowstepDictAttribute.INDEX, 0)
        expected = ".index(0)"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_ui_attribute_unsupported(self) -> None:
        """Test unsupported attribute conversion."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedAttributeForUiSelectorError
        
        with pytest.raises(ShadowstepUnsupportedAttributeForUiSelectorError):
            dict_to_ui_attribute(ShadowstepDictAttribute.CHILD_SELECTOR, {})  # type: ignore

    @pytest.mark.unit
    def test_is_hierarchical_attribute_true(self) -> None:
        """Test hierarchical attribute detection."""
        assert is_hierarchical_attribute(ShadowstepDictAttribute.CHILD_SELECTOR) is True  # noqa: S101
        assert is_hierarchical_attribute(ShadowstepDictAttribute.FROM_PARENT) is True  # noqa: S101
        assert is_hierarchical_attribute(ShadowstepDictAttribute.SIBLING) is True  # noqa: S101

    @pytest.mark.unit
    def test_is_hierarchical_attribute_false(self) -> None:
        """Test non-hierarchical attribute detection."""
        assert is_hierarchical_attribute(ShadowstepDictAttribute.TEXT) is False  # noqa: S101
        assert is_hierarchical_attribute(ShadowstepDictAttribute.CLICKABLE) is False  # noqa: S101


class TestDictToXPathMapping:
    """Test cases for dict to XPath mapping functions."""

    @pytest.mark.unit
    def test_dict_to_xpath_attribute_text(self) -> None:
        """Test text attribute conversion."""
        result = dict_to_xpath_attribute(ShadowstepDictAttribute.TEXT, "OK")
        expected = "@text='OK'"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_xpath_attribute_text_contains(self) -> None:
        """Test textContains attribute conversion."""
        result = dict_to_xpath_attribute(ShadowstepDictAttribute.TEXT_CONTAINS, "Hello")
        expected = "contains(@text, 'Hello')"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_xpath_attribute_resource_id(self) -> None:
        """Test resourceId attribute conversion."""
        result = dict_to_xpath_attribute(ShadowstepDictAttribute.RESOURCE_ID, "com.example:id/button")
        expected = "@resource-id='com.example:id/button'"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_xpath_attribute_clickable(self) -> None:
        """Test clickable attribute conversion."""
        result = dict_to_xpath_attribute(ShadowstepDictAttribute.CLICKABLE, True)
        expected = "@clickable='true'"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_xpath_attribute_clickable_false(self) -> None:
        """Test clickable attribute conversion with False."""
        result = dict_to_xpath_attribute(ShadowstepDictAttribute.CLICKABLE, False)
        expected = "@clickable='false'"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_xpath_attribute_index(self) -> None:
        """Test index attribute conversion."""
        result = dict_to_xpath_attribute(ShadowstepDictAttribute.INDEX, 0)
        expected = "@index=0"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_dict_to_xpath_attribute_unsupported(self) -> None:
        """Test unsupported attribute conversion."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedAttributeForXPathError
        
        with pytest.raises(ShadowstepUnsupportedAttributeForXPathError):
            dict_to_xpath_attribute(ShadowstepDictAttribute.CHILD_SELECTOR, {})  # type: ignore


class TestDictAttribute:
    """Test cases for ShadowstepDictAttribute enum."""

    @pytest.mark.unit
    def test_text_attributes(self) -> None:
        """Test text-related attributes."""
        assert ShadowstepDictAttribute.TEXT == "text"  # noqa: S101
        assert ShadowstepDictAttribute.TEXT_CONTAINS == "textContains"  # noqa: S101
        assert ShadowstepDictAttribute.TEXT_STARTS_WITH == "textStartsWith"  # noqa: S101
        assert ShadowstepDictAttribute.TEXT_MATCHES == "textMatches"  # noqa: S101

    @pytest.mark.unit
    def test_description_attributes(self) -> None:
        """Test description-related attributes."""
        assert ShadowstepDictAttribute.DESCRIPTION == "content-desc"  # noqa: S101
        assert ShadowstepDictAttribute.DESCRIPTION_CONTAINS == "content-descContains"  # noqa: S101
        assert ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH == "content-descStartsWith"  # noqa: S101
        assert ShadowstepDictAttribute.DESCRIPTION_MATCHES == "content-descMatches"  # noqa: S101

    @pytest.mark.unit
    def test_resource_attributes(self) -> None:
        """Test resource ID and package attributes."""
        assert ShadowstepDictAttribute.RESOURCE_ID == "resource-id"  # noqa: S101
        assert ShadowstepDictAttribute.RESOURCE_ID_MATCHES == "resource-idMatches"  # noqa: S101
        assert ShadowstepDictAttribute.PACKAGE_NAME == "package"  # noqa: S101
        assert ShadowstepDictAttribute.PACKAGE_NAME_MATCHES == "packageMatches"  # noqa: S101

    @pytest.mark.unit
    def test_class_attributes(self) -> None:
        """Test class name attributes."""
        assert ShadowstepDictAttribute.CLASS_NAME == "class"  # noqa: S101
        assert ShadowstepDictAttribute.CLASS_NAME_MATCHES == "classMatches"  # noqa: S101

    @pytest.mark.unit
    def test_boolean_attributes(self) -> None:
        """Test boolean property attributes."""
        assert ShadowstepDictAttribute.CHECKABLE == "checkable"  # noqa: S101
        assert ShadowstepDictAttribute.CHECKED == "checked"  # noqa: S101
        assert ShadowstepDictAttribute.CLICKABLE == "clickable"  # noqa: S101
        assert ShadowstepDictAttribute.ENABLED == "enabled"  # noqa: S101
        assert ShadowstepDictAttribute.FOCUSABLE == "focusable"  # noqa: S101
        assert ShadowstepDictAttribute.FOCUSED == "focused"  # noqa: S101
        assert ShadowstepDictAttribute.LONG_CLICKABLE == "long-clickable"  # noqa: S101
        assert ShadowstepDictAttribute.SCROLLABLE == "scrollable"  # noqa: S101
        assert ShadowstepDictAttribute.SELECTED == "selected"  # noqa: S101
        assert ShadowstepDictAttribute.PASSWORD == "password"  # noqa: S101, S105

    @pytest.mark.unit
    def test_numeric_attributes(self) -> None:
        """Test numeric attributes."""
        assert ShadowstepDictAttribute.INDEX == "index"  # noqa: S101
        assert ShadowstepDictAttribute.INSTANCE == "instance"  # noqa: S101

    @pytest.mark.unit
    def test_hierarchical_attributes(self) -> None:
        """Test hierarchical attributes."""
        assert ShadowstepDictAttribute.CHILD_SELECTOR == "childSelector"  # noqa: S101
        assert ShadowstepDictAttribute.FROM_PARENT == "fromParent"  # noqa: S101
        assert ShadowstepDictAttribute.SIBLING == "sibling"  # noqa: S101

    @pytest.mark.unit
    def test_string_comparison(self) -> None:
        """Test string comparison functionality."""
        assert ShadowstepDictAttribute.TEXT == "text"  # noqa: S101
        assert ShadowstepDictAttribute.TEXT != "not_text"  # noqa: S101

    @pytest.mark.unit
    def test_hash_functionality(self) -> None:
        """Test hash functionality."""
        text_hash = hash(ShadowstepDictAttribute.TEXT)
        clickable_hash = hash(ShadowstepDictAttribute.CLICKABLE)

        assert text_hash != clickable_hash  # noqa: S101
        assert hash(ShadowstepDictAttribute.TEXT) == hash("text")  # noqa: S101
