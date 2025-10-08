"""Main Shadowstep framework module.

This module provides the core Shadowstep class for mobile automation testing
with Appium, including page object management, element interaction, and
gesture controls.

https://github.com/appium/appium-uiautomator2-driver
"""

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)
from typing_extensions import Self

from shadowstep.decorators.decorators import fail_safe
from shadowstep.element.element import Element
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException
from shadowstep.image.image import ShadowstepImage
from shadowstep.navigator.navigator import PageNavigator
from shadowstep.shadowstep_base import ShadowstepBase, WebDriverSingleton
from shadowstep.ui_automator.mobile_commands import MobileCommands
from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    import numpy as np
    from numpy._typing import NDArray
    from PIL import Image
    from selenium.types import WaitExcTypes

    from shadowstep.locator import UiSelector
    from shadowstep.page_base import PageBaseShadowstep
    from shadowstep.scheduled_actions.action_history import ActionHistory
    from shadowstep.scheduled_actions.action_step import ActionStep

# Configure the root logger (basic configuration)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Shadowstep(ShadowstepBase):
    """Main Shadowstep framework class for mobile automation testing.

    This class provides a singleton instance for managing mobile app testing
    with Appium, including page object discovery, element interaction,
    gesture controls, and logging capabilities.
    """

    _instance: Shadowstep | None = None

    def __new__(cls, *args: object, **kwargs: object) -> Self:  # noqa: ARG004
        """Create a new instance or return existing singleton instance.

        Returns:
            Shadowstep: The singleton instance of the Shadowstep class.

        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance  # type: ignore[return-value]

    @classmethod
    def get_instance(cls) -> Shadowstep:
        """Get the singleton instance of Shadowstep.

        Returns:
            Shadowstep: The singleton instance of the Shadowstep class.

        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, *args: object, **kwargs: object) -> None:  # noqa: ARG002
        """Initialize the Shadowstep instance.

        Sets up logging, page discovery, and initializes core components.
        """
        if getattr(self, "_initialized", False):
            return
        super().__init__()

        self.navigator: PageNavigator = PageNavigator(self)
        self.navigator.auto_discover_pages()
        self.mobile_commands: MobileCommands = MobileCommands()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = True

    def get_page(self, name: str) -> PageBaseShadowstep:
        """Get a page instance by name.

        Args:
            name: The name of the page to retrieve.

        Returns:
            PageBaseShadowstep: An instance of the requested page.

        Raises:
            ValueError: If the page is not found in registered pages.

        """
        return self.navigator.get_page(name)

    def resolve_page(self, name: str) -> PageBaseShadowstep:
        """Resolve a page instance by name.

        Args:
            name: The name of the page to resolve.

        Returns:
            PageBaseShadowstep: An instance of the requested page.

        Raises:
            ValueError: If the page is not found.

        """
        return self.navigator.resolve_page(name)

    def get_element(
            self,
            locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
            timeout: int = 30,
            poll_frequency: float = 0.5,
            ignored_exceptions: WaitExcTypes | None = None,
    ) -> Element:
        """Get a single element by locator.

        Args:
            locator: Locator tuple, dict, Element, or UiSelector to find element.
            timeout: How long to wait for element to appear.
            poll_frequency: How often to poll for element.
            ignored_exceptions: Exceptions to ignore during waiting.

        Returns:
            Element: The found element.

        """
        self.logger.debug("%s", get_current_func_name())
        return Element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
            shadowstep=self,
        )

    def get_elements(
            self,
            locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
            timeout: int = 30,
            poll_frequency: float = 0.5,
            ignored_exceptions: WaitExcTypes | None = None,
    ) -> list[Element]:
        """Find multiple elements matching the given locator across the whole page.

        method is greedy.

        Args:
            locator: Locator tuple or dict to search elements.
            timeout: How long to wait for elements.
            poll_frequency: Polling frequency.
            ignored_exceptions: Exceptions to ignore.

        Returns:
            Elements: Lazy iterable of Element instances.

        """
        self.logger.debug("%s", get_current_func_name())
        root = Element(
            locator=("xpath", "//*"),
            shadowstep=self,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
        )
        return root.get_elements(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
        )

    def get_image(
            self,
            image: bytes | NDArray[np.uint8] | Image.Image | str,
            threshold: float = 0.5,
            timeout: float = 5.0,
    ) -> ShadowstepImage:
        """Return a lazy ShadowstepImage wrapper for the given template.

        Args:
            image: template (bytes, ndarray, PIL.Image or path)
            threshold: matching threshold [0-1]  # noqa: RUF002
            timeout: max seconds to search

        Returns:
            ShadowstepImage: Lazy object for image-actions.

        """
        self.logger.debug("%s", get_current_func_name())
        return ShadowstepImage(
            image=image,
            base=self,
            threshold=threshold,
            timeout=timeout,
        )

    def get_images(
            self,
            image: bytes | NDArray[np.uint8] | Image.Image | str,
            threshold: float = 0.5,
            timeout: float = 5.0,
    ) -> list[ShadowstepImage]:
        """Return a list of ShadowstepImage wrappers for the given template.

        Args:
            image: template (bytes, ndarray, PIL.Image or path)
            threshold: matching threshold [0-1]  # noqa: RUF002
            timeout: max seconds to search

        Returns:
            list[ShadowstepImage]: List of lazy objects for image-actions.

        """
        self.logger.debug("%s", get_current_func_name())
        # For now, return a single image wrapped in a list
        # TODO: Implement multiple image matching  # noqa: TD002, TD003, FIX002
        return [
            ShadowstepImage(
                image=image,
                base=self,
                threshold=threshold,
                timeout=timeout,
            ),
        ]

    def schedule_action(  # noqa: PLR0913
            self,
            name: str,
            steps: list[ActionStep],
            interval_ms: int = 1000,
            times: int = 1,
            max_pass: int | None = None,
            max_fail: int | None = None,
            max_history_items: int = 20,
    ) -> Shadowstep:
        """Schedule a server-side action sequence.

        Args:
            name: unique action name.
            steps: List of steps (GestureStep, SourceStep, ScreenshotStep, etc.).
            interval_ms: Pause between runs in milliseconds.
            times: How many times to attempt execution.
            max_pass: Stop after N successful runs.
            max_fail: Stop after N failures.
            max_history_items: How many records to keep in history.

        Returns:
            self — for convenient chaining.

        """
        # shadowstep/scheduled_actions
        raise NotImplementedError

    def get_action_history(self, name: str) -> ActionHistory:
        """Fetch the execution history for the named action.

        Args:
            name: Same name as used in schedule_action.

        Returns:
            ActionHistory — convenient wrapper over JSON response.

        """
        # shadowstep/scheduled_actions
        raise NotImplementedError

    def unschedule_action(self, name: str) -> ActionHistory:
        """Unschedule the action and return its final history.

        Args:
            name: Same name as used in schedule_action.

        Returns:
            ActionHistory — history of all executions until cancellation.

        """
        # shadowstep/scheduled_actions
        raise NotImplementedError

    def start_logcat(
            self,
            filename: str,
            port: int | None = None,
            filters: list[str] | None = None,
    ) -> None:
        """filename: log file name.

        port: port of Appium server instance, provide if you use grid.
        """
        if filters is not None:
            self._logcat.filters = filters
        self._logcat.start(filename, port)

    def stop_logcat(self) -> None:
        """Stop the logcat recording.

        This method stops the currently running logcat recording process.

        """
        self._logcat.stop()

    def find_and_get_element(
            self,
            locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
            timeout: int = 30,
            poll_frequency: float = 0.5,
            ignored_exceptions: WaitExcTypes | None = None,
            max_swipes: int = 30,
    ) -> Element:
        """Find and get an element by scrolling through scrollable elements.

        Args:
            locator: Locator tuple, dict, Element, or UiSelector to find element.
            timeout: How long to wait for element to appear.
            poll_frequency: How often to poll for element.
            ignored_exceptions: Exceptions to ignore during waiting.
            max_swipes: Maximum number of swipes to perform.

        Returns:
            Element: The found element.

        Raises:
            ShadowstepException: If element is not found in any scrollable element.

        """
        self.logger.debug("%s", get_current_func_name())
        try:
            scrollables = self.get_elements(
                locator={"scrollable": "true"},
                timeout=timeout,
                poll_frequency=poll_frequency,
                ignored_exceptions=ignored_exceptions,
            )
            for scrollable in scrollables:
                try:
                    scrollable: Element
                    return scrollable.scroll_to_element(locator=locator, max_swipes=max_swipes)
                except Exception as e:  # noqa: BLE001, PERF203
                    self.logger.debug("Scroll attempt failed on scrollable element: %s", e)
                    continue
            error_msg = f"Element with locator {locator} not found in any scrollable element"
            raise ShadowstepException(error_msg)  # noqa: TRY301
        except Exception as e:
            self.logger.error("Failed to find scrollable elements: %s", e)  # noqa: TRY400
            raise

    def is_text_visible(self, text: str) -> bool:
        """Check if an element with the given text is visible.

        Args:
            text (str): The exact or partial text to search for.

        Returns:
            bool: True if element is found and visible, False otherwise.

        """
        self.logger.debug("%s", get_current_func_name())
        try:
            element = Element(locator={"text": text}, shadowstep=self)
            return element.is_visible()
        except Exception as e:  # noqa: BLE001
            self.logger.warning("Failed to check visibility for text='%s': %s", text, e)
            return False

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException),
    )
    def scroll(  # noqa: PLR0913
            self,
            left: int,
            top: int,
            width: int,
            height: int,
            direction: str,
            percent: float,
            speed: int,
    ) -> Shadowstep:
        """Perform a scroll gesture in the specified area.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-scrollgesture

        Args:
            left (int): Left coordinate of the scroll area.
            top (int): Top coordinate of the scroll area.
            width (int): Width of the scroll area.
            height (int): Height of the scroll area.
            direction (str): Scroll direction: 'up', 'down', 'left', 'right'.
            percent (float): Scroll size as percentage (0.0 < percent <= 1.0).
            speed (int): Speed in pixels per second.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments:
        elementId: The id of the element to be scrolled. If the element id is missing
            then scroll bounding area must be provided. If both the element id and
            the scroll bounding area are provided then this area is effectively ignored.
        left: The left coordinate of the scroll bounding area.
        top: The top coordinate of the scroll bounding area.
        width: The width of the scroll bounding area.
        height: The height of the scroll bounding area.
        direction: Scrolling direction. Mandatory value. Acceptable values are:
            up, down, left and right (case insensitive).
        percent: The size of the scroll as a percentage of the scrolling area size.
            Valid values must be float numbers greater than zero, where 1.0 is 100%.
            Mandatory value.
        speed: The speed at which to perform this gesture in pixels per second.
            The value must not be negative. The default value is 5000 * displayDensity.

        """
        self.logger.debug("%s", get_current_func_name())

        # Defensive validation (optional, to fail early on bad input)
        if direction.lower() not in {"up", "down", "left", "right"}:
            msg = f"Invalid direction '{direction}', must be one of: up, down, left, right"
            raise ValueError(msg)

        if not (0.0 < percent <= 1.0):
            error_msg = f"Percent must be between 0 and 1, got {percent}"
            raise ValueError(error_msg)

        if speed < 0:
            error_msg = f"Speed must be non-negative, got {speed}"
            raise ValueError(error_msg)

        self.mobile_commands.scroll_gesture(
            {
                "left": left,
                "top": top,
                "width": width,
                "height": height,
                "direction": direction.lower(),
                "percent": percent,
                "speed": speed,
            },
        )
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException),
    )
    def long_click(self, x: int, y: int, duration: int) -> Shadowstep:
        """Perform a long click gesture at the given coordinates.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-longclickgesture

        Args:
            x (int): X-coordinate of the click.
            y (int): Y-coordinate of the click.
            duration (int): Duration in milliseconds (default: 500). Must be ≥ 0.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments:
        elementId: The id of the element to be clicked. If the element is missing
            then both click offset coordinates must be provided. If both the element
            id and offset are provided then the coordinates are parsed as relative
            offsets from the top left corner of the element.
        x: The x-offset coordinate.
        y: The y-offset coordinate.
        duration: Click duration in milliseconds. 500 by default. The value must
            not be negative.
        locator: The map containing strategy and selector items to make it possible
            to click dynamic elements.

        """
        self.logger.debug("%s", get_current_func_name())
        if duration < 0:
            msg = f"Duration must be non-negative, got {duration}"
            raise ValueError(msg)
        self.mobile_commands.long_click_gesture(
            {"x": x, "y": y, "duration": duration},
        )
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                StaleElementReferenceException,
        ),
    )
    def double_click(self, x: int, y: int) -> Shadowstep:
        """Perform a double click gesture at the given coordinates.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-doubleclickgesture

        Args:
            x (int): X-coordinate of the click.
            y (int): Y-coordinate of the click.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be clicked. If the element is missing
            then both click offset coordinates must be provided. If both the element
            id and offset are provided then the coordinates are parsed as relative
            offsets from the top left corner of the element.
        x: The x-offset coordinate
        y: The y-offset coordinate
        locator: The map containing strategy and selector items to make it possible
            to click dynamic elements.

        """
        self.logger.debug("%s", get_current_func_name())
        self.mobile_commands.double_click_gesture(
            {"x": x, "y": y},
        )
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                StaleElementReferenceException,
        ),
    )
    def click(self, x: int, y: int) -> Shadowstep:
        """Perform a click gesture at the given coordinates.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-clickgesture

        Args:
            x (int): X-coordinate of the click.
            y (int): Y-coordinate of the click.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be clicked. If the element is missing
            then both click offset coordinates must be provided. If both the element
            id and offset are provided then the coordinates are parsed as relative
            offsets from the top left corner of the element.
        x: The x-offset coordinate
        y: The y-offset coordinate
        locator: The map containing strategy and selector items to make it possible
            to click dynamic elements.

        """
        self.logger.debug("%s", get_current_func_name())
        self.mobile_commands.click_gesture(
            {"x": x, "y": y},
        )
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                StaleElementReferenceException,
        ),
    )
    def drag(
            self,
            start_x: int,
            start_y: int,
            end_x: int,
            end_y: int,
            speed: int,
    ) -> Shadowstep:
        """Perform a drag gesture from one point to another.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-draggesture

        Args:
            start_x (int): Starting X coordinate.
            start_y (int): Starting Y coordinate.
            end_x (int): Target X coordinate.
            end_y (int): Target Y coordinate.
            speed (int): Speed of the gesture in pixels per second.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be dragged. If the element id is missing
            then both start coordinates must be provided. If both the element id and
            the start coordinates are provided then these coordinates are considered
            as offsets from the top left element corner.
        startX: The x-start coordinate
        startY: The y-start coordinate
        endX: The x-end coordinate. Mandatory argument
        endY: The y-end coordinate. Mandatory argument
        speed: The speed at which to perform this gesture in pixels per second.
            The value must not be negative. The default value is 2500 * displayDensity.

        """
        self.logger.debug("%s", get_current_func_name())
        if speed < 0:
            error_msg = f"Speed must be non-negative, got {speed}"
            raise ValueError(error_msg)
        self.mobile_commands.drag_gesture(
            {
                "startX": start_x,
                "startY": start_y,
                "endX": end_x,
                "endY": end_y,
                "speed": speed,
            },
        )
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                StaleElementReferenceException,
        ),
    )
    def fling(  # noqa: PLR0913
            self,
            left: int,
            top: int,
            width: int,
            height: int,
            direction: str,
            speed: int,
    ) -> Shadowstep:
        """Perform a fling gesture in the specified area.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-flinggesture

        Args:
            left (int): Left coordinate of the fling area.
            top (int): Top coordinate.
            width (int): Width of the area.
            height (int): Height of the area.
            direction (str): One of: 'up', 'down', 'left', 'right'.
            speed (int): Speed in pixels per second (> 50).

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be flinged. If the element id is missing
            then fling bounding area must be provided. If both the element id and
            the fling bounding area are provided then this area is effectively ignored.
        left: The left coordinate of the fling bounding area
        top: The top coordinate of the fling bounding area
        width: The width of the fling bounding area
        height: The height of the fling bounding area
        direction: Direction of the fling. Mandatory value. Acceptable values are:
            up, down, left and right (case insensitive).
        speed: The speed at which to perform this gesture in pixels per second.
            The value must be greater than the minimum fling velocity for the given
            view (50 by default). The default value is 7500 * displayDensity.

        """
        self.logger.debug("%s", get_current_func_name())

        if direction.lower() not in {"up", "down", "left", "right"}:
            msg = "Invalid direction: {direction}"
            raise ValueError(msg)
        if speed <= 0:
            msg = f"Speed must be > 0, got {speed}"
            raise ValueError(msg)
        self.mobile_commands.fling_gesture(
            {
                "left": left,
                "top": top,
                "width": width,
                "height": height,
                "direction": direction.lower(),
                "speed": speed,
            },
        )
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                StaleElementReferenceException,
        ),
    )
    def pinch_open(  # noqa: PLR0913
            self,
            left: int,
            top: int,
            width: int,
            height: int,
            percent: float,
            speed: int,
    ) -> Shadowstep:
        """Perform a pinch-open gesture in the given bounding area.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-pinchopengesture

        Args:
            left (int): Left coordinate of the bounding box.
            top (int): Top coordinate.
            width (int): Width of the bounding box.
            height (int): Height of the bounding box.
            percent (float): Scale of the pinch (0.0 < percent ≤ 1.0).
            speed (int): Speed in pixels per second.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be pinched. If the element id is missing
            then pinch bounding area must be provided. If both the element id and
            the pinch bounding area are provided then the area is effectively ignored.
        left: The left coordinate of the pinch bounding area
        top: The top coordinate of the pinch bounding area
        width: The width of the pinch bounding area
        height: The height of the pinch bounding area
        percent: The size of the pinch as a percentage of the pinch area size.
            Valid values must be float numbers in range 0..1, where 1.0 is 100%.
            Mandatory value.
        speed: The speed at which to perform this gesture in pixels per second.
            The value must not be negative. The default value is 2500 * displayDensity.

        """
        self.logger.debug("%s", get_current_func_name())

        if not (0.0 < percent <= 1.0):
            error_msg = f"Percent must be between 0 and 1, got {percent}"
            raise ValueError(error_msg)
        if speed < 0:
            error_msg = f"Speed must be non-negative, got {speed}"
            raise ValueError(error_msg)
        self.mobile_commands.pinch_open_gesture(
            {
                "left": left,
                "top": top,
                "width": width,
                "height": height,
                "percent": percent,
                "speed": speed,
            },
        )
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                StaleElementReferenceException,
        ),
    )
    def pinch_close(  # noqa: PLR0913
            self,
            left: int,
            top: int,
            width: int,
            height: int,
            percent: float,
            speed: int,
    ) -> Shadowstep:
        """Perform a pinch-close gesture in the given bounding area.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-pinchclosegesture

        Args:
            left (int): Left coordinate of the bounding box.
            top (int): Top coordinate of the bounding box.
            width (int): Width of the bounding box.
            height (int): Height of the bounding box.
            percent (float): Pinch size as a percentage of area (0.0 < percent ≤ 1.0).
            speed (int): Speed of the gesture in pixels per second (≥ 0).

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be pinched. If the element id is missing
            then pinch bounding area must be provided. If both the element id and
            the pinch bounding area are provided then the area is effectively ignored.
        left: The left coordinate of the pinch bounding area
        top: The top coordinate of the pinch bounding area
        width: The width of the pinch bounding area
        height: The height of the pinch bounding area
        percent: The size of the pinch as a percentage of the pinch area size.
            Valid values must be float numbers in range 0..1, where 1.0 is 100%.
            Mandatory value.
        speed: The speed at which to perform this gesture in pixels per second.
            The value must not be negative. The default value is 2500 * displayDensity.

        """
        self.logger.debug("%s", get_current_func_name())

        if not (0.0 < percent <= 1.0):
            error_msg = f"Percent must be between 0 and 1, got {percent}"
            raise ValueError(error_msg)
        if speed < 0:
            error_msg = f"Speed must be non-negative, got {speed}"
            raise ValueError(error_msg)
        self.mobile_commands.pinch_open_gesture(
            {
                "left": left,
                "top": top,
                "width": width,
                "height": height,
                "percent": percent,
                "speed": speed,
            },
        )
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                StaleElementReferenceException,
        ),
    )
    def swipe(  # noqa: PLR0913
            self,
            left: int,
            top: int,
            width: int,
            height: int,
            direction: str,
            percent: float = 0.5,
            speed: int = 8000,
    ) -> Shadowstep:
        """Perform a swipe gesture within the specified bounding box.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-swipegesture

        Args:
            left (int): Left coordinate of the swipe area.
            top (int): Top coordinate of the swipe area.
            width (int): Width of the swipe area.
            height (int): Height of the swipe area.
            direction (str): Swipe direction: 'up', 'down', 'left', or 'right'.
            percent (float): Swipe distance as percentage of area size (0.0 < percent ≤ 1.0).
            speed (int): Swipe speed in pixels per second (≥ 0).

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be swiped. If the element id is missing
            then swipe bounding area must be provided. If both the element id and
            the swipe bounding area are provided then the area is effectively ignored.
        left: The left coordinate of the swipe bounding area
        top: The top coordinate of the swipe bounding area
        width: The width of the swipe bounding area
        height: The height of the swipe bounding area
        direction: Swipe direction. Mandatory value. Acceptable values are:
            up, down, left and right (case insensitive).
        percent: The size of the swipe as a percentage of the swipe area size.
            Valid values must be float numbers in range 0..1, where 1.0 is 100%.
            Mandatory value.
        speed: The speed at which to perform this gesture in pixels per second.
            The value must not be negative. The default value is 5000 * displayDensity.

        """
        self.logger.debug("%s", get_current_func_name())

        if direction.lower() not in {"up", "down", "left", "right"}:
            error_msg = f"Invalid direction '{direction}' — must be one of: up, down, left, right"
            raise ValueError(error_msg)
        if not (0.0 < percent <= 1.0):
            error_msg = f"Percent must be between 0 and 1, got {percent}"
            raise ValueError(error_msg)
        if speed < 0:
            error_msg = f"Speed must be non-negative, got {speed}"
            raise ValueError(error_msg)
        self.mobile_commands.swipe_gesture(
            {
                "left": left,
                "top": top,
                "width": width,
                "height": height,
                "direction": direction.lower(),
                "percent": percent,
                "speed": speed,
            },
        )
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException),
    )
    def swipe_right_to_left(self) -> Shadowstep:
        """Perform a full-width horizontal swipe from right to left.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())

        driver = WebDriverSingleton.get_driver()
        size: dict[str, int] = driver.get_window_size()  # type: ignore[return-value]
        width = size["width"]
        height = size["height"]

        return self.swipe(
            left=0,
            top=height // 2,
            width=width,
            height=height // 3,
            direction="left",
            percent=1.0,
            speed=1000,
        )

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                StaleElementReferenceException,
        ),
    )
    def swipe_left_to_right(self) -> Shadowstep:
        """Perform a full-width horizontal swipe from left to right.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())

        driver = WebDriverSingleton.get_driver()
        size: dict[str, int] = driver.get_window_size()  # type: ignore[return-value]
        width = size["width"]
        height = size["height"]

        return self.swipe(
            left=0,
            top=height // 2,
            width=width,
            height=height // 3,
            direction="right",
            percent=1.0,
            speed=1000,
        )

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                StaleElementReferenceException,
        ),
    )
    def swipe_top_to_bottom(self, percent: float = 1.0, speed: int = 5000) -> Shadowstep:
        """Perform a full-height vertical swipe from top to bottom.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())

        driver = WebDriverSingleton.get_driver()
        size: dict[str, int] = driver.get_window_size()  # type: ignore[return-value]
        width = size["width"]
        height = size["height"]

        return self.swipe(
            left=width // 2,
            top=0,
            width=width // 3,
            height=height,
            direction="down",
            percent=percent,
            speed=speed,
        )

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                StaleElementReferenceException,
        ),
    )
    def swipe_bottom_to_top(self, percent: float = 1.0, speed: int = 5000) -> Shadowstep:
        """Perform a full-height vertical swipe from bottom to top.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())

        driver = WebDriverSingleton.get_driver()
        size: dict[str, int] = driver.get_window_size()  # type: ignore[return-value]
        width = size["width"]
        height = size["height"]

        return self.swipe(
            left=width // 2,
            top=0,
            width=width // 3,
            height=height,
            direction="up",
            percent=percent,
            speed=speed,
        )

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                WebDriverException,
                StaleElementReferenceException,
        ),
    )
    def save_screenshot(self, path: str = "", filename: str = "screenshot.png") -> bool:
        """Save a screenshot to file.

        Args:
            path: Directory path to save the screenshot.
            filename: Name of the screenshot file.

        Returns:
            bool: True if successful.

        """
        self.logger.debug("%s", get_current_func_name())
        path_to_file = Path(path) / filename
        with path_to_file.open("wb") as f:
            f.write(self.get_screenshot())
        return True

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException),
    )
    def get_screenshot(self) -> bytes:
        """Get screenshot as bytes.

        Returns:
            bytes: Screenshot data in binary format.

        """
        self.logger.debug("%s", get_current_func_name())
        screenshot = self.driver.get_screenshot_as_base64().encode("utf-8")
        return base64.b64decode(screenshot)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException),
    )
    def save_source(self, path: str = "", filename: str = "screenshot.png") -> bool:
        """Save page source to file.

        Args:
            path: Directory path to save the file.
            filename: Name of the file to save.

        Returns:
            bool: True if successful.

        """
        self.logger.debug("%s", get_current_func_name())
        path_to_file = Path(path) / filename
        with path_to_file.open("wb") as f:
            f.write(self.driver.page_source.encode("utf-8"))
        return True

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException,
                InvalidSessionIdException,
                StaleElementReferenceException,
        ),
    )
    def tap(self, x: int, y: int, duration: int | None = None) -> Shadowstep:
        """Tap at specified coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.
            duration: Tap duration in milliseconds.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self.driver.tap([(x, y)], duration or 100)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException),
    )
    def start_recording_screen(self) -> None:
        """Start screen recording using Appium driver."""
        self.logger.debug("%s", get_current_func_name())
        self.driver.start_recording_screen()

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException),
    )
    def stop_recording_screen(self) -> bytes:
        """Stop screen recording and return video as bytes.

        Returns:
            bytes: Video recording in base64-decoded format.

        """
        self.logger.debug("%s", get_current_func_name())
        encoded = self.driver.stop_recording_screen()
        return base64.b64decode(encoded)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException),
    )
    def push(self, source_file_path: str, destination_file_path: str) -> Shadowstep:
        """Push file to device.

        Args:
            source_file_path: Local file path to push.
            destination_file_path: Destination path on device.

        Returns:
            Shadowstep: Self for method chaining.

        """
        with Path(source_file_path).open("rb") as file:
            file_data = file.read()
            base64data = base64.b64encode(file_data).decode("utf-8")
        self.driver.push_file(
            destination_path=destination_file_path,
            base64data=base64data,
        )
        return self

    def update_settings(self) -> None:
        """Update Appium driver settings.

        This method updates various Appium driver settings for UiAutomator2.
        For detailed documentation, see:
        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/README.md?plain=1#L304

        Note: This docstring contains long lines due to API documentation requirements.
        """
        # TODO move to separate class with transparent settings selection (enum?)  # noqa: TD002, TD003, TD004, FIX002
        self.driver.update_settings(settings={"enableMultiWindows": True})
