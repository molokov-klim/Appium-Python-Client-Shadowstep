# ruff: noqa
# pyright: ignore
"""Integration tests for ShadowstepImage class. Do not run in CI"""

from typing import Any

import pytest

from shadowstep.image.image import ShadowstepImage
from shadowstep.shadowstep import Shadowstep


class TestShadowstepImage:
    """Test class for ShadowstepImage functionality."""

    def test_initialization_with_string_image(self, app: Shadowstep):
        """Test ShadowstepImage initialization with string path.

        Steps:
        1. Create ShadowstepImage with string image path.
        2. Verify instance is created.
        3. Verify attributes are set correctly.
        """
        # Create instance with string path
        image_path = "/path/to/image.png"
        img = ShadowstepImage(image_path, app, threshold=0.8, timeout=10.0)

        # Verify instance
        assert img is not None  # noqa: S101
        assert isinstance(img, ShadowstepImage)  # noqa: S101

        # Verify attributes
        assert img._image == image_path  # noqa: S101
        assert img._base is app  # noqa: S101
        assert img.threshold == 0.8  # noqa: S101
        assert img.timeout == 10.0  # noqa: S101
        assert img._coords is None  # noqa: S101
        assert img._center is None  # noqa: S101

    def test_initialization_with_bytes_image(self, app: Shadowstep):
        """Test ShadowstepImage initialization with bytes.

        Steps:
        1. Create ShadowstepImage with bytes image data.
        2. Verify instance is created.
        3. Verify attributes are set correctly.
        """
        # Create instance with bytes
        image_bytes = b"fake_image_data"
        img = ShadowstepImage(image_bytes, app)

        # Verify instance
        assert img is not None  # noqa: S101
        assert isinstance(img, ShadowstepImage)  # noqa: S101
        assert img._image == image_bytes  # noqa: S101
        assert img._base is app  # noqa: S101

    def test_initialization_with_default_values(self, app: Shadowstep):
        """Test ShadowstepImage initialization with default threshold and timeout.

        Steps:
        1. Create ShadowstepImage without specifying threshold/timeout.
        2. Verify default values are set.
        """
        # Create instance with defaults
        img = ShadowstepImage("/path/to/image.png", app)

        # Verify defaults
        assert img.threshold == 0.7  # noqa: S101
        assert img.timeout == 5.0  # noqa: S101

    def test_tap(self, app: Shadowstep, android_settings_open_close: Any):
        img = ShadowstepImage("tests/test_integro/_test_data/element.png")
        img.tap()

    def test_tap_with_duration_raises_not_implemented_error(self, app: Shadowstep):
        """Test tap() with duration raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call tap() with duration parameter.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.tap(duration=500)

    def test_drag_with_tuple_raises_not_implemented_error(self, app: Shadowstep):
        """Test drag() method with tuple raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call drag() with tuple coordinates.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.drag(to=(100, 200))

    def test_drag_with_image_raises_not_implemented_error(self, app: Shadowstep):
        """Test drag() with another image raises NotImplementedError.

        Steps:
        1. Create two ShadowstepImage instances.
        2. Call drag() from first to second.
        3. Verify NotImplementedError is raised.
        """
        img1 = ShadowstepImage("/path/to/image1.png", app)
        img2 = ShadowstepImage("/path/to/image2.png", app)

        with pytest.raises(NotImplementedError):
            img1.drag(to=img2)

    def test_zoom_raises_not_implemented_error(self, app: Shadowstep):
        """Test zoom() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call zoom() method.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.zoom()

    def test_zoom_with_params_raises_not_implemented_error(self, app: Shadowstep):
        """Test zoom() with parameters raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call zoom() with percent and steps.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.zoom(percent=2.0, steps=20)

    def test_unzoom_raises_not_implemented_error(self, app: Shadowstep):
        """Test unzoom() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call unzoom() method.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.unzoom()

    def test_unzoom_with_params_raises_not_implemented_error(self, app: Shadowstep):
        """Test unzoom() with parameters raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call unzoom() with percent and steps.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.unzoom(percent=0.3, steps=15)

    def test_wait_raises_not_implemented_error(self, app: Shadowstep):
        """Test wait() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call wait() method.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.wait()

    def test_wait_not_raises_not_implemented_error(self, app: Shadowstep):
        """Test wait_not() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call wait_not() method.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.wait_not()

    def test_is_visible_raises_not_implemented_error(self, app: Shadowstep):
        """Test is_visible() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call is_visible() method.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.is_visible()

    def test_coordinates_property_raises_not_implemented_error(self, app: Shadowstep):
        """Test coordinates property raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Access coordinates property.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            _ = img.coordinates

    def test_center_property_raises_not_implemented_error(self, app: Shadowstep):
        """Test center property raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Access center property.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            _ = img.center

    def test_scroll_down_raises_not_implemented_error(self, app: Shadowstep):
        """Test scroll_down() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call scroll_down() method.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.scroll_down()

    def test_scroll_down_with_params_raises_not_implemented_error(self, app: Shadowstep):
        """Test scroll_down() with parameters raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call scroll_down() with all parameters.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.scroll_down(from_percent=0.7, to_percent=0.2, max_attempts=5, step_delay=1.0)

    def test_scroll_up_raises_not_implemented_error(self, app: Shadowstep):
        """Test scroll_up() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call scroll_up() method.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.scroll_up()

    def test_scroll_up_with_params_raises_not_implemented_error(self, app: Shadowstep):
        """Test scroll_up() with parameters raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call scroll_up() with parameters.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.scroll_up(max_attempts=15, step_delay=0.8)

    def test_scroll_left_raises_not_implemented_error(self, app: Shadowstep):
        """Test scroll_left() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call scroll_left() method.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.scroll_left()

    def test_scroll_left_with_params_raises_not_implemented_error(self, app: Shadowstep):
        """Test scroll_left() with parameters raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call scroll_left() with parameters.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.scroll_left(max_attempts=8, step_delay=0.6)

    def test_scroll_right_raises_not_implemented_error(self, app: Shadowstep):
        """Test scroll_right() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call scroll_right() method.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.scroll_right()

    def test_scroll_right_with_params_raises_not_implemented_error(self, app: Shadowstep):
        """Test scroll_right() with parameters raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call scroll_right() with parameters.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.scroll_right(max_attempts=12, step_delay=0.4)

    def test_scroll_to_raises_not_implemented_error(self, app: Shadowstep):
        """Test scroll_to() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call scroll_to() method.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.scroll_to()

    def test_scroll_to_with_params_raises_not_implemented_error(self, app: Shadowstep):
        """Test scroll_to() with parameters raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call scroll_to() with parameters.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.scroll_to(max_attempts=20, step_delay=1.5)

    def test_is_contains_raises_not_implemented_error(self, app: Shadowstep):
        """Test is_contains() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call is_contains() with another image.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.is_contains("/path/to/other.png")

    def test_is_contains_with_bytes_raises_not_implemented_error(self, app: Shadowstep):
        """Test is_contains() with bytes raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call is_contains() with bytes image.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.is_contains(b"image_bytes")

    def test_should_property_raises_not_implemented_error(self, app: Shadowstep):
        """Test should property raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Access should property.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            _ = img.should

    def test_to_ndarray_raises_not_implemented_error(self, app: Shadowstep):
        """Test to_ndarray() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call to_ndarray() with image.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.to_ndarray("/path/to/other.png")

    def test_to_ndarray_with_bytes_raises_not_implemented_error(self, app: Shadowstep):
        """Test to_ndarray() with bytes raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call to_ndarray() with bytes.
        3. Verify NotImplementedError is raised.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.to_ndarray(b"image_bytes")

    def test_multi_scale_matching_raises_not_implemented_error(self, app: Shadowstep):
        """Test multi_scale_matching() method raises NotImplementedError.

        Steps:
        1. Create ShadowstepImage instance.
        2. Call multi_scale_matching() with numpy arrays.
        3. Verify NotImplementedError is raised.

        Note: Using None as placeholder since numpy arrays aren't available.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        with pytest.raises(NotImplementedError):
            img.multi_scale_matching(None, None)  # type: ignore

    def test_logger_is_initialized(self, app: Shadowstep):
        """Test that logger is properly initialized.

        Steps:
        1. Create ShadowstepImage instance.
        2. Verify logger attribute exists.
        3. Verify logger is not None.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        assert hasattr(img, "logger")  # noqa: S101
        assert img.logger is not None  # noqa: S101

    def test_cached_coords_and_center_are_none_initially(self, app: Shadowstep):
        """Test that cached coordinates and center are None initially.

        Steps:
        1. Create ShadowstepImage instance.
        2. Verify _coords is None.
        3. Verify _center is None.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        assert img._coords is None  # noqa: S101
        assert img._center is None  # noqa: S101

    def test_threshold_can_be_set_to_different_values(self, app: Shadowstep):
        """Test threshold can be set to various valid values.

        Steps:
        1. Create instances with different threshold values.
        2. Verify each threshold is set correctly.
        """
        img1 = ShadowstepImage("/path/to/image.png", app, threshold=0.1)
        img2 = ShadowstepImage("/path/to/image.png", app, threshold=0.5)
        img3 = ShadowstepImage("/path/to/image.png", app, threshold=0.9)
        img4 = ShadowstepImage("/path/to/image.png", app, threshold=1.0)

        assert img1.threshold == 0.1  # noqa: S101
        assert img2.threshold == 0.5  # noqa: S101
        assert img3.threshold == 0.9  # noqa: S101
        assert img4.threshold == 1.0  # noqa: S101

    def test_timeout_can_be_set_to_different_values(self, app: Shadowstep):
        """Test timeout can be set to various valid values.

        Steps:
        1. Create instances with different timeout values.
        2. Verify each timeout is set correctly.
        """
        img1 = ShadowstepImage("/path/to/image.png", app, timeout=1.0)
        img2 = ShadowstepImage("/path/to/image.png", app, timeout=5.0)
        img3 = ShadowstepImage("/path/to/image.png", app, timeout=30.0)

        assert img1.timeout == 1.0  # noqa: S101
        assert img2.timeout == 5.0  # noqa: S101
        assert img3.timeout == 30.0  # noqa: S101

    def test_base_reference_is_maintained(self, app: Shadowstep):
        """Test that reference to base Shadowstep instance is maintained.

        Steps:
        1. Create ShadowstepImage instance.
        2. Verify _base references the same app instance.
        """
        img = ShadowstepImage("/path/to/image.png", app)

        assert img._base is app  # noqa: S101
        assert id(img._base) == id(app)  # noqa: S101

    def test_multiple_instances_can_be_created(self, app: Shadowstep):
        """Test that multiple independent instances can be created.

        Steps:
        1. Create multiple ShadowstepImage instances.
        2. Verify they are independent.
        3. Verify each has correct attributes.
        """
        img1 = ShadowstepImage("/path/to/image1.png", app, threshold=0.6)
        img2 = ShadowstepImage("/path/to/image2.png", app, threshold=0.7)
        img3 = ShadowstepImage("/path/to/image3.png", app, threshold=0.8)

        # Verify independence
        assert img1 is not img2  # noqa: S101
        assert img2 is not img3  # noqa: S101
        assert img1 is not img3  # noqa: S101

        # Verify attributes
        assert img1._image == "/path/to/image1.png"  # noqa: S101
        assert img2._image == "/path/to/image2.png"  # noqa: S101
        assert img3._image == "/path/to/image3.png"  # noqa: S101

        assert img1.threshold == 0.6  # noqa: S101
        assert img2.threshold == 0.7  # noqa: S101
        assert img3.threshold == 0.8  # noqa: S101
