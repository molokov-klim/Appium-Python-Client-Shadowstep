# tests/test_dict_converter.py
import logging
from typing import Any

import pytest

from shadowstep.locator_converter.dict_converter import DictConverter
from shadowstep.locator_converter.types.shadowstep_dict import DictAttribute

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
            ({DictAttribute.TEXT: "OK", DictAttribute.CLICKABLE: True}, '//*[@text="OK" and @clickable="true"]'),
            ({DictAttribute.CLASS_NAME: "Button", DictAttribute.ENABLED: False, DictAttribute.INDEX: 1},
             '//*[@class="Button" and @enabled="false" and position()=2]'),
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
            }, '//*[@text="Settings" and @clickable="true"]/..//*[@class="android.widget.LinearLayout" and @enabled="true"]/*[@text="Menu"]'),
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
