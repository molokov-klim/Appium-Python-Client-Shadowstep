# ui_selector_converter_core.py
import logging
from typing import Any, cast

from shadowstep.locator_converter.map.ui_to_xpath import (
    UI_TO_XPATH,
    get_xpath_for_method,
    is_hierarchical_method,
)
from shadowstep.locator_converter.types.ui_selector import UiMethod
from shadowstep.locator_converter.ui_selector_converter_core.ast import Selector
from shadowstep.locator_converter.ui_selector_converter_core.lexer import Lexer
from shadowstep.locator_converter.ui_selector_converter_core.parser import Parser


class LocatorConverterError(Exception):
    """Base exception for locator conversion errors."""
    pass


class InvalidUiSelectorError(LocatorConverterError):
    """Raised when UiSelector string is malformed."""
    pass


class ConversionError(LocatorConverterError):
    """Raised when conversion between formats fails."""
    pass


class UiSelectorConverter:
    """
    Enhanced UiSelector converter with improved error handling and caching.

    This class provides methods to convert UiSelector strings to various formats
    including XPath, dictionary locators, and back to UiSelector strings.
    """

    def __init__(self):
        """Initialize the converter with logging."""
        self.logger = logging.getLogger(__name__)
        self.conversion_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0
        }


    def selector_to_xpath(self, sel: dict[str, Any], base_xpath: str = "//*") -> str:
        """
        Convert a parsed selector dictionary to XPath.

        Args:
            sel: Parsed selector dictionary with methods
            base_xpath: Base XPath to start with (default: "//*")

        Returns:
            XPath string representation

        Raises:
            ConversionError: If conversion fails
        """
        try:
            xpath = base_xpath

            for method_data in sel.get("methods", []):
                name = method_data["name"]
                args = method_data.get("args", [])

                try:
                    method = UiMethod(name)
                except ValueError as e:
                    self.logger.warning(f"Unknown UiSelector method '{name}', skipping: {e}")
                    continue

                if is_hierarchical_method(method):
                    # Handle hierarchical methods specially
                    if method == UiMethod.CHILD_SELECTOR:
                        child_xpath = self._convert_nested_selector(args[0])
                        xpath += f'/{child_xpath}'
                    elif method == UiMethod.FROM_PARENT:
                        parent_xpath = self._convert_nested_selector(args[0])
                        if parent_xpath.startswith("//"):
                            xpath = f'{xpath}/..{parent_xpath}'
                        else:
                            xpath = f'{xpath}/..//{parent_xpath}'
                else:
                    # Handle regular methods
                    if method in UI_TO_XPATH:
                        if args:
                            xpath += get_xpath_for_method(method, args[0])
                        else:
                            # Boolean methods without args (e.g., .enabled())
                            xpath += get_xpath_for_method(method, True)
                    else:
                        self.logger.warning(f"Method '{method}' not supported in XPath conversion")

            self._log_successful_conversion("dict", "xpath")
            return xpath

        except Exception as e:
            self._log_failed_conversion("dict", "xpath", str(e))
            raise ConversionError(f"Failed to convert selector to XPath: {e}") from e

    def _convert_nested_selector(self, nested_sel: Any) -> str:
        """
        Convert a nested selector to XPath.

        Args:
            nested_sel: Nested selector (can be dict or Selector object)

        Returns:
            XPath string for the nested selector
        """
        if isinstance(nested_sel, dict):
            return self.selector_to_xpath(nested_sel, base_xpath="*")   # type: ignore
        elif hasattr(nested_sel, 'methods'):
            # Handle Selector AST object
            parsed_dict = self._selector_to_parsed_dict(nested_sel)
            return self.selector_to_xpath(parsed_dict, base_xpath="*")   # type: ignore
        else:
            raise ConversionError(f"Unsupported nested selector type: {type(nested_sel)}")

    def _selector_to_parsed_dict(self, sel: Selector) -> dict[str, Any]:
        """
        Convert Selector AST object to dictionary format.

        Args:
            sel: Selector AST object

        Returns:
            Dictionary representation of the selector
        """

        def convert_arg(arg: Any) -> Any:
            if hasattr(arg, 'methods'):  # Nested Selector
                return self._selector_to_parsed_dict(arg)
            return arg

        return {
            "methods": [
                {"name": method.name, "args": [convert_arg(arg) for arg in method.args]}
                for method in sel.methods
            ]
        }

    def parse_selector_string(self, selector_str: str) -> dict[str, Any]:
        """
        Parse UiSelector string into dictionary format.

        Args:
            selector_str: UiSelector string to parse

        Returns:
            Parsed selector dictionary

        Raises:
            InvalidUiSelectorError: If parsing fails
        """
        try:
            # Clean the input string
            cleaned_str = selector_str.strip()
            if cleaned_str.startswith("'") and cleaned_str.endswith("'"):
                cleaned_str = cleaned_str[1:-1]

            # Tokenize and parse
            tokens = Lexer(cleaned_str).tokens()
            selector = Parser(tokens).parse()

            return self._selector_to_parsed_dict(selector)

        except Exception as e:
            self.logger.error(f"Failed to parse UiSelector string: {e}")
            raise InvalidUiSelectorError(f"Invalid UiSelector string: {e}") from e

    def ui_selector_to_xpath(self, selector_str: str) -> str:
        """
        Convert UiSelector string directly to XPath.

        Args:
            selector_str: UiSelector string

        Returns:
            XPath string

        Raises:
            InvalidUiSelectorError: If selector string is invalid
            ConversionError: If conversion fails
        """
        try:
            parsed_dict = self.parse_selector_string(selector_str)
            return self.selector_to_xpath(parsed_dict)   # type: ignore
        except InvalidUiSelectorError:
            raise
        except Exception as e:
            raise ConversionError(f"Failed to convert UiSelector to XPath: {e}") from e

    def ui_selector_to_dict(self, selector_str: str) -> dict[str, Any]:
        """
        Convert UiSelector string to dictionary format.

        Args:
            selector_str: UiSelector string

        Returns:
            Dictionary representation of the selector
        """
        return self.parse_selector_string(selector_str)

    def _parsed_dict_to_selector(self, selector_dict: dict[str, Any], top_level: bool = True) -> str:
        """
        Convert parsed dictionary back to UiSelector string.

        Args:
            selector_dict: Parsed selector dictionary
            top_level: Whether this is the top-level selector

        Returns:
            UiSelector string
        """

        def format_arg(arg: Any) -> str:
            if isinstance(arg, dict):
                # Nested selector - without final semicolon
                return self._parsed_dict_to_selector(cast(dict[str, Any], arg), top_level=False)
            elif isinstance(arg, bool):
                return "true" if arg else "false"
            elif isinstance(arg, int):
                return str(arg)
            else:
                # Escape quotes and backslashes
                escaped = str(arg).replace('\\', '\\\\').replace('"', '\\"')
                return f'"{escaped}"'

        parts = ["new UiSelector()"]

        for method_data in selector_dict.get("methods", []):
            method_name = method_data["name"]
            args = method_data.get("args", [])

            if len(args) > 1:
                raise ConversionError(f"UiSelector methods typically take 0-1 arguments, got {len(args)}")

            arg_str = format_arg(args[0]) if args else ""
            parts.append(f'.{method_name}({arg_str})')

        result = "".join(parts)
        return result + ";" if top_level else result

    def dict_to_ui_selector(self, selector_dict: dict[str, Any]) -> str:
        """
        Convert selector dictionary to UiSelector string.

        Args:
            selector_dict: Selector dictionary

        Returns:
            UiSelector string
        """
        return self._parsed_dict_to_selector(selector_dict)

    def get_conversion_stats(self) -> dict[str, int]:
        """
        Get conversion statistics.

        Returns:
            Dictionary with conversion statistics
        """
        return self.conversion_stats.copy()

    def _log_successful_conversion(self, from_format: str, to_format: str) -> None:
        """Log successful conversion."""
        self.conversion_stats['total_conversions'] += 1
        self.conversion_stats['successful_conversions'] += 1
        self.logger.debug(f"Successfully converted {from_format} -> {to_format}")

    def _log_failed_conversion(self, from_format: str, to_format: str, error: str) -> None:
        """Log failed conversion."""
        self.conversion_stats['total_conversions'] += 1
        self.conversion_stats['failed_conversions'] += 1
        self.logger.error(f"Failed to convert {from_format} -> {to_format}: {error}")

    def reset_stats(self) -> None:
        """Reset conversion statistics."""
        self.conversion_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0
        }


# Convenience functions for backward compatibility
def selector_to_xpath(sel: dict[str, Any], base_xpath: str = "//*") -> str:
    """Convert selector dictionary to XPath (backward compatibility)."""
    converter = UiSelectorConverter()
    return converter.selector_to_xpath(sel, base_xpath)


def parse_selector_string(s: str) -> dict[str, Any]:
    """Parse UiSelector string (backward compatibility)."""
    converter = UiSelectorConverter()
    return converter.parse_selector_string(s)

