"""Element module for Shadowstep framework.

This module provides the main Element class which serves as the public API
for interacting with mobile elements in the Shadowstep framework.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

from shadowstep.decorators.element_decorators import fail_safe_element, fail_safe_element_check
from shadowstep.element import ElementDOM
from shadowstep.element.actions import ElementActions
from shadowstep.element.base import ElementBase
from shadowstep.element.coordinates import ElementCoordinates
from shadowstep.element.gestures import ElementGestures
from shadowstep.element.properties import ElementProperties
from shadowstep.element.screenshots import ElementScreenshots
from shadowstep.element.utilities import ElementUtilities
from shadowstep.element.waiting import ElementWaiting
from shadowstep.locator import UiSelector
from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    from appium.webdriver.webelement import WebElement
    from selenium.types import WaitExcTypes
    from selenium.webdriver.remote.shadowroot import ShadowRoot

    from shadowstep.element.should import Should
    from shadowstep.shadowstep import Shadowstep


# Configure the root logger (basic configuration)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Element(ElementBase):
    """Public API for Element."""

    def __init__(  # noqa: PLR0913
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        shadowstep: Shadowstep,
        timeout: float = 30,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
        native: WebElement | None = None,
    ) -> None:
        """Initialize Element with locator and configuration.

        Args:
            locator: Element locator (tuple, dict, Element, or UiSelector).
            shadowstep: Shadowstep instance for driver access.
            timeout: Maximum time to wait for element (default: 30).
            poll_frequency: Polling frequency in seconds (default: 0.5).
            ignored_exceptions: Exceptions to ignore during waiting.
            native: Pre-existing WebElement instance.

        """
        if isinstance(locator, Element):
            locator = locator.locator
        elif isinstance(locator, UiSelector):
            locator = cast("UiSelector", locator.__str__())
        super().__init__(locator, shadowstep, timeout, poll_frequency, ignored_exceptions, native)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug("Initialized Element with locator: %s", self.locator)
        self.utilities: ElementUtilities = ElementUtilities(self)
        self.properties: ElementProperties = ElementProperties(self)
        self.dom: ElementDOM = ElementDOM(self)
        self.actions: ElementActions = ElementActions(self)
        self.gestures: ElementGestures = ElementGestures(self)
        self.coordinates: ElementCoordinates = ElementCoordinates(self)
        self.screenshots: ElementScreenshots = ElementScreenshots(self)
        self.waiting: ElementWaiting = ElementWaiting(self)

    def __repr__(self) -> str:
        """Return string representation of Element.

        Returns:
            str: String representation showing locator.

        """
        return f"Element(locator={self.locator!r}"

    # ------------------------ dom ------------------------

    def get_element(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        timeout: int = 30,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> Element:
        """Return a single Element, lazy.

        Args:
            locator: Element locator to search for.
            timeout: Maximum time to wait for element (default: 30).
            poll_frequency: Polling frequency in seconds (default: 0.5).
            ignored_exceptions: Exceptions to ignore during waiting.

        Returns:
            Element: Element instance.

        """
        return self.dom.get_element(locator, timeout, poll_frequency, ignored_exceptions)

    @fail_safe_element()
    def get_elements(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        timeout: float = 30,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> list[Element]:
        """Find multiple Elements within this element's context. Greedy.

        Args:
            locator: Element locator to search for.
            timeout: Maximum time to wait for elements (default: 30).
            poll_frequency: Polling frequency in seconds (default: 0.5).
            ignored_exceptions: Exceptions to ignore during waiting.

        Returns:
            list[Element]: List of found element instances.

        """
        return self.dom.get_elements(locator, timeout, poll_frequency, ignored_exceptions)

    def get_parent(
        self,
        timeout: float = 30,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> Element:
        """Get the parent element of this element. Lazy.

        Args:
            timeout: Maximum time to wait for parent element (default: 30).
            poll_frequency: Polling frequency in seconds (default: 0.5).
            ignored_exceptions: Exceptions to ignore during waiting.

        Returns:
            Element: Parent element instance.

        """
        return self.dom.get_parent(timeout, poll_frequency, ignored_exceptions)

    @fail_safe_element()
    def get_parents(
        self,
        timeout: float = 30,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> list[Element]:
        """Get all parent elements of this element. Greedy.

        Args:
            timeout: Maximum time to wait for parent elements (default: 30).
            poll_frequency: Polling frequency in seconds (default: 0.5).
            ignored_exceptions: Exceptions to ignore during waiting.

        Returns:
            list[Element]: List of parent element instances.

        """
        return self.dom.get_parents(timeout, poll_frequency, ignored_exceptions)

    def get_sibling(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        timeout: float = 30,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> Element:
        """Get a sibling element of this element. Lazy.

        Args:
            locator: Element locator to search for.
            timeout: Maximum time to wait for sibling element (default: 30).
            poll_frequency: Polling frequency in seconds (default: 0.5).
            ignored_exceptions: Exceptions to ignore during waiting.

        Returns:
            Element: Sibling element instance.

        """
        return self.dom.get_sibling(locator, timeout, poll_frequency, ignored_exceptions)

    @fail_safe_element()
    def get_siblings(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        timeout: float = 30.0,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> list[Element]:
        """Get all sibling elements of this element. Greedy.

        Args:
            locator: Element locator to search for.
            timeout: Maximum time to wait for sibling elements (default: 30.0).
            poll_frequency: Polling frequency in seconds (default: 0.5).
            ignored_exceptions: Exceptions to ignore during waiting.

        Returns:
            list[Element]: List of sibling element instances.

        """
        return self.dom.get_siblings(locator, timeout, poll_frequency, ignored_exceptions)

    def get_cousin(
        self,
        cousin_locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        depth_to_parent: int = 1,
        timeout: float = 30.0,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> Element:
        """Get a cousin element (sibling of parent) of this element. Lazy.

        Args:
            cousin_locator: Element locator to search for.
            depth_to_parent: Number of parent levels to go up (default: 1).
            timeout: Maximum time to wait for cousin element (default: 30.0).
            poll_frequency: Polling frequency in seconds (default: 0.5).
            ignored_exceptions: Exceptions to ignore during waiting.

        Returns:
            Element: Cousin element instance.

        """
        return self.dom.get_cousin(
            cousin_locator,
            depth_to_parent,
            timeout,
            poll_frequency,
            ignored_exceptions,
        )

    @fail_safe_element()
    def get_cousins(
        self,
        cousin_locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
        depth_to_parent: int = 1,
        timeout: float = 30.0,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> list[Element]:
        """Get all cousin elements (siblings of parent) of this element. Greedy.

        Args:
            cousin_locator: Element locator to search for.
            depth_to_parent: Number of parent levels to go up (default: 1).
            timeout: Maximum time to wait for cousin elements (default: 30.0).
            poll_frequency: Polling frequency in seconds (default: 0.5).
            ignored_exceptions: Exceptions to ignore during waiting.

        Returns:
            list[Element]: List of cousin element instances.

        """
        return self.dom.get_cousins(
            cousin_locator,
            depth_to_parent,
            timeout,
            poll_frequency,
            ignored_exceptions,
        )

    # ----------------------- actions -----------------------

    # Override
    @fail_safe_element()
    def send_keys(self, *value: str) -> Element:
        """Send keys to the element.

        Args:
            *value: String values to send to the element.

        Returns:
            Element: Self for method chaining.

        """
        return self.actions.send_keys(*value)

    # Override
    @fail_safe_element()
    def clear(self) -> Element:
        """Clear the element's text content.

        Returns:
            Element: Self for method chaining.

        """
        return self.actions.clear()

    # Override
    @fail_safe_element()
    def set_value(self, value: str) -> Element:
        """Set the value of the element.

        Args:
            value: Value to set.

        Returns:
            Element: Self for method chaining.

        """
        self.logger.warning("Method %s is not implemented in UiAutomator2", get_current_func_name())
        return self.actions.set_value(value)

    # Override
    @fail_safe_element()
    def submit(self) -> Element:
        """Submit the element (e.g., form submission).

        Returns:
            Element: Self for method chaining.

        """
        self.logger.warning("Method %s is not implemented in UiAutomator2", get_current_func_name())
        return self.actions.submit()

    # ------------------------- gestures -------------------------

    @fail_safe_element()
    def tap(self, duration: int | None = None) -> Element:
        """Tap the element.

        Args:
            duration: Duration of the tap in milliseconds.

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.tap(duration)

    @fail_safe_element()
    def tap_and_move(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector | None = None,
        x: int | None = None,
        y: int | None = None,
        direction: int | None = None,
        distance: int | None = None,
    ) -> Element:
        """Tap and move to another element or coordinates.

        Args:
            locator: Target element locator.
            x: Target X coordinate.
            y: Target Y coordinate.
            direction: Direction vector for movement.
            distance: Distance to move.

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.tap_and_move(locator, x, y, direction, distance)

    @fail_safe_element()
    def click(self, duration: int | None = None) -> Element:
        """Click the element.

        Args:
            duration: Duration of the click in milliseconds.

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.click(duration)

    @fail_safe_element()
    def click_double(self) -> Element:
        """Perform a double click on the element.

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.click_double()

    @fail_safe_element()
    def drag(self, end_x: int, end_y: int, speed: int = 2500) -> Element:
        """Drag the element to target coordinates.

        Args:
            end_x: Target X coordinate.
            end_y: Target Y coordinate.
            speed: Drag speed in pixels per second (default: 2500).

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.drag(end_x, end_y, speed)

    def fling_up(self, speed: int = 2500) -> Element:
        """Perform a fling gesture upward on the element.

        Args:
            speed: Fling speed in pixels per second (default: 2500).

        Returns:
            Element: Self for method chaining.

        """
        return self.fling(speed=speed, direction="up")

    def fling_down(self, speed: int = 2500) -> Element:
        """Perform a fling gesture downward on the element.

        Args:
            speed: Fling speed in pixels per second (default: 2500).

        Returns:
            Element: Self for method chaining.

        """
        return self.fling(speed=speed, direction="down")

    def fling_left(self, speed: int = 2500) -> Element:
        """Perform a fling gesture leftward on the element.

        Args:
            speed: Fling speed in pixels per second (default: 2500).

        Returns:
            Element: Self for method chaining.

        """
        return self.fling(speed=speed, direction="left")

    def fling_right(self, speed: int = 2500) -> Element:
        """Perform a fling gesture rightward on the element.

        Args:
            speed: Fling speed in pixels per second (default: 2500).

        Returns:
            Element: Self for method chaining.

        """
        return self.fling(speed=speed, direction="right")

    @fail_safe_element()
    def fling(self, speed: int, direction: str) -> Element:
        """Perform a fling gesture on the element.

        Args:
            speed: Fling speed in pixels per second.
            direction: Direction of fling ("up", "down", "left", "right").

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.fling(speed, direction)

    def scroll_down(
        self,
        percent: float = 0.7,
        speed: int = 2000,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element:
        """Scroll down within the element.

        Args:
            percent: Scroll distance as percentage of element height (default: 0.7).
            speed: Scroll speed in pixels per second (default: 2000).
            return_bool: Whether to return boolean instead of Element (default: False).

        Returns:
            Element: Self for method chaining.

        """
        return self.scroll(direction="down", percent=percent, speed=speed, return_bool=return_bool)

    def scroll_up(
        self,
        percent: float = 0.7,
        speed: int = 2000,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element:
        """Scroll up within the element.

        Args:
            percent: Scroll distance as percentage of element height (default: 0.7).
            speed: Scroll speed in pixels per second (default: 2000).
            return_bool: Whether to return boolean instead of Element (default: False).

        Returns:
            Element: Self for method chaining.

        """
        return self.scroll(direction="up", percent=percent, speed=speed, return_bool=return_bool)

    def scroll_left(
        self,
        percent: float = 0.7,
        speed: int = 2000,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element:
        """Scroll left within the element.

        Args:
            percent: Scroll distance as percentage of element width (default: 0.7).
            speed: Scroll speed in pixels per second (default: 2000).
            return_bool: Whether to return boolean instead of Element (default: False).

        Returns:
            Element: Self for method chaining.

        """
        return self.scroll(direction="left", percent=percent, speed=speed, return_bool=return_bool)

    def scroll_right(
        self,
        percent: float = 0.7,
        speed: int = 2000,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element:
        """Scroll right within the element.

        Args:
            percent: Scroll distance as percentage of element width (default: 0.7).
            speed: Scroll speed in pixels per second (default: 2000).
            return_bool: Whether to return boolean instead of Element (default: False).

        Returns:
            Element: Self for method chaining.

        """
        return self.scroll(direction="right", percent=percent, speed=speed, return_bool=return_bool)

    @fail_safe_element()
    def scroll(self, direction: str, percent: float, speed: int, return_bool: bool) -> Element:  # noqa: FBT001
        """Scroll within the element in specified direction.

        Args:
            direction: Scroll direction ("up", "down", "left", "right").
            percent: Scroll distance as percentage of element size.
            speed: Scroll speed in pixels per second.
            return_bool: Whether to return boolean instead of Element.

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.scroll(direction, percent, speed, return_bool)

    @fail_safe_element()
    def scroll_to_bottom(self, percent: float = 0.7, speed: int = 8000) -> Element:
        """Scroll to the bottom of the element.

        Args:
            percent: Scroll distance as percentage of element height (default: 0.7).
            speed: Scroll speed in pixels per second (default: 8000).

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.scroll_to_bottom(percent, speed)

    @fail_safe_element()
    def scroll_to_top(self, percent: float = 0.7, speed: int = 8000) -> Element:
        """Scroll to the top of the element.

        Args:
            percent: Scroll distance as percentage of element height (default: 0.7).
            speed: Scroll speed in pixels per second (default: 8000).

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.scroll_to_top(percent, speed)

    @fail_safe_element()
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
        return self.gestures.scroll_to_element(locator, max_swipes)

    @fail_safe_element()
    def zoom(self, percent: float = 0.75, speed: int = 2500) -> Element:
        """Perform a zoom gesture on the element.

        Args:
            percent: Zoom scale as percentage (default: 0.75).
            speed: Zoom speed in pixels per second (default: 2500).

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.zoom(percent, speed)

    @fail_safe_element()
    def unzoom(self, percent: float = 0.75, speed: int = 2500) -> Element:
        """Perform an unzoom gesture on the element.

        Args:
            percent: Unzoom scale as percentage (default: 0.75).
            speed: Unzoom speed in pixels per second (default: 2500).

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.unzoom(percent, speed)

    def swipe_up(self, percent: float = 0.75, speed: int = 5000) -> Element:
        """Perform a swipe up gesture on the element.

        Args:
            percent: Swipe distance as percentage of element height (default: 0.75).
            speed: Swipe speed in pixels per second (default: 5000).

        Returns:
            Element: Self for method chaining.

        """
        return self.swipe(direction="up", percent=percent, speed=speed)

    def swipe_down(self, percent: float = 0.75, speed: int = 5000) -> Element:
        """Perform a swipe down gesture on the element.

        Args:
            percent: Swipe distance as percentage of element height (default: 0.75).
            speed: Swipe speed in pixels per second (default: 5000).

        Returns:
            Element: Self for method chaining.

        """
        return self.swipe(direction="down", percent=percent, speed=speed)

    def swipe_left(self, percent: float = 0.75, speed: int = 5000) -> Element:
        """Perform a swipe left gesture on the element.

        Args:
            percent: Swipe distance as percentage of element width (default: 0.75).
            speed: Swipe speed in pixels per second (default: 5000).

        Returns:
            Element: Self for method chaining.

        """
        return self.swipe(direction="left", percent=percent, speed=speed)

    def swipe_right(self, percent: float = 0.75, speed: int = 5000) -> Element:
        """Perform a swipe right gesture on the element.

        Args:
            percent: Swipe distance as percentage of element width (default: 0.75).
            speed: Swipe speed in pixels per second (default: 5000).

        Returns:
            Element: Self for method chaining.

        """
        return self.swipe(direction="right", percent=percent, speed=speed)

    @fail_safe_element()
    def swipe(self, direction: str, percent: float = 0.75, speed: int = 5000) -> Element:
        """Perform a swipe gesture on the element.

        Args:
            direction: Swipe direction ("up", "down", "left", "right").
            percent: Swipe distance as percentage of element size (default: 0.75).
            speed: Swipe speed in pixels per second (default: 5000).

        Returns:
            Element: Self for method chaining.

        """
        return self.gestures.swipe(direction, percent, speed)

    # ------------------------ properties ------------------------

    # Override
    @fail_safe_element()
    def get_attribute(self, name: str) -> str:  # type: ignore[override]
        """Get the value of the specified attribute.

        Args:
            name: Name of the attribute to retrieve.

        Returns:
            str: Value of the attribute.

        """
        return self.properties.get_attribute(name)

    @fail_safe_element()
    def get_attributes(self) -> dict[str, Any]:
        """Fetch all XML attributes of the element by matching locator against page source.

        Returns:
            dict[str, Any]: Dictionary of all attributes.

        """
        return self.properties.get_attributes()

    @fail_safe_element()
    def get_property(self, name: str) -> Any:
        """Get the value of the specified property.

        Args:
            name: Name of the property to retrieve.

        Returns:
            Any: Value of the property.

        """
        self.logger.warning("Method %s is not implemented in UiAutomator2", get_current_func_name())
        return self.properties.get_property(name)

    @fail_safe_element()
    def get_dom_attribute(self, name: str) -> str:
        """Get the given attribute of the element from HTML markup.

        Unlike get_attribute, this method only returns attributes declared
        in the element's HTML markup.

        Args:
            name: Name of the attribute to retrieve.

        Returns:
            str: Value of the DOM attribute.

        """
        return self.properties.get_dom_attribute(name)

    # Override
    @fail_safe_element_check()
    def is_displayed(self) -> bool:
        """Whether the element is visible to a user.

        Returns:
            bool: True if the element is displayed on screen and visible to the user.

        """
        return self.properties.is_displayed()

    @fail_safe_element_check()
    def is_visible(self) -> bool:
        """Check if the element is visible on screen.

        Returns:
            bool: True if element is visible, False otherwise.

        """
        return self.properties.is_visible()

    @fail_safe_element()
    def is_selected(self) -> bool:
        """Return whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.

        Returns:
            bool: True if the element is selected.

        """
        return self.properties.is_selected()

    @fail_safe_element()
    def is_enabled(self) -> bool:
        """Check if the element is enabled.

        Returns:
            bool: True if the element is enabled.

        """
        return self.properties.is_enabled()

    @fail_safe_element_check()
    def is_contains(
        self,
        locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
    ) -> bool:
        """Check if the element contains another element.

        Args:
            locator: Locator of the element to search for.

        Returns:
            bool: True if the element contains the specified element.

        """
        return self.properties.is_contains(locator)  # type: ignore[attr-defined]

    @property
    @fail_safe_element()
    def tag_name(self) -> str:
        """Get the element's tag name.

        Returns:
            str: The tag name of the element.

        """
        return self.properties.tag_name()

    @property
    @fail_safe_element()
    def attributes(self) -> Any:
        """Get all element attributes.

        Returns:
            dict[str, Any]: Dictionary of all element attributes.

        """
        return self.get_attributes()

    @property
    @fail_safe_element()
    def text(self) -> str:
        """Get the text content of the element.

        Returns:
            str: Text content of the element.

        """
        return self.properties.text()

    @property
    @fail_safe_element()
    def resource_id(self) -> str:
        """Get the resource ID of the element.

        Returns:
            str: Resource ID of the element.

        """
        return self.properties.resource_id()

    @property
    @fail_safe_element()
    def class_(self) -> str:  # 'class' is a reserved word, so class_name is better
        """Get the class name of the element.

        Returns:
            str: Class name of the element.

        """
        return self.properties.class_()

    @property
    @fail_safe_element()
    def class_name(self) -> str:  # 'class' is a reserved word, so class_name is better
        """Get the class name of the element.

        Returns:
            str: Class name of the element.

        """
        return self.properties.class_name()

    @property
    @fail_safe_element()
    def index(self) -> str:
        """Get the index of the element.

        Returns:
            str: Index of the element.

        """
        self.logger.warning(
            "Method %s 'index' attribute is unknown for the element",
            get_current_func_name(),
        )
        return self.properties.index()

    @property
    @fail_safe_element()
    def package(self) -> str:
        """Get the package name of the element.

        Returns:
            str: Package name of the element.

        """
        return self.properties.package()

    @property
    @fail_safe_element()
    def bounds(self) -> str:
        """Get the bounds of the element.

        Returns:
            str: Bounds of the element.

        """
        return self.properties.bounds()

    @property
    @fail_safe_element()
    def checked(self) -> str:
        """Get the checked state of the element.

        Returns:
            str: Checked state of the element.

        """
        return self.properties.checked()

    @property
    @fail_safe_element()
    def checkable(self) -> str:
        """Get the checkable state of the element.

        Returns:
            str: Checkable state of the element.

        """
        return self.properties.checkable()

    @property
    @fail_safe_element()
    def enabled(self) -> str:
        """Get the enabled state of the element.

        Returns:
            str: Enabled state of the element.

        """
        return self.properties.enabled()

    @property
    @fail_safe_element()
    def focusable(self) -> str:
        """Get the focusable state of the element.

        Returns:
            str: Focusable state of the element.

        """
        return self.properties.focusable()

    @property
    @fail_safe_element()
    def focused(self) -> str:
        """Get the focused state of the element.

        Returns:
            str: Focused state of the element.

        """
        return self.properties.focused()

    @property
    @fail_safe_element()
    def long_clickable(self) -> str:
        """Get the long clickable state of the element.

        Returns:
            str: Long clickable state of the element.

        """
        return self.properties.long_clickable()

    @property
    @fail_safe_element()
    def password(self) -> str:
        """Get the password state of the element.

        Returns:
            str: Password state of the element.

        """
        return self.properties.password()

    @property
    @fail_safe_element()
    def scrollable(self) -> str:
        """Get the scrollable state of the element.

        Returns:
            str: Scrollable state of the element.

        """
        return self.properties.scrollable()

    @property
    @fail_safe_element()
    def selected(self) -> str:
        """Get the selected state of the element.

        Returns:
            str: Selected state of the element.

        """
        return self.properties.selected()

    @property
    @fail_safe_element()
    def displayed(self) -> str:
        """Get the displayed state of the element.

        Returns:
            str: Displayed state of the element.

        """
        return self.properties.displayed()

    @property
    @fail_safe_element()
    def shadow_root(self) -> ShadowRoot:
        """Get the shadow root of the element.

        Returns:
            ShadowRoot: Shadow root of the element.

        """
        self.logger.warning("Method %s is not implemented in UiAutomator2", get_current_func_name())
        return self.properties.shadow_root()

    @property
    @fail_safe_element()
    def size(self) -> dict[str, Any]:
        """Get the size of the element.

        Returns:
            dict: Dictionary with keys 'width' and 'height'.

        """
        return self.properties.size()  # type: ignore[return-value]

    @fail_safe_element()
    def value_of_css_property(self, property_name: str) -> str:
        """Get the value of a CSS property.

        Args:
            property_name: Name of the CSS property.

        Returns:
            str: Value of the CSS property.

        """
        self.logger.warning("Method %s is not implemented in UiAutomator2", get_current_func_name())
        return self.properties.value_of_css_property(property_name)

    @property
    @fail_safe_element()
    def location(self) -> dict[str, Any]:
        """Get the location of the element.

        Returns:
            dict: Location coordinates of the element.

        """
        return self.properties.location()  # type: ignore[return-value]

    @property
    @fail_safe_element()
    def rect(self) -> dict[str, Any]:
        """Get the rectangle of the element.

        Returns:
            dict: Dictionary with keys 'x', 'y', 'width', 'height'.

        """
        return self.properties.rect()  # type: ignore[return-value]

    @property
    @fail_safe_element()
    def aria_role(self) -> str:
        """Get the ARIA role of the element.

        Returns:
            str: The ARIA role of the element.

        """
        return self.properties.aria_role()

    @property
    @fail_safe_element()
    def accessible_name(self) -> str:
        """Get the accessible name of the element.

        Returns:
            str: Accessible name of the element.

        """
        return self.properties.accessible_name()

    # ----------------------------- coordinates -----------------------------

    @fail_safe_element()
    def get_coordinates(self) -> tuple[int, int, int, int]:
        """Get the coordinates of the element.

        Returns:
            tuple[int, int, int, int]: Coordinates as (x, y, width, height).

        """
        return self.coordinates.get_coordinates()

    @fail_safe_element()
    def get_center(self) -> tuple[int, int]:
        """Get the center coordinates of the element.

        Returns:
            tuple[int, int]: Center coordinates as (x, y).

        """
        return self.coordinates.get_center()

    # Override
    @property
    @fail_safe_element()
    def location_in_view(self) -> dict[str, int]:
        """Get the location of the element in view.

        Returns:
            dict[str, int]: Location coordinates in view.

        """
        return self.coordinates.location_in_view()

    @property
    @fail_safe_element()
    def location_once_scrolled_into_view(self) -> dict[str, int]:
        """Get the location of the element once scrolled into view.

        Returns:
            dict[str, int]: Location coordinates once scrolled into view.

        """
        self.logger.warning("Method %s is not implemented in UiAutomator2", get_current_func_name())
        return self.coordinates.location_once_scrolled_into_view()

    # ------------------------ screenshots ------------------------

    @property
    @fail_safe_element()
    def screenshot_as_base64(self) -> str:
        """Get the screenshot of the element as base64 encoded string.

        Returns:
            str: Base64-encoded screenshot string.

        """
        return self.screenshots.screenshot_as_base64()

    @property
    @fail_safe_element()
    def screenshot_as_png(self) -> bytes:
        """Get the screenshot of the element as binary data.

        Returns:
            bytes: PNG-encoded screenshot bytes.

        """
        return self.screenshots.screenshot_as_png()

    @fail_safe_element()
    def save_screenshot(self, filename: str = "screenshot.png") -> bool:
        """Save a screenshot of the element to a PNG file.

        Args:
            filename: The full path to save the screenshot. Should end with `.png`.

        Returns:
            bool: True if successful, False otherwise.

        """
        return self.screenshots.save_screenshot(filename)

    # ------------------------------- waiting -------------------------------

    @fail_safe_element()
    def wait(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait for the element to appear (present in DOM).

        Args:
            timeout: Timeout in seconds (default: 10).
            poll_frequency: Frequency of polling (default: 0.5).
            return_bool: If True - return bool, else return Element (self) (default: False).

        Returns:
            Element | bool: Element instance or True if found, False otherwise.

        """
        return self.waiting.wait(timeout, poll_frequency=poll_frequency, return_bool=return_bool)

    @fail_safe_element()
    def wait_visible(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait until the element is visible.

        Args:
            timeout: Timeout in seconds (default: 10).
            poll_frequency: Frequency of polling (default: 0.5).
            return_bool: If True - return bool, else return Element (self) (default: False).

        Returns:
            Element | bool: Element instance or True if visible, False otherwise.

        """
        return self.waiting.wait_visible(
            timeout,
            poll_frequency=poll_frequency,
            return_bool=return_bool,
        )

    @fail_safe_element()
    def wait_clickable(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait until the element is clickable.

        Args:
            timeout: Timeout in seconds (default: 10).
            poll_frequency: Frequency of polling (default: 0.5).
            return_bool: If True - return bool, else return Element (self) (default: False).

        Returns:
            Element | bool: Element instance or True if clickable, False otherwise.

        """
        return self.waiting.wait_clickable(timeout, poll_frequency, return_bool)

    @fail_safe_element_check()
    def wait_for_not(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait until the element is no longer present in the DOM.

        Args:
            timeout: Timeout in seconds (default: 10).
            poll_frequency: Frequency of polling (default: 0.5).
            return_bool: If True - return bool, else return Element (self) (default: False).

        Returns:
            Element | bool: Element instance or True if disappears, False otherwise.

        """
        return self.waiting.wait_for_not(
            timeout,
            poll_frequency=poll_frequency,
            return_bool=return_bool,
        )

    @fail_safe_element_check()
    def wait_for_not_visible(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait until the element becomes invisible.

        Args:
            timeout: Timeout in seconds (default: 10).
            poll_frequency: Polling frequency (default: 0.5).
            return_bool: If True - return bool, else return Element (self) (default: False).

        Returns:
            Element | bool: Element instance or True if invisible, False otherwise.

        """
        return self.waiting.wait_for_not_visible(timeout, poll_frequency, return_bool)

    @fail_safe_element()
    def wait_for_not_clickable(
        self,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        return_bool: bool = False,  # noqa: FBT001, FBT002
    ) -> Element | bool:
        """Wait until the element becomes not clickable.

        Args:
            timeout: Timeout in seconds (default: 10).
            poll_frequency: Polling frequency (default: 0.5).
            return_bool: If True - return bool, else return Element (self) (default: False).

        Returns:
            Element | bool: Element instance or True if not clickable, False otherwise.

        """
        return self.waiting.wait_for_not_clickable(timeout, poll_frequency, return_bool)

    # ---------------------------- other ----------------------------

    @property
    def should(self) -> Should:
        """Get DSL-like assertions for the element.

        Returns:
            Should: DSL assertion object for chaining assertions.

        """
        from shadowstep.element.should import Should  # noqa: PLC0415

        return Should(self)

    def get_native(self) -> WebElement:
        """Get the native WebElement instance.

        Returns either the provided native element or resolves via locator.

        Returns:
            WebElement: Native WebElement instance.

        """
        if self.native:
            return self.native

        # Convert Element to its locator if needed
        locator = self.locator
        if isinstance(locator, Element):
            locator = locator.locator
        return self._get_web_element(
            locator=locator,
            timeout=self.timeout,
            poll_frequency=self.poll_frequency,
            ignored_exceptions=self.ignored_exceptions,
        )
