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
from typing import TYPE_CHECKING, Any, Literal

from typing_extensions import Self

from shadowstep.decorators.common_decorators import log_debug
from shadowstep.decorators.shadowstep_decorators import fail_safe_shadowstep
from shadowstep.element.element import Element
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException
from shadowstep.image.image import ShadowstepImage
from shadowstep.locator import LocatorConverter
from shadowstep.navigator.navigator import PageNavigator
from shadowstep.shadowstep_base import ShadowstepBase, WebDriverSingleton
from shadowstep.ui_automator.mobile_commands import MobileCommands

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
        self.converter: LocatorConverter = LocatorConverter()
        self.mobile_commands: MobileCommands = MobileCommands()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = True
        self.timeout = 10

    # ------------------ navigator ------------------

    @log_debug()
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

    @log_debug()
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

    # ----------------------- element -----------------------

    @log_debug()
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
        return Element(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
            shadowstep=self,
        )

    @log_debug()
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

    # ------------------------------- image -------------------------------

    @log_debug()
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
        return ShadowstepImage(
            image=image,
            base=self,
            threshold=threshold,
            timeout=timeout,
        )

    @log_debug()
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
        return [
            ShadowstepImage(
                image=image,
                base=self,
                threshold=threshold,
                timeout=timeout,
            ),
        ]

    # ------------------------- schedule -------------------------

    @log_debug()
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

    @log_debug()
    def get_action_history(self, name: str) -> ActionHistory:
        """Fetch the execution history for the named action.

        Args:
            name: Same name as used in schedule_action.

        Returns:
            ActionHistory — convenient wrapper over JSON response.

        """
        # shadowstep/scheduled_actions
        raise NotImplementedError

    @log_debug()
    def unschedule_action(self, name: str) -> ActionHistory:
        """Unschedule the action and return its final history.

        Args:
            name: Same name as used in schedule_action.

        Returns:
            ActionHistory — history of all executions until cancellation.

        """
        # shadowstep/scheduled_actions
        raise NotImplementedError

    # ------------------------- logcat -------------------------

    @log_debug()
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

    @log_debug()
    def stop_logcat(self) -> None:
        """Stop the logcat recording.

        This method stops the currently running logcat recording process.

        """
        self._logcat.stop()

    # ------------------------- actions ---------------------------------

    # Override
    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def tap(self, x: int, y: int, duration: int | None = None) -> Shadowstep:
        """Tap at specified coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.
            duration: Tap duration in milliseconds.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.driver.tap([(x, y)], duration or 100)
        return self

    # ------------------------- mobile commands -------------------------

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def click(self, x: int, y: int) -> Shadowstep:
        """Perform a click gesture at the given coordinates.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-clickgesture

        Args:
            x (int): X-coordinate of the click.
            y (int): Y-coordinate of the click.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.mobile_commands.click_gesture(
            {"x": x, "y": y},
        )
        return self

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def long_click(self, x: int, y: int, duration: int) -> Shadowstep:
        """Perform a long click gesture at the given coordinates.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-longclickgesture

        Args:
            x (int): X-coordinate of the click.
            y (int): Y-coordinate of the click.
            duration (int): Duration in milliseconds (default: 500). Must be ≥ 0.

        Returns:
            Shadowstep: Self for method chaining.

        """
        if duration < 0:
            msg = f"Duration must be non-negative, got {duration}"
            raise ValueError(msg)
        self.mobile_commands.long_click_gesture(
            {"x": x, "y": y, "duration": duration},
        )
        return self

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def double_click(self, x: int, y: int) -> Shadowstep:
        """Perform a double click gesture at the given coordinates.

        Documentation: https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-doubleclickgesture

        Args:
            x (int): X-coordinate of the click.
            y (int): Y-coordinate of the click.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.mobile_commands.double_click_gesture(
            {"x": x, "y": y},
        )
        return self

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
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

        """
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

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def fling(  # noqa: PLR0913
        self,
        left: int,
        top: int,
        width: int,
        height: int,
        direction: Literal["up", "down", "left", "right"],
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

        """
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

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
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

        """
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

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
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

        """
        if not (0.0 < percent <= 1.0):
            error_msg = f"Percent must be between 0 and 1, got {percent}"
            raise ValueError(error_msg)
        if speed < 0:
            error_msg = f"Speed must be non-negative, got {speed}"
            raise ValueError(error_msg)
        self.mobile_commands.pinch_close_gesture(
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

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def swipe(  # noqa: PLR0913
        self,
        left: int,
        top: int,
        width: int,
        height: int,
        direction: Literal["up", "down", "left", "right"],
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

        """
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

    @log_debug()
    def swipe_right_to_left(self) -> Shadowstep:
        """Perform a full-width horizontal swipe from right to left.

        Returns:
            Shadowstep: Self for method chaining.

        """
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

    @log_debug()
    def swipe_left_to_right(self) -> Shadowstep:
        """Perform a full-width horizontal swipe from left to right.

        Returns:
            Shadowstep: Self for method chaining.

        """
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

    @log_debug()
    def swipe_top_to_bottom(self, percent: float = 1.0, speed: int = 5000) -> Shadowstep:
        """Perform a full-height vertical swipe from top to bottom.

        Returns:
            Shadowstep: Self for method chaining.

        """
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

    @log_debug()
    def swipe_bottom_to_top(self, percent: float = 1.0, speed: int = 5000) -> Shadowstep:
        """Perform a full-height vertical swipe from bottom to top.

        Returns:
            Shadowstep: Self for method chaining.

        """
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

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
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

        """
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

    @log_debug()
    def scroll_to_element(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        max_swipes: int = 30,
    ) -> Element:
        """Scroll to find and return a specific element.

        Args:
            locator: Element locator to search for.
            max_swipes: Maximum number of swipe attempts (default: 30).

        Returns:
            Element: Found element instance.

        """
        root = Element(
            locator=("xpath", "//*"),
            shadowstep=self,
        )
        return root.scroll_to_element(locator, max_swipes)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def exec_emu_console_command(
        self,
        command: str,
        exec_timeout: int = 60000,
        conn_timeout: int = 5000,
        init_timeout: int = 5000,
    ) -> None:  # real signature unknown
        """Execute mobile: execEmuConsoleCommand command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-execemuconsolecommand

        Description:
            Executes a command through emulator telnet console interface and returns its output. The emulator_console server feature must be enabled in order to use this method.

        Args:
            command (string): The actual command to execute. See Android Emulator Console Guide for more details on available commands. Required. Example: help-verbose
            exec_timeout (number): Timeout used to wait for a server reply to the given command in milliseconds. Defaults to 60000 ms. Optional. Example: 100000
            conn_timeout (number): Console connection timeout in milliseconds. Defaults to 5000 ms. Optional. Example: 10000
            init_timeout (number): Telnet console initialization timeout in milliseconds (the time between establishing the connection and receiving the command prompt). Defaults to 5000 ms. Optional. Example: 10000

        Returns:
            Any (?): result of script execution

        """
        params = {
            "command": command,
            "execTimeout": exec_timeout,
            "connTimeout": conn_timeout,
            "initTimeout": init_timeout,
        }
        return self.mobile_commands.exec_emu_console_command(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def deep_link(
        self,
        url: str,
        package: str | None = None,
        wait_for_launch: bool = True,  # noqa: FBT001, FBT002
    ) -> None:  # real signature unknown
        """Execute mobile: deepLink command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-deeplink

        Description:
            Start URI that may take users directly to the specific content in the app. Read Reliably Opening Deep Links Across Platforms and Devices for more details.

        Args:
            url (string): The URL to start. Required. Example: theapp://login/
            package (string): The name of the package to start the URI with. This argument was required previously but became optional since version 3.9.3. Optional. Example: 'com.mycompany'
            wait_for_launch (boolean): If false, ADB won't wait for the started activity to return control. Defaults to true. Optional. Example: false

        """
        params = {
            "url": url,
            "package": package,
            "waitForLaunch": wait_for_launch,
        }
        return self.mobile_commands.deep_link(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def deviceidle(self, action: str, packages: str | list[str]) -> None:  # real signature unknown
        """Execute mobile: deviceidle command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-deviceidle

        Description:
            This is a wrapper around the 'adb shell dumpsys deviceidle' interface. For more details, see *Diving Into Android 'M' Doze*. This API is available starting from Android 6.

        Args:
            action (string): The name of the action to perform. Supported values: whitelistAdd or whitelistRemove. Required. Example: whitelistAdd
            packages (string or Array<string>): One or more package names to perform the specified action on. Required. Example: 'com.mycompany'

        """
        params = {
            "action": action,
            "packages": packages,
        }
        return self.mobile_commands.deviceidle(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def accept_alert(self, button_label: str | None = None) -> None:  # real signature unknown
        """Execute mobile: acceptAlert command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-acceptalert

        Description:
            Attempts to accept an Android alert. This method may not always be reliable since there is no single standard for how Android alerts appear in the Accessibility representation.

        Args:
            button_label (string): The name or text of the alert button to click in order to accept it. If not provided, the driver will attempt to autodetect the appropriate button. Optional. Example: Accept

        """
        params = {
            "buttonLabel": button_label,
        }
        return self.mobile_commands.accept_alert(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def dismiss_alert(self, button_label: str | None = None) -> None:  # real signature unknown
        """Execute mobile: dismissAlert command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-dismissalert

        Returns:
            Any: result of script execution

        Description:
            Attempts to dismiss an Android alert. This method may not always be reliable since there is no single standard for how Android alerts appear in the Accessibility representation.

        Args:
            button_label (string): The name or text of the alert button to click in order to dismiss it. If not provided, the driver will attempt to autodetect the appropriate button. Optional. Example: Dismiss

        Returns:
            True if the alert was successfully dismissed, otherwise an error is thrown.

        """
        params = {
            "buttonLabel": button_label,
        }
        return self.mobile_commands.dismiss_alert(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def battery_info(self) -> None:  # real signature unknown
        """Execute mobile: batteryInfo command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-batteryinfo

        Description:
            Retrieves the battery information from the device under test.

        Returns:
            A dictionary containing the following entries:
                level (number): Battery level in the range [0.0, 1.0], where 1.0 represents 100% charge. Returns -1 if the value cannot be retrieved from the system. Example: 0.5
                state (number): Battery state. Possible values are:
                    BATTERY_STATUS_UNKNOWN = 1
                    BATTERY_STATUS_CHARGING = 2
                    BATTERY_STATUS_DISCHARGING = 3
                    BATTERY_STATUS_NOT_CHARGING = 4
                    BATTERY_STATUS_FULL = 5
                Returns -1 if the value cannot be retrieved from the system. Example: 4


        """
        return self.mobile_commands.battery_info()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def device_info(self) -> None:  # real signature unknown
        """Execute mobile: deviceInfo command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-deviceinfo

        Description:
            Retrieves information about the device under test, including device model, serial number, network connectivity, and other properties.

        Returns:
            A dictionary containing device properties. For the full list of keys and their corresponding values, refer to:
            https://github.com/appium/appium-uiautomator2-server/blob/master/app/src/main/java/io/appium/uiautomator2/handler/GetDeviceInfo.java

        """
        return self.mobile_commands.device_info()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_device_time(
        self,
        format_specifiers: str | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: getDeviceTime command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getdevicetime

        Description:
            Retrieves the current timestamp of the device.

        Args:
            format_specifiers (string): The set of format specifiers to use for formatting the timestamp. See https://momentjs.com/docs/ for the full list of supported datetime format specifiers. Defaults to 'YYYY-MM-DDTHH:mm:ssZ', which complies with ISO-8601. Optional. Example: 'YYYY-MM-DDTHH:mm:ssZ'

        Returns:
            A string representing the device timestamp formatted according to the given specifiers.

        """
        params = {
            "format": format_specifiers,
        }
        return self.mobile_commands.get_device_time(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def change_permissions(
        self,
        permissions: str | list[str],
        app_package: str | None = None,
        action: str | None = None,
        target: str | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: changePermissions command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-changepermissions

        Description:
            Changes package permissions at runtime on the device under test.

        Args:
            permissions (string or Array<string>): The full name of the permission to be changed or a list of permissions. For standard Android permissions, refer to the Android documentation. If the special value 'all' is passed (available since driver version 2.8.0) and the target is 'pm' (default), the action will be applied to all permissions requested or granted by the 'appPackage'. For the 'appops' target (available since v2.11.0), refer to AppOpsManager.java for supported appops permission names. The 'all' value is not supported for the 'appops' target. Required. Example: ['android.permission.ACCESS_FINE_LOCATION', 'android.permission.BROADCAST_SMS'] or 'all'
            app_package (string): The application package to modify permissions for. Defaults to the package under test. Optional. Example: com.mycompany.myapp
            action (string): The action to perform. For target 'pm', use 'grant' (default) or 'revoke'. For target 'appops', use 'allow' (default), 'deny', 'ignore', or 'default'. Optional. Example: allow
            target (string): The permission management target. Either 'pm' (default) or 'appops' (available since v2.11.0). The 'appops' target requires the adb_shell server security option to be enabled. Optional. Example: appops

        """
        params = {
            "permissions": permissions,
            "appPackage": app_package,
            "action": action,
            "target": target,
        }
        # Remove None values - Appium expects these params to be omitted, not null
        params = {k: v for k, v in params.items() if v is not None}
        return self.mobile_commands.change_permissions(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_permissions(
        self,
        permissions_type: str | None = None,
        app_package: str | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: getPermissions command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getpermissions

        Description:
            Retrieves the runtime permissions list for the specified application package.

        Args:
            permissions_type (string): The type of permissions to retrieve. Possible values are 'denied', 'granted', or 'requested' (default). Optional. Example: granted
            app_package (string): The application package to query permissions from. Defaults to the package under test. Optional. Example: com.mycompany.myapp

        Returns:
            An array of strings, each representing a permission name. The array may be empty if no permissions match the specified type.

        """
        params = {
            "type": permissions_type,
            "appPackage": app_package,
        }
        return self.mobile_commands.get_permissions(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def perform_editor_action(self, action: str) -> None:  # real signature unknown
        """Execute mobile: performEditorAction command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-performeditoraction

        Description:
            Performs an IME (Input Method Editor) action on the currently focused edit element. This emulates the invocation of the onEditorAction callback commonly used in Android development when buttons like Search or Done are pressed on the on-screen keyboard.

        Args:
            action (string): The name or integer code of the editor action to execute. Supported action names are: 'normal', 'unspecified', 'none', 'go', 'search', 'send', 'next', 'done', 'previous'. See EditorInfo for more details. Required. Example: search

        """
        params = {
            "action": action,
        }
        return self.mobile_commands.perform_editor_action(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def start_screen_streaming(  # noqa: PLR0913
        self,
        width: int | None = None,
        height: int | None = None,
        bit_rate: int = 4000000,
        host: str = "127.0.0.1",
        path_name: str | None = None,
        tcp_port: int = 8094,
        port: int = 8093,
        quality: int = 70,
        consider_rotation: bool = False,  # noqa: FBT001, FBT002
        log_pipeline_details: bool = False,  # noqa: FBT001, FBT002
    ) -> None:  # real signature unknown
        """Execute mobile: startScreenStreaming command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startscreenstreaming

        Description:
            Starts device screen broadcasting by creating an MJPEG server. Multiple calls have no effect unless the previous streaming session is stopped. Requires the adb_screen_streaming feature on the server and GStreamer with gst-plugins-base, gst-plugins-good, and gst-plugins-bad installed and available in PATH on the server machine.

        Args:
            width (number): The scaled width of the device's screen in pixels. If unset, the actual screen width is used. Optional. Example: 768
            height (number): The scaled height of the device's screen in pixels. If unset, the actual screen height is used. Optional. Example: 1024
            bit_rate (number): The video bit rate in bits per second. Default is 4000000 (4 Mb/s). Higher bit rate improves video quality but increases file size. Optional. Example: 1024000
            host (string): The IP address or hostname to start the MJPEG server on. Use 0.0.0.0 to bind to all available interfaces. Default: 127.0.0.1. Optional. Example: 0.0.0.0
            path_name (string): The HTTP request path for the MJPEG server. Should start with a slash. Optional. Example: /myserver
            tcp_port (number): The internal TCP port for MJPEG broadcast on the loopback interface (127.0.0.1). Default: 8094. Optional. Example: 5024
            port (number): The port number for the MJPEG server. Default: 8093. Optional. Example: 5023
            quality (number): The JPEG quality for streamed images, in range [1, 100]. Default: 70. Optional. Example: 80
            consider_rotation (boolean): If true, GStreamer adjusts image dimensions for both landscape and portrait orientations. Default: false. Optional. Example: false
            log_pipeline_details (boolean): Whether to log GStreamer pipeline events to standard output. Useful for debugging. Default: false. Optional. Example: true

        Returns:
            True if the MJPEG server was successfully started; otherwise, an error is thrown.

        """
        params = {
            "width": width,
            "height": height,
            "bitRate": bit_rate,
            "host": host,
            "pathname": path_name,
            "tcpPort": tcp_port,
            "port": port,
            "quality": quality,
            "considerRotation": consider_rotation,
            "logPipelineDetails": log_pipeline_details,
        }
        return self.mobile_commands.start_screen_streaming(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def stop_screen_streaming(self) -> None:  # real signature unknown
        """Execute mobile: stopScreenStreaming command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-stopscreenstreaming

        Description:
            Stop the previously started screen streaming. If no screen streaming server has been started then nothing is done.

        """
        return self.mobile_commands.stop_screen_streaming()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_notifications(self) -> None:  # real signature unknown
        """Execute mobile: getNotifications command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getnotifications

        Description:
            Retrieves Android notifications via Appium Settings helper. Appium Settings app itself must be manually granted to access notifications under device Settings in order to make this feature working. Different vendors might require more than just the normal Notification permissions at the usual Apps menu. Try to look in places like Privacy menus if you are getting zero items retrieved while expecting some results.

            Appium Settings keeps up to 100 notifications in an internal buffer, including both active notifications and those that appeared while the service was running. Newly appeared notifications are added to the head of the array. Each notification includes an `isRemoved` flag indicating whether it has been removed. For more details, see:
            https://developer.android.com/reference/android/service/notification/StatusBarNotification
            https://developer.android.com/reference/android/app/Notification.html

        Returns:
            A dictionary containing the notifications, for example:

            {
               "statusBarNotifications":[
                 {
                   "isGroup":false,
                   "packageName":"io.appium.settings",
                   "isClearable":false,
                   "isOngoing":true,
                   "id":1,
                   "tag":null,
                   "notification":{
                     "title":null,
                     "bigTitle":"Appium Settings",
                     "text":null,
                     "bigText":"Keep this service running, so Appium for Android can properly interact with several system APIs",
                     "tickerText":null,
                     "subText":null,
                     "infoText":null,
                     "template":"android.app.Notification$BigTextStyle"
                   },
                   "userHandle":0,
                   "groupKey":"0|io.appium.settings|1|null|10133",
                   "overrideGroupKey":null,
                   "postTime":1576853518850,
                   "key":"0|io.appium.settings|1|null|10133",
                   "isRemoved":false
                 }
               ]
            }

        """
        return self.mobile_commands.get_notifications()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def open_notifications(self) -> None:  # real signature unknown
        """Execute mobile: openNotifications command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-opennotifications

        Description:
            Opens notifications drawer on the device under test. Does nothing if the drawer is already opened.

        """
        return self.mobile_commands.open_notifications()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def list_sms(self, max_number: int = 100) -> None:  # real signature unknown
        r"""Execute mobile: listSms command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-listsms

        Description:
            Retrieves the list of the most recent SMS messages via the Appium Settings helper. Messages are sorted by date in descending order (most recent first).

        Args:
            max_number (number): The maximum number of recent messages to retrieve. Defaults to 100. Optional. Example: 10

        Returns:
            A dictionary containing the retrieved SMS messages, for example:

            {
               "items":[
                 {
                   "id":"2",
                   "address":"+123456789",
                   "person":null,
                   "date":"1581936422203",
                   "read":"0",
                   "status":"-1",
                   "type":"1",
                   "subject":null,
                   "body":"\"text message2\"",
                   "serviceCenter":null
                 },
                 {
                   "id":"1",
                   "address":"+123456789",
                   "person":null,
                   "date":"1581936382740",
                   "read":"0",
                   "status":"-1",
                   "type":"1",
                   "subject":null,
                   "body":"\"text message\"",
                   "serviceCenter":null
                 }
               ],
               "total":2
            }

        """
        params = {
            "max": max_number,
        }
        return self.mobile_commands.list_sms(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def type(self, text: str) -> None:  # real signature unknown
        """Execute mobile: type command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-type

        Description:
            Types the given Unicode string into the currently focused input field. Unlike sendKeys, this method emulates real typing as if performed from an on-screen keyboard and properly supports Unicode characters. The input field must already have focus before calling this method.

        Args:
            text (string): The text to type. Required. Example: testing

        """
        params = {
            "text": text,
        }
        return self.mobile_commands.type(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def sensor_set(self, sensor_type: str, value: str) -> None:  # real signature unknown
        """Execute mobile: sensorSet command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-sensorset

        Description:
            Emulates changing sensor values on the connected Android emulator. This extension does not work on real devices. Use the emulator console or check adb-emu-commands.js (SENSORS object) to see supported sensor types and acceptable value formats.

        Args:
            sensor_type (string): The type of sensor to emulate. Required. Example: light
            value (string): The value to set for the sensor. Check the emulator console output for acceptable formats. Required. Example: 50

        """
        params = {
            "sensorType": sensor_type,
            "value": value,
        }
        return self.mobile_commands.sensor_set(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def delete_file(self, remote_path: str) -> None:  # real signature unknown
        """Execute mobile: deleteFile command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-deletefile

        Description:
            Deletes a file on the remote device. The file can be a standard file on the filesystem or a file inside an application bundle.

        Args:
            remote_path (string): The full path to the remote file or a file inside an application bundle. Required. Example: /sdcard/myfile.txt or @my.app.id/path/in/bundle

        """
        params = {
            "remotePath": remote_path,
        }
        return self.mobile_commands.delete_file(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def is_app_installed(
        self,
        app_id: str,
        user: int | str | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: isAppInstalled command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-isappinstalled

        Description:
            Verifies whether an application is installed on the device under test.

        Args:
            app_id (string): The identifier of the application package to be checked. Required. Example: my.app.id
            user (number or string): The user ID for which the package installation is checked. Defaults to the current user if not provided. Optional. Example: 1006

        Returns:
            True if the application is installed for the specified user; otherwise, False.

        """
        params = {
            "appId": app_id,
            "user": user,
        }
        return self.mobile_commands.is_app_installed(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def query_app_state(self, app_id: str) -> None:  # real signature unknown
        """Execute mobile: queryAppState command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-queryappstate

        Description:
            Queries the current state of the specified application on the device under test.

        Args:
            app_id (string): The identifier of the application package to be checked. Required. Example: my.app.id

        Returns:
            An integer representing the current state of the app:
                0: The app is not installed
                1: The app is installed but not running
                3: The app is running in the background
                4: The app is running in the foreground

        """
        params = {
            "appId": app_id,
        }
        return self.mobile_commands.query_app_state(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def activate_app(self, app_id: str) -> None:  # real signature unknown
        """Execute mobile: activateApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-activateapp

        Description:
            Activates the specified application on the device under test, or launches it if it is not already running. This simulates a user clicking the app icon on the device dashboard.

        Args:
            app_id (string): The identifier of the application package to be activated. Required. Example: my.app.id

        """
        params = {
            "appId": app_id,
        }
        return self.mobile_commands.activate_app(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def remove_app(
        self,
        app_id: str,
        timeout: int | None = None,
        keep_data: bool = False,  # noqa: FBT001, FBT002
    ) -> None:  # real signature unknown
        """Execute mobile: removeApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-removeapp

        Description:
            Uninstalls the specified application from the device under test if it is installed. If the application is not present, the call is ignored.

        Args:
            app_id (string): The identifier of the application package to be removed. Required. Example: my.app.id
            timeout (number): The time in milliseconds to wait until the app is terminated. Optional. Default is 20000 ms. Example: 1500
            keep_data (boolean): If set to true, the application data and cache folders are preserved after uninstall. Optional. Default is false. Example: true

        Returns:
            bool: True if the application was found and successfully removed; False otherwise.

        """
        params = {
            "appId": app_id,
            "timeout": timeout,
            "keepData": keep_data,
        }
        return self.mobile_commands.remove_app(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def terminate_app(self, app_id: str, timeout: int = 500) -> None:  # real signature unknown
        """Execute mobile: terminateApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-terminateapp

        Description:
            Terminates the specified application on the device under test and waits until the app is fully stopped, up to the provided timeout. If the timeout is zero or negative (since UIAutomator driver 2.9.0), the app state check is skipped, which is useful when the app may automatically restart.

        Args:
            app_id (string): The identifier of the application package to be terminated. Required. Example: my.app.id
            timeout (number): Maximum time in milliseconds to wait until the app is terminated. Optional. Default is 500 ms. Example: 1500

        Returns:
            bool: True if the application was successfully terminated; False otherwise.

        """
        params = {
            "appId": app_id,
            "timeout": timeout,
        }
        return self.mobile_commands.terminate_app(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def install_app(  # noqa: PLR0913
        self,
        app_path: str,
        timeout: int = 6000,
        allow_test_packages: bool = False,  # noqa: FBT001, FBT002
        use_sdcard: bool = False,  # noqa: FBT001, FBT002
        grant_permissions: bool = False,  # noqa: FBT001, FBT002
        replace: bool = True,  # noqa: FBT001, FBT002
        check_version: bool = False,  # noqa: FBT001, FBT002
    ) -> None:  # real signature unknown
        """Execute mobile: installApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-installapp

        Description:
            Installs the specified application package (.apk) on the device under test. May raise INSTALL_FAILED_VERSION_DOWNGRADE if the installed version is lower than the existing version on the device.

        Args:
            app_path (string): The local path to the .apk file(s) on the server filesystem or a remote URL. Required. Example: /app/path.apk
            timeout (number): Maximum time in milliseconds to wait for the installation to complete. Optional. Default is 6000 ms. Example: 120000
            allow_test_packages (bool): Whether to allow installation of test packages. Optional. Default is False. Example: True
            use_sdcard (bool): Whether to install the app on the SD card instead of device memory. Optional. Default is False. Example: True
            grant_permissions (bool): Automatically grant all permissions requested in the app manifest after installation (Android 6+). Requires targetSdkVersion ≥ 23 and device API level ≥ 23. Optional. Default is False. Example: True
            replace (bool): Whether to upgrade/reinstall the app if it already exists. If False, throws an error instead. Optional. Default is True. Example: False
            check_version (bool): Skip installation if the device already has a greater or equal app version, avoiding INSTALL_FAILED_VERSION_DOWNGRADE errors. Optional. Default is False. Example: True

        """
        params = {
            "appPath": app_path,
            "timeout": timeout,
            "allowTestPackages": allow_test_packages,
            "useSdcard": use_sdcard,
            "grantPermissions": grant_permissions,
            "replace": replace,
            "checkVersion": check_version,
        }
        return self.mobile_commands.install_app(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def clear_app(self, app_id: str) -> None:  # real signature unknown
        """Execute mobile: clearApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-clearapp

        Description:
            Deletes all data associated with the specified application package on the device under test. Internally calls `adb shell pm clear`. The app must exist, be accessible, and not running for this command to succeed.

        Args:
            app_id (string): The identifier of the application package to be cleared. Required. Example: my.app.id

        Returns:
            Stdout of the corresponding adb command. An error is thrown if the operation fails.

        """
        params = {
            "appId": app_id,
        }
        return self.mobile_commands.clear_app(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def start_activity(  # noqa: PLR0913
        self,
        intent: str,
        user: int | str | None = None,
        wait: bool = False,  # noqa: FBT001, FBT002
        stop: bool = False,  # noqa: FBT001, FBT002
        windowing_mode: int | None = None,
        activity_type: int | None = None,
        action: str | None = None,
        uri: str | None = None,
        mime_type: str | None = None,
        identifier: str | None = None,
        categories: str | list[str] | None = None,
        component: str | None = None,
        package: str | None = None,
        extras: list[list[str]] | None = None,
        flags: str | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: startActivity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startactivity

        Description:
            Starts the specified activity intent on the device under test. Internally invokes `am start` / `am start-activity` command. This method extends the functionality of the Start Activity app management API.

        Args:
            intent (string): Full name of the activity intent to start. Required. Example: com.some.package.name/.YourActivityClassName
            user (number|string): User ID for which the service is started. Optional. Defaults to current user. Example: 1006
            wait (boolean): Block the method call until the Activity Manager process returns control to the system. Optional. Default is false. Example: true
            stop (boolean): Force stop the target app before starting the activity. Optional. Default is false. Example: true
            windowing_mode (integer): Windowing mode to launch the activity into. Optional. Example: 1
            activity_type (integer): Activity type to launch the activity as. Optional. Example: 1
            action (string): Action name for the Activity Manager's `-a` argument. Optional. Example: android.intent.action.MAIN
            uri (string): Unified Resource Identifier for the `-d` argument. Optional. Example: https://appium.io
            mime_type (string): Mime type for the `-t` argument. Optional. Example: application/json
            identifier (string): Optional identifier for the `-i` argument. Optional. Example: my_identifier
            categories (string|Array[string]): One or more category names for the `-c` argument. Optional. Example: ['android.intent.category.LAUNCHER']
            component (string): Component name for the `-n` argument. Optional. Example: com.myapp/com.myapp.SplashActivity
            package (string): Package name for the `-p` argument. Optional. Example: com.myapp
            extras (Array[Array[string]]): Optional intent arguments. Each subarray contains value type, key, and value. Supported types: s, sn, z, i, l, f, u, cn, ia, ial, la, lal, fa, fal, sa, sal. Optional. Example: [['s', 'varName1', 'My String1'], ['ia', 'arrName', '1,2,3,4']]
            flags (string): Intent startup-specific flags as a hexadecimal string. Optional. Example: 0x10200000

        Returns:
            The actual stdout of the underlying `am` command. An error is thrown if the operation fails.

        """
        params = {
            "intent": intent,
            "user": user,
            "wait": wait,
            "stop": stop,
            "windowingMode": windowing_mode,
            "activityType": activity_type,
            "action": action,
            "uri": uri,
            "mimeType": mime_type,
            "identifier": identifier,
            "categories": categories,
            "component": component,
            "package": package,
            "extras": extras,
            "flags": flags,
        }
        return self.mobile_commands.start_activity(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def start_service(  # noqa: PLR0913
        self,
        intent: str | None = None,
        user: int | str | None = None,
        foreground: bool = False,  # noqa: FBT001, FBT002
        action: str | None = None,
        uri: str | None = None,
        mime_type: str | None = None,
        identifier: str | None = None,
        categories: str | list[str] | None = None,
        component: str | None = None,
        package: str | None = None,
        extras: list[list[str]] | None = None,
        flags: str | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: startService command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startservice

        Description:
            Starts the specified service intent on the device under test. Internally invokes `am startservice` or `am start-service` command.

        Args:
            intent (string): Full name of the service intent to start. Optional. Example: com.some.package.name/.YourServiceSubClassName
            user (number|string): User ID for which the service is started. Optional. Defaults to current user. Example: 1006
            foreground (boolean): Start the service as a foreground service (only works on Android 8+). Optional. Default is false. Example: true
            action (string): See documentation for `startActivity` extension. Optional. Example: android.intent.action.MAIN
            uri (string): See documentation for `startActivity` extension. Optional. Example: https://appium.io
            mime_type (string): See documentation for `startActivity` extension. Optional. Example: application/json
            identifier (string): See documentation for `startActivity` extension. Optional. Example: my_identifier
            categories (string|Array[string]): See documentation for `startActivity` extension. Optional. Example: ['com.myapp/com.myapp.SplashActivity']
            component (string): See documentation for `startActivity` extension. Optional. Example: android.intent.category.LAUNCHER
            package (string): See documentation for `startActivity` extension. Optional. Example: com.myapp
            extras (Array[Array[string]]): Optional intent arguments. Each subarray contains value type, key, and value. See `startActivity` documentation for supported types. Optional. Example: [['s', 'varName1', 'My String1'], ['ia', 'arrName', '1,2,3,4']]
            flags (string): Intent startup-specific flags as a hexadecimal string. See `startActivity` documentation for details. Optional. Example: 0x10200000

        Returns:
            The actual stdout of the underlying `am` command. An error is thrown if the operation fails.

        """
        params = {
            "intent": intent,
            "user": user,
            "foreground": foreground,
            "action": action,
            "uri": uri,
            "mimeType": mime_type,
            "identifier": identifier,
            "categories": categories,
            "component": component,
            "package": package,
            "extras": extras,
            "flags": flags,
        }
        # Remove None values - Appium expects these params to be omitted, not null
        params = {k: v for k, v in params.items() if v is not None}
        return self.mobile_commands.start_service(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def stop_service(  # noqa: PLR0913
        self,
        intent: str | None = None,
        user: int | str | None = None,
        action: str | None = None,
        uri: str | None = None,
        mime_type: str | None = None,
        identifier: str | None = None,
        categories: str | list[str] | None = None,
        component: str | None = None,
        package: str | None = None,
        extras: list[list[str]] | None = None,
        flags: str | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: stopService command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-stopservice

        Description:
            Stops the specified service intent on the device under test. Internally invokes `am stopservice` or `am stop-service` command.

        Args:
            intent (string): Full name of the service intent to stop. Optional. Example: com.some.package.name/.YourServiceSubClassName
            user (number|string): User ID for which the service is stopped. Optional. Defaults to current user. Example: 1006
            action (string): See documentation for `startActivity` extension. Optional. Example: android.intent.action.MAIN
            uri (string): See documentation for `startActivity` extension. Optional. Example: https://appium.io
            mime_type (string): See documentation for `startActivity` extension. Optional. Example: application/json
            identifier (string): See documentation for `startActivity` extension. Optional. Example: my_identifier
            categories (string|Array[string]): See documentation for `startActivity` extension. Optional. Example: ['com.myapp/com.myapp.SplashActivity']
            component (string): See documentation for `startActivity` extension. Optional. Example: android.intent.category.LAUNCHER
            package (string): See documentation for `startActivity` extension. Optional. Example: com.myapp
            extras (Array[Array[string]]): Optional intent arguments. Each subarray contains value type, key, and value. See `startActivity` documentation for supported types. Optional. Example: [['s', 'varName1', 'My String1'], ['ia', 'arrName', '1,2,3,4']]
            flags (string): Intent-specific flags as a hexadecimal string. See `startActivity` documentation for details. Optional. Example: 0x10200000

        Returns:
            The actual stdout of the underlying `am` command. An error is thrown if the operation fails.

        """
        params = {
            "intent": intent,
            "user": user,
            "action": action,
            "uri": uri,
            "mimeType": mime_type,
            "identifier": identifier,
            "categories": categories,
            "component": component,
            "package": package,
            "extras": extras,
            "flags": flags,
        }
        # Remove None values - Appium expects these params to be omitted, not null
        params = {k: v for k, v in params.items() if v is not None}
        return self.mobile_commands.stop_service(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def broadcast(  # noqa: PLR0913
        self,
        intent: str | None = None,
        user: int | str | None = None,
        receiver_permission: str | None = None,
        allow_background_activity_starts: bool = False,  # noqa: FBT001, FBT002
        action: str | None = None,
        uri: str | None = None,
        mime_type: str | None = None,
        identifier: str | None = None,
        categories: str | list[str] | None = None,
        component: str | None = None,
        package: str | None = None,
        extras: list[list[str]] | None = None,
        flags: str | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: broadcast command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-broadcast

        Description:
            Sends a broadcast Intent on the device under test. Internally invokes the `am broadcast` command.

        Args:
            intent (string): Full name of the intent to broadcast. Optional. Example: com.some.package.name/.YourIntentClassName
            user (number|string): Specify which user to send to; possible values are 'all', 'current', or a numeric user ID. Optional. Example: current
            receiver_permission (string): Require the receiver to hold the given permission. Optional. Example: android.permission.READ_PROFILE
            allow_background_activity_starts (boolean): Whether the receiver can start activities even if in the background. Optional. Default: false. Example: true
            action (string): See documentation for `startActivity` extension. Optional. Example: android.intent.action.MAIN
            uri (string): See documentation for `startActivity` extension. Optional. Example: https://appium.io
            mime_type (string): See documentation for `startActivity` extension. Optional. Example: application/json
            identifier (string): See documentation for `startActivity` extension. Optional. Example: my_identifier
            categories (string|Array[string]): See documentation for `startActivity` extension. Optional. Example: ['com.myapp/com.myapp.SplashActivity']
            component (string): See documentation for `startActivity` extension. Optional. Example: android.intent.category.LAUNCHER
            package (string): See documentation for `startActivity` extension. Optional. Example: com.myapp
            extras (Array[Array[string]]): Optional intent arguments. Each subarray contains value type, key, and value. See `startActivity` documentation for supported types. Optional. Example: [['s', 'varName1', 'My String1'], ['ia', 'arrName', '1,2,3,4']]
            flags (string): Intent-specific flags as a hexadecimal string. See `startActivity` documentation for details. Optional. Example: 0x10200000

        Returns:
            The actual stdout of the underlying `am` command. An error is thrown if the operation fails.

        """
        params = {
            "intent": intent,
            "user": user,
            "receiverPermission": receiver_permission,
            "allowBackgroundActivityStarts": allow_background_activity_starts,
            "action": action,
            "uri": uri,
            "mimeType": mime_type,
            "identifier": identifier,
            "categories": categories,
            "component": component,
            "package": package,
            "extras": extras,
            "flags": flags,
        }
        return self.mobile_commands.broadcast(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_contexts(self, wait_for_webview_ms: int = 0) -> None:  # real signature unknown
        r"""Execute mobile: getContexts command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getcontexts

        Description:
            Retrieves a mapping of WebViews on the device under test based on Chrome DevTools Protocol (CDP) endpoints. This allows interaction with WebViews in hybrid applications.

        Args:
            wait_for_webview_ms (number): Maximum time in milliseconds to wait for WebView(s) to appear. If set to 0 (default), the WebView availability is checked only once. Optional. Example: 10000

        Returns:
            A JSON object representing the WebViews mapping. Example structure:

            {
                "proc": "@webview_devtools_remote_22138",
                "webview": "WEBVIEW_22138",
                "info": {
                    "Android-Package": "io.appium.settings",
                    "Browser": "Chrome/74.0.3729.185",
                    "Protocol-Version": "1.3",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 10; Android SDK built for x86 Build/QSR1.190920.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.185 Mobile Safari/537.36",
                    "V8-Version": "7.4.288.28",
                    "WebKit-Version": "537.36 (@22955682f94ce09336197bfb8dffea991fa32f0d)",
                    "webSocketDebuggerUrl": "ws://127.0.0.1:10900/devtools/browser"
                },
                "pages": [
                    {
                        "description": "{\"attached\":true,\"empty\":false,\"height\":1458,\"screenX\":0,\"screenY\":336,\"visible\":true,\"width\":1080}",
                        "devtoolsFrontendUrl": "http://chrome-devtools-frontend.appspot.com/serve_rev/@22955682f94ce09336197bfb8dffea991fa32f0d/inspector.html?ws=127.0.0.1:10900/devtools/page/27325CC50B600D31B233F45E09487B1F",
                        "id": "27325CC50B600D31B233F45E09487B1F",
                        "title": "Releases · appium/appium · GitHub",
                        "type": "page",
                        "url": "https://github.com/appium/appium/releases",
                        "webSocketDebuggerUrl": "ws://127.0.0.1:10900/devtools/page/27325CC50B600D31B233F45E09487B1F"
                    }
                ],
                "webviewName": "WEBVIEW_com.io.appium.setting"
            }

        """
        params = {
            "waitForWebviewMs": wait_for_webview_ms,
        }
        return self.mobile_commands.get_contexts(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def install_multiple_apks(
        self,
        apks: list[str],
        options: Any,
    ) -> None:  # real signature unknown
        """Execute mobile: installMultipleApks command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-installmultipleapks

        Description:
            Installs multiple application packages on the device under test using the adb `install-multiple` option. Each APK will be installed in a single command, allowing options like granting permissions or partial installation.

        Args:
            apks (Array<string>): List of full paths or URLs to the APK files to be installed. Required. Example: ['/path/to/local.apk', 'https://github.com/appium/ruby_lib_core/blob/master/test/functional/app/api.apk.zip?raw=true']
            options (object): Installation options. Optional. Supported keys:
                - grantPermissions (boolean): If true, automatically grant all requested permissions (-g). Example: true
                - allowTestPackages (boolean): Corresponds to -t flag. Example: true
                - useSdcard (boolean): Corresponds to -s flag. Example: true
                - replace (boolean): Corresponds to -r flag; replaces existing app. Default is true. Example: false
                - partialInstall (boolean): Corresponds to -p flag for partial installation. Example: true

        Returns:
            The stdout of the corresponding adb install-multiple command. An error is thrown if the installation fails.

        """
        params = {
            "apks": apks,
            "options": options,
        }
        return self.mobile_commands.install_multiple_apks(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def lock(self, seconds: int | str | None = None) -> None:  # real signature unknown
        """Execute mobile: lock command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-lock

        Description:
            Locks the device using a simple lock (e.g., without a password). Optionally, the device can be automatically unlocked after a specified number of seconds.

        Args:
            seconds (number|string): The number of seconds after which the device should be automatically unlocked. If set to 0 or left empty, the device must be unlocked manually. Optional. Example: 10

        """
        params = {
            "seconds": seconds,
        }
        return self.mobile_commands.lock(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def unlock(
        self,
        key: str,
        unlock_type: str,
        strategy: str | None = None,
        timeout_ms: int | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: unlock command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-unlock

        Description:
            Unlocks the device if it is currently locked. No operation is performed if the device is not locked.

        Args:
            key (string): The unlock key to use. See the documentation for the `appium:unlockKey` capability for more details. Required. Example: "12345"
            unlock_type (string): The unlock type. See the documentation for the `appium:unlockType` capability for more details. Required. Example: "password"
            strategy (string): The unlock strategy to apply. See the documentation for the `appium:unlockStrategy` capability for more details. Optional. Example: "uiautomator"
            timeout_ms (number): The timeout in milliseconds to wait for a successful unlock. See the documentation for the `appium:unlockSuccessTimeout` capability. Optional. Example: 5000

        """
        params = {
            "key": key,
            "type": unlock_type,
            "strategy": strategy,
            "timeoutMs": timeout_ms,
        }
        return self.mobile_commands.unlock(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def is_locked(self) -> None:  # real signature unknown
        """Execute mobile: isLocked command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-islocked

        Description:
            Determine whether the device is locked.

        Returned Result
            Either true or false

        """
        return self.mobile_commands.is_locked()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def set_geolocation(  # noqa: PLR0913
        self,
        latitude: int,
        longitude: int,
        altitude: int | None = None,
        satellites: int | None = None,
        speed: int | None = None,
        bearing: int | None = None,
        accuracy: int | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: setGeolocation command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-setgeolocation

        Description:
            Sets the emulated geolocation coordinates on the device under test. Supports both real devices and emulators, with additional parameters available depending on the device type.

        Args:
            latitude (number): Latitude value to set. Required. Example: 32.456
            longitude (number): Longitude value to set. Required. Example: 32.456
            altitude (number): Altitude value in meters. Optional. Defaults to 0. Example: 5.678
            satellites (number): Number of satellites being tracked (1-12). Only available for emulators. Optional. Example: 2
            speed (number): Speed in meters per second. Valid value is 0.0 or greater. Optional. Example: 30.0
            bearing (number): Bearing in degrees at the time of this location. Only available for real devices. Valid range is [0, 360). Optional. Example: 10
            accuracy (number): Horizontal accuracy in meters. Only available for real devices. Valid value is 0.0 or greater. Optional. Example: 10.0

        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "satellites": satellites,
            "speed": speed,
            "bearing": bearing,
            "accuracy": accuracy,
        }
        return self.mobile_commands.set_geolocation(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_geolocation(
        self,
        latitude: int,
        longitude: int,
        altitude: int,
    ) -> None:  # real signature unknown
        """Execute mobile: getGeolocation command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getgeolocation

        Description:
            Retrieves the current geolocation coordinates from the device under test. If the coordinates are mocked or emulated, the mocked/emulated values will be returned.

        Returns:
            A dictionary containing the current geolocation:

            latitude (number): Latitude value. Example: 32.456
            longitude (number): Longitude value. Example: 32.456
            altitude (number): Altitude value in meters. Example: 5.678

        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
        }
        # Remove None values - Appium expects these params to be omitted, not null
        params = {k: v for k, v in params.items() if v is not None}  # type: ignore[reportUnnecessaryComparison]
        return self.mobile_commands.get_geolocation(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def reset_geolocation(self) -> None:  # real signature unknown
        """Execute mobile: resetGeolocation command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-resetgeolocation

        """
        return self.mobile_commands.reset_geolocation()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def refresh_gps_cache(self, timeout_ms: int = 20000) -> None:  # real signature unknown
        """Execute mobile: refreshGpsCache command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-refreshgpscache

        Description:
            Sends a request to refresh the GPS cache on the device under test. By default, location tracking is configured for low battery consumption, so this method may need to be called periodically to get updated geolocation values if the device's actual or mocked location changes frequently. This feature works only if Google Play Services are installed on the device. If the device uses the vanilla LocationManager, the device API level must be 30 (Android R) or higher.

        Args:
            timeout_ms (number): Maximum number of milliseconds to wait for GPS cache refresh. If the API call does not confirm a successful cache refresh within this timeout, an error is thrown. A value of 0 or negative skips waiting and does not check for errors. Default is 20000 ms. Example: 60000

        Returns:
            The actual command output. An error is thrown if the GPS cache refresh fails or the timeout is exceeded.

        """
        params = {
            "timeoutMs": timeout_ms,
        }
        return self.mobile_commands.refresh_gps_cache(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def start_media_projection_recording(
        self,
        resolution: str | None = None,
        max_duration_sec: int | None = None,
        priority: str | None = None,
        filename: str | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: startMediaProjectionRecording command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startmediaprojectionrecording

        Description:
            Starts a new recording of the device screen and audio using the Media Projection API. This API is available since Android 10 (API level 29) and allows high-quality recording. Video and audio encoding is handled by Android, and recording is performed via the Appium Settings helper.

        Args:
            resolution (string): The resolution of the recorded video. Supported values: "1920x1080", "1280x720", "720x480", "320x240", "176x144". Optional. Default depends on the device, usually Full HD "1920x1080". Example: "1280x720"
            max_duration_sec (number): Maximum duration of the recording in seconds. Optional. Default is 900 seconds (15 minutes). Example: 300
            priority (string): Recording thread priority. Optional. Default is "high". Can be set to "normal" or "low" to reduce performance impact. Example: "low"
            filename (string): Name of the output video file. Must end with ".mp4". Optional. If not provided, the current timestamp is used. Example: "screen.mp4"

        Returns:
            Boolean: True if a new recording has successfully started, False if another recording is currently running.

        """
        params = {
            "resolution": resolution,
            "maxDurationSec": max_duration_sec,
            "priority": priority,
            "filename": filename,
        }
        return self.mobile_commands.start_media_projection_recording(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def is_media_projection_recording_running(
        self,
    ) -> None:  # real signature unknown
        """Execute mobile: isMediaProjectionRecordingRunning command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-ismediaprojectionrecordingrunning

        """
        return self.mobile_commands.is_media_projection_recording_running()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def stop_media_projection_recording(  # noqa: PLR0913
        self,
        remote_path: str | None = None,
        user: str | None = None,
        password: str | None = None,
        method: str | None = None,
        headers: dict[str, str] | None = None,
        file_field_name: str | None = None,
        form_fields: dict[str, str] | list[str] | None = None,
        upload_timeout: int = 240000,
    ) -> None:  # real signature unknown
        """Execute mobile: stopMediaProjectionRecording command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-stopmediaprojectionrecording

        Description:
            Stops the current device recording and retrieves the recently recorded media. If no recording has been started, an error is thrown. If the recording was already finished, the most recent recorded media is returned.

        Args:
            remote_path (string): Remote location to upload the resulting video. Supported protocols: http, https, ftp. If null or empty, the file content is returned Base64-encoded. Optional. Example: "https://myserver.com/upload"
            user (string): Username for remote authentication. Optional. Example: "admin"
            password (string): Password for remote authentication. Optional. Example: "pa$$w0rd"
            method (string): HTTP multipart upload method. Default is "PUT". Optional. Example: "POST"
            headers (Map<string, string>): Additional headers for HTTP(S) uploads. Optional. Example: {"Agent": "007"}
            file_field_name (string): Form field name for file content in HTTP(S) uploads. Default is "file". Optional. Example: "blob"
            form_fields (Map<string, string> or Array<Pair>): Additional form fields for HTTP(S) uploads. Optional. Example: {"name": "yolo.mp4"}
            upload_timeout (number): Maximum time in milliseconds to wait for file upload. Default is 240000 ms. Optional. Example: 30000

        Returns:
            Base64-encoded content of the recorded media file if `remotePath` is falsy or empty. Otherwise, the result depends on the upload response.

        """
        params = {
            "remotePath": remote_path,
            "user": user,
            "pass": password,
            "method": method,
            "headers": headers,
            "fileFieldName": file_field_name,
            "formFields": form_fields,
            "uploadTimeout": upload_timeout,
        }
        return self.mobile_commands.stop_media_projection_recording(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_connectivity(
        self,
        services: str | list[str] | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: getConnectivity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getconnectivity

        Description:
            Returns the connectivity states for various services on the device under test.

        Args:
            services (string or Array<string>): One or more service names to query connectivity for. Supported values: "wifi", "data", "airplaneMode". If not provided, all supported services are returned by default. Optional. Example: ["wifi", "data"]

        Returns:
            A map containing the connectivity state of each requested service. Possible keys include:
                wifi (boolean): True if Wi-Fi is enabled.
                data (boolean): True if mobile data connection is enabled.
                airplaneMode (boolean): True if Airplane Mode is enabled.

        """
        params = {
            "services": services,
        }
        return self.mobile_commands.get_connectivity(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def set_connectivity(
        self,
        wifi: bool = False,  # noqa: FBT001, FBT002
        data: bool = False,  # noqa: FBT001, FBT002
        airplane_mode: bool = False,  # noqa: FBT001, FBT002
    ) -> None:  # real signature unknown
        """Execute mobile: setConnectivity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-setconnectivity

        Description:
            Sets the connectivity state for various services on the device under test. At least one service must be specified. Missing values indicate that the corresponding service state should not be changed.

        Note:
                - Switching Wi-Fi and mobile data states works reliably on emulators for all Android versions. On real devices, proper state switching is supported only from Android 11 onward.
                - The UiAutomator2 REST server app may be terminated or disconnected by Android when using this API, which can cause the driver session to fail. To restore the session, quit it after changing the network state and then reopen it with the noReset capability set to true once connectivity is restored.

        Args:
            wifi (boolean): Whether to enable or disable Wi-Fi. Optional. Example: False
            data (boolean): Whether to enable or disable mobile data. Optional. Example: False
            airplane_mode (boolean): Whether to enable or disable Airplane Mode. Optional. Example: False

        Returns:
            The actual command output. An error is thrown if execution fails.

        """
        params = {
            "wifi": wifi,
            "data": data,
            "airplaneMode": airplane_mode,
        }
        return self.mobile_commands.set_connectivity(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_app_strings(self, language: str | None = None) -> None:  # real signature unknown
        """Execute mobile: getAppStrings command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getappstrings

        Description:
            Retrieves string resources for the specified app language. An error is thrown if the strings cannot be fetched or if no strings exist for the given language abbreviation. Available since driver version 2.15.0.

        Args:
            language (string): The language abbreviation to fetch app strings for. If not provided, strings for the default language on the device under test will be returned. Optional. Example: "fr"

        Returns:
            A dictionary mapping resource identifiers to string values for the given language. An error is thrown if execution fails.

        """
        params = {
            "language": language,
        }
        # Remove None values - Appium expects these params to be omitted, not null
        params = {k: v for k, v in params.items() if v is not None}
        return self.mobile_commands.get_app_strings(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def hide_keyboard(self) -> None:  # real signature unknown
        """Execute mobile: hideKeyboard command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-hidekeyboard

        Description:
            Attempts to hide the on-screen keyboard on the device under test. Throws an exception if the keyboard cannot be hidden. Does nothing if the keyboard is already hidden.

        Returns:
            Boolean: True if the keyboard was successfully hidden, or False if it was already invisible. An error is thrown if execution fails.

        """
        return self.mobile_commands.hide_keyboard()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def is_keyboard_shown(self) -> None:  # real signature unknown
        """Execute mobile: isKeyboardShown command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-iskeyboardshown

        Description:
            Checks whether the system on-screen keyboard is currently visible on the device under test.

        Returns:
            Boolean: True if the keyboard is visible, False otherwise. An error is thrown if execution fails.

        """
        return self.mobile_commands.is_keyboard_shown()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def press_key(
        self,
        keycode: int,
        metastate: int | None = None,
        flags: int | None = None,
        is_long_press: bool = False,  # noqa: FBT001, FBT002
    ) -> None:  # real signature unknown
        """Execute mobile: pressKey command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-presskey

        Description:
            Emulates a single key press event on the device under test using the specified Android key code. Available since driver version 2.17.0.

        Args:
            keycode (number): A valid Android key code representing the key to press. Required. Example: 0x00000099 (KEYCODE_NUMPAD_9)
            metastate (number): An integer in which each bit set to 1 represents a pressed meta key (e.g., SHIFT, ALT). Optional. Example: 0x00000010 (META_ALT_LEFT_ON)
            flags (number): Flags for the key event as defined in KeyEvent documentation. Optional. Example: 0x00000001 (FLAG_WOKE_HERE)
            is_long_press (boolean): Whether to emulate a long key press. False by default. Optional. Example: True

        """
        params = {
            "keycode": keycode,
            "metastate": metastate,
            "flags": flags,
            "isLongPress": is_long_press,
        }
        return self.mobile_commands.press_key(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def background_app(self, seconds: int | None = None) -> None:  # real signature unknown
        """Execute mobile: backgroundApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-backgroundapp

        Description:
            Puts the app under test to the background for a specified duration and optionally restores it afterward. This call is blocking. Available since driver version 2.19.0.

        Args:
            seconds (number): The amount of seconds to wait between putting the app to background and restoring it. Negative values indicate that the app should not be restored (default behavior). Optional. Example: 5

        Returns:
            The actual command output. An error is thrown if the operation fails.

        """
        params = {
            "seconds": seconds,
        }
        return self.mobile_commands.background_app(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_current_activity(self) -> None:  # real signature unknown
        """Execute mobile: getCurrentActivity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getcurrentactivity

        Description:
            Retrieves the name of the currently focused app activity on the device under test. Available since driver version 2.20.

        Returns:
            The activity class name as a string. Could be None if no activity is currently focused.

        """
        return self.mobile_commands.get_current_activity()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_current_package(self) -> None:  # real signature unknown
        """Execute mobile: getCurrentPackage command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getcurrentpackage

        Description:
            Retrieves the package identifier of the currently focused app on the device under test. Available since driver version 2.20.

        Returns:
            The package class name as a string. Could be None if no app is currently focused.

        """
        return self.mobile_commands.get_current_package()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_display_density(self) -> None:  # real signature unknown
        """Execute mobile: getDisplayDensity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getdisplaydensity

        Description:
            Retrieves the display density of the device under test in dots per inch (DPI). Available since driver version 2.21.

        Returns:
            The display density as an integer value representing DPI.

        """
        return self.mobile_commands.get_display_density()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_system_bars(self) -> None:  # real signature unknown
        """Execute mobile: getSystemBars command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getsystembars

        Description:
            Retrieves properties of various system bars on the device under test. Available since driver version 2.21.

        Returns:
            A dictionary containing entries for 'statusBar' and 'navigationBar'. Each entry is a dictionary with the following properties:
                visible (boolean): True if the bar is visible; false if the bar is not present.
                x (number): X coordinate of the bar; may be 0 if the bar is not present.
                y (number): Y coordinate of the bar; may be 0 if the bar is not present.
                width (number): Width of the bar; may be 0 if the bar is not present.
                height (number): Height of the bar; may be 0 if the bar is not present.

        """
        return self.mobile_commands.get_system_bars()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def fingerprint(self, fingerprint_id: int) -> None:  # real signature unknown
        """Execute mobile: fingerprint command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-fingerprint

        Description:
            Emulates a fingerprint scan on the Android Emulator. Only works on API level 23 and above. Available since driver version

        Args:
            fingerprint_id (number):	The value is the id for the finger that was "scanned". It is a unique integer that you assign for each virtual fingerprint. When the app is running you can run this same command each time the emulator prompts you for a fingerprint, you can run the adb command and pass it the fingerprintId to simulate the fingerprint scan. Required. Example: 1

        Returns:
            Any: result of script execution

        """
        params = {
            "fingerprintId": fingerprint_id,
        }
        return self.mobile_commands.fingerprint(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def send_sms(
        self,
        phone_number: str,
        message: str,
    ) -> None:  # real signature unknown
        """Execute mobile: sendSms command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-sendsms

        Description:
            Emulates sending an SMS to a specified phone number on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Args:
            phone_number (string): The phone number to which the SMS should be sent. Required. Example: '0123456789'
            message (string): The content of the SMS message. Required. Example: 'Hello'

        Returns:
            The actual command output. An error is thrown if SMS emulation fails.

        """
        params = {
            "phoneNumber": phone_number,
            "message": message,
        }
        return self.mobile_commands.send_sms(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def gsm_call(
        self,
        phone_number: str,
        action: str,
    ) -> None:  # real signature unknown
        """Execute mobile: gsmCall command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-gsmcall

        Description:
            Emulates a GSM call to a specified phone number on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Args:
            phone_number (string): The phone number to call. Required. Example: '0123456789'
            action (string): The action to perform on the call. Must be one of 'call', 'accept', 'cancel', or 'hold'. Required. Example: 'accept'

        """
        params = {
            "phoneNumber": phone_number,
            "action": action,
        }
        return self.mobile_commands.gsm_call(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def gsm_signal(self, strength: int) -> None:  # real signature unknown
        """Execute mobile: gsmSignal command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-gsmsignal

        Description:
            Emulates a GSM signal strength change event on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Args:
            strength (int): Signal strength value to emulate. Must be one of 0, 1, 2, 3, or 4, where 4 is the best signal. Required. Example: 3

        Returns:
            The actual command output. An error is thrown if GSM signal emulation fails.

        """
        params = {
            "strength": strength,
        }
        return self.mobile_commands.gsm_signal(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def gsm_voice(
        self,
        state: Literal["on", "off", "denied", "searching", "roaming", "home", "unregistered"],
    ) -> None:  # real signature unknown
        """Execute mobile: gsmVoice command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-gsmvoice

        Description:
            Emulates a GSM voice state change event on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Args:
            state (str): Voice state to emulate. Must be one of 'on', 'off', 'denied', 'searching', 'roaming', 'home', or 'unregistered'. Required. Example: 'off'

        Returns:
            The actual command output. An error is thrown if GSM voice state emulation fails.

        """
        params = {
            "state": state,
        }
        return self.mobile_commands.gsm_voice(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def power_ac(self, state: Literal["on", "off"]) -> None:  # real signature unknown
        """Execute mobile: powerAC command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-powerac

        Description:
            Emulates an AC power state change on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Args:
            state (str): AC power state to emulate. Must be either 'on' or 'off'. Required. Example: 'off'

        """
        params = {
            "state": state,
        }
        return self.mobile_commands.power_ac(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def power_capacity(self, percent: int) -> None:  # real signature unknown
        """Execute mobile: powerCapacity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-powercapacity

        Description:
            Emulates a change in battery power capacity on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Args:
            percent (int): Battery percentage to emulate, must be in the range 0 to 100. Required. Example: 50

        """
        params = {
            "percent": percent,
        }
        return self.mobile_commands.power_capacity(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def network_speed(
        self,
        speed: Literal["gsm", "scsd", "gprs", "edge", "umts", "hsdpa", "lte", "evdo", "full"],
    ) -> None:  # real signature unknown
        """Execute mobile: networkSpeed command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-networkspeed

        Description:
            Emulates different mobile network connection speed modes on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Args:
            speed (str): The mobile network speed mode to emulate. Supported values are "gsm", "scsd", "gprs", "edge", "umts", "hsdpa", "lte", "evdo", or "full". Required. Example: "edge"

        Returns:
            The actual command output. An error is thrown if network speed emulation fails.

        """
        params = {
            "speed": speed,
        }
        return self.mobile_commands.network_speed(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def replace_element_value(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        text: str,
    ) -> None:  # real signature unknown
        r"""Execute mobile: replaceElementValue command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-replaceelementvalue

        Description:
            Sends a text to the specified element by replacing its previous content. If the text ends with "\\n" (backslash must be escaped, so it is not translated into 0x0A), the Enter key press will be emulated after typing. Available since driver version 2.22.

        Args:
            locator (tuple[str, str] | dict[str, Any] | Element | UiSelector): locator of element to retreive
            text (str): The text to enter. Can include Unicode characters. If ending with "\\n", the Enter key is emulated after typing (the "\\n" substring itself is removed). Required. Example: "yolo"

        Returns:
            The actual command output. An error is thrown if sending text fails.

        """
        element = self.get_element(locator)
        native_element = element.get_native()
        params = {
            "elementId": native_element.id,
            "text": text,
        }
        return self.mobile_commands.replace_element_value(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def toggle_gps(self) -> None:  # real signature unknown
        """Execute mobile: toggleGps command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-togglegps

        Description:
            Switches GPS setting state. This API only works reliably since Android 12 (API 31). Available since driver version 2.23.

        """
        return self.mobile_commands.toggle_gps()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def is_gps_enabled(self) -> None:  # real signature unknown
        """Execute mobile: isGpsEnabled command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-isgpsenabled

        Description:
            Returns true if GPS is enabled on the device under test. Available since driver version 2.23.

        """
        return self.mobile_commands.is_gps_enabled()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_performance_data_types(self) -> None:  # real signature unknown
        """Execute mobile: getPerformanceDataTypes command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getperformancedatatypes

        Description:
            Fetches the list of supported performance data types that can be used as the `dataType` argument for the `mobile: getPerformanceData` extension. Available since driver version 2.24.

        Returns:
            List[str]: A list of supported performance data type names.

        """
        return self.mobile_commands.get_performance_data_types()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_performance_data(
        self,
        package_name: str,
        data_type: str,
    ) -> None:  # real signature unknown
        """Execute mobile: getPerformanceData command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getperformancedata

        Description:
            Retrieves performance data about the specified Android subsystem for a given app. The data is parsed from the output of the `dumpsys` utility. Available since driver version 2.24.

        Args:
            package_name (str): The package identifier of the app to fetch performance data for. Required. Example: "com.myapp"
            data_type (str): The subsystem name for which to retrieve performance data. Must be one of the values returned by `mobile: getPerformanceDataTypes`. Required. Example: "batteryinfo" or "cpuinfo" or "memoryinfo" or "networkinfo"

        Returns:
            List[List[Any]]: The data is organized as a table:
                - The first row contains column names.
                - Subsequent rows contain sampled data for each column.

            Example outputs:

            batteryinfo:
                [
                    ["power"],
                    [23]
                ]

            memoryinfo:
                [
                    ["totalPrivateDirty", "nativePrivateDirty", "dalvikPrivateDirty", "eglPrivateDirty", "glPrivateDirty", "totalPss", "nativePss", "dalvikPss", "eglPss", "glPss", "nativeHeapAllocatedSize", "nativeHeapSize"],
                    [18360, 8296, 6132, None, None, 42588, 8406, 7024, None, None, 26519, 10344]
                ]

            networkinfo (emulator):
                [
                    ["bucketStart", "activeTime", "rxBytes", "rxPackets", "txBytes", "txPackets", "operations", "bucketDuration"],
                    [1478091600000, None, 1099075, 610947, 928, 114362, 769, 3600000],
                    [1478095200000, None, 1306300, 405997, 509, 46359, 370, 3600000]
                ]

            networkinfo (real devices):
                [
                    ["st", "activeTime", "rb", "rp", "tb", "tp", "op", "bucketDuration"],
                    [1478088000, None, None, 32115296, 34291, 2956805, 25705, 3600],
                    [1478091600, None, None, 2714683, 11821, 1420564, 12650, 3600],
                    [1478095200, None, None, 10079213, 19962, 2487705, 20015, 3600],
                    [1478098800, None, None, 4444433, 10227, 1430356, 10493, 3600]
                ]

            cpuinfo:
                [
                    ["user", "kernel"],
                    [0.9, 1.3]
                ]

        """
        params = {
            "packageName": package_name,
            "dataType": data_type,
        }
        return self.mobile_commands.get_performance_data(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def status_bar(
        self,
        command: Literal[
            "expandNotifications",
            "expandSettings",
            "collapse",
            "addTile",
            "removeTile",
            "clickTile",
            "getStatusIcons",
        ],
        component: Literal["addTile", "removeTile", "clickTile"],
    ) -> None:  # real signature unknown
        """Execute mobile: statusBar command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-statusbar

        Description:
            Performs operations on the system status bar using the `adb shell cmd statusbar` CLI. Only works on Android 8 (Oreo) and newer. Available since driver version 2.25.

        Args:
            command (str): The status bar command to execute. Required. Example: "expandNotifications"
                Supported commands:
                    - "expandNotifications": Open the notifications panel.
                    - "expandSettings": Open the notifications panel and expand quick settings if present.
                    - "collapse": Collapse the notifications and settings panel.
                    - "addTile": Add a TileService of the specified component.
                    - "removeTile": Remove a TileService of the specified component.
                    - "clickTile": Click on a TileService of the specified component.
                    - "getStatusIcons": Returns the list of status bar icons in the order they appear (each item separated by a newline).

            component (str): The fully qualified name of a TileService component. Only required for "addTile", "removeTile", or "clickTile" commands. Optional. Example: "com.package.name/.service.QuickSettingsTileComponent"

        Returns:
            str: The actual output from the underlying status bar command. The output depends on the selected command and may be empty.

        """
        params = {
            "command": command,
            "component": component,
        }
        return self.mobile_commands.status_bar(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def screenshots(
        self,
        display_id: int | str | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: screenshots command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-screenshots

        Description:
            Captures a screenshot of each display available on the Android device. This functionality is supported on Android 10 and newer.

        Args:
            display_id (int or str, optional): Identifier of the display to capture. If not provided, screenshots for all displays will be returned. If the specified display does not exist, an error is thrown. Display identifiers can be retrieved using `adb shell dumpsys SurfaceFlinger --display-id`. Example: 1

        Returns:
            Dict[str, Dict]: A dictionary where each key is a display identifier and each value is a dictionary with the following keys:

                id (int or str): The display identifier. Example: 1
                name (str): Display name. Example: "Built-in Display"
                isDefault (bool): True if this display is the default display, False otherwise. Example: True
                payload (str): PNG screenshot data encoded as a base64 string. Example: "iVBORw0KGgoAAAANSUhEUgAA..."

        """
        params = {
            "displayId": display_id,
        }
        # Remove None values - Appium expects these params to be omitted, not null
        params = {k: v for k, v in params.items() if v is not None}
        return self.mobile_commands.screenshots(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def set_ui_mode(
        self,
        mode: Literal["night", "car"],
        value: str,
    ) -> None:  # real signature unknown
        """Execute mobile: setUiMode command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-setuimode

        Description:
            Sets the device UI appearance using a thin wrapper over `adb shell cmd uimode`. Supported on Android 10 and newer.

        Args:
            mode (str): The UI mode to configure. Supported values are:
                - "night": Night mode
                - "car": Car mode
              Example: "night"

            value (str): The value to apply for the selected UI mode. Supported values depend on the mode:
                - night: "yes", "no", "auto", "custom_schedule", "custom_bedtime"
                - car: "yes", "no"
              Example: "yes" (to enable night/dark mode)

        Returns:
            The actual command output. An error is thrown if command execution fails.

        """
        params = {
            "mode": mode,
            "value": value,
        }
        return self.mobile_commands.set_ui_mode(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_ui_mode(self, mode: Literal["night", "car"]) -> str:
        """Execute mobile: getUiMode command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getuimode

        Description:
            Retrieves the current device UI appearance for the specified mode using a thin wrapper over `adb shell cmd uimode`. Supported on Android 10 and newer.

        Args:
            mode (str): The UI mode to query. Supported values are:
                - "night": Night mode
                - "car": Car mode
              Example: "night"

        Returns:
            str: The current value of the specified UI mode. Supported values depend on the mode:
                - night: "yes", "no", "auto", "custom_schedule", "custom_bedtime"
                - car: "yes", "no"

        """
        params = {
            "mode": mode,
        }
        return self.mobile_commands.get_ui_mode(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def send_trim_memory(
        self,
        pkg: str,
        level: Literal[
            "COMPLETE",
            "MODERATE",
            "BACKGROUND",
            "UI_HIDDEN",
            "RUNNING_CRITICAL",
            "RUNNING_LOW",
            "RUNNING_MODERATE",
        ],
    ) -> None:  # real signature unknown
        """Execute mobile: sendTrimMemory command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-sendtrimmemory

        Description:
            Simulates the `onTrimMemory()` event for a given Android package. This allows testing the app's behavior under various memory pressure conditions. For more details, see "Manage your app's memory". Supported since driver version 2.41.

        Args:
            pkg (str): The package name to send the trimMemory event to. Required. Example: "com.my.company"
            level (str): The memory trim level to simulate. Required. Supported values are:
                - "COMPLETE"
                - "MODERATE"
                - "BACKGROUND"
                - "UI_HIDDEN"
                - "RUNNING_CRITICAL"
                - "RUNNING_LOW"
                - "RUNNING_MODERATE"
              Example: "RUNNING_CRITICAL"

        Returns:
            The actual command output. An error is thrown if the simulation fails.

        """
        params = {
            "pkg": pkg,
            "level": level,
        }
        return self.mobile_commands.send_trim_memory(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def inject_emulator_camera_image(self, payload: str) -> None:  # real signature unknown
        """Execute mobile: injectEmulatorCameraImage command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-injectemulatorcameraimage

        Description:
            Simulates an image injection into the VirtualScene emulator camera foreground. After a successful call, the supplied PNG image will appear as the camera's foreground scene (useful for testing QR/barcode scanners, OCR, etc.). This only works on Android emulators. Available since driver version 3.2.0.

        Args:
            payload (string): Base64-encoded PNG image payload. Only PNG is supported. Required. Example: "iVBORw0KGgoAAAANSUh..."

        Required preconditions:
            - This feature only works on Android emulators.
            - For newly created or reset emulators you must provide the `appium:injectedImageProperties` capability (it may be an empty map to use defaults) so the emulator is prepared for image injection.
            - Alternatively, you may configure the emulator manually by editing `$ANDROID_HOME/emulator/resources/Toren1BD.posters` as described in the docs (replace contents, save, then restart the emulator). This manual step is only necessary if you prefer not to restart the emulator during session startup.

        Returns:
            Boolean: True if the image was injected successfully. An error is thrown if the operation fails (for example, if the payload is not a valid base64 PNG or the emulator is not prepared).

        """
        params = {
            "payload": payload,
        }
        return self.mobile_commands.inject_emulator_camera_image(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def bluetooth(
        self,
        action: Literal["enable", "disable", "unpairAll"],
    ) -> None:  # real signature unknown
        """Execute mobile: bluetooth command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-bluetooth

        Description:
            Allows controlling the Bluetooth adapter on the device under test. An error is thrown if the device has no default Bluetooth adapter. Available since driver version 3.4.0.

        Args:
            action (string): The action to execute on the Bluetooth adapter. Supported values are:
                - "enable": Turns the Bluetooth adapter on.
                - "disable": Turns the Bluetooth adapter off.
                - "unpairAll": Unpairs all currently paired devices.
              Calling the same action multiple times has no effect. Required. Example: "disable"

        Returns:
            Boolean: True if the action was successfully executed. An error is thrown if the device has no Bluetooth adapter or if the operation fails.

        """
        params = {
            "action": action,
        }
        return self.mobile_commands.bluetooth(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def nfc(self, action: Literal["enable", "disable"]) -> None:  # real signature unknown
        """Execute mobile: nfc command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-nfc

        Description:
            Allows controlling the NFC adapter on the device under test. An error is thrown if the device has no default NFC adapter. Available since driver version 3.4.0.

        Args:
            action (string): The action to execute on the NFC adapter. Supported values are:
                - "enable": Turns the NFC adapter on.
                - "disable": Turns the NFC adapter off.
              Calling the same action multiple times has no effect. Required. Example: "disable"

        Returns:
            Boolean: True if the action was successfully executed. An error is thrown if the device has no NFC adapter or if the operation fails.

        """
        params = {
            "action": action,
        }
        return self.mobile_commands.nfc(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def pull_file(self, remote_path: str) -> str:
        """Execute mobile: pullFile command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-pullfile

        Description:
            Pulls a remote file from the device. Supports pulling files from standard device paths or from app bundles (debugging must be enabled for app bundle access).

        Args:
            remote_path (string): The full path to the remote file or a specially formatted path inside an app bundle (e.g., "@my.app.id/my/path"). Required. Example: "/sdcard/foo.bar"

        Returns:
            string: Base64-encoded content of the remote file. An error is thrown if the file does not exist or if the operation fails.

        """
        params = {
            "remotePath": remote_path,
        }
        return self.mobile_commands.pull_file(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def push_file(self, remote_path: str, payload: str) -> None:  # real signature unknown
        """Execute mobile: pushFile command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-pushfile

        Description:
            Pushes a local file to the device. If a file already exists at the target path, it will be silently overwritten.

        Args:
            remote_path (str): The path on the device where the file should be written. Required. Example: "/sdcard/foo.bar"
            payload (str): Base64-encoded content of the file to be pushed. Required. Example: "QXBwaXVt"

        Returns:
            Any: result of script execution

        """
        params = {
            "remotePath": remote_path,
            "payload": payload,
        }
        return self.mobile_commands.push_file(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def pull_folder(self, remote_path: str) -> None:  # real signature unknown
        """Execute mobile: pullFolder command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-pullfolder

        Description:
            Pulls a remote folder from the device. The folder content is zipped and returned as a Base64-encoded string.

        Args:
            remote_path (string): The path to the remote folder on the device. Required. Example: "/sdcard/yolo/"

        Returns:
            Any: Base64-encoded string representing the zipped content of the remote folder. An error is thrown if the folder does not exist or the operation fails.

        """
        params = {
            "remotePath": remote_path,
        }
        return self.mobile_commands.pull_folder(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_clipboard(self) -> str:
        """Execute mobile: getClipboard command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getclipboard

        Description:
            Retrieves the plaintext content of the device's clipboard.

        Returns:
            Base64-encoded string representing the clipboard content. Returns an empty string if the clipboard is empty. An error is thrown if the operation fails.

        """
        return self.mobile_commands.get_clipboard()

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def set_clipboard(
        self,
        content: str,
        content_type: str = "plaintext",
        label: str | None = None,
    ) -> None:  # real signature unknown
        """Execute mobile: setClipboard command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-setclipboard

        Description:
            Sets the plain text content of the device's clipboard.

        Args:
            content (string): Base64-encoded clipboard payload. Required. Example: 'YXBwaXVt'
            content_type (string): The type of content to set. Only 'plaintext' is supported and is used by default. Optional. Example: 'plaintext'
            label (string): Optional label to identify the current clipboard payload. Optional. Example: 'yolo'

        Returns:
            Any: result of script execution

        """
        params = {
            "content": content,
            "contentType": content_type,
            "label": label,
        }
        return self.mobile_commands.set_clipboard(params)

    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def shell(self, command: str, args: str = "") -> str:
        """Execute mobile: shell command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-shell

        Args:
            command (str): shell command
            args (str): arguments

        Returns:
            Any: result of script execution

        """
        params = {
            "command": command,
            "args": [args],
        }
        return self.mobile_commands.shell(params)

    # -------------------------- screenshot --------------------------

    # Override
    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def save_screenshot(self, path: str = "", filename: str = "screenshot.png") -> bool:
        """Save a screenshot to file.

        Args:
            path: Directory path to save the screenshot.
            filename: Name of the screenshot file.

        Returns:
            bool: True if successful.

        """
        path_to_file = Path(path) / filename
        with path_to_file.open("wb") as f:
            f.write(self.get_screenshot())
        return True

    # Override
    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def get_screenshot(self) -> bytes:
        """Get screenshot as bytes.

        Returns:
            bytes: Screenshot data in binary format.

        """
        screenshot = self.driver.get_screenshot_as_base64().encode("utf-8")
        return base64.b64decode(screenshot)

    # Override
    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def save_source(self, path: str = "", filename: str = "screenshot.png") -> bool:
        """Save page source to file.

        Args:
            path: Directory path to save the file.
            filename: Name of the file to save.

        Returns:
            bool: True if successful.

        """
        path_to_file = Path(path) / filename
        with path_to_file.open("wb") as f:
            f.write(self.driver.page_source.encode("utf-8"))
        return True

    # Override
    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def start_recording_screen(self) -> None:
        """Start screen recording using Appium driver."""
        self.driver.start_recording_screen()

    # Override
    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def stop_recording_screen(self) -> bytes:
        """Stop screen recording and return video as bytes.

        Returns:
            bytes: Video recording in base64-decoded format.

        """
        encoded = self.driver.stop_recording_screen()
        return base64.b64decode(encoded)

    # Override
    @fail_safe_shadowstep(raise_exception=ShadowstepException)
    @log_debug()
    def update_settings(self) -> None:
        """Update Appium driver settings.

        This method updates various Appium driver settings for UiAutomator2.
        For detailed documentation, see:
        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/README.md?plain=1#L304

        Note: This docstring contains long lines due to API documentation requirements.
        """
        # TODO move to separate class with transparent settings selection (enum?)  # noqa: TD002, TD003, TD004, FIX002
        self.driver.update_settings(settings={"enableMultiWindows": True})
