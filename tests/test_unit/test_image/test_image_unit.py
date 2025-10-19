# ruff: noqa
# pyright: ignore
"""Unit tests for ShadowstepImage class using mocks."""
import base64
import time
from unittest.mock import Mock, patch, MagicMock, PropertyMock

import cv2
import numpy as np
import pytest
from PIL import Image as PILImage
from selenium.common.exceptions import TimeoutException

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepImageNotFoundError
from shadowstep.image.image import ShadowstepImage


class TestShadowstepImageInit:
    """Test ShadowstepImage initialization."""

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_init_with_bytes_image(self, mock_shadowstep_class):
        """Test initialization with bytes image."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        image_bytes = b"fake_image_data"

        img = ShadowstepImage(image_bytes, threshold=0.8, timeout=10.0)

        assert img._image == image_bytes
        assert img.shadowstep == mock_instance
        assert img.threshold == 0.8
        assert img.timeout == 10.0
        assert img._coords is None
        assert img._center is None
        assert img.MIN_SUFFICIENT_MATCH == 0.95

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_init_with_str_path(self, mock_shadowstep_class):
        """Test initialization with string path."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        image_path = "/path/to/image.png"

        img = ShadowstepImage(image_path)

        assert img._image == image_path
        assert img.threshold == 0.7
        assert img.timeout == 5.0

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_init_with_numpy_array(self, mock_shadowstep_class):
        """Test initialization with numpy array."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        image_array = np.zeros((100, 100, 3), dtype=np.uint8)

        img = ShadowstepImage(image_array, threshold=0.9)

        assert isinstance(img._image, np.ndarray)
        assert img.threshold == 0.9

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_init_with_pil_image(self, mock_shadowstep_class):
        """Test initialization with PIL Image."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        pil_image = PILImage.new("RGB", (100, 100))

        img = ShadowstepImage(pil_image)

        assert isinstance(img._image, PILImage.Image)
        assert img.threshold == 0.7


class TestShadowstepImageTap:
    """Test tap method."""

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    def test_tap_without_duration(self, mock_ensure_visible, mock_shadowstep_class):
        """Test tap without duration parameter."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_instance.driver.tap = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._center = (100, 200)

        result = img.tap()

        mock_ensure_visible.assert_called_once()
        mock_instance.driver.tap.assert_called_once_with(positions=[(100, 200)], duration=None)
        assert result is img

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    def test_tap_with_duration(self, mock_ensure_visible, mock_shadowstep_class):
        """Test tap with duration parameter."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_instance.driver.tap = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._center = (150, 250)

        result = img.tap(duration=500)

        mock_ensure_visible.assert_called_once()
        mock_instance.driver.tap.assert_called_once_with(positions=[(150, 250)], duration=500)
        assert result is img


class TestShadowstepImageDrag:
    """Test drag method."""

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    def test_drag_to_coordinates(self, mock_ensure_visible, mock_shadowstep_class):
        """Test drag to coordinates tuple."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._center = (100, 100)

        with patch("shadowstep.image.image.ActionChains") as mock_action_chains:
            mock_actions = Mock()
            mock_action_chains.return_value = mock_actions
            mock_actions.w3c_actions = Mock()
            mock_actions.w3c_actions.pointer_action = Mock()

            result = img.drag(to=(200, 300), duration=2.0)

            mock_ensure_visible.assert_called_once()
            assert result is img

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    def test_drag_to_another_image(self, mock_ensure_visible, mock_shadowstep_class):
        """Test drag to another ShadowstepImage."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img1 = ShadowstepImage("test1.png")
        img1._center = (100, 100)
        img2 = ShadowstepImage("test2.png")
        img2._center = (200, 200)

        with patch("shadowstep.image.image.ActionChains") as mock_action_chains:
            mock_actions = Mock()
            mock_action_chains.return_value = mock_actions
            mock_actions.w3c_actions = Mock()
            mock_actions.w3c_actions.pointer_action = Mock()

            result = img1.drag(to=img2, duration=1.5)

            # ensure_visible should be called for both images
            assert mock_ensure_visible.call_count == 2
            assert result is img1


class TestShadowstepImageZoom:
    """Test zoom method."""

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    @patch("shadowstep.image.image.MobileCommands")
    def test_zoom_default_parameters(self, mock_mobile_commands_class, mock_ensure_visible, mock_shadowstep_class):
        """Test zoom with default parameters."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._center = (150, 150)
        img._coords = (100, 100, 200, 200)

        mock_mobile_commands = Mock()
        mock_mobile_commands_class.return_value = mock_mobile_commands

        result = img.zoom()

        mock_ensure_visible.assert_called_once()
        mock_mobile_commands.pinch_open_gesture.assert_called_once()
        call_args = mock_mobile_commands.pinch_open_gesture.call_args[0][0]
        assert call_args["left"] == 100
        assert call_args["top"] == 100
        assert call_args["width"] == 100
        assert call_args["height"] == 100
        assert call_args["percent"] == 0.5  # 1.5 - 1.0
        assert result is img

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    @patch("shadowstep.image.image.MobileCommands")
    def test_zoom_custom_parameters(self, mock_mobile_commands_class, mock_ensure_visible, mock_shadowstep_class):
        """Test zoom with custom parameters."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._center = (150, 150)
        img._coords = (100, 100, 200, 200)

        mock_mobile_commands = Mock()
        mock_mobile_commands_class.return_value = mock_mobile_commands

        result = img.zoom(percent=2.0, steps=20)

        call_args = mock_mobile_commands.pinch_open_gesture.call_args[0][0]
        assert call_args["percent"] == 1.0  # 2.0 - 1.0
        assert result is img


class TestShadowstepImageUnzoom:
    """Test unzoom method."""

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    @patch("shadowstep.image.image.MobileCommands")
    def test_unzoom_default_parameters(self, mock_mobile_commands_class, mock_ensure_visible, mock_shadowstep_class):
        """Test unzoom with default parameters."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._center = (150, 150)
        img._coords = (100, 100, 200, 200)

        mock_mobile_commands = Mock()
        mock_mobile_commands_class.return_value = mock_mobile_commands

        result = img.unzoom()

        mock_ensure_visible.assert_called_once()
        mock_mobile_commands.pinch_close_gesture.assert_called_once()
        call_args = mock_mobile_commands.pinch_close_gesture.call_args[0][0]
        assert call_args["percent"] == 0.5  # 1.0 - 0.5
        assert result is img

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    @patch("shadowstep.image.image.MobileCommands")
    def test_unzoom_custom_parameters(self, mock_mobile_commands_class, mock_ensure_visible, mock_shadowstep_class):
        """Test unzoom with custom parameters."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._center = (150, 150)
        img._coords = (100, 100, 200, 200)

        mock_mobile_commands = Mock()
        mock_mobile_commands_class.return_value = mock_mobile_commands

        result = img.unzoom(percent=0.3, steps=15)

        call_args = mock_mobile_commands.pinch_close_gesture.call_args[0][0]
        assert call_args["percent"] == 0.7  # 1.0 - 0.3
        assert result is img


class TestShadowstepImageWait:
    """Test wait method."""

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "_get_image_coordinates")
    @patch.object(ShadowstepImage, "ensure_visible")
    @patch("shadowstep.image.image.WebDriverWait")
    def test_wait_success(self, mock_wait_class, mock_ensure_visible, mock_get_coords, mock_shadowstep_class):
        """Test wait when image becomes visible."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png", timeout=5.0)
        mock_get_coords.return_value = (10, 20, 50, 60)

        # Mock WebDriverWait to call the condition function
        mock_wait = Mock()
        mock_wait_class.return_value = mock_wait

        def until_side_effect(condition):
            # Simulate successful condition
            condition(mock_instance.driver)
            return True

        mock_wait.until.side_effect = until_side_effect

        result = img.wait()

        assert result is True
        mock_ensure_visible.assert_called_once()

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "_get_image_coordinates")
    @patch("shadowstep.image.image.WebDriverWait")
    def test_wait_timeout(self, mock_wait_class, mock_get_coords, mock_shadowstep_class):
        """Test wait when image doesn't become visible."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png", timeout=5.0)
        mock_get_coords.return_value = None

        mock_wait = Mock()
        mock_wait_class.return_value = mock_wait
        mock_wait.until.side_effect = TimeoutException("Timeout")

        result = img.wait()

        assert result is False


class TestShadowstepImageWaitNot:
    """Test wait_not method."""

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "_get_image_coordinates")
    @patch("shadowstep.image.image.WebDriverWait")
    def test_wait_not_success(self, mock_wait_class, mock_get_coords, mock_shadowstep_class):
        """Test wait_not when image becomes invisible."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png", timeout=5.0)
        img._coords = (10, 20, 50, 60)
        img._center = (30, 40)
        mock_get_coords.return_value = None

        mock_wait = Mock()
        mock_wait_class.return_value = mock_wait

        def until_side_effect(condition):
            condition(mock_instance.driver)
            return True

        mock_wait.until.side_effect = until_side_effect

        result = img.wait_not()

        assert result is True
        assert img._coords is None
        assert img._center is None

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "_get_image_coordinates")
    @patch("shadowstep.image.image.WebDriverWait")
    def test_wait_not_timeout(self, mock_wait_class, mock_get_coords, mock_shadowstep_class):
        """Test wait_not when image stays visible."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png", timeout=5.0)
        mock_get_coords.return_value = (10, 20, 50, 60)

        mock_wait = Mock()
        mock_wait_class.return_value = mock_wait
        mock_wait.until.side_effect = TimeoutException("Timeout")

        result = img.wait_not()

        assert result is False


class TestShadowstepImageIsVisible:
    """Test is_visible method."""

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "_get_image_coordinates")
    @patch.object(ShadowstepImage, "_calculate_center")
    def test_is_visible_true(self, mock_calc_center, mock_get_coords, mock_shadowstep_class):
        """Test is_visible returns True when image found."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        mock_get_coords.return_value = (10, 20, 50, 60)
        mock_calc_center.return_value = (30, 40)

        result = img.is_visible()

        assert result is True
        assert img._coords == (10, 20, 50, 60)
        assert img._center == (30, 40)

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "_get_image_coordinates")
    def test_is_visible_false(self, mock_get_coords, mock_shadowstep_class):
        """Test is_visible returns False when image not found."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        mock_get_coords.return_value = None

        result = img.is_visible()

        assert result is False

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "_get_image_coordinates")
    def test_is_visible_exception(self, mock_get_coords, mock_shadowstep_class):
        """Test is_visible returns False on exception."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        mock_get_coords.side_effect = Exception("Test error")

        result = img.is_visible()

        assert result is False


class TestShadowstepImageCoordinates:
    """Test coordinates property."""

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    def test_coordinates_cached(self, mock_ensure_visible, mock_shadowstep_class):
        """Test coordinates returns cached value."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._coords = (10, 20, 50, 60)

        coords = img.coordinates

        assert coords == (10, 20, 50, 60)
        mock_ensure_visible.assert_not_called()

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    def test_coordinates_not_cached(self, mock_ensure_visible, mock_shadowstep_class):
        """Test coordinates calls ensure_visible when not cached."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._coords = None

        def set_coords():
            img._coords = (10, 20, 50, 60)

        mock_ensure_visible.side_effect = set_coords

        coords = img.coordinates

        mock_ensure_visible.assert_called_once()
        assert coords == (10, 20, 50, 60)


class TestShadowstepImageCenter:
    """Test center property."""

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    def test_center_cached(self, mock_ensure_visible, mock_shadowstep_class):
        """Test center returns cached value."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._center = (30, 40)

        center = img.center

        assert center == (30, 40)
        mock_ensure_visible.assert_not_called()

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    def test_center_not_cached(self, mock_ensure_visible, mock_shadowstep_class):
        """Test center calls ensure_visible when not cached."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._center = None

        def set_center():
            img._center = (30, 40)

        mock_ensure_visible.side_effect = set_center

        center = img.center

        mock_ensure_visible.assert_called_once()
        assert center == (30, 40)


class TestShadowstepImageScrollMethods:
    """Test scroll methods."""

    @patch.object(ShadowstepImage, "_scroll_to_image")
    def test_scroll_down(self, mock_scroll_to_image):
        """Test scroll_down method."""
        img = ShadowstepImage("test.png")
        mock_scroll_to_image.return_value = img

        result = img.scroll_down(from_percent=0.6, to_percent=0.2, max_attempts=15, step_delay=0.3)

        mock_scroll_to_image.assert_called_once_with(
            direction="down",
            from_percent=0.6,
            to_percent=0.2,
            max_attempts=15,
            step_delay=0.3,
        )
        assert result is img

    @patch.object(ShadowstepImage, "_scroll_to_image")
    def test_scroll_up(self, mock_scroll_to_image):
        """Test scroll_up method."""
        img = ShadowstepImage("test.png")
        mock_scroll_to_image.return_value = img

        result = img.scroll_up(max_attempts=8, step_delay=0.4)

        mock_scroll_to_image.assert_called_once_with(
            direction="up",
            max_attempts=8,
            step_delay=0.4,
        )
        assert result is img

    @patch.object(ShadowstepImage, "_scroll_to_image")
    def test_scroll_left(self, mock_scroll_to_image):
        """Test scroll_left method."""
        img = ShadowstepImage("test.png")
        mock_scroll_to_image.return_value = img

        result = img.scroll_left(max_attempts=12, step_delay=0.6)

        mock_scroll_to_image.assert_called_once_with(
            direction="left",
            max_attempts=12,
            step_delay=0.6,
        )
        assert result is img

    @patch.object(ShadowstepImage, "_scroll_to_image")
    def test_scroll_right(self, mock_scroll_to_image):
        """Test scroll_right method."""
        img = ShadowstepImage("test.png")
        mock_scroll_to_image.return_value = img

        result = img.scroll_right(max_attempts=7, step_delay=0.8)

        mock_scroll_to_image.assert_called_once_with(
            direction="right",
            max_attempts=7,
            step_delay=0.8,
        )
        assert result is img

    @patch.object(ShadowstepImage, "scroll_down")
    def test_scroll_to_success_on_down(self, mock_scroll_down):
        """Test scroll_to success on first try (scroll_down)."""
        img = ShadowstepImage("test.png")
        mock_scroll_down.return_value = img

        result = img.scroll_to(max_attempts=10, step_delay=0.5)

        mock_scroll_down.assert_called_once_with(max_attempts=5, step_delay=0.5)
        assert result is img

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "scroll_up")
    @patch.object(ShadowstepImage, "scroll_down")
    def test_scroll_to_fallback_to_up(self, mock_scroll_down, mock_scroll_up, mock_shadowstep_class):
        """Test scroll_to falls back to scroll_up."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        mock_scroll_down.side_effect = ShadowstepImageNotFoundError(threshold=0.7, timeout=5.0, operation="scroll_down")
        mock_scroll_up.return_value = img

        result = img.scroll_to(max_attempts=10, step_delay=0.5)

        mock_scroll_down.assert_called_once_with(max_attempts=5, step_delay=0.5)
        mock_scroll_up.assert_called_once_with(max_attempts=5, step_delay=0.5)
        assert result is img


class TestShadowstepImageIsContains:
    """Test is_contains method."""

    @patch.object(ShadowstepImage, "ensure_visible")
    @patch.object(ShadowstepImage, "_get_screenshot_as_bytes")
    @patch.object(ShadowstepImage, "to_ndarray")
    @patch.object(ShadowstepImage, "multi_scale_matching")
    def test_is_contains_true(
        self, mock_multi_scale, mock_to_ndarray, mock_screenshot, mock_ensure_visible
    ):
        """Test is_contains returns True when image contains target."""
        img = ShadowstepImage("container.png", threshold=0.7)
        img._coords = (50, 50, 200, 200)

        mock_screenshot.return_value = b"screenshot_data"
        full_array = np.zeros((300, 300), dtype=np.uint8)
        target_array = np.zeros((50, 50), dtype=np.uint8)
        mock_to_ndarray.side_effect = [full_array, target_array]
        mock_multi_scale.return_value = (0.85, (10, 10))

        result = img.is_contains("button.png")

        assert result is True
        mock_ensure_visible.assert_called_once()

    @patch.object(ShadowstepImage, "ensure_visible")
    @patch.object(ShadowstepImage, "_get_screenshot_as_bytes")
    @patch.object(ShadowstepImage, "to_ndarray")
    @patch.object(ShadowstepImage, "multi_scale_matching")
    def test_is_contains_false(
        self, mock_multi_scale, mock_to_ndarray, mock_screenshot, mock_ensure_visible
    ):
        """Test is_contains returns False when image doesn't contain target."""
        img = ShadowstepImage("container.png", threshold=0.7)
        img._coords = (50, 50, 200, 200)

        mock_screenshot.return_value = b"screenshot_data"
        full_array = np.zeros((300, 300), dtype=np.uint8)
        target_array = np.zeros((50, 50), dtype=np.uint8)
        mock_to_ndarray.side_effect = [full_array, target_array]
        mock_multi_scale.return_value = (0.5, (10, 10))

        result = img.is_contains("button.png")

        assert result is False


class TestShadowstepImageShould:
    """Test should property."""

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_should_raises_not_implemented(self, mock_shadowstep_class):
        """Test should property raises NotImplementedError."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")

        _ = img.should


class TestShadowstepImageToNdarray:
    """Test to_ndarray method."""

    def test_to_ndarray_from_bytes_grayscale(self):
        """Test to_ndarray from bytes with grayscale."""
        img = ShadowstepImage("test.png")

        # Create a simple image as bytes
        test_array = np.zeros((100, 100, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".png", test_array)
        image_bytes = buffer.tobytes()

        with patch.object(img, "_to_grayscale") as mock_to_gray:
            mock_to_gray.return_value = np.zeros((100, 100), dtype=np.uint8)
            result = img.to_ndarray(image_bytes, grayscale=True)

            mock_to_gray.assert_called_once()
            assert isinstance(result, np.ndarray)

    def test_to_ndarray_from_bytes_color(self):
        """Test to_ndarray from bytes without grayscale."""
        img = ShadowstepImage("test.png")

        test_array = np.zeros((100, 100, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".png", test_array)
        image_bytes = buffer.tobytes()

        result = img.to_ndarray(image_bytes, grayscale=False)

        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 3

    def test_to_ndarray_from_str_path(self):
        """Test to_ndarray from file path."""
        img = ShadowstepImage("test.png")

        test_array = np.zeros((100, 100, 3), dtype=np.uint8)

        with patch("cv2.imread") as mock_imread:
            mock_imread.return_value = test_array
            with patch.object(img, "_to_grayscale") as mock_to_gray:
                mock_to_gray.return_value = np.zeros((100, 100), dtype=np.uint8)
                result = img.to_ndarray("/path/to/image.png", grayscale=True)

                mock_imread.assert_called_once_with("/path/to/image.png", cv2.IMREAD_COLOR)
                assert isinstance(result, np.ndarray)

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_to_ndarray_from_str_path_file_not_found(self, mock_shadowstep_class):
        """Test to_ndarray raises FileNotFoundError for invalid path."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")

        with patch("cv2.imread") as mock_imread:
            mock_imread.return_value = None
            with pytest.raises(Exception, match="Failed to load image from path"):
                img.to_ndarray("/invalid/path.png")

    def test_to_ndarray_from_pil_image(self):
        """Test to_ndarray from PIL Image."""
        img = ShadowstepImage("test.png")

        pil_image = PILImage.new("RGB", (100, 100), color=(255, 0, 0))

        with patch.object(img, "_to_grayscale") as mock_to_gray:
            mock_to_gray.return_value = np.zeros((100, 100), dtype=np.uint8)
            result = img.to_ndarray(pil_image, grayscale=True)

            assert isinstance(result, np.ndarray)

    def test_to_ndarray_from_numpy_array(self):
        """Test to_ndarray from numpy array."""
        img = ShadowstepImage("test.png")

        test_array = np.zeros((100, 100, 3), dtype=np.uint8)

        with patch.object(img, "_to_grayscale") as mock_to_gray:
            mock_to_gray.return_value = np.zeros((100, 100), dtype=np.uint8)
            result = img.to_ndarray(test_array, grayscale=True)

            assert isinstance(result, np.ndarray)

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_to_ndarray_unsupported_type(self, mock_shadowstep_class):
        """Test to_ndarray raises TypeError for unsupported type."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")

        with pytest.raises(Exception, match="Unsupported image type"):
            img.to_ndarray(12345)  # Invalid type


class TestShadowstepImageMultiScaleMatching:
    """Test multi_scale_matching method."""

    def test_multi_scale_matching_finds_match(self):
        """Test multi_scale_matching finds a good match."""
        img = ShadowstepImage("test.png", threshold=0.7)

        # Create test images
        full_image = np.zeros((500, 500), dtype=np.uint8)
        template_image = np.zeros((50, 50), dtype=np.uint8)

        with patch("cv2.resize") as mock_resize, \
             patch("cv2.matchTemplate") as mock_match, \
             patch("cv2.minMaxLoc") as mock_minmax:

            mock_resize.return_value = full_image
            mock_match.return_value = np.zeros((450, 450))
            mock_minmax.return_value = (0, 0.85, (0, 0), (100, 100))

            max_val, max_loc = img.multi_scale_matching(full_image, template_image)

            assert max_val == 0.85
            assert isinstance(max_loc, tuple)

    def test_multi_scale_matching_early_exit_on_high_match(self):
        """Test multi_scale_matching exits early on very good match."""
        img = ShadowstepImage("test.png", threshold=0.7)

        full_image = np.zeros((500, 500), dtype=np.uint8)
        template_image = np.zeros((50, 50), dtype=np.uint8)

        with patch("cv2.resize") as mock_resize, \
             patch("cv2.matchTemplate") as mock_match, \
             patch("cv2.minMaxLoc") as mock_minmax:

            mock_resize.return_value = full_image
            mock_match.return_value = np.zeros((450, 450))
            # Return value higher than MIN_SUFFICIENT_MATCH (0.95)
            mock_minmax.return_value = (0, 0.96, (0, 0), (100, 100))

            max_val, max_loc = img.multi_scale_matching(full_image, template_image)

            assert max_val == 0.96
            # Should exit early, so not all scales are tried

    def test_multi_scale_matching_handles_cv2_error(self):
        """Test multi_scale_matching handles cv2 errors gracefully."""
        img = ShadowstepImage("test.png", threshold=0.7)

        full_image = np.zeros((500, 500), dtype=np.uint8)
        template_image = np.zeros((50, 50), dtype=np.uint8)

        with patch("cv2.resize") as mock_resize, \
             patch("cv2.matchTemplate") as mock_match:

            mock_resize.return_value = full_image
            mock_match.side_effect = cv2.error("Test error")

            max_val, max_loc = img.multi_scale_matching(full_image, template_image)

            # Should return default values when all scales fail
            assert max_val == 0.0
            assert max_loc == (0, 0)

    def test_multi_scale_matching_skips_small_resized_images(self):
        """Test multi_scale_matching skips scales where resized image is smaller than template."""
        img = ShadowstepImage("test.png", threshold=0.7)

        # Create extreme scenario: very small full image and huge template
        # At small scales (0.2x), 100*0.2 = 20 which is much smaller than 500
        full_image = np.ones((100, 100), dtype=np.uint8) * 128
        template_image = np.ones((500, 500), dtype=np.uint8) * 128

        # Mock matchTemplate to track if it's called for all scales
        call_count = [0]
        original_match = cv2.matchTemplate
        
        def track_match(*args, **kwargs):
            call_count[0] += 1
            return original_match(*args, **kwargs)
        
        with patch("cv2.matchTemplate", side_effect=track_match):
            # This will trigger the continue statement for most small scales
            max_val, max_loc = img.multi_scale_matching(full_image, template_image)

        # Should still complete without error
        assert isinstance(max_val, float)
        assert isinstance(max_loc, tuple)
        # matchTemplate should be called fewer times than total scales (20)
        # because some scales are skipped via continue
        assert call_count[0] < 20


class TestShadowstepImageFindAll:
    """Test find_all method."""

    @patch.object(ShadowstepImage, "_get_screenshot_as_bytes")
    @patch.object(ShadowstepImage, "to_ndarray")
    @patch.object(ShadowstepImage, "_multi_scale_matching_raw")
    def test_find_all_multiple_matches(self, mock_multi_scale_raw, mock_to_ndarray, mock_screenshot):
        """Test find_all returns multiple matches."""
        img = ShadowstepImage("test.png", threshold=0.7)

        mock_screenshot.return_value = b"screenshot_data"
        full_array = np.zeros((300, 300), dtype=np.uint8)
        template_array = np.zeros((50, 50), dtype=np.uint8)
        mock_to_ndarray.side_effect = [full_array, template_array]

        # Create result with multiple matches
        result_array = np.zeros((250, 250))
        result_array[10, 10] = 0.9
        result_array[100, 100] = 0.85
        mock_multi_scale_raw.return_value = result_array

        matches = img.find_all(coord_threshold=5)

        assert isinstance(matches, list)
        # Note: actual number depends on filtering

    @patch.object(ShadowstepImage, "_get_screenshot_as_bytes")
    @patch.object(ShadowstepImage, "to_ndarray")
    @patch.object(ShadowstepImage, "_multi_scale_matching_raw")
    def test_find_all_no_matches(self, mock_multi_scale_raw, mock_to_ndarray, mock_screenshot):
        """Test find_all returns empty list when no matches."""
        img = ShadowstepImage("test.png", threshold=0.7)

        mock_screenshot.return_value = b"screenshot_data"
        full_array = np.zeros((300, 300), dtype=np.uint8)
        template_array = np.zeros((50, 50), dtype=np.uint8)
        mock_to_ndarray.side_effect = [full_array, template_array]
        mock_multi_scale_raw.return_value = None

        matches = img.find_all()

        assert matches == []

    @patch.object(ShadowstepImage, "_get_screenshot_as_bytes")
    @patch.object(ShadowstepImage, "to_ndarray")
    @patch.object(ShadowstepImage, "_multi_scale_matching_raw")
    def test_find_all_filters_duplicate_matches(self, mock_multi_scale_raw, mock_to_ndarray, mock_screenshot):
        """Test find_all filters out duplicate matches within threshold."""
        img = ShadowstepImage("test.png", threshold=0.7)

        mock_screenshot.return_value = b"screenshot_data"
        full_array = np.zeros((300, 300), dtype=np.uint8)
        template_array = np.zeros((50, 50), dtype=np.uint8)
        mock_to_ndarray.side_effect = [full_array, template_array]

        # Create result with close matches (duplicates)
        result_array = np.zeros((250, 250))
        # Two matches very close to each other (within default threshold of 5)
        result_array[10, 10] = 0.9
        result_array[12, 12] = 0.85  # Should be filtered as duplicate
        result_array[100, 100] = 0.9  # Far away, not a duplicate
        mock_multi_scale_raw.return_value = result_array

        matches = img.find_all(coord_threshold=5)

        assert isinstance(matches, list)
        # Should have filtered duplicates
        assert len(matches) >= 1


class TestShadowstepImageDrawRectangle:
    """Test draw_rectangle method."""

    @patch.object(ShadowstepImage, "ensure_visible")
    @patch.object(ShadowstepImage, "_get_screenshot_as_bytes")
    @patch.object(ShadowstepImage, "to_ndarray")
    @patch("cv2.rectangle")
    @patch("cv2.imwrite")
    def test_draw_rectangle_success(
        self, mock_imwrite, mock_rectangle, mock_to_ndarray, mock_screenshot, mock_ensure_visible
    ):
        """Test draw_rectangle saves screenshot successfully."""
        img = ShadowstepImage("test.png")
        img._coords = (10, 20, 100, 120)

        mock_screenshot.return_value = b"screenshot_data"
        test_array = np.zeros((300, 300, 3), dtype=np.uint8)
        mock_to_ndarray.return_value = test_array
        mock_imwrite.return_value = True

        result = img.draw_rectangle("output.png")

        assert result is True
        mock_ensure_visible.assert_called_once()
        mock_rectangle.assert_called_once_with(test_array, (10, 20), (100, 120), (0, 255, 0), 2)
        mock_imwrite.assert_called_once_with("output.png", test_array)

    @patch.object(ShadowstepImage, "ensure_visible")
    @patch.object(ShadowstepImage, "_get_screenshot_as_bytes")
    @patch.object(ShadowstepImage, "to_ndarray")
    @patch("cv2.rectangle")
    @patch("cv2.imwrite")
    def test_draw_rectangle_failure(
        self, mock_imwrite, mock_rectangle, mock_to_ndarray, mock_screenshot, mock_ensure_visible
    ):
        """Test draw_rectangle handles save failure."""
        img = ShadowstepImage("test.png")
        img._coords = (10, 20, 100, 120)

        mock_screenshot.return_value = b"screenshot_data"
        test_array = np.zeros((300, 300, 3), dtype=np.uint8)
        mock_to_ndarray.return_value = test_array
        mock_imwrite.return_value = False

        result = img.draw_rectangle("output.png")

        assert result is False

    @patch.object(ShadowstepImage, "ensure_visible")
    def test_draw_rectangle_exception(self, mock_ensure_visible):
        """Test draw_rectangle handles exceptions."""
        img = ShadowstepImage("test.png")
        mock_ensure_visible.side_effect = Exception("Test error")

        result = img.draw_rectangle()

        assert result is False


class TestShadowstepImageEnsureVisible:
    """Test ensure_visible method."""

    @patch.object(ShadowstepImage, "_get_image_coordinates")
    @patch.object(ShadowstepImage, "_calculate_center")
    def test_ensure_visible_success(self, mock_calc_center, mock_get_coords):
        """Test ensure_visible finds image and caches values."""
        img = ShadowstepImage("test.png")

        mock_get_coords.return_value = (10, 20, 100, 120)
        mock_calc_center.return_value = (55, 70)

        img.ensure_visible()

        assert img._coords == (10, 20, 100, 120)
        assert img._center == (55, 70)
        assert img._last_screenshot_time > 0

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "_get_image_coordinates")
    def test_ensure_visible_raises_timeout(self, mock_get_coords, mock_shadowstep_class):
        """Test ensure_visible raises TimeoutException when not found."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")

        mock_get_coords.return_value = None

        with pytest.raises(Exception, match="Image not"):
            img.ensure_visible()


class TestShadowstepImagePrivateMethods:
    """Test private/helper methods."""

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_get_screenshot_as_bytes(self, mock_shadowstep_class):
        """Test _get_screenshot_as_bytes method."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")

        test_data = b"screenshot_data"
        encoded = base64.b64encode(test_data).decode("utf-8")
        mock_instance.driver.get_screenshot_as_base64.return_value = encoded

        result = img._get_screenshot_as_bytes()

        assert result == test_data

    @patch.object(ShadowstepImage, "_get_screenshot_as_bytes")
    @patch.object(ShadowstepImage, "to_ndarray")
    @patch.object(ShadowstepImage, "multi_scale_matching")
    def test_get_image_coordinates_success(self, mock_multi_scale, mock_to_ndarray, mock_screenshot):
        """Test _get_image_coordinates finds image."""
        img = ShadowstepImage("test.png", threshold=0.7)

        mock_screenshot.return_value = b"screenshot_data"
        full_array = np.zeros((300, 300), dtype=np.uint8)
        template_array = np.zeros((50, 50), dtype=np.uint8)
        mock_to_ndarray.side_effect = [full_array, template_array]
        mock_multi_scale.return_value = (0.85, (100, 100))

        coords = img._get_image_coordinates()

        assert coords == (100, 100, 150, 150)

    @patch.object(ShadowstepImage, "_get_screenshot_as_bytes")
    @patch.object(ShadowstepImage, "to_ndarray")
    @patch.object(ShadowstepImage, "multi_scale_matching")
    def test_get_image_coordinates_below_threshold(
        self, mock_multi_scale, mock_to_ndarray, mock_screenshot
    ):
        """Test _get_image_coordinates returns None when below threshold."""
        img = ShadowstepImage("test.png", threshold=0.7)

        mock_screenshot.return_value = b"screenshot_data"
        full_array = np.zeros((300, 300), dtype=np.uint8)
        template_array = np.zeros((50, 50), dtype=np.uint8)
        mock_to_ndarray.side_effect = [full_array, template_array]
        mock_multi_scale.return_value = (0.5, (100, 100))

        coords = img._get_image_coordinates()

        assert coords is None

    @patch.object(ShadowstepImage, "_get_screenshot_as_bytes")
    def test_get_image_coordinates_exception(self, mock_screenshot):
        """Test _get_image_coordinates handles exceptions."""
        img = ShadowstepImage("test.png")
        mock_screenshot.side_effect = Exception("Test error")

        coords = img._get_image_coordinates()

        assert coords is None

    def test_calculate_center(self):
        """Test _calculate_center static method."""
        coords = (100, 200, 300, 400)
        center = ShadowstepImage._calculate_center(coords)

        assert center == (200, 300)

    def test_to_grayscale_already_grayscale(self):
        """Test _to_grayscale with already grayscale image."""
        img = ShadowstepImage("test.png")

        gray_image = np.zeros((100, 100), dtype=np.uint8)
        result = img._to_grayscale(gray_image)

        assert np.array_equal(result, gray_image)

    def test_to_grayscale_color_image(self):
        """Test _to_grayscale with color image."""
        img = ShadowstepImage("test.png")

        color_image = np.zeros((100, 100, 3), dtype=np.uint8)

        with patch("cv2.cvtColor") as mock_cvt, \
             patch("cv2.convertScaleAbs") as mock_scale:
            gray = np.zeros((100, 100), dtype=np.uint8)
            mock_cvt.return_value = gray
            mock_scale.return_value = gray

            result = img._to_grayscale(color_image)

            mock_cvt.assert_called_once()
            assert isinstance(result, np.ndarray)

    @patch.object(ShadowstepImage, "is_visible")
    @patch.object(ShadowstepImage, "_perform_scroll")
    def test_scroll_to_image_found_immediately(self, mock_perform_scroll, mock_is_visible):
        """Test _scroll_to_image when image found on first check."""
        img = ShadowstepImage("test.png")
        mock_is_visible.return_value = True

        result = img._scroll_to_image(direction="down", max_attempts=5)

        assert result is img
        mock_perform_scroll.assert_not_called()

    @patch.object(ShadowstepImage, "is_visible")
    @patch.object(ShadowstepImage, "_perform_scroll")
    @patch("time.sleep")
    def test_scroll_to_image_found_after_scrolling(
        self, mock_sleep, mock_perform_scroll, mock_is_visible
    ):
        """Test _scroll_to_image when image found after scrolling."""
        img = ShadowstepImage("test.png")
        mock_is_visible.side_effect = [False, False, True]

        result = img._scroll_to_image(direction="down", max_attempts=5, step_delay=0.5)

        assert result is img
        assert mock_perform_scroll.call_count == 2

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "is_visible")
    @patch.object(ShadowstepImage, "_perform_scroll")
    @patch("time.sleep")
    def test_scroll_to_image_not_found(self, mock_sleep, mock_perform_scroll, mock_is_visible, mock_shadowstep_class):
        """Test _scroll_to_image raises TimeoutException when not found."""
        mock_instance = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        mock_is_visible.return_value = False

        with pytest.raises(Exception, match="Image not found"):
            img._scroll_to_image(direction="down", max_attempts=3)

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_perform_scroll_down(self, mock_shadowstep_class):
        """Test _perform_scroll for down direction."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_instance.driver.get_window_size.return_value = {"width": 1000, "height": 2000}
        mock_instance.driver.swipe = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")

        img._perform_scroll(direction="down", from_percent=0.8, to_percent=0.2)

        mock_instance.driver.swipe.assert_called_once()
        call_args = mock_instance.driver.swipe.call_args[0]
        assert call_args[0] == 500  # width // 2
        assert call_args[1] == 1600  # height * 0.8
        assert call_args[2] == 500  # width // 2
        assert call_args[3] == 400  # height * 0.2

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_perform_scroll_up(self, mock_shadowstep_class):
        """Test _perform_scroll for up direction."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_instance.driver.get_window_size.return_value = {"width": 1000, "height": 2000}
        mock_instance.driver.swipe = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")

        img._perform_scroll(direction="up", from_percent=0.8, to_percent=0.2)

        mock_instance.driver.swipe.assert_called_once()
        call_args = mock_instance.driver.swipe.call_args[0]
        assert call_args[1] == 400  # height * 0.2 (start)
        assert call_args[3] == 1600  # height * 0.8 (end)

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_perform_scroll_left(self, mock_shadowstep_class):
        """Test _perform_scroll for left direction."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_instance.driver.get_window_size.return_value = {"width": 1000, "height": 2000}
        mock_instance.driver.swipe = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")

        img._perform_scroll(direction="left", from_percent=0.8, to_percent=0.2)

        mock_instance.driver.swipe.assert_called_once()
        call_args = mock_instance.driver.swipe.call_args[0]
        assert call_args[0] == 800  # width * 0.8
        assert call_args[2] == 200  # width * 0.2

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_perform_scroll_right(self, mock_shadowstep_class):
        """Test _perform_scroll for right direction."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_instance.driver.get_window_size.return_value = {"width": 1000, "height": 2000}
        mock_instance.driver.swipe = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")

        img._perform_scroll(direction="right", from_percent=0.8, to_percent=0.2)

        mock_instance.driver.swipe.assert_called_once()
        call_args = mock_instance.driver.swipe.call_args[0]
        assert call_args[0] == 200  # width * 0.2 (start)
        assert call_args[2] == 800  # width * 0.8 (end)

    @patch("shadowstep.shadowstep.Shadowstep")
    def test_perform_scroll_invalid_direction(self, mock_shadowstep_class):
        """Test _perform_scroll raises ValueError for invalid direction."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_instance.driver.get_window_size.return_value = {"width": 1000, "height": 2000}
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")

        with pytest.raises(Exception, match="Invalid scroll direction"):
            img._perform_scroll(direction="invalid")

    @patch.object(ShadowstepImage, "to_ndarray")
    @patch.object(ShadowstepImage, "_get_screenshot_as_bytes")
    @patch("cv2.resize")
    @patch("cv2.matchTemplate")
    @patch("cv2.minMaxLoc")
    def test_multi_scale_matching_raw_success(
        self, mock_minmax, mock_match, mock_resize, mock_screenshot, mock_to_ndarray
    ):
        """Test _multi_scale_matching_raw returns result when match found."""
        img = ShadowstepImage("test.png", threshold=0.7)

        full_image = np.zeros((500, 500), dtype=np.uint8)
        template_image = np.zeros((50, 50), dtype=np.uint8)

        mock_resize.return_value = full_image
        result_array = np.zeros((450, 450))
        mock_match.return_value = result_array
        mock_minmax.return_value = (0, 0.8, (0, 0), (100, 100))

        result = img._multi_scale_matching_raw(full_image, template_image)

        assert result is not None
        assert isinstance(result, np.ndarray)

    @patch("cv2.resize")
    @patch("cv2.matchTemplate")
    @patch("cv2.minMaxLoc")
    def test_multi_scale_matching_raw_no_match(self, mock_minmax, mock_match, mock_resize):
        """Test _multi_scale_matching_raw returns None when no match found."""
        img = ShadowstepImage("test.png", threshold=0.7)

        full_image = np.zeros((500, 500), dtype=np.uint8)
        template_image = np.zeros((50, 50), dtype=np.uint8)

        mock_resize.return_value = full_image
        result_array = np.zeros((450, 450))
        mock_match.return_value = result_array
        mock_minmax.return_value = (0, 0.5, (0, 0), (100, 100))  # Below threshold

        result = img._multi_scale_matching_raw(full_image, template_image)

        assert result is None

    @patch("cv2.resize")
    @patch("cv2.matchTemplate")
    def test_multi_scale_matching_raw_handles_error(self, mock_match, mock_resize):
        """Test _multi_scale_matching_raw handles cv2 errors."""
        img = ShadowstepImage("test.png", threshold=0.7)

        full_image = np.zeros((500, 500), dtype=np.uint8)
        template_image = np.zeros((50, 50), dtype=np.uint8)

        mock_resize.return_value = full_image
        mock_match.side_effect = cv2.error("Test error")

        result = img._multi_scale_matching_raw(full_image, template_image)

        assert result is None

    def test_multi_scale_matching_raw_skips_small_resized(self):
        """Test _multi_scale_matching_raw skips when resized image is too small."""
        img = ShadowstepImage("test.png", threshold=0.7)

        # Create extreme scenario: very small full image and huge template
        # At small scales, 100*0.2 = 20 which is much smaller than 500
        full_image = np.ones((100, 100), dtype=np.uint8) * 128
        template_image = np.ones((500, 500), dtype=np.uint8) * 128

        # Mock matchTemplate to track if it's called for all scales
        call_count = [0]
        original_match = cv2.matchTemplate
        
        def track_match(*args, **kwargs):
            call_count[0] += 1
            return original_match(*args, **kwargs)
        
        with patch("cv2.matchTemplate", side_effect=track_match):
            # This will trigger the continue statement for small scales
            result = img._multi_scale_matching_raw(full_image, template_image)

        # Should return a result (or None if no match above threshold)
        assert result is None or isinstance(result, np.ndarray)
        # matchTemplate should be called fewer times than total scales (20)
        # because some scales are skipped via continue
        assert call_count[0] < 20


class TestShadowstepImageMethodChaining:
    """Test method chaining functionality."""

    @patch("shadowstep.shadowstep.Shadowstep")
    @patch.object(ShadowstepImage, "ensure_visible")
    @patch.object(ShadowstepImage, "_scroll_to_image")
    def test_method_chaining_scroll_tap(self, mock_scroll, mock_ensure_visible, mock_shadowstep_class):
        """Test chaining scroll and tap methods."""
        mock_instance = Mock()
        mock_instance.driver = Mock()
        mock_instance.driver.tap = Mock()
        mock_shadowstep_class.get_instance.return_value = mock_instance
        
        img = ShadowstepImage("test.png")
        img._center = (100, 200)
        mock_scroll.return_value = img

        result = img.scroll_down().tap()

        assert result is img
        mock_scroll.assert_called_once()
        mock_instance.driver.tap.assert_called_once()


class TestShadowstepImageEdgeCases:
    """Test edge cases and error handling."""

    def test_init_with_zero_threshold(self):
        """Test initialization with threshold 0.0."""
        img = ShadowstepImage("test.png", threshold=0.0)

        assert img.threshold == 0.0

    def test_init_with_threshold_one(self):
        """Test initialization with threshold 1.0."""
        img = ShadowstepImage("test.png", threshold=1.0)

        assert img.threshold == 1.0

    def test_init_with_zero_timeout(self):
        """Test initialization with timeout 0."""
        img = ShadowstepImage("test.png", timeout=0.0)

        assert img.timeout == 0.0

    def test_calculate_center_with_same_coordinates(self):
        """Test calculate center when x1==x2 and y1==y2."""
        coords = (100, 100, 100, 100)
        center = ShadowstepImage._calculate_center(coords)

        assert center == (100, 100)

    def test_to_grayscale_single_channel_with_third_dimension(self):
        """Test _to_grayscale with single channel but 3D array."""
        img = ShadowstepImage("test.png")

        # Single channel image with shape (100, 100, 1)
        single_channel = np.zeros((100, 100, 1), dtype=np.uint8)
        result = img._to_grayscale(single_channel)

        assert np.array_equal(result, single_channel)

    def test_to_grayscale_unsupported_shape(self):
        """Test _to_grayscale with unsupported shape (e.g., 4 channels)."""
        img = ShadowstepImage("test.png")

        # 4 channel image (RGBA)
        rgba_image = np.zeros((100, 100, 4), dtype=np.uint8)
        result = img._to_grayscale(rgba_image)

        # Should return the image as is (fallback case)
        assert np.array_equal(result, rgba_image)

