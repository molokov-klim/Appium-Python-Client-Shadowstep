"""Mobile commands for Appium automation.

This module provides a comprehensive set of mobile commands for Appium automation,
including app management, device information, clipboard operations, and more.
"""

from __future__ import annotations

import logging
from typing import Any

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
)

from shadowstep.decorators.decorators import fail_safe
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException
from shadowstep.shadowstep_base import WebDriverSingleton
from shadowstep.utils.utils import get_current_func_name


class MobileCommands:
    """Mobile commands wrapper for Appium automation.

    This class provides a comprehensive set of mobile commands for Appium automation,
    including app management, device information, clipboard operations, and more.
    """

    def __init__(self) -> None:
        """Initialize MobileCommands instance."""
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

        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-shell

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Any: result of script execution

        """
        self.logger.debug("%s", get_current_func_name())
        return self._execute("mobile: longClickGesture", params)

    def _execute(self, name: str, params: dict[str, Any] | list[Any] | None) -> Any:
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
        self.driver = WebDriverSingleton.get_driver()
        if self.driver is None:
            error_msg = "WebDriver is not available"
            raise ShadowstepException(error_msg)
        return self.driver.execute_script(name, params or {})
