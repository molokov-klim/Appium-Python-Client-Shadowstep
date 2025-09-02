# shadowstep/locator/dict_converter.py
"""
DictConverter for converting Shadowstep dictionary locators to other formats.

This module provides the main DictConverter class that handles conversion
from Shadowstep dictionary format to XPath and UiSelector expressions.
"""
from __future__ import annotations

import logging
from typing import Any, Union

from shadowstep.exceptions.shadowstep_exceptions import ConversionError
from shadowstep.locator.map.dict_to_ui import (
    DICT_TO_UI_MAPPING,
    get_ui_method_for_hierarchical_attribute,
)
from shadowstep.locator.map.dict_to_xpath import (
    DICT_TO_XPATH_MAPPING,
    get_xpath_for_hierarchical_attribute,
)
from shadowstep.locator.types.shadowstep_dict import DictAttribute


class DictConverter:
    """
    Converter for Shadowstep dictionary locators to XPath and UiSelector formats.
    
    This class provides methods to convert dictionary-based locators to various
    formats including XPath expressions and UiSelector strings.
    """

    def __init__(self):
        """Initialize the converter with logging."""
        self.logger = logging.getLogger(__name__)

    def dict_to_xpath(self, selector_dict: dict[str, Any] | dict[DictAttribute, Any]) -> str:
        """
        Convert Shadowstep dictionary locator to XPath expression.
        
        Args:
            selector_dict: Dictionary representation of the selector
            
        Returns:
            XPath expression string
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            return self._dict_to_xpath_recursive(selector_dict, base_xpath="//*")
        except Exception as e:
            raise ConversionError(f"Failed to convert dict to XPath: {e}") from e

    def dict_to_ui_selector(self, selector_dict: Union[dict[str, Any], dict[DictAttribute, Any]]) -> str:
        """
        Convert Shadowstep dictionary locator to UiSelector string.
        
        Args:
            selector_dict: Dictionary representation of the selector
            
        Returns:
            UiSelector string
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            ui_selector = self._dict_to_ui_recursive(selector_dict)
            return f"new UiSelector(){ui_selector};"
        except Exception as e:
            raise ConversionError(f"Failed to convert dict to UiSelector: {e}") from e

    def _dict_to_xpath_recursive(self, selector_dict: dict[str, Any] | dict[DictAttribute, Any], base_xpath: str = "//*") -> str:  # noqa: C901
        """
        Recursively convert dictionary to XPath expression.
        
        Args:
            selector_dict: Dictionary representation of the selector
            base_xpath: Base XPath to start with
            
        Returns:
            XPath expression string
        """
        if not selector_dict:
            return base_xpath

        xpath_parts = []
        hierarchical_parts = []
        instance_part = None
        
        # Process regular attributes
        for key, value in selector_dict.items():
            if key in (DictAttribute.CHILD_SELECTOR, DictAttribute.FROM_PARENT, DictAttribute.SIBLING):
                # Handle hierarchical attributes separately
                hierarchical_parts.append((key, value))
                continue
                
            try:
                # Map UiSelector keys to DictAttribute keys
                key_mapping = {
                    "className": "class",
                    "classNameMatches": "classMatches",
                    "textContains": "textContains",
                    "textStartsWith": "textStartsWith", 
                    "textMatches": "textMatches",
                    "description": "content-desc",
                    "descriptionContains": "content-descContains",
                    "descriptionStartsWith": "content-descStartsWith",
                    "descriptionMatches": "content-descMatches",
                    "resourceId": "resource-id",
                    "resourceIdMatches": "resource-idMatches",
                    "packageName": "package",
                    "packageNameMatches": "packageMatches",
                    "longClickable": "long-clickable",
                }
                mapped_key = key_mapping.get(key, key)
                attr = DictAttribute(mapped_key)
                if attr == DictAttribute.INSTANCE:
                    # Handle instance separately as it affects the entire XPath
                    instance_part = f"[{int(value) + 1}]"
                elif attr in DICT_TO_XPATH_MAPPING:
                    xpath_part = DICT_TO_XPATH_MAPPING[attr](value)
                    xpath_parts.append(xpath_part)
                else:
                    self.logger.warning(f"Unsupported attribute for XPath: {key}")
            except ValueError:
                self.logger.warning(f"Unknown attribute: {key}")
                continue

        # Build base XPath with conditions (avoid logical operators for compatibility)
        if xpath_parts:
            # Use nested conditions instead of logical operators
            xpath = base_xpath
            for condition in xpath_parts:
                xpath = f"{xpath}[{condition}]"
        else:
            xpath = base_xpath
            
        # Add instance if present
        if instance_part:
            xpath += instance_part

        # Handle hierarchical relationships
        for hierarchical_key, hierarchical_value in hierarchical_parts:
            if isinstance(hierarchical_value, dict):
                nested_xpath = self._dict_to_xpath_recursive(hierarchical_value, base_xpath="*")
                hierarchical_attr = DictAttribute(hierarchical_key)
                xpath += get_xpath_for_hierarchical_attribute(hierarchical_attr, nested_xpath)
            else:
                self.logger.warning(f"Hierarchical attribute {hierarchical_key} requires dict value")

        return xpath

    def _dict_to_ui_recursive(self, selector_dict: Union[dict[str, Any], dict[DictAttribute, Any]]) -> str:
        """
        Recursively convert dictionary to UiSelector method chain.
        
        Args:
            selector_dict: Dictionary representation of the selector
            
        Returns:
            UiSelector method chain string
        """
        if not selector_dict:
            return ""

        ui_parts = []
        hierarchical_parts = []
        
        # Process regular attributes
        for key, value in selector_dict.items():
            if key in (DictAttribute.CHILD_SELECTOR, DictAttribute.FROM_PARENT, DictAttribute.SIBLING):
                # Handle hierarchical attributes separately
                hierarchical_parts.append((key, value))
                continue
                
            try:
                # Map UiSelector keys to DictAttribute keys
                key_mapping = {
                    "className": "class",
                    "classNameMatches": "classMatches",
                    "textContains": "textContains",
                    "textStartsWith": "textStartsWith", 
                    "textMatches": "textMatches",
                    "description": "content-desc",
                    "descriptionContains": "content-descContains",
                    "descriptionStartsWith": "content-descStartsWith",
                    "descriptionMatches": "content-descMatches",
                    "resourceId": "resource-id",
                    "resourceIdMatches": "resource-idMatches",
                    "packageName": "package",
                    "packageNameMatches": "packageMatches",
                    "longClickable": "long-clickable",
                }
                mapped_key = key_mapping.get(key, key)
                attr = DictAttribute(mapped_key)
                if attr in DICT_TO_UI_MAPPING:
                    ui_part = DICT_TO_UI_MAPPING[attr](value)
                    ui_parts.append(ui_part)
                else:
                    self.logger.warning(f"Unsupported attribute for UiSelector: {key}")
            except ValueError:
                self.logger.warning(f"Unknown attribute: {key}")
                continue

        # Build base UiSelector chain
        ui_selector = "".join(ui_parts)

        # Handle hierarchical relationships
        for hierarchical_key, hierarchical_value in hierarchical_parts:
            if isinstance(hierarchical_value, dict):
                nested_ui = self._dict_to_ui_recursive(hierarchical_value)
                hierarchical_attr = DictAttribute(hierarchical_key)
                method_name = get_ui_method_for_hierarchical_attribute(hierarchical_attr)
                ui_selector += f".{method_name}(new UiSelector(){nested_ui})"
            else:
                self.logger.warning(f"Hierarchical attribute {hierarchical_key} requires dict value")

        return ui_selector

    def validate_dict_selector(self, selector_dict: Union[dict[str, Any], dict[DictAttribute, Any]]) -> None:
        """
        Validate dictionary selector for compatibility.
        
        Args:
            selector_dict: Dictionary representation of the selector
            
        Raises:
            ValueError: If selector is invalid
        """
        if not isinstance(selector_dict, dict):
            raise ValueError("Selector must be a dictionary")
        
        if not selector_dict:
            # Empty selector is valid (matches any element)
            return
        
        # Check for conflicting attributes
        text_attrs = [DictAttribute.TEXT, DictAttribute.TEXT_CONTAINS,
                     DictAttribute.TEXT_STARTS_WITH, DictAttribute.TEXT_MATCHES]
        desc_attrs = [DictAttribute.DESCRIPTION, DictAttribute.DESCRIPTION_CONTAINS,
                     DictAttribute.DESCRIPTION_STARTS_WITH, DictAttribute.DESCRIPTION_MATCHES]
        
        found_text_attrs = [attr for attr in text_attrs if attr.value in selector_dict]
        found_desc_attrs = [attr for attr in desc_attrs if attr.value in selector_dict]
        
        if len(found_text_attrs) > 1:
            raise ValueError(f"Conflicting text attributes: {found_text_attrs}")
        if len(found_desc_attrs) > 1:
            raise ValueError(f"Conflicting description attributes: {found_desc_attrs}")
        
        # Validate hierarchical attributes
        for key, value in selector_dict.items():
            if key in (DictAttribute.CHILD_SELECTOR, DictAttribute.FROM_PARENT, DictAttribute.SIBLING):
                if not isinstance(value, dict):
                    raise ValueError(f"Hierarchical attribute {key} must have dict value")
                self.validate_dict_selector(value)  # Recursive validation
