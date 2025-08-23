# shadowstep/element/base.py
from __future__ import annotations

import datetime
import inspect
import logging
import re
import typing
from typing import Dict, Optional, Tuple, Union

from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.types import WaitExcTypes
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from shadowstep.base import WebDriverSingleton
from shadowstep.utils.locator_converter import LocatorConverter
from shadowstep.utils.utils import get_current_func_name

logger = logging.getLogger(__name__)


class ShadowstepNoSuchElementError(NoSuchElementException):
    def __init__(self, msg: str, screen: str, stacktrace: list,
                 locator: Union[Tuple, Dict[str, str]]):
        super().__init__(msg, screen, stacktrace)
        self.locator = locator
        self.msg = msg
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self):
        return f"ShadowstepNoSuchElementError: Locator: {self.locator} \n Message: {self.msg} \n Stacktrace: {self.stacktrace}"


class ShadowstepTimeoutException(TimeoutException):
    """Custom timeout exception with additional context."""

    def __init__(self, msg: str = None, screen: str = None, stacktrace: list = None,
                 locator: Union[Tuple, Dict[str, str]] = None, driver=None):
        super().__init__(msg, screen, stacktrace)
        self.locator = locator
        self.driver = driver
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    def __str__(self):
        return (f"ShadowstepTimeoutException\n"
                f"Timestamp: {self.timestamp}\n"
                f"Message: {self.msg}\n"
                f"Locator: {self.locator}\n"
                f"Current URL: {self.driver.current_url if self.driver else 'N/A'}\n"
                f"Stacktrace:\n{''.join(self.stacktrace) if self.stacktrace else 'N/A'}")


class ElementBase:
    """
    A base class for interacting with web elements in the Shadowstep application.
    """

    def __init__(self,
                 locator: tuple[str, str] | dict[str, str] | str | WebElement,
                 base: "Shadowstep",
                 timeout: float = 30,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                 contains: bool = False,
                 native: WebElement = None):
        self.logger = logger
        self.driver: WebDriver = None
        self.locator: Union[Tuple, Dict[str, str], 'Element'] = locator
        self.base = base  # Shadowstep instance
        self.timeout: float = timeout
        self.poll_frequency: float = poll_frequency
        self.ignored_exceptions: typing.Optional[WaitExcTypes] = ignored_exceptions
        self.contains: bool = contains
        self.native: WebElement = native
        self.id = None
        self.locator_converter = LocatorConverter()

    def _get_element(self,
                     locator: Union[Tuple, Dict[str, str], WebElement],
                     timeout: float = 3,
                     poll_frequency: float = 0.5,
                     ignored_exceptions: Optional[WaitExcTypes] = None,
                     contains: bool = False) -> Union[WebElement, None]:
        """
        Retrieve a web element based on the specified locator.

        Args:
            locator : Union[Tuple, Dict[str, str]]
                The locator used to find the element.
            timeout : float, optional
                The maximum time to wait for the element to be located (default is 3 seconds).
            poll_frequency : float, optional
                The interval at which to poll for the element (default is 0.5 seconds).
            ignored_exceptions : Optional[WaitExcTypes], optional
                A list of exceptions to ignore while waiting for the element.

        Returns:
            Union[WebElement, None]
                The located web element, or None if not found.
        """
        self.logger.debug(f"{get_current_func_name()}")
        self._get_driver()
        if isinstance(locator, WebElement):
            return locator
        wait = WebDriverWait(driver=self.driver, timeout=timeout,
                             poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
        locator = self.handle_locator(locator, contains)
        try:
            element = wait.until(EC.presence_of_element_located(locator))
            self.id = element.id
            return element
        except NoSuchElementException as error:
            self.logger.debug(f"{get_current_func_name()} {locator=} {error}")
            raise ShadowstepNoSuchElementError(
                msg=error.msg,
                screen=error.screen,
                stacktrace=error.stacktrace,
                locator=locator
            )
        except TimeoutException as error:
            self.logger.debug(f"{get_current_func_name()} {locator=} {error}")
            for stack in error.stacktrace:
                if 'NoSuchElementError' in stack:
                    raise ShadowstepNoSuchElementError(
                        msg=error.msg,
                        screen=error.screen,
                        stacktrace=error.stacktrace,
                        locator=locator
                    )
            raise ShadowstepTimeoutException(
                msg=f"Timeout waiting for element with locator: {locator}. Original: {error.msg}",
                screen=error.screen,
                stacktrace=error.stacktrace,
                locator=locator,
                driver=self.driver
            )
        except InvalidSessionIdException as error:
            self.logger.debug(f"{get_current_func_name()} {locator=} {error}")
            raise
        except WebDriverException as error:
            from icecream import ic
            ic()
            ic("DEBUG INSTRUMENTATION PROCESS CRUSHED (INVESTIGATION)")
            self.logger.debug(f"{get_current_func_name()} {locator=} {error}")
            raise

    def handle_locator(self,
                       locator: Union[Tuple[str, str], Dict[str, str], str, WebElement],
                       contains: bool = False) -> Optional[Tuple[str, str]]:
        self.logger.debug(f"{get_current_func_name()}")
        if isinstance(locator, tuple):
            by, value = locator
            # Удаляем части типа [@attr='null']
            value = re.sub(r"\[@[\w\-]+='null'\]", "", value)
            return by, value
        elif isinstance(locator, dict):
            # Удаляем ключи, у которых значение == 'null'
            locator = {k: v for k, v in locator.items() if v != 'null'}
            locator = self.handle_dict_locator(locator, contains)
        return locator

    def handle_dict_locator(self, locator, contains: bool = False) -> Optional[Tuple[str, str]]:
        """
        Convert a dictionary locator to an XPath locator.

        Args:
            locator : Dict[str, str]
                The dictionary containing locator attributes.
            contains : bool, optional
                Indicates whether to use partial matching in the XPath (default is False).

        Returns:
            Union[Tuple, None]
                The XPath locator as a tuple, or None if there was an error.
        """
        self.logger.debug(f"{get_current_func_name()}")
        if 'class' not in locator:
            xpath = "//*"
        else:
            xpath = "//" + locator['class']
        try:
            if contains:
                for attr, value in locator.items():
                    xpath += f"[contains(@{attr}, '{value}')]"
                new_locator = ("xpath", xpath)
                return new_locator
            for attr, value in locator.items():
                xpath += f"[@{attr}='{value}']"
            new_locator = ("xpath", xpath)
            return new_locator
        except KeyError as e:
            self.logger.error(f"Ошибка dict: {locator}")
            self.logger.error(f"{str(e)}")
            return None

    def _get_driver(self):
        """
        Retrieve the WebDriver instance, creating it if necessary.

        Returns:
            WebDriverSingleton
                The WebDriver instance.
        """
        self.logger.debug(f"{get_current_func_name()}")
        self.driver = WebDriverSingleton.get_driver()
