# shadowstep/element/properties.py
from __future__ import annotations

import inspect
import logging
import time
import traceback
from typing import TYPE_CHECKING, Any, cast

from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.remote.shadowroot import ShadowRoot

from shadowstep.decorators.decorators import log_debug
from shadowstep.element.utilities import ElementUtilities
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.locator import LocatorConverter, UiSelector
    from shadowstep.shadowstep import Shadowstep


class ElementProperties:
    def __init__(self, element: Element):
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    # Override
    @log_debug()
    def get_attribute(self, name: str) -> str:  # type: ignore[override]
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return cast(str, current_element.get_attribute(name))  # never seen not str
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'}('{name}') within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'}('{name}') within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def get_attributes(self) -> dict[str, Any]:
        xpath_expr = self._resolve_xpath_for_attributes()
        if not xpath_expr:
            return {}
        return self.utilities.extract_el_attrs_from_source(xpath_expr, self.shadowstep.driver.page_source)[0]

    @log_debug()
    def get_property(self, name: str) -> Any:
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.get_property(name)
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def get_dom_attribute(self, name: str) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.get_dom_attribute(name)
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    @log_debug()
    def is_displayed(self) -> bool:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.is_displayed()
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    #################################################################################3

    @log_debug()
    def is_visible(self) -> bool:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            result = self._check_element_visibility()
            if result is not None:
                return result
            time.sleep(0.1)
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def is_selected(self) -> bool:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.is_selected()
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def is_enabled(self) -> bool:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.is_enabled()
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def is_contains(self,
                    locator: tuple | dict[str, Any] | Element | UiSelector,
                    ) -> bool:
        from shadowstep.element.element import Element
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                if isinstance(locator, Element):
                    locator = locator.locator
                child_element = self.element._get_web_element(locator=locator)
                return child_element is not None
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def tag_name(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.tag_name
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve tag_name within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve tag_name within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def attributes(self):
        return self.get_attributes()

    @log_debug()
    def text(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.text
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve text within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve text within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def resource_id(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("resource-id")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def class_(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("class")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def index(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("index")
            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def package(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("package")
            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def class_name(self) -> str:  # 'class' is a reserved word, so class_name is better
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("class")
            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def bounds(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("bounds")
            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def checked(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("checked")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def checkable(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("checkable")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def enabled(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("enabled")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def focusable(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("focusable")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def focused(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("focused")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def long_clickable(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("long-clickable")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def password(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("password")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def scrollable(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("scrollable")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def selected(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("selected")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def displayed(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("displayed")
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def shadow_root(self) -> ShadowRoot:
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.shadow_root
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)
        raise ShadowstepElementException(
            msg=f"Failed to retrieve shadow_root within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def size(self) -> dict:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.size
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)
        raise ShadowstepElementException(
            msg=f"Failed to retrieve size within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def value_of_css_property(self, property_name: str) -> str:
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.value_of_css_property(property_name)
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)
        raise ShadowstepElementException(
            msg=f"Failed to retrieve CSS property '{property_name}' within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def location(self) -> dict:
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.location
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)
        raise ShadowstepElementException(
            msg=f"Failed to retrieve location within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def rect(self) -> dict:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.rect
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)
        raise ShadowstepElementException(
            msg=f"Failed to retrieve rect within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def aria_role(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.aria_role
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)
        raise ShadowstepElementException(
            msg=f"Failed to retrieve aria_role within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def accessible_name(self) -> str:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.accessible_name
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)
        raise ShadowstepElementException(
            msg=f"Failed to retrieve accessible_name within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def _resolve_xpath_for_attributes(self) -> str | None:
        """Resolve XPath expression from locator for attributes fetching."""
        try:
            xpath_expr = self.converter.to_xpath(self.element.locator)[1]
            if not xpath_expr:
                self.logger.error(f"Failed to resolve XPath from locator: {self.element.locator}")
                return None
            self.logger.debug(f"Resolved XPath: {xpath_expr}")
            return xpath_expr
        except Exception as e:
            self.logger.error(f"Exception in to_xpath: {e}")
            return None

    def _check_element_visibility(self) -> bool | None:
        """Check if element is visible, handling exceptions."""
        try:
            screen_size = self.shadowstep.terminal.get_screen_resolution()
            screen_width = screen_size[0]
            screen_height = screen_size[1]
            current_element = self.element.get_native()

            if current_element is None:
                return False
            if current_element.get_attribute("displayed") != "true":
                return False

            element_location = current_element.location
            element_size = current_element.size
            return self._check_element_bounds(element_location, element_size, screen_width, screen_height)

        except NoSuchElementException:
            return False
        except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
            self.element.utilities.handle_driver_error(error)
            return None
        except StaleElementReferenceException as error:
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.element.native = None
            self.element.get_native()
            return None
        except WebDriverException as error:
            err_msg = str(error).lower()
            if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                self.element.utilities.handle_driver_error(error)
                return None
            raise
    
    def _check_element_bounds(self, element_location: dict, element_size: dict, screen_width: int,
                              screen_height: int) -> bool:
        """Check if element is within screen bounds."""
        return not (
                element_location["y"] + element_size["height"] > screen_height or
                element_location["x"] + element_size["width"] > screen_width or
                element_location["y"] < 0 or
                element_location["x"] < 0
        )
