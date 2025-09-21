# shadowstep/element/waiting.py
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support.wait import WebDriverWait

from shadowstep.decorators.decorators import log_debug
from shadowstep.element import conditions
from shadowstep.element.utilities import ElementUtilities

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.locator import LocatorConverter
    from shadowstep.shadowstep import Shadowstep


class ElementWaiting:
    def __init__(self, element: Element) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    @log_debug()
    def wait(self, timeout: int = 10, poll_frequency: float = 0.5,  # noqa: C901
             return_bool: bool = False) -> Element | bool:  # noqa: C901
        start_time: float = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                resolved_locator: tuple[str, str] | None = self.converter.to_xpath(self.element.remove_null_value(self.element.locator))
                if not resolved_locator:
                    self.logger.error("Resolved locator is None or invalid")
                    if return_bool:
                        return False
                    return self.element
                WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(
                    conditions.present(resolved_locator)
                )
                if return_bool:
                    return True
                return self.element
            except TimeoutException:
                if return_bool:
                    return False
                return self.element
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except Exception as error:
                self.logger.error(f"{error}")
                continue
        return False

    @log_debug()
    def wait_visible(self, timeout: int = 10, poll_frequency: float = 0.5, return_bool: bool = False) -> Element | bool:
        start_time: float = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                resolved_locator: tuple[str, str] | None = self.converter.to_xpath(self.element.remove_null_value(self.element.locator))
                if not resolved_locator:
                    self.logger.error("Resolved locator is None or invalid")
                    return True if return_bool else self.element

                if self._wait_for_visibility_with_locator(resolved_locator, timeout, poll_frequency):
                    return True if return_bool else self.element

            except Exception as error:
                self._handle_wait_visibility_errors(error)
                if isinstance(error, StaleElementReferenceException):
                    continue

        return True if return_bool else self.element

    @log_debug()
    def wait_clickable(self, timeout: int = 10, poll_frequency: float = 0.5,
                       return_bool: bool = False) -> Element | bool:
        start_time: float = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                resolved_locator: tuple[str, str] | None = self.converter.to_xpath(self.element.remove_null_value(self.element.locator))
                if not resolved_locator:
                    self.logger.error("Resolved locator is None or invalid")
                    return True if return_bool else self.element

                if self._wait_for_clickability_with_locator(resolved_locator, timeout, poll_frequency):
                    return True if return_bool else self.element

            except Exception as error:
                self._handle_wait_clickability_errors(error)
                if isinstance(error, StaleElementReferenceException):
                    continue

        return True if return_bool else self.element

    @log_debug()
    def wait_for_not(self, timeout: int = 10, poll_frequency: float = 0.5, return_bool: bool = False) -> Element | bool:
        start_time: float = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                resolved_locator: tuple[str, str] | None = self.converter.to_xpath(self.element.remove_null_value(self.element.locator))
                if not resolved_locator:
                    return True if return_bool else self.element

                if self._wait_for_not_present_with_locator(resolved_locator, timeout, poll_frequency):
                    return True if return_bool else self.element

            except Exception as error:
                self._handle_wait_for_not_errors(error)
                if isinstance(error, StaleElementReferenceException):
                    continue

        return False

    @log_debug()
    def wait_for_not_visible(self, timeout: int = 10, poll_frequency: float = 0.5,
                             return_bool: bool = False) -> Element | bool:
        start_time: float = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                resolved_locator: tuple[str, str] | None = self.converter.to_xpath(self.element.remove_null_value(self.element.locator))
                if not resolved_locator:
                    return True if return_bool else self.element

                if self._wait_for_not_visible_with_locator(resolved_locator, timeout, poll_frequency):
                    return True if return_bool else self.element

            except Exception as error:
                self._handle_wait_for_not_visible_errors(error)
                if isinstance(error, StaleElementReferenceException):
                    continue

        return True if return_bool else self.element

    @log_debug()
    def wait_for_not_clickable(self, timeout: int = 10, poll_frequency: float = 0.5,
                               return_bool: bool = False) -> Element | bool:
        start_time: float = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                resolved_locator: tuple[str, str] | None = self.converter.to_xpath(self.element.remove_null_value(self.element.locator))
                if not resolved_locator:
                    self.logger.error("Resolved locator is None or invalid")
                    return True if return_bool else self.element

                if self._wait_for_not_clickable_with_locator(resolved_locator, timeout, poll_frequency):
                    return True if return_bool else self.element

            except Exception as error:
                self._handle_wait_for_not_clickable_errors(error)
                if isinstance(error, StaleElementReferenceException):
                    continue

        return True if return_bool else self.element

    def _wait_for_visibility_with_locator(self, resolved_locator: tuple[str, str], timeout: int,
                                          poll_frequency: float) -> bool:
        """Wait for element visibility using resolved locator."""
        try:
            WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(
                conditions.visible(resolved_locator)
            )
            return True
        except TimeoutException:
            return False

    def _wait_for_clickability_with_locator(self, resolved_locator: tuple[str, str], timeout: int,
                                            poll_frequency: float) -> bool:
        """Wait for element clickability using resolved locator."""
        try:
            WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(
                conditions.clickable(resolved_locator)
            )
            return True
        except TimeoutException:
            return False

    def _wait_for_not_present_with_locator(self, resolved_locator: tuple[str, str], timeout: int,
                                           poll_frequency: float) -> bool:
        """Wait for element to not be present using resolved locator."""
        try:
            WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(
                conditions.not_present(resolved_locator)
            )
            return True
        except TimeoutException:
            return False

    def _handle_wait_visibility_errors(self, error: Exception) -> None:
        """Handle errors during wait visibility operation."""
        if isinstance(error,  # noqa   # type: ignore
                      (NoSuchDriverException, InvalidSessionIdException, WebDriverException)):  # noqa   # type: ignore
            self.element.utilities.handle_driver_error(error)
        elif isinstance(error, StaleElementReferenceException):
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.element.native = None
            self.element.get_native()
        else:
            self.logger.error(f"{error}")

    def _handle_wait_clickability_errors(self, error: Exception) -> None:
        """Handle errors during wait clickability operation."""
        if isinstance(error,  # noqa   # type: ignore
                      (NoSuchDriverException, InvalidSessionIdException, WebDriverException)):  # noqa   # type: ignore
            self.element.utilities.handle_driver_error(error)
        elif isinstance(error, StaleElementReferenceException):
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.element.native = None
            self.element.get_native()
        else:
            self.logger.error(f"{error}")

    def _handle_wait_for_not_errors(self, error: Exception) -> None:
        """Handle errors during wait for not operation."""
        if isinstance(error,  # noqa   # type: ignore
                      (NoSuchDriverException, InvalidSessionIdException, WebDriverException)):  # noqa   # type: ignore
            self.element.utilities.handle_driver_error(error)
        elif isinstance(error, StaleElementReferenceException):
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.element.native = None
            self.element.get_native()
        else:
            self.logger.error(f"{error}")

    def _wait_for_not_visible_with_locator(self, resolved_locator: tuple[str, str], timeout: int,
                                           poll_frequency: float) -> bool:
        """Wait for element to not be visible using resolved locator."""
        try:
            WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(
                conditions.not_visible(resolved_locator)
            )
            return True
        except TimeoutException:
            return False

    def _handle_wait_for_not_visible_errors(self, error: Exception) -> None:
        """Handle errors during wait for not visible operation."""
        if isinstance(error, (NoSuchDriverException, InvalidSessionIdException, WebDriverException)):  # noqa
            self.element.utilities.handle_driver_error(error)
        elif isinstance(error, StaleElementReferenceException):
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.element.native = None
            self.element.get_native()
        else:
            self.logger.error(f"{error}")

    def _wait_for_not_clickable_with_locator(self, resolved_locator: tuple[str, str], timeout: int,
                                             poll_frequency: float) -> bool:
        """Wait for element to not be clickable using resolved locator."""
        try:
            WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(
                conditions.not_clickable(resolved_locator)
            )
            return True
        except TimeoutException:
            return False

    def _handle_wait_for_not_clickable_errors(self, error: Exception) -> None:
        """Handle errors during wait for not clickable operation."""
        if isinstance(error, (NoSuchDriverException, InvalidSessionIdException, WebDriverException)):  # noqa
            self.element.utilities.handle_driver_error(error)
        elif isinstance(error, StaleElementReferenceException):
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.element.native = None
            self.element.get_native()
        else:
            self.logger.error(f"{error}")
