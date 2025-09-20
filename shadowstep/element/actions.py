# shadowstep/element/actions.py
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
from shadowstep.element.utilities import ElementUtilities
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.locator import LocatorConverter
    from shadowstep.shadowstep import Shadowstep


class ElementActions:
    def __init__(self, element: Element):
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    # Override
    @log_debug()
    def send_keys(self, *value: str) -> Element:
        start_time = time.time()
        text = "".join(value)
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                element.send_keys(text)
                return self.element
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
                    msg=f"Failed to send_keys({text}) within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to send_keys({text}) within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    @log_debug()
    def clear(self) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                current_element = self.element.get_native()
                current_element.clear()
                return self.element
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
                    msg=f"Failed to clear element within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to clear element within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    @log_debug()
    def set_value(self, value: str) -> Element:
        """
        NOT IMPLEMENTED in UiAutomator2!
        """
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                element.set_value(value)  # type: ignore
                return self.element
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
                    msg=f"Failed to set_value({value}) within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to set_value({value}) within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    @log_debug()
    def submit(self) -> Element:
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                element = self.element.get_native()
                element.submit()
                return self.element
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
                    msg=f"Failed to submit element within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to submit element within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )
