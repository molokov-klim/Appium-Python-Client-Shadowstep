import inspect
import logging
import time
import traceback
import typing
from typing import Union, Tuple, Dict, Optional, cast

import xml.etree.ElementTree as ET

from appium.webdriver import WebElement
from icecream import ic
from selenium.common import NoSuchDriverException, InvalidSessionIdException, WebDriverException, \
    StaleElementReferenceException
from selenium.types import WaitExcTypes
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.remote.shadowroot import ShadowRoot

from shadowstep.element.base import ElementBase
from shadowstep.utils.utils import find_coordinates_by_vector

# Configure the root logger (basic configuration)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeneralElementException(WebDriverException):
    """Raised when driver is not specified and cannot be located."""

    def __init__(
            self, msg: Optional[str] = None, screen: Optional[str] = None,
            stacktrace: Optional[typing.Sequence[str]] = None
    ) -> None:
        super().__init__(msg, screen, stacktrace)


class Element(ElementBase):
    """
    A class to represent a UI element in the Shadowstep application.
    """

    def __init__(self,
                 locator: Union[Tuple, Dict[str, str], str, WebElement, 'Element'] = None,
                 base=None,
                 timeout: int = 30,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                 contains: bool = False):
        super().__init__(locator, base, timeout, poll_frequency, ignored_exceptions, contains)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"Initialized Element with locator: {self.locator}")

    def __repr__(self):
        return f"Element(locator={self.locator}"

    def get_element(self,
                    locator: Union[Tuple, Dict[str, str]],
                    timeout: int = 3,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: Optional[WaitExcTypes] = None,
                    contains: bool = False) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            self._get_driver()
            locator = self.handle_locator(locator, contains)
            current_element = self._get_element(locator=self.locator,
                                                timeout=self.timeout,
                                                poll_frequency=self.poll_frequency,
                                                ignored_exceptions=self.ignored_exceptions,
                                                contains=contains)
            inner_element = current_element.find_element(*locator)
            return Element(locator=inner_element,
                           base=self.base,
                           timeout=timeout,
                           poll_frequency=poll_frequency,
                           ignored_exceptions=ignored_exceptions,
                           contains=contains)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} NoSuchDriverException")
            self.base.reconnect()
            return None
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} InvalidSessionIdException")
            self.base.reconnect()
            return None

    def get_elements(self,
                     locator: Union[Tuple, Dict[str, str], str] = None,
                     contains: bool = False) -> Union[typing.List['Element'], None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            self._get_driver()
            locator = self.handle_locator(locator, contains)
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

    def get_attributes(self,
                       desired_attributes: typing.List[str] = None,
                       tries: int = 3) -> Dict[str, str]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        for _ in range(tries):
            try:
                self._get_driver()
                # Инициализация пустого словаря для хранения атрибутов
                result = {}

                # Если desired_attributes не указан, установка значения 'all'
                if not desired_attributes:
                    desired_attributes = 'all'

                # Если desired_attributes не указан, установка значения 'all'
                root = ET.fromstring(self.driver.page_source)

                # Поиск требуемого элемента по критериям атрибутов
                found_element = None
                for element in root.iter():
                    if 'bounds' in element.attrib and 'class' in element.attrib:
                        if self.get_attribute('bounds') == element.attrib['bounds'] and self.get_attribute('class') == \
                                element.attrib['class']:
                            found_element = element
                            break

                # Если элемент найден, получение его атрибутов
                if found_element is not None:
                    attributes = found_element.attrib
                    # Сохранение атрибутов в словаре result
                    for attribute_name, attribute_value in attributes.items():
                        result[attribute_name] = attribute_value

                # Если desired_attributes указан, фильтрация словаря result
                if desired_attributes:
                    new_result = {}
                    for attribute in desired_attributes:
                        if attribute not in result:
                            # Возврат всех атрибутов если не найден искомый
                            return result
                        new_result[attribute] = result[attribute]
                    # Возврат отфильтрованных атрибутов
                    return new_result
                # Возврат всех атрибутов
                return result
            except StaleElementReferenceException:
                continue

    def tap(self, duration: Optional[int] = None) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                element = self._get_element(locator=self.locator)
                x, y = self.get_center(element)
                if x is None or y is None:
                    continue
                self.driver.tap(positions=[(x, y)], duration=duration)
                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}\n{duration}",
            stacktrace=traceback.format_stack()
        )

    def tap_and_move(
            self,
            locator: Union[Tuple, WebElement, 'Element', Dict[str, str], str] = None,
            x: int = None,
            y: int = None,
            direction: int = None,
            distance: int = None,
    ) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                # Получение координат центра исходного элемента
                element = self._get_element(locator=self.locator)
                x1, y1 = self.get_center(element)

                # Настройка жеста
                actions = ActionChains(self.driver)
                actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
                actions.w3c_actions.pointer_action.move_to_location(x1, y1)
                actions.w3c_actions.pointer_action.pointer_down()

                # === Прямое указание координат ===
                if x is not None and y is not None:
                    actions.w3c_actions.pointer_action.move_to_location(x, y)
                    actions.w3c_actions.pointer_action.pointer_up()
                    actions.perform()
                    return cast('Element', self)

                # === Перемещение к другому элементу ===
                if locator is not None:
                    target_element = self._get_element(locator=locator)
                    x, y = self.get_center(target_element)
                    actions.w3c_actions.pointer_action.move_to_location(x, y)
                    actions.w3c_actions.pointer_action.pointer_up()
                    actions.perform()
                    return cast('Element', self)
                # === Перемещение по вектору направления ===
                if direction is not None and distance is not None:
                    width, height = self.base.terminal.get_screen_resolution()
                    x2, y2 = find_coordinates_by_vector(width=width, height=height,
                                                        direction=direction, distance=distance,
                                                        start_x=x1, start_y=y1)
                    actions.w3c_actions.pointer_action.move_to_location(x2, y2)
                    actions.w3c_actions.pointer_action.pointer_up()
                    actions.perform()
                    return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
        # === Недостаточно данных для действия ===
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}\n{locator=}\n{x=}\n{y=}\n{direction}\n{distance}\n",
            stacktrace=traceback.format_stack()
        )

    def click(self, duration: int = None):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                self._get_element(locator=self.locator)
                if duration is None:
                    self._mobile_gesture('mobile: clickGesture', {'elementId': self.id})
                else:
                    self._mobile_gesture('mobile: longClickGesture', {'elementId': self.id, 'duration': duration})
                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}\n{duration}",
            stacktrace=traceback.format_stack()
        )

    def click_double(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                self._get_element(locator=self.locator)
                self._mobile_gesture('mobile: doubleClickGesture', {'elementId': self.id})
                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def drag(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    # flinggesture
    # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-flinggesture
    def scroll_down(self):
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollgesture
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def scroll_up(self):
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollgesture
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def scroll_to_bottom(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def scroll_to_top(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def scroll_and_get(self):
        # https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-scroll
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def get_parent(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def get_parents(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def get_sibling(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def get_siblings(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def get_cousin(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def get_cousins(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def is_contains(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def zoom(self):
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-pinchopengesture
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    def unzoom(self):
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-pinchclosegesture
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

    # swipe
    # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-swipegesture

    def get_center(self, element: WebElement) -> Union[Tuple[int, int], None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
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
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            # Получение границ элемента
            left, top, right, bottom = map(int,
                                           element.get_attribute('bounds').strip("[]").replace("][", ",").split(","))
            return left, top, right, bottom
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} NoSuchDriverException")
            self.base.reconnect()
            return None
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} InvalidSessionIdException")
            self.base.reconnect()
            return None

    ################ override from appium/webdriver/webelement.py

    # Override
    def get_attribute(self, name: str) -> Optional[Union[str, Dict]]:
        """Gets the given attribute or property of the element.

        Override for Appium

        This method will first try to return the value of a property with the
        given name. If a property with that name doesn't exist, it returns the
        value of the attribute with the same name. If there's no attribute with
        that name, ``None`` is returned.

        Values which are considered truthy, that is equals "true" or "false",
        are returned as booleans.  All other non-``None`` values are returned
        as strings.  For attributes or properties which do not exist, ``None``
        is returned.

        Args:
            name: Name of the attribute/property to retrieve.

        Usage:
            # Check if the "active" CSS class is applied to an element.

            is_active = "active" in target_element.get_attribute("class")

        Returns:
            The given attribute or property of the element
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            self._get_driver()
            current_element = self._get_element(locator=self.locator,
                                                timeout=self.timeout,
                                                poll_frequency=self.poll_frequency,
                                                ignored_exceptions=self.ignored_exceptions)
            return current_element.get_attribute(name)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} {error}")
            self.base.reconnect()
            return None
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} {error}")
            self.base.reconnect()
            return None
        except WebDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} {error}")
            self.base.reconnect()
            return None

    # Override
    def is_displayed(self) -> bool:
        """Whether the element is visible to a user.

        Override for Appium
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    # Override
    def clear(self) -> 'WebElement':
        """Clears text.

        Override for Appium

        Returns:
            `appium.webdriver.webelement.WebElement`
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    # Override
    def set_text(self, keys: str = '') -> 'WebElement':
        """Sends text to the element.
        deprecated:: 2.8.1

        Previous text is removed.
        Android only.

        Args:
            keys: the text to be sent to the element.

        Usage:
            element.set_text('some text')

        Returns:
            `appium.webdriver.webelement.WebElement`
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    # Override
    @property
    def location_in_view(self) -> Dict[str, int]:
        """Gets the location of an element relative to the view.

        Usage:
            | location = element.location_in_view
            | x = location['x']
            | y = location['y']

        Returns:
            dict: The location of an element relative to the view
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    # Override
    def set_value(self, value: str) -> 'WebElement':
        """Set the value on this element in the application
        deprecated:: 2.8.1

        Args:
            value: The value to be set

        Returns:
            `appium.webdriver.webelement.WebElement`
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    # Override
    def send_keys(self, *value: str) -> 'WebElement':
        """Simulates typing into the element.

        Args:
            value: A string for typing.

        Returns:
            `appium.webdriver.webelement.WebElement`
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    ######## override from selenium/webdriver/remote/webelement.py

    @property
    def tag_name(self) -> str:
        """This element's ``tagName`` property."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    @property
    def text(self) -> str:
        """The text of the element."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def submit(self) -> None:
        """Submits a form."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def get_property(self, name) -> str | bool | WebElement | dict:
        """Gets the given property of the element.

        :Args:
            - name - Name of the property to retrieve.

        :Usage:
            ::

                text_length = target_element.get_property("text_length")
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def get_dom_attribute(self, name) -> str:
        """Gets the given attribute of the element. Unlike
        :func:`~selenium.webdriver.remote.BaseWebElement.get_attribute`, this
        method only returns attributes declared in the element's HTML markup.

        :Args:
            - name - Name of the attribute to retrieve.

        :Usage:
            ::

                text_length = target_element.get_dom_attribute("class")
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def is_selected(self) -> bool:
        """Returns whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def is_enabled(self) -> bool:
        """Returns whether the element is enabled."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    @property
    def shadow_root(self) -> ShadowRoot:
        """Returns a shadow root of the element if there is one or an error.
        Only works from Chromium 96, Firefox 96, and Safari 16.4 onwards.

        :Returns:
          - ShadowRoot object or
          - NoSuchShadowRoot - if no shadow root was attached to element
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    # RenderedWebElement Items
    @property
    def location_once_scrolled_into_view(self) -> dict:
        """THIS PROPERTY MAY CHANGE WITHOUT WARNING. Use this to discover where
        on the screen an element is so that we can click it. This method should
        cause the element to be scrolled into view.

        Returns the top lefthand corner location on the screen, or zero
        coordinates if the element is not visible.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    @property
    def size(self) -> dict:
        """The size of the element."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def value_of_css_property(self, property_name) -> str:
        """The value of a CSS property."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    @property
    def location(self) -> dict:
        """The location of the element in the renderable canvas."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    @property
    def rect(self) -> dict:
        """A dictionary with the size and location of the element."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    @property
    def aria_role(self) -> str:
        """Returns the ARIA role of the current web element."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    @property
    def accessible_name(self) -> str:
        """Returns the ARIA Level of the current webelement."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    @property
    def screenshot_as_base64(self) -> str:
        """Gets the screenshot of the current element as a base64 encoded
        string.

        :Usage:
            ::

                img_b64 = element.screenshot_as_base64
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    @property
    def screenshot_as_png(self) -> bytes:
        """Gets the screenshot of the current element as a binary data.

        :Usage:
            ::

                element_png = element.screenshot_as_png
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def save_screenshot(self, filename) -> bool:
        """Saves a screenshot of the current element to a PNG image file.
        Returns False if there is any IOError, else returns True. Use full
        paths in your filename.

        :Args:
         - filename: The full path you wish to save your screenshot to. This
           should end with a `.png` extension.

        :Usage:
            ::

                element.screenshot('/Screenshots/foo.png')
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def _handle_driver_error(self, error: Exception):
        self.logger.error(f"{inspect.currentframe().f_code.co_name} {error}")
        self.base.reconnect()
        time.sleep(0.3)

    def _mobile_gesture(self, name: str, params: Union[dict, list]) -> None:
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
        self.driver.execute_script(name, params)

    def _ensure_session_alive(self) -> None:
        try:
            self._get_driver()
        except NoSuchDriverException:
            self.logger.warning("Reconnecting driver due to session issue")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.warning("Reconnecting driver due to session issue")
            self.base.reconnect()
