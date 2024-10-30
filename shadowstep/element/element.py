import inspect
import logging
import typing
from typing import Union, Tuple, Dict, Optional, cast

from appium.webdriver import WebElement
from selenium.common import NoSuchDriverException, InvalidSessionIdException
from selenium.types import WaitExcTypes
from shadowstep.element.base import ElementBase

# Configure the root logger (basic configuration)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Element(ElementBase):
    """
    A class to represent a UI element in the Shadowstep application.
    """

    def __init__(self,
                 locator: Union[Tuple, Dict[str, str], str, WebElement, 'Element'] = None,
                 base=None,
                 timeout: int = 30,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None):
        super().__init__(locator, base, timeout, poll_frequency, ignored_exceptions)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"Initialized Element with locator: {self.locator}")

    def __repr__(self):
        return f"Element(locator={self.locator}"

    def get_element(self, locator: Union[Tuple, Dict[str, str], str] = None) -> Union['Element', None]:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            self._get_driver()
            locator = self.handle_locator(locator)
            current_element = self._get_element(locator=self.locator)
            inner_element = current_element.find_element(*locator)
            return Element(inner_element, self.base)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} NoSuchDriverException")
            self.base.reconnect()
            return None
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} InvalidSessionIdException")
            self.base.reconnect()
            return None

    def get_elements(self, locator: Union[Tuple, Dict[str, str], str] = None) -> Union[typing.List['Element'], None]:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            self._get_driver()
            locator = self.handle_locator(locator)
            current_element = self._get_element(locator=self.locator)
            inner_elements = current_element.find_elements(*locator)
            elements = []
            for element in inner_elements:
                elements.append(Element(element, self.base))
            return elements
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} NoSuchDriverException")
            self.base.reconnect()
            return None
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} InvalidSessionIdException")
            self.base.reconnect()
            return None

    def get_attributes(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def tap(self, duration: Optional[int] = None) -> Union['Element', None]:
        """
        Tap on the element.

        Args:
            duration : Optional[int], optional
                The duration for the tap action in milliseconds (default is None).

        Returns:
            Element
                The current Element instance after the tap action.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            self._get_driver()
            element = self._get_element(locator=self.locator)
            x, y = self.get_center(element)
            self.driver.tap(positions=[(x, y)], duration=duration)
            return cast('Element', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} NoSuchDriverException")
            self.base.reconnect()
            return cast('Element', self)
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} InvalidSessionIdException")
            self.base.reconnect()
            return cast('Element', self)

    def tap_and_move(self):
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-draggesture
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def click(self):
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-clickgesture
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    # longclickgesture
    # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-longclickgesture

    # double click
    # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-doubleclickgesture

    def click_and_move(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    # flinggesture
    # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-flinggesture
    def scroll_down(self):
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollgesture
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def scroll_up(self):
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollgesture
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def scroll_to_bottom(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def scroll_to_top(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def scroll_and_get(self):
        # https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-scroll
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def get_parent(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def get_parents(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def get_sibling(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def get_siblings(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def get_cousin(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def get_cousins(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def is_contains(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def zoom(self):
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-pinchopengesture
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    def unzoom(self):
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-pinchclosegesture
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

    # swipe
    # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-swipegesture

    def get_center(self, element: WebElement) -> Union[Tuple[int, int], None]:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            left, top, right, bottom = self.get_coordinates(element)
            # Расчет координат центра элемента
            x = int((left + right) / 2)
            y = int((top + bottom) / 2)
            return x, y
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} NoSuchDriverException")
            self.base.reconnect()
            return None
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} InvalidSessionIdException")
            self.base.reconnect()
            return None

    def get_coordinates(self, element: WebElement) -> Union[Tuple[int, int, int, int], None]:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            # Получение границ элемента
            left, top, right, bottom = map(int, element.get_attribute('bounds').strip("[]").replace("][", ",").split(","))
            return left, top, right, bottom
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} NoSuchDriverException")
            self.base.reconnect()
            return None
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} InvalidSessionIdException")
            self.base.reconnect()
            return None

