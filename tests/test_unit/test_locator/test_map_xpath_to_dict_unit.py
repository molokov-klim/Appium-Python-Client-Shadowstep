# ruff: noqa
# pyright: ignore
"""Tests for xpath_to_dict mapping module."""

import pytest

from shadowstep.locator.map.xpath_to_dict import XPATH_TO_SHADOWSTEP_DICT
from shadowstep.locator.locator_types.shadowstep_dict import ShadowstepDictAttribute
from shadowstep.locator.locator_types.xpath import XPathAttribute


class TestXPathToDictMapping:
    """Test XPath to ShadowstepDict mapping functionality."""

    @pytest.mark.unit
    def test_text_attributes(self):
        """Test text-based attribute mappings."""
        # Test TEXT
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.TEXT]("Hello World")
        expected = {ShadowstepDictAttribute.TEXT.value: "Hello World"}
        assert result == expected

        # Test TEXT_CONTAINS
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.TEXT_CONTAINS]("Hello")
        expected = {ShadowstepDictAttribute.TEXT_CONTAINS.value: "Hello"}
        assert result == expected

        # Test TEXT_STARTS_WITH
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.TEXT_STARTS_WITH]("Hello")
        expected = {ShadowstepDictAttribute.TEXT_STARTS_WITH.value: "Hello"}
        assert result == expected

        # Test TEXT_MATCHES
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.TEXT_MATCHES]("\\d+")
        expected = {ShadowstepDictAttribute.TEXT_MATCHES.value: "\\d+"}
        assert result == expected

    @pytest.mark.unit
    def test_description_attributes(self):
        """Test description-based attribute mappings."""
        # Test DESCRIPTION
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.DESCRIPTION]("Button")
        expected = {ShadowstepDictAttribute.DESCRIPTION.value: "Button"}
        assert result == expected

        # Test DESCRIPTION_CONTAINS
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.DESCRIPTION_CONTAINS]("Btn")
        expected = {ShadowstepDictAttribute.DESCRIPTION_CONTAINS.value: "Btn"}
        assert result == expected

        # Test DESCRIPTION_STARTS_WITH
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.DESCRIPTION_STARTS_WITH]("Button")
        expected = {ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH.value: "Button"}
        assert result == expected

        # Test DESCRIPTION_MATCHES
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.DESCRIPTION_MATCHES]("Btn\\d+")
        expected = {ShadowstepDictAttribute.DESCRIPTION_MATCHES.value: "Btn\\d+"}
        assert result == expected

    @pytest.mark.unit
    def test_resource_id_attributes(self):
        """Test resource ID and package attribute mappings."""
        # Test RESOURCE_ID
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.RESOURCE_ID]("com.example:id/button")
        expected = {ShadowstepDictAttribute.RESOURCE_ID.value: "com.example:id/button"}
        assert result == expected

        # Test RESOURCE_ID_MATCHES
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.RESOURCE_ID_MATCHES](".*button.*")
        expected = {ShadowstepDictAttribute.RESOURCE_ID_MATCHES.value: ".*button.*"}
        assert result == expected

        # Test PACKAGE_NAME
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.PACKAGE_NAME]("com.example")
        expected = {ShadowstepDictAttribute.PACKAGE_NAME.value: "com.example"}
        assert result == expected

        # Test PACKAGE_NAME_MATCHES
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.PACKAGE_NAME_MATCHES]("com\\..*")
        expected = {ShadowstepDictAttribute.PACKAGE_NAME_MATCHES.value: "com\\..*"}
        assert result == expected

    @pytest.mark.unit
    def test_class_attributes(self):
        """Test class name attribute mappings."""
        # Test CLASS_NAME
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.CLASS_NAME]("android.widget.Button")
        expected = {ShadowstepDictAttribute.CLASS_NAME.value: "android.widget.Button"}
        assert result == expected

        # Test CLASS_NAME_MATCHES
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.CLASS_NAME_MATCHES]("android\\..*")
        expected = {ShadowstepDictAttribute.CLASS_NAME_MATCHES.value: "android\\..*"}
        assert result == expected

    @pytest.mark.unit
    def test_boolean_attributes(self):
        """Test boolean attribute mappings."""
        # Test CHECKABLE
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.CHECKABLE]("true")
        expected = {ShadowstepDictAttribute.CHECKABLE.value: "true"}
        assert result == expected

        # Test CHECKED
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.CHECKED]("false")
        expected = {ShadowstepDictAttribute.CHECKED.value: "false"}
        assert result == expected

        # Test CLICKABLE
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.CLICKABLE]("true")
        expected = {ShadowstepDictAttribute.CLICKABLE.value: "true"}
        assert result == expected

        # Test LONG_CLICKABLE
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.LONG_CLICKABLE]("false")
        expected = {ShadowstepDictAttribute.LONG_CLICKABLE.value: "false"}
        assert result == expected

        # Test ENABLED
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.ENABLED]("true")
        expected = {ShadowstepDictAttribute.ENABLED.value: "true"}
        assert result == expected

        # Test FOCUSABLE
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.FOCUSABLE]("false")
        expected = {ShadowstepDictAttribute.FOCUSABLE.value: "false"}
        assert result == expected

        # Test FOCUSED
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.FOCUSED]("true")
        expected = {ShadowstepDictAttribute.FOCUSED.value: "true"}
        assert result == expected

        # Test SCROLLABLE
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.SCROLLABLE]("false")
        expected = {ShadowstepDictAttribute.SCROLLABLE.value: "false"}
        assert result == expected

        # Test SELECTED
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.SELECTED]("true")
        expected = {ShadowstepDictAttribute.SELECTED.value: "true"}
        assert result == expected

        # Test PASSWORD
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.PASSWORD]("false")
        expected = {ShadowstepDictAttribute.PASSWORD.value: "false"}
        assert result == expected

    @pytest.mark.unit
    def test_numeric_attributes(self):
        """Test numeric attribute mappings."""
        # Test INDEX
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.INDEX]("0")
        expected = {ShadowstepDictAttribute.INDEX.value: "0"}
        assert result == expected

        # Test INSTANCE
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.INSTANCE]("5")
        expected = {ShadowstepDictAttribute.INSTANCE.value: "5"}
        assert result == expected

    @pytest.mark.unit
    def test_hierarchical_attributes(self):
        """Test hierarchical attribute mappings."""
        # Test CHILD_SELECTOR
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.CHILD_SELECTOR]("child_selector")
        expected = {ShadowstepDictAttribute.CHILD_SELECTOR.value: "child_selector"}
        assert result == expected

        # Test FROM_PARENT
        result = XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.FROM_PARENT]("parent_selector")
        expected = {ShadowstepDictAttribute.FROM_PARENT.value: "parent_selector"}
        assert result == expected

    @pytest.mark.unit
    def test_all_attributes_covered(self):
        """Test that all supported XPathAttribute enum values are covered in the mapping."""
        # SIBLING is not supported in the mapping
        unsupported_attributes = {XPathAttribute.SIBLING}
        
        for attr in XPathAttribute:
            if attr not in unsupported_attributes:
                assert attr in XPATH_TO_SHADOWSTEP_DICT
                # Test that the mapping function works
                result = XPATH_TO_SHADOWSTEP_DICT[attr]("test_value")
                assert isinstance(result, dict)
                assert len(result) == 1
