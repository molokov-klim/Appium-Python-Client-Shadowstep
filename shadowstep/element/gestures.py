"""Element gestures module for Shadowstep framework.

This module provides gesture functionality for elements,
including tap, click, drag, swipe, and other mobile gestures.
"""

from __future__ import annotations

import inspect
import logging
import time
import traceback
from typing import TYPE_CHECKING, Any, cast

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from shadowstep.decorators.decorators import log_debug
from shadowstep.enums import GestureStrategy
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.ui_automator.mobile_commands import MobileCommands
from shadowstep.utils.utils import find_coordinates_by_vector, get_current_func_name
from shadowstep.w3c_actions.w3c_actions import W3CActions

if TYPE_CHECKING:
    from appium.webdriver.webelement import WebElement

    from shadowstep.element.element import Element
    from shadowstep.element.utilities import ElementUtilities
    from shadowstep.locator import LocatorConverter, UiSelector
    from shadowstep.shadowstep import Shadowstep


class ElementGestures:
    """Element gestures handler for Shadowstep framework."""

    def __init__(self, element: Element) -> None:
        """Initialize ElementGestures.

        Args:
            element: The element to perform gestures on.

        """
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = self.element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities
        self.mobile_commands = MobileCommands()
        self.w3c_actions = W3CActions()

    @log_debug()
    def tap(self, duration: int | None = None) -> Element:
        """Tap the element.

        Args:
            duration: Duration of the tap in milliseconds.

        Returns:
            The element for method chaining.

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        self.element.get_driver()
        x, y = self.element.get_center()
        self.element.driver.tap(positions=[(x, y)], duration=duration)
        return self.element

    @log_debug()
    def tap_and_move(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector | None = None,
        x: int | None = None,
        y: int | None = None,
        direction: int | None = None,
        distance: int | None = None,
    ) -> Element:
        """Tap and move to a location or element.

        Args:
            locator: Target element locator.
            x: Target x coordinate.
            y: Target y coordinate.
            direction: Direction vector for movement.
            distance: Distance to move.

        Returns:
            The element for method chaining.

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        result = self._perform_tap_and_move_action(locator, x, y, direction, distance)
        if result is not None:
            return result
        return self.element

    @log_debug()
    def click(
        self,
        duration: int | None = None,
        strategy: GestureStrategy = GestureStrategy.AUTO,
    ) -> Element:
        """Click the element.

        Args:
            duration: Duration of the click in milliseconds.
            strategy: Gesture execution strategy (W3C_ACTIONS, MOBILE_COMMANDS, AUTO).

        Returns:
            The element for method chaining.

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        self.element.get_driver()
        native_element = self.element._get_web_element(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
            locator=self.element.locator,
        )  # type: ignore[reportPrivateUsage]
        method_map = {
            GestureStrategy.W3C_ACTIONS: self._click_w3c_commands,
            GestureStrategy.MOBILE_COMMANDS: self._click_mobile_commands,
            GestureStrategy.AUTO: self._click_mobile_commands,
        }
        return method_map[strategy](native_element, duration)

    @log_debug()
    def _click_w3c_commands(
        self,
        native_element: WebElement,
        duration: int | None = None,
    ) -> Element:
        self.w3c_actions.click(native_element, duration=duration)
        return self.element

    @log_debug()
    def _click_mobile_commands(
        self,
        native_element: WebElement,
        duration: int | None = None,
    ) -> Element:
        if duration is None:
            self.mobile_commands.click_gesture({"elementId": self.element.id})
        else:
            self.mobile_commands.long_click_gesture(
                {"elementId": native_element.id, "duration": duration},
            )
        return self.element

    @log_debug()
    def double_click(self, strategy: GestureStrategy = GestureStrategy.AUTO) -> Element:
        """Double-click the element.

        Returns:
            The element for method chaining.

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        self.element.get_driver()
        native_element = self.element._get_web_element(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
            locator=self.element.locator,
        )  # type: ignore[reportPrivateUsage]
        method_map = {
            GestureStrategy.W3C_ACTIONS: self._double_click_w3c_commands,
            GestureStrategy.MOBILE_COMMANDS: self._double_click_mobile_commands,
            GestureStrategy.AUTO: self._double_click_w3c_commands,
        }
        return method_map[strategy](native_element)

    @log_debug()
    def _double_click_mobile_commands(self, native_element: WebElement) -> Element:
        self.mobile_commands.double_click_gesture({"elementId": native_element.id})
        return self.element

    @log_debug()
    def _double_click_w3c_commands(self, native_element: WebElement) -> Element:
        self.w3c_actions.double_click(native_element)
        return self.element

    @log_debug()
    def drag(
        self,
        end_x: int,
        end_y: int,
        speed: int = 2500,
        strategy: GestureStrategy = GestureStrategy.AUTO,
    ) -> Element:
        """Drag the element to specified coordinates.

        Args:
            end_x: Target x coordinate.
            end_y: Target y coordinate.
            speed: Speed of the drag gesture.
            strategy: Gesture execution strategy (W3C_ACTIONS, MOBILE_COMMANDS, AUTO).

        Returns:
            The element for method chaining.

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        self.element.get_driver()
        native_element = self.element._get_web_element(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
            locator=self.element.locator,
        )  # type: ignore[reportPrivateUsage]
        method_map = {
            GestureStrategy.W3C_ACTIONS: self._drag_w3c_actions,
            GestureStrategy.MOBILE_COMMANDS: self._drag_mobile_commands,
            GestureStrategy.AUTO: self._drag_w3c_actions,
        }
        return method_map[strategy](native_element, end_x, end_y, speed)

    @log_debug()
    def _drag_mobile_commands(
        self,
        native_element: WebElement,
        end_x: int,
        end_y: int,
        speed: int = 2500,
    ) -> Element:
        self.mobile_commands.drag_gesture(
            {"elementId": native_element.id, "endX": end_x, "endY": end_y, "speed": speed},
        )
        return self.element

    @log_debug()
    def _drag_w3c_actions(
        self,
        native_element: WebElement,
        end_x: int,
        end_y: int,
        speed: int = 2500,
    ) -> Element:
        self.w3c_actions.drag(element=native_element, end_x=end_x, end_y=end_y, speed=speed)
        return self.element

    @log_debug()
    def fling(
        self,
        speed: int,
        direction: str,
        strategy: GestureStrategy = GestureStrategy.AUTO,
    ) -> Element:
        """Perform a fling gesture on the element.

        Args:
            speed: The speed at which to perform this gesture in pixels per second.
                The value must be greater than the minimum fling velocity for the given view
                (50 by default).
                The default value is 7500 * displayDensity.
            direction: Direction of the fling. Mandatory value. Acceptable values are:
                up, down, left and right (case-insensitive).
            strategy: Gesture strategy.

        Returns:
            The element for method chaining.

        Note:
            https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-flinggesture

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        self.element.get_driver()
        native_element = self.element._get_web_element(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
            locator=self.element.locator,
        )  # type: ignore[reportPrivateUsage]
        method_map = {
            GestureStrategy.W3C_ACTIONS: self._fling_w3c_actions,
            GestureStrategy.MOBILE_COMMANDS: self._fling_mobile_commands,
            GestureStrategy.AUTO: self._fling_w3c_actions,
        }
        return method_map[strategy](native_element, speed, direction)

    @log_debug()
    def _fling_w3c_actions(
        self,
        native_element: WebElement,
        speed: int,
        direction: str,
    ) -> Element:
        self.w3c_actions.fling(element=native_element, speed=speed, direction=direction)
        return self.element

    @log_debug()
    def _fling_mobile_commands(
        self,
        native_element: WebElement,
        speed: int,
        direction: str,
    ) -> Element:
        self.mobile_commands.fling_gesture(
            {"elementId": native_element.id, "direction": direction, "speed": speed},
        )
        return self.element

    @log_debug()
    def scroll(
        self,
        direction: str,
        percent: float,
        speed: int,
        return_bool: bool,  # noqa: FBT001
        strategy: GestureStrategy = GestureStrategy.AUTO,
    ) -> Element | bool:
        """Perform a scroll gesture on the element.

        Args:
            direction: Scrolling direction. Mandatory value. Acceptable values are:
                up, down, left and right (case-insensitive).
            percent: The size of the scroll as a percentage of the scrolling area size.
                Valid values must be float numbers greater than zero, where 1.0 is 100%.
                Mandatory value.
            speed: The speed at which to perform this gesture in pixels per second.
                The value must not be negative. The default value is 5000 * displayDensity.
            return_bool: If true return bool else return self.
            strategy: Gesture execution strategy (W3C_ACTIONS, MOBILE_COMMANDS, AUTO).

        Returns:
            The element for method chaining.

        Note:
            https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollgesture

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        self.element.get_driver()
        native_element = self.element._get_web_element(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
            locator=self.element.locator,
        )  # type: ignore[reportPrivateUsage]
        method_map = {
            GestureStrategy.W3C_ACTIONS: self._scroll_w3c_actions,
            GestureStrategy.MOBILE_COMMANDS: self._scroll_mobile_commands,
            GestureStrategy.AUTO: self._scroll_mobile_commands,
        }
        return method_map[strategy](native_element, direction, percent, speed, return_bool)

    @log_debug()
    def _scroll_mobile_commands(
        self,
        element: WebElement,
        direction: str,
        percent: float,
        speed: int,
        return_bool: bool,  # noqa: FBT001
    ) -> Element | bool:
        can_scroll = self.mobile_commands.scroll_gesture(
            {
                "elementId": element.id,
                "percent": percent,
                "direction": direction,
                "speed": speed,
            },
        )
        if return_bool:
            return can_scroll
        return self.element

    @log_debug()
    def _scroll_w3c_actions(
        self,
        element: WebElement,
        direction: str,
        percent: float,
        speed: int,
        return_bool: bool,  # noqa: FBT001
    ) -> Element | bool:
        can_scroll = self.w3c_actions.scroll(element, direction, percent, speed)
        if return_bool:
            return can_scroll
        return self.element

    @log_debug()
    def scroll_to_bottom(
        self,
        percent: float = 0.7,
        speed: int = 8000,
        strategy: GestureStrategy = GestureStrategy.AUTO,
    ) -> Element:
        """Scroll to the bottom of the element.

        Args:
            percent: Scroll percentage (default: 0.7).
            speed: Speed of the scroll gesture (default: 8000).
            strategy: Gesture execution strategy (W3C_ACTIONS, MOBILE_COMMANDS, AUTO).

        Returns:
            The element for method chaining.

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        method_map = {
            GestureStrategy.W3C_ACTIONS: self._scroll_to_bottom_w3c_actions,
            GestureStrategy.MOBILE_COMMANDS: self._scroll_to_bottom_mobile_commands,
            GestureStrategy.AUTO: self._scroll_to_bottom_mobile_commands,
        }
        return method_map[strategy](percent, speed)

    @log_debug()
    def _scroll_to_bottom_w3c_actions(self, percent: float = 0.7, speed: int = 8000) -> Element:
        last_hash = cast("int", None)
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            page_hash = hash(self.shadowstep.driver.page_source)
            if page_hash == last_hash:
                return self.element
            last_hash = page_hash
            self.element.scroll_down(
                percent=percent,
                speed=speed,
                return_bool=True,
                strategy=GestureStrategy.W3C_ACTIONS,
            )
        return self.element

    @log_debug()
    def _scroll_to_bottom_mobile_commands(self, percent: float = 0.7, speed: int = 8000) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            if not self.element.scroll_down(
                percent=percent,
                speed=speed,
                return_bool=True,
                strategy=GestureStrategy.MOBILE_COMMANDS,
            ):
                break
        return self.element

    @log_debug()
    def scroll_to_top(
        self,
        percent: float = 0.7,
        speed: int = 8000,
        strategy: GestureStrategy = GestureStrategy.AUTO,
    ) -> Element:
        """Scroll to the top of the element.

        Args:
            percent: Scroll percentage (default: 0.7).
            speed: Speed of the scroll gesture (default: 8000).
            strategy: Gesture execution strategy (W3C_ACTIONS, MOBILE_COMMANDS, AUTO).

        Returns:
            The element for method chaining.

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        method_map = {
            GestureStrategy.W3C_ACTIONS: self._scroll_to_top_w3c_actions,
            GestureStrategy.MOBILE_COMMANDS: self._scroll_to_top_mobile_commands,
            GestureStrategy.AUTO: self._scroll_to_top_mobile_commands,
        }
        return method_map[strategy](percent, speed)

    @log_debug()
    def _scroll_to_top_w3c_actions(self, percent: float = 0.7, speed: int = 8000) -> Element:
        last_hash = cast("int", None)
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            page_hash = hash(self.shadowstep.driver.page_source)
            if page_hash == last_hash:
                return self.element
            last_hash = page_hash
            self.element.scroll_up(
                percent=percent,
                speed=speed,
                return_bool=True,
                strategy=GestureStrategy.W3C_ACTIONS,
            )
        return self.element

    @log_debug()
    def _scroll_to_top_mobile_commands(self, percent: float = 0.7, speed: int = 8000) -> Element:
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            if not self.element.scroll_up(
                percent=percent,
                speed=speed,
                return_bool=True,
                strategy=GestureStrategy.MOBILE_COMMANDS,
            ):
                break
        return self.element

    @log_debug()
    def scroll_to_element(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        max_swipes: int = 30,
        percent: float = 0.7,
        speed: int = 5000,
        strategy: GestureStrategy = GestureStrategy.AUTO,
    ) -> Element:
        """Scroll to find a specific element.

        Args:
            locator: Element locator to scroll to.
            max_swipes: Maximum number of swipes to perform (default: 30).
            percent: Scroll distance as percentage of element size (default: 0.7).
            speed: Scroll speed in pixels per second (default: 5000).
            strategy: Gesture execution strategy (W3C_ACTIONS, MOBILE_COMMANDS, AUTO).

        Returns:
            The element for method chaining.

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        method_map = {
            GestureStrategy.W3C_ACTIONS: self._scroll_to_element_w3c_actions,
            GestureStrategy.MOBILE_COMMANDS: self._scroll_to_element_mobile_commands,
            GestureStrategy.AUTO: self._scroll_to_element_mobile_commands,
        }
        return method_map[strategy](locator, max_swipes, percent, speed)

    @log_debug()
    def _scroll_to_element_w3c_actions(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        max_swipes: int = 30,  # noqa: ARG002
        percent: float = 0.7,
        speed: int = 5000,
    ) -> Element:
        self.logger.info("1")
        target_element = self.shadowstep.get_element(locator)
        target_element.timeout = 1.5
        start_time = time.time()
        self.logger.info("2")
        while time.time() - start_time < self.element.timeout:
            self.logger.info("3")
            if target_element.is_displayed():
                self.logger.info("4")
                return target_element
            self.logger.info("5")
            self.element.scroll_down(percent=percent, speed=speed)
        self.logger.info("6")
        while time.time() - start_time < self.element.timeout:
            self.logger.info("7")
            if target_element.is_displayed():
                self.logger.info("8")
                return target_element
            self.logger.info("9")
            self.element.scroll_up(percent=percent, speed=speed)
        self.logger.info("10")
        return self.shadowstep.get_element(locator)

    @log_debug()
    def _scroll_to_element_mobile_commands(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        max_swipes: int = 30,
        percent: float = 0.7,  # noqa: ARG002
        speed: int = 5000,  # noqa: ARG002
    ) -> Element:
        selector = self.converter.to_uiselector(locator)
        try:
            self._execute_scroll_script(selector, max_swipes)
        except WebDriverException:
            self.logger.warning("Failed execute_scroll_script")
        return self.shadowstep.get_element(locator)

    @log_debug()
    def zoom(
        self,
        percent: float = 0.75,
        speed: int = 2500,
        strategy: GestureStrategy = GestureStrategy.AUTO,
    ) -> Element:
        """Perform a zoom gesture on the element.

        Args:
            percent: Zoom percentage (default: 0.75).
            speed: Speed of the zoom gesture (default: 2500).
            strategy: Gesture execution strategy (W3C_ACTIONS, MOBILE_COMMANDS, AUTO).

        Returns:
            The element for method chaining.

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        self.element.get_driver()
        native_element = self.element._get_web_element(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
            locator=self.element.locator,
        )
        method_map = {
            GestureStrategy.W3C_ACTIONS: self._zoom_w3c_actions,
            GestureStrategy.MOBILE_COMMANDS: self._zoom_mobile_commands,
            GestureStrategy.AUTO: self._zoom_w3c_actions,
        }
        return method_map[strategy](native_element, percent, speed)

    @log_debug()
    def _zoom_w3c_actions(
        self,
        native_element: WebElement,
        percent: float = 0.75,
        speed: int = 2500,
    ) -> Element:
        self.w3c_actions.zoom(element=native_element, percent=percent, speed=speed)
        return self.element

    @log_debug()
    def _zoom_mobile_commands(
        self,
        native_element: WebElement,
        percent: float = 0.75,
        speed: int = 2500,
    ) -> Element:
        self.mobile_commands.pinch_open_gesture(
            {
                "elementId": native_element.id,
                "percent": percent,
                "speed": speed,
            },
        )
        return self.element

    @log_debug()
    def unzoom(
        self,
        percent: float = 0.75,
        speed: int = 2500,
        strategy: GestureStrategy = GestureStrategy.AUTO,
    ) -> Element:
        """Perform an unzoom gesture on the element.

        Args:
            percent: Unzoom percentage (default: 0.75).
            speed: Speed of the unzoom gesture (default: 2500).
            strategy: Gesture execution strategy (W3C_ACTIONS, MOBILE_COMMANDS, AUTO).

        Returns:
            The element for method chaining.

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        self.element.get_driver()
        native_element = self.element._get_web_element(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
            locator=self.element.locator,
        )
        method_map = {
            GestureStrategy.W3C_ACTIONS: self._unzoom_w3c_actions,
            GestureStrategy.MOBILE_COMMANDS: self._unzoom_mobile_commands_actions,
            GestureStrategy.AUTO: self._unzoom_w3c_actions,
        }
        return method_map[strategy](native_element, percent, speed)

    @log_debug()
    def _unzoom_mobile_commands_actions(
        self,
        native_element: WebElement,
        percent: float = 0.75,
        speed: int = 2500,
    ) -> Element:
        self.mobile_commands.pinch_close_gesture(
            {
                "elementId": native_element.id,
                "percent": percent,
                "speed": speed,
            },
        )
        return self.element

    @log_debug()
    def _unzoom_w3c_actions(
        self,
        native_element: WebElement,
        percent: float = 0.75,
        speed: int = 2500,
    ) -> Element:
        self.w3c_actions.unzoom(element=native_element, percent=percent, speed=speed)
        return self.element

    @log_debug()
    def swipe(
        self,
        direction: str,
        percent: float = 0.75,
        speed: int = 5000,
        strategy: GestureStrategy = GestureStrategy.AUTO,
    ) -> Element:
        """Perform a swipe gesture on the element.

        Args:
            direction: Swipe direction (up, down, left, right).
            percent: Swipe percentage (default: 0.75).
            speed: Speed of the swipe gesture (default: 5000).
            strategy: Gesture execution strategy (W3C_ACTIONS, MOBILE_COMMANDS, AUTO).

        Returns:
            The element for method chaining.

        """
        self.logger.info(f"{get_current_func_name()}: {self.element}")  # noqa: G004
        self.element.get_driver()
        native_element = self.element._get_web_element(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
            locator=self.element.locator,
        )  # type: ignore[reportPrivateUsage]
        method_map = {
            GestureStrategy.W3C_ACTIONS: self._swipe_w3c_actions,
            GestureStrategy.MOBILE_COMMANDS: self._swipe_mobile_commands,
            GestureStrategy.AUTO: self._swipe_mobile_commands,
        }
        return method_map[strategy](native_element, direction, percent, speed)

    @log_debug()
    def _swipe_w3c_actions(
        self,
        native_element: WebElement,
        direction: str,
        percent: float = 0.75,
        speed: int = 5000,
    ) -> Element:
        self.w3c_actions.swipe(native_element, direction, percent, speed)
        return self.element

    @log_debug()
    def _swipe_mobile_commands(
        self,
        native_element: WebElement,
        direction: str,
        percent: float = 0.75,
        speed: int = 5000,
    ) -> Element:
        self.mobile_commands.swipe_gesture(
            {
                "elementId": native_element.id,
                "direction": direction.lower(),
                "percent": percent,
                "speed": speed,
            },
        )
        return self.element

    @log_debug()
    def _execute_scroll_script(self, selector: str, max_swipes: int) -> None:
        """Execute mobile scroll script.

        Args:
            selector: UI selector string.
            max_swipes: Maximum number of swipes to perform.

        """
        # https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-scroll
        self.element.get_driver()
        self.element._get_web_element(locator=self.element.locator)  # type: ignore[reportPrivateUsage]  # noqa: SLF001
        self.mobile_commands.scroll(
            {
                "strategy": "-android uiautomator",
                "selector": selector,
                "maxSwipes": max_swipes,
            },
        )

    @log_debug()
    def _perform_tap_and_move_action(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector | None = None,
        x: int | None = None,
        y: int | None = None,
        direction: int | None = None,
        distance: int | None = None,
    ) -> Element | None:
        """Perform tap and move action with error handling.

        Args:
            locator: Target element locator.
            x: Target x coordinate.
            y: Target y coordinate.
            direction: Direction vector for movement.
            distance: Distance to move.

        Returns:
            The element if successful, None otherwise.

        """
        from shadowstep.element.element import Element  # noqa: PLC0415

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
            return self._execute_tap_and_move_by_direction(
                actions,
                x1,
                y1,
                direction,
                distance,
            )

        raise ShadowstepElementException(
            msg=f"Failed to {inspect.currentframe() if inspect.currentframe() else 'unknown'} within {self.element.timeout=} {direction=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def _create_touch_actions(self, x1: int, y1: int) -> ActionChains:
        """Create touch action chain starting at given coordinates.

        Args:
            x1: Starting x coordinate.
            y1: Starting y coordinate.

        Returns:
            ActionChains object for touch actions.

        """
        actions = ActionChains(self.element.driver)
        actions.w3c_actions = ActionBuilder(
            self.element.driver,
            mouse=PointerInput(interaction.POINTER_TOUCH, "touch"),
        )
        actions.w3c_actions.pointer_action.move_to_location(x1, y1)  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.pointer_down()  # type: ignore[reportUnknownMemberType]
        return actions

    @log_debug()
    def _execute_tap_and_move_to_coordinates(
        self,
        actions: ActionChains,
        x: int,
        y: int,
    ) -> Element:
        """Execute tap and move to specific coordinates.

        Args:
            actions: ActionChains object.
            x: Target x coordinate.
            y: Target y coordinate.

        Returns:
            The element for method chaining.

        """
        actions.w3c_actions.pointer_action.move_to_location(x, y)  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.pointer_up()  # type: ignore[reportUnknownMemberType]
        actions.perform()
        return self.element

    @log_debug()
    def _execute_tap_and_move_to_element(
        self,
        actions: ActionChains,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
    ) -> Element:
        """Execute tap and move to another element.

        Args:
            actions: ActionChains object.
            locator: Target element locator.

        Returns:
            The element for method chaining.

        """
        target_element = self.element._get_web_element(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
            locator=locator,
        )  # type: ignore[reportPrivateUsage]
        x, y = self.element.coordinates._get_center_from_native(  # type: ignore[reportPrivateUsage]  # noqa: SLF001
            target_element,
        )  # type: ignore[reportPrivateUsage]
        return self._execute_tap_and_move_to_coordinates(actions, x, y)

    @log_debug()
    def _execute_tap_and_move_by_direction(
        self,
        actions: ActionChains,
        x1: int,
        y1: int,
        direction: int,
        distance: int,
    ) -> Element:
        """Execute tap and move by direction vector.

        Args:
            actions: ActionChains object.
            x1: Starting x coordinate.
            y1: Starting y coordinate.
            direction: Direction vector for movement.
            distance: Distance to move.

        Returns:
            The element for method chaining.

        """
        width, height = self.shadowstep.terminal.get_screen_resolution()  # type: ignore[reportOptionalMemberAccess]
        x2, y2 = find_coordinates_by_vector(
            width=width,
            height=height,
            direction=direction,
            distance=distance,
            start_x=x1,
            start_y=y1,
        )
        return self._execute_tap_and_move_to_coordinates(actions, x2, y2)
