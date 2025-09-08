# shadowstep/element/utilities.py
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, cast

from exceptions.shadowstep_exceptions import ShadowstepElementException
from lxml import etree as etree
from selenium.common import WebDriverException

from shadowstep.locator import UiSelector
from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.shadowstep import Shadowstep


class ElementUtilities:
    def __init__(self, element: "Element"):
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
            return self.element.build_xpath_from_attributes(attrs)
        except (AttributeError, KeyError, WebDriverException) as e:
            self.logger.error(f"Error forming XPath: {str(e)}")
        return ""
