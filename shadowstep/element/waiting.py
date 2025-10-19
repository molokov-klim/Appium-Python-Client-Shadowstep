"""Element waiting module for Shadowstep framework.

This module provides waiting functionality for elements,
including visibility, clickability, and presence checks.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from selenium.common import (
    TimeoutException,
)
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

from shadowstep.decorators.common_decorators import log_debug
from shadowstep.element import conditions

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.element.utilities import ElementUtilities
    from shadowstep.locator import LocatorConverter
    from shadowstep.shadowstep import Shadowstep


class ElementWaiting:
    """Element waiting handler for Shadowstep framework."""

    def __init__(self, element: Element) -> None:
        """Initialize ElementWaiting.

        Args:
            element: The element to perform waiting operations on.

        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    @log_debug()
    def wait(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait for element to be present.

        Args:
            timeout: Timeout in seconds.
            poll_frequency: Polling frequency in seconds.
            return_bool: Whether to return boolean instead of element.

        Returns:
            Element or boolean based on return_bool.

        """
        resolved_locator: tuple[str, str] | None = self.converter.to_xpath(
            self.element.remove_null_value(self.element.locator),
        )
        try:
            WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(  # type: ignore[reportArgumentType, reportUnknownMemberType]
                conditions.present(resolved_locator),
            )
        except TimeoutException:
            return False if return_bool else self.element
        return True if return_bool else self.element

    @log_debug()
    def wait_visible(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait for element to be visible.

        Args:
            timeout: Timeout in seconds.
            poll_frequency: Polling frequency in seconds.
            return_bool: Whether to return boolean instead of element.

        Returns:
            Element or boolean based on return_bool.

        """
        resolved_locator: tuple[str, str] | None = self.converter.to_xpath(
            self.element.remove_null_value(self.element.locator),
        )
        if not self._wait_for_visibility_with_locator(
            resolved_locator,
            timeout,
            poll_frequency,
        ):
            return False if return_bool else self.element
        return True if return_bool else self.element

    @log_debug()
    def wait_clickable(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait for element to be clickable.

        Args:
            timeout: Timeout in seconds.
            poll_frequency: Polling frequency in seconds.
            return_bool: Whether to return boolean instead of element.

        Returns:
            Element or boolean based on return_bool.

        """
        resolved_locator: tuple[str, str] | None = self.converter.to_xpath(
            self.element.remove_null_value(self.element.locator),
        )
        if not self._wait_for_clickability_with_locator(
            resolved_locator,
            timeout,
            poll_frequency,
        ):
            return False if return_bool else self.element
        return True if return_bool else self.element

    @log_debug()
    def wait_for_not(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait for element to not be present.

        Args:
            timeout: Timeout in seconds.
            poll_frequency: Polling frequency in seconds.
            return_bool: Whether to return boolean instead of element.

        Returns:
            Element or boolean based on return_bool.

        """
        resolved_locator: tuple[str, str] | None = self.converter.to_xpath(
            self.element.remove_null_value(self.element.locator),
        )
        if not self._wait_for_not_present_with_locator(
            resolved_locator,
            timeout,
            poll_frequency,
        ):
            return False if return_bool else self.element
        return True if return_bool else self.element

    @log_debug()
    def wait_for_not_visible(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait for element to not be visible.

        Args:
            timeout: Timeout in seconds.
            poll_frequency: Polling frequency in seconds.
            return_bool: Whether to return boolean instead of element.

        Returns:
            Element or boolean based on return_bool.

        """
        resolved_locator: tuple[str, str] | None = self.converter.to_xpath(
            self.element.remove_null_value(self.element.locator),
        )
        if not self._wait_for_not_visible_with_locator(
            resolved_locator,
            timeout,
            poll_frequency,
        ):
            return False if return_bool else self.element
        return True if return_bool else self.element

    @log_debug()
    def wait_for_not_clickable(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait for element to not be clickable.

        Args:
            timeout: Timeout in seconds.
            poll_frequency: Polling frequency in seconds.
            return_bool: Whether to return boolean instead of element.

        Returns:
            Element or boolean based on return_bool.

        """
        resolved_locator: tuple[str, str] | None = self.converter.to_xpath(
            self.element.remove_null_value(self.element.locator),
        )
        if not self._wait_for_not_clickable_with_locator(
            resolved_locator,
            timeout,
            poll_frequency,
        ):
            return False if return_bool else self.element
        return True if return_bool else self.element

    def _wait_for_visibility_with_locator(
        self,
        resolved_locator: tuple[str, str],
        timeout: int,
        poll_frequency: float,
    ) -> bool:
        """Wait for element visibility using resolved locator."""
        try:
            WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(  # type: ignore[reportArgumentType, reportUnknownMemberType]
                conditions.visible(resolved_locator),
            )
            return True  # noqa: TRY300
        except TimeoutException:
            return False

    def _wait_for_clickability_with_locator(
        self,
        resolved_locator: tuple[str, str],
        timeout: int,
        poll_frequency: float,
    ) -> bool:
        """Wait for element clickability using resolved locator."""
        try:
            WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(  # type: ignore[reportArgumentType, reportUnknownMemberType]
                conditions.clickable(resolved_locator),
            )
            return True  # noqa: TRY300
        except TimeoutException:
            return False

    def _wait_for_not_present_with_locator(
        self,
        resolved_locator: tuple[str, str],
        timeout: int,
        poll_frequency: float,
    ) -> bool:
        """Wait for element to not be present using resolved locator."""
        try:
            WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(  # type: ignore[reportArgumentType, reportUnknownMemberType]
                conditions.not_present(resolved_locator),
            )
            return True  # noqa: TRY300
        except NoSuchElementException:
            return True
        except TimeoutException:
            return False

    def _wait_for_not_visible_with_locator(
        self,
        resolved_locator: tuple[str, str],
        timeout: int,
        poll_frequency: float,
    ) -> bool:
        """Wait for element to not be visible using resolved locator."""
        try:
            WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(  # type: ignore[reportArgumentType, reportUnknownMemberType]
                conditions.not_visible(resolved_locator),
            )
            return True  # noqa: TRY300
        except NoSuchElementException:
            return True
        except TimeoutException:
            return False

    def _wait_for_not_clickable_with_locator(
        self,
        resolved_locator: tuple[str, str],
        timeout: int,
        poll_frequency: float,
    ) -> bool:
        """Wait for element to not be clickable using resolved locator."""
        try:
            WebDriverWait(self.shadowstep.driver, timeout, poll_frequency).until(  # type: ignore[reportArgumentType, reportUnknownMemberType]
                conditions.not_clickable(resolved_locator),
            )
            return True  # noqa: TRY300
        except TimeoutException:
            return False
