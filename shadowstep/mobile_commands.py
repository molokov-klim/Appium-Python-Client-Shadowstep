"""Mobile commands for Appium automation.

This module provides a comprehensive set of mobile commands for Appium automation,
including app management, device information, clipboard operations, and more.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
)

if TYPE_CHECKING:
    from shadowstep.shadowstep import Shadowstep
from shadowstep.decorators.decorators import fail_safe
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException
from shadowstep.shadowstep_base import WebDriverSingleton
from shadowstep.utils.utils import get_current_func_name


class MobileCommands:
    """Mobile commands wrapper for Appium automation.

    This class provides a comprehensive set of mobile commands for Appium automation,
    including app management, device information, clipboard operations, and more.
    """

    def __init__(self, shadowstep: Shadowstep) -> None:
        """Initialize MobileCommands instance.

        Args:
            shadowstep: Shadowstep instance for mobile command execution.

        """
        self.shadowstep = shadowstep
        self.driver: Any = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def battery_info(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: batteryInfo command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-batteryinfo

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: batteryInfo", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def device_info(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: deviceInfo command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-deviceinfo

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: deviceInfo", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_clipboard(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: getClipboard command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-getclipboard

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: getClipboard", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_current_activity(
        self,
        params: dict[str, Any] | list[Any] | None = None,
    ) -> MobileCommands:
        """Execute mobile: getCurrentActivity command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-getcurrentactivity

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: getCurrentActivity", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_current_package(
        self,
        params: dict[str, Any] | list[Any] | None = None,
    ) -> MobileCommands:
        """Execute mobile: getCurrentPackage command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-getcurrentpackage

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: getCurrentPackage", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_device_time(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: getDeviceTime command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-getdevicetime

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: getDeviceTime", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_performance_data(
        self,
        params: dict[str, Any] | list[Any] | None = None,
    ) -> MobileCommands:
        """Execute mobile: getPerformanceData command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-getperformancedata

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: getPerformanceData", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def get_performance_data_types(
        self,
        params: dict[str, Any] | list[Any] | None = None,
    ) -> MobileCommands:
        """Execute mobile: getPerformanceDataTypes command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-getperformancedatatypes

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: getPerformanceDataTypes", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def hide_keyboard(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: hideKeyboard command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-hidekeyboard

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: hideKeyboard", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def open_notifications(
        self,
        params: dict[str, Any] | list[Any] | None = None,
    ) -> MobileCommands:
        """Execute mobile: openNotifications command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-opennotifications

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: openNotifications", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def press_key(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: pressKey command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-presskey

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: pressKey", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def set_clipboard(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: setClipboard command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-setclipboard

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: setClipboard", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def shell(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: shell command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-shell

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: shell", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def start_logs_broadcast(
        self,
        params: dict[str, Any] | list[Any] | None = None,
    ) -> MobileCommands:
        """Execute mobile: startLogsBroadcast command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-startlogsbroadcast

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: startLogsBroadcast", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
            NoSuchDriverException,
            InvalidSessionIdException,
            StaleElementReferenceException,
        ),
    )
    def stop_logs_broadcast(
        self,
        params: dict[str, Any] | list[Any] | None = None,
    ) -> MobileCommands:
        """Execute mobile: stopLogsBroadcast command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-stoplogsbroadcast

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: stopLogsBroadcast", params)
        return self

    def _execute(self, name: str, params: dict[str, Any] | list[Any] | None) -> None:
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
        self.driver = WebDriverSingleton.get_driver()
        if self.driver is None:
            error_msg = "WebDriver is not available"
            raise ShadowstepException(error_msg)
        self.driver.execute_script(name, params or {})
