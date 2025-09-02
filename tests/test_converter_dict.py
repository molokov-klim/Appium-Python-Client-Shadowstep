# tests/test_converter_dict.py
import logging
from typing import Any

import pytest

from shadowstep.locator.converter.dict_converter import DictConverter
from shadowstep.locator.types.shadowstep_dict import DictAttribute

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
            ({DictAttribute.TEXT: "OK"}, '//*[@text="OK"]'),
            ({DictAttribute.CLASS_NAME: "android.widget.Button"}, '//*[@class="android.widget.Button"]'),
            ({DictAttribute.RESOURCE_ID: "com.example:id/button"}, '//*[@resource-id="com.example:id/button"]'),
            ({DictAttribute.DESCRIPTION: "Submit"}, '//*[@content-desc="Submit"]'),
            
            # Boolean attributes
            ({DictAttribute.CLICKABLE: True}, '//*[@clickable="true"]'),
            ({DictAttribute.ENABLED: False}, '//*[@enabled="false"]'),
            ({DictAttribute.CHECKED: True}, '//*[@checked="true"]'),
            
            # Numeric attributes
            ({DictAttribute.INDEX: 2}, "//*[position()=3]"),
            ({DictAttribute.INSTANCE: 1}, "//*[2]"),
            
            # Text functions
            ({DictAttribute.TEXT_CONTAINS: "Hello"}, '//*[contains(@text, "Hello")]'),
            ({DictAttribute.TEXT_STARTS_WITH: "Start"}, '//*[starts-with(@text, "Start")]'),
            ({DictAttribute.TEXT_MATCHES: ".*test.*"}, '//*[matches(@text, ".*test.*")]'),
            
            # Description functions
            ({DictAttribute.DESCRIPTION_CONTAINS: "icon"}, '//*[contains(@content-desc, "icon")]'),
            ({DictAttribute.DESCRIPTION_STARTS_WITH: "prefix"}, '//*[starts-with(@content-desc, "prefix")]'),
            ({DictAttribute.DESCRIPTION_MATCHES: ".*icon.*"}, '//*[matches(@content-desc, ".*icon.*")]'),
            
            # Resource ID and Package functions
            ({DictAttribute.RESOURCE_ID_MATCHES: ".*button.*"}, '//*[matches(@resource-id, ".*button.*")]'),
            ({DictAttribute.PACKAGE_NAME: "com.example.app"}, '//*[@package="com.example.app"]'),
            ({DictAttribute.PACKAGE_NAME_MATCHES: "com.example.*"}, '//*[matches(@package, "com.example.*")]'),
            
            # Class functions
            ({DictAttribute.CLASS_NAME_MATCHES: ".*Button"}, '//*[matches(@class, ".*Button")]'),
            
            # Multiple attributes
            ({DictAttribute.TEXT: "OK", DictAttribute.CLICKABLE: True}, '//*[@text="OK"][@clickable="true"]'),
            ({DictAttribute.CLASS_NAME: "Button", DictAttribute.ENABLED: False, DictAttribute.INDEX: 1},
             '//*[@class="Button"][@enabled="false"][position()=2]'),
        ]
    )
    def test_dict_to_xpath_basic_attributes(self, selector_dict: dict[str, Any], expected_xpath: str):
        """Test conversion of basic dictionary attributes to XPath."""
        result = self.converter.dict_to_xpath(selector_dict)
        logger.info(f"Input: {selector_dict}")
        logger.info(f"Expected: {expected_xpath}")
        logger.info(f"Result: {result}")
        assert result == expected_xpath

    @pytest.mark.parametrize(
        "selector_dict, expected_ui",  # noqa: PT006
        [
            # Basic attributes
            ({DictAttribute.TEXT: "OK"}, 'new UiSelector().text("OK");'),
            ({DictAttribute.CLASS_NAME: "android.widget.Button"}, 'new UiSelector().className("android.widget.Button");'),
            ({DictAttribute.RESOURCE_ID: "com.example:id/button"}, 'new UiSelector().resourceId("com.example:id/button");'),
            ({DictAttribute.DESCRIPTION: "Submit"}, 'new UiSelector().description("Submit");'),
            
            # Boolean attributes
            ({DictAttribute.CLICKABLE: True}, "new UiSelector().clickable(true);"),
            ({DictAttribute.ENABLED: False}, "new UiSelector().enabled(false);"),
            ({DictAttribute.CHECKED: True}, "new UiSelector().checked(true);"),
            
            # Numeric attributes
            ({DictAttribute.INDEX: 2}, "new UiSelector().index(2);"),
            ({DictAttribute.INSTANCE: 1}, "new UiSelector().instance(1);"),
            
            # Text functions
            ({DictAttribute.TEXT_CONTAINS: "Hello"}, 'new UiSelector().textContains("Hello");'),
            ({DictAttribute.TEXT_STARTS_WITH: "Start"}, 'new UiSelector().textStartsWith("Start");'),
            ({DictAttribute.TEXT_MATCHES: ".*test.*"}, 'new UiSelector().textMatches(".*test.*");'),
            
            # Description functions
            ({DictAttribute.DESCRIPTION_CONTAINS: "icon"}, 'new UiSelector().descriptionContains("icon");'),
            ({DictAttribute.DESCRIPTION_STARTS_WITH: "prefix"}, 'new UiSelector().descriptionStartsWith("prefix");'),
            ({DictAttribute.DESCRIPTION_MATCHES: ".*icon.*"}, 'new UiSelector().descriptionMatches(".*icon.*");'),
            
            # Resource ID and Package functions
            ({DictAttribute.RESOURCE_ID_MATCHES: ".*button.*"}, 'new UiSelector().resourceIdMatches(".*button.*");'),
            ({DictAttribute.PACKAGE_NAME: "com.example.app"}, 'new UiSelector().packageName("com.example.app");'),
            ({DictAttribute.PACKAGE_NAME_MATCHES: "com.example.*"}, 'new UiSelector().packageNameMatches("com.example.*");'),
            
            # Class functions
            ({DictAttribute.CLASS_NAME_MATCHES: ".*Button"}, 'new UiSelector().classNameMatches(".*Button");'),
            
            # Multiple attributes
            ({DictAttribute.TEXT: "OK", DictAttribute.CLICKABLE: True}, 'new UiSelector().text("OK").clickable(true);'),
            ({DictAttribute.CLASS_NAME: "Button", DictAttribute.ENABLED: False, DictAttribute.INDEX: 1},
             'new UiSelector().className("Button").enabled(false).index(1);'),
        ]
    )
    def test_dict_to_ui_selector_basic_attributes(self, selector_dict: dict[str, Any], expected_ui: str):
        """Test conversion of basic dictionary attributes to UiSelector."""
        result = self.converter.dict_to_ui_selector(selector_dict)
        logger.info(f"Input: {selector_dict}")
        logger.info(f"Expected: {expected_ui}")
        logger.info(f"Result: {result}")
        assert result == expected_ui

    @pytest.mark.parametrize(
        "selector_dict, expected_xpath",  # noqa: PT006
        [
            # Child selector
            ({
                DictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                DictAttribute.CHILD_SELECTOR: {
                    DictAttribute.TEXT: "Item"
                }
            }, '//*[@class="android.widget.LinearLayout"]/*[@text="Item"]'),
            
            # From parent selector
            ({
                DictAttribute.TEXT: "Child",
                DictAttribute.FROM_PARENT: {
                    DictAttribute.CLASS_NAME: "android.widget.FrameLayout"
                }
            }, '//*[@text="Child"]/..//*[@class="android.widget.FrameLayout"]'),
            
            # Sibling selector
            ({
                DictAttribute.TEXT: "First",
                DictAttribute.SIBLING: {
                    DictAttribute.TEXT: "Second"
                }
            }, '//*[@text="First"]/following-sibling::*[@text="Second"]'),
            
            # Nested hierarchy
            ({
                DictAttribute.CLASS_NAME: "Container",
                DictAttribute.CHILD_SELECTOR: {
                    DictAttribute.CLASS_NAME: "Row",
                    DictAttribute.CHILD_SELECTOR: {
                        DictAttribute.TEXT: "Cell"
                    }
                }
            }, '//*[@class="Container"]/*[@class="Row"]/*[@text="Cell"]'),
            
            # Complex hierarchy with multiple attributes
            ({
                DictAttribute.TEXT: "Settings",
                DictAttribute.CLICKABLE: True,
                DictAttribute.FROM_PARENT: {
                    DictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                    DictAttribute.ENABLED: True,
                    DictAttribute.CHILD_SELECTOR: {
                        DictAttribute.TEXT: "Menu"
                    }
                }
            }, '//*[@text="Settings"][@clickable="true"]/..//*[@class="android.widget.LinearLayout"][@enabled="true"]/*[@text="Menu"]'),
        ]
    )
    def test_dict_to_xpath_hierarchical(self, selector_dict: dict[str, Any], expected_xpath: str):
        """Test conversion of hierarchical dictionary selectors to XPath."""
        result = self.converter.dict_to_xpath(selector_dict)
        logger.info(f"Input: {selector_dict}")
        logger.info(f"Expected: {expected_xpath}")
        logger.info(f"Result: {result}")
        assert result == expected_xpath

    @pytest.mark.parametrize(
        "selector_dict, expected_ui",  # noqa: PT006
        [
            # Child selector
            ({
                DictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                DictAttribute.CHILD_SELECTOR: {
                    DictAttribute.TEXT: "Item"
                }
            }, 'new UiSelector().className("android.widget.LinearLayout").childSelector(new UiSelector().text("Item"));'),
            
            # From parent selector
            ({
                DictAttribute.TEXT: "Child",
                DictAttribute.FROM_PARENT: {
                    DictAttribute.CLASS_NAME: "android.widget.FrameLayout"
                }
            }, 'new UiSelector().text("Child").fromParent(new UiSelector().className("android.widget.FrameLayout"));'),
            
            # Sibling selector
            ({
                DictAttribute.TEXT: "First",
                DictAttribute.SIBLING: {
                    DictAttribute.TEXT: "Second"
                }
            }, 'new UiSelector().text("First").sibling(new UiSelector().text("Second"));'),
            
            # Nested hierarchy
            ({
                DictAttribute.CLASS_NAME: "Container",
                DictAttribute.CHILD_SELECTOR: {
                    DictAttribute.CLASS_NAME: "Row",
                    DictAttribute.CHILD_SELECTOR: {
                        DictAttribute.TEXT: "Cell"
                    }
                }
            }, 'new UiSelector().className("Container").childSelector(new UiSelector().className("Row").childSelector(new UiSelector().text("Cell")));'),
            
            # Complex hierarchy with multiple attributes
            ({
                DictAttribute.TEXT: "Settings",
                DictAttribute.CLICKABLE: True,
                DictAttribute.FROM_PARENT: {
                    DictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                    DictAttribute.ENABLED: True,
                    DictAttribute.CHILD_SELECTOR: {
                        DictAttribute.TEXT: "Menu"
                    }
                }
            }, 'new UiSelector().text("Settings").clickable(true).fromParent(new UiSelector().className("android.widget.LinearLayout").enabled(true).childSelector(new UiSelector().text("Menu")));'),
        ]
    )
    def test_dict_to_ui_selector_hierarchical(self, selector_dict: dict[str, Any], expected_ui: str):
        """Test conversion of hierarchical dictionary selectors to UiSelector."""
        result = self.converter.dict_to_ui_selector(selector_dict)
        logger.info(f"Input: {selector_dict}")
        logger.info(f"Expected: {expected_ui}")
        logger.info(f"Result: {result}")
        assert result == expected_ui

    def test_validate_dict_selector_valid(self):
        """Test validation of valid dictionary selectors."""
        valid_selectors = [
            {DictAttribute.TEXT: "OK"},
            {DictAttribute.CLASS_NAME: "Button", DictAttribute.CLICKABLE: True},
            {
                DictAttribute.TEXT: "Parent",
                DictAttribute.CHILD_SELECTOR: {
                    DictAttribute.TEXT: "Child"
                }
            }
        ]
        
        for selector in valid_selectors:
            # Should not raise any exception
            self.converter.validate_dict_selector(selector)

    def test_validate_dict_selector_invalid(self):
        """Test validation of invalid dictionary selectors."""
        # Empty dictionary
        with pytest.raises(ValueError, match="Selector dictionary cannot be empty"):
            self.converter.validate_dict_selector({})
        
        # Not a dictionary
        with pytest.raises(ValueError, match="Selector must be a dictionary"):
            self.converter.validate_dict_selector("not a dict")
        
        # Conflicting text attributes
        with pytest.raises(ValueError, match="Conflicting text attributes"):
            self.converter.validate_dict_selector({
                DictAttribute.TEXT: "OK",
                DictAttribute.TEXT_CONTAINS: "Hello"
            })
        
        # Conflicting description attributes
        with pytest.raises(ValueError, match="Conflicting description attributes"):
            self.converter.validate_dict_selector({
                DictAttribute.DESCRIPTION: "OK",
                DictAttribute.DESCRIPTION_CONTAINS: "Hello"
            })
        
        # Invalid hierarchical attribute value
        with pytest.raises(ValueError, match="Hierarchical attribute.*must have dict value"):
            self.converter.validate_dict_selector({
                DictAttribute.CHILD_SELECTOR: "not a dict"
            })

    def test_roundtrip_conversion(self):
        """Test roundtrip conversion: dict -> xpath -> dict (via existing converters)."""
        # This test would require integration with existing XPathConverter
        # For now, we'll test that our converter produces valid output
        selector_dict = {
            DictAttribute.TEXT: "Test",
            DictAttribute.CLICKABLE: True,
            DictAttribute.CHILD_SELECTOR: {
                DictAttribute.CLASS_NAME: "Button"
            }
        }
        
        xpath = self.converter.dict_to_xpath(selector_dict)
        ui_selector = self.converter.dict_to_ui_selector(selector_dict)
        
        # Basic validation that output is not empty and contains expected elements
        assert xpath
        assert ui_selector
        assert "Test" in xpath
        assert "Test" in ui_selector
        assert "Button" in xpath
        assert "Button" in ui_selector


class TestDictConverterComplex:
    """Complex test cases for DictConverter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = DictConverter()

    def test_deep_nested_hierarchy_xpath(self):
        """Test XPath conversion with 5+ levels of nesting."""
        # Create a deeply nested structure: Container > Row > Cell > Button > Text
        deep_selector = {
            DictAttribute.CLASS_NAME: "android.widget.FrameLayout",
            DictAttribute.CHILD_SELECTOR: {
                DictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                DictAttribute.INDEX: 0,
                DictAttribute.CHILD_SELECTOR: {
                    DictAttribute.CLASS_NAME: "android.widget.GridLayout",
                    DictAttribute.CHILD_SELECTOR: {
                        DictAttribute.CLASS_NAME: "android.widget.Button",
                        DictAttribute.CLICKABLE: True,
                        DictAttribute.CHILD_SELECTOR: {
                            DictAttribute.CLASS_NAME: "android.widget.TextView",
                            DictAttribute.TEXT: "Deep Text"
                        }
                    }
                }
            }
        }

        result = self.converter.dict_to_xpath(deep_selector)
        expected = ('//*[@class="android.widget.FrameLayout"]'
                    '/*[@class="android.widget.LinearLayout"][position()=1]'
                    '/*[@class="android.widget.GridLayout"]'
                    '/*[@class="android.widget.Button"][@clickable="true"]'
                    '/*[@class="android.widget.TextView"][@text="Deep Text"]')

        logger.info(f"Deep nested XPath result: {result}")
        assert result == expected

    def test_deep_nested_hierarchy_ui_selector(self):
        """Test UiSelector conversion with 5+ levels of nesting."""
        deep_selector = {
            DictAttribute.CLASS_NAME: "android.widget.FrameLayout",
            DictAttribute.CHILD_SELECTOR: {
                DictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                DictAttribute.INDEX: 0,
                DictAttribute.CHILD_SELECTOR: {
                    DictAttribute.CLASS_NAME: "android.widget.GridLayout",
                    DictAttribute.CHILD_SELECTOR: {
                        DictAttribute.CLASS_NAME: "android.widget.Button",
                        DictAttribute.CLICKABLE: True,
                        DictAttribute.CHILD_SELECTOR: {
                            DictAttribute.CLASS_NAME: "android.widget.TextView",
                            DictAttribute.TEXT: "Deep Text"
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
        assert result == expected

    def test_mixed_hierarchical_relationships(self):
        """Test complex selector with mixed hierarchical relationships."""
        complex_selector = {
            DictAttribute.TEXT: "Main Element",
            DictAttribute.CLICKABLE: True,
            DictAttribute.CHILD_SELECTOR: {
                DictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                DictAttribute.FROM_PARENT: {
                    DictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                    DictAttribute.ENABLED: True,
                    DictAttribute.SIBLING: {
                        DictAttribute.TEXT: "Sibling Element",
                        DictAttribute.CHILD_SELECTOR: {
                            DictAttribute.TEXT: "Nested Child"
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
        assert xpath_result
        assert ui_result
        assert "Main Element" in xpath_result
        assert "Main Element" in ui_result
        assert "Sibling Element" in xpath_result
        assert "Sibling Element" in ui_result

    def test_multiple_instances_and_indexes(self):
        """Test selector with multiple instance and index attributes."""
        multi_selector = {
            DictAttribute.CLASS_NAME: "android.widget.Button",
            DictAttribute.INSTANCE: 2,
            DictAttribute.INDEX: 1,
            DictAttribute.TEXT: "Button Text",
            DictAttribute.CLICKABLE: True
        }

        xpath_result = self.converter.dict_to_xpath(multi_selector)
        ui_result = self.converter.dict_to_ui_selector(multi_selector)

        logger.info(f"Multiple instances XPath: {xpath_result}")
        logger.info(f"Multiple instances UiSelector: {ui_result}")

        # XPath should have both position() and [n] syntax
        assert "position()=2" in xpath_result
        assert "[3]" in xpath_result
        # UiSelector should have both index and instance
        assert ".index(1)" in ui_result
        assert ".instance(2)" in ui_result

    def test_all_text_functions_combined(self):
        """Test selector with all text function types."""
        text_functions_selector = {
            DictAttribute.TEXT: "Exact Text",
            DictAttribute.TEXT_CONTAINS: "Contains",
            DictAttribute.TEXT_STARTS_WITH: "Starts",
            DictAttribute.TEXT_MATCHES: ".*Pattern.*"
        }

        # This should fail validation due to conflicting text attributes
        with pytest.raises(ValueError, match="Conflicting text attributes"):
            self.converter.validate_dict_selector(text_functions_selector)

    def test_all_description_functions_combined(self):
        """Test selector with all description function types."""
        desc_functions_selector = {
            DictAttribute.DESCRIPTION: "Exact Desc",
            DictAttribute.DESCRIPTION_CONTAINS: "Contains",
            DictAttribute.DESCRIPTION_STARTS_WITH: "Starts",
            DictAttribute.DESCRIPTION_MATCHES: ".*Pattern.*"
        }

        # This should fail validation due to conflicting description attributes
        with pytest.raises(ValueError, match="Conflicting description attributes"):
            self.converter.validate_dict_selector(desc_functions_selector)

    def test_complex_regex_patterns(self):
        """Test selector with complex regex patterns."""
        regex_selector = {
            DictAttribute.TEXT_MATCHES: r"^[A-Z][a-z]+\s+\d{2,4}$",  # Name + Year pattern
            DictAttribute.RESOURCE_ID_MATCHES: r"com\.example\..*\.id\..*",
            DictAttribute.CLASS_NAME_MATCHES: r".*Button.*|.*TextView.*"
        }

        xpath_result = self.converter.dict_to_xpath(regex_selector)
        ui_result = self.converter.dict_to_ui_selector(regex_selector)

        logger.info(f"Complex regex XPath: {xpath_result}")
        logger.info(f"Complex regex UiSelector: {ui_result}")

        assert "matches(@text" in xpath_result
        assert "matches(@resource-id" in xpath_result
        assert "matches(@class" in xpath_result
        assert ".textMatches(" in ui_result
        assert ".resourceIdMatches(" in ui_result
        assert ".classNameMatches(" in ui_result

    def test_boolean_attributes_combinations(self):
        """Test all possible boolean attribute combinations."""
        boolean_selector = {
            DictAttribute.CHECKABLE: True,
            DictAttribute.CHECKED: False,
            DictAttribute.CLICKABLE: True,
            DictAttribute.ENABLED: True,
            DictAttribute.FOCUSABLE: False,
            DictAttribute.FOCUSED: True,
            DictAttribute.LONG_CLICKABLE: False,
            DictAttribute.SCROLLABLE: True,
            DictAttribute.SELECTED: False,
            DictAttribute.PASSWORD: True
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
            assert f"@{attr}=" in xpath_result
        for attr in boolean_attrs_ui:
            assert f".{attr}(" in ui_result

    def test_edge_case_empty_dict(self):
        """Test edge case with empty dictionary."""
        with pytest.raises(ValueError, match="Selector dictionary cannot be empty"):
            self.converter.validate_dict_selector({})

    def test_edge_case_invalid_hierarchical_value(self):
        """Test edge case with invalid hierarchical attribute value."""
        invalid_selector = {
            DictAttribute.CHILD_SELECTOR: "not a dict"  # Should be dict
        }

        with pytest.raises(ValueError, match="Hierarchical attribute.*must have dict value"):
            self.converter.validate_dict_selector(invalid_selector)

    def test_edge_case_non_dict_input(self):
        """Test edge case with non-dictionary input."""
        with pytest.raises(ValueError, match="Selector must be a dictionary"):
            self.converter.validate_dict_selector("not a dict")

    def test_performance_large_selector(self):
        """Test performance with large selector containing many attributes."""
        large_selector = {}

        # Add many boolean attributes
        for i in range(10):
            large_selector[f"attr_{i}"] = f"value_{i}"

        # Add some valid attributes
        large_selector.update({
            DictAttribute.TEXT: "Performance Test",
            DictAttribute.CLASS_NAME: "android.widget.Button",
            DictAttribute.CLICKABLE: True,
            DictAttribute.ENABLED: True,
            DictAttribute.INDEX: 5,
            DictAttribute.INSTANCE: 3
        })

        # Should work without errors (unknown attributes are ignored)
        xpath_result = self.converter.dict_to_xpath(large_selector)
        ui_result = self.converter.dict_to_ui_selector(large_selector)

        assert xpath_result
        assert ui_result
        assert "Performance Test" in xpath_result
        assert "Performance Test" in ui_result

    def test_unicode_and_special_characters(self):
        """Test selector with unicode and special characters."""
        unicode_selector = {
            DictAttribute.TEXT: "Привет мир! 🌍",
            DictAttribute.DESCRIPTION: "Special chars: @#$%^&*()",
            DictAttribute.RESOURCE_ID: "com.example:id/button_with_underscore",
            DictAttribute.CLASS_NAME: "android.widget.Button"
        }

        xpath_result = self.converter.dict_to_xpath(unicode_selector)
        ui_result = self.converter.dict_to_ui_selector(unicode_selector)

        logger.info(f"Unicode XPath: {xpath_result}")
        logger.info(f"Unicode UiSelector: {ui_result}")

        assert "Привет мир! 🌍" in xpath_result
        assert "Привет мир! 🌍" in ui_result
        assert "Special chars: @#$%^&*()" in xpath_result
        assert "Special chars: @#$%^&*()" in ui_result

    def test_nested_validation_errors(self):
        """Test validation errors in nested structures."""
        nested_invalid_selector = {
            DictAttribute.TEXT: "Parent",
            DictAttribute.CHILD_SELECTOR: {
                DictAttribute.TEXT: "Child",
                DictAttribute.TEXT_CONTAINS: "Conflict"  # Conflicting attributes
            }
        }

        with pytest.raises(ValueError, match="Conflicting text attributes"):
            self.converter.validate_dict_selector(nested_invalid_selector)

    def test_circular_reference_protection(self):
        """Test protection against potential circular references."""
        # Create a selector that could potentially cause issues
        complex_selector = {
            DictAttribute.TEXT: "Root",
            DictAttribute.CHILD_SELECTOR: {
                DictAttribute.TEXT: "Child1",
                DictAttribute.FROM_PARENT: {
                    DictAttribute.TEXT: "Child2",
                    DictAttribute.SIBLING: {
                        DictAttribute.TEXT: "Child3",
                        DictAttribute.CHILD_SELECTOR: {
                            DictAttribute.TEXT: "Deep Child"
                        }
                    }
                }
            }
        }

        # Should not cause infinite recursion or errors
        xpath_result = self.converter.dict_to_xpath(complex_selector)
        ui_result = self.converter.dict_to_ui_selector(complex_selector)

        assert xpath_result
        assert ui_result
        assert "Root" in xpath_result
        assert "Root" in ui_result

    def test_conversion_error_handling(self):
        """Test proper error handling during conversion."""
        # Create a selector that might cause conversion errors
        problematic_selector = {
            DictAttribute.INSTANCE: "not_a_number"  # Should be int
        }

        # Should handle the error gracefully - the converter logs warning but continues
        # because it treats unknown attributes as warnings, not errors
        xpath_result = self.converter.dict_to_xpath(problematic_selector)
        ui_result = self.converter.dict_to_ui_selector(problematic_selector)

        # The result should be empty or minimal since INSTANCE is treated as unknown
        assert xpath_result == "//*"  # Just the base XPath
        assert ui_result == "new UiSelector();"  # Just the base UiSelector

    def test_stress_test_deep_nesting(self):
        """Stress test with very deep nesting (10+ levels)."""
        # Build a very deep nested structure
        current_level: dict = {}
        for i in range(10):
            next_level = {
                DictAttribute.CLASS_NAME: f"android.widget.Level{i}",
                DictAttribute.INDEX: i
            }
            if i == 0:
                current_level = next_level
            else:
                # Add to the deepest level
                deepest = current_level
                while DictAttribute.CHILD_SELECTOR in deepest:
                    deepest = deepest[DictAttribute.CHILD_SELECTOR]  # type: ignore
                deepest[DictAttribute.CHILD_SELECTOR] = next_level  # type: ignore

        # Add final text element
        deepest = current_level
        while DictAttribute.CHILD_SELECTOR in deepest:
            deepest = deepest[DictAttribute.CHILD_SELECTOR]  # type: ignore
        deepest[DictAttribute.TEXT] = "Deepest Element"  # type: ignore

        # Should handle deep nesting without issues
        xpath_result = self.converter.dict_to_xpath(current_level)
        ui_result = self.converter.dict_to_ui_selector(current_level)

        assert xpath_result
        assert ui_result
        assert "Deepest Element" in xpath_result
        assert "Deepest Element" in ui_result
        assert "Level9" in xpath_result  # Deepest level
        assert "Level9" in ui_result
