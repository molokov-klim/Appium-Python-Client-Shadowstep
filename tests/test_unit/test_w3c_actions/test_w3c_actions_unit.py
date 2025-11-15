# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Unit tests for W3CActions class using mocks."""
from unittest.mock import Mock, PropertyMock, patch

import pytest

from shadowstep.w3c_actions.w3c_actions import W3CActions


class TestW3CActionsInit:
    """Test W3CActions initialization."""

    def test_init_creates_instance(self):
        """Test initialization creates instance with logger."""
        w3c_actions = W3CActions()

        assert w3c_actions.logger is not None


class TestScroll:
    """Test scroll method."""

    def test_scroll_down_success(self):
        """Test scroll down returns True on success."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 100,
            "y": 200,
            "width": 300,
            "height": 400
        }

        mock_driver = Mock()
        type(mock_driver).page_source = PropertyMock(side_effect=["<page1/>", "<page2/>"])

        with patch.object(w3c_actions, '_swipe_with_duration') as mock_swipe, \
             patch.object(type(w3c_actions), '_driver', PropertyMock(return_value=mock_driver)):
            result = w3c_actions.scroll(
                element=mock_element,
                direction="down",
                percent=0.8,
                speed=5000
            )

            mock_swipe.assert_called_once()
            call_args = mock_swipe.call_args[0]

            # Check coordinates (center_x, start_y, center_x, end_y)
            assert call_args[0] == 250  # center_x = 100 + 300//2
            assert call_args[2] == 250  # center_x
            assert call_args[1] > call_args[3]  # start_y > end_y for down (swipe from bottom to top)

            assert result is True

    def test_scroll_up_success(self):
        """Test scroll up returns True on success."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 50,
            "y": 100,
            "width": 200,
            "height": 300
        }

        mock_driver = Mock()
        type(mock_driver).page_source = PropertyMock(side_effect=["<page1/>", "<page2/>"])

        with patch.object(w3c_actions, '_swipe_with_duration') as mock_swipe, \
             patch.object(type(w3c_actions), '_driver', PropertyMock(return_value=mock_driver)):
            result = w3c_actions.scroll(
                element=mock_element,
                direction="up",
                percent=0.5,
                speed=3000
            )

            mock_swipe.assert_called_once()
            call_args = mock_swipe.call_args[0]

            # Check coordinates - for up direction start_y < end_y (swipe from top to bottom)
            assert call_args[1] < call_args[3]
            assert result is True

    def test_scroll_left_success(self):
        """Test scroll left returns True on success."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 100,
            "y": 200,
            "width": 400,
            "height": 300
        }

        mock_driver = Mock()
        type(mock_driver).page_source = PropertyMock(side_effect=["<page1/>", "<page2/>"])

        with patch.object(w3c_actions, '_swipe_with_duration') as mock_swipe, \
             patch.object(type(w3c_actions), '_driver', PropertyMock(return_value=mock_driver)):
            result = w3c_actions.scroll(
                element=mock_element,
                direction="left",
                percent=0.7,
                speed=4000
            )

            mock_swipe.assert_called_once()
            call_args = mock_swipe.call_args[0]

            # Check coordinates - for left direction start_x < end_x (swipe from left to right)
            assert call_args[0] < call_args[2]
            assert result is True

    def test_scroll_right_success(self):
        """Test scroll right returns True on success."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 100,
            "y": 200,
            "width": 400,
            "height": 300
        }

        mock_driver = Mock()
        type(mock_driver).page_source = PropertyMock(side_effect=["<page1/>", "<page2/>"])

        with patch.object(w3c_actions, '_swipe_with_duration') as mock_swipe, \
             patch.object(type(w3c_actions), '_driver', PropertyMock(return_value=mock_driver)):
            result = w3c_actions.scroll(
                element=mock_element,
                direction="right",
                percent=0.6,
                speed=6000
            )

            mock_swipe.assert_called_once()
            call_args = mock_swipe.call_args[0]

            # Check coordinates - for right direction start_x > end_x (swipe from right to left)
            assert call_args[0] > call_args[2]
            assert result is True

    def test_scroll_calculates_duration_correctly(self):
        """Test scroll calculates duration based on speed."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 1000
        }

        mock_driver = Mock()
        mock_driver.page_source = "<page1/>"

        with patch.object(w3c_actions, '_swipe_with_duration') as mock_swipe, \
             patch.object(type(w3c_actions), '_driver', PropertyMock(return_value=mock_driver)):
            # With 1000 pixels distance and 1000 px/s speed, duration should be 1000ms
            w3c_actions.scroll(
                element=mock_element,
                direction="down",
                percent=1.0,  # full height = 1000px
                speed=1000
            )

            duration_ms = mock_swipe.call_args[0][4]
            assert duration_ms == 1000

    def test_scroll_with_zero_speed(self):
        """Test scroll with zero speed sets duration to 0."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100
        }

        mock_driver = Mock()
        mock_driver.page_source = "<page1/>"

        with patch.object(w3c_actions, '_swipe_with_duration') as mock_swipe, \
             patch.object(type(w3c_actions), '_driver', PropertyMock(return_value=mock_driver)):
            w3c_actions.scroll(
                element=mock_element,
                direction="down",
                percent=0.5,
                speed=0
            )

            duration_ms = mock_swipe.call_args[0][4]
            assert duration_ms == 0

    def test_scroll_invalid_direction_returns_false(self):
        """Test scroll with invalid direction raises ValueError."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100
        }

        with pytest.raises(ValueError, match="Invalid direction: invalid"):
            w3c_actions.scroll(
                element=mock_element,
                direction="invalid",
                percent=0.5,
                speed=1000
            )

    def test_scroll_exception_propagates(self):
        """Test scroll propagates exception when it occurs."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {"x": 0, "y": 0, "width": 100, "height": 100}

        mock_driver = Mock()
        mock_driver.page_source = "<page1/>"

        with patch.object(w3c_actions, '_swipe_with_duration', side_effect=Exception("Test error")), \
             patch.object(type(w3c_actions), '_driver', PropertyMock(return_value=mock_driver)):
            with pytest.raises(Exception, match="Test error"):
                w3c_actions.scroll(
                    element=mock_element,
                    direction="down",
                    percent=0.5,
                    speed=1000
                )


class TestSwipe:
    """Test swipe method."""

    def test_swipe_calls_scroll(self):
        """Test swipe delegates to scroll method."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100
        }

        with patch.object(w3c_actions, 'scroll') as mock_scroll:
            w3c_actions.swipe(
                element=mock_element,
                direction="left",
                percent=0.8,
                speed=5000
            )

            mock_scroll.assert_called_once_with(
                mock_element,
                "left",
                0.8,
                5000
            )

    def test_swipe_with_different_parameters(self):
        """Test swipe with various parameters."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 50,
            "y": 100,
            "width": 200,
            "height": 300
        }

        with patch.object(w3c_actions, 'scroll') as mock_scroll:
            w3c_actions.swipe(
                element=mock_element,
                direction="right",
                percent=0.6,
                speed=3000
            )

            mock_scroll.assert_called_once_with(
                mock_element,
                "right",
                0.6,
                3000
            )


class TestClick:
    """Test click method."""

    @patch('shadowstep.w3c_actions.w3c_actions.WebDriverSingleton.get_driver')
    @patch('shadowstep.w3c_actions.w3c_actions.ActionChains')
    def test_click_without_duration(self, mock_action_chains, mock_get_driver):
        """Test click without duration performs quick tap."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 100,
            "y": 200,
            "width": 50,
            "height": 50
        }

        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver

        mock_actions = Mock()
        mock_action_chains.return_value = mock_actions

        w3c_actions.click(mock_element)

        # Verify ActionChains was created with driver
        mock_action_chains.assert_called_once_with(mock_driver)

        # Verify perform was called
        mock_actions.perform.assert_called_once()

    @patch('shadowstep.w3c_actions.w3c_actions.WebDriverSingleton.get_driver')
    @patch('shadowstep.w3c_actions.w3c_actions.ActionChains')
    def test_click_with_duration(self, mock_action_chains, mock_get_driver):
        """Test click with duration performs long press."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 50,
            "y": 100,
            "width": 100,
            "height": 80
        }

        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver

        mock_actions = Mock()
        mock_action_chains.return_value = mock_actions

        w3c_actions.click(mock_element, duration=1000)

        # Verify perform was called
        mock_actions.perform.assert_called_once()


class TestDoubleClick:
    """Test double_click method."""

    @patch('shadowstep.w3c_actions.w3c_actions.WebDriverSingleton.get_driver')
    @patch('shadowstep.w3c_actions.w3c_actions.ActionChains')
    def test_double_click_performs_two_clicks(self, mock_action_chains, mock_get_driver):
        """Test double_click performs two quick clicks with pause."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 100,
            "y": 200,
            "width": 60,
            "height": 60
        }

        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver

        mock_actions = Mock()
        mock_action_chains.return_value = mock_actions

        w3c_actions.double_click(mock_element)

        # Verify ActionChains was created with driver
        mock_action_chains.assert_called_once_with(mock_driver)

        # Verify perform was called
        mock_actions.perform.assert_called_once()


class TestDrag:
    """Test drag method."""

    def test_drag_calculates_distance_and_calls_swipe(self):
        """Test drag calculates distance and delegates to _swipe_with_duration."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100
        }

        with patch.object(w3c_actions, '_swipe_with_duration') as mock_swipe:
            # Drag from element center (50, 50) to (200, 200)
            w3c_actions.drag(
                element=mock_element,
                end_x=200,
                end_y=200,
                speed=1000
            )

            mock_swipe.assert_called_once()
            call_args = mock_swipe.call_args[0]

            # Verify start position (center of element)
            assert call_args[0] == 50  # start_x
            assert call_args[1] == 50  # start_y

            # Verify end position
            assert call_args[2] == 200  # end_x
            assert call_args[3] == 200  # end_y

            # Duration should be calculated from distance and speed
            # Distance = sqrt((200-50)^2 + (200-50)^2) = sqrt(45000) H 212
            # Duration = 212 / 1000 * 1000 = 212ms
            assert call_args[4] > 0

    def test_drag_with_zero_speed(self):
        """Test drag with zero speed sets duration to 0."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 0,
            "y": 0,
            "width": 50,
            "height": 50
        }

        with patch.object(w3c_actions, '_swipe_with_duration') as mock_swipe:
            w3c_actions.drag(
                element=mock_element,
                end_x=100,
                end_y=100,
                speed=0
            )

            duration_ms = mock_swipe.call_args[0][4]
            assert duration_ms == 0


class TestFling:
    """Test fling method."""

    def test_fling_calls_scroll_with_high_percent(self):
        """Test fling delegates to scroll with 0.8 percent."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100
        }

        with patch.object(w3c_actions, 'scroll') as mock_scroll:
            w3c_actions.fling(
                element=mock_element,
                direction="up",
                speed=8000
            )

            mock_scroll.assert_called_once_with(
                mock_element,
                "up",
                percent=0.8,
                speed=8000
            )

    def test_fling_with_different_directions(self):
        """Test fling with all directions."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100
        }

        directions = ["up", "down", "left", "right"]

        for direction in directions:
            with patch.object(w3c_actions, 'scroll') as mock_scroll:
                w3c_actions.fling(
                    element=mock_element,
                    direction=direction,
                    speed=5000
                )

                mock_scroll.assert_called_once_with(
                    mock_element,
                    direction,
                    percent=0.8,
                    speed=5000
                )


class TestZoom:
    """Test zoom method."""

    def test_zoom_performs_pinch_open_gesture(self):
        """Test zoom performs two-finger pinch open gesture."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 100,
            "y": 200,
            "width": 200,
            "height": 300
        }

        with patch.object(w3c_actions, '_multi_touch_gesture') as mock_multi_touch:
            w3c_actions.zoom(
                element=mock_element,
                percent=0.8,
                speed=2500
            )

            mock_multi_touch.assert_called_once()
            call_args = mock_multi_touch.call_args[0]

            start_positions = call_args[0]
            end_positions = call_args[1]

            # Both fingers should start at center
            center_x = 200  # 100 + 200//2
            center_y = 350  # 200 + 300//2

            assert start_positions[0][0] == center_x
            assert start_positions[0][1] == center_y
            assert start_positions[1][0] == center_x
            assert start_positions[1][1] == center_y

            # Fingers should move apart (one up, one down)
            assert end_positions[0][1] < center_y  # finger1 moves up
            assert end_positions[1][1] > center_y  # finger2 moves down

    def test_zoom_calculates_distance_from_smaller_dimension(self):
        """Test zoom uses smaller dimension for pinch distance calculation."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 0,
            "y": 0,
            "width": 100,  # smaller
            "height": 300  # larger
        }

        with patch.object(w3c_actions, '_multi_touch_gesture') as mock_multi_touch:
            w3c_actions.zoom(
                element=mock_element,
                percent=0.5,
                speed=1000
            )

            call_args = mock_multi_touch.call_args[0]
            start_positions = call_args[0]
            end_positions = call_args[1]

            # Distance should be based on width (100), not height (300)
            # distance = min(100, 300) * 0.5 / 2 = 25
            distance = abs(end_positions[0][1] - start_positions[0][1])
            assert distance == 25


class TestUnzoom:
    """Test unzoom method."""

    def test_unzoom_performs_pinch_close_gesture(self):
        """Test unzoom performs two-finger pinch close gesture."""
        w3c_actions = W3CActions()

        mock_element = Mock()
        mock_element.rect = {
            "x": 100,
            "y": 200,
            "width": 200,
            "height": 300
        }

        with patch.object(w3c_actions, '_multi_touch_gesture') as mock_multi_touch:
            w3c_actions.unzoom(
                element=mock_element,
                percent=0.6,
                speed=2000
            )

            mock_multi_touch.assert_called_once()
            call_args = mock_multi_touch.call_args[0]

            start_positions = call_args[0]
            end_positions = call_args[1]

            # Fingers should start apart
            center_x = 200
            center_y = 350

            # Check fingers start apart and end at center
            assert start_positions[0][1] < center_y  # finger1 starts above
            assert start_positions[1][1] > center_y  # finger2 starts below

            assert end_positions[0][0] == center_x  # finger1 ends at center
            assert end_positions[0][1] == center_y
            assert end_positions[1][0] == center_x  # finger2 ends at center
            assert end_positions[1][1] == center_y


class TestSwipeWithDuration:
    """Test _swipe_with_duration private method."""

    @patch('shadowstep.w3c_actions.w3c_actions.WebDriverSingleton.get_driver')
    @patch('shadowstep.w3c_actions.w3c_actions.ActionChains')
    def test_swipe_with_duration_creates_action_chain(self, mock_action_chains, mock_get_driver):
        """Test _swipe_with_duration creates proper action chain."""
        w3c_actions = W3CActions()

        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver

        mock_actions = Mock()
        mock_action_chains.return_value = mock_actions

        w3c_actions._swipe_with_duration(
            start_x=100,
            start_y=200,
            end_x=300,
            end_y=400,
            duration_ms=500
        )

        # Verify ActionChains was created with driver
        mock_action_chains.assert_called_once_with(mock_driver)

        # Verify perform was called
        mock_actions.perform.assert_called_once()

    @patch('shadowstep.w3c_actions.w3c_actions.WebDriverSingleton.get_driver')
    @patch('shadowstep.w3c_actions.w3c_actions.ActionChains')
    def test_swipe_with_zero_duration(self, mock_action_chains, mock_get_driver):
        """Test _swipe_with_duration with zero duration."""
        w3c_actions = W3CActions()

        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver

        mock_actions = Mock()
        mock_action_chains.return_value = mock_actions

        w3c_actions._swipe_with_duration(
            start_x=0,
            start_y=0,
            end_x=100,
            end_y=100,
            duration_ms=0
        )

        # Verify ActionChains was created with driver
        mock_action_chains.assert_called_once_with(mock_driver)

        # Verify perform was called
        mock_actions.perform.assert_called_once()


class TestRaiseInvalidDirectionError:
    """Test _raise_invalid_direction_error method."""

    def test_raise_invalid_direction_error(self):
        """Test _raise_invalid_direction_error raises ValueError."""
        w3c_actions = W3CActions()

        with pytest.raises(ValueError, match="Invalid direction: diagonal"):
            w3c_actions._raise_invalid_direction_error("diagonal")

    def test_raise_invalid_direction_error_message_format(self):
        """Test error message includes direction and valid options."""
        w3c_actions = W3CActions()

        with pytest.raises(ValueError, match="up/down/left/right"):
            w3c_actions._raise_invalid_direction_error("sideways")


class TestDriverProperty:
    """Test _driver property."""

    @patch('shadowstep.w3c_actions.w3c_actions.WebDriverSingleton.get_driver')
    def test_driver_property_returns_driver_from_singleton(self, mock_get_driver):
        """Test _driver property gets driver from WebDriverSingleton."""
        w3c_actions = W3CActions()

        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver

        result = w3c_actions._driver

        mock_get_driver.assert_called_once()
        assert result == mock_driver
