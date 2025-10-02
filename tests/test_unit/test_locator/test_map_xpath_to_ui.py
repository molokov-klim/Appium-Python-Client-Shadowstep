"""Tests for xpath_to_ui mapping module."""

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedXPathAttributeError
from shadowstep.locator.map.xpath_to_ui import (
    XPATH_TO_UI,
    _handle_child_selector,
    _handle_from_parent,
    get_supported_attributes,
    get_ui_for_method,
    is_hierarchical_xpath,
)
from shadowstep.locator.locator_types.ui_selector import UiAttribute
from shadowstep.locator.locator_types.xpath import XPathAttribute


class TestXPathToUiMapping:
    """Test XPath to UiSelector mapping functionality."""

    def test_handle_child_selector(self):
        """Test child selector handling."""
        result = _handle_child_selector("new UiSelector().text('Child')")
        expected = ".childSelector(new UiSelector().text('Child'))"
        assert result == expected

    def test_handle_from_parent(self):
        """Test from parent handling."""
        result = _handle_from_parent("new UiSelector().text('Parent')")
        expected = ".fromParent(new UiSelector().text('Parent'))"
        assert result == expected

    def test_text_attributes(self):
        """Test text-based attribute mappings."""
        # Test TEXT
        result = XPATH_TO_UI[XPathAttribute.TEXT]("Hello World")
        expected = f"{UiAttribute.TEXT.value}(Hello World)"
        assert result == expected

        # Test TEXT_CONTAINS
        result = XPATH_TO_UI[XPathAttribute.TEXT_CONTAINS]("Hello")
        expected = f"{UiAttribute.TEXT_CONTAINS.value}(Hello)"
        assert result == expected

        # Test TEXT_STARTS_WITH
        result = XPATH_TO_UI[XPathAttribute.TEXT_STARTS_WITH]("Hello")
        expected = f"{UiAttribute.TEXT_STARTS_WITH.value}(Hello)"
        assert result == expected

        # Test TEXT_MATCHES
        result = XPATH_TO_UI[XPathAttribute.TEXT_MATCHES]("\\d+")
        expected = f"{UiAttribute.TEXT_MATCHES.value}(\\d+)"
        assert result == expected

    def test_description_attributes(self):
        """Test description-based attribute mappings."""
        # Test DESCRIPTION
        result = XPATH_TO_UI[XPathAttribute.DESCRIPTION]("Button")
        expected = f"{UiAttribute.DESCRIPTION.value}(Button)"
        assert result == expected

        # Test DESCRIPTION_CONTAINS
        result = XPATH_TO_UI[XPathAttribute.DESCRIPTION_CONTAINS]("Btn")
        expected = f"{UiAttribute.DESCRIPTION_CONTAINS.value}(Btn)"
        assert result == expected

        # Test DESCRIPTION_STARTS_WITH
        result = XPATH_TO_UI[XPathAttribute.DESCRIPTION_STARTS_WITH]("Button")
        expected = f"{UiAttribute.DESCRIPTION_STARTS_WITH.value}(Button)"
        assert result == expected

        # Test DESCRIPTION_MATCHES
        result = XPATH_TO_UI[XPathAttribute.DESCRIPTION_MATCHES]("Btn\\d+")
        expected = f"{UiAttribute.DESCRIPTION_MATCHES.value}(Btn\\d+)"
        assert result == expected

    def test_resource_id_attributes(self):
        """Test resource ID and package attribute mappings."""
        # Test RESOURCE_ID
        result = XPATH_TO_UI[XPathAttribute.RESOURCE_ID]("com.example:id/button")
        expected = f"{UiAttribute.RESOURCE_ID.value}(com.example:id/button)"
        assert result == expected

        # Test RESOURCE_ID_MATCHES
        result = XPATH_TO_UI[XPathAttribute.RESOURCE_ID_MATCHES](".*button.*")
        expected = f"{UiAttribute.RESOURCE_ID_MATCHES.value}(.*button.*)"
        assert result == expected

        # Test PACKAGE_NAME
        result = XPATH_TO_UI[XPathAttribute.PACKAGE_NAME]("com.example")
        expected = f"{UiAttribute.PACKAGE_NAME.value}(com.example)"
        assert result == expected

        # Test PACKAGE_NAME_MATCHES
        result = XPATH_TO_UI[XPathAttribute.PACKAGE_NAME_MATCHES]("com\\..*")
        expected = f"{UiAttribute.PACKAGE_NAME_MATCHES.value}(com\\..*)"
        assert result == expected

    def test_class_attributes(self):
        """Test class name attribute mappings."""
        # Test CLASS_NAME
        result = XPATH_TO_UI[XPathAttribute.CLASS_NAME]("android.widget.Button")
        expected = f"{UiAttribute.CLASS_NAME.value}(android.widget.Button)"
        assert result == expected

        # Test CLASS_NAME_MATCHES
        result = XPATH_TO_UI[XPathAttribute.CLASS_NAME_MATCHES]("android\\..*")
        expected = f"{UiAttribute.CLASS_NAME_MATCHES.value}(android\\..*)"
        assert result == expected

    def test_boolean_attributes(self):
        """Test boolean attribute mappings."""
        # Test CHECKABLE
        result = XPATH_TO_UI[XPathAttribute.CHECKABLE]("true")
        expected = f"{UiAttribute.CHECKABLE.value}(true)"
        assert result == expected

        # Test CHECKED
        result = XPATH_TO_UI[XPathAttribute.CHECKED]("false")
        expected = f"{UiAttribute.CHECKED.value}(false)"
        assert result == expected

        # Test CLICKABLE
        result = XPATH_TO_UI[XPathAttribute.CLICKABLE]("true")
        expected = f"{UiAttribute.CLICKABLE.value}(true)"
        assert result == expected

        # Test ENABLED
        result = XPATH_TO_UI[XPathAttribute.ENABLED]("true")
        expected = f"{UiAttribute.ENABLED.value}(true)"
        assert result == expected

        # Test FOCUSABLE
        result = XPATH_TO_UI[XPathAttribute.FOCUSABLE]("false")
        expected = f"{UiAttribute.FOCUSABLE.value}(false)"
        assert result == expected

        # Test FOCUSED
        result = XPATH_TO_UI[XPathAttribute.FOCUSED]("true")
        expected = f"{UiAttribute.FOCUSED.value}(true)"
        assert result == expected

        # Test LONG_CLICKABLE
        result = XPATH_TO_UI[XPathAttribute.LONG_CLICKABLE]("false")
        expected = f"{UiAttribute.CLICKABLE.value}(false)"
        assert result == expected

        # Test SCROLLABLE
        result = XPATH_TO_UI[XPathAttribute.SCROLLABLE]("false")
        expected = f"{UiAttribute.SCROLLABLE.value}(false)"
        assert result == expected

        # Test SELECTED
        result = XPATH_TO_UI[XPathAttribute.SELECTED]("true")
        expected = f"{UiAttribute.SELECTED.value}(true)"
        assert result == expected

        # Test PASSWORD
        result = XPATH_TO_UI[XPathAttribute.PASSWORD]("false")
        expected = f"{UiAttribute.PASSWORD.value}(false)"
        assert result == expected

    def test_numeric_attributes(self):
        """Test numeric attribute mappings."""
        # Test INDEX
        result = XPATH_TO_UI[XPathAttribute.INDEX]("0")
        expected = f"{UiAttribute.INDEX.value}(0)"
        assert result == expected

        # Test INSTANCE
        result = XPATH_TO_UI[XPathAttribute.INSTANCE]("5")
        expected = f"{UiAttribute.INSTANCE.value}(5)"
        assert result == expected

    def test_hierarchical_attributes(self):
        """Test hierarchical attribute mappings."""
        # Test CHILD_SELECTOR
        result = XPATH_TO_UI[XPathAttribute.CHILD_SELECTOR]("new UiSelector().text('Child')")
        expected = ".childSelector(new UiSelector().text('Child'))"
        assert result == expected

        # Test FROM_PARENT
        result = XPATH_TO_UI[XPathAttribute.FROM_PARENT]("new UiSelector().text('Parent')")
        expected = ".fromParent(new UiSelector().text('Parent'))"
        assert result == expected

    def test_get_ui_for_method_success(self):
        """Test get_ui_for_method with valid method."""
        result = get_ui_for_method(XPathAttribute.TEXT, "Hello")
        expected = f"{UiAttribute.TEXT.value}(Hello)"
        assert result == expected

    def test_get_ui_for_method_unsupported(self):
        """Test get_ui_for_method with unsupported method."""
        # Create a mock XPathAttribute that's not in the mapping
        class MockXPathAttribute:
            pass
        
        with pytest.raises(ShadowstepUnsupportedXPathAttributeError):
            get_ui_for_method(MockXPathAttribute(), "test")

    def test_is_hierarchical_xpath_true(self):
        """Test is_hierarchical_xpath returns True for hierarchical methods."""
        assert is_hierarchical_xpath(XPathAttribute.CHILD_SELECTOR) is True
        assert is_hierarchical_xpath(XPathAttribute.FROM_PARENT) is True

    def test_is_hierarchical_xpath_false(self):
        """Test is_hierarchical_xpath returns False for non-hierarchical methods."""
        assert is_hierarchical_xpath(XPathAttribute.TEXT) is False
        assert is_hierarchical_xpath(XPathAttribute.CLASS_NAME) is False
        assert is_hierarchical_xpath(XPathAttribute.CLICKABLE) is False

    def test_get_supported_attributes(self):
        """Test get_supported_attributes returns all supported attributes."""
        supported = get_supported_attributes()
        assert isinstance(supported, list)
        assert len(supported) == len(XPATH_TO_UI)
        
        # Check that all attributes in the mapping are in the supported list
        for attr in XPATH_TO_UI.keys():
            assert attr in supported

    def test_all_attributes_covered(self):
        """Test that all supported XPathAttribute enum values are covered in the mapping."""
        # SIBLING is not supported in the mapping
        unsupported_attributes = {XPathAttribute.SIBLING}
        
        for attr in XPathAttribute:
            if attr not in unsupported_attributes:
                assert attr in XPATH_TO_UI
                # Test that the mapping function works
                result = XPATH_TO_UI[attr]("test_value")
                assert isinstance(result, str)
                assert len(result) > 0
