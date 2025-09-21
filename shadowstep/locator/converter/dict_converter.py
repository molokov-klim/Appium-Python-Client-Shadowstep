# shadowstep/locator/dict_converter.py
"""
DictConverter for converting Shadowstep dictionary locators to other formats.

This module provides the main DictConverter class that handles conversion
from Shadowstep dictionary format to XPath and UiSelector expressions.
"""
from __future__ import annotations

import logging
from typing import Any

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepConversionError
from shadowstep.locator.map.dict_to_ui import (
    DICT_TO_UI_MAPPING,
    get_ui_method_for_hierarchical_attribute,
)
from shadowstep.locator.map.dict_to_xpath import (
    DICT_TO_XPATH_MAPPING,
    get_xpath_for_hierarchical_attribute,
)
from shadowstep.locator.types.shadowstep_dict import ShadowstepDictAttribute


class DictConverter:
    """
    Converter for Shadowstep dictionary locators to XPath and UiSelector formats.
    
    This class provides methods to convert dictionary-based locators to various
    formats including XPath expressions and UiSelector strings.
    """

    def __init__(self):
        """Initialize the converter with logging."""
        self.logger = logging.getLogger(__name__)

    def dict_to_xpath(self, selector_dict: dict[str, Any] | dict[ShadowstepDictAttribute, Any]) -> str:
        """
        Convert Shadowstep dictionary locator to XPath expression.
        
        Args:
            selector_dict: Dictionary representation of the selector
            
        Returns:
            XPath expression string
            
        Raises:
            ShadowstepConversionError: If conversion fails
        """
        try:
            return self._dict_to_xpath_recursive(selector_dict)
        except Exception as e:
            raise ShadowstepConversionError(f"Failed to convert dict to XPath: {e}") from e

    def dict_to_ui_selector(self, selector_dict: dict[str, Any] | dict[ShadowstepDictAttribute, Any]) -> str:
        """
        Convert Shadowstep dictionary locator to UiSelector string.
        
        Args:
            selector_dict: Dictionary representation of the selector
            
        Returns:
            UiSelector string
            
        Raises:
            ShadowstepConversionError: If conversion fails
        """
        try:
            ui_selector = self._dict_to_ui_recursive(selector_dict)
            return f"new UiSelector(){ui_selector};"
        except Exception as e:
            raise ShadowstepConversionError(f"Failed to convert dict to UiSelector: {e}") from e

    def _dict_to_xpath_recursive(  # noqa: C901
            self,
            selector_dict: dict[str, Any] | dict[ShadowstepDictAttribute, Any],
            base_xpath: str = "//*",
    ) -> str:  # noqa: C901
        if not selector_dict:
            return base_xpath

        xpath_parts = []
        hierarchical_parts = []
        instance_part = None

        for key, value in selector_dict.items():
            if key in (
                    ShadowstepDictAttribute.CHILD_SELECTOR,
                    ShadowstepDictAttribute.FROM_PARENT,
                    ShadowstepDictAttribute.SIBLING,
            ):
                hierarchical_parts.append((key, value))
                continue

            try:
                # try Enum
                attr = ShadowstepDictAttribute(key)
            except ValueError:
                # fallback: key not in ShadowstepDictAttribute → take as is
                xpath_parts.append(f"@{key}='{value}'")
                continue

            if attr == ShadowstepDictAttribute.INSTANCE:
                instance_part = f"[{int(value) + 1}]"
            elif attr in DICT_TO_XPATH_MAPPING:
                xpath_parts.append(DICT_TO_XPATH_MAPPING[attr](value))
            else:
                # fallback: Enum exists but not in DICT_TO_XPATH_MAPPING → still use raw
                xpath_parts.append(f"@{attr.value}='{value}'")

        # build XPath
        xpath = base_xpath
        for condition in xpath_parts:
            xpath = f"{xpath}[{condition}]"

        if instance_part:
            xpath += instance_part

        for hierarchical_key, hierarchical_value in hierarchical_parts:
            if isinstance(hierarchical_value, dict):
                nested_xpath = self._dict_to_xpath_recursive(
                    hierarchical_value
                )
                hierarchical_attr = ShadowstepDictAttribute(hierarchical_key)
                xpath += get_xpath_for_hierarchical_attribute(
                    hierarchical_attr, nested_xpath
                )
            else:
                self.logger.warning(
                    f"Hierarchical attribute {hierarchical_key} requires dict value"
                )

        return xpath

    def _dict_to_ui_recursive(self, selector_dict: dict[str, Any] | dict[ShadowstepDictAttribute, Any]) -> str:
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
            if key in (ShadowstepDictAttribute.CHILD_SELECTOR, ShadowstepDictAttribute.FROM_PARENT, ShadowstepDictAttribute.SIBLING):
                # Handle hierarchical attributes separately
                hierarchical_parts.append((key, value))
                continue
                
            try:
                # Map UiSelector keys to ShadowstepDictAttribute keys
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
                attr = ShadowstepDictAttribute(mapped_key)
                if attr in DICT_TO_UI_MAPPING:
                    ui_part = DICT_TO_UI_MAPPING[attr](value)
                    ui_parts.append(ui_part)
                else:
                    self.logger.warning(f"Unsupported attribute for UiSelector: {key}")
            except ValueError:
                self.logger.warning(f"Unknown attribute: {key}")
                continue

        # Build shadowstep UiSelector chain
        ui_selector = "".join(ui_parts)

        # Handle hierarchical relationships
        for hierarchical_key, hierarchical_value in hierarchical_parts:
            if isinstance(hierarchical_value, dict):
                nested_ui = self._dict_to_ui_recursive(hierarchical_value)
                hierarchical_attr = ShadowstepDictAttribute(hierarchical_key)
                method_name = get_ui_method_for_hierarchical_attribute(hierarchical_attr)
                ui_selector += f".{method_name}(new UiSelector(){nested_ui})"
            else:
                self.logger.warning(f"Hierarchical attribute {hierarchical_key} requires dict value")

        return ui_selector

    def validate_dict_selector(self, selector_dict: dict[str, Any] | dict[ShadowstepDictAttribute, Any]) -> None:
        """
        Validate dictionary selector for compatibility.
        
        Args:
            selector_dict: Dictionary representation of the selector
            
        Raises:
            ValueError: If selector is invalid
        """
        if not isinstance(selector_dict, dict): # type: ignore
            raise ValueError("Selector must be a dictionary")
        
        if not selector_dict:
            raise ValueError("Selector dictionary cannot be empty")
        
        # Check for conflicting attributes
        text_attrs = [ShadowstepDictAttribute.TEXT, ShadowstepDictAttribute.TEXT_CONTAINS,
                      ShadowstepDictAttribute.TEXT_STARTS_WITH, ShadowstepDictAttribute.TEXT_MATCHES]
        desc_attrs = [ShadowstepDictAttribute.DESCRIPTION, ShadowstepDictAttribute.DESCRIPTION_CONTAINS,
                      ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH, ShadowstepDictAttribute.DESCRIPTION_MATCHES]
        
        found_text_attrs = [attr for attr in text_attrs if attr.value in selector_dict]
        found_desc_attrs = [attr for attr in desc_attrs if attr.value in selector_dict]
        
        if len(found_text_attrs) > 1:
            raise ValueError(f"Conflicting text attributes: {found_text_attrs}")
        if len(found_desc_attrs) > 1:
            raise ValueError(f"Conflicting description attributes: {found_desc_attrs}")
        
        # Validate hierarchical attributes
        for key, value in selector_dict.items():
            if key in (ShadowstepDictAttribute.CHILD_SELECTOR, ShadowstepDictAttribute.FROM_PARENT, ShadowstepDictAttribute.SIBLING):
                if not isinstance(value, dict):
                    raise ValueError(f"Hierarchical attribute {key} must have dict value")
                self.validate_dict_selector(value)  # Recursive validation
