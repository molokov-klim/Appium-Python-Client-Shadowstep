# shadowstep/element/base.py
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, cast

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
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepNoSuchElementError,
    ShadowstepTimeoutException,
)
from shadowstep.locator_converter.locator_converter import LocatorConverter
from shadowstep.utils.utils import get_current_func_name

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.shadowstep import Shadowstep


class ElementBase:
    """
    A base class for interacting with web elements in the Shadowstep application.
    """

    def __init__(self,
                 locator: tuple[str, str] | dict[str, str] | str | WebElement,
                 base: Shadowstep,
                 timeout: float = 30,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: WaitExcTypes | None = None,
                 contains: bool = False,
                 native: WebElement | None = None):
        self.logger = logger
        self.driver: WebDriver = None
        self.locator: tuple[str, str] | dict[str, str] | Element = locator
        self.base = base  # Shadowstep instance
        self.timeout: float = timeout
        self.poll_frequency: float = poll_frequency
        self.ignored_exceptions: WaitExcTypes | None = ignored_exceptions
        self.contains: bool = contains
        self.native: WebElement = native
        self.id = None
        self.locator_converter = LocatorConverter()

    def _get_element(self,
                     locator: tuple[str, str] | dict[str, str] | str | WebElement,
                     timeout: float = 3,
                     poll_frequency: float = 0.5,
                     ignored_exceptions: WaitExcTypes | None = None,
                     contains: bool = False) -> WebElement:
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
        wait = WebDriverWait(driver=self.driver,
                             timeout=timeout,
                             poll_frequency=poll_frequency,
                             ignored_exceptions=ignored_exceptions)
        locator = self.handle_locator(locator, contains)
        try:
            element = wait.until(EC.presence_of_element_located(locator))
            self.id = element.id
            return cast(WebElement, element)
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
            self.logger.debug(f"{get_current_func_name()} {locator=} {error}")
            raise

    def handle_locator(self,
                       locator: tuple[str, str] | dict[str, str] | str | WebElement,
                       contains: bool = False) -> tuple[str, str] | None:
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

    def handle_dict_locator(self, locator, contains: bool = False) -> tuple[str, str] | None:
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
