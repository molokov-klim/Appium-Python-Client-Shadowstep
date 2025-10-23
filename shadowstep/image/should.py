"""Image assertions module for Shadowstep framework.

This module provides DSL-style assertions for images using 'should.be' syntax.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from shadowstep.image.image import ShadowstepImage


class ImageShould:
    """DSL wrapper for image assertions using 'should.be' syntax."""

    def __init__(self, image: ShadowstepImage) -> None:
        """Initialize ImageShould instance.

        Args:
            image: The ShadowstepImage to perform assertions on.

        """
        self.image = image
        self.be = _ShouldBe(image)
        self.not_be = _ShouldNotBe(image)

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attribute access to the underlying ShadowstepImage instance."""
        try:
            return getattr(self.image, name)
        except AttributeError as error:
            msg = (
                f"'ImageShould' has no attribute '{name}', and '{self.image.__class__.__name__}' "
                "also does not have it."
            )
            raise AttributeError(msg) from error

    def contain(
        self,
        image: bytes | Any | str,
    ) -> ImageShould:
        """Assert that this image contains another image.

        Args:
            image: Image to search for within this image's bounds.

        Returns:
            ImageShould: Self for method chaining.

        Raises:
            AssertionError: If the image does not contain the target image.

        Example:
            container.should.contain("button.png")

        """
        result = self.image.is_contains(image)
        if not result:
            msg = "[should] contain: expected image to contain target, but it doesn't"
            raise AssertionError(
                msg,
            )
        return self

    def not_contain(
        self,
        image: bytes | Any | str,
    ) -> ImageShould:
        """Assert that this image does not contain another image.

        Args:
            image: Image to search for within this image's bounds.

        Returns:
            ImageShould: Self for method chaining.

        Raises:
            AssertionError: If the image contains the target image.

        Example:
            container.should.not_contain("button.png")

        """
        result = self.image.is_contains(image)
        if result:
            msg = "[should.not] not_contain: expected image not to contain target, but it does"
            raise AssertionError(
                msg,
            )
        return self


class _ShouldBase:
    """Base class for 'be' assertion helpers, with optional negation."""

    def __init__(self, image: ShadowstepImage, negate: bool = False) -> None:  # noqa: FBT001, FBT002
        self.image = image
        self.negate = negate

    def _assert(self, condition: bool, message: str) -> None:  # noqa: FBT001
        if self.negate:
            if condition:
                raise AssertionError("[should.not] " + message)
        elif not condition:
            raise AssertionError("[should] " + message)


class _ShouldBe(_ShouldBase):
    """Assertions for image state: should.be.visible."""

    def visible(self) -> ImageShould:
        """Assert that the image is visible on screen.

        Returns:
            ImageShould: ImageShould instance for method chaining.

        Raises:
            AssertionError: If the image is not visible.

        Example:
            image.should.be.visible()

        """
        self._assert(self.image.is_visible(), "be.visible: expected image to be visible")
        return ImageShould(self.image)


class _ShouldNotBe(_ShouldBe):
    """Negative assertions for 'be': should.not_be.visible()."""

    def __init__(self, image: ShadowstepImage) -> None:
        super().__init__(image, negate=True)
