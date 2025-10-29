"""W3C WebDriver Actions implementation for mobile gestures.

This module provides a stable, cross-platform implementation of mobile gestures
using the W3C WebDriver Actions API instead of Appium-specific mobile: commands.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, NoReturn

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from shadowstep.web_driver.web_driver_singleton import WebDriverSingleton

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver
    from appium.webdriver.webelement import WebElement


logger = logging.getLogger(__name__)


class W3CActions:
    """W3C WebDriver Actions implementation for mobile gestures.

    This class provides gesture implementations using ActionChains and ActionBuilder
    from Selenium WebDriver, which are more stable and predictable than Appium's
    mobile: commands.

    All gestures support the same rich API as mobile_commands (direction, percent, speed)
    but use the W3C standard under the hood.
    """

    def __init__(self) -> None:
        """Initialize W3CActions."""
        self.logger = logging.getLogger(__name__)

    def scroll(
        self,
        element: WebElement,
        direction: str,
        percent: float,
        speed: int,
    ) -> bool:
        """Perform scroll gesture on element using W3C Actions.

        Args:
            element: WebElement to scroll.
            direction: Scroll direction (up, down, left, right).
            percent: Scroll distance as percentage of element size (0.0-1.0).
            speed: Scroll speed in pixels per second.

        Returns:
            True if scroll was performed, False if element cannot scroll further.

        """
        try:
            # Get element bounds
            rect = element.rect  # type: ignore[reportUnknownVariableType, reportUnknownMemberType]
            width: int = int(rect["width"])  # type: ignore[reportUnknownArgumentType]
            height: int = int(rect["height"])  # type: ignore[reportUnknownArgumentType]
            center_x: int = int(rect["x"]) + width // 2  # type: ignore[reportUnknownArgumentType]
            center_y: int = int(rect["y"]) + height // 2  # type: ignore[reportUnknownArgumentType]

            # Calculate scroll distance
            direction_lower = direction.lower()
            if direction_lower in ("up", "down"):
                distance = int(height * percent)
            else:  # left, right
                distance = int(width * percent)

            # Calculate start and end points
            start_x: int
            start_y: int
            end_x: int
            end_y: int
            if direction_lower == "down":
                start_x, start_y = center_x, center_y - distance // 2
                end_x, end_y = center_x, center_y + distance // 2
            elif direction_lower == "up":
                start_x, start_y = center_x, center_y + distance // 2
                end_x, end_y = center_x, center_y - distance // 2
            elif direction_lower == "right":
                start_x, start_y = center_x - distance // 2, center_y
                end_x, end_y = center_x + distance // 2, center_y
            elif direction_lower == "left":
                start_x, start_y = center_x + distance // 2, center_y
                end_x, end_y = center_x - distance // 2, center_y
            else:
                self._raise_invalid_direction_error(direction)

            # Calculate duration from speed (pixels/second -> milliseconds)
            duration_ms = int((distance / speed) * 1000) if speed > 0 else 0

            # Execute scroll using W3C Actions
            self._swipe_with_duration(start_x, start_y, end_x, end_y, duration_ms)

        except Exception:
            self.logger.exception("W3C scroll failed")
            return False
        else:
            return True

    def swipe(
        self,
        element: WebElement,
        direction: str,
        percent: float,
        speed: int,
    ) -> None:
        """Perform swipe gesture on element using W3C Actions.

        Args:
            element: WebElement to swipe.
            direction: Swipe direction (up, down, left, right).
            percent: Swipe distance as percentage of element size (0.0-1.0).
            speed: Swipe speed in pixels per second.

        """
        # Swipe is essentially the same as scroll
        self.scroll(element, direction, percent, speed)

    def click(self, element: WebElement, duration: int | None = None) -> None:
        """Perform click gesture on element using W3C Actions.

        Args:
            element: WebElement to click.
            duration: Optional duration for long press in milliseconds.

        """
        rect = element.rect  # type: ignore[reportUnknownVariableType, reportUnknownMemberType]
        x: int = int(rect["x"]) + int(rect["width"]) // 2  # type: ignore[reportUnknownArgumentType]
        y: int = int(rect["y"]) + int(rect["height"]) // 2  # type: ignore[reportUnknownArgumentType]

        actions = ActionChains(self._driver)
        actions.w3c_actions = ActionBuilder(
            self._driver,
            mouse=PointerInput(interaction.POINTER_TOUCH, "touch"),
        )

        actions.w3c_actions.pointer_action.move_to_location(x, y)  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.pointer_down()  # type: ignore[reportUnknownMemberType]

        if duration:
            actions.w3c_actions.pointer_action.pause(duration / 1000)  # type: ignore[reportUnknownMemberType]

        actions.w3c_actions.pointer_action.pointer_up()  # type: ignore[reportUnknownMemberType]
        actions.perform()

    def double_click(self, element: WebElement) -> None:
        """Perform double-click gesture on element using W3C Actions.

        Args:
            element: WebElement to double-click.

        """
        rect = element.rect  # type: ignore[reportUnknownVariableType, reportUnknownMemberType]
        x: int = int(rect["x"]) + int(rect["width"]) // 2  # type: ignore[reportUnknownArgumentType]
        y: int = int(rect["y"]) + int(rect["height"]) // 2  # type: ignore[reportUnknownArgumentType]

        actions = ActionChains(self._driver)
        actions.w3c_actions = ActionBuilder(
            self._driver,
            mouse=PointerInput(interaction.POINTER_TOUCH, "touch"),
        )

        # First click
        actions.w3c_actions.pointer_action.move_to_location(x, y)  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.pointer_down()  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.pointer_up()  # type: ignore[reportUnknownMemberType]

        # Small pause between clicks
        actions.w3c_actions.pointer_action.pause(0.1)  # type: ignore[reportUnknownMemberType]

        # Second click
        actions.w3c_actions.pointer_action.pointer_down()  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.pointer_up()  # type: ignore[reportUnknownMemberType]

        actions.perform()

    def drag(self, element: WebElement, end_x: int, end_y: int, speed: int) -> None:
        """Perform drag gesture from element to coordinates using W3C Actions.

        Args:
            element: WebElement to drag from.
            end_x: Target x coordinate.
            end_y: Target y coordinate.
            speed: Drag speed in pixels per second.

        """
        rect = element.rect  # type: ignore[reportUnknownVariableType, reportUnknownMemberType]
        start_x: int = int(rect["x"]) + int(rect["width"]) // 2  # type: ignore[reportUnknownArgumentType]
        start_y: int = int(rect["y"]) + int(rect["height"]) // 2  # type: ignore[reportUnknownArgumentType]

        # Calculate distance and duration
        distance: int = int(((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5)
        duration_ms = int((distance / speed) * 1000) if speed > 0 else 0

        self._swipe_with_duration(start_x, start_y, end_x, end_y, duration_ms)

    def fling(self, element: WebElement, direction: str, speed: int) -> None:
        """Perform fling gesture on element using W3C Actions.

        Args:
            element: WebElement to fling.
            direction: Fling direction (up, down, left, right).
            speed: Fling speed in pixels per second.

        """
        # Fling is a fast swipe across the element
        # Use a large percent (0.8) to cover most of the element
        self.scroll(element, direction, percent=0.8, speed=speed)

    def zoom(self, element: WebElement, percent: float, speed: int) -> None:
        """Perform pinch-open (zoom) gesture on element using W3C Actions.

        Args:
            element: WebElement to zoom.
            percent: Zoom magnitude as percentage (0.0-1.0).
            speed: Zoom speed in pixels per second.

        """
        rect = element.rect  # type: ignore[reportUnknownVariableType, reportUnknownMemberType]
        center_x: int = int(rect["x"]) + int(rect["width"]) // 2  # type: ignore[reportUnknownArgumentType]
        center_y: int = int(rect["y"]) + int(rect["height"]) // 2  # type: ignore[reportUnknownArgumentType]

        # Calculate pinch distance
        distance: int = int(min(int(rect["width"]), int(rect["height"])) * percent / 2)  # type: ignore[reportUnknownArgumentType]
        duration_ms = int((distance / speed) * 1000) if speed > 0 else 0

        # Two fingers moving apart from center
        finger1_start_x: int = center_x
        finger1_start_y: int = center_y
        finger1_end_x: int = center_x
        finger1_end_y: int = center_y - distance

        finger2_start_x: int = center_x
        finger2_start_y: int = center_y
        finger2_end_x: int = center_x
        finger2_end_y: int = center_y + distance

        self._multi_touch_gesture(
            [(finger1_start_x, finger1_start_y), (finger2_start_x, finger2_start_y)],
            [(finger1_end_x, finger1_end_y), (finger2_end_x, finger2_end_y)],
            duration_ms,
        )

    def unzoom(self, element: WebElement, percent: float, speed: int) -> None:
        """Perform pinch-close (unzoom) gesture on element using W3C Actions.

        Args:
            element: WebElement to unzoom.
            percent: Unzoom magnitude as percentage (0.0-1.0).
            speed: Unzoom speed in pixels per second.

        """
        rect = element.rect  # type: ignore[reportUnknownVariableType, reportUnknownMemberType]
        center_x: int = int(rect["x"]) + int(rect["width"]) // 2  # type: ignore[reportUnknownArgumentType]
        center_y: int = int(rect["y"]) + int(rect["height"]) // 2  # type: ignore[reportUnknownArgumentType]

        # Calculate pinch distance
        distance: int = int(min(int(rect["width"]), int(rect["height"])) * percent / 2)  # type: ignore[reportUnknownArgumentType]
        duration_ms = int((distance / speed) * 1000) if speed > 0 else 0

        # Two fingers moving toward center
        finger1_start_x: int = center_x
        finger1_start_y: int = center_y - distance
        finger1_end_x: int = center_x
        finger1_end_y: int = center_y

        finger2_start_x: int = center_x
        finger2_start_y: int = center_y + distance
        finger2_end_x: int = center_x
        finger2_end_y: int = center_y

        self._multi_touch_gesture(
            [(finger1_start_x, finger1_start_y), (finger2_start_x, finger2_start_y)],
            [(finger1_end_x, finger1_end_y), (finger2_end_x, finger2_end_y)],
            duration_ms,
        )

    def _swipe_with_duration(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration_ms: int,
    ) -> None:
        """Execute swipe gesture with specified duration.

        Args:
            start_x: Starting x coordinate.
            start_y: Starting y coordinate.
            end_x: Ending x coordinate.
            end_y: Ending y coordinate.
            duration_ms: Duration of the swipe in milliseconds.

        """
        touch_input = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions = ActionChains(self._driver)
        actions.w3c_actions = ActionBuilder(self._driver, mouse=touch_input)

        # Move to start position
        actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.pointer_down()  # type: ignore[reportUnknownMemberType]

        # Create new action builder with duration for the move
        if duration_ms > 0:
            actions.w3c_actions = ActionBuilder(
                self._driver,
                mouse=touch_input,
                duration=duration_ms,
            )

        # Move to end position
        actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.release()  # type: ignore[reportUnknownMemberType]

        actions.perform()

    def _multi_touch_gesture(
        self,
        start_positions: list[tuple[int, int]],
        end_positions: list[tuple[int, int]],
        duration_ms: int,
    ) -> None:
        """Execute multi-touch gesture (e.g., pinch).

        Args:
            start_positions: List of (x, y) starting positions for each finger.
            end_positions: List of (x, y) ending positions for each finger.
            duration_ms: Duration of the gesture in milliseconds.

        """
        actions = ActionChains(self._driver)
        actions.w3c_actions.devices = []

        for i, (start_pos, end_pos) in enumerate(zip(start_positions, end_positions, strict=False)):  # type: ignore[reportUnknownArgumentType]
            finger_input = actions.w3c_actions.add_pointer_input(
                interaction.POINTER_TOUCH,
                f"finger{i + 1}",
            )

            # Move to start position
            finger_input.create_pointer_move(x=start_pos[0], y=start_pos[1])  # type: ignore[reportUnknownMemberType]
            finger_input.create_pointer_down()  # type: ignore[reportUnknownMemberType]

            # Pause for duration (optional)
            if duration_ms > 0:
                finger_input.create_pause(duration_ms / 1000)

            # Move to end position
            finger_input.create_pointer_move(  # type: ignore[reportUnknownMemberType]
                x=end_pos[0],  # type: ignore[reportUnknownArgumentType]
                y=end_pos[1],  # type: ignore[reportUnknownArgumentType]
                duration=int(duration_ms / 1000) if duration_ms > 0 else 0,
            )
            finger_input.create_pointer_up(interaction.POINTER_TOUCH)  # type: ignore[reportUnknownMemberType]

        actions.perform()

    def _raise_invalid_direction_error(self, direction: str) -> NoReturn:
        """Raise ValueError for invalid direction.

        Args:
            direction: Направление, которое было передано.

        Raises:
            ValueError: Всегда вызывает исключение для неверного направления.

        """
        msg = f"Invalid direction: {direction}. Use up/down/left/right."
        raise ValueError(msg)

    @property
    def _driver(self) -> WebDriver:
        """Return driver instance."""
        return WebDriverSingleton.get_driver()
