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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def activate_app(self, params: dict[str, Any] | list[Any]) -> MobileCommands:
        """Execute mobile: activateApp command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-activateapp

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: activateApp", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def clear_element(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: clearElement command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-clearelement

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: clearElement", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def fingerprint(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: fingerprint command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-fingerprint

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: fingerprint", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def get_current_activity(
            self, params: dict[str, Any] | list[Any] | None = None,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def get_current_package(
            self, params: dict[str, Any] | list[Any] | None = None,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def get_performance_data(
            self, params: dict[str, Any] | list[Any] | None = None,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def get_performance_data_types(
            self, params: dict[str, Any] | list[Any] | None = None,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def get_settings(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: getSettings command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-getsettings

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: getSettings", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def install_app(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: installApp command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-installapp

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: installApp", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def is_app_installed(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: isAppInstalled command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-isappinstalled

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: isAppInstalled", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def long_press_key(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: longPressKey command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-longpresskey

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: longPressKey", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def open_notifications(
            self, params: dict[str, Any] | list[Any] | None = None,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def open_settings(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: openSettings command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-opensettings

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: openSettings", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def query_app_state(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: queryAppState command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-queryappstate

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: queryAppState", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def remove_app(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: removeApp command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-removeapp

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: removeApp", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def replace_element_value(
            self, params: dict[str, Any] | list[Any] | None = None,
    ) -> MobileCommands:
        """Execute mobile: replaceElementValue command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-replaceelementvalue

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: replaceElementValue", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def scroll_back_to(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: scrollBackTo command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollbackto

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: scrollBackTo", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def send_sms(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: sendSMS command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-sendsms

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: sendSMS", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def set_text(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: setText command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-settext

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: setText", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def start_activity(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: startActivity command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-startactivity

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: startActivity", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def start_logs_broadcast(
            self, params: dict[str, Any] | list[Any] | None = None,
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
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def stop_logs_broadcast(
            self, params: dict[str, Any] | list[Any] | None = None,
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

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def terminate_app(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: terminateApp command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-terminateapp

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: terminateApp", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def toggle_location_services(
            self, params: dict[str, Any] | list[Any] | None = None,
    ) -> MobileCommands:
        """Execute mobile: toggleLocationServices command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-togglelocationservices

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: toggleLocationServices", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def update_settings(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: updateSettings command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-updatesettings

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: updateSettings", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def get_text(self, params: dict[str, Any] | list[Any] | None = None) -> MobileCommands:
        """Execute mobile: getText command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-gettext

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: getText", params)
        return self

    @fail_safe(
        raise_exception=ShadowstepException,
        exceptions=(
                NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException,
        ),
    )
    def perform_editor_action(
            self, params: dict[str, Any] | list[Any] | None = None,
    ) -> MobileCommands:
        """Execute mobile: performEditorAction command.

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-performeditoraction

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.

        """
        self.logger.debug("%s", get_current_func_name())
        self._execute("mobile: performEditorAction", params)
        return self

    def _execute(self, name: str, params: dict[str, Any] | list[Any] | None) -> None:
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
        self.driver = WebDriverSingleton.get_driver()
        if self.driver is None:
            error_msg = "WebDriver is not available"
            raise ShadowstepException(error_msg)
        self.driver.execute_script(name, params or {})
