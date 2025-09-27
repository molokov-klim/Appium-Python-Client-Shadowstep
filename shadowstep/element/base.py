"""Element base module for Shadowstep framework.

This module provides the base functionality for element interactions,
including element location, driver management, and utility methods.
"""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, cast

from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from shadowstep.base import WebDriverSingleton
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepNoSuchElementError,
    ShadowstepTimeoutException,
)
from shadowstep.locator.converter.locator_converter import LocatorConverter
from shadowstep.utils.utils import get_current_func_name

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver
    from selenium.types import WaitExcTypes

    from shadowstep.element.element import Element
    from shadowstep.locator import UiSelector
    from shadowstep.shadowstep import Shadowstep


class ElementBase:
    """A shadowstep class for interacting with web elements in the Shadowstep application."""

    def __init__(self,  # noqa: PLR0913
                 locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                 shadowstep: Shadowstep,
                 timeout: float = 30,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: WaitExcTypes | None = None,
                 native: WebElement | None = None) -> None:
        """Initialize ElementBase with locator and configuration.

        Args:
            locator: The locator used to find the element.
            shadowstep: The Shadowstep instance.
            timeout: Maximum time to wait for element operations.
            poll_frequency: Interval for polling operations.
            ignored_exceptions: Exceptions to ignore during waiting.
            native: Native WebElement if already available.

        """
        self.logger = logger
        self.driver: WebDriver = cast("WebDriver", None)
        self.locator: tuple[str, str] | dict[str, Any] | Element | UiSelector = locator  # type: ignore[assignment]
        self.shadowstep = shadowstep
        self.timeout: float = timeout
        self.poll_frequency: float = poll_frequency
        self.ignored_exceptions: WaitExcTypes | None = ignored_exceptions
        self.native: WebElement | None = native
        self.converter = LocatorConverter()
        self.id: str = cast("str", None)

    def _get_web_element(self,
                         locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                         timeout: float = 3,
                         poll_frequency: float = 0.5,
                         ignored_exceptions: WaitExcTypes | None = None) -> WebElement:
        """Retrieve a web element based on the specified locator.

        Args:
            locator: The locator used to find the element.
            timeout: The maximum time to wait for the element to be located (default is 3 seconds).
            poll_frequency: The interval at which to poll for the element (default is 0.5 seconds).
            ignored_exceptions: A list of exceptions to ignore while waiting for the element.

        Returns:
            The located web element.

        Raises:
            ShadowstepNoSuchElementError: If element is not found.
            ShadowstepTimeoutException: If element is not found within timeout.

        """
        self.logger.debug("%s", get_current_func_name())
        self.get_driver()
        if isinstance(locator, WebElement):
            return locator
        wait = WebDriverWait(driver=self.driver,
                             timeout=timeout,
                             poll_frequency=poll_frequency,
                             ignored_exceptions=ignored_exceptions)
        locator = self.remove_null_value(locator)
        if not locator:
            raise ShadowstepNoSuchElementError(msg="Failed to resolve locator", locator=locator)
        try:
            locator = LocatorConverter().to_xpath(locator)
            element = wait.until(expected_conditions.presence_of_element_located(locator))
            self.id = element.id
            return cast("WebElement", element)
        except NoSuchElementException as error:
            self.logger.debug("%s locator=%s %s", get_current_func_name(), locator, error)
            raise ShadowstepNoSuchElementError(
                msg=error.msg,
                screen=error.screen,
                stacktrace=list(error.stacktrace) if error.stacktrace else None,
                locator=locator,
            ) from error
        except TimeoutException as error:
            self.logger.debug("%s locator=%s %s", get_current_func_name(), locator, error)
            if error.stacktrace is not None:
                for stack in error.stacktrace:
                    if "NoSuchElementError" in stack:
                        raise ShadowstepNoSuchElementError(
                            msg=error.msg,
                            screen=error.screen,
                            stacktrace=list(error.stacktrace) if error.stacktrace else None,
                            locator=locator,
                        ) from error
            raise ShadowstepTimeoutException(
                msg=f"Timeout waiting for element with locator: {locator}. Original: {error.msg}",
                screen=error.screen,
                stacktrace=list(error.stacktrace) if error.stacktrace else None,
                locator=locator,
                driver=self.driver,
            ) from error
        except InvalidSessionIdException as error:
            self.logger.debug("%s locator=%s %s", get_current_func_name(), locator, error)
            raise
        except WebDriverException as error:
            self.logger.debug("%s locator=%s %s", get_current_func_name(), locator, error)
            raise

    def remove_null_value(self,
                          locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                          ) -> tuple[str, str] | dict[str, Any] | Element | UiSelector:
        """Remove null values from locator tuple.

        Args:
            locator: The locator to process.

        Returns:
            The processed locator with null values removed.

        """
        self.logger.debug("%s", get_current_func_name())
        if isinstance(locator, tuple):
            by, value = locator
            # Remove parts like [@attr='null']
            value = re.sub(r"\[@[\w\-]+='null']", "", value)
            return by, value
        if isinstance(locator, dict):
            # Remove keys where value == 'null'
            return {k: v for k, v in locator.items() if v != "null"}
        return locator

    def get_driver(self) -> None:
        """Retrieve the WebDriver instance, creating it if necessary.

        Returns:
            The WebDriver instance.

        """
        self.logger.debug("%s", get_current_func_name())
        self.driver = WebDriverSingleton.get_driver()
