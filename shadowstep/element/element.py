# shadowstep/element/element.py
from __future__ import annotations

import inspect
import logging
import time
import traceback
from typing import TYPE_CHECKING, Any, cast

from appium.webdriver.webelement import WebElement
from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.types import WaitExcTypes
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.support.wait import WebDriverWait

from shadowstep.element import conditions
from shadowstep.element.actions import ElementActions
from shadowstep.element.base import ElementBase
from shadowstep.element.coordinates import ElementCoordinates
from shadowstep.element.dom import ElementDOM
from shadowstep.element.gestures import ElementGestures
from shadowstep.element.properties import ElementProperties
from shadowstep.element.screenshots import ElementScreenshots
from shadowstep.element.utilities import ElementUtilities
from shadowstep.element.waiting import ElementWaiting
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.locator import UiSelector
from shadowstep.utils.utils import find_coordinates_by_vector, get_current_func_name

if TYPE_CHECKING:
    from shadowstep.element.should import Should
    from shadowstep.shadowstep import Shadowstep

# Configure the root logger (basic configuration)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Element(ElementBase):
    """
    Public API for Element
    """

    def __init__(self,
                 locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                 shadowstep: Shadowstep,
                 timeout: float = 30,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: WaitExcTypes | None = None,
                 native: WebElement | None = None):
        # Convert Element to its locator if needed
        if isinstance(locator, Element):
            locator = locator.locator
        elif isinstance(locator, UiSelector):
            locator = cast(UiSelector, locator.__str__())
        super().__init__(locator, shadowstep, timeout, poll_frequency, ignored_exceptions, native)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug(f"Initialized Element with locator: {self.locator}")
        self.utilities = ElementUtilities(self)
        self.properties = ElementProperties(self)
        self.dom = ElementDOM(self)
        self.actions = ElementActions(self)
        self.gestures = ElementGestures(self)
        self.coordinates = ElementCoordinates(self)
        self.screenshots = ElementScreenshots(self)
        self.waiting = ElementWaiting(self)

    def __repr__(self):
        return f"Element(locator={self.locator!r}"

    """
    Element DOM navigation
    """

    def get_element(self,
                    locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                    timeout: int = 30,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: WaitExcTypes | None = None) -> Element:
        return self.dom.get_element(locator, timeout, poll_frequency, ignored_exceptions)

    def get_elements(
            self,
            locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
            timeout: float = 30,
            poll_frequency: float = 0.5,
            ignored_exceptions: WaitExcTypes | None = None
    ) -> list[Element]:
        return self.dom.get_elements(locator, timeout, poll_frequency, ignored_exceptions)

    def get_parent(self,
                   timeout: float = 30,
                   poll_frequency: float = 0.5,
                   ignored_exceptions: WaitExcTypes | None = None) -> Element:
        return self.dom.get_parent(timeout, poll_frequency, ignored_exceptions)

    def get_parents(self,
                    timeout: float = 30,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: WaitExcTypes | None = None) -> list[Element]:
        return self.dom.get_parents(timeout, poll_frequency, ignored_exceptions)

    def get_sibling(self,
                    locator: tuple[str, str] | dict[str, Any] | Element,
                    timeout: float = 30,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: WaitExcTypes | None = None) -> Element:
        return self.dom.get_sibling(locator, timeout, poll_frequency, ignored_exceptions)

    def get_siblings(self,
                     locator: tuple[str, str] | dict[str, Any] | Element,
                     timeout: float = 30.0,
                     poll_frequency: float = 0.5,
                     ignored_exceptions: WaitExcTypes | None = None) -> list[Element]:
        return self.dom.get_siblings(locator, timeout, poll_frequency, ignored_exceptions)

    def get_cousin(
            self,
            cousin_locator: tuple[str, str] | dict[str, Any] | Element,
            depth_to_parent: int = 1,
            timeout: float = 30.0,
            poll_frequency: float = 0.5,
            ignored_exceptions: WaitExcTypes | None = None
    ) -> Element:
        return self.dom.get_cousin(cousin_locator, depth_to_parent, timeout, poll_frequency, ignored_exceptions)

    def get_cousins(
            self,
            cousin_locator: tuple[str, str] | dict[str, Any] | Element,
            depth_to_parent: int = 1,
            timeout: float = 30.0,
            poll_frequency: float = 0.5,
            ignored_exceptions: WaitExcTypes | None = None
    ) -> list[Element]:
        return self.dom.get_cousins(cousin_locator, depth_to_parent, timeout, poll_frequency, ignored_exceptions)

    """
    Element Actions
    """

    # Override
    def send_keys(self, *value: str) -> Element:
        return self.actions.send_keys(*value)

    # Override
    def clear(self) -> Element:
        return self.actions.clear()

    # Override
    def set_value(self, value: str) -> Element:
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")
        return self.actions.set_value(value)

    # Override
    def submit(self) -> Element:
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")
        return self.actions.submit()

    """
    Element Gestures
    """

    def tap(self, duration: int = None) -> Element:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                x, y = self.get_center()
                if x is None or y is None:
                    continue
                self.driver.tap(positions=[(x, y)], duration=duration)
                return self
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}\n{duration}",
            stacktrace=traceback.format_stack()
        )

    def tap_and_move(
            self,
            locator: tuple[str, str] | WebElement | Element | dict[str, Any] | str | None = None,
            x: int = None,
            y: int = None,
            direction: int = None,
            distance: int = None,
    ) -> Element:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            result = self._perform_tap_and_move_action(locator, x, y, direction, distance)
            if result is not None:
                return result
            time.sleep(0.1)

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}\n{locator=}\n{x=}\n{y=}\n{direction}\n{distance}\n",
            stacktrace=traceback.format_stack()
        )

    def click(self, duration: int = None) -> Element:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                self._get_element(locator=self.locator)
                if duration is None:
                    self._mobile_gesture("mobile: clickGesture",
                                         {"elementId": self.id})
                else:
                    self._mobile_gesture("mobile: longClickGesture",
                                         {"elementId": self.id, "duration": duration})
                return self
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}\n{duration}",
            stacktrace=traceback.format_stack()
        )

    def click_double(self) -> Element:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                self._get_element(locator=self.locator)
                self._mobile_gesture("mobile: doubleClickGesture",
                                     {"elementId": self.id})
                return self
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    """
    
    """

    def get_attributes(self) -> dict[str, Any]:
        """Fetch all XML attributes of the element by matching locator against page source.

        Returns:
            Optional[dict[str, Any]]: Dictionary of all attributes, or None if not found.
        """
        self.logger.debug(f"{get_current_func_name()}")
        xpath_expr = self._resolve_xpath_for_attributes()
        if not xpath_expr:
            return {}
        return self.utilities.extract_el_attrs_from_source(xpath_expr, self.shadowstep.driver.page_source)[0]

    def get_center(self, element: WebElement | None = None) -> tuple[int, int]:
        """Get the center coordinates of the element.

        Args:
            element (Optional[WebElement]): Optional direct WebElement. If not provided, uses current locator.

        Returns:
            Optional[Tuple[int, int]]: (x, y) center point or None if element not found.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                if element is None:
                    element = self.get_native()
                coords = self.get_coordinates(element)
                if coords is None:
                    continue
                left, top, right, bottom = coords
                x = int((left + right) / 2)
                y = int((top + bottom) / 2)
                return x, y
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def get_coordinates(self, element: WebElement | None = None) -> tuple[int, int, int, int]:
        """Get the bounding box coordinates of the element.

        Args:
            element (Optional[WebElement]): Element to get bounds from. If None, uses internal locator.

        Returns:
            Optional[Tuple[int, int, int, int]]: (left, top, right, bottom) or None.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                if element is None:
                    element = self.get_native()
                bounds = element.get_attribute("bounds")
                if not bounds:
                    continue
                left, top, right, bottom = map(int, bounds.strip("[]").replace("][", ",").split(","))
                return left, top, right, bottom
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    def get_attribute(self, name: str) -> str:
        """Gets the specified attribute of the element.

        Args:
            name (str): Name of the attribute to retrieve.

        Returns:
            Optional[Union[str, Dict]]: Value of the attribute or None.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                current_element = self.get_native()
                return current_element.get_attribute(name)
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'}('{name}') within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def get_property(self, name: str) -> Any:
        """NOT IMPLEMENTED!
        Gets the given property of the element.

        Args:
            name (str): Name of the property to retrieve.

        Returns:
            Union[str, bool, dict, None]: Property value.
        """
        self.logger.debug(f"{get_current_func_name()}")
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                current_element = self.get_native()
                return current_element.get_property(name)
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def get_dom_attribute(self, name: str) -> str:
        """Gets the given attribute of the element. Unlike
        :func:`~selenium.webdriver.remote.BaseWebElement.get_attribute`, this
        method only returns attributes declared in the element's HTML markup.

        :Args:
            - name - Name of the attribute to retrieve.

        :Usage:
            ::

                text_length = target_element.get_dom_attribute("class")
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                current_element = self.get_native()
                return current_element.get_dom_attribute(name)
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    def is_displayed(self) -> bool:
        """Whether the element is visible to a user.

        Returns:
            bool: True if the element is displayed on screen and visible to the user.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                element = self.get_native()
                return element.is_displayed()
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def is_visible(self) -> bool:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            result = self._check_element_visibility()
            if result is not None:
                return result
            time.sleep(0.1)

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def is_selected(self) -> bool:
        """Returns whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.

        Returns:
            bool: True if the element is selected.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                element = self.get_native()
                return element.is_selected()
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def is_enabled(self) -> bool:
        """Returns whether the element is enabled.

        Returns:
            bool: True if the element is enabled.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                element = self.get_native()
                return element.is_enabled()
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def is_contains(self,
                    locator: tuple | dict[str, Any] | Element = None,
                    contains: bool = False
                    ) -> bool:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                if isinstance(locator, Element):
                    locator = locator.locator
                child_element = self._get_element(locator=locator)
                return child_element is not None
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def drag(self, end_x: int, end_y: int, speed: int = 2500) -> Element:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                self._get_element(locator=self.locator)
                self._mobile_gesture("mobile: dragGesture",
                                     {"elementId": self.id,
                                      "endX": end_x,
                                      "endY": end_y,
                                      "speed": speed})
                return self
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def fling_up(self, speed: int = 2500) -> Element:
        return self._fling(speed=speed, direction="up")

    def fling_down(self, speed: int = 2500) -> Element:
        return self._fling(speed=speed, direction="down")

    def fling_left(self, speed: int = 2500) -> Element:
        return self._fling(speed=speed, direction="left")

    def fling_right(self, speed: int = 2500) -> Element:
        return self._fling(speed=speed, direction="right")

    def _fling(self, speed: int, direction: str) -> Element:
        """
        direction: Direction of the fling. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
        speed: The speed at which to perform this gesture in pixels per second. The value must be greater than the minimum fling velocity for the given view (50 by default). The default value is 7500 * displayDensity
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-flinggesture
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                self._get_element(locator=self.locator)
                self._mobile_gesture("mobile: flingGesture",
                                     {"elementId": self.id,
                                      "direction": direction,
                                      "speed": speed})
                return self
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def scroll_down(self, percent: float = 0.7, speed: int = 2000, return_bool: bool = False) -> Element:
        self.logger.debug(f"{get_current_func_name()}")
        return self._scroll(direction="down", percent=percent, speed=speed, return_bool=return_bool)

    def scroll_up(self, percent: float = 0.7, speed: int = 2000, return_bool: bool = False) -> Element:
        self.logger.debug(f"{get_current_func_name()}")
        return self._scroll(direction="up", percent=percent, speed=speed, return_bool=return_bool)

    def scroll_left(self, percent: float = 0.7, speed: int = 2000, return_bool: bool = False) -> Element:
        self.logger.debug(f"{get_current_func_name()}")
        return self._scroll(direction="left", percent=percent, speed=speed, return_bool=return_bool)

    def scroll_right(self, percent: float = 0.7, speed: int = 2000, return_bool: bool = False) -> Element:
        self.logger.debug(f"{get_current_func_name()}")
        return self._scroll(direction="right", percent=percent, speed=speed, return_bool=return_bool)

    def _scroll(self, direction: str, percent: float, speed: int, return_bool: bool) -> Element:
        """
        direction: Scrolling direction. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
        percent: The size of the scroll as a percentage of the scrolling area size. Valid values must be float numbers greater than zero, where 1.0 is 100%. Mandatory value.
        speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 5000 * displayDensity
        return_bool: if true return bool else return self
        """
        self.logger.debug(f"{get_current_func_name()}")
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollgesture
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                self._get_element(locator=self.locator)
                can_scroll = self._mobile_gesture("mobile: scrollGesture",
                                                  {"elementId": self.id,
                                                   "percent": percent,
                                                   "direction": direction,
                                                   "speed": speed})
                if return_bool:
                    return can_scroll
                return self
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def scroll_to_bottom(self, percent: float = 0.7, speed: int = 8000) -> Element:
        """Scrolls down until the bottom is reached."""
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                if not self.scroll_down(percent=percent, speed=speed, return_bool=True):
                    return self
                self.scroll_down(percent=percent, speed=speed, return_bool=True)
            except (
                    NoSuchDriverException, InvalidSessionIdException, AttributeError
            ) as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to scroll to bottom within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def scroll_to_top(self, percent: float = 0.7, speed: int = 8000) -> Element:
        """Scrolls up until the top is reached."""
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                if not self.scroll_up(percent, speed, return_bool=True):
                    return self
                self.scroll_up(percent=percent, speed=speed, return_bool=True)
            except (
                    NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to scroll to top within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def _prepare_scroll_locator(self, locator: Element | dict[str, Any] | tuple[str, str]) -> tuple[str, str]:
        """Prepare locator for scrolling operation."""
        if isinstance(locator, Element):
            locator = locator.locator
        if isinstance(locator, (dict, tuple)):
            selector = self.converter.to_uiselector(locator)
        else:
            raise ShadowstepElementException("Only dictionary locators are supported")
        return self.converter.to_xpath(locator), selector

    def _execute_scroll_script(self, selector: str, max_swipes: int) -> None:
        """Execute mobile scroll script."""
        self.get_driver()
        self.driver.execute_script("mobile: scroll", {
            "elementId": self.id,
            "strategy": "-android uiautomator",
            "selector": selector,
            "maxSwipes": max_swipes
        })

    def _perform_scroll_to_element(self, selector: str, max_swipes: int, locator: tuple[str, str]) -> Element | None:
        """Perform scroll to element with error handling."""
        try:
            self._execute_scroll_script(selector, max_swipes)
            return cast(Element, self.shadowstep.get_element(locator))
        except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
            self.handle_driver_error(error)
            return None
        except StaleElementReferenceException as error:
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.native = None
            self.get_native()
            return None
        except WebDriverException as error:
            if "instrumentation process is not running" in str(error).lower():
                self.handle_driver_error(error)
                return None
            raise
        except Exception as error:
            self.logger.error(error)
            self.logger.error(type(error))
            self.logger.error(traceback.format_stack())
            self.handle_driver_error(error)
            self.scroll_to_top(percent=0.75, speed=8000)
            return None

    def scroll_to_element(self, locator: Element | dict[str, Any] | tuple[str, str], max_swipes: int = 30) -> Element:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        locator, selector = self._prepare_scroll_locator(locator)

        while time.time() - start_time < self.timeout:
            result = self._perform_scroll_to_element(selector, max_swipes, locator)
            if result is not None:
                return result
            time.sleep(0.1)

        raise ShadowstepElementException(
            msg=f"Failed to scroll to element with locator: {locator}",
            stacktrace=traceback.format_stack()
        )

    def _prepare_optional_scroll_locator(self, locator: Element | dict[str, Any] | tuple[str, str]) -> tuple[str, str]:
        """Prepare locator for optional scroll operation."""
        if isinstance(locator, Element):
            locator = locator.locator
        if isinstance(locator, (dict, tuple)):  # noqa
            pass
        else:
            raise ShadowstepElementException("Only dictionary locators are supported")
        return self.converter.to_xpath(locator), locator

    def _check_element_visibility_after_scroll(self, locator: tuple[str, str],
                                               waiting_element_timeout: int) -> Element | None:
        """Check if element is visible after scroll operation."""
        found = self.shadowstep.get_element(locator)
        found.timeout = waiting_element_timeout
        if found.is_visible():
            return found
        return None

    def _perform_optional_scroll_sequence(self, locator: tuple[str, str], percent: float, speed: int,
                                          waiting_element_timeout: int) -> Element | None:
        """Perform scroll sequence to find element."""
        self.get_driver()
        self.get_native()
        self.scroll_to_top()

        # Check if element is visible at top
        result = self._check_element_visibility_after_scroll(locator, waiting_element_timeout)
        if result is not None:
            return result

        # Scroll down while element is not visible
        while self.scroll_down(return_bool=True, percent=percent, speed=speed):
            result = self._check_element_visibility_after_scroll(locator, waiting_element_timeout)
            if result is not None:
                return result

        # Final scroll and check
        self.scroll_down(return_bool=True, percent=percent, speed=speed)
        return self._check_element_visibility_after_scroll(locator, waiting_element_timeout)

    def _handle_optional_scroll_errors(self, error: Exception) -> None:
        """Handle errors during optional scroll operation."""
        if isinstance(error, (NoSuchDriverException, InvalidSessionIdException, AttributeError)):
            self.handle_driver_error(error)
        elif isinstance(error, StaleElementReferenceException):
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.native = None
            self.get_native()
        elif isinstance(error, WebDriverException):
            if "instrumentation process is not running" in str(error).lower():
                self.handle_driver_error(error)
            else:
                raise
        else:
            self.logger.error(error)
            self.logger.error(type(error))
            self.logger.error(traceback.format_stack())
            self.handle_driver_error(error)
            self.scroll_to_top(percent=0.75, speed=8000)

    def scroll_to_element_optional(self, locator: Element | dict[str, Any] | tuple[str, str], max_swipes: int = 30,
                                   percent: float = 0.7, speed: int = 2000,
                                   waiting_element_timeout: int = 1) -> Element:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        locator, _ = self._prepare_optional_scroll_locator(locator)

        while time.time() - start_time < self.timeout:
            try:
                result = self._perform_optional_scroll_sequence(locator, percent, speed, waiting_element_timeout)
                if result is not None:
                    return result
            except Exception as error:
                self._handle_optional_scroll_errors(error)
                if isinstance(error, StaleElementReferenceException) or isinstance(error,
                                                                                   WebDriverException) and "instrumentation process is not running" in str(
                    error).lower():
                    continue
                if not isinstance(error, (NoSuchDriverException, InvalidSessionIdException, AttributeError)):
                    raise
            time.sleep(0.1)

        raise ShadowstepElementException(
            msg=f"Failed to scroll to element with locator: {locator}",
            stacktrace=traceback.format_stack()
        )

    def zoom(self, percent: float = 0.75, speed: int = 2500) -> Element:
        """
        Performs a pinch-open (zoom) gesture on the element.

        Args:
            percent (float): Size of the pinch as a percentage of the pinch area size (0.0 to 1.0).
            speed (int): Speed in pixels per second.

        Returns:
            Element: Self instance on success.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                self._get_element(locator=self.locator)

                self._mobile_gesture("mobile: pinchOpenGesture", {
                    "elementId": self.id,
                    "percent": percent,
                    "speed": speed
                })

                return self
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def unzoom(self, percent: float = 0.75, speed: int = 2500) -> Element:
        """
        Performs a pinch-close (unzoom) gesture on the element.

        Args:
            percent (float): Size of the pinch as a percentage of the pinch area size (0.0 to 1.0).
            speed (int): Speed in pixels per second.

        Returns:
            Element: Self instance on success.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                self._get_element(locator=self.locator)

                self._mobile_gesture("mobile: pinchCloseGesture", {
                    "elementId": self.id,
                    "percent": percent,
                    "speed": speed
                })

                return self
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def swipe_up(self, percent: float = 0.75, speed: int = 5000) -> Element:
        """Performs a swipe up gesture on the current element."""
        return self.swipe(direction="up", percent=percent, speed=speed)

    def swipe_down(self, percent: float = 0.75, speed: int = 5000) -> Element:
        """Performs a swipe down gesture on the current element."""
        return self.swipe(direction="down", percent=percent, speed=speed)

    def swipe_left(self, percent: float = 0.75, speed: int = 5000) -> Element:
        """Performs a swipe left gesture on the current element."""
        return self.swipe(direction="left", percent=percent, speed=speed)

    def swipe_right(self, percent: float = 0.75, speed: int = 5000) -> Element:
        """Performs a swipe right gesture on the current element."""
        return self.swipe(direction="right", percent=percent, speed=speed)

    def swipe(self, direction: str, percent: float = 0.75, speed: int = 5000) -> Element:
        """
        Performs a swipe gesture on the current element.

        Args:
            direction (str): Swipe direction. Acceptable values: 'up', 'down', 'left', 'right'.
            percent (float): The size of the swipe as a percentage of the swipe area size (0.0 - 1.0).
            speed (int): Speed in pixels per second (default: 5000).

        Returns:
            Element: Self instance on success.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                self._mobile_gesture("mobile: swipeGesture", {
                    "elementId": self.id,
                    "direction": direction.lower(),
                    "percent": percent,
                    "speed": speed
                })

                return self
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.timeout=} {direction=} {percent=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    @property
    def location_in_view(self) -> dict | None:
        """Gets the location of an element relative to the view.

        Returns:
            dict: Dictionary with keys 'x' and 'y', or None on failure.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                current_element = self.get_native()

                return current_element.location_in_view  # Appium WebElement property
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to get location_in_view within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def tag_name(self) -> str:
        """This element's ``tagName`` property.

        Returns:
            Optional[str]: The tag name of the element, or None if not retrievable.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                element = self.get_native()

                return element.tag_name

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve tag_name within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def attributes(self):
        return self.get_attributes()

    @property
    def text(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                element = self.get_native()

                return element.text

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve text within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def resource_id(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                return self.get_attribute("resource-id")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def class_(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                return self.get_attribute("class")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def index(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("index")

            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def package(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("package")

            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def class_name(self) -> str:  # 'class' is a reserved word, so class_name is better
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("class")

            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def bounds(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("bounds")

            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def checked(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("checked")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def checkable(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("checkable")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def enabled(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("enabled")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def focusable(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("focusable")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def focused(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("focused")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def long_clickable(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("long-clickable")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def password(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("password")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def scrollable(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("scrollable")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def selected(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("selected")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def displayed(self) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                return self.get_attribute("displayed")

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to retrieve attr within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def shadow_root(self) -> ShadowRoot:
        """NOT IMPLEMENTED!
        Returns the shadow root of the current element if available.

        Returns:
            ShadowRoot: Shadow DOM root attached to the element.

        Raises:
            ShadowstepElementException: If shadow root is not available or an error occurs.
        """
        self.logger.debug(f"{get_current_func_name()}")
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")

        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()
                element = self.get_native()
                return element.shadow_root

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except WebDriverException as error:
                self.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to retrieve shadow_root within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def location_once_scrolled_into_view(self) -> dict[str, int]:
        """NOT IMPLEMENTED
        Gets the top-left corner location of the element after scrolling it into view.

        Returns:
            dict: Dictionary with keys 'x' and 'y' indicating location on screen.

        Raises:
            ShadowstepElementException: If element could not be scrolled into view or location determined.
        """
        self.logger.debug(f"{get_current_func_name()}")
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")

        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                current_element = self.get_native()

                return current_element.location_once_scrolled_into_view

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except WebDriverException as error:
                self.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to get location_once_scrolled_into_view within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def size(self) -> dict:
        """Returns the size of the element.

        Returns:
            dict: Dictionary with keys 'width' and 'height'.

        Raises:
            ShadowstepElementException: If size cannot be determined.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                current_element = self.get_native()

                return current_element.size

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                self.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to retrieve size within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def value_of_css_property(self, property_name: str) -> str:
        """NOT IMPLEMENTED!
        Returns the value of a CSS property.

        Args:
            property_name (str): The name of the CSS property.

        Returns:
            str: The value of the CSS property.

        Raises:
            ShadowstepElementException: If value could not be retrieved within timeout.
        """
        self.logger.debug(f"{get_current_func_name()}")
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")

        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                current_element = self.get_native()

                return current_element.value_of_css_property(property_name)

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                self.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to retrieve CSS property '{property_name}' within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def location(self) -> dict:
        """NOT IMPLEMENTED
        The location of the element in the renderable canvas.

        Returns:
            dict: Dictionary with 'x' and 'y' coordinates of the element.

        Raises:
            ShadowstepElementException: If location could not be retrieved within timeout.
        """
        self.logger.debug(f"{get_current_func_name()}")
        self.logger.warning(
            f"Method {inspect.currentframe() if inspect.currentframe() else 'unknown'} is not implemented in UiAutomator2")

        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                current_element = self.get_native()

                return current_element.location

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                self.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to retrieve location within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def rect(self) -> dict:
        """A dictionary with the size and location of the element.

        Returns:
            dict: Dictionary with keys 'x', 'y', 'width', 'height'.

        Raises:
            ShadowstepElementException: If rect could not be retrieved within timeout.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                current_element = self.get_native()

                return current_element.rect

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                self.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to retrieve rect within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def aria_role(self) -> str:
        """Returns the ARIA role of the current web element.

        Returns:
            str: The ARIA role of the element, or None if not found.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                current_element = self.get_native()

                return current_element.aria_role

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                self.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to retrieve aria_role within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def accessible_name(self) -> str:
        """Returns the ARIA Level (accessible name) of the current web element.

        Returns:
            Optional[str]: Accessible name or None if not found.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                current_element = self.get_native()

                return current_element.accessible_name

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                self.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to retrieve accessible_name within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def screenshot_as_base64(self) -> str:
        """Gets the screenshot of the current element as a base64 encoded string.

        Returns:
            Optional[str]: Base64-encoded screenshot string or None if failed.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                current_element = self.get_native()

                return current_element.screenshot_as_base64

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                self.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to get screenshot_as_base64 within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def screenshot_as_png(self) -> bytes:
        """Gets the screenshot of the current element as binary data.

        Returns:
            Optional[bytes]: PNG-encoded screenshot bytes or None if failed.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                current_element = self.get_native()

                return current_element.screenshot_as_png

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                self.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to get screenshot_as_png within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def save_screenshot(self, filename: str) -> bool:
        """Saves a screenshot of the current element to a PNG image file.

        Args:
            filename (str): The full path to save the screenshot. Should end with `.png`.

        Returns:
            bool: True if successful, False otherwise.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.get_driver()

                current_element = self.get_native()

                return current_element.screenshot(filename)

            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except AttributeError as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except OSError as error:
                self.logger.error(f"IOError while saving screenshot to {filename}: {error}")
                return False
            except WebDriverException as error:
                self.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to save screenshot to {filename} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def handle_driver_error(self, error: Exception) -> None:
        self.logger.warning(f"{inspect.currentframe() if inspect.currentframe() else 'unknown'} {error}")
        self.shadowstep.reconnect()
        time.sleep(0.3)

    def _mobile_gesture(self, name: str, params: dict[str, Any] | list[Any]) -> Any:
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
        return self.driver.execute_script(name, params)

    def _ensure_session_alive(self) -> None:
        self.logger.debug(f"{get_current_func_name()}")
        try:
            self.get_driver()
        except NoSuchDriverException:
            self.logger.warning("Reconnecting driver due to session issue")
            self.shadowstep.reconnect()
        except InvalidSessionIdException:
            self.logger.warning("Reconnecting driver due to session issue")
            self.shadowstep.reconnect()

    def _get_first_child_class(self, tries: int = 3) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        for _ in range(tries):
            try:
                parent_element = self
                parent_class = parent_element.get_attribute("class")
                child_elements = parent_element.get_elements(("xpath", "//*[1]"))
                for _i, child_element in enumerate(child_elements):
                    child_class = child_element.get_attribute("class")
                    if parent_class != child_class:
                        return str(child_class)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                if "instrumentation process is not running" in str(error).lower():
                    self.handle_driver_error(error)
                    continue
                raise
        return ""  # Return empty string if no child class found

    def _build_xpath_attribute_condition(self, key: str, value: str) -> str:
        """Build XPath attribute condition based on value content."""
        if value is None or value == "null":
            return f"[@{key}]"
        if "'" in value and '"' not in value:
            return f'[@{key}="{value}"]'
        if '"' in value and "'" not in value:
            return f"[@{key}='{value}']"
        if "'" in value and '"' in value:
            parts = value.split('"')
            escaped = "concat(" + ", ".join(
                f'"{part}"' if i % 2 == 0 else "'\"'" for i, part in enumerate(parts)) + ")"
            return f"[@{key}={escaped}]"
        return f"[@{key}='{value}']"

    def build_xpath_from_attributes(self, attrs: dict[str, Any]) -> str:
        """Build XPath from element attributes."""
        xpath = "//"
        element_type = attrs.get("class")
        except_attrs = ["hint", "selection-start", "selection-end", "extras"]

        # Start XPath with element class or wildcard
        if element_type:
            xpath += element_type
        else:
            xpath += "*"

        for key, value in attrs.items():
            if key in except_attrs:
                continue
            xpath += self._build_xpath_attribute_condition(key, value)
        return xpath

    def wait(self, timeout: int = 10, poll_frequency: float = 0.5, return_bool: bool = False) -> Element:  # noqa: C901
        """Waits for the element to appear (present in DOM).

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Frequency of polling.
            return_bool (bool): If True - return bool, else return Element (self)

        Returns:
            bool: True if the element is found, False otherwise.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                resolved_locator = self.remove_null_value(self.locator)
                if not resolved_locator:
                    self.logger.error("Resolved locator is None or invalid")
                    if return_bool:
                        return False
                    return self
                WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(
                    conditions.present(resolved_locator)
                )
                if return_bool:
                    return True
                return self
            except TimeoutException:
                if return_bool:
                    return False
                return self
            except NoSuchDriverException as error:
                self.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.native = None
                self.get_native()
                continue
            except WebDriverException as error:
                self.handle_driver_error(error)
            except Exception as error:
                self.logger.error(f"{error}")
                continue
        return False

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

    def _handle_wait_visibility_errors(self, error: Exception) -> None:
        """Handle errors during wait visibility operation."""
        if isinstance(error, (NoSuchDriverException, InvalidSessionIdException, WebDriverException)):
            self.handle_driver_error(error)
        elif isinstance(error, StaleElementReferenceException):
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.native = None
            self.get_native()
        else:
            self.logger.error(f"{error}")

    def wait_visible(self, timeout: int = 10, poll_frequency: float = 0.5, return_bool: bool = False) -> Element | bool:
        """Waits until the element is visible.

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Frequency of polling.
            return_bool (bool): If True - return bool, else return Element (self)

        Returns:
            bool: True if the element becomes visible, False otherwise.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                resolved_locator = self.remove_null_value(self.locator)
                if not resolved_locator:
                    self.logger.error("Resolved locator is None or invalid")
                    return False if return_bool else self

                if self._wait_for_visibility_with_locator(resolved_locator, timeout, poll_frequency):
                    return True if return_bool else self

            except Exception as error:
                self._handle_wait_visibility_errors(error)
                if isinstance(error, StaleElementReferenceException):
                    continue

        return False if return_bool else self

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

    def _handle_wait_clickability_errors(self, error: Exception) -> None:
        """Handle errors during wait clickability operation."""
        if isinstance(error, (NoSuchDriverException, InvalidSessionIdException, WebDriverException)):
            self.handle_driver_error(error)
        elif isinstance(error, StaleElementReferenceException):
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.native = None
            self.get_native()
        else:
            self.logger.error(f"{error}")

    def wait_clickable(self, timeout: int = 10, poll_frequency: float = 0.5,
                       return_bool: bool = False) -> Element | bool:
        """Waits until the element is clickable.

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Frequency of polling.
            return_bool (bool): If True - return bool, else return Element (self)

        Returns:
            bool: True if the element becomes clickable, False otherwise.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                resolved_locator = self.remove_null_value(self.locator)
                if not resolved_locator:
                    self.logger.error("Resolved locator is None or invalid")
                    return False if return_bool else self

                if self._wait_for_clickability_with_locator(resolved_locator, timeout, poll_frequency):
                    return True if return_bool else self

            except Exception as error:
                self._handle_wait_clickability_errors(error)
                if isinstance(error, StaleElementReferenceException):
                    continue

        return False if return_bool else self

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

    def _handle_wait_for_not_errors(self, error: Exception) -> None:
        """Handle errors during wait for not operation."""
        if isinstance(error, (NoSuchDriverException, InvalidSessionIdException, WebDriverException)):
            self.handle_driver_error(error)
        elif isinstance(error, StaleElementReferenceException):
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.native = None
            self.get_native()
        else:
            self.logger.error(f"{error}")

    def wait_for_not(self, timeout: int = 10, poll_frequency: float = 0.5, return_bool: bool = False) -> Element | bool:
        """Waits until the element is no longer present in the DOM.

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Frequency of polling.
            return_bool (bool): If True - return bool, else return Element (self)

        Returns:
            bool: True if the element disappears, False otherwise.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                resolved_locator = self.remove_null_value(self.locator)
                if not resolved_locator:
                    return False if return_bool else self

                if self._wait_for_not_present_with_locator(resolved_locator, timeout, poll_frequency):
                    return True if return_bool else self

            except Exception as error:
                self._handle_wait_for_not_errors(error)
                if isinstance(error, StaleElementReferenceException):
                    continue

        return False

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
            self.handle_driver_error(error)
        elif isinstance(error, StaleElementReferenceException):
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.native = None
            self.get_native()
        else:
            self.logger.error(f"{error}")

    def wait_for_not_visible(self, timeout: int = 10, poll_frequency: float = 0.5,
                             return_bool: bool = False) -> Element | bool:
        """Waits until the element becomes invisible.

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Polling frequency.
            return_bool (bool): If True - return bool, else return Element (self)

        Returns:
            bool: True if the element becomes invisible, False otherwise.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                resolved_locator = self.remove_null_value(self.locator)
                if not resolved_locator:
                    return False if return_bool else self

                if self._wait_for_not_visible_with_locator(resolved_locator, timeout, poll_frequency):
                    return True if return_bool else self

            except Exception as error:
                self._handle_wait_for_not_visible_errors(error)
                if isinstance(error, StaleElementReferenceException):
                    continue

        return False if return_bool else self

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
            self.handle_driver_error(error)
        elif isinstance(error, StaleElementReferenceException):
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.native = None
            self.get_native()
        else:
            self.logger.error(f"{error}")

    def wait_for_not_clickable(self, timeout: int = 10, poll_frequency: float = 0.5,
                               return_bool: bool = False) -> Element | bool:
        """Waits until the element becomes not clickable.

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Polling frequency.
            return_bool (bool): If True - return bool, else return Element (self)

        Returns:
            bool: True if the element becomes not clickable, False otherwise.
        """
        self.logger.debug(f"{get_current_func_name()}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                resolved_locator = self.remove_null_value(self.locator)
                if not resolved_locator:
                    self.logger.error("Resolved locator is None or invalid")
                    return False if return_bool else self

                if self._wait_for_not_clickable_with_locator(resolved_locator, timeout, poll_frequency):
                    return True if return_bool else self

            except Exception as error:
                self._handle_wait_for_not_clickable_errors(error)
                if isinstance(error, StaleElementReferenceException):
                    continue

        return False if return_bool else self

    @property
    def should(self) -> Should:
        """Provides DSL-like assertions: element.should.have.text(...), etc."""
        from shadowstep.element.should import (
            Should,  # import inside method to avoid circular dependency
        )
        return Should(self)

    def get_native(self) -> WebElement:
        """
        Returns either the provided native element or resolves via locator.
        """
        if self.native:
            return self.native

        # Convert Element to its locator if needed
        locator = self.locator
        if isinstance(locator, Element):
            locator = locator.locator

        return self._get_element(
            locator=locator,
            timeout=self.timeout,
            poll_frequency=self.poll_frequency,
            ignored_exceptions=self.ignored_exceptions
        )

    def _resolve_xpath_for_attributes(self) -> str | None:
        """Resolve XPath expression from locator for attributes fetching."""
        try:
            xpath_expr = self.converter.to_xpath(self.locator)[1]
            if not xpath_expr:
                self.logger.error(f"Failed to resolve XPath from locator: {self.locator}")
                return None
            self.logger.debug(f"Resolved XPath: {xpath_expr}")
            return xpath_expr
        except Exception as e:
            self.logger.error(f"Exception in to_xpath: {e}")
            return None

    def _check_element_bounds(self, element_location: dict, element_size: dict, screen_width: int,
                              screen_height: int) -> bool:
        """Check if element is within screen bounds."""
        return not (
                element_location["y"] + element_size["height"] > screen_height or
                element_location["x"] + element_size["width"] > screen_width or
                element_location["y"] < 0 or
                element_location["x"] < 0
        )

    def _check_element_visibility(self) -> bool | None:
        """Check if element is visible, handling exceptions."""
        try:
            screen_size = self.shadowstep.terminal.get_screen_resolution()
            screen_width = screen_size[0]
            screen_height = screen_size[1]
            current_element = self.get_native()

            if current_element is None:
                return False
            if current_element.get_attribute("displayed") != "true":
                return False

            element_location = current_element.location
            element_size = current_element.size
            return self._check_element_bounds(element_location, element_size, screen_width, screen_height)

        except NoSuchElementException:
            return False
        except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
            self.handle_driver_error(error)
            return None
        except StaleElementReferenceException as error:
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.native = None
            self.get_native()
            return None
        except WebDriverException as error:
            if "instrumentation process is not running" in str(error).lower():
                self.handle_driver_error(error)
                return None
            raise

    def _create_touch_actions(self, x1: int, y1: int) -> ActionChains:
        """Create touch action chain starting at given coordinates."""
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(x1, y1)
        actions.w3c_actions.pointer_action.pointer_down()
        return actions

    def _execute_tap_and_move_to_coordinates(self, actions: ActionChains, x: int, y: int) -> Element:
        """Execute tap and move to specific coordinates."""
        actions.w3c_actions.pointer_action.move_to_location(x, y)
        actions.w3c_actions.pointer_action.pointer_up()
        actions.perform()
        return self

    def _execute_tap_and_move_to_element(self, actions: ActionChains,
                                         locator: tuple[str, str] | WebElement | dict[str, Any] | str) -> Element:
        """Execute tap and move to another element."""
        target_element = self._get_element(locator=locator)
        x, y = self.get_center(target_element)
        return self._execute_tap_and_move_to_coordinates(actions, x, y)

    def _execute_tap_and_move_by_direction(self, actions: ActionChains, x1: int, y1: int, direction: int,
                                           distance: int) -> Element:
        """Execute tap and move by direction vector."""
        width, height = self.shadowstep.terminal.get_screen_resolution()
        x2, y2 = find_coordinates_by_vector(width=width, height=height, direction=direction, distance=distance,
                                            start_x=x1, start_y=y1)
        return self._execute_tap_and_move_to_coordinates(actions, x2, y2)

    def _perform_tap_and_move_action(self,
                                     locator: tuple[str, str] | WebElement | Element | dict[str, Any] | str | None,
                                     x: int | None, y: int | None, direction: int | None,
                                     distance: int | None) -> Element | None:
        """Perform tap and move action with error handling."""
        try:
            self.get_driver()
            if isinstance(locator, Element):
                locator = locator.locator

            x1, y1 = self.get_center()
            actions = self._create_touch_actions(x1, y1)

            # Direct coordinate specification
            if x is not None and y is not None:
                return self._execute_tap_and_move_to_coordinates(actions, x, y)

            # Move to another element
            if locator is not None:
                return self._execute_tap_and_move_to_element(actions, locator)

            # Move by direction vector
            if direction is not None and distance is not None:
                return self._execute_tap_and_move_by_direction(actions, x1, y1, direction, distance)

            return None
        except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
            self.handle_driver_error(error)
            return None
        except StaleElementReferenceException as error:
            self.logger.debug(error)
            self.logger.warning("StaleElementReferenceException\nRe-acquire element")
            self.native = None
            self.get_native()
            return None
        except WebDriverException as error:
            if "instrumentation process is not running" in str(error).lower():
                self.handle_driver_error(error)
                return None
            raise


"""
Предлагаемое логическое разделение на сегменты
Основываясь на анализе кода, я предлагаю разделить модуль на следующие логические сегменты:
1. Element Core (element_core.py)
Основной класс Element с базовой функциональностью
Инициализация и базовые методы
Основные свойства и атрибуты
Логирование и обработка ошибок

2. Element DOM navigation (dom.py)
Методы навигации по DOM-дереву:
get_element(),
get_elements()
get_parent(),
get_parents()
get_sibling(),
get_siblings(),
get_cousin(),
get_cousins(),

3. Element Actions (actions.py)
Методы взаимодействия с элементами:
send_keys(),
clear()
set_value(),
submit()

4. Element Gestures (gestures.py)
Жесты и движения:
click(),
click_double()
tap(),
tap_and_move()
swipe(),
swipe_up(),
swipe_down(),
swipe_left(),
swipe_right()
scroll(),
scroll_up(),
scroll_down(),
scroll_left(),
scroll_right()
fling(),
fling_up(),
fling_down(),
fling_left(),
fling_right()
drag(),
zoom(),
unzoom()
scroll_to_element(),
scroll_to_bottom(),
scroll_to_top()

5. Element Properties (element_properties.py)
Свойства и атрибуты элементов:
text,
tag_name,
size,
location, rect
resource_id,
class_,
index,
package,
bounds
checked,
checkable,
enabled,
focusable,
focused
long_clickable,
password,
scrollable,
selected,
displayed
aria_role,
accessible_name

6. Element Coordinates (element_coordinates.py)
Работа с координатами:
get_coordinates(),
get_center()
location_in_view,
location_once_scrolled_into_view

7. Element Screenshots (element_screenshots.py)
Снимки экрана:
screenshot_as_base64,
screenshot_as_png
save_screenshot()

8. Element Waiting (element_waiting.py)
Методы ожидания:
wait(),
wait_visible(),
wait_clickable()
wait_for_not(),
wait_for_not_visible(),
wait_for_not_clickable()

9. Element Utilities (element_utilities.py)
Вспомогательные методы:
_handle_driver_error(),
_mobile_gesture()
_ensure_session_alive(),
_get_xpath(),
_get_xpath_by_driver()
_build_element_xpath(),
_contains_to_xpath()
_get_first_child_class(),
_get_native()

Архитектура композиции
После разделения основной класс Element будет использовать композицию:
class Element(ElementBase):
    def __init__(self, ...):
        super().__init__(...)
        self.dom = ElementDOM(self)
        self.actions = ElementActions(self)
        self.gestures = ElementGestures(self)
        self.properties = ElementProperties(self)
        self.coordinates = ElementCoordinates(self)
        self.screenshots = ElementScreenshots(self)
        self.waiting = ElementWaiting(self)
        self.utilities = ElementUtilities(self)
"""
