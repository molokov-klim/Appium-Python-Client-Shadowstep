"""Image-based interaction module for Shadowstep framework.

This module provides the ShadowstepImage class for performing
image-based automation operations such as image recognition,
tapping, dragging, scrolling, and other visual interactions
with mobile applications.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np
from PIL import Image as PILImage

from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    from shadowstep.shadowstep import Shadowstep


class ShadowstepImage:
    """Lazy wrapper for image-based interactions."""

    def __init__(
        self,
        image: bytes | np.ndarray[Any, Any] | PILImage.Image | str,
        base: Shadowstep,
        threshold: float = 0.5,
        timeout: float = 5.0,
    ) -> None:
        """Initialize the ShadowstepImage.

        Args:
            image: Image data in various formats (bytes, numpy array, PIL Image, or file path).
            base: Shadowstep instance for automation operations.
            threshold: Matching threshold for image recognition (0.0 to 1.0).
            timeout: Timeout in seconds for image visibility operations.

        """
        self._image = image
        self._base: Shadowstep = base
        self.threshold = threshold
        self.timeout = timeout
        self._coords: tuple[int, int, int, int] | None = None
        self._center: tuple[int, int] | None = None
        self.logger = logging.getLogger(__name__)

    def _ensure_visible(self) -> None:
        """Check visibility and cache coordinates/center if found."""
        raise NotImplementedError

    def tap(self, duration: int | None = None) -> ShadowstepImage:
        """Tap on the image center.

        Args:
            duration: Duration of the tap in milliseconds.

        Returns:
            ShadowstepImage: Self for method chaining.

        """
        raise NotImplementedError

    def drag(self, to: tuple[int, int] | ShadowstepImage, duration: float = 1.0) -> ShadowstepImage:
        """Drag from image center to target location.

        Args:
            to: Target coordinates as tuple or another ShadowstepImage.
            duration: Duration of the drag gesture in seconds.

        Returns:
            ShadowstepImage: Self for method chaining.

        """
        raise NotImplementedError

    def zoom(self, percent: float = 1.5, steps: int = 10) -> ShadowstepImage:
        """Zoom in on the image center.

        Args:
            percent: Zoom percentage (1.0 = no zoom, >1.0 = zoom in).
            steps: Number of steps to perform the zoom.

        Returns:
            ShadowstepImage: Self for method chaining.

        """
        raise NotImplementedError

    def unzoom(self, percent: float = 0.5, steps: int = 10) -> ShadowstepImage:
        """Zoom out from the image center.

        Args:
            percent: Zoom percentage (<1.0 = zoom out).
            steps: Number of steps to perform the zoom.

        Returns:
            ShadowstepImage: Self for method chaining.

        """
        raise NotImplementedError

    def wait(self) -> bool:
        """Wait for the image to become visible.

        Returns:
            bool: True if image becomes visible within timeout, False otherwise.

        """
        raise NotImplementedError

    def wait_not(self) -> bool:
        """Wait for the image to become invisible.

        Returns:
            bool: True if image becomes invisible within timeout, False otherwise.

        """
        raise NotImplementedError

    def is_visible(self) -> bool:
        """Check if the image is currently visible on screen.

        Returns:
            bool: True if image is visible, False otherwise.

        """
        raise NotImplementedError

    @property
    def coordinates(self) -> tuple[int, int, int, int]:
        """Get the bounding box coordinates of the image.

        Returns:
            tuple[int, int, int, int]: (x1, y1, x2, y2) coordinates of the image.

        """
        raise NotImplementedError

    @property
    def center(self) -> tuple[int, int]:
        """Get the center coordinates of the image.

        Returns:
            tuple[int, int]: (x, y) center coordinates of the image.

        """
        raise NotImplementedError

    def scroll_down(
        self,
        from_percent: float = 0.5,
        to_percent: float = 0.1,
        max_attempts: int = 10,
        step_delay: float = 0.5,
    ) -> ShadowstepImage:
        """Scroll down within the image container.

        Args:
            from_percent: Starting position as percentage of container height.
            to_percent: Ending position as percentage of container height.
            max_attempts: Maximum number of scroll attempts.
            step_delay: Delay between scroll attempts in seconds.

        Returns:
            ShadowstepImage: Self for method chaining.

        """
        raise NotImplementedError

    def scroll_up(self, max_attempts: int = 10, step_delay: float = 0.5) -> ShadowstepImage:
        """Scroll up to find the image.

        Args:
            max_attempts: Maximum number of scroll attempts.
            step_delay: Delay between scroll attempts in seconds.

        Returns:
            ShadowstepImage: Self for method chaining.

        """
        raise NotImplementedError

    def scroll_left(self, max_attempts: int = 10, step_delay: float = 0.5) -> ShadowstepImage:
        """Scroll left to find the image.

        Args:
            max_attempts: Maximum number of scroll attempts.
            step_delay: Delay between scroll attempts in seconds.

        Returns:
            ShadowstepImage: Self for method chaining.

        """
        raise NotImplementedError

    def scroll_right(self, max_attempts: int = 10, step_delay: float = 0.5) -> ShadowstepImage:
        """Scroll right to find the image.

        Args:
            max_attempts: Maximum number of scroll attempts.
            step_delay: Delay between scroll attempts in seconds.

        Returns:
            ShadowstepImage: Self for method chaining.

        """
        raise NotImplementedError

    def scroll_to(self, max_attempts: int = 10, step_delay: float = 0.5) -> ShadowstepImage:
        """Scroll to bring the image into view.

        Args:
            max_attempts: Maximum number of scroll attempts.
            step_delay: Delay between scroll attempts in seconds.

        Returns:
            ShadowstepImage: Self for method chaining.

        """
        raise NotImplementedError

    def is_contains(self, image: bytes | np.ndarray[Any, Any] | PILImage.Image | str) -> bool:
        """Check if this image contains another image.

        Args:
            image: Image to search for (bytes, numpy array, PIL Image, or file path).

        Returns:
            bool: True if the image contains the target image, False otherwise.

        """
        raise NotImplementedError

    @property
    def should(self) -> Any:  # type: ignore[return-any]
        """ImageShould functionality - not yet implemented."""
        self.logger.debug("%s", get_current_func_name())
        raise NotImplementedError

    def to_ndarray(
        self, image: bytes | np.ndarray[Any, Any] | PILImage.Image | str,
    ) -> np.ndarray[Any, Any]:
        """Convert various image formats to numpy array.

        Args:
            image: Image in various formats (bytes, numpy array, PIL Image, or file path).

        Returns:
            np.ndarray[Any, Any]: Image as numpy array in RGB format.

        """
        raise NotImplementedError

    def _preprocess(self, image: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        raise NotImplementedError

    def _enhance_image(self, image: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        raise NotImplementedError

    def multi_scale_matching(
        self, full_image: np.ndarray[Any, Any], template_image: np.ndarray[Any, Any],
    ) -> tuple[float, tuple[int, int]]:
        """Perform multi-scale template matching.

        Args:
            full_image: The full image to search in.
            template_image: The template image to search for.

        Returns:
            tuple[float, tuple[int, int]]: (confidence, (x, y)) coordinates of best match.

        """
        raise NotImplementedError
