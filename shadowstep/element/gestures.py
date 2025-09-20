# shadowstep/element/gestures.py
from __future__ import annotations

import inspect
import logging
import time
import traceback
from typing import TYPE_CHECKING, Any

from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from shadowstep.decorators.decorators import log_debug
from shadowstep.element.utilities import ElementUtilities
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.utils.utils import find_coordinates_by_vector, get_current_func_name

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.locator import LocatorConverter, UiSelector
    from shadowstep.shadowstep import Shadowstep


class ElementGestures:
    def __init__(self, element: Element):
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    @log_debug()
    def tap(self, duration: int | None = None) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                x, y = self.element.get_center()
                if x is None or y is None:
                    continue
                self.element.driver.tap(positions=[(x, y)], duration=duration)
                return self.element
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
                continue
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
                continue
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
                continue
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}\n{duration}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}\n{duration}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def tap_and_move(
            self,
            locator: tuple[str, str] | dict[str, Any] | Element | UiSelector | None = None,
            x: int | None = None,
            y: int | None = None,
            direction: int | None = None,
            distance: int | None = None,
    ) -> Element:
        start_time = time.time()

        while time.time() - start_time < self.element.timeout:
            result = self._perform_tap_and_move_action(locator, x, y, direction, distance)
            if result is not None:
                return result
            time.sleep(0.1)

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}\n{locator=}\n{x=}\n{y=}\n{direction}\n{distance}\n",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def click(self, duration: int | None = None) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                self.element._get_web_element(locator=self.element.locator)
                if duration is None:
                    self._mobile_gesture("mobile: clickGesture",
                                         {"elementId": self.element.id})
                else:
                    self._mobile_gesture("mobile: longClickGesture",
                                         {"elementId": self.element.id, "duration": duration})
                return self.element
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}\n{duration}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}\n{duration}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def click_double(self) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                self.element._get_web_element(locator=self.element.locator)
                self._mobile_gesture("mobile: doubleClickGesture",
                                     {"elementId": self.element.id})
                return self.element
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def drag(self, end_x: int, end_y: int, speed: int = 2500) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                self.element._get_web_element(locator=self.element.locator)
                self._mobile_gesture("mobile: dragGesture",
                                     {"elementId": self.element.id,
                                      "endX": end_x,
                                      "endY": end_y,
                                      "speed": speed})
                return self.element
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def fling(self, speed: int, direction: str) -> Element:
        """
        direction: Direction of the fling. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
        speed: The speed at which to perform this gesture in pixels per second. The value must be greater than the minimum fling velocity for the given view (50 by default). The default value is 7500 * displayDensity
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-flinggesture
        """
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                self.element._get_web_element(locator=self.element.locator)
                self._mobile_gesture("mobile: flingGesture",
                                     {"elementId": self.element.id,
                                      "direction": direction,
                                      "speed": speed})
                return self.element
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def scroll(self, direction: str, percent: float, speed: int, return_bool: bool) -> Element:
        """
        direction: Scrolling direction. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
        percent: The size of the scroll as a percentage of the scrolling area size. Valid values must be float numbers greater than zero, where 1.0 is 100%. Mandatory value.
        speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 5000 * displayDensity
        return_bool: if true return bool else return self
        """
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollgesture
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                self.element._get_web_element(locator=self.element.locator)
                can_scroll = self._mobile_gesture("mobile: scrollGesture",
                                                  {"elementId": self.element.id,
                                                   "percent": percent,
                                                   "direction": direction,
                                                   "speed": speed})
                if return_bool:
                    return can_scroll
                return self.element
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def scroll_to_bottom(self, percent: float = 0.7, speed: int = 8000) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                if not self.element.scroll_down(percent=percent, speed=speed, return_bool=True):
                    return self.element
                self.element.scroll_down(percent=percent, speed=speed, return_bool=True)
            except (
                    NoSuchDriverException, InvalidSessionIdException, AttributeError
            ) as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to scroll to bottom within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to scroll to bottom within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def scroll_to_top(self, percent: float = 0.7, speed: int = 8000) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                if not self.element.scroll_up(percent, speed, return_bool=True):
                    return self.element
                self.element.scroll_up(percent=percent, speed=speed, return_bool=True)
            except (
                    NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to scroll to top within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to scroll to top within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def scroll_to_element(self,
                          locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                          max_swipes: int = 30) -> Element:
        start_time = time.time()

        selector = self.converter.to_uiselector(locator)

        while time.time() - start_time < self.element.timeout:
            try:
                self._execute_scroll_script(selector, max_swipes)
                return self.shadowstep.get_element(locator)
            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.element.utilities.handle_driver_error(error)
                continue
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to scroll to element with locator: {locator}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to scroll to element with locator: {locator}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def zoom(self, percent: float = 0.75, speed: int = 2500) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                self.element._get_web_element(locator=self.element.locator)
                self._mobile_gesture("mobile: pinchOpenGesture", {
                    "elementId": self.element.id,
                    "percent": percent,
                    "speed": speed
                })
                return self.element
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def unzoom(self, percent: float = 0.75, speed: int = 2500) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                self.element._get_web_element(locator=self.element.locator)
                self._mobile_gesture("mobile: pinchCloseGesture", {
                    "elementId": self.element.id,
                    "percent": percent,
                    "speed": speed
                })
                return self.element
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def swipe(self, direction: str, percent: float = 0.75, speed: int = 5000) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                self.element._get_web_element(locator=self.element.locator)
                self._mobile_gesture("mobile: swipeGesture", {
                    "elementId": self.element.id,
                    "direction": direction.lower(),
                    "percent": percent,
                    "speed": speed
                })
                return self.element
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=} {direction=} {percent=}",
                    stacktrace=traceback.format_stack()
                ) from error
        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=} {direction=} {percent=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def _execute_scroll_script(self, selector: str, max_swipes: int) -> None:
        """Execute mobile scroll script."""
        # https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-scroll
        self.element.get_driver()
        self.element._get_web_element(locator=self.element.locator)
        self.element.driver.execute_script("mobile: scroll", {
            # "elementId": self.element.id,  # some issue with this - "java.lang.IllegalArgumentException: The given origin element must be a valid scrollable UiObject"
            "strategy": "-android uiautomator",
            "selector": selector,
            "maxSwipes": max_swipes
        })

    @log_debug()
    def _perform_tap_and_move_action(self,
                                     locator: tuple[str, str] | dict[str, Any] | Element | UiSelector | None = None,
                                     x: int | None = None,
                                     y: int | None = None,
                                     direction: int | None = None,
                                     distance: int | None = None) -> Element | None:
        """Perform tap and move action with error handling."""
        from shadowstep.element.element import Element
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                if isinstance(locator, Element):
                    locator = locator.locator

                x1, y1 = self.element.get_center()
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

                raise ShadowstepElementException(
                    msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=} {direction=}",
                    stacktrace=traceback.format_stack()
                )
            except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                self.element.utilities.handle_driver_error(error)
                continue
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.utilities.handle_driver_error(error)
                    continue
        raise ShadowstepElementException(
            msg=f"Failed to {get_current_func_name()} within {self.element.timeout=} {direction=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def _create_touch_actions(self, x1: int, y1: int) -> ActionChains:
        """Create touch action chain starting at given coordinates."""
        actions = ActionChains(self.element.driver)
        actions.w3c_actions = ActionBuilder(self.element.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(x1, y1)
        actions.w3c_actions.pointer_action.pointer_down()
        return actions

    @log_debug()
    def _execute_tap_and_move_to_coordinates(self, actions: ActionChains, x: int, y: int) -> Element:
        """Execute tap and move to specific coordinates."""
        actions.w3c_actions.pointer_action.move_to_location(x, y)
        actions.w3c_actions.pointer_action.pointer_up()
        actions.perform()
        return self.element

    @log_debug()
    def _execute_tap_and_move_to_element(self, actions: ActionChains,
                                         locator: tuple[str, str] | dict[str, Any] | Element | UiSelector) -> Element:
        """Execute tap and move to another element."""
        target_element = self.element._get_web_element(locator=locator)
        x, y = self.element.get_center(target_element)
        return self._execute_tap_and_move_to_coordinates(actions, x, y)

    @log_debug()
    def _execute_tap_and_move_by_direction(self, actions: ActionChains, x1: int, y1: int, direction: int,
                                           distance: int) -> Element:
        """Execute tap and move by direction vector."""
        width, height = self.shadowstep.terminal.get_screen_resolution()
        x2, y2 = find_coordinates_by_vector(width=width, height=height, direction=direction, distance=distance,
                                            start_x=x1, start_y=y1)
        return self._execute_tap_and_move_to_coordinates(actions, x2, y2)

    def _mobile_gesture(self, name: str, params: dict[str, Any] | list[Any]) -> Any:
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
        return self.element.driver.execute_script(name, params)
