# shadowstep/locator_converter/xpath_converter.py
from __future__ import annotations

import logging
import re
from typing import Any

from shadowstep.exceptions.shadowstep_exceptions import ConversionError
from shadowstep.locator_converter.map.xpath_to_dict import XPATH_TO_SHADOWSTEP_DICT


class XPathConverter:
    """
    Enhanced XPath converter with improved error handling and caching.

    This class provides methods to convert XPath strings to various formats
    including UiSelector, dictionary locators, and back to XPath strings.
    """

    def __init__(self):
        """Initialize the converter with logging."""
        self.logger = logging.getLogger(__name__)
        self._compatible_groups = self._build_compatibility_groups()

    def xpath_to_ui(self, xpath_str: str) -> str:
        """
        Convert XPath string directly to UiSelector.

        Args:
            xpath_str: XPath string

        Returns:
            UiSelector string

        Raises:
            ConversionError: If conversion fails
        """
        try:
            parsed_dict = self.parse_xpath_string(xpath_str)
            return self._xpath_to_ui(parsed_dict)
        except Exception as e:
            raise ConversionError(f"Failed to convert XPath to UiSelector: {e}") from e

    def xpath_to_dict(self, xpath_str: str) -> dict[str, Any]:
        """
        Convert XPath string to dictionary format.

        Args:
            xpath_str: XPath string

        Returns:
            Dictionary representation of the XPath
        """
        try:
            parsed_dict = self.parse_xpath_string(xpath_str)
            return self._xpath_to_dict(parsed_dict)
        except Exception as e:
            raise ConversionError(f"Failed to convert XPath to dictionary: {e}") from e

    def parse_xpath_string(self, xpath_str: str) -> dict[str, Any]:
        """
        Parse XPath string into dictionary format.

        Args:
            xpath_str: XPath string to parse

        Returns:
            Parsed XPath dictionary

        Raises:
            ConversionError: If parsing fails
        """
        try:
            # Clean the input string
            cleaned_str = xpath_str.strip()

            # Parse XPath structure
            return self._parse_xpath_structure(cleaned_str)

        except Exception as e:
            self.logger.error(f"Failed to parse XPath string: {e}")
            raise ConversionError(f"Invalid XPath string: {e}") from e

    def _parse_xpath_structure(self, xpath: str) -> dict[str, Any]:
        """
        Parse XPath structure into dictionary format.

        Args:
            xpath: XPath string to parse

        Returns:
            Parsed XPath dictionary
        """
        result: dict[str, Any] = {"methods": []}

        # Handle hierarchical structure
        if "/.." in xpath:
            parts = xpath.split("/..")
            if len(parts) == 2:
                # Handle fromParent case
                parent_part = parts[0]
                child_part = parts[1]

                # Parse parent part
                parent_methods = self._parse_xpath_predicates(parent_part)
                result["methods"].extend(parent_methods)

                # Parse child part with fromParent
                if child_part.startswith("//"):
                    child_part = child_part[2:]  # Remove //
                child_methods = self._parse_xpath_predicates(child_part)
                result["methods"].append({
                    "name": "fromParent",
                    "args": [{"methods": child_methods}]
                })
                return result

        # Handle child selector
        if "/*[" in xpath:
            parts = xpath.split("/*[")
            if len(parts) == 2:
                # Handle childSelector case
                parent_part = parts[0]
                child_part = "[" + parts[1]

                # Parse parent part
                parent_methods = self._parse_xpath_predicates(parent_part)
                result["methods"].extend(parent_methods)

                # Parse child part
                child_methods = self._parse_xpath_predicates(child_part)
                result["methods"].append({
                    "name": "childSelector",
                    "args": [{"methods": child_methods}]
                })
                return result

        # Parse simple XPath
        methods = self._parse_xpath_predicates(xpath)
        result["methods"] = methods

        return result

    def _parse_xpath_predicates(self, xpath: str) -> list[dict[str, Any]]:
        """
        Parse XPath predicates into method list.

        Args:
            xpath: XPath string to parse

        Returns:
            List of parsed methods
        """
        methods = []

        # Extract predicates from XPath
        # Pattern: //*[predicate1][predicate2]...
        predicate_pattern = r"\[([^\]]+)\]"
        predicates = re.findall(predicate_pattern, xpath)

        for predicate in predicates:
            method = self._parse_predicate(predicate)
            if method:
                methods.append(method)

        return methods

    def _parse_predicate(self, predicate: str) -> dict[str, Any] | None:
        """
        Parse single XPath predicate into method.

        Args:
            predicate: Single predicate string

        Returns:
            Parsed method dictionary or None if not supported
        """
        # Handle position() function
        if predicate.startswith("position()="):
            value = int(predicate.split("=")[1])
            return {"name": "index", "args": [value - 1]}  # Convert to 0-based

        # Handle instance (position without position() function)
        if predicate.isdigit():
            value = int(predicate)
            return {"name": "instance", "args": [value - 1]}  # Convert to 0-based

        # Handle attribute predicates
        # Pattern: @attr="value" or contains(@attr,"value") or starts-with(@attr,"value") or matches(@attr,"value")

        # Exact match: @attr="value"
        exact_match = re.match(r'@(\w+)=["\']([^"\']*)["\']', predicate)
        if exact_match:
            attr_name = exact_match.group(1)
            value = exact_match.group(2)
            return self._map_attribute_to_method(attr_name, "exact", value)

        # Contains: contains(@attr,"value")
        contains_match = re.match(r'contains\(@(\w+),["\']([^"\']*)["\']\)', predicate)
        if contains_match:
            attr_name = contains_match.group(1)
            value = contains_match.group(2)
            return self._map_attribute_to_method(attr_name, "contains", value)

        # Starts-with: starts-with(@attr,"value")
        starts_with_match = re.match(r'starts-with\(@(\w+),["\']([^"\']*)["\']\)', predicate)
        if starts_with_match:
            attr_name = starts_with_match.group(1)
            value = starts_with_match.group(2)
            return self._map_attribute_to_method(attr_name, "starts_with", value)

        # Matches: matches(@attr,"value")
        matches_match = re.match(r'matches\(@(\w+),["\']([^"\']*)["\']\)', predicate)
        if matches_match:
            attr_name = matches_match.group(1)
            value = matches_match.group(2)
            return self._map_attribute_to_method(attr_name, "matches", value)

        return None

    def _map_attribute_to_method(self, attr_name: str, match_type: str, value: str | bool) -> dict[str, Any]:
        """
        Map XPath attribute to UiSelector method.

        Args:
            attr_name: XPath attribute name
            match_type: Type of match (exact, contains, starts_with, matches)
            value: Attribute value

        Returns:
            Method dictionary
        """
        # Map XPath attributes to UiSelector methods
        attr_mapping = {
            "text": {
                "exact": "text",
                "contains": "textContains",
                "starts_with": "textStartsWith",
                "matches": "textMatches"
            },
            "content-desc": {
                "exact": "description",
                "contains": "descriptionContains",
                "starts_with": "descriptionStartsWith",
                "matches": "descriptionMatches"
            },
            "resource-id": {
                "exact": "resourceId",
                "matches": "resourceIdMatches"
            },
            "package": {
                "exact": "packageName",
                "matches": "packageNameMatches"
            },
            "class": {
                "exact": "className",
                "matches": "classNameMatches"
            },
            "checkable": {"exact": "checkable"},
            "checked": {"exact": "checked"},
            "clickable": {"exact": "clickable"},
            "enabled": {"exact": "enabled"},
            "focusable": {"exact": "focusable"},
            "focused": {"exact": "focused"},
            "long-clickable": {"exact": "longClickable"},
            "scrollable": {"exact": "scrollable"},
            "selected": {"exact": "selected"},
            "password": {"exact": "password"}
        }

        if attr_name in attr_mapping and match_type in attr_mapping[attr_name]:
            method_name = attr_mapping[attr_name][match_type]

            # Convert boolean values
            if attr_name in ["checkable", "checked", "clickable", "enabled", "focusable",
                           "focused", "long-clickable", "scrollable", "selected", "password"]:
                value = value.lower() == "true"

            return {"name": method_name, "args": [value]}

        raise ValueError("XPATH mapping error")

    def _xpath_to_ui(self, xpath_dict: dict[str, Any]) -> str:
        """
        Convert parsed XPath dictionary to UiSelector string.

        Args:
            xpath_dict: Parsed XPath dictionary

        Returns:
            UiSelector string
        """
        try:
            parts = ["new UiSelector()"]

            for method_data in xpath_dict.get("methods", []):
                name = method_data["name"]
                args = method_data.get("args", [])

                if name in ["childSelector", "fromParent"]:
                    # Handle hierarchical methods
                    if args and isinstance(args[0], dict):
                        nested_ui = self._xpath_to_ui(args[0])
                        parts.append(f".{name}({nested_ui})")
                    else:
                        parts.append(f".{name}({args[0] if args else ''})")
                else:
                    # Handle regular methods
                    arg_str = self._format_ui_arg(args[0]) if args else ""
                    parts.append(f".{name}({arg_str})")

            result = "".join(parts)
            return result + ";"

        except Exception as e:
            raise ConversionError(f"Failed to convert XPath to UiSelector: {e}") from e

    def _xpath_to_dict(self, xpath_dict: dict[str, Any]) -> dict[str, Any]:
        """
        Convert parsed XPath dictionary to Shadowstep dict format.

        Args:
            xpath_dict: Parsed XPath dictionary

        Returns:
            Shadowstep dict representation
        """
        result: dict[str, Any] = {}
        methods = xpath_dict.get("methods", [])

        if not methods:
            raise ValueError("No methods found in XPath")

        for method_data in methods:
            method_name = method_data["name"]
            args = method_data.get("args", [])

            if method_name not in XPATH_TO_SHADOWSTEP_DICT:
                raise NotImplementedError(f"Method '{method_name}' is not supported")

            self._validate_method_compatibility(method_name, result.keys())     # type: ignore

            if method_name in ["childSelector", "fromParent"]:
                if args and isinstance(args[0], dict):
                    nested_result = self._xpath_to_dict(args[0])
                    result[method_name] = nested_result
                else:
                    result[method_name] = args[0] if args else None
            else:
                converter = XPATH_TO_SHADOWSTEP_DICT[method_name]
                if not args:
                    raise ValueError(f"Method '{method_name}' requires an argument")

                converted = converter(args[0])
                result.update(converted)

        return result

    def _format_ui_arg(self, arg: Any) -> str:
        """
        Format argument for UiSelector string.

        Args:
            arg: Argument to format

        Returns:
            Formatted argument string
        """
        if isinstance(arg, bool):
            return "true" if arg else "false"
        if isinstance(arg, int):
            return str(arg)
        if isinstance(arg, str):
            # Escape quotes and backslashes
            escaped = arg.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return str(arg)

    def _validate_method_compatibility(self, new_method: str, existing_methods: list[str]) -> None:
        """
        Validate that new method is compatible with existing methods.

        Args:
            new_method: New method to add
            existing_methods: List of already added methods

        Raises:
            ValueError: If methods are incompatible
        """
        if not existing_methods:
            return

        for group_name, group_methods in self._compatible_groups.items():
            if new_method in group_methods:
                for existing in existing_methods:
                    if (existing in group_methods and existing != new_method and
                            group_name in ["text", "description", "resource", "class"]):
                            raise ValueError(
                                f"Conflicting methods: '{existing}' and '{new_method}' "
                                f"belong to the same group '{group_name}'. "
                                f"Only one method per group is allowed."
                            )
                break

    def _build_compatibility_groups(self) -> dict[str, list[str]]:
        """Build compatibility groups for methods."""
        return {
            "text": ["text", "textContains", "textStartsWith", "textMatches"],
            "description": ["description", "descriptionContains", "descriptionStartsWith", "descriptionMatches"],
            "resource": ["resourceId", "resourceIdMatches", "packageName", "packageNameMatches"],
            "class": ["className", "classNameMatches"],
            "boolean": ["checkable", "checked", "clickable", "longClickable", "enabled",
                       "focusable", "focused", "scrollable", "selected", "password"],
            "numeric": ["index", "instance"],
            "hierarchy": ["childSelector", "fromParent"]
        }
