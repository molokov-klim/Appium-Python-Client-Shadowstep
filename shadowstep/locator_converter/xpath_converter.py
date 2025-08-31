# shadowstep/locator_converter/xpath_converter.py
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from shadowstep.locator_converter.map.xpath_to_dict import XPATH_TO_SHADOWSTEP_DICT
from shadowstep.locator_converter.types.xpath import XPathAttribute


@dataclass
class XPathPredicate:
    """Represents a single XPath predicate."""
    attribute: str
    operator: str
    value: str
    function: str | None = None


@dataclass
class XPathExpression:
    """Represents parsed XPath expression."""
    element: str
    predicates: list[XPathPredicate]
    position: int | None = None
    child_path: str | None = None
    parent_path: str | None = None


class XPathConverter:
    """
    Converts XPath expressions to UiSelector and Dictionary formats.
    
    Supports:
    - Basic attribute predicates (@text, @resource-id, etc.)
    - Function-based predicates (contains, starts-with, matches)
    - Position predicates ([1], [position()=2])
    - Hierarchical paths (//element1/element2)
    - Complex expressions with multiple predicates
    """

    def __init__(self):
        """Initialize the converter with logging."""
        self.logger = logging.getLogger(__name__)
        
        # XPath attribute to UiSelector method mapping
        self.xpath_to_ui_mapping = {
            '@text': 'text',
            '@content-desc': 'description',
            '@resource-id': 'resourceId',
            '@package': 'packageName',
            '@class': 'className',
            '@password': 'password',
            '@checkable': 'checkable',
            '@checked': 'checked',
            '@clickable': 'clickable',
            '@enabled': 'enabled',
            '@focusable': 'focusable',
            '@focused': 'focused',
            '@long-clickable': 'longClickable',
            '@scrollable': 'scrollable',
            '@selected': 'selected'
        }

    def xpath_to_uiselector(self, xpath: str) -> str:
        """
        Convert XPath expression to UiSelector string.
        
        Args:
            xpath: XPath expression string
            
        Returns:
            UiSelector string in Java format
            
        Raises:
            ValueError: If XPath cannot be converted
        """
        try:
            parsed = self._parse_xpath(xpath)
            return self._build_uiselector(parsed)
        except Exception as e:
            raise ValueError(f"Failed to convert XPath to UiSelector: {e}") from e

    def xpath_to_dict(self, xpath: str) -> dict[str, Any]:
        """
        Convert XPath expression to Shadowstep Dictionary format.
        
        Args:
            xpath: XPath expression string
            
        Returns:
            Dictionary representation of the XPath
            
        Raises:
            ValueError: If XPath cannot be converted
        """
        try:
            parsed = self._parse_xpath(xpath)
            return self._build_dict(parsed)
        except Exception as e:
            raise ValueError(f"Failed to convert XPath to Dictionary: {e}") from e

    def _parse_xpath(self, xpath: str) -> XPathExpression:
        """
        Parse XPath expression into structured format.
        
        Args:
            xpath: XPath expression string
            
        Returns:
            Parsed XPath expression
        """
        # Clean and normalize XPath
        xpath = xpath.strip()
        
        # Handle hierarchical paths
        if '//' in xpath:
            parts = xpath.split('//')
            if len(parts) > 2:
                # Complex hierarchical path
                return self._parse_hierarchical_xpath(xpath)
            else:
                # Simple //element path
                element = parts[-1]
        else:
            element = xpath.lstrip('/')
        
        # Extract element name and predicates
        element_match = re.match(r'^([a-zA-Z0-9_*]+)(.*)$', element)
        if not element_match:
            raise ValueError(f"Invalid XPath element: {element}")
        
        element_name = element_match.group(1)
        predicates_str = element_match.group(2)
        
        # Parse predicates
        predicates = self._parse_predicates(predicates_str)
        
        # Extract position if present
        position = self._extract_position(predicates_str)
        
        return XPathExpression(
            element=element_name,
            predicates=predicates,
            position=position
        )

    def _parse_hierarchical_xpath(self, xpath: str) -> XPathExpression:
        """
        Parse complex hierarchical XPath expressions.
        
        Args:
            xpath: Hierarchical XPath expression
            
        Returns:
            Parsed XPath expression with hierarchy info
        """
        # Split by // and get the target element
        parts = xpath.split('//')
        target_element = parts[-1]
        
        # Check for parent navigation
        if '/..' in xpath:
            parent_path = xpath.split('/..')[0]
            return XPathExpression(
                element=target_element,
                predicates=[],
                parent_path=parent_path
            )
        
        # Check for child navigation
        if '/' in xpath and '//' in xpath:
            child_path = xpath.split('//')[-2] if len(parts) > 2 else None
            return XPathExpression(
                element=target_element,
                predicates=[],
                child_path=child_path
            )
        
        # Simple hierarchical path
        return XPathExpression(
            element=target_element,
            predicates=[]
        )

    def _parse_predicates(self, predicates_str: str) -> List[XPathPredicate]:
        """
        Parse XPath predicates into structured format.
        
        Args:
            predicates_str: String containing predicates
            
        Returns:
            List of parsed predicates
        """
        predicates = []
        
        # Extract all predicate expressions
        predicate_pattern = r'\[([^\]]+)\]'
        predicate_matches = re.findall(predicate_pattern, predicates_str)
        
        for pred_str in predicate_matches:
            predicate = self._parse_single_predicate(pred_str)
            if predicate:
                predicates.append(predicate)
        
        return predicates

    def _parse_single_predicate(self, pred_str: str) -> Optional[XPathPredicate]:
        """
        Parse a single XPath predicate.
        
        Args:
            pred_str: Single predicate string
            
        Returns:
            Parsed predicate or None if invalid
        """
        pred_str = pred_str.strip()
        
        # Handle function-based predicates
        if pred_str.startswith('contains('):
            return self._parse_contains_predicate(pred_str)
        if pred_str.startswith('starts-with('):
            return self._parse_starts_with_predicate(pred_str)
        if pred_str.startswith('matches('):
            return self._parse_matches_predicate(pred_str)
        if pred_str.startswith('position()'):
            return self._parse_position_predicate(pred_str)
        
        # Handle simple attribute predicates
        if '=' in pred_str:
            return self._parse_simple_predicate(pred_str)
        
        # Handle boolean predicates
        if pred_str in ['@enabled', '@clickable', '@focusable']:
            return XPathPredicate(
                attribute=pred_str,
                operator='=',
                value='true'
            )
        
        return None

    def _parse_contains_predicate(self, pred_str: str) -> XPathPredicate:
        """Parse contains() function predicate."""
        match = re.match(r'contains\(([^,]+),\s*["\']([^"\']+)["\']\)', pred_str)
        if match:
            attribute = match.group(1).strip()
            value = match.group(2)
            return XPathPredicate(
                attribute=attribute,
                operator='contains',
                value=value,
                function='contains'
            )
        raise ValueError(f"Invalid contains predicate: {pred_str}")

    def _parse_starts_with_predicate(self, pred_str: str) -> XPathPredicate:
        """Parse starts-with() function predicate."""
        match = re.match(r'starts-with\(([^,]+),\s*["\']([^"\']+)["\']\)', pred_str)
        if match:
            attribute = match.group(1).strip()
            value = match.group(2)
            return XPathPredicate(
                attribute=attribute,
                operator='starts-with',
                value=value,
                function='starts-with'
            )
        raise ValueError(f"Invalid starts-with predicate: {pred_str}")

    def _parse_matches_predicate(self, pred_str: str) -> XPathPredicate:
        """Parse matches() function predicate."""
        match = re.match(r'matches\(([^,]+),\s*["\']([^"\']+)["\']\)', pred_str)
        if match:
            attribute = match.group(1).strip()
            value = match.group(2)
            return XPathPredicate(
                attribute=attribute,
                operator='matches',
                value=value,
                function='matches'
            )
        raise ValueError(f"Invalid matches predicate: {pred_str}")

    def _parse_simple_predicate(self, pred_str: str) -> XPathPredicate:
        """Parse simple attribute=value predicate."""
        parts = pred_str.split('=', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid simple predicate: {pred_str}")
        
        attribute = parts[0].strip()
        value = parts[1].strip().strip('"\'')
        
        return XPathPredicate(
            attribute=attribute,
            operator='=',
            value=value
        )

    def _parse_position_predicate(self, pred_str: str) -> XPathPredicate:
        """Parse position() function predicate."""
        pred_str = pred_str.strip().rstrip(")")
        match = re.match(r"position\(\)\s*=\s*['\"]?(\d+)['\"]?$", pred_str)
        if match:
            value = int(match.group(1))
            return XPathPredicate(
                attribute="position",
                operator="=",
                value=str(value),  # храним 1-based!
                function="position",
            )
        raise ValueError(f"Invalid position predicate: {pred_str}")

    def _extract_position(self, predicates_str: str) -> Optional[int]:
        """Extract position from predicates string."""
        position_match = re.search(r"\[(\d+)\]", predicates_str)
        if position_match:
            pos = int(position_match.group(1)) - 1  # XPath → 0-based
            return pos if pos >= 0 else None
        return None

    def _build_uiselector(self, parsed: XPathExpression) -> str:
        """
        Build UiSelector string from parsed XPath.
        
        Args:
            parsed: Parsed XPath expression
            
        Returns:
            UiSelector string
        """
        selector_parts = ['new UiSelector()']
        
        # Handle parent navigation
        if parsed.parent_path:
            parent_selector = self._build_uiselector_from_path(parsed.parent_path)
            selector_parts.append(f'.fromParent({parent_selector})')
        
        # Handle child navigation
        if parsed.child_path:
            child_selector = self._build_uiselector_from_path(parsed.child_path)
            selector_parts.append(f'.childSelector({child_selector})')
        
        # Add predicates
        for predicate in parsed.predicates:
            ui_method = self._predicate_to_uiselector_method(predicate)
            if ui_method:
                selector_parts.append(ui_method)
        
        # Add position if specified
        if parsed.position is not None:
            selector_parts.append(f'.instance({parsed.position})')
        
        return ''.join(selector_parts)

    def _build_uiselector_from_path(self, path: str) -> str:
        """Build UiSelector for hierarchical paths."""
        # Simple implementation - can be enhanced
        return f'new UiSelector().className("{path}")'

    def _predicate_to_uiselector_method(self, predicate: XPathPredicate) -> Optional[str]:
        """
        Convert XPath predicate to UiSelector method.
        
        Args:
            predicate: Parsed XPath predicate
            
        Returns:
            UiSelector method string or None
        """
        if predicate.function == 'contains':
            return self._build_contains_method(predicate)
        elif predicate.function == 'starts-with':
            return self._build_starts_with_method(predicate)
        elif predicate.function == 'matches':
            return self._build_matches_method(predicate)
        elif predicate.function == 'position':
            return self._build_instance_method(predicate)
        else:
            return self._build_simple_method(predicate)

    def _build_contains_method(self, predicate: XPathPredicate) -> str:
        """Build contains method for UiSelector."""
        ui_method = self.xpath_to_ui_mapping.get(predicate.attribute)
        if not ui_method:
            return ''
        
        if predicate.attribute == '@text':
            return f'.textContains("{predicate.value}")'
        elif predicate.attribute == '@content-desc':
            return f'.descriptionContains("{predicate.value}")'
        elif predicate.attribute == '@resource-id':
            return f'.resourceIdMatches("{predicate.value}")'
        elif predicate.attribute == '@package':
            return f'.packageNameMatches("{predicate.value}")'
        elif predicate.attribute == '@class':
            return f'.classNameMatches("{predicate.value}")'
        
        return ''

    def _build_starts_with_method(self, predicate: XPathPredicate) -> str:
        """Build starts-with method for UiSelector."""
        ui_method = self.xpath_to_ui_mapping.get(predicate.attribute)
        if not ui_method:
            return ''
        
        if predicate.attribute == '@text':
            return f'.textStartsWith("{predicate.value}")'
        elif predicate.attribute == '@content-desc':
            return f'.descriptionStartsWith("{predicate.value}")'
        elif predicate.attribute == '@resource-id':
            return f'.resourceIdMatches("^{predicate.value}.*")'
        elif predicate.attribute == '@package':
            return f'.packageNameMatches("^{predicate.value}.*")'
        elif predicate.attribute == '@class':
            return f'.classNameMatches("^{predicate.value}.*")'
        
        return ''

    def _build_matches_method(self, predicate: XPathPredicate) -> str:
        """Build matches method for UiSelector."""
        ui_method = self.xpath_to_ui_mapping.get(predicate.attribute)
        if not ui_method:
            return ''
        
        if predicate.attribute == '@text':
            return f'.textMatches("{predicate.value}")'
        elif predicate.attribute == '@content-desc':
            return f'.descriptionMatches("{predicate.value}")'
        elif predicate.attribute == '@resource-id':
            return f'.resourceIdMatches("{predicate.value}")'
        elif predicate.attribute == '@package':
            return f'.packageNameMatches("{predicate.value}")'
        elif predicate.attribute == '@class':
            return f'.classNameMatches("{predicate.value}")'
        
        return ''

    def _build_instance_method(self, predicate: XPathPredicate) -> str:
        """Build instance method for UiSelector."""
        pos = int(predicate.value)
        if pos < 1:
            raise ValueError(f"Invalid position() value: {pos}. Must be >= 1.")
        return f".instance({pos - 1})"

    def _build_simple_method(self, predicate: XPathPredicate) -> str:
        """Build simple method for UiSelector."""
        ui_method = self.xpath_to_ui_mapping.get(predicate.attribute)
        if not ui_method:
            return ''
        
        # Handle boolean values
        if predicate.value.lower() in ['true', 'false']:
            return f'.{ui_method}({predicate.value.lower()})'
        
        # Handle string values
        return f'.{ui_method}("{predicate.value}")'

    def _build_dict(self, parsed: XPathExpression) -> dict[str, Any]:
        result: dict[str, Any] = {}

        if parsed.element != "*":
            result.update(XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.CLASS_NAME](parsed.element))

        for predicate in parsed.predicates:
            entry = self._predicate_to_dict_entry(predicate)
            if entry:
                result.update(entry)

        if parsed.position is not None:
            result.update(XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.INSTANCE](parsed.position))

        if parsed.child_path is not None:
            result.update(
                XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.CHILD_SELECTOR](parsed.child_path)
            )

        if parsed.parent_path is not None:
            result.update(XPATH_TO_SHADOWSTEP_DICT[XPathAttribute.FROM_PARENT](parsed.parent_path))

        return result

    def _predicate_to_dict_entry(self, predicate: XPathPredicate) -> dict[str, Any] | None:
        """
        Конвертирует предикат в Shadowstep dict через XPATH_TO_SHADOWSTEP_DICT.
        """
        try:
            # Определяем тип предиката → находим нужный XPathAttribute
            if predicate.function == "contains":
                if predicate.attribute == "@text":
                    attr = XPathAttribute.TEXT_CONTAINS
                elif predicate.attribute == "@content-desc":
                    attr = XPathAttribute.DESCRIPTION_CONTAINS
                elif predicate.attribute == "@resource-id":
                    attr = XPathAttribute.RESOURCE_ID_MATCHES
                elif predicate.attribute == "@package":
                    attr = XPathAttribute.PACKAGE_NAME_MATCHES
                elif predicate.attribute == "@class":
                    attr = XPathAttribute.CLASS_NAME_MATCHES
                else:
                    return None

            elif predicate.function == "starts-with":
                if predicate.attribute == "@text":
                    attr = XPathAttribute.TEXT_STARTS_WITH
                elif predicate.attribute == "@content-desc":
                    attr = XPathAttribute.DESCRIPTION_STARTS_WITH
                elif predicate.attribute == "@resource-id":
                    attr = XPathAttribute.RESOURCE_ID_MATCHES
                elif predicate.attribute == "@package":
                    attr = XPathAttribute.PACKAGE_NAME_MATCHES
                elif predicate.attribute == "@class":
                    attr = XPathAttribute.CLASS_NAME_MATCHES
                else:
                    return None

            elif predicate.function == "matches":
                if predicate.attribute == "@text":
                    attr = XPathAttribute.TEXT_MATCHES
                elif predicate.attribute == "@content-desc":
                    attr = XPathAttribute.DESCRIPTION_MATCHES
                elif predicate.attribute == "@resource-id":
                    attr = XPathAttribute.RESOURCE_ID_MATCHES
                elif predicate.attribute == "@package":
                    attr = XPathAttribute.PACKAGE_NAME_MATCHES
                elif predicate.attribute == "@class":
                    attr = XPathAttribute.CLASS_NAME_MATCHES
                else:
                    return None

            elif predicate.function == "position":
                attr = XPathAttribute.INDEX

            else:
                # Обычное равенство
                mapping = {
                    "@text": XPathAttribute.TEXT,
                    "@content-desc": XPathAttribute.DESCRIPTION,
                    "@resource-id": XPathAttribute.RESOURCE_ID,
                    "@package": XPathAttribute.PACKAGE_NAME,
                    "@class": XPathAttribute.CLASS_NAME,
                    "@checkable": XPathAttribute.CHECKABLE,
                    "@checked": XPathAttribute.CHECKED,
                    "@clickable": XPathAttribute.CLICKABLE,
                    "@enabled": XPathAttribute.ENABLED,
                    "@focusable": XPathAttribute.FOCUSABLE,
                    "@focused": XPathAttribute.FOCUSED,
                    "@long-clickable": XPathAttribute.LONG_CLICKABLE,
                    "@scrollable": XPathAttribute.SCROLLABLE,
                    "@selected": XPathAttribute.SELECTED,
                    "@password": XPathAttribute.PASSWORD,
                }
                attr = mapping.get(predicate.attribute)
                if not attr:
                    return None

            # Вызываем готовый маппинг
            factory = XPATH_TO_SHADOWSTEP_DICT[attr]
            return factory(self._extract_dict_value(predicate))

        except Exception as e:
            self.logger.warning(f"Не удалось преобразовать предикат {predicate}: {e}")
            return None

    def _extract_dict_value(self, predicate: XPathPredicate) -> Any:
        """Extract value for dictionary from predicate."""
        if predicate.function == 'position':
            return int(predicate.value)
        elif predicate.value.lower() in ['true', 'false']:
            return predicate.value.lower() == 'true'
        else:
            return predicate.value


# Convenience functions for easy usage
def xpath_to_uiselector(xpath: str) -> str:
    """
    Convert XPath to UiSelector string.
    
    Args:
        xpath: XPath expression
        
    Returns:
        UiSelector string
    """
    converter = XPathConverter()
    return converter.xpath_to_uiselector(xpath)


def xpath_to_dict(xpath: str) -> Dict[str, Any]:
    """
    Convert XPath to Dictionary format.
    
    Args:
        xpath: XPath expression
        
    Returns:
        Dictionary representation
    """
    converter = XPathConverter()
    return converter.xpath_to_dict(xpath)
