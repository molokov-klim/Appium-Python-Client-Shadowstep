import re
from typing import Tuple, Optional, Dict, Union

from loguru import logger


class UiSelectorBuilder:
    """Constructs a UiSelector Java expression from a Shadowstep-style dictionary or XPath tuple."""

    SHADOWSTEP_TO_UISELECTOR = {
        "text": "text",
        "textContains": "textContains",
        "textStartsWith": "textStartsWith",
        "textMatches": "textMatches",
        "resource-id": "resourceId",
        "resourceIdMatches": "resourceIdMatches",
        "class": "className",
        "classNameMatches": "classNameMatches",
        "content-desc": "description",
        "descriptionContains": "descriptionContains",
        "descriptionStartsWith": "descriptionStartsWith",
        "descriptionMatches": "descriptionMatches",
        "index": "index",
        "instance": "instance",
        "package": "packageName",
        "packageNameMatches": "packageNameMatches",
        "enabled": "enabled",
        "focused": "focused",
        "clickable": "clickable",
        "long-clickable": "longClickable",
        "checkable": "checkable",
        "checked": "checked",
        "scrollable": "scrollable",
        "selected": "selected",
    }

    def build(self, selector: Union[Dict[str, Union[str, int, bool]], Tuple[str, str]]) -> Optional[Tuple[str, str]]:
        """Universal build method supporting dict and XPath-based selectors.

        Args:
            selector (Union[Dict, Tuple]): Shadowstep-style locator.

        Returns:
            Optional[str]: Java expression for UiSelector or None.
        """
        if isinstance(selector, dict):
            return "-android uiautomator", self.build_from_dict(selector)
        elif isinstance(selector, tuple):
            return "-android uiautomator", self.build_from_xpath(selector)
        else:
            logger.error(f"Unsupported selector type: {type(selector)}")
            return None

    def build_from_dict(self, selector: Dict[str, Union[str, int, bool]]) -> str:
        """Builds UiSelector expression from dict-based locator.

        Args:
            selector (Dict[str, Union[str, int, bool]]): Shadowstep-style dictionary.

        Returns:
            str: UiSelector Java string.
        """
        parts = ["new UiSelector()"]
        for key, value in selector.items():
            if key not in self.SHADOWSTEP_TO_UISELECTOR:
                continue
            method = self.SHADOWSTEP_TO_UISELECTOR[key]
            if isinstance(value, bool):
                value_str = "true" if value else "false"
                parts.append(f".{method}({value_str})")
            elif isinstance(value, int):
                parts.append(f".{method}({value})")
            else:
                escaped_value = str(value).replace('"', '\\"')
                parts.append(f'.{method}("{escaped_value}")')
        return "".join(parts)

    def build_from_xpath(self, selector: Tuple[str, str]) -> Optional[str]:
        """Converts simple XPath to UiSelector expression.

        Supports:
            - //*[@attr='value']
            - //*[@attr='value']/following-sibling::*[@attr2='value2'][N]

        Args:
            selector (Tuple[str, str]): Tuple of ('xpath', expression).

        Returns:
            Optional[str]: Java expression or None.
        """
        prefix, xpath = selector
        if prefix != "xpath":
            logger.error("Selector must start with 'xpath'")
            return None

        # Handle `following-sibling`
        if "/following-sibling::" in xpath:
            try:
                parent_part, child_part = xpath.split("/following-sibling::", 1)
                parent_selector = self.xpath_to_uiselector(parent_part)
                child_selector = self.xpath_to_uiselector(child_part)
                return f"{parent_selector}.fromParent({child_selector})"
            except Exception as e:
                logger.warning(f"Failed to parse XPath: {xpath}, error: {e}")
                return None
        else:
            return self.xpath_to_uiselector(xpath)

    def xpath_to_uiselector(self, xpath: str) -> str:
        """Helper to convert simple one-level XPath to UiSelector.

        Args:
            xpath (str): XPath string like //*[@text='...'][2] or [contains(@text, '...')]

        Returns:
            str: UiSelector expression
        """
        parts = ["new UiSelector()"]

        # Match [@attr='value']
        attr_eq_matches = re.findall(r"\[@([\w:-]+)='([^']+)'\]", xpath)

        # Match [contains(@attr, 'value')]
        attr_contains_matches = re.findall(r"\[contains\(@([\w:-]+),\s*'([^']+)'\)\]", xpath)

        for attr, value in attr_eq_matches:
            method = self.SHADOWSTEP_TO_UISELECTOR.get(attr)
            if not method:
                logger.warning(f"Unsupported XPath attr: {attr}")
                continue
            parts.append(f'.{method}("{value}")')

        for attr, value in attr_contains_matches:
            contains_method = f"{self.SHADOWSTEP_TO_UISELECTOR.get(attr, '')}Contains"
            if contains_method not in self.SHADOWSTEP_TO_UISELECTOR.values():
                logger.warning(f"Unsupported 'contains' XPath attr: {attr}")
                continue
            parts.append(f'.{contains_method}("{value}")')

        # Extract instance like [2] => .instance(1)
        index_match = re.search(r"\[(\d+)\]$", xpath)
        if index_match:
            idx = int(index_match.group(1)) - 1
            parts.append(f".instance({idx})")

        return "".join(parts)

    def xpath_to_dict(self, xpath: str) -> Dict[str, str]:
        """Parses simple XPath expression to a Shadowstep-style locator dictionary.

        Supports:
            - //*[@attr='value']
            - [contains(@attr, 'value')]
            - trailing index [N] → instance=N-1

        Args:
            xpath (str): XPath expression.

        Returns:
            Dict[str, str]: Parsed locator dictionary.
        """
        result = {}

        # Exact matches like [@text='value']
        attr_eq_matches = re.findall(r"\[@([\w:-]+)='([^']+)'\]", xpath)
        for attr, value in attr_eq_matches:
            result[attr] = value

        # Contains matches like [contains(@text, 'value')]
        attr_contains_matches = re.findall(r"\[contains\(@([\w:-]+),\s*'([^']+)'\)\]", xpath)
        for attr, value in attr_contains_matches:
            result[f"{attr}Contains"] = value

        # Index match like [2] at the end → instance=1 (zero-based)
        index_match = re.search(r"\[(\d+)\]$", xpath)
        if index_match:
            result["instance"] = str(int(index_match.group(1)) - 1)

        return result

    def dict_to_xpath(self, selector: Dict[str, Union[str, int, bool]]) -> str:
        """Converts a Shadowstep-style dictionary to an XPath expression.

        Args:
            selector (Dict[str, Union[str, int, bool]]): Dictionary locator.

        Returns:
            str: XPath string.
        """
        conditions = []
        for key, value in selector.items():
            if isinstance(value, bool):
                value = 'true' if value else 'false'
            elif isinstance(value, int):
                value = str(value)
            else:
                value = f"'{value}'"
            conditions.append(f"@{key}={value}")
        return f".//*[{ ' and '.join(conditions) }]"


    def to_xpath(self, selector: Union[Dict[str, Union[str, int, bool]], Tuple[str, str], str]) -> Optional[str]:
        """Converts dict, tuple or UiSelector Java string into XPath expression.

        Args:
            selector (Union[Dict, Tuple, str]): Locator in dict, xpath-tuple, or Java string form.

        Returns:
            Optional[str]: XPath expression or None.
        """
        if isinstance(selector, dict):
            return self.dict_to_xpath(selector)
        elif isinstance(selector, tuple) and selector[0] == "xpath":
            return selector[1]
        elif isinstance(selector, str) and selector.strip().startswith("new UiSelector()"):
            try:
                locator = self.xpath_to_dict(selector)
                return self.dict_to_xpath(locator)
            except Exception as e:
                logger.error(f"Failed to convert UiSelector to XPath: {e}")
                return None
        else:
            logger.error(f"Unsupported selector format for to_xpath: {type(selector)}")
            return None



