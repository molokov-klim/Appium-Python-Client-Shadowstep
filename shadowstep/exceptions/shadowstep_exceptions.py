"""Custom exceptions for the Shadowstep framework.

This module defines custom exception classes that extend standard
Selenium and Appium exceptions to provide more specific error handling
and context for the Shadowstep automation framework.
"""
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
            stacktrace: Sequence[str] | None = None,
    ) -> None:
        """Initialize the ShadowstepException.

        Args:
            msg: Error message.
            screen: Screenshot data.
            stacktrace: Stack trace information.

        """
        super().__init__(msg, screen, stacktrace)


class ShadowstepElementError(ShadowstepException):
    """Raised when an element operation fails with additional context.

    This exception provides additional context about the original exception
    that caused the element operation to fail, including the traceback.
    """

    def __init__(self,
                 message: str | None = None,
                 original_exception: Exception | None = None):
        """Initialize the ShadowstepElementError.

        Args:
            message: Error message.
            original_exception: The original exception that caused this error.

        """
        super().__init__(message)
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class ShadowstepNoSuchElementError(NoSuchElementException):
    """Raised when an element cannot be found with enhanced locator information.

    This exception extends the standard NoSuchElementException to provide
    additional context about the locator that was used and other debugging
    information.
    """

    def __init__(self,
                 msg: str | None = None,
                 screen: str | None = None,
                 stacktrace: list[Any] | None = None,
                 locator: Any = None):
        """Initialize the ShadowstepNoSuchElementError.

        Args:
            msg: Error message.
            screen: Screenshot data.
            stacktrace: Stack trace information.
            locator: The locator that was used to find the element.

        """
        super().__init__(msg, screen, stacktrace)
        self.locator = locator
        self.msg = msg
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self):
        """Return string representation of the exception with locator and context info.

        Returns:
            str: Formatted string containing locator, message, and stacktrace.

        """
        return f"ShadowstepNoSuchElementError: Locator: {self.locator} \n Message: {self.msg} \n Stacktrace: {self.stacktrace}"


class ShadowstepTimeoutException(TimeoutException):
    """Custom timeout exception with additional context."""

    def __init__(self,
                 msg: str | None = None,
                 screen: str | None = None,
                 stacktrace: list[Any] | None = None,
                 locator: Any = None,
                 driver: WebDriver | None = None):
        """Initialize the ShadowstepTimeoutException.

        Args:
            msg: Error message.
            screen: Screenshot data.
            stacktrace: Stack trace information.
            locator: The locator that was used to find the element.
            driver: The WebDriver instance.

        """
        super().__init__(msg, screen, stacktrace)
        self.locator = locator
        self.driver = driver
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def __str__(self):
        """Return string representation of the timeout exception with detailed context.

        Returns:
            str: Formatted string containing timestamp, message, locator, URL, and stacktrace.

        """
        return (f"ShadowstepTimeoutException\n"
                f"Timestamp: {self.timestamp}\n"
                f"Message: {self.msg}\n"
                f"Locator: {self.locator}\n"
                f"Current URL: {self.driver.current_url if self.driver else 'N/A'}\n"
                f"Stacktrace:\n{''.join(self.stacktrace) if self.stacktrace else 'N/A'}")


class ShadowstepElementException(WebDriverException):
    """Raised when driver is not specified and cannot be located."""

    def __init__(
            self, msg: str | None = None, screen: str | None = None,
            stacktrace: Sequence[str] | None = None,
    ) -> None:
        """Initialize the ShadowstepElementException.

        Args:
            msg: Error message.
            screen: Screenshot data.
            stacktrace: Stack trace information.

        """
        super().__init__(msg, screen, stacktrace)


class ShadowstepLocatorConverterError(Exception):
    """Base exception for locator conversion errors."""



class ShadowstepInvalidUiSelectorError(Exception):
    """Raised when UiSelector string is malformed."""



class ShadowstepConversionError(ShadowstepLocatorConverterError):
    """Raised when conversion between formats fails."""



class ShadowstepResolvingLocatorError(Exception):
    """Raised when locator resolving is failed (used in shadowstep.element.dom)."""


