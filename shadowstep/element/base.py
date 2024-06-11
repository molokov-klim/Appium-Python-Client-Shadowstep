import inspect
import logging
from typing import Union, List, Optional, Tuple, Dict

from selenium.types import WaitExcTypes
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from appium.webdriver import WebElement

from shadowstep.base import WebDriverSingleton


class ElementBase:
    def __init__(self):
        self.driver = None

    def _get_element(self, locator: Union[Tuple, Dict[str, str]], timeout: float = 3,
                     poll_frequency: float = 0.5,
                     ignored_exceptions: Optional[WaitExcTypes] = None) -> Union[WebElement, None]:
        wait = WebDriverWait(driver=self.driver, timeout=timeout,
                             poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
        locator = self.handle_locator(locator)
        try:
            element = wait.until(EC.presence_of_element_located(locator))
            return element
        except NoSuchElementException:
            return None
        except TimeoutException as error:
            logging.debug(f"Элемент не обнаружен!\n"
                          f"{locator=}\n"
                          f"{timeout=}\n\n" +
                          f"{error=}\n")
            return None
        except WebDriverException as error:
            logging.debug(f"Элемент не обнаружен!\n"
                          f"{locator=}\n"
                          f"{timeout=}\n\n" +
                          f"{error=}\n")
            return None

    def handle_locator(self, locator):
        if isinstance(locator, dict):
            locator = self.handle_dict_locator(locator)
        return locator

    @staticmethod
    def handle_dict_locator(locator,
                            contains: bool = False) -> Union[Tuple, None]:
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
            logging.error(f"Ошибка dict: {locator}")
            logging.error(f"{str(e)}")
            return None

    def _get_driver(self):
        if self.driver is None:
            self.driver = WebDriverSingleton.get_driver()
