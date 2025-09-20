# shadowstep/element/utilities.py
from __future__ import annotations

import logging
import re
import time
from typing import TYPE_CHECKING, Any

from lxml import etree as etree
from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.locator import UiSelector
from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.shadowstep import Shadowstep


class ElementUtilities:
    def __init__(self, element: Element):
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.logger: logging.Logger = logging.getLogger(get_current_func_name())

    def remove_null_value(self,
                          locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                          ) -> tuple[str, str] | dict[str, Any] | Element | UiSelector:
        self.logger.debug(f"{get_current_func_name()}")
        if isinstance(locator, tuple):
            by, value = locator
            # Удаляем части типа [@attr='null']
            value = re.sub(r"\[@[\w\-]+='null']", "", value)
            return by, value
        if isinstance(locator, dict):
            # Удаляем ключи, у которых значение == 'null'
            return {k: v for k, v in locator.items() if v != "null"}
        return locator

    def extract_el_attrs_from_source(
            self, xpath_expr: str, page_source: str
    ) -> list[dict[str, Any]]:
        """Parse page source and extract attributes of all elements matching XPath."""
        try:
            parser = etree.XMLParser(recover=True)
            root = etree.fromstring(page_source.encode("utf-8"), parser=parser)
            matches = root.xpath(self.remove_null_value(("xpath", xpath_expr)[1]))  # type: ignore
            if not matches:
                self.logger.warning(f"No matches found for XPath: {xpath_expr}")
                return []
            result = [
                {**{k: str(v) for k, v in el.attrib.items()}}
                for el in matches
            ]
            self.logger.debug(f"Matched {len(result)} elements: {result}")
            return result
        except (etree.XPathEvalError, etree.XMLSyntaxError, UnicodeEncodeError) as error:
            self.logger.error(f"Parsing error: {error}")
            if isinstance(error, etree.XPathEvalError):
                self.logger.error(f"XPath: {xpath_expr}")
            raise ShadowstepElementException(f"Parsing error: {xpath_expr}") from error

    def get_xpath(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        locator = self.remove_null_value(self.element.locator)
        if isinstance(locator, tuple):
            return locator[1]
        return self._get_xpath_by_driver()

    def _get_xpath_by_driver(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        try:
            attrs = self.element.get_attributes()
            if not attrs:
                raise ShadowstepElementException("Failed to retrieve attributes for XPath construction.")
            return self.element.utilities.build_xpath_from_attributes(attrs)
        except (AttributeError, KeyError, WebDriverException) as e:
            self.logger.error(f"Error forming XPath: {str(e)}")
        return ""

    def handle_driver_error(self, error: Exception) -> None:
        self.logger.warning(f"{get_current_func_name()} {error}")
        self.shadowstep.reconnect()
        time.sleep(0.3)

    def _build_xpath_attribute_condition(self, key: str, value: str) -> str:
        """Build XPath attribute condition based on value content."""
        if value is None or value == "null":
            return f"[@{key}]"
        if "'" in value and '"' not in value:
            return f'[@{key}="{value}"]'
        if '"' in value and "'" not in value:
            return f"[@{key}='{value}']"
        if "'" in value and '"' in value:
            parts = value.split('"')
            escaped = "concat(" + ", ".join(
                f'"{part}"' if i % 2 == 0 else "'\"'" for i, part in enumerate(parts)) + ")"
            return f"[@{key}={escaped}]"
        return f"[@{key}='{value}']"

    def build_xpath_from_attributes(self, attrs: dict[str, Any]) -> str:
        """Build XPath from element attributes."""
        xpath = "//"
        element_type = attrs.get("class")
        except_attrs = ["hint", "selection-start", "selection-end", "extras"]

        # Start XPath with element class or wildcard
        if element_type:
            xpath += element_type
        else:
            xpath += "*"

        for key, value in attrs.items():
            if key in except_attrs:
                continue
            xpath += self._build_xpath_attribute_condition(key, value)
        return xpath

    def _ensure_session_alive(self) -> None:
        self.logger.debug(f"{get_current_func_name()}")
        try:
            self.element.get_driver()
        except NoSuchDriverException:
            self.logger.warning("Reconnecting driver due to session issue")
            self.shadowstep.reconnect()
        except InvalidSessionIdException:
            self.logger.warning("Reconnecting driver due to session issue")
            self.shadowstep.reconnect()

    def _get_first_child_class(self, tries: int = 3) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        for _ in range(tries):
            try:
                parent_element = self
                parent_class = parent_element.element.get_attribute("class")
                child_elements = parent_element.element.get_elements(("xpath", "//*[1]"))
                for _i, child_element in enumerate(child_elements):
                    child_class = child_element.get_attribute("class")
                    if parent_class != child_class:
                        return str(child_class)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.handle_driver_error(error)
                    continue
                raise
        return ""  # Return empty string if no child class found
