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

from shadowstep.decorators.decorators import fail_safe
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException
from shadowstep.shadowstep_base import WebDriverSingleton
from shadowstep.utils.utils import get_current_func_name


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

        """
        self.logger.debug("%s", get_current_func_name())
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
        """Execute mobile: listSms command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-listsms

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

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
        """Execute mobile: getContexts command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getcontexts

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

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
        self, params: dict[str, Any] | list[Any] | None = None,
    ) -> Any:
        """Execute mobile: startMediaProjectionRecording command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startmediaprojectionrecording

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

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
        self, params: dict[str, Any] | list[Any] | None = None,
    ) -> Any:
        """Execute mobile: isMediaProjectionRecordingRunning command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-ismediaprojectionrecordingrunning

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

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
        self, params: dict[str, Any] | list[Any] | None = None,
    ) -> Any:
        """Execute mobile: stopMediaProjectionRecording command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-stopmediaprojectionrecording

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

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
        """Execute mobile: replaceElementValue command.

        https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-replaceelementvalue

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

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

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: setClipboard", params)

    def _execute(self, name: str, params: dict[str, Any] | list[Any] | None) -> Any:
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
        driver = WebDriverSingleton.get_driver()
        return driver.execute_script(name, params or {})  # type: ignore[reportUnknownMemberType]
