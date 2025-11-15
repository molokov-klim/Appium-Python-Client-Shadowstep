# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Integration tests for ImageShould assertion classes."""

from typing import Any

import pytest

from shadowstep.image.image import ShadowstepImage
from shadowstep.shadowstep import Shadowstep

ELEMENT_1_IMG_PATH = "tests/test_integro/_test_data/element.png"
ELEMENT_2_IMG_PATH = "tests/test_integro/_test_data/element2.png"
CONNECTED_DEVICES_IMG_PATH = "tests/test_integro/_test_data/connected_devices.png"


class TestImageShould:
    """Test class for ImageShould assertion functionality."""

    def test_should_be_visible_passes(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test should.be.visible passes when image is visible."""
        img = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.7)
        
        # Should not raise
        img.should.be.visible()

    def test_should_be_visible_fails_when_not_visible(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test should.be.visible raises when image is not visible."""
        # Use an image that doesn't exist on screen
        # We'll use a completely different image that shouldn't be visible
        img = ShadowstepImage(CONNECTED_DEVICES_IMG_PATH, threshold=0.7)
        
        # If the image is actually visible, skip the test
        if img.is_visible():
            pytest.skip("Image is visible on screen, cannot test negative case")
        
        with pytest.raises(AssertionError) as exc_info:
            img.should.be.visible()
        
        assert "[should]" in str(exc_info.value)
        assert "be.visible" in str(exc_info.value)

    def test_should_not_be_visible_passes(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test should.not_be.visible passes when image is not visible."""
        # Use an image that doesn't exist on screen
        img = ShadowstepImage(CONNECTED_DEVICES_IMG_PATH, threshold=0.7)
        
        # If the image is actually visible, skip the test
        if img.is_visible():
            pytest.skip("Image is visible on screen, cannot test negative case")
        
        # Should not raise
        img.should.not_be.visible()

    def test_should_not_be_visible_fails_when_visible(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test should.not_be.visible raises when image is visible."""
        img = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.7)
        
        with pytest.raises(AssertionError) as exc_info:
            img.should.not_be.visible()
        
        assert "[should.not]" in str(exc_info.value)

    def test_should_contain_passes(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test should.contain passes when image contains target."""
        # First ensure the container is visible
        container = ShadowstepImage(CONNECTED_DEVICES_IMG_PATH, threshold=0.6)
        
        if not container.is_visible():
            pytest.skip("Container image not visible, skipping contain test")
        
        # Use a smaller threshold for the contained image
        container.should.contain(ELEMENT_2_IMG_PATH)

    def test_should_contain_fails_when_not_contains(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test should.contain raises when image doesn't contain target."""
        container = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.7)
        
        # Ensure container is visible
        if not container.is_visible():
            pytest.skip("Container image not visible")
        
        # Try to find an image that definitely isn't there
        # Using a completely different image
        with pytest.raises(AssertionError) as exc_info:
            container.should.contain(CONNECTED_DEVICES_IMG_PATH)
        
        assert "[should]" in str(exc_info.value)
        assert "contain" in str(exc_info.value)

    def test_should_not_contain_passes(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test should.not_contain passes when image doesn't contain target."""
        container = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.7)
        
        # Ensure container is visible
        if not container.is_visible():
            pytest.skip("Container image not visible")
        
        # Should not raise - image definitely doesn't contain this
        container.should.not_contain(CONNECTED_DEVICES_IMG_PATH)

    def test_should_not_contain_fails_when_contains(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test should.not_contain raises when image contains target."""
        container = ShadowstepImage(CONNECTED_DEVICES_IMG_PATH, threshold=0.6)
        
        # Ensure container is visible
        if not container.is_visible():
            pytest.skip("Container image not visible")
        
        with pytest.raises(AssertionError) as exc_info:
            container.should.not_contain(ELEMENT_2_IMG_PATH)
        
        assert "[should.not]" in str(exc_info.value)
        assert "not_contain" in str(exc_info.value)

    def test_method_chaining_be_and_contain(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test chaining be.visible and contain assertions."""
        container = ShadowstepImage(CONNECTED_DEVICES_IMG_PATH, threshold=0.6)
        
        if not container.is_visible():
            pytest.skip("Container image not visible")
        
        # Chain assertions
        container.should.be.visible().contain(ELEMENT_2_IMG_PATH)

    def test_method_chaining_multiple_assertions(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test chaining multiple assertions."""
        img1 = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.7)
        img2 = ShadowstepImage(ELEMENT_2_IMG_PATH, threshold=0.7)
        
        # Both should be visible
        img1.should.be.visible()
        img2.should.be.visible()

    def test_should_property_returns_correct_type(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test that should property returns ImageShould instance."""
        from shadowstep.image.should import ImageShould
        
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        
        assert hasattr(img, "should")
        assert isinstance(img.should, ImageShould)
        assert img.should.image is img

    def test_should_getattr_delegates_to_image(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test that should.__getattr__ delegates to underlying image."""
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        
        # Access image attributes through should
        assert img.should.threshold == img.threshold
        assert img.should.timeout == img.timeout

    def test_should_getattr_raises_for_unknown_attribute(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test that should.__getattr__ raises AttributeError for unknown attributes."""
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        
        with pytest.raises(AttributeError) as exc_info:
            _ = img.should.nonexistent_attribute
        
        assert "ImageShould" in str(exc_info.value)
        assert "nonexistent_attribute" in str(exc_info.value)

    def test_should_assertions_can_be_combined(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test that multiple should assertions can be combined."""
        img = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.7)
        
        # Perform multiple assertions
        img.should.be.visible()
        
        # Can create new should chain
        img.should.be.visible()
        
        # All assertions should pass

    def test_should_with_bytes_image(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test should works with bytes image."""
        # Load image as bytes
        with open(ELEMENT_1_IMG_PATH, "rb") as f:
            image_bytes = f.read()
        
        img = ShadowstepImage(image_bytes, threshold=0.7)
        
        # Should work with bytes
        img.should.be.visible()

    def test_should_with_different_thresholds(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test should with different threshold values."""
        # Low threshold - should find image
        img_low = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.5)
        img_low.should.be.visible()
        
        # Very high threshold - might not find image
        img_high = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.99)
        # This will likely fail, which is expected
        try:
            img_high.should.be.visible()
        except AssertionError:
            pass  # Expected

    def test_should_fails_with_clear_message(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        """Test that should failures provide clear error messages."""
        # Use an image that doesn't exist on screen
        img = ShadowstepImage(CONNECTED_DEVICES_IMG_PATH, threshold=0.7)
        
        # If the image is actually visible, skip the test
        if img.is_visible():
            pytest.skip("Image is visible on screen, cannot test negative case")
        
        with pytest.raises(AssertionError) as exc_info:
            img.should.be.visible()
        
        error_msg = str(exc_info.value)
        assert "[should]" in error_msg
        assert "be.visible" in error_msg
        assert "expected image to be visible" in error_msg

