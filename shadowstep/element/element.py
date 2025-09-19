# shadowstep/element/element.py
from __future__ import annotations

import logging
import time
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
from shadowstep.locator import UiSelector
from shadowstep.utils.utils import get_current_func_name

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
    DOM
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
                    locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                    timeout: float = 30,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: WaitExcTypes | None = None) -> Element:
        return self.dom.get_sibling(locator, timeout, poll_frequency, ignored_exceptions)

    def get_siblings(self,
                     locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                     timeout: float = 30.0,
                     poll_frequency: float = 0.5,
                     ignored_exceptions: WaitExcTypes | None = None) -> list[Element]:
        return self.dom.get_siblings(locator, timeout, poll_frequency, ignored_exceptions)

    def get_cousin(
            self,
            cousin_locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
            depth_to_parent: int = 1,
            timeout: float = 30.0,
            poll_frequency: float = 0.5,
            ignored_exceptions: WaitExcTypes | None = None
    ) -> Element:
        return self.dom.get_cousin(cousin_locator, depth_to_parent, timeout, poll_frequency, ignored_exceptions)

    def get_cousins(
            self,
            cousin_locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
            depth_to_parent: int = 1,
            timeout: float = 30.0,
            poll_frequency: float = 0.5,
            ignored_exceptions: WaitExcTypes | None = None
    ) -> list[Element]:
        return self.dom.get_cousins(cousin_locator, depth_to_parent, timeout, poll_frequency, ignored_exceptions)

    """
    Actions
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
            f"Method {get_current_func_name()} is not implemented in UiAutomator2")
        return self.actions.set_value(value)

    # Override
    def submit(self) -> Element:
        self.logger.warning(
            f"Method {get_current_func_name()} is not implemented in UiAutomator2")
        return self.actions.submit()

    """
    Gestures
    """

    def tap(self, duration: int | None = None) -> Element:
        return self.gestures.tap(duration)

    def tap_and_move(
            self,
            locator: tuple[str, str] | dict[str, Any] | Element | UiSelector | None = None,
            x: int | None = None,
            y: int | None = None,
            direction: int | None = None,
            distance: int | None = None,
    ) -> Element:
        return self.gestures.tap_and_move(locator, x, y, direction, distance)

    def click(self, duration: int | None = None) -> Element:
        return self.gestures.click(duration)

    def click_double(self) -> Element:
        return self.gestures.click_double()

    def drag(self, end_x: int, end_y: int, speed: int = 2500) -> Element:
        return self.gestures.drag(end_x, end_y, speed)

    def fling_up(self, speed: int = 2500) -> Element:
        return self.fling(speed=speed, direction="up")

    def fling_down(self, speed: int = 2500) -> Element:
        return self.fling(speed=speed, direction="down")

    def fling_left(self, speed: int = 2500) -> Element:
        return self.fling(speed=speed, direction="left")

    def fling_right(self, speed: int = 2500) -> Element:
        return self.fling(speed=speed, direction="right")

    def fling(self, speed: int, direction: str) -> Element:
        return self.gestures.fling(speed, direction)

    def scroll_down(self, percent: float = 0.7, speed: int = 2000, return_bool: bool = False) -> Element:
        return self.scroll(direction="down", percent=percent, speed=speed, return_bool=return_bool)

    def scroll_up(self, percent: float = 0.7, speed: int = 2000, return_bool: bool = False) -> Element:
        return self.scroll(direction="up", percent=percent, speed=speed, return_bool=return_bool)

    def scroll_left(self, percent: float = 0.7, speed: int = 2000, return_bool: bool = False) -> Element:
        return self.scroll(direction="left", percent=percent, speed=speed, return_bool=return_bool)

    def scroll_right(self, percent: float = 0.7, speed: int = 2000, return_bool: bool = False) -> Element:
        return self.scroll(direction="right", percent=percent, speed=speed, return_bool=return_bool)

    def scroll(self, direction: str, percent: float, speed: int, return_bool: bool) -> Element:
        return self.gestures.scroll(direction, percent, speed, return_bool)

    def scroll_to_bottom(self, percent: float = 0.7, speed: int = 8000) -> Element:
        return self.gestures.scroll_to_bottom(percent, speed)

    def scroll_to_top(self, percent: float = 0.7, speed: int = 8000) -> Element:
        return self.gestures.scroll_to_top(percent, speed)

    def scroll_to_element(self,
                          locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                          max_swipes: int = 30) -> Element:
        return self.gestures.scroll_to_element(locator, max_swipes)

    def zoom(self, percent: float = 0.75, speed: int = 2500) -> Element:
        return self.gestures.zoom(percent, speed)

    def unzoom(self, percent: float = 0.75, speed: int = 2500) -> Element:
        return self.gestures.unzoom(percent, speed)

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
        return self.gestures.swipe(direction, percent, speed)

    """
    Properties
    """

    # Override
    def get_attribute(self, name: str) -> str:  # type: ignore[override]
        return self.properties.get_attribute(name)

    def get_attributes(self) -> dict[str, Any]:
        """Fetch all XML attributes of the element by matching locator against page source.

        Returns:
            Optional[dict[str, Any]]: Dictionary of all attributes, or None if not found.
        """
        return self.properties.get_attributes()

    def get_property(self, name: str) -> Any:
        self.logger.warning(
            f"Method {get_current_func_name()} is not implemented in UiAutomator2")
        return self.properties.get_property(name)

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
        return self.properties.get_dom_attribute(name)

    # Override
    def is_displayed(self) -> bool:
        """Whether the element is visible to a user.

        Returns:
            bool: True if the element is displayed on screen and visible to the user.
        """
        return self.properties.is_displayed()

    def is_visible(self) -> bool:
        return self.properties.is_visible()

    def is_selected(self) -> bool:
        """Returns whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.

        Returns:
            bool: True if the element is selected.
        """
        return self.properties.is_selected()

    def is_enabled(self) -> bool:
        """Returns whether the element is enabled.

        Returns:
            bool: True if the element is enabled.
        """
        return self.properties.is_enabled()

    def is_contains(self,
                    locator: tuple | dict[str, Any] | Element | UiSelector,
                    ) -> bool:
        return self.properties.is_contains(locator)

    @property
    def tag_name(self) -> str:
        """This element's ``tagName`` property.

        Returns:
            Optional[str]: The tag name of the element, or None if not retrievable.
        """
        return self.properties.tag_name()

    @property
    def attributes(self):
        return self.get_attributes()

    @property
    def text(self) -> str:
        return self.properties.text()

    @property
    def resource_id(self) -> str:
        return self.properties.resource_id()

    @property
    def class_(self) -> str:  # 'class' is a reserved word, so class_name is better
        return self.properties.class_()

    @property
    def class_name(self) -> str:  # 'class' is a reserved word, so class_name is better
        return self.properties.class_name()

    @property
    def index(self) -> str:
        self.logger.warning(
            f"Method {get_current_func_name()} 'index' attribute is unknown for the element")
        return self.properties.index()

    @property
    def package(self) -> str:
        return self.properties.package()

    @property
    def bounds(self) -> str:
        return self.properties.bounds()

    @property
    def checked(self) -> str:
        return self.properties.checked()

    @property
    def checkable(self) -> str:
        return self.properties.checkable()

    @property
    def enabled(self) -> str:
        return self.properties.enabled()

    @property
    def focusable(self) -> str:
        return self.properties.focusable()

    @property
    def focused(self) -> str:
        return self.properties.focused()

    @property
    def long_clickable(self) -> str:
        return self.properties.long_clickable()

    @property
    def password(self) -> str:
        return self.properties.password()

    @property
    def scrollable(self) -> str:
        return self.properties.scrollable()

    @property
    def selected(self) -> str:
        return self.properties.selected()

    @property
    def displayed(self) -> str:
        return self.properties.displayed()

    @property
    def shadow_root(self) -> ShadowRoot:
        self.logger.warning(
            f"Method {get_current_func_name()} is not implemented in UiAutomator2")
        return self.properties.shadow_root()

    @property
    def size(self) -> dict:
        """Returns the size of the element.

        Returns:
            dict: Dictionary with keys 'width' and 'height'.

        Raises:
            ShadowstepElementException: If size cannot be determined.
        """
        return self.properties.size()

    def value_of_css_property(self, property_name: str) -> str:
        self.logger.warning(
            f"Method {get_current_func_name()} is not implemented in UiAutomator2")
        return self.properties.value_of_css_property(property_name)

    @property
    def location(self) -> dict:
        self.logger.warning(
            f"Method {get_current_func_name()} is not implemented in UiAutomator2")
        return self.properties.location()

    @property
    def rect(self) -> dict:
        """A dictionary with the size and location of the element.

        Returns:
            dict: Dictionary with keys 'x', 'y', 'width', 'height'.

        Raises:
            ShadowstepElementException: If rect could not be retrieved within timeout.
        """
        return self.properties.rect()

    @property
    def aria_role(self) -> str:
        """Returns the ARIA role of the current web element.

        Returns:
            str: The ARIA role of the element, or None if not found.
        """
        return self.properties.aria_role()

    @property
    def accessible_name(self) -> str:
        """Returns the ARIA Level (accessible name) of the current web element.

        Returns:
            Optional[str]: Accessible name or None if not found.
        """
        return self.properties.accessible_name()

    """
    Coordinates
    """

    def get_coordinates(self, element: WebElement | None = None) -> tuple[int, int, int, int]:
        return self.coordinates.get_coordinates(element)

    def get_center(self, element: WebElement | None = None) -> tuple[int, int]:
        return self.coordinates.get_center(element)

    # Override
    @property
    def location_in_view(self) -> dict[str, int]:
        return self.coordinates.location_in_view()

    @property
    def location_once_scrolled_into_view(self) -> dict[str, int]:
        self.logger.warning(
            f"Method {get_current_func_name()} is not implemented in UiAutomator2")
        return self.coordinates.location_once_scrolled_into_view()

    """
    Screenshots
    """

    @property
    def screenshot_as_base64(self) -> str:
        """Gets the screenshot of the current element as a base64 encoded string.

        Returns:
            Optional[str]: Base64-encoded screenshot string or None if failed.
        """
        return self.screenshots.screenshot_as_base64()

    @property
    def screenshot_as_png(self) -> bytes:
        """Gets the screenshot of the current element as binary data.

        Returns:
            Optional[bytes]: PNG-encoded screenshot bytes or None if failed.
        """
        return self.screenshots.screenshot_as_png()

    def save_screenshot(self, filename: str) -> bool:
        """Saves a screenshot of the current element to a PNG image file.

        Args:
            filename (str): The full path to save the screenshot. Should end with `.png`.

        Returns:
            bool: True if successful, False otherwise.
        """
        return self.screenshots.save_screenshot(filename)

    """
    
    """

    def handle_driver_error(self, error: Exception) -> None:
        self.logger.warning(f"{get_current_func_name()} {error}")
        self.shadowstep.reconnect()
        time.sleep(0.3)

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
                resolved_locator = self.converter.to_xpath(self.remove_null_value(self.locator))
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
                resolved_locator = self.converter.to_xpath(self.remove_null_value(self.locator))
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
                resolved_locator = self.converter.to_xpath(self.remove_null_value(self.locator))
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
                resolved_locator = self.converter.to_xpath(self.remove_null_value(self.locator))
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
                resolved_locator = self.converter.to_xpath(self.remove_null_value(self.locator))
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
                resolved_locator = self.converter.to_xpath(self.remove_null_value(self.locator))
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
        return self._get_web_element(
            locator=locator,
            timeout=self.timeout,
            poll_frequency=self.poll_frequency,
            ignored_exceptions=self.ignored_exceptions
        )

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
            err_msg = str(error).lower()
            if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                self.handle_driver_error(error)
                return None
            raise

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
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.handle_driver_error(error)
                    continue
                raise
        return ""  # Return empty string if no child class found


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
