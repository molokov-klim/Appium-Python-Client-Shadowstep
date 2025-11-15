# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
import base64
from unittest.mock import patch, Mock, mock_open

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.shadowstep_base import WebDriverSingleton
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_element_quality.py
"""

shadowstep = Shadowstep()

class TestShadowstepUnit:

    def _create_test_shadowstep(self) -> Shadowstep:
        """Helper method to create test Shadowstep instance."""
        # Clear any existing instances
        Shadowstep._instance = None
        return Shadowstep()
    
    @pytest.mark.unit
    def test_singleton_behavior(self):
        """Test that Shadowstep implements singleton pattern correctly."""
        # Clear any existing instances
        Shadowstep._instance = None

        # Create first instance
        instance1 = Shadowstep()
        assert instance1 is not None

        # Create second instance - should return the same instance
        instance2 = Shadowstep()
        assert instance1 is instance2

    @pytest.mark.unit
    def test_get_instance_class_method(self):
        """Test get_instance class method returns singleton instance."""
        # Clear any existing instances
        Shadowstep._instance = None

        instance1 = Shadowstep.get_instance()
        instance2 = Shadowstep.get_instance()

        assert instance1 is instance2
        assert isinstance(instance1, Shadowstep)

    @pytest.mark.unit
    def test_initialization_with_existing_instance(self):
        """Test initialization when instance already exists."""
        # Create an instance first
        instance1 = Shadowstep()
        instance1._initialized = True

        # Mock the parent __init__ to avoid actual initialization
        with patch("shadowstep.shadowstep.ShadowstepBase.__init__"):
            instance2 = Shadowstep()
            assert instance1 is instance2


    @pytest.mark.unit
    def test_list_registered_pages(self):
        """Test list_registered_pages method."""
        shadowstep = self._create_test_shadowstep()

        # Add some mock pages to navigator.pages
        mock_page1 = Mock()
        mock_page1.__name__ = "Page1"
        mock_page1.__module__ = "test_module"
        mock_page2 = Mock()
        mock_page2.__name__ = "Page2"
        mock_page2.__module__ = "test_module"
        shadowstep.navigator.pages = {"Page1": mock_page1, "Page2": mock_page2}

        with patch.object(shadowstep.navigator, "logger") as mock_logger:
            shadowstep.navigator.list_registered_pages()

            # Verify logging was called
            assert mock_logger.info.call_count >= 1

    @pytest.mark.unit
    def test_get_page_success(self):
        """Test get_page method with existing page."""
        shadowstep = self._create_test_shadowstep()

        mock_page_class = Mock()
        mock_page_instance = Mock()
        mock_page_class.return_value = mock_page_instance
        shadowstep.navigator.pages = {"TestPage": mock_page_class}

        result = shadowstep.get_page("TestPage")

        assert result is mock_page_instance
        mock_page_class.assert_called_once()

    @pytest.mark.unit
    def test_get_page_not_found(self):
        """Test get_page method with non-existing page."""
        shadowstep = self._create_test_shadowstep()

        shadowstep.navigator.pages = {}

        with pytest.raises(
                ValueError, match="Page 'NonExistentPage' not found in registered pages"
        ):
            shadowstep.get_page("NonExistentPage")

    @pytest.mark.unit
    def test_resolve_page_success(self):
        """Test resolve_page method with existing page."""
        shadowstep = self._create_test_shadowstep()

        mock_page_class = Mock()
        mock_page_instance = Mock()
        mock_page_class.return_value = mock_page_instance
        shadowstep.navigator.pages = {"TestPage": mock_page_class}

        result = shadowstep.resolve_page("TestPage")

        assert result is mock_page_instance
        mock_page_class.assert_called_once()

    @pytest.mark.unit
    def test_resolve_page_not_found(self):
        """Test resolve_page method with non-existing page."""
        shadowstep = self._create_test_shadowstep()

        shadowstep.navigator.pages = {}

        with pytest.raises(ValueError, match="Page 'NonExistentPage' not found"):
            shadowstep.resolve_page("NonExistentPage")

    @pytest.mark.unit
    def test_get_elements(self):
        """Test get_elements method."""
        shadowstep = self._create_test_shadowstep()

        mock_element = Mock()
        mock_elements = [Mock()()]
        mock_element.get_elements.return_value = mock_elements

        with patch("shadowstep.shadowstep.Element", return_value=mock_element):
            result = shadowstep.get_elements({"class": "test"})

            assert result is mock_elements
            mock_element.get_elements.assert_called_once()

    @pytest.mark.unit
    def test_get_image(self):
        """Test get_image method."""
        shadowstep = self._create_test_shadowstep()

        mock_image = Mock()

        with patch("shadowstep.shadowstep.ShadowstepImage", return_value=mock_image):
            result = shadowstep.get_image("test_image.png")

            assert result is mock_image

    @pytest.mark.unit
    def test_get_images(self):
        """Test get_images method."""
        shadowstep = self._create_test_shadowstep()

        mock_image = Mock()

        with patch("shadowstep.shadowstep.ShadowstepImage", return_value=mock_image):
            result = shadowstep.get_images("test_image.png")

            assert result == [mock_image]

    @pytest.mark.unit
    def test_schedule_action_not_implemented(self):
        """Test schedule_action method raises NotImplementedError."""
        shadowstep = self._create_test_shadowstep()

        with pytest.raises(NotImplementedError):
            shadowstep.schedule_action("test", [])

    @pytest.mark.unit
    def test_get_action_history_not_implemented(self):
        """Test get_action_history method raises NotImplementedError."""
        shadowstep = self._create_test_shadowstep()

        with pytest.raises(NotImplementedError):
            shadowstep.get_action_history("test")

    @pytest.mark.unit
    def test_unschedule_action_not_implemented(self):
        """Test unschedule_action method raises NotImplementedError."""
        shadowstep = self._create_test_shadowstep()

        with pytest.raises(NotImplementedError):
            shadowstep.unschedule_action("test")

    @pytest.mark.unit
    def test_start_logcat_with_filters(self):
        """Test start_logcat method with filters."""
        shadowstep = self._create_test_shadowstep()

        with patch.object(shadowstep._logcat, "start") as mock_start:
            filters = ["test_filter"]
            shadowstep.start_logcat("test.log", port=4723, filters=filters)

            assert shadowstep._logcat.filters == filters
            mock_start.assert_called_once_with("test.log", 4723)

    @pytest.mark.unit
    def test_start_logcat_without_filters(self):
        """Test start_logcat method without filters."""
        shadowstep = self._create_test_shadowstep()

        with patch.object(shadowstep._logcat, "start") as mock_start:
            shadowstep.start_logcat("test.log")

            mock_start.assert_called_once_with("test.log", None)

    @pytest.mark.unit
    def test_stop_logcat(self):
        """Test stop_logcat method."""
        shadowstep = self._create_test_shadowstep()

        with patch.object(shadowstep._logcat, "stop") as mock_stop:
            shadowstep.stop_logcat()

            mock_stop.assert_called_once()



    @pytest.mark.unit
    def test_scroll_invalid_direction(self):
        """Test scroll method with invalid direction."""
        shadowstep = self._create_test_shadowstep()

        with pytest.raises(ValueError, match="Invalid direction"):
            shadowstep.scroll(0, 0, 100, 100, "invalid", 0.5, 1000)

    @pytest.mark.unit
    def test_scroll_invalid_percent(self):
        """Test scroll method with invalid percent."""
        shadowstep = self._create_test_shadowstep()

        with pytest.raises(ValueError, match="Percent must be between 0 and 1"):
            shadowstep.scroll(0, 0, 100, 100, "up", 1.5, 1000)

    @pytest.mark.unit
    def test_scroll_negative_speed(self):
        """Test scroll method with negative speed."""
        shadowstep = self._create_test_shadowstep()

        with pytest.raises(ValueError, match="Speed must be non-negative"):
            shadowstep.scroll(0, 0, 100, 100, "up", 0.5, -1)

    @pytest.mark.unit
    def test_scroll_success(self):
        """Test scroll method with valid parameters."""
        shadowstep = self._create_test_shadowstep()

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "scroll_gesture") as mock_scroll:
                    result = shadowstep.scroll(100, 200, 300, 400, "up", 0.5, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify scroll_gesture was called with correct parameters
                    mock_scroll.assert_called_once_with(
                        {
                            "left": 100,
                            "top": 200,
                            "width": 300,
                            "height": 400,
                            "direction": "up",
                            "percent": 0.5,
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_long_click_negative_duration(self):
        """Test long_click method with negative duration."""

        with pytest.raises(ValueError, match="Duration must be non-negative"):
            shadowstep.long_click(100, 100, -1)

    @pytest.mark.unit
    def test_long_click_success(self):
        """Test long_click method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "long_click_gesture") as mock_long_click:
                    result = shadowstep.long_click(100, 200, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify long_click_gesture was called with correct parameters
                    mock_long_click.assert_called_once_with(
                        {"x": 100, "y": 200, "duration": 1000}
                    )

    @pytest.mark.unit
    def test_double_click_success(self):
        """Test double_click method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "double_click_gesture") as mock_double_click:
                    result = shadowstep.double_click(100, 200)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify double_click_gesture was called with correct parameters
                    mock_double_click.assert_called_once_with(
                        {"x": 100, "y": 200}
                    )

    @pytest.mark.unit
    def test_click_success(self):
        """Test click method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "click_gesture") as mock_click:
                    result = shadowstep.click(100, 200)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify click_gesture was called with correct parameters
                    mock_click.assert_called_once_with(
                        {"x": 100, "y": 200}
                    )

    @pytest.mark.unit
    def test_drag_success(self):
        """Test drag method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "drag_gesture") as mock_drag:
                    result = shadowstep.drag(100, 200, 300, 400, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify drag_gesture was called with correct parameters
                    mock_drag.assert_called_once_with(
                        {
                            "startX": 100,
                            "startY": 200,
                            "endX": 300,
                            "endY": 400,
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_fling_success(self):
        """Test fling method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "fling_gesture") as mock_fling:
                    result = shadowstep.fling(100, 200, 300, 400, "up", 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify fling_gesture was called with correct parameters
                    mock_fling.assert_called_once_with(
                        {
                            "left": 100,
                            "top": 200,
                            "width": 300,
                            "height": 400,
                            "direction": "up",
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_pinch_open_success(self):
        """Test pinch_open method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "pinch_open_gesture") as mock_pinch:
                    result = shadowstep.pinch_open(100, 200, 300, 400, 0.5, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify pinch_open_gesture was called with correct parameters
                    mock_pinch.assert_called_once_with(
                        {
                            "left": 100,
                            "top": 200,
                            "width": 300,
                            "height": 400,
                            "percent": 0.5,
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_pinch_close_success(self):
        """Test pinch_close method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "pinch_close_gesture") as mock_pinch:
                    result = shadowstep.pinch_close(100, 200, 300, 400, 0.5, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify pinch_close_gesture was called with correct parameters
                    mock_pinch.assert_called_once_with(
                        {
                            "left": 100,
                            "top": 200,
                            "width": 300,
                            "height": 400,
                            "percent": 0.5,
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_swipe_success(self):
        """Test swipe method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "swipe_gesture") as mock_swipe:
                    result = shadowstep.swipe(100, 200, 300, 400, "up", 0.5, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify swipe_gesture was called with correct parameters
                    mock_swipe.assert_called_once_with(
                        {
                            "left": 100,
                            "top": 200,
                            "width": 300,
                            "height": 400,
                            "direction": "up",
                            "percent": 0.5,
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_swipe_right_to_left_success(self):
        """Test swipe_right_to_left method with valid parameters."""

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "swipe", return_value=shadowstep) as mock_swipe:
                    result = shadowstep.swipe_right_to_left()

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify swipe was called with correct parameters
                    mock_swipe.assert_called_once_with(
                        left=0,
                        top=1000,  # height // 2
                        width=1000,
                        height=666,  # height // 3
                        direction="left",
                        percent=1.0,
                        speed=1000,
                    )

    @pytest.mark.unit
    def test_swipe_left_to_right_success(self):
        """Test swipe_left_to_right method with valid parameters."""

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "swipe", return_value=shadowstep) as mock_swipe:
                    result = shadowstep.swipe_left_to_right()

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify swipe was called with correct parameters
                    mock_swipe.assert_called_once_with(
                        left=0,
                        top=1000,  # height // 2
                        width=1000,
                        height=666,  # height // 3
                        direction="right",
                        percent=1.0,
                        speed=1000,
                    )

    @pytest.mark.unit
    def test_swipe_top_to_bottom_success(self):
        """Test swipe_top_to_bottom method with valid parameters."""

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "swipe", return_value=shadowstep) as mock_swipe:
                    result = shadowstep.swipe_top_to_bottom()

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify swipe was called with correct parameters
                    mock_swipe.assert_called_once_with(
                        left=500,  # width // 2
                        top=0,
                        width=333,  # width // 3
                        height=2000,
                        direction="down",
                        percent=1.0,
                        speed=5000,
                    )

    @pytest.mark.unit
    def test_swipe_bottom_to_top_success(self):
        """Test swipe_bottom_to_top method with valid parameters."""

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "swipe", return_value=shadowstep) as mock_swipe:
                    result = shadowstep.swipe_bottom_to_top()

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify swipe was called with correct parameters
                    mock_swipe.assert_called_once_with(
                        left=500,  # width // 2
                        top=0,
                        width=333,  # width // 3
                        height=2000,
                        direction="up",
                        percent=1.0,
                        speed=5000,
                    )

    @pytest.mark.unit
    def test_get_screenshot_success(self):
        """Test get_screenshot method with valid driver."""

        mock_driver = Mock()
        mock_driver.get_screenshot_as_base64.return_value = "dGVzdA=="  # base64 for "test"

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                result = shadowstep.get_screenshot()

                # Verify the method returns decoded screenshot
                expected = base64.b64decode("dGVzdA==")
                assert result == expected

    @pytest.mark.unit
    def test_save_source_success(self):
        """Test save_source method with valid driver."""

        mock_driver = Mock()
        mock_driver.page_source = "test page source"

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch("pathlib.Path.open", mock_open()) as mock_file:
                    result = shadowstep.save_source("/test/path", "test.xml")

                    # Verify the method returns True
                    assert result is True

                    # Verify file was opened and written to
                    mock_file.assert_called_once_with("wb")
                    mock_file().write.assert_called_once_with("test page source".encode("utf-8"))




    @pytest.mark.unit
    def test_drag_negative_speed(self):
        """Test drag method with negative speed."""

        with pytest.raises(ValueError, match="Speed must be non-negative"):
            shadowstep.drag(0, 0, 100, 100, -1)

    @pytest.mark.unit
    def test_fling_invalid_direction(self):
        """Test fling method with invalid direction."""

        with pytest.raises(ValueError, match="Invalid direction"):
            shadowstep.fling(0, 0, 100, 100, "invalid", 1000)

    @pytest.mark.unit
    def test_fling_zero_speed(self):
        """Test fling method with zero speed."""

        with pytest.raises(ValueError, match="Speed must be"):
            shadowstep.fling(0, 0, 100, 100, "up", 0)

    @pytest.mark.unit
    def test_pinch_open_invalid_percent(self):
        """Test pinch_open method with invalid percent."""

        with pytest.raises(ValueError, match="Percent must be between 0 and 1"):
            shadowstep.pinch_open(0, 0, 100, 100, 1.5, 1000)

    @pytest.mark.unit
    def test_pinch_open_negative_speed(self):
        """Test pinch_open method with negative speed."""

        with pytest.raises(ValueError, match="Speed must be non-negative"):
            shadowstep.pinch_open(0, 0, 100, 100, 0.5, -1)

    @pytest.mark.unit
    def test_pinch_close_invalid_percent(self):
        """Test pinch_close method with invalid percent."""

        with pytest.raises(ValueError, match="Percent must be between 0 and 1"):
            shadowstep.pinch_close(0, 0, 100, 100, 1.5, 1000)

    @pytest.mark.unit
    def test_pinch_close_negative_speed(self):
        """Test pinch_close method with negative speed."""

        with pytest.raises(ValueError, match="Speed must be non-negative"):
            shadowstep.pinch_close(0, 0, 100, 100, 0.5, -1)

    @pytest.mark.unit
    def test_swipe_invalid_direction(self):
        """Test swipe method with invalid direction."""

        with pytest.raises(ValueError, match="Invalid direction"):
            shadowstep.swipe(0, 0, 100, 100, "invalid", 0.5, 1000)

    @pytest.mark.unit
    def test_swipe_invalid_percent(self):
        """Test swipe method with invalid percent."""

        with pytest.raises(ValueError, match="Percent must be between 0 and 1"):
            shadowstep.swipe(0, 0, 100, 100, "up", 1.5, 1000)

    @pytest.mark.unit
    def test_swipe_negative_speed(self):
        """Test swipe method with negative speed."""

        with pytest.raises(ValueError, match="Speed must be non-negative"):
            shadowstep.swipe(0, 0, 100, 100, "up", 0.5, -1)

    @pytest.mark.unit
    def test_save_screenshot(self):
        """Test save_screenshot method."""

        mock_screenshot_data = b"fake_screenshot_data"

        with patch.object(shadowstep, "is_connected", return_value=True):
            with patch.object(shadowstep, "get_screenshot", return_value=mock_screenshot_data):
                with patch("pathlib.Path.open", mock_open()) as mock_file:
                    result = shadowstep.save_screenshot("/test/path", "test.png")

                    assert result is True
                    mock_file.assert_called_once_with("wb")



    @pytest.mark.unit
    def test_tap_with_duration(self):
        """Test tap method with duration."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                result = shadowstep.tap(100, 200, 500)

                assert result is shadowstep
                mock_driver.tap.assert_called_once_with([(100, 200)], 500)

    @pytest.mark.unit
    def test_tap_without_duration(self):
        """Test tap method without duration."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                result = shadowstep.tap(100, 200)

                assert result is shadowstep
                mock_driver.tap.assert_called_once_with([(100, 200)], 100)

    @pytest.mark.unit
    def test_start_recording_screen(self):
        """Test start_recording_screen method."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                shadowstep.start_recording_screen()

                mock_driver.start_recording_screen.assert_called_once()

    @pytest.mark.unit
    def test_stop_recording_screen(self):
        """Test stop_recording_screen method."""

        mock_driver = Mock()
        mock_driver.stop_recording_screen.return_value = "dGVzdA=="  # base64 for "test"

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                result = shadowstep.stop_recording_screen()

                expected = base64.b64decode("dGVzdA==")
                assert result == expected


    @pytest.mark.unit
    def test_update_settings_not_implemented(self):
        """Test update_settings method with no driver."""
        test_shadowstep = self._create_test_shadowstep()
        test_shadowstep.driver = None
        with pytest.raises(AttributeError):
            test_shadowstep.update_settings()


    @pytest.mark.unit
    def test_get_element(self):
        """Test get_element method."""
        mock_element = Mock()

        with patch("shadowstep.shadowstep.Element", return_value=mock_element):
            result = shadowstep.get_element({"class": "test"}, timeout=10, poll_frequency=0.2)

            assert result is mock_element

    @pytest.mark.unit
    def test_update_settings_with_driver(self):
        """Test update_settings method with valid driver."""
        test_shadowstep = self._create_test_shadowstep()
        mock_driver = Mock()
        test_shadowstep.driver = mock_driver

        test_shadowstep.update_settings()

        # Verify that update_settings was called with correct settings
        mock_driver.update_settings.assert_called_once_with(settings={"enableMultiWindows": True})



    # ================ Mobile Commands Tests ================

    @pytest.mark.unit
    def test_exec_emu_console_command_success(self):
        """Test exec_emu_console_command method with valid parameters."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "exec_emu_console_command", return_value="OK") as mock_cmd:
                    result = shadowstep.exec_emu_console_command("help", exec_timeout=10000)

                    mock_cmd.assert_called_once_with({
                        "command": "help",
                        "execTimeout": 10000,
                        "connTimeout": 5000,
                        "initTimeout": 5000,
                    })
                    assert result == "OK"

    @pytest.mark.unit
    def test_deep_link_success(self):
        """Test deep_link method with valid parameters."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "deep_link") as mock_cmd:
                    shadowstep.deep_link("myapp://test", package="com.test")

                    mock_cmd.assert_called_once_with({
                        "url": "myapp://test",
                        "package": "com.test",
                        "waitForLaunch": True,
                    })

    @pytest.mark.unit
    def test_deviceidle_success(self):
        """Test deviceidle method with valid parameters."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "deviceidle") as mock_cmd:
                    shadowstep.deviceidle("whitelistAdd", "com.test")

                    mock_cmd.assert_called_once_with({
                        "action": "whitelistAdd",
                        "packages": "com.test",
                    })

    @pytest.mark.unit
    def test_accept_alert_success(self):
        """Test accept_alert method with valid parameters."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "accept_alert") as mock_cmd:
                    shadowstep.accept_alert("OK")

                    mock_cmd.assert_called_once_with({"buttonLabel": "OK"})

    @pytest.mark.unit
    def test_dismiss_alert_success(self):
        """Test dismiss_alert method with valid parameters."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "dismiss_alert") as mock_cmd:
                    shadowstep.dismiss_alert("Cancel")

                    mock_cmd.assert_called_once_with({"buttonLabel": "Cancel"})

    @pytest.mark.unit
    def test_battery_info_success(self):
        """Test battery_info method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "battery_info", return_value={"level": 0.8}) as mock_cmd:
                    result = shadowstep.battery_info()

                    mock_cmd.assert_called_once()
                    assert result == {"level": 0.8}

    @pytest.mark.unit
    def test_device_info_success(self):
        """Test device_info method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "device_info", return_value={"model": "test"}) as mock_cmd:
                    result = shadowstep.device_info()

                    mock_cmd.assert_called_once()
                    assert result == {"model": "test"}

    @pytest.mark.unit
    def test_get_device_time_success(self):
        """Test get_device_time method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "get_device_time", return_value="2024-01-01") as mock_cmd:
                    result = shadowstep.get_device_time("YYYY-MM-DD")

                    mock_cmd.assert_called_once_with({"format": "YYYY-MM-DD"})
                    assert result == "2024-01-01"

    @pytest.mark.unit
    def test_change_permissions_success(self):
        """Test change_permissions method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "change_permissions") as mock_cmd:
                    shadowstep.change_permissions("android.permission.CAMERA", app_package="com.test", action="grant")

                    mock_cmd.assert_called_once_with({
                        "permissions": "android.permission.CAMERA",
                        "appPackage": "com.test",
                        "action": "grant",
                    })

    @pytest.mark.unit
    def test_get_permissions_success(self):
        """Test get_permissions method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "get_permissions", return_value=["CAMERA"]) as mock_cmd:
                    result = shadowstep.get_permissions(permissions_type="granted", app_package="com.test")

                    mock_cmd.assert_called_once_with({
                        "type": "granted",
                        "appPackage": "com.test",
                    })
                    assert result == ["CAMERA"]

    @pytest.mark.unit
    def test_perform_editor_action_success(self):
        """Test perform_editor_action method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "perform_editor_action") as mock_cmd:
                    shadowstep.perform_editor_action("search")

                    mock_cmd.assert_called_once_with({"action": "search"})

    @pytest.mark.unit
    def test_get_notifications_success(self):
        """Test get_notifications method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "get_notifications", return_value=[]) as mock_cmd:
                    result = shadowstep.get_notifications()

                    mock_cmd.assert_called_once()
                    assert result == []

    @pytest.mark.unit
    def test_open_notifications_success(self):
        """Test open_notifications method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "open_notifications") as mock_cmd:
                    shadowstep.open_notifications()

                    mock_cmd.assert_called_once()

    @pytest.mark.unit
    def test_list_sms_success(self):
        """Test list_sms method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "list_sms", return_value=[]) as mock_cmd:
                    result = shadowstep.list_sms(50)

                    mock_cmd.assert_called_once_with({"max": 50})
                    assert result == []

    @pytest.mark.unit
    def test_type_text_success(self):
        """Test type method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "type") as mock_cmd:
                    shadowstep.type("test text")

                    mock_cmd.assert_called_once_with({"text": "test text"})

    @pytest.mark.unit
    def test_sensor_set_success(self):
        """Test sensor_set method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "sensor_set") as mock_cmd:
                    shadowstep.sensor_set("light", "50")

                    mock_cmd.assert_called_once_with({
                        "sensorType": "light",
                        "value": "50",
                    })

    @pytest.mark.unit
    def test_delete_file_success(self):
        """Test delete_file method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "delete_file") as mock_cmd:
                    shadowstep.delete_file("/sdcard/test.txt")

                    mock_cmd.assert_called_once_with({"remotePath": "/sdcard/test.txt"})

    @pytest.mark.unit
    def test_is_app_installed_success(self):
        """Test is_app_installed method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "is_app_installed", return_value=True) as mock_cmd:
                    result = shadowstep.is_app_installed("com.test")

                    mock_cmd.assert_called_once_with({
                        "appId": "com.test",
                        "user": None,
                    })
                    assert result is True

    @pytest.mark.unit
    def test_query_app_state_success(self):
        """Test query_app_state method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "query_app_state", return_value=4) as mock_cmd:
                    result = shadowstep.query_app_state("com.test")

                    mock_cmd.assert_called_once_with({"appId": "com.test"})
                    assert result == 4

    @pytest.mark.unit
    def test_activate_app_success(self):
        """Test activate_app method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "activate_app") as mock_cmd:
                    shadowstep.activate_app("com.test")

                    mock_cmd.assert_called_once_with({"appId": "com.test"})

    @pytest.mark.unit
    def test_remove_app_success(self):
        """Test remove_app method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "remove_app") as mock_cmd:
                    shadowstep.remove_app("com.test", timeout=15000, keep_data=True)

                    mock_cmd.assert_called_once_with({
                        "appId": "com.test",
                        "keepData": True,
                        "timeout": 15000,
                    })

    @pytest.mark.unit
    def test_terminate_app_success(self):
        """Test terminate_app method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "terminate_app") as mock_cmd:
                    shadowstep.terminate_app("com.test", 1000)

                    mock_cmd.assert_called_once_with({
                        "appId": "com.test",
                        "timeout": 1000,
                    })

    @pytest.mark.unit
    def test_install_app_success(self):
        """Test install_app method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "install_app") as mock_cmd:
                    shadowstep.install_app("/path/to/app.apk", timeout=10000, replace=False)

                    mock_cmd.assert_called_once_with({
                        "appPath": "/path/to/app.apk",
                        "timeout": 10000,
                        "allowTestPackages": False,
                        "useSdcard": False,
                        "grantPermissions": False,
                        "replace": False,
                        "checkVersion": False,
                    })

    @pytest.mark.unit
    def test_clear_app_success(self):
        """Test clear_app method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "clear_app") as mock_cmd:
                    shadowstep.clear_app("com.test")

                    mock_cmd.assert_called_once_with({"appId": "com.test"})

    @pytest.mark.unit
    def test_scroll_to_element_success(self):
        """Test scroll_to_element method."""
        mock_element = Mock()

        with patch("shadowstep.shadowstep.Element", return_value=mock_element) as mock_element_class:
            mock_element.scroll_to_element.return_value = mock_element

            result = shadowstep.scroll_to_element(("id", "test"), max_swipes=20)

            assert result is mock_element
            mock_element.scroll_to_element.assert_called_once_with(("id", "test"), 20)

    @pytest.mark.unit
    def test_lock_success(self):
        """Test lock method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "lock") as mock_cmd:
                    shadowstep.lock(5)

                    mock_cmd.assert_called_once_with({"seconds": 5})

    @pytest.mark.unit
    def test_unlock_success(self):
        """Test unlock method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "unlock") as mock_cmd:
                    shadowstep.unlock("1234", "password", strategy="locksettings", timeout_ms=3000)

                    mock_cmd.assert_called_once_with({
                        "key": "1234",
                        "type": "password",
                        "strategy": "locksettings",
                        "timeoutMs": 3000,
                    })

    @pytest.mark.unit
    def test_is_locked_success(self):
        """Test is_locked method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "is_locked", return_value=False) as mock_cmd:
                    result = shadowstep.is_locked()

                    mock_cmd.assert_called_once()
                    assert result is False

    @pytest.mark.unit
    def test_background_app_success(self):
        """Test background_app method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "background_app") as mock_cmd:
                    shadowstep.background_app(10)

                    mock_cmd.assert_called_once_with({"seconds": 10})

    @pytest.mark.unit
    def test_hide_keyboard_success(self):
        """Test hide_keyboard method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "hide_keyboard") as mock_cmd:
                    shadowstep.hide_keyboard()

                    mock_cmd.assert_called_once()

    @pytest.mark.unit
    def test_is_keyboard_shown_success(self):
        """Test is_keyboard_shown method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "is_keyboard_shown", return_value=True) as mock_cmd:
                    result = shadowstep.is_keyboard_shown()

                    mock_cmd.assert_called_once()
                    assert result is True

    @pytest.mark.unit
    def test_get_current_activity_success(self):
        """Test get_current_activity method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "get_current_activity", return_value=".MainActivity") as mock_cmd:
                    result = shadowstep.get_current_activity()

                    mock_cmd.assert_called_once()
                    assert result == ".MainActivity"

    @pytest.mark.unit
    def test_get_current_package_success(self):
        """Test get_current_package method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "get_current_package", return_value="com.test") as mock_cmd:
                    result = shadowstep.get_current_package()

                    mock_cmd.assert_called_once()
                    assert result == "com.test"

    @pytest.mark.unit
    def test_shell_success(self):
        """Test shell method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "shell", return_value="output") as mock_cmd:
                    result = shadowstep.shell("ls", "-la")

                    mock_cmd.assert_called_once_with({
                        "command": "ls",
                        "args": ["-la"],
                    })
                    assert result == "output"

    @pytest.mark.unit
    def test_pull_file_success(self):
        """Test pull_file method."""
        mock_driver = Mock()
        mock_content = base64.b64encode(b"test content").decode("utf-8")

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "pull_file", return_value=mock_content) as mock_cmd:
                    result = shadowstep.pull_file("/sdcard/test.txt")

                    mock_cmd.assert_called_once_with({"remotePath": "/sdcard/test.txt"})
                    assert result == mock_content

    @pytest.mark.unit
    def test_get_clipboard_success(self):
        """Test get_clipboard method."""
        mock_driver = Mock()
        mock_content = base64.b64encode(b"clipboard text").decode("utf-8")

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "get_clipboard", return_value=mock_content) as mock_cmd:
                    result = shadowstep.get_clipboard()

                    mock_cmd.assert_called_once()
                    assert result == mock_content

    @pytest.mark.unit
    def test_set_clipboard_success(self):
        """Test set_clipboard method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "set_clipboard") as mock_cmd:
                    shadowstep.set_clipboard("test", content_type="plaintext", label="test")

                    mock_cmd.assert_called_once_with({
                        "content": "test",
                        "contentType": "plaintext",
                        "label": "test",
                    })

    @pytest.mark.unit
    def test_press_key_success(self):
        """Test press_key method."""
        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep.mobile_commands, "press_key") as mock_cmd:
                    shadowstep.press_key(4)  # BACK key

                    mock_cmd.assert_called_once_with({
                        "keycode": 4,
                        "metastate": None,
                        "flags": None,
                        "isLongPress": False,
                    })
