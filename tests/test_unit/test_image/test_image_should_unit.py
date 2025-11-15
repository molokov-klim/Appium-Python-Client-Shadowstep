# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Unit tests for ImageShould assertion classes using mocks."""
from unittest.mock import Mock

import pytest

from shadowstep.image.image import ShadowstepImage
from shadowstep.image.should import ImageShould, _ShouldBe, _ShouldNotBe


class TestImageShouldInit:
    """Test ImageShould initialization."""

    def test_init_creates_instance_with_image(self):
        """Test initialization creates instance with image reference."""
        mock_image = Mock(spec=ShadowstepImage)

        should = ImageShould(mock_image)

        assert should.image == mock_image
        assert isinstance(should.be, _ShouldBe)
        assert isinstance(should.not_be, _ShouldNotBe)

    def test_getattr_delegates_to_image(self):
        """Test __getattr__ delegates to underlying image."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.some_method = Mock(return_value="test_value")

        should = ImageShould(mock_image)

        result = should.some_method()

        assert result == "test_value"
        mock_image.some_method.assert_called_once()

    def test_getattr_raises_attribute_error_when_not_found(self):
        """Test __getattr__ raises AttributeError when attribute doesn't exist."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.__class__.__name__ = "ShadowstepImage"

        should = ImageShould(mock_image)

        with pytest.raises(AttributeError) as exc_info:
            _ = should.nonexistent_attribute

        assert "ImageShould" in str(exc_info.value)
        assert "nonexistent_attribute" in str(exc_info.value)


class TestImageShouldBeVisible:
    """Test should.be.visible assertion."""

    def test_be_visible_passes_when_image_is_visible(self):
        """Test be.visible passes when image is visible."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.is_visible = Mock(return_value=True)

        should = ImageShould(mock_image)

        result = should.be.visible()

        mock_image.is_visible.assert_called_once()
        assert isinstance(result, ImageShould)

    def test_be_visible_raises_when_image_is_not_visible(self):
        """Test be.visible raises AssertionError when image is not visible."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.is_visible = Mock(return_value=False)

        should = ImageShould(mock_image)

        with pytest.raises(AssertionError) as exc_info:
            should.be.visible()

        assert "be.visible" in str(exc_info.value)
        assert "[should]" in str(exc_info.value)


class TestImageShouldNotBeVisible:
    """Test should.not_be.visible assertion."""

    def test_not_be_visible_passes_when_image_is_not_visible(self):
        """Test not_be.visible passes when image is not visible."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.is_visible = Mock(return_value=False)

        should = ImageShould(mock_image)

        result = should.not_be.visible()

        assert isinstance(result, ImageShould)

    def test_not_be_visible_raises_when_image_is_visible(self):
        """Test not_be.visible raises AssertionError when image is visible."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.is_visible = Mock(return_value=True)

        should = ImageShould(mock_image)

        with pytest.raises(AssertionError) as exc_info:
            should.not_be.visible()

        assert "[should.not]" in str(exc_info.value)


class TestImageShouldContain:
    """Test should.contain assertion."""

    def test_contain_passes_when_image_contains_target(self):
        """Test contain passes when image contains target."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.is_contains = Mock(return_value=True)

        should = ImageShould(mock_image)

        result = should.contain("button.png")

        mock_image.is_contains.assert_called_with("button.png")
        assert isinstance(result, ImageShould)

    def test_contain_raises_when_image_does_not_contain_target(self):
        """Test contain raises AssertionError when image doesn't contain target."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.is_contains = Mock(return_value=False)

        should = ImageShould(mock_image)

        with pytest.raises(AssertionError) as exc_info:
            should.contain("button.png")

        assert "contain" in str(exc_info.value)
        assert "[should]" in str(exc_info.value)

    def test_contain_with_bytes(self):
        """Test contain works with bytes."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.is_contains = Mock(return_value=True)

        should = ImageShould(mock_image)
        image_bytes = b"fake_image_data"

        result = should.contain(image_bytes)

        mock_image.is_contains.assert_called_with(image_bytes)
        assert isinstance(result, ImageShould)


class TestImageShouldNotContain:
    """Test should.not_contain assertion."""

    def test_not_contain_passes_when_image_does_not_contain_target(self):
        """Test not_contain passes when image doesn't contain target."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.is_contains = Mock(return_value=False)

        should = ImageShould(mock_image)

        result = should.not_contain("button.png")

        mock_image.is_contains.assert_called_with("button.png")
        assert isinstance(result, ImageShould)

    def test_not_contain_raises_when_image_contains_target(self):
        """Test not_contain raises AssertionError when image contains target."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.is_contains = Mock(return_value=True)

        should = ImageShould(mock_image)

        with pytest.raises(AssertionError) as exc_info:
            should.not_contain("button.png")

        assert "not_contain" in str(exc_info.value)
        assert "[should.not]" in str(exc_info.value)


class TestMethodChaining:
    """Test method chaining capability."""

    def test_chaining_be_and_contain_assertions(self):
        """Test chaining be and contain assertions."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.is_visible = Mock(return_value=True)
        mock_image.is_contains = Mock(return_value=True)

        should = ImageShould(mock_image)

        # Chain multiple assertions
        result = should.be.visible().contain("icon.png")

        assert isinstance(result, ImageShould)
        mock_image.is_visible.assert_called_once()
        mock_image.is_contains.assert_called_with("icon.png")

    def test_chaining_multiple_contain_assertions(self):
        """Test chaining multiple contain assertions."""
        mock_image = Mock(spec=ShadowstepImage)
        mock_image.is_contains = Mock(return_value=True)

        should = ImageShould(mock_image)

        # Chain multiple contain assertions
        result = should.contain("button.png").contain("icon.png")

        assert isinstance(result, ImageShould)
        assert mock_image.is_contains.call_count == 2


class TestShouldProperty:
    """Test should property on ShadowstepImage."""

    def test_should_property_returns_image_should_instance(self):
        """Test that should property returns ImageShould instance."""
        mock_image = Mock(spec=ShadowstepImage)
        
        # Mock the should property to return ImageShould
        mock_image.should = ImageShould(mock_image)
        
        assert isinstance(mock_image.should, ImageShould)
        assert mock_image.should.image == mock_image

