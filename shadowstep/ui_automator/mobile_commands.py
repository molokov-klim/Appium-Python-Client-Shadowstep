"""Mobile commands for Appium automation.

This module provides a comprehensive set of mobile commands for Appium automation,
including app management, device information, clipboard operations, and more.
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
)
from typing_extensions import Self

from shadowstep.decorators.common_decorators import fail_safe
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException
from shadowstep.utils.utils import get_current_func_name
from shadowstep.web_driver.web_driver_singleton import WebDriverSingleton


class MobileCommands:
    """Singleton mobile commands wrapper for Appium automation.

    This class provides a comprehensive set of mobile commands for Appium automation,
    including app management, device information, clipboard operations, and more.
    see https://github.com/appium/appium-uiautomator2-driver
    """

    _instance: ClassVar[MobileCommands | None] = None
    logger: logging.Logger

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:  # noqa: ARG004
        """Ensure only one instance of MobileCommands exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance  # type: ignore[return-value]

    def __init__(self) -> None:
        """Initialize the MobileCommands singleton."""
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def shell(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: shell command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-shell

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Executes the given shell command on the device under test via ADB connection. This extension exposes a potential security risk and thus is only enabled when explicitly activated by the adb_shell server command line feature specifier.

        Supported arguments:
            command (string): Shell command name to execute, for example echo or rm. Required. Example: echo
            args (Array<string>): Array of command arguments. Optional. Example: ['-f', '/sdcard/myfile.txt']
            timeout (number): Command timeout in milliseconds. If the command blocks for longer than this timeout then an exception is going to be thrown. The default timeout is 20000 ms. Optional. Example: 100000
            includeStderr (boolean): Whether to include stderr stream into the returned result. false by default. Optional. Example: true

        Returned Result:
            The actual command output. An error is thrown if command execution fails.

        """
        self.logger.debug("%s", get_current_func_name())
        self.logger.info("shell: %s", params)
        return self._execute("mobile: shell", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def scroll(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: scroll command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-shell

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Scrolls the given scrollable element until an element identified by strategy and selector becomes visible. This function returns immediately if the destination element is already visible in the view port. Otherwise it would scroll to the very beginning of the scrollable control and tries to reach the destination element by scrolling its parent to the end step by step. The scroll direction (vertical or horizontal) is detected automatically.

        Supported arguments:
            elementId (string): The identifier of the scrollable element. It is required that this element is a valid scrollable container and was located using the -android uiautomator strategy. If not provided, the first currently available scrollable view is selected for the interaction. Optional. Example: 123456-3456-3435-3453453
            strategy (string): The lookup strategy to use. Supported values: accessibility id (UiSelector().description), class name (UiSelector().className), -android uiautomator (UiSelector). Required. Example: 'accessibility id'
            selector (string): The corresponding lookup value for the selected strategy. Required. Example: 'com.mycompany:id/table'
            maxSwipes (number): The maximum number of swipes to perform on the target scrollable view in order to reach the destination element. If unset, it will be retrieved from the scrollable element itself via getMaxSearchSwipes() property. Optional. Example: 10

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: scroll", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def long_click_gesture(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: longClickGesture command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-longclickgesture

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            This gesture performs long click action on the given element/coordinates.

        Supported arguments:
            elementId: The id of the element to be clicked. If the element is missing then both click offset coordinates must be provided. If both the element id and offset are provided then the coordinates are parsed as relative offsets from the top left corner of the element.
            x: The x-offset coordinate
            y: The y-offset coordinate
            duration: Click duration in milliseconds. 500 by default. The value must not be negative
            locator: The map containing strategy and selector items to make it possible to click dynamic elements.

        Example:
            driver.execute_script('mobile: longClickGesture', {'x': 100, 'y': 100, 'duration': 1000})

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: longClickGesture", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def double_click_gesture(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: doubleClickGesture command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-doubleclickgesture

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            This gesture performs double click action on the given element/coordinates.

        Supported arguments
            elementId: The id of the element to be clicked. If the element is missing then both click offset coordinates must be provided. If both the element id and offset are provided then the coordinates are parsed as relative offsets from the top left corner of the element.
            x: The x-offset coordinate
            y: The y-offset coordinate
            locator: The map containing strategy and selector items to make it possible to click dynamic elements.

        Example:
            driver.execute_script('mobile: doubleClickGesture', {'x': 100, 'y': 100})

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: doubleClickGesture", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def click_gesture(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: clickGesture command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-clickgesture

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            This gesture performs click action on the given element/coordinates. Available since Appium UiAutomator2 driver 1.71.0. Usage of this gesture is recommended as a possible workaround for cases where the "native" tap call fails, even though tap coordinates seem correct. This issue is related to the fact these calls use the legacy UIAutomator-based calls while this extension is based on the same foundation as W3C does.

        Supported arguments
            elementId: The id of the element to be clicked. If the element is missing then both click offset coordinates must be provided. If both the element id and offset are provided then the coordinates are parsed as relative offsets from the top left corner of the element.
            x: The x-offset coordinate
            y: The y-offset coordinate
            locator: The map containing strategy and selector items to make it possible to click dynamic elements.

        Example:
            driver.execute_script('mobile: clickGesture', {'x': 100, 'y': 100})

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: clickGesture", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def drag_gesture(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: dragGesture command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-draggesture

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            This gesture performs drag action from the given element/coordinates to the given point.

        Supported arguments
            elementId: The id of the element to be dragged. If the element id is missing then both start coordinates must be provided. If both the element id and the start coordinates are provided then these coordinates are considered as offsets from the top left element corner.
            startX: The x-start coordinate
            startY: The y-start coordinate
            endX: The x-end coordinate. Mandatory argument
            endY: The y-end coordinate. Mandatory argument
            speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 2500 * displayDensity

        Example:
            // Java
            ((JavascriptExecutor) driver).executeScript("mobile: dragGesture", ImmutableMap.of(
                "elementId", ((RemoteWebElement) element).getId(),
                "endX", 100,
                "endY", 100
            ));

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: dragGesture", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def fling_gesture(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: flingGesture command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-flinggesture

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            This gesture performs fling gesture on the given element/area.

        Supported arguments
            elementId: The id of the element to be flinged. If the element id is missing then fling bounding area must be provided. If both the element id and the fling bounding area are provided then this area is effectively ignored.
            left: The left coordinate of the fling bounding area
            top: The top coordinate of the fling bounding area
            width: The width of the fling bounding area
            height: The height of the fling bounding area
            direction: Direction of the fling. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
            speed: The speed at which to perform this gesture in pixels per second. The value must be greater than the minimum fling velocity for the given view (50 by default). The default value is 7500 * displayDensity

        Returned value:
            The returned value is a boolean one and equals to true if the object can still scroll in the given direction

        Example:
            // Java
            boolean canScrollMore = (Boolean) ((JavascriptExecutor) driver).executeScript("mobile: flingGesture", ImmutableMap.of(
                "elementId", ((RemoteWebElement) element).getId(),
                "direction", "down",
                "speed", 500
            ));

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: flingGesture", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def pinch_open_gesture(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: pinchOpenGesture command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-pinchopengesture

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            This gesture performs pinch-open gesture on the given element/area.

        Supported arguments
            elementId: The id of the element to be pinched. If the element id is missing then pinch bounding area must be provided. If both the element id and the pinch bounding area are provided then the area is effectively ignored.
            left: The left coordinate of the pinch bounding area
            top: The top coordinate of the pinch bounding area
            width: The width of the pinch bounding area
            height: The height of the pinch bounding area
            percent: The size of the pinch as a percentage of the pinch area size. Valid values must be float numbers in range 0..1, where 1.0 is 100%. Mandatory value.
            speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 2500 * displayDensity

        Example:
            // Java
            ((JavascriptExecutor) driver).executeScript("mobile: pinchOpenGesture", ImmutableMap.of(
                "elementId", ((RemoteWebElement) element).getId(),
                "percent", 0.75
            ));

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: pinchOpenGesture", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def pinch_close_gesture(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: pinchCloseGesture command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-pinchclosegesture

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            This gesture performs pinch-close gesture on the given element/area.

        Supported arguments
            elementId: The id of the element to be pinched. If the element id is missing then pinch bounding area must be provided. If both the element id and the pinch bounding area are provided then the area is effectively ignored.
            left: The left coordinate of the pinch bounding area
            top: The top coordinate of the pinch bounding area
            width: The width of the pinch bounding area
            height: The height of the pinch bounding area
            percent: The size of the pinch as a percentage of the pinch area size. Valid values must be float numbers in range 0..1, where 1.0 is 100%. Mandatory value.
            speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 2500 * displayDensity

        Example:
            # Python
            can_scroll_more = driver.execute_script('mobile: pinchCloseGesture', {
                'elementId': element.id,
                'percent': 0.75
            })

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: pinchCloseGesture", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def swipe_gesture(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: swipeGesture command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-swipegesture

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            This gesture performs swipe gesture on the given element/area.

        Supported arguments
            elementId: The id of the element to be swiped. If the element id is missing then swipe bounding area must be provided. If both the element id and the swipe bounding area are provided then the area is effectively ignored.
            left: The left coordinate of the swipe bounding area
            top: The top coordinate of the swipe bounding area
            width: The width of the swipe bounding area
            height: The height of the swipe bounding area
            direction: Swipe direction. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
            percent: The size of the swipe as a percentage of the swipe area size. Valid values must be float numbers in range 0..1, where 1.0 is 100%. Mandatory value.
            speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 5000 * displayDensity

        Example:
            # Python
            driver.execute_script('mobile: swipeGesture', {
                'left': 100,
                'top': 100,
                'width': 200,
                'height': 200,
                'direction': direction, 'percent': 0.75
            })

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: swipeGesture", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def scroll_gesture(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: scrollGesture command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollgesture

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            This gesture performs scroll gesture on the given element/area.

        Supported arguments
            elementId: The id of the element to be scrolled. If the element id is missing then scroll bounding area must be provided. If both the element id and the scroll bounding area are provided then this area is effectively ignored.
            left: The left coordinate of the scroll bounding area
            top: The top coordinate of the scroll bounding area
            width: The width of the scroll bounding area
            height: The height of the scroll bounding area
            direction: Scrolling direction. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
            percent: The size of the scroll as a percentage of the scrolling area size. Valid values must be float numbers greater than zero, where 1.0 is 100%. Mandatory value.
            speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 5000 * displayDensity

        Returned value:
            The returned value is a boolean one and equals to true if the object can still scroll in the given direction

        Example:
            # Python
            can_scroll_more = driver.execute_script('mobile: scrollGesture', {
                'left': 100, 'top': 100, 'width': 200, 'height': 200,
                'direction': 'down',
                'percent': 3.0
            })

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: scrollGesture", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def exec_emu_console_command(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: execEmuConsoleCommand command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-execemuconsolecommand

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Executes a command through emulator telnet console interface and returns its output. The emulator_console server feature must be enabled in order to use this method.

        Supported arguments:
            command (string): The actual command to execute. See Android Emulator Console Guide for more details on available commands. Required. Example: help-verbose
            execTimeout (number): Timeout used to wait for a server reply to the given command in milliseconds. Defaults to 60000 ms. Optional. Example: 100000
            connTimeout (number): Console connection timeout in milliseconds. Defaults to 5000 ms. Optional. Example: 10000
            initTimeout (number): Telnet console initialization timeout in milliseconds (the time between establishing the connection and receiving the command prompt). Defaults to 5000 ms. Optional. Example: 10000

        Returned Result:
            The actual command output. An error is thrown if command execution fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: execEmuConsoleCommand", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def deep_link(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: deepLink command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-deeplink

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Start URI that may take users directly to the specific content in the app. Read Reliably Opening Deep Links Across Platforms and Devices for more details.

        Supported arguments:
            url (string): The URL to start. Required. Example: theapp://login/
            package (string): The name of the package to start the URI with. This argument was required previously but became optional since version 3.9.3. Optional. Example: 'com.mycompany'
            waitForLaunch (boolean): If false, ADB won't wait for the started activity to return control. Defaults to true. Optional. Example: false

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: deepLink", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def start_logs_broadcast(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: startLogsBroadcast command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startlogsbroadcast

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Starts Android logcat broadcast websocket on the same host and port where Appium server is running at /ws/session/:sessionId:/appium/device/logcat endpoint. The method will return immediately if the web socket is already listening. Each connected websocket listener will receive logcat log lines as soon as they are visible to Appium. Read Using Mobile Execution Commands to Continuously Stream Device Logs with Appium for more details.
            Consider using logs broadcast via BiDi over this extension.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: startLogsBroadcast", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def stop_logs_broadcast(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: stopLogsBroadcast command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-stoplogsbroadcast

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Stops the previously started logcat broadcasting websocket server. This method will return immediately if no server is running. Read Using Mobile Execution Commands to Continuously Stream Device Logs with Appium for more details.
            Consider using logs broadcast via BiDi over this extension.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: stopLogsBroadcast", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def deviceidle(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: deviceidle command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-deviceidle

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            This is a wrapper around the 'adb shell dumpsys deviceidle' interface. For more details, see *Diving Into Android 'M' Doze*. This API is available starting from Android 6.

        Supported arguments:
            action (string): The name of the action to perform. Supported values: whitelistAdd or whitelistRemove. Required. Example: whitelistAdd
            packages (string or Array<string>): One or more package names to perform the specified action on. Required. Example: 'com.mycompany'

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: deviceidle", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def accept_alert(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: acceptAlert command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-acceptalert

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Attempts to accept an Android alert. This method may not always be reliable since there is no single standard for how Android alerts appear in the Accessibility representation.

        Supported arguments:
            buttonLabel (string): The name or text of the alert button to click in order to accept it. If not provided, the driver will attempt to autodetect the appropriate button. Optional. Example: Accept

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: acceptAlert", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def dismiss_alert(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: dismissAlert command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-dismissalert

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Attempts to dismiss an Android alert. This method may not always be reliable since there is no single standard for how Android alerts appear in the Accessibility representation.

        Supported arguments:
            buttonLabel (string): The name or text of the alert button to click in order to dismiss it. If not provided, the driver will attempt to autodetect the appropriate button. Optional. Example: Dismiss

        Returned Result:
            True if the alert was successfully dismissed, otherwise an error is thrown.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: dismissAlert", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def battery_info(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: batteryInfo command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-batteryinfo

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves the battery information from the device under test.

        Returned Result:
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
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: batteryInfo", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def device_info(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: deviceInfo command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-deviceinfo

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves information about the device under test, including device model, serial number, network connectivity, and other properties.

        Returned Result:
            A dictionary containing device properties. For the full list of keys and their corresponding values, refer to:
            https://github.com/appium/appium-uiautomator2-server/blob/master/app/src/main/java/io/appium/uiautomator2/handler/GetDeviceInfo.java

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: deviceInfo", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_device_time(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getDeviceTime command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getdevicetime

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves the current timestamp of the device.

        Supported arguments:
            format (string): The set of format specifiers to use for formatting the timestamp. See https://momentjs.com/docs/ for the full list of supported datetime format specifiers. Defaults to 'YYYY-MM-DDTHH:mm:ssZ', which complies with ISO-8601. Optional. Example: 'YYYY-MM-DDTHH:mm:ssZ'

        Returned Result:
            A string representing the device timestamp formatted according to the given specifiers.


        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getDeviceTime", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def change_permissions(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: changePermissions command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-changepermissions

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Changes package permissions at runtime on the device under test.

        Supported arguments:
            permissions (string or Array<string>): The full name of the permission to be changed or a list of permissions. For standard Android permissions, refer to the Android documentation. If the special value 'all' is passed (available since driver version 2.8.0) and the target is 'pm' (default), the action will be applied to all permissions requested or granted by the 'appPackage'. For the 'appops' target (available since v2.11.0), refer to AppOpsManager.java for supported appops permission names. The 'all' value is not supported for the 'appops' target. Required. Example: ['android.permission.ACCESS_FINE_LOCATION', 'android.permission.BROADCAST_SMS'] or 'all'
            appPackage (string): The application package to modify permissions for. Defaults to the package under test. Optional. Example: com.mycompany.myapp
            action (string): The action to perform. For target 'pm', use 'grant' (default) or 'revoke'. For target 'appops', use 'allow' (default), 'deny', 'ignore', or 'default'. Optional. Example: allow
            target (string): The permission management target. Either 'pm' (default) or 'appops' (available since v2.11.0). The 'appops' target requires the adb_shell server security option to be enabled. Optional. Example: appops

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: changePermissions", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_permissions(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getPermissions command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getpermissions

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves the runtime permissions list for the specified application package.

        Supported arguments:
            type (string): The type of permissions to retrieve. Possible values are 'denied', 'granted', or 'requested' (default). Optional. Example: granted
            appPackage (string): The application package to query permissions from. Defaults to the package under test. Optional. Example: com.mycompany.myapp

        Returned Result:
            An array of strings, each representing a permission name. The array may be empty if no permissions match the specified type.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getPermissions", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def perform_editor_action(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: performEditorAction command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-performeditoraction

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Performs an IME (Input Method Editor) action on the currently focused edit element. This emulates the invocation of the onEditorAction callback commonly used in Android development when buttons like Search or Done are pressed on the on-screen keyboard.

        Supported arguments:
            action (string): The name or integer code of the editor action to execute. Supported action names are: 'normal', 'unspecified', 'none', 'go', 'search', 'send', 'next', 'done', 'previous'. See EditorInfo for more details. Required. Example: search

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: performEditorAction", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def start_screen_streaming(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: startScreenStreaming command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startscreenstreaming

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Starts device screen broadcasting by creating an MJPEG server. Multiple calls have no effect unless the previous streaming session is stopped. Requires the adb_screen_streaming feature on the server and GStreamer with gst-plugins-base, gst-plugins-good, and gst-plugins-bad installed and available in PATH on the server machine.

        Supported arguments:
            width (number): The scaled width of the device's screen in pixels. If unset, the actual screen width is used. Optional. Example: 768
            height (number): The scaled height of the device's screen in pixels. If unset, the actual screen height is used. Optional. Example: 1024
            bitRate (number): The video bit rate in bits per second. Default is 4000000 (4 Mb/s). Higher bit rate improves video quality but increases file size. Optional. Example: 1024000
            host (string): The IP address or hostname to start the MJPEG server on. Use 0.0.0.0 to bind to all available interfaces. Default: 127.0.0.1. Optional. Example: 0.0.0.0
            pathname (string): The HTTP request path for the MJPEG server. Should start with a slash. Optional. Example: /myserver
            tcpPort (number): The internal TCP port for MJPEG broadcast on the loopback interface (127.0.0.1). Default: 8094. Optional. Example: 5024
            port (number): The port number for the MJPEG server. Default: 8093. Optional. Example: 5023
            quality (number): The JPEG quality for streamed images, in range [1, 100]. Default: 70. Optional. Example: 80
            considerRotation (boolean): If true, GStreamer adjusts image dimensions for both landscape and portrait orientations. Default: false. Optional. Example: false
            logPipelineDetails (boolean): Whether to log GStreamer pipeline events to standard output. Useful for debugging. Default: false. Optional. Example: true

        Returned Result:
            True if the MJPEG server was successfully started; otherwise, an error is thrown.


        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: startScreenStreaming", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def stop_screen_streaming(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: stopScreenStreaming command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-stopscreenstreaming

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Stop the previously started screen streaming. If no screen streaming server has been started then nothing is done.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: stopScreenStreaming", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_notifications(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getNotifications command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getnotifications

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves Android notifications via Appium Settings helper. Appium Settings app itself must be manually granted to access notifications under device Settings in order to make this feature working. Different vendors might require more than just the normal Notification permissions at the usual Apps menu. Try to look in places like Privacy menus if you are getting zero items retrieved while expecting some results.

            Appium Settings keeps up to 100 notifications in an internal buffer, including both active notifications and those that appeared while the service was running. Newly appeared notifications are added to the head of the array. Each notification includes an `isRemoved` flag indicating whether it has been removed. For more details, see:
            https://developer.android.com/reference/android/service/notification/StatusBarNotification
            https://developer.android.com/reference/android/app/Notification.html

        Supported arguments:
            None

        Returned Result:
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
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getNotifications", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def open_notifications(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: openNotifications command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-opennotifications

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Opens notifications drawer on the device under test. Does nothing if the drawer is already opened.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: openNotifications", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def list_sms(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        r"""Execute mobile: listSms command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-listsms

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves the list of the most recent SMS messages via the Appium Settings helper. Messages are sorted by date in descending order (most recent first).

        Supported arguments:
            max (number): The maximum number of recent messages to retrieve. Defaults to 100. Optional. Example: 10

        Returned Result:
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
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: listSms", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def type(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: type command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-type

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Types the given Unicode string into the currently focused input field. Unlike sendKeys, this method emulates real typing as if performed from an on-screen keyboard and properly supports Unicode characters. The input field must already have focus before calling this method.

        Supported arguments:
            text (string): The text to type. Required. Example: testing

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: type", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def sensor_set(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: sensorSet command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-sensorset

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Emulates changing sensor values on the connected Android emulator. This extension does not work on real devices. Use the emulator console or check adb-emu-commands.js (SENSORS object) to see supported sensor types and acceptable value formats.

        Supported arguments:
            sensorType (string): The type of sensor to emulate. Required. Example: light
            value (string): The value to set for the sensor. Check the emulator console output for acceptable formats. Required. Example: 50

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: sensorSet", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def delete_file(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: deleteFile command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-deletefile

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Deletes a file on the remote device. The file can be a standard file on the filesystem or a file inside an application bundle.

        Supported arguments:
            remotePath (string): The full path to the remote file or a file inside an application bundle. Required. Example: /sdcard/myfile.txt or @my.app.id/path/in/bundle

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: deleteFile", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def is_app_installed(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: isAppInstalled command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-isappinstalled

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Verifies whether an application is installed on the device under test.

        Supported arguments:
            appId (string): The identifier of the application package to be checked. Required. Example: my.app.id
            user (number or string): The user ID for which the package installation is checked. Defaults to the current user if not provided. Optional. Example: 1006

        Returned Result:
            True if the application is installed for the specified user; otherwise, False.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: isAppInstalled", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def query_app_state(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: queryAppState command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-queryappstate

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Queries the current state of the specified application on the device under test.

        Supported arguments:
            appId (string): The identifier of the application package to be checked. Required. Example: my.app.id

        Returned Result:
            An integer representing the current state of the app:
                0: The app is not installed
                1: The app is installed but not running
                3: The app is running in the background
                4: The app is running in the foreground

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: queryAppState", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def activate_app(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: activateApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-activateapp

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Activates the specified application on the device under test, or launches it if it is not already running. This simulates a user clicking the app icon on the device dashboard.

        Supported arguments:
            appId (string): The identifier of the application package to be activated. Required. Example: my.app.id

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: activateApp", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def remove_app(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: removeApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-removeapp

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Uninstalls the specified application from the device under test if it is installed. If the application is not present, the call is ignored.

        Supported arguments:
            appId (string): The identifier of the application package to be removed. Required. Example: my.app.id
            timeout (number): The time in milliseconds to wait until the app is terminated. Optional. Default is 20000 ms. Example: 1500
            keepData (boolean): If set to true, the application data and cache folders are preserved after uninstall. Optional. Default is false. Example: true

        Returned Result:
            bool: True if the application was found and successfully removed; False otherwise.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: removeApp", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def terminate_app(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: terminateApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-terminateapp

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Terminates the specified application on the device under test and waits until the app is fully stopped, up to the provided timeout. If the timeout is zero or negative (since UIAutomator driver 2.9.0), the app state check is skipped, which is useful when the app may automatically restart.

        Supported arguments:
            appId (string): The identifier of the application package to be terminated. Required. Example: my.app.id
            timeout (number): Maximum time in milliseconds to wait until the app is terminated. Optional. Default is 500 ms. Example: 1500

        Returned Result:
            bool: True if the application was successfully terminated; False otherwise.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: terminateApp", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def install_app(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: installApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-installapp

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Installs the specified application package (.apk) on the device under test. May raise INSTALL_FAILED_VERSION_DOWNGRADE if the installed version is lower than the existing version on the device.

        Supported arguments:
            appPath (string): The local path to the .apk file(s) on the server filesystem or a remote URL. Required. Example: /app/path.apk
            timeout (number): Maximum time in milliseconds to wait for the installation to complete. Optional. Default is 6000 ms. Example: 120000
            allowTestPackages (bool): Whether to allow installation of test packages. Optional. Default is False. Example: True
            useSdcard (bool): Whether to install the app on the SD card instead of device memory. Optional. Default is False. Example: True
            grantPermissions (bool): Automatically grant all permissions requested in the app manifest after installation (Android 6+). Requires targetSdkVersion ≥ 23 and device API level ≥ 23. Optional. Default is False. Example: True
            replace (bool): Whether to upgrade/reinstall the app if it already exists. If False, throws an error instead. Optional. Default is True. Example: False
            checkVersion (bool): Skip installation if the device already has a greater or equal app version, avoiding INSTALL_FAILED_VERSION_DOWNGRADE errors. Optional. Default is False. Example: True

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: installApp", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def clear_app(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: clearApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-clearapp

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Deletes all data associated with the specified application package on the device under test. Internally calls `adb shell pm clear`. The app must exist, be accessible, and not running for this command to succeed.

        Supported arguments:
            appId (string): The identifier of the application package to be cleared. Required. Example: my.app.id

        Returned Result:
            Stdout of the corresponding adb command. An error is thrown if the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: clearApp", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def start_activity(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: startActivity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startactivity

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Starts the specified activity intent on the device under test. Internally invokes `am start` / `am start-activity` command. This method extends the functionality of the Start Activity app management API.

        Supported arguments:
            intent (string): Full name of the activity intent to start. Required. Example: com.some.package.name/.YourActivityClassName
            user (number|string): User ID for which the service is started. Optional. Defaults to current user. Example: 1006
            wait (boolean): Block the method call until the Activity Manager process returns control to the system. Optional. Default is false. Example: true
            stop (boolean): Force stop the target app before starting the activity. Optional. Default is false. Example: true
            windowingMode (integer): Windowing mode to launch the activity into. Optional. Example: 1
            activityType (integer): Activity type to launch the activity as. Optional. Example: 1
            action (string): Action name for the Activity Manager's `-a` argument. Optional. Example: android.intent.action.MAIN
            uri (string): Unified Resource Identifier for the `-d` argument. Optional. Example: https://appium.io
            mimeType (string): Mime type for the `-t` argument. Optional. Example: application/json
            identifier (string): Optional identifier for the `-i` argument. Optional. Example: my_identifier
            categories (string|Array[string]): One or more category names for the `-c` argument. Optional. Example: ['android.intent.category.LAUNCHER']
            component (string): Component name for the `-n` argument. Optional. Example: com.myapp/com.myapp.SplashActivity
            package (string): Package name for the `-p` argument. Optional. Example: com.myapp
            extras (Array[Array[string]]): Optional intent arguments. Each subarray contains value type, key, and value. Supported types: s, sn, z, i, l, f, u, cn, ia, ial, la, lal, fa, fal, sa, sal. Optional. Example: [['s', 'varName1', 'My String1'], ['ia', 'arrName', '1,2,3,4']]
            flags (string): Intent startup-specific flags as a hexadecimal string. Optional. Example: 0x10200000

        Returned Result:
            The actual stdout of the underlying `am` command. An error is thrown if the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: startActivity", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def start_service(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: startService command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startservice

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Starts the specified service intent on the device under test. Internally invokes `am startservice` or `am start-service` command.

        Supported arguments:
            intent (string): Full name of the service intent to start. Optional. Example: com.some.package.name/.YourServiceSubClassName
            user (number|string): User ID for which the service is started. Optional. Defaults to current user. Example: 1006
            foreground (boolean): Start the service as a foreground service (only works on Android 8+). Optional. Default is false. Example: true
            action (string): See documentation for `startActivity` extension. Optional. Example: android.intent.action.MAIN
            uri (string): See documentation for `startActivity` extension. Optional. Example: https://appium.io
            mimeType (string): See documentation for `startActivity` extension. Optional. Example: application/json
            identifier (string): See documentation for `startActivity` extension. Optional. Example: my_identifier
            categories (string|Array[string]): See documentation for `startActivity` extension. Optional. Example: ['com.myapp/com.myapp.SplashActivity']
            component (string): See documentation for `startActivity` extension. Optional. Example: android.intent.category.LAUNCHER
            package (string): See documentation for `startActivity` extension. Optional. Example: com.myapp
            extras (Array[Array[string]]): Optional intent arguments. Each subarray contains value type, key, and value. See `startActivity` documentation for supported types. Optional. Example: [['s', 'varName1', 'My String1'], ['ia', 'arrName', '1,2,3,4']]
            flags (string): Intent startup-specific flags as a hexadecimal string. See `startActivity` documentation for details. Optional. Example: 0x10200000

        Returned Result:
            The actual stdout of the underlying `am` command. An error is thrown if the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: startService", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def stop_service(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: stopService command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-stopservice

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Stops the specified service intent on the device under test. Internally invokes `am stopservice` or `am stop-service` command.

        Supported arguments:
            intent (string): Full name of the service intent to stop. Optional. Example: com.some.package.name/.YourServiceSubClassName
            user (number|string): User ID for which the service is stopped. Optional. Defaults to current user. Example: 1006
            action (string): See documentation for `startActivity` extension. Optional. Example: android.intent.action.MAIN
            uri (string): See documentation for `startActivity` extension. Optional. Example: https://appium.io
            mimeType (string): See documentation for `startActivity` extension. Optional. Example: application/json
            identifier (string): See documentation for `startActivity` extension. Optional. Example: my_identifier
            categories (string|Array[string]): See documentation for `startActivity` extension. Optional. Example: ['com.myapp/com.myapp.SplashActivity']
            component (string): See documentation for `startActivity` extension. Optional. Example: android.intent.category.LAUNCHER
            package (string): See documentation for `startActivity` extension. Optional. Example: com.myapp
            extras (Array[Array[string]]): Optional intent arguments. Each subarray contains value type, key, and value. See `startActivity` documentation for supported types. Optional. Example: [['s', 'varName1', 'My String1'], ['ia', 'arrName', '1,2,3,4']]
            flags (string): Intent-specific flags as a hexadecimal string. See `startActivity` documentation for details. Optional. Example: 0x10200000

        Returned Result:
            The actual stdout of the underlying `am` command. An error is thrown if the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: stopService", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def broadcast(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: broadcast command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-broadcast

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Sends a broadcast Intent on the device under test. Internally invokes the `am broadcast` command.

        Supported arguments:
            intent (string): Full name of the intent to broadcast. Optional. Example: com.some.package.name/.YourIntentClassName
            user (number|string): Specify which user to send to; possible values are 'all', 'current', or a numeric user ID. Optional. Example: current
            receiverPermission (string): Require the receiver to hold the given permission. Optional. Example: android.permission.READ_PROFILE
            allowBackgroundActivityStarts (boolean): Whether the receiver can start activities even if in the background. Optional. Default: false. Example: true
            action (string): See documentation for `startActivity` extension. Optional. Example: android.intent.action.MAIN
            uri (string): See documentation for `startActivity` extension. Optional. Example: https://appium.io
            mimeType (string): See documentation for `startActivity` extension. Optional. Example: application/json
            identifier (string): See documentation for `startActivity` extension. Optional. Example: my_identifier
            categories (string|Array[string]): See documentation for `startActivity` extension. Optional. Example: ['com.myapp/com.myapp.SplashActivity']
            component (string): See documentation for `startActivity` extension. Optional. Example: android.intent.category.LAUNCHER
            package (string): See documentation for `startActivity` extension. Optional. Example: com.myapp
            extras (Array[Array[string]]): Optional intent arguments. Each subarray contains value type, key, and value. See `startActivity` documentation for supported types. Optional. Example: [['s', 'varName1', 'My String1'], ['ia', 'arrName', '1,2,3,4']]
            flags (string): Intent-specific flags as a hexadecimal string. See `startActivity` documentation for details. Optional. Example: 0x10200000

        Returned Result:
            The actual stdout of the underlying `am` command. An error is thrown if the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: broadcast", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_contexts(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        r"""Execute mobile: getContexts command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getcontexts

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves a mapping of WebViews on the device under test based on Chrome DevTools Protocol (CDP) endpoints. This allows interaction with WebViews in hybrid applications.

        Supported arguments:
            waitForWebviewMs (number): Maximum time in milliseconds to wait for WebView(s) to appear. If set to 0 (default), the WebView availability is checked only once. Optional. Example: 10000

        Returned Result:
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
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getContexts", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def install_multiple_apks(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: installMultipleApks command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-installmultipleapks

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Installs multiple application packages on the device under test using the adb `install-multiple` option. Each APK will be installed in a single command, allowing options like granting permissions or partial installation.

        Supported arguments:
            apks (Array<string>): List of full paths or URLs to the APK files to be installed. Required. Example: ['/path/to/local.apk', 'https://github.com/appium/ruby_lib_core/blob/master/test/functional/app/api.apk.zip?raw=true']
            options (object): Installation options. Optional. Supported keys:
                - grantPermissions (boolean): If true, automatically grant all requested permissions (-g). Example: true
                - allowTestPackages (boolean): Corresponds to -t flag. Example: true
                - useSdcard (boolean): Corresponds to -s flag. Example: true
                - replace (boolean): Corresponds to -r flag; replaces existing app. Default is true. Example: false
                - partialInstall (boolean): Corresponds to -p flag for partial installation. Example: true

        Returned Result:
            The stdout of the corresponding adb install-multiple command. An error is thrown if the installation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: installMultipleApks", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def lock(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: lock command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-lock

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Locks the device using a simple lock (e.g., without a password). Optionally, the device can be automatically unlocked after a specified number of seconds.

        Supported arguments:
            seconds (number|string): The number of seconds after which the device should be automatically unlocked. If set to 0 or left empty, the device must be unlocked manually. Optional. Example: 10

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: lock", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def unlock(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: unlock command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-unlock

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Unlocks the device if it is currently locked. No operation is performed if the device is not locked.

        Supported arguments:
            key (string): The unlock key to use. See the documentation for the `appium:unlockKey` capability for more details. Required. Example: "12345"
            type (string): The unlock type. See the documentation for the `appium:unlockType` capability for more details. Required. Example: "password"
            strategy (string): The unlock strategy to apply. See the documentation for the `appium:unlockStrategy` capability for more details. Optional. Example: "uiautomator"
            timeoutMs (number): The timeout in milliseconds to wait for a successful unlock. See the documentation for the `appium:unlockSuccessTimeout` capability. Optional. Example: 5000

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: unlock", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def is_locked(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: isLocked command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-islocked

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Determine whether the device is locked.

        Returned Result
            Either true or false

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: isLocked", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def set_geolocation(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: setGeolocation command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-setgeolocation

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Sets the emulated geolocation coordinates on the device under test. Supports both real devices and emulators, with additional parameters available depending on the device type.

        Supported arguments:
            latitude (number): Latitude value to set. Required. Example: 32.456
            longitude (number): Longitude value to set. Required. Example: 32.456
            altitude (number): Altitude value in meters. Optional. Defaults to 0. Example: 5.678
            satellites (number): Number of satellites being tracked (1-12). Only available for emulators. Optional. Example: 2
            speed (number): Speed in meters per second. Valid value is 0.0 or greater. Optional. Example: 30.0
            bearing (number): Bearing in degrees at the time of this location. Only available for real devices. Valid range is [0, 360). Optional. Example: 10
            accuracy (number): Horizontal accuracy in meters. Only available for real devices. Valid value is 0.0 or greater. Optional. Example: 10.0

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: setGeolocation", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_geolocation(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getGeolocation command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getgeolocation

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves the current geolocation coordinates from the device under test. If the coordinates are mocked or emulated, the mocked/emulated values will be returned.

        Returned Result:
            A dictionary containing the current geolocation:

            latitude (number): Latitude value. Example: 32.456
            longitude (number): Longitude value. Example: 32.456
            altitude (number): Altitude value in meters. Example: 5.678

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getGeolocation", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def reset_geolocation(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: resetGeolocation command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-resetgeolocation

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Resets mocked geolocation provider to the default/system one. Only works for real devices.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: resetGeolocation", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def refresh_gps_cache(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: refreshGpsCache command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-refreshgpscache

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Sends a request to refresh the GPS cache on the device under test. By default, location tracking is configured for low battery consumption, so this method may need to be called periodically to get updated geolocation values if the device's actual or mocked location changes frequently. This feature works only if Google Play Services are installed on the device. If the device uses the vanilla LocationManager, the device API level must be 30 (Android R) or higher.

        Supported arguments:
            timeoutMs (number): Maximum number of milliseconds to wait for GPS cache refresh. If the API call does not confirm a successful cache refresh within this timeout, an error is thrown. A value of 0 or negative skips waiting and does not check for errors. Default is 20000 ms. Example: 60000

        Returned Result:
            The actual command output. An error is thrown if the GPS cache refresh fails or the timeout is exceeded.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: refreshGpsCache", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def start_media_projection_recording(
        self,
        params: dict[str, Any] | list[Any] | None = None,
    ) -> Any:
        """Execute mobile: startMediaProjectionRecording command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startmediaprojectionrecording

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Starts a new recording of the device screen and audio using the Media Projection API. This API is available since Android 10 (API level 29) and allows high-quality recording. Video and audio encoding is handled by Android, and recording is performed via the Appium Settings helper.

        Supported arguments:
            resolution (string): The resolution of the recorded video. Supported values: "1920x1080", "1280x720", "720x480", "320x240", "176x144". Optional. Default depends on the device, usually Full HD "1920x1080". Example: "1280x720"
            maxDurationSec (number): Maximum duration of the recording in seconds. Optional. Default is 900 seconds (15 minutes). Example: 300
            priority (string): Recording thread priority. Optional. Default is "high". Can be set to "normal" or "low" to reduce performance impact. Example: "low"
            filename (string): Name of the output video file. Must end with ".mp4". Optional. If not provided, the current timestamp is used. Example: "screen.mp4"

        Returned Result:
            Boolean: True if a new recording has successfully started, False if another recording is currently running.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: startMediaProjectionRecording", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def is_media_projection_recording_running(
        self,
        params: dict[str, Any] | list[Any] | None = None,
    ) -> Any:
        """Execute mobile: isMediaProjectionRecordingRunning command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-ismediaprojectionrecordingrunning

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Check if a media projection recording is currently running

        Returned Result:
            true if a recording is running.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: isMediaProjectionRecordingRunning", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def stop_media_projection_recording(
        self,
        params: dict[str, Any] | list[Any] | None = None,
    ) -> Any:
        """Execute mobile: stopMediaProjectionRecording command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-stopmediaprojectionrecording

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Stops the current device recording and retrieves the recently recorded media. If no recording has been started, an error is thrown. If the recording was already finished, the most recent recorded media is returned.

        Supported arguments:
            remotePath (string): Remote location to upload the resulting video. Supported protocols: http, https, ftp. If null or empty, the file content is returned Base64-encoded. Optional. Example: "https://myserver.com/upload"
            user (string): Username for remote authentication. Optional. Example: "admin"
            pass (string): Password for remote authentication. Optional. Example: "pa$$w0rd"
            method (string): HTTP multipart upload method. Default is "PUT". Optional. Example: "POST"
            headers (Map<string, string>): Additional headers for HTTP(S) uploads. Optional. Example: {"Agent": "007"}
            fileFieldName (string): Form field name for file content in HTTP(S) uploads. Default is "file". Optional. Example: "blob"
            formFields (Map<string, string> or Array<Pair>): Additional form fields for HTTP(S) uploads. Optional. Example: {"name": "yolo.mp4"}
            uploadTimeout (number): Maximum time in milliseconds to wait for file upload. Default is 240000 ms. Optional. Example: 30000

        Returned Result:
            Base64-encoded content of the recorded media file if `remotePath` is falsy or empty. Otherwise, the result depends on the upload response.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: stopMediaProjectionRecording", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_connectivity(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getConnectivity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getconnectivity

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Returns the connectivity states for various services on the device under test.

        Supported arguments:
            services (string or Array<string>): One or more service names to query connectivity for. Supported values: "wifi", "data", "airplaneMode". If not provided, all supported services are returned by default. Optional. Example: ["wifi", "data"]

        Returned Result:
            A map containing the connectivity state of each requested service. Possible keys include:
                wifi (boolean): True if Wi-Fi is enabled.
                data (boolean): True if mobile data connection is enabled.
                airplaneMode (boolean): True if Airplane Mode is enabled.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getConnectivity", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def set_connectivity(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: setConnectivity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-setconnectivity

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Sets the connectivity state for various services on the device under test. At least one service must be specified. Missing values indicate that the corresponding service state should not be changed.

        Note:
                - Switching Wi-Fi and mobile data states works reliably on emulators for all Android versions. On real devices, proper state switching is supported only from Android 11 onward.
                - The UiAutomator2 REST server app may be terminated or disconnected by Android when using this API, which can cause the driver session to fail. To restore the session, quit it after changing the network state and then reopen it with the noReset capability set to true once connectivity is restored.

        Supported arguments:
            wifi (boolean): Whether to enable or disable Wi-Fi. Optional. Example: False
            data (boolean): Whether to enable or disable mobile data. Optional. Example: False
            airplaneMode (boolean): Whether to enable or disable Airplane Mode. Optional. Example: False

        Returned Result:
            The actual command output. An error is thrown if execution fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: setConnectivity", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_app_strings(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getAppStrings command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getappstrings

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves string resources for the specified app language. An error is thrown if the strings cannot be fetched or if no strings exist for the given language abbreviation. Available since driver version 2.15.0.

        Supported arguments:
            language (string): The language abbreviation to fetch app strings for. If not provided, strings for the default language on the device under test will be returned. Optional. Example: "fr"

        Returned Result:
            A dictionary mapping resource identifiers to string values for the given language. An error is thrown if execution fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getAppStrings", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def hide_keyboard(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: hideKeyboard command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-hidekeyboard

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Attempts to hide the on-screen keyboard on the device under test. Throws an exception if the keyboard cannot be hidden. Does nothing if the keyboard is already hidden.

        Supported arguments:
            This method does not accept any arguments.

        Returned Result:
            Boolean: True if the keyboard was successfully hidden, or False if it was already invisible. An error is thrown if execution fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: hideKeyboard", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def is_keyboard_shown(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: isKeyboardShown command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-iskeyboardshown

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Checks whether the system on-screen keyboard is currently visible on the device under test.

        Supported arguments:
            This method does not accept any arguments.

        Returned Result:
            Boolean: True if the keyboard is visible, False otherwise. An error is thrown if execution fails.


        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: isKeyboardShown", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def press_key(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: pressKey command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-presskey

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Emulates a single key press event on the device under test using the specified Android key code. Available since driver version 2.17.0.

        Supported arguments:
            keycode (number): A valid Android key code representing the key to press. Required. Example: 0x00000099 (KEYCODE_NUMPAD_9)
            metastate (number): An integer in which each bit set to 1 represents a pressed meta key (e.g., SHIFT, ALT). Optional. Example: 0x00000010 (META_ALT_LEFT_ON)
            flags (number): Flags for the key event as defined in KeyEvent documentation. Optional. Example: 0x00000001 (FLAG_WOKE_HERE)
            isLongPress (boolean): Whether to emulate a long key press. False by default. Optional. Example: True

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: pressKey", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def background_app(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: backgroundApp command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-backgroundapp

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Puts the app under test to the background for a specified duration and optionally restores it afterward. This call is blocking. Available since driver version 2.19.0.

        Supported arguments:
            seconds (number): The amount of seconds to wait between putting the app to background and restoring it. Negative values indicate that the app should not be restored (default behavior). Optional. Example: 5

        Returned Result:
            The actual command output. An error is thrown if the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: backgroundApp", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_current_activity(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getCurrentActivity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getcurrentactivity

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves the name of the currently focused app activity on the device under test. Available since driver version 2.20.

        Supported arguments:
            None

        Returned Result:
            The activity class name as a string. Could be None if no activity is currently focused.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getCurrentActivity", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_current_package(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getCurrentPackage command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getcurrentpackage

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves the package identifier of the currently focused app on the device under test. Available since driver version 2.20.

        Supported arguments:
            None

        Returned Result:
            The package class name as a string. Could be None if no app is currently focused.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getCurrentPackage", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_display_density(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getDisplayDensity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getdisplaydensity

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves the display density of the device under test in dots per inch (DPI). Available since driver version 2.21.

        Supported arguments:
            None

        Returned Result:
            The display density as an integer value representing DPI.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getDisplayDensity", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_system_bars(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getSystemBars command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getsystembars

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves properties of various system bars on the device under test. Available since driver version 2.21.

        Supported arguments:
            None

        Returned Result:
            A dictionary containing entries for 'statusBar' and 'navigationBar'. Each entry is a dictionary with the following properties:
                visible (boolean): True if the bar is visible; false if the bar is not present.
                x (number): X coordinate of the bar; may be 0 if the bar is not present.
                y (number): Y coordinate of the bar; may be 0 if the bar is not present.
                width (number): Width of the bar; may be 0 if the bar is not present.
                height (number): Height of the bar; may be 0 if the bar is not present.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getSystemBars", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def fingerprint(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: fingerprint command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-fingerprint

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Emulates a fingerprint scan on the Android Emulator. Only works on API level 23 and above. Available since driver version

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: fingerprint", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def send_sms(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: sendSms command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-sendsms

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Emulates sending an SMS to a specified phone number on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Supported arguments:
            phoneNumber (string): The phone number to which the SMS should be sent. Required. Example: '0123456789'
            message (string): The content of the SMS message. Required. Example: 'Hello'

        Returned Result:
            The actual command output. An error is thrown if SMS emulation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: sendSms", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def gsm_call(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: gsmCall command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-gsmcall

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Emulates a GSM call to a specified phone number on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Supported arguments:
            phoneNumber (string): The phone number to call. Required. Example: '0123456789'
            action (string): The action to perform on the call. Must be one of 'call', 'accept', 'cancel', or 'hold'. Required. Example: 'accept'

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: gsmCall", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def gsm_signal(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: gsmSignal command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-gsmsignal

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Emulates a GSM signal strength change event on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Supported arguments:
            strength (int): Signal strength value to emulate. Must be one of 0, 1, 2, 3, or 4, where 4 is the best signal. Required. Example: 3

        Returned Result:
            The actual command output. An error is thrown if GSM signal emulation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: gsmSignal", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def gsm_voice(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: gsmVoice command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-gsmvoice

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Emulates a GSM voice state change event on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Supported arguments:
            state (str): Voice state to emulate. Must be one of 'on', 'off', 'denied', 'searching', 'roaming', 'home', or 'unregistered'. Required. Example: 'off'

        Returned Result:
            The actual command output. An error is thrown if GSM voice state emulation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: gsmVoice", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def power_ac(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: powerAC command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-powerac

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Emulates an AC power state change on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Supported arguments:
            state (str): AC power state to emulate. Must be either 'on' or 'off'. Required. Example: 'off'

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: powerAC", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def power_capacity(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: powerCapacity command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-powercapacity

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Emulates a change in battery power capacity on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Supported arguments:
            percent (int): Battery percentage to emulate, must be in the range 0 to 100. Required. Example: 50

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: powerCapacity", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def network_speed(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: networkSpeed command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-networkspeed

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Emulates different mobile network connection speed modes on an Android Emulator. Only works on emulators. Available since driver version 2.22.

        Supported arguments:
            speed (str): The mobile network speed mode to emulate. Supported values are "gsm", "scsd", "gprs", "edge", "umts", "hsdpa", "lte", "evdo", or "full". Required. Example: "edge"

        Returned Result:
            The actual command output. An error is thrown if network speed emulation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: networkSpeed", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def replace_element_value(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        r"""Execute mobile: replaceElementValue command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-replaceelementvalue

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Sends a text to the specified element by replacing its previous content. If the text ends with "\\n" (backslash must be escaped, so it is not translated into 0x0A), the Enter key press will be emulated after typing. Available since driver version 2.22.

        Supported arguments:
            elementId (str): Hexadecimal identifier of the target text input element. Required. Example: "123456-3456-3435-3453453"
            text (str): The text to enter. Can include Unicode characters. If ending with "\\n", the Enter key is emulated after typing (the "\\n" substring itself is removed). Required. Example: "yolo"

        Returned Result:
            The actual command output. An error is thrown if sending text fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: replaceElementValue", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def toggle_gps(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: toggleGps command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-togglegps

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Switches GPS setting state. This API only works reliably since Android 12 (API 31). Available since driver version 2.23.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: toggleGps", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def is_gps_enabled(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: isGpsEnabled command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-isgpsenabled

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Returns true if GPS is enabled on the device under test. Available since driver version 2.23.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: isGpsEnabled", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_performance_data_types(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getPerformanceDataTypes command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getperformancedatatypes

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Fetches the list of supported performance data types that can be used as the `dataType` argument for the `mobile: getPerformanceData` extension. Available since driver version 2.24.

        Supported arguments:
            This command does not require any arguments.

        Returned Result:
            List[str]: A list of supported performance data type names.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getPerformanceDataTypes", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_performance_data(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getPerformanceData command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getperformancedata

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves performance data about the specified Android subsystem for a given app. The data is parsed from the output of the `dumpsys` utility. Available since driver version 2.24.

        Supported arguments:
            packageName (str): The package identifier of the app to fetch performance data for. Required. Example: "com.myapp"
            dataType (str): The subsystem name for which to retrieve performance data. Must be one of the values returned by `mobile: getPerformanceDataTypes`. Required. Example: "batteryinfo" or "cpuinfo" or "memoryinfo" or "networkinfo"

        Returned Result:
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
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getPerformanceData", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def status_bar(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: statusBar command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-statusbar

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Performs operations on the system status bar using the `adb shell cmd statusbar` CLI. Only works on Android 8 (Oreo) and newer. Available since driver version 2.25.

        Supported arguments:
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

        Returned Result:
            str: The actual output from the underlying status bar command. The output depends on the selected command and may be empty.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: statusBar", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def schedule_action(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: scheduleAction command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-scheduleaction

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Adds a new scheduled action consisting of one or more sequential steps. Each step is executed in order, and the overall action is considered failed if at least one step fails. The action can be configured with limits on rescheduling, execution times, and history retention.

        Supported arguments:
            name (str): Unique name of the action. Required. Example: "popupHandlingAction"
            steps (List[dict]): List of action steps to execute. Steps are executed sequentially. Required. Example: [{"type": "gesture", "name": "click", "payload": {"subtype": "click", "locator": {"strategy": "id", "selector": "buttonIdentifier"}}}]
            maxPass (int): Maximum number of times the action can pass before it stops rescheduling. Optional. Example: 1
            maxFail (int): Maximum number of times the action can fail before it stops rescheduling. Optional. Example: 1
            times (int): Total number of times the action should execute. Defaults to 1. Optional. Example: 10
            intervalMs (int): Interval in milliseconds between reschedules. Defaults to 1000 ms. Optional. Example: 100
            maxHistoryItems (int): Maximum number of history items stored for this action. Defaults to 20. Optional. Example: 100

        Action Step arguments:
            type (str): Step type. One of "gesture", "source", or "screenshot". Required. Example: "gesture"
            name (str): Step name for tracking execution history. Required. Example: "click"
            payload (dict): Step payload. Required. Format depends on step type and subtype.

        Step payload examples:
            gesture (subtype: click): {"subtype": "click", "locator": {"strategy": "id", "selector": "buttonIdentifier"}}
            gesture (subtype: longClick): {"subtype": "longClick", "locator": {"strategy": "accessibility id", "selector": "buttonIdentifier"}}
            gesture (subtype: doubleClick): {"subtype": "doubleClick", "elementId": "yolo", "x": 150, "y": 200}
            source (subtype: xml): {"subtype": "xml"}
            screenshot (subtype: png): {"subtype": "png"}

        Returned Result:
            The actual command output. An error is thrown if adding the action fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: scheduleAction", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def unschedule_action(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: unscheduleAction command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-unscheduleaction

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Unschedules a previously scheduled action from asynchronous execution and returns its execution history. Useful for stopping actions that repeatedly interact with the application (e.g., polling UI snapshots or automating popups) and analyzing what steps were executed.

        Supported arguments:
            name (str): Unique name of the action to unschedule. Required. Example: "popupHandlingAction"

        Returned Result:
            Dict containing the execution history of the unscheduled action. The structure matches the output of the `mobile: getActionHistory` endpoint, including step results, timestamps, and pass/fail statuses.

        Usage Example:
            # Schedule an action to capture page source snapshots every second for 30 seconds
            driver.execute_script('mobile: scheduleAction', {
                'name': 'myPopupHandlingAction',
                'steps': [{
                    'type': 'source',
                    'name': 'fetchPageSourceStep',
                    'payload': {'subtype': 'xml'}
                }],
                'intervalMs': 1000,
                'times': 30,
                'maxHistoryItems': 30,
            })

            # Later, unschedule the action and retrieve its history
            history: Dict[str, Any] = driver.execute_script('mobile: unscheduleAction', {
                'name': 'myPopupHandlingAction',
            })

            # Example function to check if all steps in an execution passed
            def did_execution_pass(execution: List[Dict]) -> bool:
                return all(step['passed'] for step in execution)

            # Assert that at least one execution fully passed
            assert any(did_execution_pass(execution) for execution in history['stepResults'])

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: unscheduleAction", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_action_history(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getActionHistory command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getactionhistory

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves the execution history of a previously scheduled action. Each action run and its individual steps are recorded, including pass/fail status, results, timestamps, and any exceptions that occurred. An error is thrown if no action with the given name has been scheduled or if it has already been unscheduled.

        Supported arguments:
            name (str): Unique name of the action whose history is being requested. Required. Example: "popupHandlingAction"

        Returned Result:
            Dict containing the action execution history:

            repeats (int): Number of times this action has been executed so far. Example: 1

            stepResults (List[List[Dict]]): History of step executions for each action run. The outer list is sorted by execution timestamp in descending order. Its maximum length is limited by the action's maxHistoryItems value. Each step execution is represented as a dictionary with the following keys:

                name (str): Name of the corresponding step. Example: "clickStep"
                type (str): Type of the step. Example: "gesture"
                timestamp (int): Unix timestamp in milliseconds when the step execution started. Example: 1685370112000
                passed (bool): True if the step completed successfully (no exceptions), False otherwise. Example: True
                result (Any): Actual step result, dependent on step type and subtype. Null if an exception occurred. Example: "something"
                exception (Dict or None): If the step threw an exception, this dictionary contains:
                    name (str): Exception class name. Example: "java.lang.Exception"
                    message (str): Exception message. Example: "Bad things happen"
                    stacktrace (str): Full exception stack trace. Example: "happened somewhere"
                If no exception occurred, this value is None.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getActionHistory", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def screenshots(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: screenshots command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-screenshots

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Captures a screenshot of each display available on the Android device. This functionality is supported on Android 10 and newer.

        Supported arguments:
            displayId (int or str, optional): Identifier of the display to capture. If not provided, screenshots for all displays will be returned. If the specified display does not exist, an error is thrown. Display identifiers can be retrieved using `adb shell dumpsys SurfaceFlinger --display-id`. Example: 1

        Returned Result:
            Dict[str, Dict]: A dictionary where each key is a display identifier and each value is a dictionary with the following keys:

                id (int or str): The display identifier. Example: 1
                name (str): Display name. Example: "Built-in Display"
                isDefault (bool): True if this display is the default display, False otherwise. Example: True
                payload (str): PNG screenshot data encoded as a base64 string. Example: "iVBORw0KGgoAAAANSUhEUgAA..."

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: screenshots", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def set_ui_mode(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: setUiMode command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-setuimode

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Sets the device UI appearance using a thin wrapper over `adb shell cmd uimode`. Supported on Android 10 and newer.

        Supported arguments:
            mode (str): The UI mode to configure. Supported values are:
                - "night": Night mode
                - "car": Car mode
              Example: "night"

            value (str): The value to apply for the selected UI mode. Supported values depend on the mode:
                - night: "yes", "no", "auto", "custom_schedule", "custom_bedtime"
                - car: "yes", "no"
              Example: "yes" (to enable night/dark mode)

        Returned Result:
            The actual command output. An error is thrown if command execution fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: setUiMode", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_ui_mode(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getUiMode command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getuimode

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves the current device UI appearance for the specified mode using a thin wrapper over `adb shell cmd uimode`. Supported on Android 10 and newer.

        Supported arguments:
            mode (str): The UI mode to query. Supported values are:
                - "night": Night mode
                - "car": Car mode
              Example: "night"

        Returned Result:
            str: The current value of the specified UI mode. Supported values depend on the mode:
                - night: "yes", "no", "auto", "custom_schedule", "custom_bedtime"
                - car: "yes", "no"

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getUiMode", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def send_trim_memory(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: sendTrimMemory command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-sendtrimmemory

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Simulates the `onTrimMemory()` event for a given Android package. This allows testing the app's behavior under various memory pressure conditions. For more details, see "Manage your app's memory". Supported since driver version 2.41.

        Supported arguments:
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

        Returned Result:
            The actual command output. An error is thrown if the simulation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: sendTrimMemory", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def inject_emulator_camera_image(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: injectEmulatorCameraImage command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-injectemulatorcameraimage

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Simulates an image injection into the VirtualScene emulator camera foreground. After a successful call, the supplied PNG image will appear as the camera's foreground scene (useful for testing QR/barcode scanners, OCR, etc.). This only works on Android emulators. Available since driver version 3.2.0.

        Supported arguments:
            payload (string): Base64-encoded PNG image payload. Only PNG is supported. Required. Example: "iVBORw0KGgoAAAANSUh..."

        Required preconditions:
            - This feature only works on Android emulators.
            - For newly created or reset emulators you must provide the `appium:injectedImageProperties` capability (it may be an empty map to use defaults) so the emulator is prepared for image injection.
            - Alternatively, you may configure the emulator manually by editing `$ANDROID_HOME/emulator/resources/Toren1BD.posters` as described in the docs (replace contents, save, then restart the emulator). This manual step is only necessary if you prefer not to restart the emulator during session startup.

        Returned Result:
            Boolean: True if the image was injected successfully. An error is thrown if the operation fails (for example, if the payload is not a valid base64 PNG or the emulator is not prepared).

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: injectEmulatorCameraImage", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def bluetooth(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: bluetooth command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-bluetooth

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Allows controlling the Bluetooth adapter on the device under test. An error is thrown if the device has no default Bluetooth adapter. Available since driver version 3.4.0.

        Supported arguments:
            action (string): The action to execute on the Bluetooth adapter. Supported values are:
                - "enable": Turns the Bluetooth adapter on.
                - "disable": Turns the Bluetooth adapter off.
                - "unpairAll": Unpairs all currently paired devices.
              Calling the same action multiple times has no effect. Required. Example: "disable"

        Returned Result:
            Boolean: True if the action was successfully executed. An error is thrown if the device has no Bluetooth adapter or if the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: bluetooth", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def nfc(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: nfc command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-nfc

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Allows controlling the NFC adapter on the device under test. An error is thrown if the device has no default NFC adapter. Available since driver version 3.4.0.

        Supported arguments:
            action (string): The action to execute on the NFC adapter. Supported values are:
                - "enable": Turns the NFC adapter on.
                - "disable": Turns the NFC adapter off.
              Calling the same action multiple times has no effect. Required. Example: "disable"

        Returned Result:
            Boolean: True if the action was successfully executed. An error is thrown if the device has no NFC adapter or if the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: nfc", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def pull_file(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: pullFile command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-pullfile

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Pulls a remote file from the device. Supports pulling files from standard device paths or from app bundles (debugging must be enabled for app bundle access).

        Supported arguments:
            remotePath (string): The full path to the remote file or a specially formatted path inside an app bundle (e.g., "@my.app.id/my/path"). Required. Example: "/sdcard/foo.bar"

        Returned Result:
            string: Base64-encoded content of the remote file. An error is thrown if the file does not exist or if the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: pullFile", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def push_file(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: pushFile command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-pushfile

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Pushes a local file to the device. If a file already exists at the target path, it will be silently overwritten.

        Supported arguments:
            remotePath (string): The path on the device where the file should be written. Required. Example: "/sdcard/foo.bar"
            payload (string): Base64-encoded content of the file to be pushed. Required. Example: "QXBwaXVt"

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: pushFile", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def pull_folder(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: pullFolder command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-pullfolder

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Pulls a remote folder from the device. The folder content is zipped and returned as a Base64-encoded string.

        Supported arguments:
            remotePath (string): The path to the remote folder on the device. Required. Example: "/sdcard/yolo/"

        Returned Result:
            Base64-encoded string representing the zipped content of the remote folder. An error is thrown if the folder does not exist or the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: pullFolder", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_clipboard(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: getClipboard command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getclipboard

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Retrieves the plaintext content of the device's clipboard.

        Supported arguments:
            This command does not require any arguments.

        Returned Result:
            Base64-encoded string representing the clipboard content. Returns an empty string if the clipboard is empty. An error is thrown if the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: getClipboard", params)

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def set_clipboard(self, params: dict[str, Any] | list[Any] | None = None) -> Any:
        """Execute mobile: setClipboard command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-setclipboard

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        Description:
            Sets the plain text content of the device's clipboard.

        Supported arguments:
            content (string): Base64-encoded clipboard payload. Required. Example: 'YXBwaXVt'
            contentType (string): The type of content to set. Only 'plaintext' is supported and is used by default. Optional. Example: 'plaintext'
            label (string): Optional label to identify the current clipboard payload. Optional. Example: 'yolo'

        Returned Result:
            The actual command output. An error is thrown if the operation fails.

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: setClipboard", params)

    def _execute(self, name: str, params: dict[str, Any] | list[Any] | None) -> Any:
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
        driver = WebDriverSingleton.get_driver()
        return driver.execute_script(name, params or {})  # type: ignore[reportUnknownMemberType]
