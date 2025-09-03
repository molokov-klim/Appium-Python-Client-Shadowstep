# shadowstep/element/dom_navigation.py
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.types import WaitExcTypes
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from shadowstep.element.element import GeneralElementException
from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    from shadowstep.element.element import Element


class DomNavigation:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_element(self,
                    locator: tuple[str, str] | dict[str, str],
                    timeout: int = 30,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: WaitExcTypes | None = None,
                    contains: bool = False) -> Element:
        self.logger.debug(f"{get_current_func_name()}")

        if isinstance(locator, "Element"):
            locator = locator.locator

        # XPath for parent
        parent_locator = self.handle_locator(self.locator, self.contains)
        if not parent_locator:
            raise GeneralElementException("Failed to resolve parent locator")

        # XPath for child (relative)
        pre_inner_locator = self.handle_locator(locator, contains)
        if not pre_inner_locator:
            raise GeneralElementException("Failed to resolve child locator")
        inner_path = pre_inner_locator[1].lstrip("/")  # Remove accidental `/` in front

        # Guaranteed nesting: parent//child
        if not inner_path.startswith("//"):
            inner_path = f"//{inner_path}"

        inner_locator = ("xpath", f"{parent_locator[1]}{inner_path}")

        return Element(locator=inner_locator,
                       base=self.base,
                       timeout=timeout,
                       poll_frequency=poll_frequency,
                       ignored_exceptions=ignored_exceptions,
                       contains=contains)

    def get_elements(  # noqa: C901
            self,
            locator: tuple[str, str] | dict[str, str] | Element,
            timeout: float = 30,
            poll_frequency: float = 0.5,
            ignored_exceptions: WaitExcTypes | None = None,
            contains: bool = False
    ) -> list[Element]:
        """
        method is greedy
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        # [Step] Normalize locator
        step = "Normalizing locator"
        self.logger.debug(f"[{step}] started")
        if isinstance(locator, Element):
            locator = locator.locator

        # [Step] Resolve base XPath
        step = "Resolving base XPath"
        self.logger.debug(f"[{step}] started")
        base_xpath = self._get_xpath()
        if not base_xpath:
            raise GeneralElementException("Unable to resolve base xpath")

        # [Step] Convert locator to XPath
        step = "Converting locator to XPath"
        self.logger.debug(f"[{step}] started")
        locator = self.locator_converter.to_xpath(locator)
        locator = self._contains_to_xpath(locator)

        # [Step] Iteratively collect elements
        step = "Collecting elements"
        self.logger.debug(f"[{step}] started")

        self.logger.info(f"{locator=}")
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                wait = WebDriverWait(
                    driver=self.driver,
                    timeout=timeout,
                    poll_frequency=poll_frequency,
                    ignored_exceptions=ignored_exceptions,
                )
                wait.until(expected_conditions.presence_of_element_located(locator))
                native_parent = self._get_native()
                native_elements = native_parent.find_elements(*locator)

                elements = []
                for native_element in native_elements:
                    # [Extract attributes]
                    attributes = {
                        attr: native_element.get_attribute(attr) for attr in [
                            "resource-id", "bounds",
                            "class", "text", "content-desc", "checkable", "checked",
                            "clickable", "enabled", "focusable", "focused",
                            "long-clickable", "scrollable", "selected", "displayed"
                        ]
                    }
                    element = Element(
                        locator=attributes,
                        base=self.base,
                        timeout=timeout,
                        poll_frequency=poll_frequency,
                        ignored_exceptions=ignored_exceptions,
                        contains=contains
                    )
                    elements.append(element)
                return elements

            except NoSuchDriverException as error:
                self._handle_driver_error(error)

            except InvalidSessionIdException as error:
                self._handle_driver_error(error)

            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self._get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self._handle_driver_error(error)
                    continue
                raise

            except TimeoutException as error:
                self.logger.warning(f"Timeout while waiting for presence of element | {error}")
                continue
        # if nothing found return empty list
        return []
