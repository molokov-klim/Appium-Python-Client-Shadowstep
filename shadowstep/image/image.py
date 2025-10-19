"""Image-based interaction module for Shadowstep framework.

This module provides the ShadowstepImage class for performing
image-based automation operations such as image recognition,
tapping, dragging, scrolling, and other visual interactions
with mobile applications.

Migrated from legacy AppiumImage implementation with modern
architecture patterns and type safety.
"""

from __future__ import annotations

import base64
import logging
import time
from typing import TYPE_CHECKING, Any, cast

import cv2
import numpy as np
from PIL import Image as PILImage
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support.wait import WebDriverWait

from shadowstep.decorators.common_decorators import log_image
from shadowstep.decorators.image_decorators import fail_safe_image
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepImageLoadError,
    ShadowstepImageNotFoundError,
    ShadowstepImageNotImplementedError,
    ShadowstepInvalidScrollDirectionError,
    ShadowstepUnsupportedImageTypeError,
)
from shadowstep.ui_automator.mobile_commands import MobileCommands
from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    from shadowstep.shadowstep import Shadowstep


class ShadowstepImage:
    """Image-based interactions with lazy evaluation and method chaining support.

    This class provides a fluent interface for working with images on mobile screens,
    including template matching, OCR, coordinate calculations, and gesture operations.

    Architecture:
        - Lazy evaluation: coordinates are cached after first visibility check
        - Fluent interface: all action methods return self for chaining
        - Multi-scale matching: automatically handles different screen densities
        - Type-safe: comprehensive type hints with TYPE_CHECKING

    Example:
        image = ShadowstepImage("button.png", base, threshold=0.8)
        image.wait().tap()

        Method chaining
        ShadowstepImage("icon.png", base).scroll_to().tap().wait_not()

        # Coordinates access
        coords = image.coordinates  # (x1, y1, x2, y2)
        center = image.center  # (x, y)

    """

    def __init__(
        self,
        image: bytes | np.ndarray[Any, Any] | PILImage.Image | str,
        threshold: float = 0.7,
        timeout: float = 5.0,
    ) -> None:
        """Initialize the ShadowstepImage.

        Args:
            image: Image data in various formats:
                - bytes: Raw image bytes (PNG, JPEG, etc.)
                - np.ndarray: NumPy array (from cv2, PIL conversion, etc.)
                - PIL.Image.Image: PIL Image object
                - str: File path to image on disk
            base: Shadowstep instance for automation operations.
            threshold: Matching threshold for image recognition (0.0 to 1.0).
                Higher values require better match. Default: 0.7 (70% match).
            timeout: Timeout in seconds for visibility/wait operations. Default: 5.0.

        """
        from shadowstep.shadowstep import Shadowstep  # noqa: PLC0415

        self.shadowstep: Shadowstep = Shadowstep.get_instance()

        self._image = image
        self.threshold = threshold
        self.timeout = timeout

        # Cached values (lazy evaluation)
        self._coords: tuple[int, int, int, int] = cast("tuple[int, int, int, int]", None)
        self._center: tuple[int, int] = cast("tuple[int, int]", None)
        self._last_screenshot_time: float = 0.0

        # consts
        self.MIN_SUFFICIENT_MATCH = 0.95

        self.logger = logging.getLogger(__name__)
        self.logger.info(
            "Initialized ShadowstepImage with threshold=%s, timeout=%s",
            threshold,
            timeout,
        )

    @fail_safe_image()
    @log_image()
    def tap(self, duration: int | None = None) -> ShadowstepImage:
        """Tap on the image center.

        Args:
            duration: Duration of the tap in milliseconds. If None, performs a quick tap.

        Returns:
            ShadowstepImage: Self for method chaining.

        Example:
            image.tap()  # Quick tap
            image.tap(duration=500)  # Long press for 500ms

        Raises:
            ShadowstepImageNotFoundError: If image not found on screen.

        """
        self.ensure_visible()
        x, y = self._center  # type: ignore[misc]
        self.shadowstep.driver.tap(positions=[(x, y)], duration=duration)
        self.logger.info("Tapped at (%s, %s) with duration=%s", x, y, duration)
        return self

    @fail_safe_image()
    @log_image()
    def drag(
        self,
        to: tuple[int, int] | ShadowstepImage,
        duration: float = 1.0,
    ) -> ShadowstepImage:
        """Drag from image center to target location.

        Args:
            to: Target coordinates as tuple (x, y) or another ShadowstepImage.
            duration: Duration of the drag gesture in seconds. Default: 1.0.

        Returns:
            ShadowstepImage: Self for method chaining.

        Example:
            image1.drag(to=(500, 500))  # Drag to coordinates
            image1.drag(to=image2)  # Drag to another image

        Raises:
            ShadowstepImageNotFoundError: If source or target image not found.

        """
        self.ensure_visible()
        start_x, start_y = self._center  # type: ignore[misc]

        # Get target coordinates
        if isinstance(to, ShadowstepImage):
            to.ensure_visible()
            end_x, end_y = to._center  # type: ignore[misc]  # noqa: SLF001
        else:
            end_x, end_y = to

        actions = ActionChains(self.shadowstep.driver)
        actions.w3c_actions = ActionBuilder(
            self.shadowstep.driver,
            mouse=PointerInput(interaction.POINTER_TOUCH, "touch"),
        )
        actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.pointer_down()  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.pause(duration)  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)  # type: ignore[reportUnknownMemberType]
        actions.w3c_actions.pointer_action.pointer_up()  # type: ignore[reportUnknownMemberType]
        actions.perform()

        self.logger.info("Dragged from (%s, %s) to (%s, %s)", start_x, start_y, end_x, end_y)
        return self

    @fail_safe_image()
    @log_image()
    def zoom(self, percent: float = 1.5, steps: int = 10) -> ShadowstepImage:
        """Zoom in on the image center using pinch-open gesture.

        Args:
            percent: Zoom percentage (1.0 = no zoom, >1.0 = zoom in). Default: 1.5 (150%).
            steps: Number of steps to perform the zoom smoothly. Default: 10.

        Returns:
            ShadowstepImage: Self for method chaining.

        Example:
            image.zoom()  # 150% zoom
            image.zoom(percent=2.0, steps=20)  # 200% zoom, smooth

        Raises:
            ShadowstepImageNotFoundError: If image not found on screen.

        """
        self.ensure_visible()
        x, y = self._center  # type: ignore[misc]

        # Use mobile gesture command for pinch-open (zoom in)

        mobile_commands = MobileCommands()

        # Calculate speed based on steps
        speed = int(2500 / steps) * 10

        # Get coordinates and perform zoom
        coords = self._coords  # type: ignore[assignment]
        x1, y1, x2, y2 = coords

        # Perform multi-finger zoom gesture
        mobile_commands.pinch_open_gesture(
            {
                "left": x1,
                "top": y1,
                "width": x2 - x1,
                "height": y2 - y1,
                "percent": percent - 1.0,  # Percent is relative to original
                "speed": speed,
            },
        )

        self.logger.info("Zoomed at (%s, %s) by %s%%", x, y, percent * 100)
        return self

    @fail_safe_image()
    @log_image()
    def unzoom(self, percent: float = 0.5, steps: int = 10) -> ShadowstepImage:
        """Zoom out from the image center using pinch-close gesture.

        Args:
            percent: Zoom percentage (<1.0 = zoom out). Default: 0.5 (50%).
            steps: Number of steps to perform the zoom smoothly. Default: 10.

        Returns:
            ShadowstepImage: Self for method chaining.

        Example:
            image.unzoom()  # 50% zoom out
            image.unzoom(percent=0.3, steps=15)  # 30% zoom out

        Raises:
            ShadowstepImageNotFoundError: If image not found on screen.

        """
        self.ensure_visible()
        x, y = self._center  # type: ignore[misc]

        mobile_commands = MobileCommands()

        # Calculate speed based on steps
        speed = int(2500 / steps) * 10

        # Get coordinates and perform unzoom
        coords = self._coords  # type: ignore[assignment]
        x1, y1, x2, y2 = coords

        # Perform multi-finger unzoom gesture
        mobile_commands.pinch_close_gesture(
            {
                "left": x1,
                "top": y1,
                "width": x2 - x1,
                "height": y2 - y1,
                "percent": 1.0 - percent,  # Percent is relative to original
                "speed": speed,
            },
        )

        self.logger.info("Unzoomed at (%s, %s) by %s%%", x, y, percent * 100)
        return self

    @fail_safe_image()
    @log_image()
    def wait(self) -> bool:
        """Wait for the image to become visible.

        Returns:
            bool: True if image becomes visible within timeout, False otherwise.

        Example:
            if image.wait():
            ...     image.tap()

        Note:
            This method uses WebDriverWait for robust waiting with polling.

        """
        start_time = time.time()

        def image_visible(_driver: Any) -> bool:
            """Check if image is visible (for WebDriverWait)."""
            return self._get_image_coordinates() is not None

        try:
            WebDriverWait(self.shadowstep.driver, self.timeout, poll_frequency=0.5).until(
                image_visible,
            )
            self.ensure_visible()  # Cache coordinates
        except TimeoutException:
            elapsed = time.time() - start_time
            self.logger.warning("Image not visible after %.2fs", elapsed)
            return False
        else:
            return True

    @fail_safe_image()
    @log_image()
    def wait_not(self) -> bool:
        """Wait for the image to become invisible.

        Returns:
            bool: True if image becomes invisible within timeout, False otherwise.

        Example:
            image.tap()
            image.wait_not()  # Wait for it to disappear

        Note:
            This method uses WebDriverWait for robust waiting with polling.

        """
        start_time = time.time()

        def image_not_visible(_driver: Any) -> bool:
            """Check if image is not visible (for WebDriverWait)."""
            return self._get_image_coordinates() is None

        try:
            WebDriverWait(self.shadowstep.driver, self.timeout, poll_frequency=0.5).until(
                image_not_visible,
            )
            # Clear cache since image is no longer visible
            self._coords = cast("tuple[int, int, int, int]", None)
            self._center = cast("tuple[int, int]", None)
        except TimeoutException:
            elapsed = time.time() - start_time
            self.logger.warning("Image still visible after %.2fs", elapsed)
            return False
        else:
            return True

    @fail_safe_image()
    @log_image()
    def is_visible(self) -> bool:
        """Check if the image is currently visible on screen.

        Returns:
            bool: True if image is visible, False otherwise.

        Example:
            if image.is_visible():
            ...     print("Image found!")

        Note:
            This is a single check, not a wait. Use wait() for waiting behavior.

        """
        try:
            coords = self._get_image_coordinates()
            if coords is not None:
                # Update cache
                self._coords = coords
                self._center = self._calculate_center(coords)
                return True
        except Exception:
            self.logger.exception("Error checking visibility")
            return False
        else:
            return False

    @property
    def coordinates(self) -> tuple[int, int, int, int]:
        """Get the bounding box coordinates of the image.

        Returns:
            tuple[int, int, int, int]: (x1, y1, x2, y2) coordinates of the image.

        Example:
            x1, y1, x2, y2 = image.coordinates
            width = x2 - x1
            height = y2 - y1

        Raises:
            ShadowstepImageNotFoundError: If image not found on screen.

        """
        if self._coords is None:  # type: ignore[reportUnnecessaryComparison]
            self.ensure_visible()
        return self._coords  # type: ignore[return-value]

    @property
    def center(self) -> tuple[int, int]:
        """Get the center coordinates of the image.

        Returns:
            tuple[int, int]: (x, y) center coordinates of the image.

        Example:
            x, y = image.center
            print(f"Center at ({x}, {y})")

        Raises:
            ShadowstepImageNotFoundError: If image not found on screen.

        """
        if self._center is None:  # type: ignore[reportUnnecessaryComparison]
            self.ensure_visible()
        return self._center  # type: ignore[return-value]

    @log_image()
    def scroll_down(
        self,
        from_percent: float = 0.5,
        to_percent: float = 0.1,
        max_attempts: int = 10,
        step_delay: float = 0.5,
    ) -> ShadowstepImage:
        """Scroll down until the image is visible.

        Args:
            from_percent: Starting position as percentage of screen height (0.0-1.0).
            to_percent: Ending position as percentage of screen height (0.0-1.0).
            max_attempts: Maximum number of scroll attempts. Default: 10.
            step_delay: Delay between scroll attempts in seconds. Default: 0.5.

        Returns:
            ShadowstepImage: Self for method chaining.

        Example:
            image.scroll_down().tap()  # Scroll down until visible, then tap

        Raises:
            ShadowstepImageNotFoundError: If image not found after max_attempts.

        """
        return self._scroll_to_image(
            direction="down",
            from_percent=from_percent,
            to_percent=to_percent,
            max_attempts=max_attempts,
            step_delay=step_delay,
        )

    @log_image()
    def scroll_up(
        self,
        max_attempts: int = 10,
        step_delay: float = 0.5,
    ) -> ShadowstepImage:
        """Scroll up until the image is visible.

        Args:
            max_attempts: Maximum number of scroll attempts. Default: 10.
            step_delay: Delay between scroll attempts in seconds. Default: 0.5.

        Returns:
            ShadowstepImage: Self for method chaining.

        Example:
            image.scroll_up().tap()

        Raises:
            ShadowstepImageNotFoundError: If image not found after max_attempts.

        """
        return self._scroll_to_image(
            direction="up",
            max_attempts=max_attempts,
            step_delay=step_delay,
        )

    @log_image()
    def scroll_left(
        self,
        max_attempts: int = 10,
        step_delay: float = 0.5,
    ) -> ShadowstepImage:
        """Scroll left until the image is visible.

        Args:
            max_attempts: Maximum number of scroll attempts. Default: 10.
            step_delay: Delay between scroll attempts in seconds. Default: 0.5.

        Returns:
            ShadowstepImage: Self for method chaining.

        Raises:
            ShadowstepImageNotFoundError: If image not found after max_attempts.

        """
        return self._scroll_to_image(
            direction="left",
            max_attempts=max_attempts,
            step_delay=step_delay,
        )

    @log_image()
    def scroll_right(
        self,
        max_attempts: int = 10,
        step_delay: float = 0.5,
    ) -> ShadowstepImage:
        """Scroll right until the image is visible.

        Args:
            max_attempts: Maximum number of scroll attempts. Default: 10.
            step_delay: Delay between scroll attempts in seconds. Default: 0.5.

        Returns:
            ShadowstepImage: Self for method chaining.

        Raises:
            ShadowstepImageNotFoundError: If image not found after max_attempts.

        """
        return self._scroll_to_image(
            direction="right",
            max_attempts=max_attempts,
            step_delay=step_delay,
        )

    @log_image()
    def scroll_to(
        self,
        max_attempts: int = 10,
        step_delay: float = 0.5,
    ) -> ShadowstepImage:
        """Scroll to bring the image into view (auto-detect direction).

        Args:
            max_attempts: Maximum number of scroll attempts. Default: 10.
            step_delay: Delay between scroll attempts in seconds. Default: 0.5.

        Returns:
            ShadowstepImage: Self for method chaining.

        Example:
            image.scroll_to().tap()  # Smart scroll then tap

        Raises:
            ShadowstepImageNotFoundError: If image not found after max_attempts.

        Note:
            This method tries scrolling down first, then up if not found.

        """
        # Try scrolling down first
        try:
            return self.scroll_down(max_attempts=max_attempts // 2, step_delay=step_delay)
        except ShadowstepImageNotFoundError:
            # If not found, try scrolling up
            return self.scroll_up(max_attempts=max_attempts // 2, step_delay=step_delay)

    @log_image()
    def is_contains(
        self,
        image: bytes | np.ndarray[Any, Any] | PILImage.Image | str,
    ) -> bool:
        """Check if this image contains another image.

        Args:
            image: Image to search for within this image's bounds.

        Returns:
            bool: True if the image contains the target image, False otherwise.

        Example:
            container = ShadowstepImage("dialog.png", base)
            if container.is_contains("button.png"):
            ...     print("Button is inside dialog")

        Raises:
            ShadowstepImageNotFoundError: If container image not found on screen.

        Note:
            This performs template matching within the bounding box of this image.

        """
        self.ensure_visible()

        # Get screenshot and crop to this image's bounds
        screenshot = self._get_screenshot_as_bytes()
        full_image_array = self.to_ndarray(screenshot, grayscale=True)

        x1, y1, x2, y2 = self._coords  # type: ignore[misc]
        cropped_region = full_image_array[y1:y2, x1:x2]

        # Convert target image to ndarray
        target_array = self.to_ndarray(image, grayscale=True)

        # Perform template matching in cropped region
        max_val, _ = self.multi_scale_matching(
            full_image=cropped_region,
            template_image=target_array,
        )

        result = max_val >= self.threshold
        self.logger.info(
            "is_contains: max_val=%.3f, threshold=%.3f, result=%s",
            max_val,
            self.threshold,
            result,
        )
        return result

    @property
    def should(self) -> Any:  # type: ignore[return-any]
        """ImageShould functionality - assertions interface.

        Example:
            image.should.be_visible()
            image.should.have_text("Hello")

        Note:
            Not yet implemented. Reserved for future assertion DSL.

        """
        self.logger.info("%s", get_current_func_name())
        raise ShadowstepImageNotImplementedError(feature="ImageShould functionality")

    @log_image()
    def to_ndarray(
        self,
        image: bytes | np.ndarray[Any, Any] | PILImage.Image | str,
        grayscale: bool = True,  # noqa: FBT001, FBT002
    ) -> np.ndarray[Any, Any]:
        """Convert various image formats to numpy array.

        Args:
            image: Image in various formats:
                - bytes: Raw image bytes
                - np.ndarray: Already a numpy array (returned as-is or converted)
                - PIL.Image.Image: PIL Image object
                - str: File path to image
            grayscale: If True, convert to grayscale. Default: True.

        Returns:
            np.ndarray[Any, Any]: Image as numpy array (grayscale or RGB).

        Example:
            arr = image.to_ndarray("button.png")
            arr_color = image.to_ndarray("icon.png", grayscale=False)

        Note:
            This method is adapted from legacy _to_ndarray implementation.

        """
        result: np.ndarray[Any, Any]

        # Handle bytes
        if isinstance(image, bytes):
            result = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)  # type: ignore[reportAssignmentType]

        # Handle file path
        elif isinstance(image, str):
            result = cv2.imread(image, cv2.IMREAD_COLOR)  # type: ignore[reportAssignmentType]
            if result is None:  # type: ignore[reportUnnecessaryComparison]
                raise ShadowstepImageLoadError(path=image)

        # Handle PIL Image
        elif isinstance(image, PILImage.Image):
            result = np.array(image)
            # Convert RGB to BGR for OpenCV compatibility
            if len(result.shape) == 3 and result.shape[2] == 3:  # noqa: PLR2004
                result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

        # Handle numpy array
        elif isinstance(image, np.ndarray):  # type: ignore[reportUnnecessaryIsInstance]
            result = image

        else:
            raise ShadowstepUnsupportedImageTypeError(image_type=type(image).__name__)

        # Convert to grayscale if requested
        if grayscale:
            result = self._to_grayscale(result)

        return result

    @log_image()
    def multi_scale_matching(
        self,
        full_image: np.ndarray[Any, Any],
        template_image: np.ndarray[Any, Any],
    ) -> tuple[float, tuple[int, int]]:
        """Perform multi-scale template matching.

        Args:
            full_image: The full image to search in (grayscale).
            template_image: The template image to search for (grayscale).

        Returns:
            tuple[float, tuple[int, int]]:
                - confidence: Match confidence (0.0 to 1.0)
                - coordinates: (x, y) top-left corner of best match

        Example:
            screenshot = image.to_ndarray(screenshot_bytes)
            template = image.to_ndarray("button.png")
            confidence, (x, y) = image.multi_scale_matching(screenshot, template)

        Note:
            This method tries multiple scales (0.2x to 2.0x) to handle
            different screen densities and resolutions. Adapted from
            legacy _multi_scale_matching implementation.

        """
        origin_width, origin_height = template_image.shape[::-1]

        best_val = 0.0
        best_loc = (0, 0)

        # Try both shrinking (0.2-1.0) and expanding (1.1-2.0) scales
        scales = np.concatenate(
            [
                np.linspace(0.2, 1.0, 10)[::-1],  # Shrink template
                np.linspace(1.1, 2.0, 10),  # Expand template
            ],
        )

        for scale in scales:
            # Resize template to current scale
            new_width = int(origin_width * scale)
            new_height = int(origin_height * scale)

            # Skip if resized template is larger than full image
            if new_height > full_image.shape[0] or new_width > full_image.shape[1]:
                continue

            resized_template = cv2.resize(template_image, (new_width, new_height))

            # Perform template matching
            try:
                result = cv2.matchTemplate(full_image, resized_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                max_loc = (int(max_loc[0]), int(max_loc[1]))

                # Update best match if this is better
                if max_val > best_val:
                    best_val = max_val
                    best_loc = max_loc

                # Early exit if we found a very good match
                if max_val > self.MIN_SUFFICIENT_MATCH:
                    break

            except cv2.error as e:
                self.logger.warning("Template matching error at scale %.2f: %s", scale, e)
                continue

        self.logger.info("Multi-scale matching: best_val=%.3f at %s", best_val, best_loc)
        return best_val, best_loc

    # ==================== ADDITIONAL METHODS (P2 - Extended functionality) ====================

    @log_image()
    def find_all(
        self,
        coord_threshold: int = 5,
    ) -> list[tuple[int, int, int, int]]:
        """Find all occurrences of the image on screen.

        Args:
            coord_threshold: Minimum pixel distance between matches to consider them unique.

        Returns:
            list[tuple[int, int, int, int]]: List of (x1, y1, x2, y2) coordinates
                for each match found.

        Example:
            # Find all instances of a button
            all_buttons = image.find_all()
            print(f"Found {len(all_buttons)} buttons")
            for x1, y1, x2, y2 in all_buttons:
            ...     print(f"Button at ({x1}, {y1})")

        Note:
            This is migrated from legacy get_many_coordinates_of_image.
            Close matches (within coord_threshold pixels) are filtered out.

        """
        screenshot = self._get_screenshot_as_bytes()
        full_image = self.to_ndarray(screenshot, grayscale=True)
        template = self.to_ndarray(self._image, grayscale=True)

        # Perform multi-scale matching to get all possible matches
        # We need to modify multi_scale_matching to return raw result
        result = self._multi_scale_matching_raw(full_image, template)

        if result is None:
            self.logger.warning("No matches found for find_all()")
            return []

        # Get all matches above threshold
        locations = np.where(result >= self.threshold)
        matches = list(zip(*locations[::-1]))

        # Filter out duplicate/close matches
        unique_matches: list[tuple[int, int]] = []
        for x1, y1 in matches:
            is_duplicate = False
            for x2, y2 in unique_matches:
                if abs(x1 - x2) <= coord_threshold and abs(y1 - y2) <= coord_threshold:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_matches.append((x1, y1))

        # Convert to bounding boxes
        template_height, template_width = template.shape[:2]
        bounding_boxes = [
            (x, y, x + template_width, y + template_height) for x, y in unique_matches
        ]

        self.logger.info("Found %d unique matches", len(bounding_boxes))
        return bounding_boxes

    @log_image()
    def draw_rectangle(
        self,
        output_path: str = "debug_screenshot.png",
    ) -> bool:
        """Draw a rectangle around the image on a screenshot for debugging.

        Args:
            output_path: Path to save the debug screenshot. Default: "debug_screenshot.png".

        Returns:
            bool: True if successful, False otherwise.

        Example:
            image.draw_rectangle("found_button.png")  # Visual debugging

        Note:
            This is useful for debugging template matching issues.
            Migrated from legacy draw_by_coordinates.

        """
        try:
            self.ensure_visible()

            screenshot = self._get_screenshot_as_bytes()
            img_array = self.to_ndarray(screenshot, grayscale=False)

            x1, y1, x2, y2 = self._coords  # type: ignore[misc]

            # Draw green rectangle
            cv2.rectangle(img_array, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Save image
            success = cv2.imwrite(output_path, img_array)

            if success:
                self.logger.info("Debug screenshot saved to: %s", output_path)
            else:
                self.logger.error("Failed to save debug screenshot")

        except Exception:
            self.logger.exception("Error drawing rectangle")
            return False
        else:
            return success

    @log_image()
    def ensure_visible(self) -> None:
        """Check visibility and cache coordinates/center if found.

        This method performs template matching to find the image on screen
        and caches the results for subsequent operations. It's called
        automatically by most methods that need coordinates.

        Raises:
            ShadowstepImageNotFoundError: If image not found within timeout period.

        Note:
            Results are cached and reused. Call this method explicitly
            to force a fresh search (e.g., after screen changes).

        """
        coords = self._get_image_coordinates()
        if coords is None:
            self.logger.error("Image not visible on screen")
            raise ShadowstepImageNotFoundError(
                threshold=self.threshold,
                timeout=self.timeout,
                operation="visibility check",
            )

        self._coords = coords
        self._center = self._calculate_center(coords)
        self._last_screenshot_time = time.time()
        self.logger.info("Image found at coords=%s, center=%s", self._coords, self._center)

    def _get_screenshot_as_bytes(self) -> bytes:
        """Get current screenshot as bytes.

        Returns:
            bytes: Screenshot in PNG format as bytes.

        """
        screenshot_b64 = self.shadowstep.driver.get_screenshot_as_base64()
        return base64.b64decode(screenshot_b64.encode("utf-8"))

    def _get_image_coordinates(self) -> tuple[int, int, int, int] | None:
        """Find coordinates of the image on current screen.

        Returns:
            tuple[int, int, int, int] | None: (x1, y1, x2, y2) if found, None otherwise.

        Note:
            This is the core template matching logic migrated from legacy
            get_image_coordinates method.

        """
        try:
            # Get screenshot
            screenshot = self._get_screenshot_as_bytes()
            full_image = self.to_ndarray(screenshot, grayscale=True)

            # Convert template to ndarray
            template = self.to_ndarray(self._image, grayscale=True)

            # Perform multi-scale matching
            max_val, max_loc = self.multi_scale_matching(full_image, template)

            # Check if match is good enough
            if max_val < self.threshold:
                self.logger.info(
                    "Match quality %.3f below threshold %.3f",
                    max_val,
                    self.threshold,
                )
                return None

            # Calculate bounding box
            template_height, template_width = template.shape[:2]
            x1 = int(max_loc[0])
            y1 = int(max_loc[1])
            x2 = x1 + template_width
            y2 = y1 + template_height

        except Exception:
            self.logger.exception("Error finding image coordinates")
            return None
        else:
            return x1, y1, x2, y2

    @staticmethod
    def _calculate_center(coords: tuple[int, int, int, int]) -> tuple[int, int]:
        """Calculate center point from bounding box coordinates.

        Args:
            coords: (x1, y1, x2, y2) bounding box.

        Returns:
            tuple[int, int]: (x, y) center coordinates.

        """
        x1, y1, x2, y2 = coords
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return center_x, center_y

    def _to_grayscale(self, image: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        """Convert image to grayscale if it's in color.

        Args:
            image: Input image array.

        Returns:
            np.ndarray: Grayscale image array.

        Note:
            Migrated from legacy to_grayscale method.

        """
        # Check if already grayscale
        if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):  # noqa: PLR2004
            return image

        # Convert RGB/BGR to grayscale
        if len(image.shape) == 3 and image.shape[2] == 3:  # noqa: PLR2004
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return cv2.convertScaleAbs(gray)

        return image

    def _scroll_to_image(
        self,
        direction: str,
        from_percent: float = 0.5,
        to_percent: float = 0.1,
        max_attempts: int = 10,
        step_delay: float = 0.5,
    ) -> ShadowstepImage:
        """Internal method to scroll in a direction until image is found.

        Args:
            direction: "up", "down", "left", or "right".
            from_percent: Starting position (for down/right).
            to_percent: Ending position (for down/right).
            max_attempts: Maximum scroll attempts.
            step_delay: Delay between attempts.

        Returns:
            ShadowstepImage: Self for method chaining.

        Raises:
            ShadowstepImageNotFoundError: If image not found after max_attempts.

        """
        for attempt in range(max_attempts):
            # Check if image is visible
            if self.is_visible():
                self.logger.info("Image found after %d scroll attempts", attempt)
                return self

            # Perform scroll
            self._perform_scroll(direction, from_percent, to_percent)

            # Wait before next attempt
            time.sleep(step_delay)

        # Not found after all attempts
        self.logger.error("Image not found after scroll attempts")
        raise ShadowstepImageNotFoundError(
            threshold=self.threshold,
            timeout=self.timeout,
            operation=f"{max_attempts} scroll attempts ({direction})",
        )

    def _perform_scroll(
        self,
        direction: str,
        from_percent: float = 0.5,
        to_percent: float = 0.1,
    ) -> None:
        """Perform a single scroll gesture.

        Args:
            direction: "up", "down", "left", or "right".
            from_percent: Starting position as percentage of screen dimension.
            to_percent: Ending position as percentage of screen dimension.

        """
        # Get screen dimensions
        width = int(self.shadowstep.driver.get_window_size()["width"])  # type: ignore[reportUnknownMemberType]
        height = int(self.shadowstep.driver.get_window_size()["height"])  # type: ignore[reportUnknownMemberType]

        # Calculate scroll coordinates based on direction
        if direction == "down":
            start_x = int(width // 2)
            start_y = int(height * from_percent)
            end_x = int(width // 2)
            end_y = int(height * to_percent)
        elif direction == "up":
            start_x = int(width // 2)
            start_y = int(height * to_percent)
            end_x = int(width // 2)
            end_y = int(height * from_percent)
        elif direction == "left":
            start_x = int(width * from_percent)
            start_y = int(height // 2)
            end_x = int(width * to_percent)
            end_y = int(height // 2)
        elif direction == "right":
            start_x = int(width * to_percent)
            start_y = int(height // 2)
            end_x = int(width * from_percent)
            end_y = int(height // 2)
        else:
            raise ShadowstepInvalidScrollDirectionError(
                direction=direction,
                valid_directions=["up", "down", "left", "right"],
            )

        # Perform swipe
        self.shadowstep.driver.swipe(start_x, start_y, end_x, end_y, duration=500)
        self.logger.info(
            "Scrolled %s: (%d,%d) -> (%d,%d)",
            direction,
            start_x,
            start_y,
            end_x,
            end_y,
        )

    def _multi_scale_matching_raw(
        self,
        full_image: np.ndarray[Any, Any],
        template_image: np.ndarray[Any, Any],
    ) -> np.ndarray[Any, Any] | None:
        """Perform multi-scale matching and return raw result matrix.

        This is used by find_all() to get all matches, not just the best one.

        Args:
            full_image: Full image to search in.
            template_image: Template to search for.

        Returns:
            np.ndarray | None: Raw matching result matrix or None if no valid matches.

        """
        origin_width, origin_height = template_image.shape[::-1]

        # Try multiple scales
        scales = np.concatenate(
            [
                np.linspace(0.2, 1.0, 10)[::-1],
                np.linspace(1.1, 2.0, 10),
            ],
        )

        for scale in scales:
            new_width = int(origin_width * scale)
            new_height = int(origin_height * scale)

            # Skip if resized template is larger than full image
            if new_height > full_image.shape[0] or new_width > full_image.shape[1]:
                continue

            resized_template = cv2.resize(template_image, (new_width, new_height))

            try:
                result = cv2.matchTemplate(full_image, resized_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)

                if max_val > self.threshold:
                    return result

            except cv2.error:
                continue

        return None
