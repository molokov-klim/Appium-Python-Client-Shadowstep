# shadowstep/exceptions/shadowstep_exceptions.py
from __future__ import annotations

import datetime
import traceback
from collections.abc import Sequence
from typing import Any

from appium.webdriver.webdriver import WebDriver
from selenium.common import NoSuchElementException, TimeoutException, WebDriverException


class ShadowstepException(WebDriverException):
    """Raised when driver is not specified and cannot be located."""

    def __init__(
            self,
            msg: str | None = None,
            screen: str | None = None,
            stacktrace: Sequence[str] | None = None
    ) -> None:
        super().__init__(msg, screen, stacktrace)


class ShadowstepElementError(ShadowstepException):
    def __init__(self,
                 message: str | None = None,
                 original_exception: Exception | None = None):
        super().__init__(message)
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class ShadowstepNoSuchElementError(NoSuchElementException):
    def __init__(self,
                 msg: str | None = None,
                 screen: str | None = None,
                 stacktrace: list[Any] | None = None,
                 locator: tuple[Any, Any] | dict[str, str] | str | None = None):
        super().__init__(msg, screen, stacktrace)
        self.locator = locator
        self.msg = msg
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self):
        return f"ShadowstepNoSuchElementError: Locator: {self.locator} \n Message: {self.msg} \n Stacktrace: {self.stacktrace}"


class ShadowstepTimeoutException(TimeoutException):
    """Custom timeout exception with additional context."""

    def __init__(self,
                 msg: str | None = None,
                 screen: str | None = None,
                 stacktrace: list[Any] | None = None,
                 locator: tuple[Any, Any] | dict[str, str] | None = None,
                 driver: WebDriver | None = None):
        super().__init__(msg, screen, stacktrace)
        self.locator = locator
        self.driver = driver
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def __str__(self):
        return (f"ShadowstepTimeoutException\n"
                f"Timestamp: {self.timestamp}\n"
                f"Message: {self.msg}\n"
                f"Locator: {self.locator}\n"
                f"Current URL: {self.driver.current_url if self.driver else 'N/A'}\n"
                f"Stacktrace:\n{''.join(self.stacktrace) if self.stacktrace else 'N/A'}")

class GeneralElementException(WebDriverException):
    """Raised when driver is not specified and cannot be located."""

    def __init__(
            self, msg: str | None = None, screen: str | None = None,
            stacktrace: Sequence[str] | None = None
    ) -> None:
        super().__init__(msg, screen, stacktrace)


class LocatorConverterError(Exception):
    """Base exception for locator conversion errors."""
    pass


class InvalidUiSelectorError(LocatorConverterError):
    """Raised when UiSelector string is malformed."""
    pass


class ConversionError(LocatorConverterError):
    """Raised when conversion between formats fails."""
    pass
