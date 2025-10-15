"""Element gestures module for Shadowstep framework.

This module provides gesture functionality for elements,
including tap, click, drag, swipe, and other mobile gestures.
"""

from __future__ import annotations

import inspect
import logging
import time
import traceback
from typing import TYPE_CHECKING, Any

from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from shadowstep.decorators.common_decorators import log_debug
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.ui_automator.mobile_commands import MobileCommands
from shadowstep.utils.utils import find_coordinates_by_vector

if TYPE_CHECKING:
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

    @log_debug()
    def tap(self, duration: int | None = None) -> Element:
        """Tap the element.

        Args:
            duration: Duration of the tap in milliseconds.

        Returns:
            The element for method chaining.

        """
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
        result = self._perform_tap_and_move_action(locator, x, y, direction, distance)
        if result is not None:
            return result
        return self.element

    @log_debug()
    def click(self, duration: int | None = None) -> Element:
        """Click the element.

        Args:
            duration: Duration of the click in milliseconds.

        Returns:
            The element for method chaining.

        """
        self.element.get_driver()
        self.element._get_web_element(locator=self.element.locator)  # type: ignore[reportPrivateUsage]  # noqa: SLF001
        if duration is None:
            self.mobile_commands.click_gesture({"elementId": self.element.id})
        else:
            self.mobile_commands.long_click_gesture(
                {"elementId": self.element.id, "duration": duration},
            )
        return self.element

    @log_debug()
    def click_double(self) -> Element:
        """Double-click the element.

        Returns:
            The element for method chaining.

        """
        self.element.get_driver()
        self.element._get_web_element(locator=self.element.locator)  # type: ignore[reportPrivateUsage]  # noqa: SLF001
        self.mobile_commands.double_click_gesture({"elementId": self.element.id})
        return self.element

    @log_debug()
    def drag(self, end_x: int, end_y: int, speed: int = 2500) -> Element:
        """Drag the element to specified coordinates.

        Args:
            end_x: Target x coordinate.
            end_y: Target y coordinate.
            speed: Speed of the drag gesture.

        Returns:
            The element for method chaining.

        """
        self.element.get_driver()
        self.element._get_web_element(locator=self.element.locator)  # type: ignore[reportPrivateUsage]  # noqa: SLF001
        self.mobile_commands.drag_gesture(
            {"elementId": self.element.id, "endX": end_x, "endY": end_y, "speed": speed},
        )
        return self.element

    @log_debug()
    def fling(self, speed: int, direction: str) -> Element:
        """Perform a fling gesture on the element.

        Args:
            speed: The speed at which to perform this gesture in pixels per second.
                The value must be greater than the minimum fling velocity for the given view
                (50 by default).
                The default value is 7500 * displayDensity.
            direction: Direction of the fling. Mandatory value. Acceptable values are:
                up, down, left and right (case-insensitive).

        Returns:
            The element for method chaining.

        Note:
            https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-flinggesture

        """
        self.element.get_driver()
        self.element._get_web_element(locator=self.element.locator)  # type: ignore[reportPrivateUsage]  # noqa: SLF001
        self.mobile_commands.fling_gesture(
            {"elementId": self.element.id, "direction": direction, "speed": speed},
        )
        return self.element

    @log_debug()
    def scroll(self, direction: str, percent: float, speed: int, return_bool: bool) -> Element:  # noqa: FBT001
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

        Returns:
            The element for method chaining.

        Note:
            https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollgesture

        """
        self.element.get_driver()
        self.element._get_web_element(locator=self.element.locator)  # type: ignore[reportPrivateUsage]  # noqa: SLF001
        can_scroll = self.mobile_commands.scroll_gesture(
            {
                "elementId": self.element.id,
                "percent": percent,
                "direction": direction,
                "speed": speed,
            },
        )
        if return_bool:
            return can_scroll
        return self.element

    @log_debug()
    def scroll_to_bottom(self, percent: float = 0.7, speed: int = 8000) -> Element:
        """Scroll to the bottom of the element.

        Args:
            percent: Scroll percentage (default: 0.7).
            speed: Speed of the scroll gesture (default: 8000).

        Returns:
            The element for method chaining.

        """
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            if not self.element.scroll_down(percent=percent, speed=speed, return_bool=True):
                return self.element
            self.element.scroll_down(percent=percent, speed=speed, return_bool=True)
        return self.element

    @log_debug()
    def scroll_to_top(self, percent: float = 0.7, speed: int = 8000) -> Element:
        """Scroll to the top of the element.

        Args:
            percent: Scroll percentage (default: 0.7).
            speed: Speed of the scroll gesture (default: 8000).

        Returns:
            The element for method chaining.

        """
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            if not self.element.scroll_up(percent, speed, return_bool=True):
                return self.element
            self.element.scroll_up(percent=percent, speed=speed, return_bool=True)
        return self.element

    @log_debug()
    def scroll_to_element(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        max_swipes: int = 30,
    ) -> Element:
        """Scroll to find a specific element.

        Args:
            locator: Element locator to scroll to.
            max_swipes: Maximum number of swipes to perform (default: 30).

        Returns:
            The element for method chaining.

        """
        selector = self.converter.to_uiselector(locator)
        self._execute_scroll_script(selector, max_swipes)
        return self.shadowstep.get_element(locator)

    @log_debug()
    def zoom(self, percent: float = 0.75, speed: int = 2500) -> Element:
        """Perform a zoom gesture on the element.

        Args:
            percent: Zoom percentage (default: 0.75).
            speed: Speed of the zoom gesture (default: 2500).

        Returns:
            The element for method chaining.

        """
        self.element.get_driver()
        self.element._get_web_element(locator=self.element.locator)  # type: ignore[reportPrivateUsage]  # noqa: SLF001
        self.mobile_commands.pinch_open_gesture(
            {
                "elementId": self.element.id,
                "percent": percent,
                "speed": speed,
            },
        )
        return self.element

    @log_debug()
    def unzoom(self, percent: float = 0.75, speed: int = 2500) -> Element:
        """Perform an unzoom gesture on the element.

        Args:
            percent: Unzoom percentage (default: 0.75).
            speed: Speed of the unzoom gesture (default: 2500).

        Returns:
            The element for method chaining.

        """
        self.element.get_driver()
        self.element._get_web_element(locator=self.element.locator)  # type: ignore[reportPrivateUsage]  # noqa: SLF001
        self.mobile_commands.pinch_close_gesture(
            {
                "elementId": self.element.id,
                "percent": percent,
                "speed": speed,
            },
        )
        return self.element

    @log_debug()
    def swipe(self, direction: str, percent: float = 0.75, speed: int = 5000) -> Element:
        """Perform a swipe gesture on the element.

        Args:
            direction: Swipe direction (up, down, left, right).
            percent: Swipe percentage (default: 0.75).
            speed: Speed of the swipe gesture (default: 5000).

        Returns:
            The element for method chaining.

        """
        self.element.get_driver()
        self.element._get_web_element(locator=self.element.locator)  # type: ignore[reportPrivateUsage]  # noqa: SLF001
        self.mobile_commands.swipe_gesture(
            {
                "elementId": self.element.id,
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
        target_element = self.element._get_web_element(locator=locator)  # type: ignore[reportPrivateUsage]  # noqa: SLF001
        x, y = self.element.coordinates._get_center_from_native(target_element)  # type: ignore[reportPrivateUsage]  # noqa: SLF001
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
