import inspect
import logging
import typing
from typing import Union, List, Optional, Tuple, Dict

from selenium.types import WaitExcTypes
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from appium.webdriver import WebElement

from shadowstep.base import WebDriverSingleton
from shadowstep.element.element import Element

# Configure the root logger (basic configuration)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ElementBase:
    """
    A base class for interacting with web elements in the Shadowstep application.
    """

    def __init__(self,
                 locator: Union[Tuple, Dict[str, str], str, WebElement] = None,
                 base=None,
                 timeout: int = 30,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.driver = None
        self.locator = locator
        self.base = base  # Shadowstep instance
        self.timeout = timeout
        self.poll_frequency = poll_frequency
        self.ignored_exceptions = ignored_exceptions

    def _get_element(self, locator: Union[Tuple, Dict[str, str]], timeout: float = 3,
                     poll_frequency: float = 0.5,
                     ignored_exceptions: Optional[WaitExcTypes] = None) -> Union[WebElement, None]:
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
        wait = WebDriverWait(driver=self.driver, timeout=timeout,
                             poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
        locator = self.handle_locator(locator)
        try:
            element = wait.until(EC.presence_of_element_located(locator))
            return element
        except NoSuchElementException:
            logging.debug(f"{inspect.currentframe().f_code.co_name}")
            return None
        except TimeoutException as error:
            logging.debug(f"{inspect.currentframe().f_code.co_name}")
            return None
        except WebDriverException as error:
            logging.debug(f"{inspect.currentframe().f_code.co_name}")
            return None

    def handle_locator(self, locator: Union[Tuple, Dict[str, str], str, WebElement, 'Element']):
        """
        Handle the provided locator and convert it if necessary.

        Args:
            locator : Union[Tuple, Dict[str, str], str, WebElement, 'Element']
                The locator to be processed.

        Returns:
            Union[Tuple, None]
                The processed locator or None if not valid.
        """
        if isinstance(locator, tuple):
            return locator
        elif isinstance(locator, WebElement):
            raise NotImplementedError
        elif isinstance(locator, Element):
            raise NotImplementedError
        elif isinstance(locator, dict):
            locator = self.handle_dict_locator(locator)
        return locator

    @staticmethod
    def handle_dict_locator(locator) -> Union[Tuple, None]:
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
        if 'class' not in locator:
            xpath = "//*"
        else:
            xpath = "//" + locator['class']
        try:
            for attr, value in locator.items():
                xpath += f"[contains(@{attr}, '{value}')]"
                new_locator = ("xpath", xpath)
                return new_locator
            for attr, value in locator.items():
                xpath += f"[@{attr}='{value}']"
            new_locator = ("xpath", xpath)
            return new_locator
        except KeyError as e:
            logging.error(f"{inspect.currentframe().f_code.co_name}")
            logging.error(f"{str(e)}")
            return None

    def _get_driver(self):
        """
        Retrieve the WebDriver instance, creating it if necessary.

        Returns:
            WebDriverSingleton
                The WebDriver instance.
        """
        if self.driver is None:
            self.driver = WebDriverSingleton.get_driver()
