# /shadowstep/locator_converter/locator_validator.py
# created by AI

"""
Locator validator for checking correctness of various locator formats.
This module provides validation methods for UiSelector, XPath, and dictionary locators.
"""

import re
from typing import Any, Dict, List, Tuple, Union

from shadowstep.locator_converter.types.ui_selector import UiMethod


class LocatorValidator:
    """
    Validator class for different types of locators.
    
    This class provides static methods to validate locators in various formats
    including UiSelector strings, XPath expressions, and dictionary locators.
    """

    # Regex patterns for validation
    XPATH_PATTERN = re.compile(r'^//.*$')
    UISELECTOR_PATTERN = re.compile(r'^new\s+UiSelector\s*\(\s*\)\s*(\..*)*;?\s*$')
    
    @staticmethod
    def validate_ui_selector(selector: str) -> Tuple[bool, List[str]]:
        """
        Validate UiSelector string format and content.
        
        Args:
            selector: UiSelector string to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
            
        Examples:
            >>> LocatorValidator.validate_ui_selector('new UiSelector().text("Button");')
            (True, [])
            
            >>> LocatorValidator.validate_ui_selector('invalid selector')
            (False, ['Invalid UiSelector format'])
        """
        errors = []
        
        # Check basic format
        if not LocatorValidator.UISELECTOR_PATTERN.match(selector.strip()):
            errors.append("Invalid UiSelector format")
            return False, errors
        
        # Check for required parts
        if "new UiSelector()" not in selector:
            errors.append("Missing 'new UiSelector()' constructor")
        
        # Check method calls
        method_calls = re.findall(r'\.(\w+)\s*\([^)]*\)', selector)
        for method_name in method_calls:
            try:
                UiMethod(method_name)
            except ValueError:
                errors.append(f"Unknown UiSelector method: {method_name}")
        
        # Check for balanced parentheses
        if selector.count('(') != selector.count(')'):
            errors.append("Unbalanced parentheses")
        
        # Check for balanced quotes
        quote_count = selector.count('"')
        if quote_count % 2 != 0:
            errors.append("Unbalanced quotes")
        
        return len(errors) == 0, errors

    @staticmethod
    def validate_xpath(xpath: str) -> Tuple[bool, List[str]]:
        """
        Validate XPath expression format and syntax.
        
        Args:
            xpath: XPath string to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
            
        Examples:
            >>> LocatorValidator.validate_xpath('//*[@text="Button"]')
            (True, [])
            
            >>> LocatorValidator.validate_xpath('invalid xpath')
            (False, ['XPath must start with //'])
        """
        errors = []
        
        # Check if starts with //
        if not LocatorValidator.XPATH_PATTERN.match(xpath):
            errors.append("XPath must start with //")
        
        # Check for balanced brackets
        bracket_count = xpath.count('[') + xpath.count(']')
        if bracket_count % 2 != 0:
            errors.append("Unbalanced brackets")
        
        # Check for balanced quotes in predicates
        predicates = re.findall(r'\[([^\]]*)\]', xpath)
        for predicate in predicates:
            quote_count = predicate.count('"') + predicate.count("'")
            if quote_count % 2 != 0:
                errors.append(f"Unbalanced quotes in predicate: [{predicate}]")
        
        # Check for valid attribute syntax
        attr_pattern = re.compile(r'@\w+\s*[=<>!]\s*["\'][^"\']*["\']')
        predicates_without_quotes = re.findall(r'\[([^\]]*)\]', xpath)
        for predicate in predicates_without_quotes:
            if '=' in predicate and not re.search(r'@\w+\s*=\s*["\'][^"\']*["\']', predicate):
                errors.append(f"Invalid attribute syntax in predicate: [{predicate}]")
        
        return len(errors) == 0, errors

    @staticmethod
    def validate_dict_locator(locator: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate dictionary locator format and content.
        
        Args:
            locator: Dictionary locator to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
            
        Examples:
            >>> LocatorValidator.validate_dict_locator({'text': 'Button', 'class': 'android.widget.Button'})
            (True, [])
            
            >>> LocatorValidator.validate_dict_locator({'invalid_key': 'value'})
            (False, ['Unknown attribute: invalid_key'])
        """
        errors = []
        
        if not isinstance(locator, dict):
            errors.append("Locator must be a dictionary")
            return False, errors
        
        if not locator:
            errors.append("Locator dictionary cannot be empty")
            return False, errors
        
        # Valid Android UI attributes
        valid_attributes = {
            'text', 'resource-id', 'class', 'package', 'content-desc',
            'checkable', 'checked', 'clickable', 'enabled', 'focusable',
            'focused', 'long-clickable', 'scrollable', 'selected',
            'bounds', 'displayed', 'password', 'index', 'instance'
        }
        
        for key, value in locator.items():
            # Check if attribute is valid
            if key not in valid_attributes:
                errors.append(f"Unknown attribute: {key}")
            
            # Check value types
            if key in ['checkable', 'checked', 'clickable', 'enabled', 'focusable', 
                       'focused', 'long-clickable', 'scrollable', 'selected', 'displayed', 'password']:
                if not isinstance(value, bool):
                    errors.append(f"Attribute {key} must be boolean, got {type(value).__name__}")
            
            elif key in ['index', 'instance']:
                if not isinstance(value, int) or value < 0:
                    errors.append(f"Attribute {key} must be non-negative integer, got {value}")
            
            elif key in ['text', 'resource-id', 'class', 'package', 'content-desc', 'bounds']:
                if not isinstance(value, str):
                    errors.append(f"Attribute {key} must be string, got {type(value).__name__}")
        
        return len(errors) == 0, errors

    @staticmethod
    def validate_locator_format(locator: Any, expected_format: str) -> Tuple[bool, List[str]]:
        """
        Validate that a locator matches the expected format.
        
        Args:
            locator: Locator to validate
            expected_format: Expected format ("ui_selector", "xpath", or "dict")
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if expected_format == "ui_selector":
            if not isinstance(locator, str):
                return False, ["UiSelector locator must be a string"]
            return LocatorValidator.validate_ui_selector(locator)
        
        elif expected_format == "xpath":
            if not isinstance(locator, str):
                return False, ["XPath locator must be a string"]
            return LocatorValidator.validate_xpath(locator)
        
        elif expected_format == "dict":
            return LocatorValidator.validate_dict_locator(locator)
        
        else:
            return False, [f"Unknown format: {expected_format}"]

    @staticmethod
    def get_validation_summary(locators: List[Any], formats: List[str]) -> Dict[str, Any]:
        """
        Get validation summary for multiple locators.
        
        Args:
            locators: List of locators to validate
            formats: List of expected formats for each locator
            
        Returns:
            Dictionary with validation summary
            
        Examples:
            >>> locators = ['new UiSelector().text("Button");', '//*[@text="Button"]']
            >>> formats = ['ui_selector', 'xpath']
            >>> LocatorValidator.get_validation_summary(locators, formats)
            {'total': 2, 'valid': 2, 'invalid': 0, 'errors': {}}
        """
        if len(locators) != len(formats):
            raise ValueError("Number of locators must match number of formats")
        
        summary = {
            'total': len(locators),
            'valid': 0,
            'invalid': 0,
            'errors': {}
        }
        
        for i, (locator, format_type) in enumerate(zip(locators, formats)):
            is_valid, errors = LocatorValidator.validate_locator_format(locator, format_type)
            
            if is_valid:
                summary['valid'] += 1
            else:
                summary['invalid'] += 1
                summary['errors'][f'locator_{i}'] = {
                    'format': format_type,
                    'errors': errors
                }
        
        return summary

    @staticmethod
    def suggest_fixes(locator: Any, format_type: str) -> List[str]:
        """
        Suggest fixes for common validation errors.
        
        Args:
            locator: Locator that failed validation
            format_type: Format of the locator
            
        Returns:
            List of suggested fixes
        """
        suggestions = []
        
        if format_type == "ui_selector":
            if isinstance(locator, str):
                if "new UiSelector()" not in locator:
                    suggestions.append("Add 'new UiSelector()' constructor")
                if not locator.endswith(';'):
                    suggestions.append("Add semicolon at the end")
                if locator.count('(') != locator.count(')'):
                    suggestions.append("Check for balanced parentheses")
        
        elif format_type == "xpath":
            if isinstance(locator, str):
                if not locator.startswith('//'):
                    suggestions.append("XPath must start with //")
                if locator.count('[') != locator.count(']'):
                    suggestions.append("Check for balanced brackets")
        
        elif format_type == "dict":
            if isinstance(locator, dict):
                for key in locator.keys():
                    if key not in ['text', 'resource-id', 'class', 'package', 'content-desc',
                                  'checkable', 'checked', 'clickable', 'enabled', 'focusable',
                                  'focused', 'long-clickable', 'scrollable', 'selected',
                                  'bounds', 'displayed', 'password', 'index', 'instance']:
                        suggestions.append(f"Remove or rename invalid attribute: {key}")
        
        return suggestions

    @staticmethod
    def is_valid_locator(locator: Any, format_type: str) -> bool:
        """
        Quick check if a locator is valid.
        
        Args:
            locator: Locator to check
            format_type: Expected format
            
        Returns:
            True if valid, False otherwise
        """
        is_valid, _ = LocatorValidator.validate_locator_format(locator, format_type)
        return is_valid
