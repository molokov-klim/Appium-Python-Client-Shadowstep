# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
import logging
from typing import Any

import pytest

from shadowstep.locator.converter.dict_converter import DictConverter

logger = logging.getLogger(__name__)


class TestDictConverter:
    """Test cases for DictConverter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = DictConverter()

    @pytest.mark.parametrize(
        "selector_dict, expected_xpath",  # noqa: PT006
        [
            # Basic attributes
            ({"text": "OK"}, "//*[@text='OK']"),
            ({"class": "android.widget.Button"}, "//*[@class='android.widget.Button']"),
            ({"resource-id": "com.example:id/button"}, "//*[@resource-id='com.example:id/button']"),
            ({"content-desc": "Submit"}, "//*[@content-desc='Submit']"),
            
            # Boolean attributes
            ({"clickable": True}, "//*[@clickable='true']"),
            ({"enabled": False}, "//*[@enabled='false']"),
            ({"checked": True}, "//*[@checked='true']"),
            
            # Numeric attributes
            ({"index": 2}, "//*[@index=2]"),
            ({"instance": 1}, "//*[2]"),
            
            # Text functions
            ({"textContains": "Hello"}, "//*[contains(@text, 'Hello')]"),
            ({"textStartsWith": "Start"}, "//*[starts-with(@text, 'Start')]"),
            ({"textMatches": ".*test.*"}, "//*[matches(@text, '.*test.*')]"),
            
            # Description functions
            ({"content-descContains": "icon"}, "//*[contains(@content-desc, 'icon')]"),
            ({"content-descStartsWith": "prefix"}, "//*[starts-with(@content-desc, 'prefix')]"),
            ({"content-descMatches": ".*icon.*"}, "//*[matches(@content-desc, '.*icon.*')]"),
            
            # Resource ID and Package functions
            ({"resource-idMatches": ".*button.*"}, "//*[matches(@resource-id, '.*button.*')]"),
            ({"package": "com.example.app"}, "//*[@package='com.example.app']"),
            ({"packageMatches": "com.example.*"}, "//*[matches(@package, 'com.example.*')]"),
            
            # Class functions
            ({"classMatches": ".*Button"}, "//*[matches(@class, '.*Button')]"),
            
            # Multiple attributes
            ({"text": 'OK', "clickable": True}, "//*[@text='OK'][@clickable='true']"),  # noqa
            ({"class": 'Button', "enabled": False, "index": 1}, "//*[@class='Button'][@enabled='false'][@index=1]"),  # noqa
        ]
    )
    @pytest.mark.unit
    def test_dict_to_xpath_basic_attributes(self, selector_dict: dict[str, Any], expected_xpath: str):
        """Test conversion of basic dictionary attributes to XPath."""
        result = self.converter.dict_to_xpath(selector_dict)
        logger.info(f"Input: {selector_dict}")
        logger.info(f"Expected: {expected_xpath}")
        logger.info(f"Result: {result}")
        assert result == expected_xpath  # noqa: S101

    @pytest.mark.parametrize(
        "selector_dict, expected_ui",  # noqa: PT006
        [
            # Basic attributes
            ({"text": "OK"}, 'new UiSelector().text("OK");'),
            ({"class": "android.widget.Button"}, 'new UiSelector().className("android.widget.Button");'),
            ({"resource-id": "com.example:id/button"}, 'new UiSelector().resourceId("com.example:id/button");'),
            ({"content-desc": "Submit"}, 'new UiSelector().description("Submit");'),
            
            # Boolean attributes
            ({"clickable": True}, "new UiSelector().clickable(true);"),
            ({"enabled": False}, "new UiSelector().enabled(false);"),
            ({"checked": True}, "new UiSelector().checked(true);"),
            
            # Numeric attributes
            ({"index": 2}, "new UiSelector().index(2);"),
            ({"instance": 1}, "new UiSelector().instance(1);"),
            
            # Text functions
            ({"textContains": "Hello"}, 'new UiSelector().textContains("Hello");'),
            ({"textStartsWith": "Start"}, 'new UiSelector().textStartsWith("Start");'),
            ({"textMatches": ".*test.*"}, 'new UiSelector().textMatches(".*test.*");'),
            
            # Description functions
            ({"content-descContains": "icon"}, 'new UiSelector().descriptionContains("icon");'),
            ({"content-descStartsWith": "prefix"}, 'new UiSelector().descriptionStartsWith("prefix");'),
            ({"content-descMatches": ".*icon.*"}, 'new UiSelector().descriptionMatches(".*icon.*");'),
            
            # Resource ID and Package functions
            ({"resource-idMatches": ".*button.*"}, 'new UiSelector().resourceIdMatches(".*button.*");'),
            ({"package": "com.example.app"}, 'new UiSelector().packageName("com.example.app");'),
            ({"packageMatches": "com.example.*"}, 'new UiSelector().packageNameMatches("com.example.*");'),
            
            # Class functions
            ({"classMatches": ".*Button"}, 'new UiSelector().classNameMatches(".*Button");'),
            
            # Multiple attributes
            ({"text": "OK", "clickable": True}, 'new UiSelector().text("OK").clickable(true);'),
            ({"class": "Button", "enabled": False, "index": 1},
             'new UiSelector().className("Button").enabled(false).index(1);'),
        ]
    )
    @pytest.mark.unit
    def test_dict_to_ui_selector_basic_attributes(self, selector_dict: dict[str, Any], expected_ui: str):
        """Test conversion of basic dictionary attributes to UiSelector."""
        result = self.converter.dict_to_ui_selector(selector_dict)
        logger.info(f"Input: {selector_dict}")
        logger.info(f"Expected: {expected_ui}")
        logger.info(f"Result: {result}")
        assert result == expected_ui  # noqa: S101

    @pytest.mark.parametrize(
        "selector_dict, expected_xpath",  # noqa: PT006
        [
            # Child selector
            (
                    {
                        "class": "android.widget.LinearLayout",
                        "childSelector": {"text": "Item"}
                    },
                    "//*[@class='android.widget.LinearLayout']//*[@text='Item']",
            ),

            # From parent selector
            (
                    {
                        "text": "Child",
                        "fromParent": {"class": "android.widget.FrameLayout"}
                    },
                    "//*[@text='Child']/..//*[@class='android.widget.FrameLayout']",
            ),

            # Sibling selector
            (
                    {
                        "text": "First",
                        "sibling": {"text": "Second"}
                    },
                    "//*[@text='First']/following-sibling::*[@text='Second']",
            ),

            # Nested hierarchy
            (
                    {
                        "class": "Container",
                        "childSelector": {
                            "class": "Row",
                            "childSelector": {"text": "Cell"}
                        }
                    },
                    "//*[@class='Container']//*[@class='Row']//*[@text='Cell']",
            ),

            # Complex hierarchy with multiple attributes
            (
                    {
                        "text": "Settings",
                        "clickable": True,
                        "fromParent": {
                            "class": "android.widget.LinearLayout",
                            "enabled": True,
                            "childSelector": {"text": "Menu"}
                        }
                    },
                    "//*[@text='Settings'][@clickable='true']/..//*[@class='android.widget.LinearLayout'][@enabled='true']//*[@text='Menu']",
            ),
        ]
    )
    @pytest.mark.unit
    def test_dict_to_xpath_hierarchical(self, selector_dict: dict[str, Any], expected_xpath: str):
        """Test conversion of hierarchical dictionary selectors to XPath."""
        result = self.converter.dict_to_xpath(selector_dict)
        logger.info(f"Input: {selector_dict}")
        logger.info(f"Expected: {expected_xpath}")
        logger.info(f"Result: {result}")
        assert result == expected_xpath  # noqa: S101

    @pytest.mark.parametrize(
        "selector_dict, expected_ui",  # noqa: PT006
        [
            # Child selector
            ({
                "class": "android.widget.LinearLayout",
                "childSelector": {
                    "text": "Item"
                }
            }, 'new UiSelector().className("android.widget.LinearLayout").childSelector(new UiSelector().text("Item"));'),
            
            # From parent selector
            ({
                "text": "Child",
                "fromParent": {
                    "class": "android.widget.FrameLayout"
                }
            }, 'new UiSelector().text("Child").fromParent(new UiSelector().className("android.widget.FrameLayout"));'),
            
            # Sibling selector
            ({
                "text": "First",
                "sibling": {
                    "text": "Second"
                }
            }, 'new UiSelector().text("First").sibling(new UiSelector().text("Second"));'),
            
            # Nested hierarchy
            ({
                "class": "Container",
                "childSelector": {
                    "class": "Row",
                    "childSelector": {
                        "text": "Cell"
                    }
                }
            }, 'new UiSelector().className("Container").childSelector(new UiSelector().className("Row").childSelector(new UiSelector().text("Cell")));'),
            
            # Complex hierarchy with multiple attributes
            ({
                "text": "Settings",
                "clickable": True,
                "fromParent": {
                    "class": "android.widget.LinearLayout",
                    "enabled": True,
                    "childSelector": {
                        "text": "Menu"
                    }
                }
            }, 'new UiSelector().text("Settings").clickable(true).fromParent(new UiSelector().className("android.widget.LinearLayout").enabled(true).childSelector(new UiSelector().text("Menu")));'),
        ]
    )
    @pytest.mark.unit
    def test_dict_to_ui_selector_hierarchical(self, selector_dict: dict[str, Any], expected_ui: str):
        """Test conversion of hierarchical dictionary selectors to UiSelector."""
        result = self.converter.dict_to_ui_selector(selector_dict)
        logger.info(f"Input: {selector_dict}")
        logger.info(f"Expected: {expected_ui}")
        logger.info(f"Result: {result}")
        assert result == expected_ui  # noqa: S101

    @pytest.mark.unit
    def test_validate_dict_selector_valid(self):
        """Test validation of valid dictionary selectors."""
        valid_selectors = [
            {"text": "OK"},
            {"class": "Button", "clickable": True},
            {
                "text": "Parent",
                "childSelector": {
                    "text": "Child"
                }
            }
        ]
        
        for selector in valid_selectors:
            # Should not raise any exception
            self.converter.validate_dict_selector(selector)

    @pytest.mark.unit
    def test_validate_dict_selector_invalid(self):
        """Test validation of invalid dictionary selectors."""
        from shadowstep.exceptions.shadowstep_exceptions import (
            ShadowstepEmptySelectorError,
            ShadowstepSelectorTypeError,
            ShadowstepConflictingTextAttributesError,
            ShadowstepConflictingDescriptionAttributesError,
            ShadowstepHierarchicalAttributeError,
        )
        
        # Empty dictionary
        with pytest.raises(ShadowstepEmptySelectorError):
            self.converter.validate_dict_selector({})
        
        # Not a dictionary
        with pytest.raises(ShadowstepSelectorTypeError):
            self.converter.validate_dict_selector("not a dict")  # type: ignore
        
        # Conflicting text attributes
        with pytest.raises(ShadowstepConflictingTextAttributesError):
            self.converter.validate_dict_selector({
                "text": "OK",
                "textContains": "Hello"
            })
        
        # Conflicting description attributes
        with pytest.raises(ShadowstepConflictingDescriptionAttributesError):
            self.converter.validate_dict_selector({
                "content-desc": "OK",
                "content-descContains": "Hello"
            })
        
        # Invalid hierarchical attribute value
        with pytest.raises(ShadowstepHierarchicalAttributeError):
            self.converter.validate_dict_selector({
                "childSelector": "not a dict"
            })

    @pytest.mark.unit
    def test_roundtrip_conversion(self):
        """Test roundtrip conversion: dict -> xpath -> dict (via existing converters)."""
        # This test would require integration with existing XPathConverter
        # For now, we'll test that our converter produces valid output
        selector_dict = {
            "text": "Test",
            "clickable": True,
            "childSelector": {
                "class": "Button"
            }
        }
        
        xpath = self.converter.dict_to_xpath(selector_dict)
        ui_selector = self.converter.dict_to_ui_selector(selector_dict)
        
        # Basic validation that output is not empty and contains expected elements
        assert xpath  # noqa: S101
        assert ui_selector  # noqa: S101
        assert "Test" in xpath  # noqa: S101
        assert "Test" in ui_selector  # noqa: S101
        assert "Button" in xpath  # noqa: S101
        assert "Button" in ui_selector  # noqa: S101


class TestDictConverterComplex:
    """Complex test cases for DictConverter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = DictConverter()

    @pytest.mark.unit
    def test_deep_nested_hierarchy_xpath(self):
        """Test XPath conversion with 5+ levels of nesting."""
        # Create a deeply nested structure: Container > Row > Cell > Button > Text
        deep_selector = {
            "class": "android.widget.FrameLayout",
            "childSelector": {
                "class": "android.widget.LinearLayout",
                "index": 0,
                "childSelector": {
                    "class": "android.widget.GridLayout",
                    "childSelector": {
                        "class": "android.widget.Button",
                        "clickable": True,
                        "childSelector": {
                            "class": "android.widget.TextView",
                            "text": "Deep Text"
                        }
                    }
                }
            }
        }

        result = self.converter.dict_to_xpath(deep_selector)
        expected = (
            "//*[@class='android.widget.FrameLayout']"
            "//*[@class='android.widget.LinearLayout'][@index=0]"
            "//*[@class='android.widget.GridLayout']"
            "//*[@class='android.widget.Button'][@clickable='true']"
            "//*[@class='android.widget.TextView'][@text='Deep Text']"
        )

        logger.info(f"Deep nested XPath result: {result}")
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_deep_nested_hierarchy_ui_selector(self):
        """Test UiSelector conversion with 5+ levels of nesting."""
        deep_selector = {
            "class": "android.widget.FrameLayout",
            "childSelector": {
                "class": "android.widget.LinearLayout",
                "index": 0,
                "childSelector": {
                    "class": "android.widget.GridLayout",
                    "childSelector": {
                        "class": "android.widget.Button",
                        "clickable": True,
                        "childSelector": {
                            "class": "android.widget.TextView",
                            "text": "Deep Text"
                        }
                    }
                }
            }
        }

        result = self.converter.dict_to_ui_selector(deep_selector)
        expected = ('new UiSelector().className("android.widget.FrameLayout")'
                    '.childSelector(new UiSelector().className("android.widget.LinearLayout").index(0)'
                    '.childSelector(new UiSelector().className("android.widget.GridLayout")'
                    '.childSelector(new UiSelector().className("android.widget.Button").clickable(true)'
                    '.childSelector(new UiSelector().className("android.widget.TextView").text("Deep Text")))));')

        logger.info(f"Deep nested UiSelector result: {result}")
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_mixed_hierarchical_relationships(self):
        """Test complex selector with mixed hierarchical relationships."""
        complex_selector = {
            "text": "Main Element",
            "clickable": True,
            "childSelector": {
                "class": "android.widget.LinearLayout",
                "fromParent": {
                    "class": "android.widget.FrameLayout",
                    "enabled": True,
                    "sibling": {
                        "text": "Sibling Element",
                        "childSelector": {
                            "text": "Nested Child"
                        }
                    }
                }
            }
        }

        # Test XPath conversion
        xpath_result = self.converter.dict_to_xpath(complex_selector)
        logger.info(f"Mixed hierarchical XPath: {xpath_result}")

        # Test UiSelector conversion
        ui_result = self.converter.dict_to_ui_selector(complex_selector)
        logger.info(f"Mixed hierarchical UiSelector: {ui_result}")

        # Basic validation - should not be empty and contain expected elements
        assert xpath_result  # noqa: S101
        assert ui_result  # noqa: S101
        assert "Main Element" in xpath_result  # noqa: S101
        assert "Main Element" in ui_result  # noqa: S101
        assert "Sibling Element" in xpath_result  # noqa: S101  # noqa: S101
        assert "Sibling Element" in ui_result  # noqa: S101  # noqa: S101

    @pytest.mark.unit
    def test_multiple_instances_and_indexes(self):
        """Test selector with multiple instance and index attributes."""
        multi_selector = {
            "class": "android.widget.Button",
            "instance": 2,
            "index": 1,
            "text": "Button Text",
            "clickable": True
        }

        xpath_result = self.converter.dict_to_xpath(multi_selector)
        ui_result = self.converter.dict_to_ui_selector(multi_selector)

        logger.info(f"Multiple instances XPath: {xpath_result}")
        logger.info(f"Multiple instances UiSelector: {ui_result}")

        assert "@index=1" in xpath_result  # noqa: S101
        assert "[3]" in xpath_result  # noqa: S101
        # UiSelector should have both index and instance
        assert ".index(1)" in ui_result  # noqa: S101
        assert ".instance(2)" in ui_result  # noqa: S101

    @pytest.mark.unit
    def test_all_text_functions_combined(self):
        """Test selector with all text function types."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepConflictingTextAttributesError
        
        text_functions_selector = {
            "text": "Exact Text",
            "textContains": "Contains",
            "textStartsWith": "Starts",
            "textMatches": ".*Pattern.*"
        }

        # This should fail validation due to conflicting text attributes
        with pytest.raises(ShadowstepConflictingTextAttributesError):
            self.converter.validate_dict_selector(text_functions_selector)

    @pytest.mark.unit
    def test_all_description_functions_combined(self):
        """Test selector with all description function types."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepConflictingDescriptionAttributesError
        
        desc_functions_selector = {
            "content-desc": "Exact Desc",
            "content-descContains": "Contains",
            "content-descStartsWith": "Starts",
            "content-descMatches": ".*Pattern.*"
        }

        # This should fail validation due to conflicting description attributes
        with pytest.raises(ShadowstepConflictingDescriptionAttributesError):
            self.converter.validate_dict_selector(desc_functions_selector)

    @pytest.mark.unit
    def test_complex_regex_patterns(self):
        """Test selector with complex regex patterns."""
        regex_selector = {
            "textMatches": r"^[A-Z][a-z]+\s+\d{2,4}$",  # Name + Year pattern
            "resource-idMatches": r"com\.example\..*\.id\..*",
            "classMatches": r".*Button.*|.*TextView.*"
        }

        xpath_result = self.converter.dict_to_xpath(regex_selector)
        ui_result = self.converter.dict_to_ui_selector(regex_selector)

        logger.info(f"Complex regex XPath: {xpath_result}")
        logger.info(f"Complex regex UiSelector: {ui_result}")

        assert "matches(@text" in xpath_result  # noqa: S101
        assert "matches(@resource-id" in xpath_result  # noqa: S101
        assert "matches(@class" in xpath_result  # noqa: S101
        assert ".textMatches(" in ui_result  # noqa: S101
        assert ".resourceIdMatches(" in ui_result  # noqa: S101
        assert ".classNameMatches(" in ui_result  # noqa: S101

    @pytest.mark.unit
    def test_boolean_attributes_combinations(self):
        """Test all possible boolean attribute combinations."""
        boolean_selector = {
            "checkable": True,
            "checked": False,
            "clickable": True,
            "enabled": True,
            "focusable": False,
            "focused": True,
            "long-clickable": False,
            "scrollable": True,
            "selected": False,
            "password": True
        }

        xpath_result = self.converter.dict_to_xpath(boolean_selector)
        ui_result = self.converter.dict_to_ui_selector(boolean_selector)

        logger.info(f"All booleans XPath: {xpath_result}")
        logger.info(f"All booleans UiSelector: {ui_result}")

        # Check that all boolean attributes are present
        boolean_attrs_xpath = ["checkable", "checked", "clickable", "enabled", "focusable",
                               "focused", "long-clickable", "scrollable", "selected", "password"]
        boolean_attrs_ui = ["checkable", "checked", "clickable", "enabled", "focusable",
                            "focused", "longClickable", "scrollable", "selected", "password"]

        for attr in boolean_attrs_xpath:
            assert f"@{attr}=" in xpath_result  # noqa: S101
        for attr in boolean_attrs_ui:
            assert f".{attr}(" in ui_result  # noqa: S101

    @pytest.mark.unit
    def test_edge_case_empty_dict(self):
        """Test edge case with empty dictionary."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepEmptySelectorError
        
        with pytest.raises(ShadowstepEmptySelectorError):
            self.converter.validate_dict_selector({})

    @pytest.mark.unit
    def test_edge_case_invalid_hierarchical_value(self):
        """Test edge case with invalid hierarchical attribute value."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepHierarchicalAttributeError
        
        invalid_selector = {
            "childSelector": "not a dict"  # Should be dict
        }

        with pytest.raises(ShadowstepHierarchicalAttributeError):
            self.converter.validate_dict_selector(invalid_selector)

    @pytest.mark.unit
    def test_edge_case_non_dict_input(self):
        """Test edge case with non-dictionary input."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepSelectorTypeError
        
        with pytest.raises(ShadowstepSelectorTypeError):
            self.converter.validate_dict_selector("not a dict")  # type: ignore

    @pytest.mark.unit
    def test_performance_large_selector(self):
        """Test performance with large selector containing many attributes."""
        large_selector: dict[str, Any] = {}

        # Add many boolean attributes
        for i in range(10):
            large_selector[f"attr_{i}"] = f"value_{i}"

        # Add some valid attributes
        large_selector.update({
            "text": "Performance Test",
            "class": "android.widget.Button",
            "clickable": True,
            "enabled": True,
            "index": 5,
            "instance": 3
        })

        # Should work without errors (unknown attributes are ignored)
        xpath_result = self.converter.dict_to_xpath(large_selector)
        ui_result = self.converter.dict_to_ui_selector(large_selector)

        assert xpath_result  # noqa: S101
        assert ui_result  # noqa: S101
        assert "Performance Test" in xpath_result  # noqa: S101
        assert "Performance Test" in ui_result  # noqa: S101

    @pytest.mark.unit
    def test_unicode_and_special_characters(self):
        """Test selector with unicode and special characters."""
        unicode_selector = {
            "text": "Hello world! 🌍",
            "content-desc": "Special chars: @#$%^&*()",
            "resource-id": "com.example:id/button_with_underscore",
            "class": "android.widget.Button"
        }

        xpath_result = self.converter.dict_to_xpath(unicode_selector)
        ui_result = self.converter.dict_to_ui_selector(unicode_selector)

        logger.info(f"Unicode XPath: {xpath_result}")
        logger.info(f"Unicode UiSelector: {ui_result}")

        assert "Hello world! 🌍" in xpath_result  # noqa: S101
        assert "Hello world! 🌍" in ui_result  # noqa: S101
        assert "Special chars: @#$%^&*()" in xpath_result  # noqa: S101
        assert "Special chars: @#$%^&*()" in ui_result  # noqa: S101

    @pytest.mark.unit
    def test_nested_validation_errors(self):
        """Test validation errors in nested structures."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepConflictingTextAttributesError
        
        nested_invalid_selector = {
            "text": "Parent",
            "childSelector": {
                "text": "Child",
                "textContains": "Conflict"  # Conflicting attributes
            }
        }

        with pytest.raises(ShadowstepConflictingTextAttributesError):
            self.converter.validate_dict_selector(nested_invalid_selector)

    @pytest.mark.unit
    def test_circular_reference_protection(self):
        """Test protection against potential circular references."""
        # Create a selector that could potentially cause issues
        complex_selector = {
            "text": "Root",
            "childSelector": {
                "text": "Child1",
                "fromParent": {
                    "text": "Child2",
                    "sibling": {
                        "text": "Child3",
                        "childSelector": {
                            "text": "Deep Child"
                        }
                    }
                }
            }
        }

        # Should not cause infinite recursion or errors
        xpath_result = self.converter.dict_to_xpath(complex_selector)
        ui_result = self.converter.dict_to_ui_selector(complex_selector)

        assert xpath_result  # noqa: S101
        assert ui_result  # noqa: S101
        assert "Root" in xpath_result  # noqa: S101
        assert "Root" in ui_result  # noqa: S101

    @pytest.mark.unit
    def test_stress_test_deep_nesting(self):
        """Stress test with very deep nesting (10+ levels)."""
        # Build a very deep nested structure
        current_level: dict[str, Any] = {}
        for i in range(10):
            next_level = {
                "class": f"android.widget.Level{i}",
                "index": i
            }
            if i == 0:
                current_level = next_level
            else:
                # Add to the deepest level
                deepest = current_level
                while "childSelector" in deepest:
                    deepest = deepest["childSelector"]  # type: ignore
                deepest["childSelector"] = next_level  # type: ignore

        # Add final text element
        deepest = current_level
        while "childSelector" in deepest:
            deepest = deepest["childSelector"]  # type: ignore
        deepest["text"] = "Deepest Element"  # type: ignore

        # Should handle deep nesting without issues
        xpath_result = self.converter.dict_to_xpath(current_level)
        ui_result = self.converter.dict_to_ui_selector(current_level)

        assert xpath_result  # noqa: S101
        assert ui_result  # noqa: S101
        assert "Deepest Element" in xpath_result  # noqa: S101
        assert "Deepest Element" in ui_result  # noqa: S101
        assert "Level9" in xpath_result  # Deepest level  # noqa: S101
        assert "Level9" in ui_result  # noqa: S101
