"""Element coordinates module for Shadowstep framework.

This module provides coordinate-related functionality for elements,
including getting bounds, center coordinates, and view locations.
"""
from __future__ import annotations

import logging
import time
import traceback
from typing import TYPE_CHECKING, Any

from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.decorators.decorators import log_debug
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    from appium.webdriver.webelement import WebElement

    from shadowstep.element.element import Element
    from shadowstep.element.utilities import ElementUtilities
    from shadowstep.locator import LocatorConverter
    from shadowstep.shadowstep import Shadowstep


class ElementCoordinates:
    """Element coordinates handler for Shadowstep framework."""

    def __init__(self, element: Element) -> None:
        """Initialize ElementCoordinates.

        Args:
            element: The element to get coordinates for.

        """
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    @log_debug()
    def get_coordinates(self, element: WebElement | None = None) -> tuple[int, int, int, int]:
        """Get the bounding box coordinates of the element.

        Args:
            element: Element to get bounds from. If None, uses internal locator.

        Returns:
            (left, top, right, bottom) or None.

        """
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                if element is None:
                    element = self.element.get_native()
                bounds: Any = element.get_attribute("bounds")  # type: ignore[attr-defined]
                if not bounds:
                    continue
                left, top, right, bottom = map(
                    int, bounds.strip("[]").replace("][", ",").split(","),
                )  # type: ignore[arg-type]
                return left, top, right, bottom  # noqa: TRY300
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise

        raise ShadowstepElementException(
            msg=f"Failed to {get_current_func_name()} within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def get_center(self, element: WebElement | None = None) -> tuple[int, int]:
        """Get the center coordinates of the element.

        Args:
            element: Optional direct WebElement. If not provided, uses current locator.

        Returns:
            (x, y) center point or None if element not found.

        """
        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                if element is None:
                    element = self.element.get_native()
                coordinates = self.get_coordinates(element)
                if not coordinates:
                    continue
                left, top, right, bottom = coordinates
                x = int((left + right) / 2)
                y = int((top + bottom) / 2)
                return x, y  # noqa: TRY300
            except NoSuchDriverException as error:
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise

        raise ShadowstepElementException(
            msg=f"Failed to {get_current_func_name()} within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    # Override
    @log_debug()
    def location_in_view(self) -> dict[str, Any]:
        """Get the location of an element relative to the view.

        Returns:
            Dictionary with keys 'x' and 'y', or None on failure.

        """
        start_time = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()

                current_element = self.element.get_native()

                return current_element.location_in_view  # type: ignore[attr-defined]  # Appium WebElement property  # noqa: TRY300
            except NoSuchDriverException as error:  # noqa: PERF203
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if ("instrumentation process is not running" in err_msg or
                        "socket hang up" in err_msg):
                    self.element.utilities.handle_driver_error(error)
                    continue
                raise
        raise ShadowstepElementException(
            msg=f"Failed to get location_in_view within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def location_once_scrolled_into_view(self) -> dict[str, Any]:
        """Get the top-left corner location of the element after scrolling it into view.

        NOT IMPLEMENTED

        Returns:
            Dictionary with keys 'x' and 'y' indicating location on screen.

        Raises:
            ShadowstepElementException: If element could not be scrolled into view or
                location determined.

        """
        self.logger.warning(
            "Method %s is not implemented in UiAutomator2", get_current_func_name())

        start_time = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()

                current_element = self.element.get_native()

                return current_element.location_once_scrolled_into_view  # type: ignore[attr-defined]  # noqa: TRY300

            except NoSuchDriverException as error:  # noqa: PERF203
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to get location_once_scrolled_into_view within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )
