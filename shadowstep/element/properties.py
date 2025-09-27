"""Element properties module for Shadowstep framework.

This module provides property access functionality for elements,
including attributes, CSS properties, dimensions, and visibility checks.
"""
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

from shadowstep.decorators.decorators import log_debug
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException

if TYPE_CHECKING:
    from selenium.webdriver.remote.shadowroot import ShadowRoot

    from shadowstep.element.element import Element
    from shadowstep.element.utilities import ElementUtilities
    from shadowstep.locator import LocatorConverter, UiSelector
    from shadowstep.shadowstep import Shadowstep


class ElementProperties:
    """Element properties handler for Shadowstep framework."""

    def __init__(self, element: Element) -> None:
        """Initialize ElementProperties.

        Args:
            element: The element to get properties from.

        """
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    # Override
    @log_debug()
    def get_attribute(self, name: str) -> str:  # type: ignore[override]
        """Get element attribute value."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return cast("str", current_element.get_attribute(name))  # type: ignore[reportUnknownMemberType]  # never seen not str
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'}('{name}') within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'}('{name}') within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def get_attributes(self) -> dict[str, Any]:
        """Get all attributes of the element.

        Returns:
            dict[str, Any]: Dictionary containing all element attributes.

        """
        xpath_expr = self._resolve_xpath_for_attributes()
        if not xpath_expr:
            return {}
        extracted_attributes = self.utilities.extract_el_attrs_from_source(xpath_expr,
                                                                           self.shadowstep.driver.page_source)
        if any(extracted_attributes):
            return extracted_attributes[0]
        return {}

    @log_debug()
    def get_property(self, name: str) -> Any:
        """Get element property value."""
        self.logger.warning(
            "Method %s is not implemented in UiAutomator2",
            inspect.currentframe() if inspect.currentframe() else "unknown")
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.get_property(name)  # type: ignore[reportUnknownMemberType]
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def get_dom_attribute(self, name: str) -> str:
        """Get element DOM attribute value."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.get_dom_attribute(name)  # type: ignore[reportUnknownMemberType]
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    # Override
    @log_debug()
    def is_displayed(self) -> bool:
        """Check if element is displayed."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.is_displayed()
            except NoSuchElementException:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    #################################################################################3

    @log_debug()
    def is_visible(self) -> bool:
        """Check if element is visible."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            result = self._check_element_visibility()
            if result is not None:
                return result
            time.sleep(0.1)
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def is_selected(self) -> bool:
        """Check if element is selected."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.is_selected()
            except NoSuchElementException:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def is_enabled(self) -> bool:
        """Check if element is enabled."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.is_enabled()
            except NoSuchElementException:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def is_contains(self,
                    locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                    ) -> bool:
        """Check if element contains another element."""
        from shadowstep.element.element import Element  # noqa: PLC0415
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                if isinstance(locator, Element):
                    locator = locator.locator
                child_element = self.element._get_web_element(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
                    locator=locator)
                return child_element is not None  # type: ignore[reportUnnecessaryComparison]  # noqa: TRY300
            except NoSuchElementException:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def tag_name(self) -> str:
        """Get element tag name."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.tag_name  # noqa: TRY300
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve tag_name within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve tag_name within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def attributes(self) -> dict[str, Any]:
        """Get element attributes."""
        return self.get_attributes()

    @log_debug()
    def text(self) -> str:
        """Get element text."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.text  # noqa: TRY300
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve text within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve text within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def resource_id(self) -> str:
        """Get element resource ID."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("resource-id")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def class_(self) -> str:
        """Get element class."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("class")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def index(self) -> str:
        """Get element index."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("index")
            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:  # noqa: PERF203
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def package(self) -> str:
        """Get element package."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("package")
            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:  # noqa: PERF203
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def class_name(self) -> str:  # 'class' is a reserved word, so class_name is better
        """Get element class name."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("class")
            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:  # noqa: PERF203
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def bounds(self) -> str:
        """Get element bounds."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("bounds")
            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:  # noqa: PERF203
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def checked(self) -> str:
        """Get element checked state."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("checked")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def checkable(self) -> str:
        """Get element checkable state."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("checkable")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def enabled(self) -> str:
        """Get element enabled state."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("enabled")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def focusable(self) -> str:
        """Get element focusable state."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("focusable")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def focused(self) -> str:
        """Get element focused state."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("focused")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def long_clickable(self) -> str:
        """Get element long clickable state."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("long-clickable")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def password(self) -> str:
        """Get element password attribute."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("password")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def scrollable(self) -> str:
        """Get element scrollable attribute."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("scrollable")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def selected(self) -> str:
        """Get element selected attribute."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("selected")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def displayed(self) -> str:
        """Get element displayed attribute."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                return self.get_attribute("displayed")
            except NoSuchDriverException as error:  # noqa: PERF203
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
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to retrieve attr within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def shadow_root(self) -> ShadowRoot:
        """Get element shadow root."""
        self.logger.warning(
            "Method %s is not implemented in UiAutomator2",
            inspect.currentframe() if inspect.currentframe() else "unknown")
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                return element.shadow_root  # noqa: TRY300
            except NoSuchDriverException as error:  # noqa: PERF203
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)
        raise ShadowstepElementException(
            msg=f"Failed to retrieve shadow_root within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def size(self) -> dict[str, Any]:
        """Get element size."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.size  # type: ignore[reportUnknownMemberType]  # noqa: TRY300
            except NoSuchDriverException as error:  # noqa: PERF203
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
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def value_of_css_property(self, property_name: str) -> str:
        """Get element CSS property value."""
        self.logger.warning(
            "Method %s is not implemented in UiAutomator2",
            inspect.currentframe() if inspect.currentframe() else "unknown")
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.value_of_css_property(property_name)  # type: ignore[reportUnknownMemberType]
            except NoSuchDriverException as error:  # noqa: PERF203
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
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def location(self) -> dict[str, Any]:
        """Get element location."""
        self.logger.warning(
            "Method %s is not implemented in UiAutomator2",
            inspect.currentframe() if inspect.currentframe() else "unknown")
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.location  # type: ignore[reportUnknownMemberType]  # noqa: TRY300
            except NoSuchDriverException as error:  # noqa: PERF203
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
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def rect(self) -> dict[str, Any]:
        """Get element rectangle."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.rect  # type: ignore[reportUnknownMemberType]  # noqa: TRY300
            except NoSuchDriverException as error:  # noqa: PERF203
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
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def aria_role(self) -> str:
        """Get element ARIA role."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.aria_role  # noqa: TRY300
            except NoSuchDriverException as error:  # noqa: PERF203
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
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def accessible_name(self) -> str:
        """Get element accessible name."""
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                return current_element.accessible_name  # noqa: TRY300
            except NoSuchDriverException as error:  # noqa: PERF203
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
            stacktrace=traceback.format_stack(),
        )

    def _resolve_xpath_for_attributes(self) -> str | None:
        """Resolve XPath expression from locator for attributes fetching."""
        try:
            xpath_expr = self.converter.to_xpath(self.element.locator)[1]
            if not xpath_expr:
                self.logger.error("Failed to resolve XPath from locator: %s", self.element.locator)
                return None
            self.logger.debug("Resolved XPath: %s", xpath_expr)
            return xpath_expr  # noqa: TRY300
        except Exception:
            self.logger.exception("Exception in to_xpath")
            return None

    def _check_element_visibility(self) -> bool | None:  # noqa: PLR0911
        """Check if element is visible, handling exceptions."""
        try:
            screen_size = self.shadowstep.terminal.get_screen_resolution()  # type: ignore[reportOptionalMemberAccess]
            screen_width = screen_size[0]
            screen_height = screen_size[1]
            current_element = self.element.get_native()

            if current_element is None:  # type: ignore[reportUnnecessaryComparison]
                return False
            if current_element.get_attribute("displayed") != "true":  # type: ignore[reportUnknownMemberType]
                return False

            element_location = current_element.location  # type: ignore[reportUnknownMemberType]
            element_size = current_element.size  # type: ignore[reportUnknownMemberType]
            return self._check_element_bounds(
                element_location, element_size, screen_width, screen_height)  # type: ignore[reportUnknownMemberType]

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

    def _check_element_bounds(self, element_location: dict[str, Any],
                              element_size: dict[str, Any], screen_width: int,
                              screen_height: int) -> bool:
        """Check if element is within screen bounds."""
        return not (
                element_location["y"] + element_size["height"] > screen_height or
                element_location["x"] + element_size["width"] > screen_width or
                element_location["y"] < 0 or
                element_location["x"] < 0
        )
