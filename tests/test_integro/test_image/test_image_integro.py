# ruff: noqa
# pyright: ignore
"""Integration tests for ShadowstepImage class. Do not run in CI"""

from typing import Any

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepImageNotImplementedError
from shadowstep.image.image import ShadowstepImage
from shadowstep.shadowstep import Shadowstep

ELEMENT_1_IMG_PATH = "tests/test_integro/_test_data/element.png"
ELEMENT_2_IMG_PATH = "tests/test_integro/_test_data/element2.png"


class TestShadowstepImage:
    """Test class for ShadowstepImage functionality."""

    def test_initialization_with_string_image(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        image_path = ELEMENT_1_IMG_PATH
        img = ShadowstepImage(image_path, threshold=0.8, timeout=10.0)
        assert img is not None  # noqa: S101
        assert isinstance(img, ShadowstepImage)  # noqa: S101
        assert img._image == image_path  # noqa: S101
        assert img.shadowstep is app  # noqa: S101
        assert img.threshold == 0.8  # noqa: S101
        assert img.timeout == 10.0  # noqa: S101
        assert img._coords is None  # noqa: S101
        assert img._center is None  # noqa: S101

    def test_initialization_with_bytes_image(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        image_bytes = b"fake_image_data"
        img = ShadowstepImage(image_bytes)
        assert img is not None  # noqa: S101
        assert isinstance(img, ShadowstepImage)  # noqa: S101
        assert img._image == image_bytes  # noqa: S101
        assert img.shadowstep is app  # noqa: S101

    def test_initialization_with_default_values(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        assert img.threshold == 0.7  # noqa: S101
        assert img.timeout == 5.0  # noqa: S101

    def test_tap(self, app: Shadowstep, android_settings_open_close: Any):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.tap()

    def test_tap_with_duration(self, app: Shadowstep, android_settings_open_close: Any):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.tap(duration=500)

    def test_drag_with_tuple(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.drag(to=(100, 200))

    def test_drag_with_image(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img1 = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img2 = ShadowstepImage(ELEMENT_2_IMG_PATH)
        img1.drag(to=img2)

    def test_zoom(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.zoom()

    def test_zoom_with_params(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.zoom(percent=2.0, steps=20)

    def test_unzoom(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.unzoom()

    def test_unzoom_with_params(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.unzoom(percent=0.3, steps=15)

    def test_wait(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.wait()

    def test_wait_not(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.wait_not()

    def test_is_visible(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.is_visible()

    def test_coordinates_property(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        _ = img.coordinates

    def test_center_property(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        _ = img.center

    def test_scroll_down(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.scroll_down()

    def test_scroll_down_with_params(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.scroll_down(from_percent=0.7, to_percent=0.2, max_attempts=5, step_delay=1.0)

    def test_scroll_up(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.scroll_up()

    def test_scroll_up_with_params(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.scroll_up(max_attempts=15, step_delay=0.8)

    def test_scroll_left(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.scroll_left()

    def test_scroll_left_with_params(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.scroll_left(max_attempts=8, step_delay=0.6)

    def test_scroll_right(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.scroll_right()

    def test_scroll_right_with_params(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.scroll_right(max_attempts=12, step_delay=0.4)

    def test_scroll_to(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.scroll_to()

    def test_scroll_to_with_params(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.scroll_to(max_attempts=20, step_delay=1.5)

    def test_is_contains(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.is_contains(ELEMENT_2_IMG_PATH)

    def test_is_contains_with_bytes(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.is_contains(b"image_bytes")

    def test_should_property(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        with pytest.raises(ShadowstepImageNotImplementedError):
            _ = img.should

    def test_to_ndarray(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.to_ndarray(ELEMENT_2_IMG_PATH)

    def test_to_ndarray_with_bytes(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.to_ndarray(b"image_bytes")

    def test_multi_scale_matching(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        img.multi_scale_matching(None, None)  # type: ignore

    def test_logger_is_initialized(self, app: Shadowstep, android_settings_open_close: Any):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)

        assert hasattr(img, "logger")  # noqa: S101
        assert img.logger is not None  # noqa: S101

    def test_cached_coords_and_center_are_none_initially(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)
        assert img._coords is None  # noqa: S101
        assert img._center is None  # noqa: S101

    def test_threshold_can_be_set_to_different_values(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img1 = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.1)
        img2 = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.5)
        img3 = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.9)
        img4 = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=1.0)

        assert img1.threshold == 0.1  # noqa: S101
        assert img2.threshold == 0.5  # noqa: S101
        assert img3.threshold == 0.9  # noqa: S101
        assert img4.threshold == 1.0  # noqa: S101

    def test_timeout_can_be_set_to_different_values(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img1 = ShadowstepImage(ELEMENT_1_IMG_PATH, timeout=1.0)
        img2 = ShadowstepImage(ELEMENT_1_IMG_PATH, timeout=5.0)
        img3 = ShadowstepImage(ELEMENT_1_IMG_PATH, timeout=30.0)

        assert img1.timeout == 1.0  # noqa: S101
        assert img2.timeout == 5.0  # noqa: S101
        assert img3.timeout == 30.0  # noqa: S101

    def test_base_reference_is_maintained(self, app: Shadowstep, android_settings_open_close: Any):
        img = ShadowstepImage(ELEMENT_1_IMG_PATH)

        assert img.shadowstep is app  # noqa: S101
        assert id(img.shadowstep) == id(app)  # noqa: S101

    def test_multiple_instances_can_be_created(
        self, app: Shadowstep, android_settings_open_close: Any
    ):
        img1 = ShadowstepImage(ELEMENT_1_IMG_PATH, threshold=0.6)
        img2 = ShadowstepImage(ELEMENT_2_IMG_PATH, threshold=0.7)
        img3 = ShadowstepImage("/path/to/image3.png", threshold=0.8)

        # Verify independence
        assert img1 is not img2  # noqa: S101
        assert img2 is not img3  # noqa: S101
        assert img1 is not img3  # noqa: S101

        # Verify attributes
        assert img1._image == ELEMENT_1_IMG_PATH  # noqa: S101
        assert img2._image == ELEMENT_2_IMG_PATH  # noqa: S101
        assert img3._image == "/path/to/image3.png"  # noqa: S101

        assert img1.threshold == 0.6  # noqa: S101
        assert img2.threshold == 0.7  # noqa: S101
        assert img3.threshold == 0.8  # noqa: S101
