"""Element actions module for Shadowstep framework.

This module provides action methods for interacting with UI elements,
including sending keys, clearing fields, setting values, and submitting forms.
"""
from __future__ import annotations

import inspect
import logging
import time
import traceback
from typing import TYPE_CHECKING

from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.decorators.decorators import log_debug
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException

if TYPE_CHECKING:
    from shadowstep.element import Element
    from shadowstep.element.utilities import ElementUtilities
    from shadowstep.locator import LocatorConverter
    from shadowstep.shadowstep import Shadowstep


class ElementActions:
    """Element actions handler for UI interactions.

    This class provides methods for performing actions on UI elements
    such as sending keys, clearing fields, setting values, and submitting forms.
    """

    def __init__(self, element: Element) -> None:
        """Initialize ElementActions with an element.

        Args:
            element: The Element instance to perform actions on.

        """
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    # Override
    @log_debug()
    def send_keys(self, *value: str) -> Element:
        """Send keys to the element.

        Args:
            *value: Variable number of string values to send to the element.

        Returns:
            Element: The current element instance for method chaining.

        Raises:
            ShadowstepElementException: If sending keys fails within timeout.

        """
        start_time = time.time()
        text = "".join(value)
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                element.send_keys(text)
                return self.element  # noqa: TRY300
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
                    msg=f"Failed to send_keys({text}) within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to send_keys({text}) within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    # Override
    @log_debug()
    def clear(self) -> Element:
        """Clear the element's text content.

        Returns:
            Element: The current element instance for method chaining.

        Raises:
            ShadowstepElementException: If clearing the element fails within timeout.

        """
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                current_element.clear()
                return self.element  # noqa: TRY300
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
                    msg=f"Failed to clear element within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to clear element within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    # Override
    @log_debug()
    def set_value(self, value: str) -> Element:
        """Set value for the element.

        Note: NOT IMPLEMENTED in UiAutomator2!

        Args:
            value: The value to set for the element.

        Returns:
            Element: The current element instance for method chaining.

        Raises:
            ShadowstepElementException: If setting value fails within timeout.

        """
        current_frame = inspect.currentframe()
        method_name = (current_frame.f_code.co_name
                      if current_frame else "unknown")
        self.logger.warning(
            "Method %s is not implemented in UiAutomator2", method_name)
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                element.set_value(value)  # type: ignore[attr-defined]
                return self.element  # noqa: TRY300
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
                    msg=f"Failed to set_value({value}) within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to set_value({value}) within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    # Override
    @log_debug()
    def submit(self) -> Element:
        """Submit the element (typically a form).

        Returns:
            Element: The current element instance for method chaining.

        Raises:
            ShadowstepElementException: If submitting the element fails within timeout.

        """
        current_frame = inspect.currentframe()
        method_name = (current_frame.f_code.co_name
                      if current_frame else "unknown")
        self.logger.warning(
            "Method %s is not implemented in UiAutomator2", method_name)
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                element.submit()
                return self.element  # noqa: TRY300
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
                    msg=f"Failed to submit element within {self.element.timeout=}",
                    stacktrace=traceback.format_stack(),
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to submit element within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )
