# /shadowstep/locator_converter/locator_converter.py
# created by AI

"""
Unified locator converter that provides a single interface for all locator conversions.
This module combines all the functionality of the locator converter system.
"""

import logging
from typing import Any, Dict, List

from shadowstep.locator_converter.locator_factory import LocatorFactory
from shadowstep.locator_converter.locator_validator import LocatorValidator
from shadowstep.locator_converter.ui_selector_converter import UiSelectorConverter, InvalidUiSelectorError, \
    ConversionError


class LocatorConverter:
    """
    Unified interface for all locator conversions.
    
    This class provides a comprehensive set of methods to convert between
    different locator formats with validation and error handling.
    """

    def __init__(self, enable_logging: bool = True):
        """
        Initialize the unified converter.
        
        Args:
            enable_logging: Whether to enable logging (default: True)
        """
        self.ui_converter = UiSelectorConverter()
        self.validator = LocatorValidator()
        self.factory = LocatorFactory()
        
        if enable_logging:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.disabled = True

    # --- UiSelector conversions ---

    def ui_selector_to_xpath(self, selector: str) -> str:
        """
        Convert UiSelector string to XPath.
        
        Args:
            selector: UiSelector string
            
        Returns:
            XPath string
            
        Raises:
            InvalidUiSelectorError: If selector is invalid
            ConversionError: If conversion fails
        """
        # Validate input
        is_valid, errors = self.validator.validate_ui_selector(selector)
        if not is_valid:
            raise InvalidUiSelectorError(f"Invalid UiSelector: {'; '.join(errors)}")
        
        try:
            return self.ui_converter.ui_selector_to_xpath(selector)
        except Exception as e:
            raise ConversionError(f"Failed to convert UiSelector to XPath: {e}") from e

    def ui_selector_to_dict(self, selector: str) -> Dict[str, Any]:
        """
        Convert UiSelector string to dictionary format.
        
        Args:
            selector: UiSelector string
            
        Returns:
            Dictionary representation
            
        Raises:
            InvalidUiSelectorError: If selector is invalid
        """
        # Validate input
        is_valid, errors = self.validator.validate_ui_selector(selector)
        if not is_valid:
            raise InvalidUiSelectorError(f"Invalid UiSelector: {'; '.join(errors)}")
        
        return self.ui_converter.ui_selector_to_dict(selector)

    # --- Dictionary conversions ---

    def dict_to_xpath(self, locator: Dict[str, Any]) -> str:
        """
        Convert dictionary locator to XPath.
        
        Args:
            locator: Dictionary locator
            
        Returns:
            XPath string
            
        Raises:
            ValueError: If locator is invalid
        """
        # Validate input
        is_valid, errors = self.validator.validate_dict_locator(locator)
        if not is_valid:
            raise ValueError(f"Invalid dictionary locator: {'; '.join(errors)}")
        
        return self.factory.create_xpath(**locator)

    def dict_to_ui_selector(self, locator: Dict[str, Any]) -> str:
        """
        Convert dictionary locator to UiSelector string.
        
        Args:
            locator: Dictionary locator
            
        Returns:
            UiSelector string
            
        Raises:
            ValueError: If locator is invalid
        """
        # Validate input
        is_valid, errors = self.validator.validate_dict_locator(locator)
        if not is_valid:
            raise ValueError(f"Invalid dictionary locator: {'; '.join(errors)}")
        
        return self.factory.create_ui_selector(**locator)

    # --- XPath conversions ---

    def xpath_to_dict(self, xpath: str) -> Dict[str, Any]:
        """
        Convert XPath to dictionary format (basic conversion).
        
        Args:
            xpath: XPath string
            
        Returns:
            Dictionary representation (limited)
            
        Raises:
            ValueError: If XPath is invalid
        """
        # Validate input
        is_valid, errors = self.validator.validate_xpath(xpath)
        if not is_valid:
            raise ValueError(f"Invalid XPath: {'; '.join(errors)}")
        
        # Basic XPath to dict conversion
        # This is a simplified conversion - full parsing would require more complex logic
        result = {}
        
        # Extract basic attributes
        if '@text=' in xpath:
            text_match = xpath.split('@text=')[1].split('"')[1]
            result['text'] = text_match
        
        if '@resource-id=' in xpath:
            id_match = xpath.split('@resource-id=')[1].split('"')[1]
            result['resource-id'] = id_match
        
        if '@class=' in xpath:
            class_match = xpath.split('@class=')[1].split('"')[1]
            result['class'] = class_match
        
        return result

    def xpath_to_ui_selector(self, xpath: str) -> str:
        """
        Convert XPath to UiSelector string (basic conversion).
        
        Args:
            xpath: XPath string
            
        Returns:
            UiSelector string
            
        Raises:
            ValueError: If XPath is invalid
        """
        # Convert to dict first, then to UiSelector
        locator_dict = self.xpath_to_dict(xpath)
        return self.dict_to_ui_selector(locator_dict)

    # --- Factory methods ---

    def create_ui_selector(self, **kwargs) -> str:
        """
        Create UiSelector string using factory.
        
        Args:
            **kwargs: UiSelector method names and values
            
        Returns:
            UiSelector string
        """
        return self.factory.create_ui_selector(**kwargs)

    def create_xpath(self, **kwargs) -> str:
        """
        Create XPath expression using factory.
        
        Args:
            **kwargs: XPath attributes and values
            
        Returns:
            XPath string
        """
        return self.factory.create_xpath(**kwargs)

    def create_dict(self, **kwargs) -> Dict[str, Any]:
        """
        Create dictionary locator using factory.
        
        Args:
            **kwargs: Locator attributes and values
            
        Returns:
            Dictionary locator
        """
        return self.factory.create_dict(**kwargs)

    # --- Validation methods ---

    def validate_locator(self, locator: Any, format_type: str) -> bool:
        """
        Validate a locator in the specified format.
        
        Args:
            locator: Locator to validate
            format_type: Expected format
            
        Returns:
            True if valid, False otherwise
        """
        return self.validator.is_valid_locator(locator, format_type)

    def get_validation_errors(self, locator: Any, format_type: str) -> List[str]:
        """
        Get validation errors for a locator.
        
        Args:
            locator: Locator to validate
            format_type: Expected format
            
        Returns:
            List of validation errors
        """
        _, errors = self.validator.validate_locator_format(locator, format_type)
        return errors

    def suggest_fixes(self, locator: Any, format_type: str) -> List[str]:
        """
        Get suggestions for fixing validation errors.
        
        Args:
            locator: Locator that failed validation
            format_type: Format of the locator
            
        Returns:
            List of suggested fixes
        """
        return self.validator.suggest_fixes(locator, format_type)

    # --- Utility methods ---

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported locator formats.
        
        Returns:
            List of supported formats
        """
        return ["ui_selector", "xpath", "dict"]

    def get_supported_methods(self) -> List[str]:
        """
        Get list of supported UiSelector methods.
        
        Returns:
            List of supported method names
        """
        return self.factory.get_supported_methods()

    def get_conversion_stats(self) -> Dict[str, Any]:
        """
        Get conversion statistics.
        
        Returns:
            Dictionary with conversion statistics
        """
        ui_stats = self.ui_converter.get_conversion_stats()
        return {
            'ui_selector_conversions': ui_stats,
            'total_formats_supported': len(self.get_supported_formats()),
            'total_methods_supported': len(self.get_supported_methods())
        }

    def reset_stats(self) -> None:
        """Reset all conversion statistics."""
        self.ui_converter.reset_stats()

    # --- Batch conversion methods ---

    def convert_batch(self, locators: List[Any], from_format: str, to_format: str) -> List[Any]:
        """
        Convert multiple locators in batch.
        
        Args:
            locators: List of locators to convert
            from_format: Source format
            to_format: Target format
            
        Returns:
            List of converted locators
            
        Raises:
            ValueError: If formats are not supported
        """
        if from_format not in self.get_supported_formats():
            raise ValueError(f"Unsupported source format: {from_format}")
        
        if to_format not in self.get_supported_formats():
            raise ValueError(f"Unsupported target format: {to_format}")
        
        converted = []
        errors = []
        
        for i, locator in enumerate(locators):
            try:
                if from_format == "ui_selector" and to_format == "xpath":
                    converted.append(self.ui_selector_to_xpath(locator))
                elif from_format == "ui_selector" and to_format == "dict":
                    converted.append(self.ui_selector_to_dict(locator))
                elif from_format == "dict" and to_format == "xpath":
                    converted.append(self.dict_to_xpath(locator))
                elif from_format == "dict" and to_format == "ui_selector":
                    converted.append(self.dict_to_ui_selector(locator))
                elif from_format == "xpath" and to_format == "dict":
                    converted.append(self.xpath_to_dict(locator))
                elif from_format == "xpath" and to_format == "ui_selector":
                    converted.append(self.xpath_to_ui_selector(locator))
                else:
                    raise ValueError(f"Conversion from {from_format} to {to_format} not implemented")
            except Exception as e:
                errors.append(f"Locator {i}: {e}")
                converted.append(None)  # Keep indices aligned
        
        if errors:
            self.logger.warning(f"Batch conversion completed with {len(errors)} errors: {errors}")
        
        return converted

    def validate_batch(self, locators: List[Any], formats: List[str]) -> Dict[str, Any]:
        """
        Validate multiple locators in batch.
        
        Args:
            locators: List of locators to validate
            formats: List of expected formats
            
        Returns:
            Validation summary
        """
        return self.validator.get_validation_summary(locators, formats)


# Convenience functions for backward compatibility
def convert_ui_selector_to_xpath(selector: str) -> str:
    """Convert UiSelector to XPath (backward compatibility)."""
    converter = LocatorConverter()
    return converter.ui_selector_to_xpath(selector)


def convert_dict_to_xpath(locator: Dict[str, Any]) -> str:
    """Convert dictionary to XPath (backward compatibility)."""
    converter = LocatorConverter()
    return converter.dict_to_xpath(locator)


def validate_locator(locator: Any, format_type: str) -> bool:
    """Validate locator (backward compatibility)."""
    converter = LocatorConverter()
    return converter.validate_locator(locator, format_type)
