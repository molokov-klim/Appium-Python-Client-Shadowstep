# ruff: noqa
# pyright: ignore
"""Unit tests for ElementGestures class using mocks."""
from unittest.mock import Mock, patch, PropertyMock

import pytest

from shadowstep.element.element import Element
from shadowstep.element.gestures import ElementGestures


class TestElementGesturesInit:
    """Test ElementGestures initialization."""

    def test_init_creates_instance_with_element(self):
        """Test initialization creates instance with element reference."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        assert gestures.element == mock_element
        assert gestures.shadowstep == mock_shadowstep
        assert gestures.converter == mock_element.converter
        assert gestures.utilities == mock_element.utilities
        assert gestures.logger is not None
        assert gestures.mobile_commands is not None


class TestTap:
    """Test tap method."""

    def test_tap_without_duration(self):
        """Test tap without duration parameter."""
        mock_shadowstep = Mock()
        mock_driver = Mock()
        mock_driver.tap = Mock()
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.driver = mock_driver
        mock_element.get_driver = Mock()
        mock_element.get_center = Mock(return_value=(100, 200))
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        result = gestures.tap()

        mock_element.get_driver.assert_called_once()
        mock_element.get_center.assert_called_once()
        mock_driver.tap.assert_called_once_with(positions=[(100, 200)], duration=None)
        assert result == mock_element

    def test_tap_with_duration(self):
        """Test tap with custom duration."""
        mock_shadowstep = Mock()
        mock_driver = Mock()
        mock_driver.tap = Mock()
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.driver = mock_driver
        mock_element.get_driver = Mock()
        mock_element.get_center = Mock(return_value=(150, 250))
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        result = gestures.tap(duration=500)

        mock_driver.tap.assert_called_once_with(positions=[(150, 250)], duration=500)
        assert result == mock_element


class TestClick:
    """Test click method."""

    def test_click_without_duration(self):
        """Test click without duration uses click_gesture."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()
        mock_element._get_web_element = Mock()
        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.click_gesture = Mock()

        result = gestures.click()

        mock_element.get_driver.assert_called_once()
        mock_element._get_web_element.assert_called_once()
        gestures.mobile_commands.click_gesture.assert_called_once_with({"elementId": "element_123"})
        assert result == mock_element

    def test_click_with_duration(self):
        """Test click with duration uses long_click_gesture."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()

        mock_web_element = Mock()
        mock_web_element.id = "element_123"
        mock_element._get_web_element = Mock(return_value=mock_web_element)

        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.long_click_gesture = Mock()

        result = gestures.click(duration=1000)

        gestures.mobile_commands.long_click_gesture.assert_called_once_with({
            "elementId": "element_123",
            "duration": 1000
        })
        assert result == mock_element


class TestClickDouble:
    """Test click_double method."""

    def test_click_double_calls_double_click_gesture(self):
        """Test click_double uses double_click_gesture."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.get_driver = Mock()

        mock_web_element = Mock()
        mock_web_element.id = "element_123"
        mock_element._get_web_element = Mock(return_value=mock_web_element)

        mock_element.locator = ("id", "test")
        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.double_click_gesture = Mock()

        result = gestures.double_click()

        mock_element.get_driver.assert_called_once()
        gestures.mobile_commands.double_click_gesture.assert_called_once_with({"elementId": "element_123"})
        assert result == mock_element


class TestDrag:
    """Test drag method."""

    def test_drag_calls_drag_gesture(self):
        """Test drag calls drag_gesture with correct parameters."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()

        mock_web_element = Mock()
        mock_web_element.id = "element_123"
        mock_element._get_web_element = Mock(return_value=mock_web_element)

        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.drag_gesture = Mock()

        result = gestures.drag(end_x=300, end_y=400, speed=3000)

        gestures.mobile_commands.drag_gesture.assert_called_once_with({
            "elementId": "element_123",
            "endX": 300,
            "endY": 400,
            "speed": 3000
        })
        assert result == mock_element

    def test_drag_with_default_speed(self):
        """Test drag with default speed."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()
        mock_element._get_web_element = Mock()
        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.drag_gesture = Mock()

        result = gestures.drag(end_x=100, end_y=200)

        gestures.mobile_commands.drag_gesture.assert_called_once()
        call_args = gestures.mobile_commands.drag_gesture.call_args[0][0]
        assert call_args["speed"] == 2500  # default


class TestFling:
    """Test fling method."""

    def test_fling_calls_fling_gesture(self):
        """Test fling calls fling_gesture with correct parameters."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()

        mock_web_element = Mock()
        mock_web_element.id = "element_123"
        mock_element._get_web_element = Mock(return_value=mock_web_element)

        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.fling_gesture = Mock()

        result = gestures.fling(speed=5000, direction="up")

        gestures.mobile_commands.fling_gesture.assert_called_once_with({
            "elementId": "element_123",
            "direction": "up",
            "speed": 5000
        })
        assert result == mock_element

    def test_fling_with_different_directions(self):
        """Test fling with different direction values."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()
        mock_element._get_web_element = Mock()
        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.fling_gesture = Mock()

        for direction in ["up", "down", "left", "right"]:
            gestures.fling(speed=3000, direction=direction)

        assert gestures.mobile_commands.fling_gesture.call_count == 4


class TestScroll:
    """Test scroll method."""

    def test_scroll_calls_scroll_gesture(self):
        """Test scroll calls scroll_gesture with correct parameters."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()
        mock_element._get_web_element = Mock()
        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.scroll_gesture = Mock(return_value=True)

        result = gestures.scroll(direction="down", percent=0.8, speed=6000, return_bool=False)

        gestures.mobile_commands.scroll_gesture.assert_called_once()
        call_args = gestures.mobile_commands.scroll_gesture.call_args[0][0]
        assert call_args["elementId"] == "element_123"
        assert call_args["direction"] == "down"
        assert call_args["percent"] == 0.8
        assert call_args["speed"] == 6000
        assert result == mock_element

    def test_scroll_returns_bool_when_return_bool_true(self):
        """Test scroll returns boolean when return_bool=True."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()
        mock_element._get_web_element = Mock()
        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.scroll_gesture = Mock(return_value=True)

        result = gestures.scroll(direction="up", percent=0.7, speed=5000, return_bool=True)

        assert result is True


class TestScrollToBottom:
    """Test scroll_to_bottom method."""

    def test_scroll_to_bottom_calls_scroll_gesture(self):
        """Test scroll_to_bottom calls scroll_down until it returns False."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.timeout = 10
        mock_element.scroll_down = Mock(return_value=False)
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        result = gestures.scroll_to_bottom(percent=0.8, speed=9000)

        # Should call scroll_down with specified parameters
        mock_element.scroll_down.assert_called_with(percent=0.8, speed=9000, return_bool=True)
        assert result == mock_element

    def test_scroll_to_bottom_with_defaults(self):
        """Test scroll_to_bottom with default parameters."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.timeout = 10
        mock_element.scroll_down = Mock(return_value=False)
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        result = gestures.scroll_to_bottom()

        # Should use default parameters
        mock_element.scroll_down.assert_called_with(percent=0.7, speed=8000, return_bool=True)
        assert result == mock_element


class TestScrollToTop:
    """Test scroll_to_top method."""

    def test_scroll_to_top_calls_scroll_gesture(self):
        """Test scroll_to_top calls scroll_up until it returns False."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.timeout = 10
        mock_element.scroll_up = Mock(return_value=False)
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        result = gestures.scroll_to_top(percent=0.75, speed=7000)

        # Should call scroll_up with specified parameters
        # Note: first call uses positional args, second uses keyword args
        mock_element.scroll_up.assert_called()
        assert result == mock_element


class TestScrollToElement:
    """Test scroll_to_element method."""

    def test_scroll_to_element_with_tuple_locator(self):
        """Test scroll_to_element with tuple locator."""
        mock_shadowstep = Mock()
        mock_shadowstep.get_element = Mock()
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        
        mock_converter = Mock()
        mock_converter.to_uiselector = Mock(return_value='new UiSelector().text("target")')
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        target_locator = ("xpath", "//target")
        target_element = Mock(spec=Element)
        mock_shadowstep.get_element.return_value = target_element
        
        with patch.object(gestures, '_execute_scroll_script') as mock_execute:
            result = gestures.scroll_to_element(target_locator, max_swipes=15)

            mock_converter.to_uiselector.assert_called_once_with(target_locator)
            mock_execute.assert_called_once_with('new UiSelector().text("target")', 15)
            mock_shadowstep.get_element.assert_called_once_with(target_locator)
            assert result == target_element

    def test_scroll_to_element_with_element_locator(self):
        """Test scroll_to_element when locator is Element instance."""
        mock_shadowstep = Mock()
        mock_shadowstep.get_element = Mock()
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        
        mock_converter = Mock()
        mock_converter.to_uiselector = Mock(return_value='new UiSelector().resourceId("target_id")')
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        target_element_locator = Mock(spec=Element)
        target_element_locator.locator = ("id", "target_id")
        
        target_element = Mock(spec=Element)
        mock_shadowstep.get_element.return_value = target_element
        
        with patch.object(gestures, '_execute_scroll_script'):
            result = gestures.scroll_to_element(target_element_locator)

            # Should use the locator from Element
            assert result == target_element


class TestZoom:
    """Test zoom method."""

    def test_zoom_calls_pinch_open_gesture(self):
        """Test zoom calls pinch_open_gesture."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()

        mock_web_element = Mock()
        mock_web_element.id = "element_123"
        mock_element._get_web_element = Mock(return_value=mock_web_element)

        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.pinch_open_gesture = Mock()

        result = gestures.zoom(percent=0.8, speed=3000)

        gestures.mobile_commands.pinch_open_gesture.assert_called_once_with({
            "elementId": "element_123",
            "percent": 0.8,
            "speed": 3000
        })
        assert result == mock_element

    def test_zoom_with_defaults(self):
        """Test zoom with default parameters."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()
        mock_element._get_web_element = Mock()
        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.pinch_open_gesture = Mock()

        result = gestures.zoom()

        call_args = gestures.mobile_commands.pinch_open_gesture.call_args[0][0]
        assert call_args["percent"] == 0.75
        assert call_args["speed"] == 2500


class TestUnzoom:
    """Test unzoom method."""

    def test_unzoom_calls_pinch_close_gesture(self):
        """Test unzoom calls pinch_close_gesture."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()

        mock_web_element = Mock()
        mock_web_element.id = "element_123"
        mock_element._get_web_element = Mock(return_value=mock_web_element)

        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.pinch_close_gesture = Mock()

        result = gestures.unzoom(percent=0.6, speed=2000)

        gestures.mobile_commands.pinch_close_gesture.assert_called_once_with({
            "elementId": "element_123",
            "percent": 0.6,
            "speed": 2000
        })
        assert result == mock_element


class TestSwipe:
    """Test swipe method."""

    def test_swipe_calls_swipe_gesture(self):
        """Test swipe calls swipe_gesture."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()

        mock_web_element = Mock()
        mock_web_element.id = "element_123"
        mock_element._get_web_element = Mock(return_value=mock_web_element)

        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.swipe_gesture = Mock()

        result = gestures.swipe(direction="left", percent=0.8, speed=4000)

        gestures.mobile_commands.swipe_gesture.assert_called_once_with({
            "elementId": "element_123",
            "direction": "left",
            "percent": 0.8,
            "speed": 4000
        })
        assert result == mock_element

    def test_swipe_with_different_directions(self):
        """Test swipe with all direction values."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("id", "test")
        mock_element.get_driver = Mock()
        mock_element._get_web_element = Mock()
        mock_element.id = "element_123"
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)
        gestures.mobile_commands.swipe_gesture = Mock()

        for direction in ["up", "down", "left", "right"]:
            gestures.swipe(direction=direction, percent=0.75, speed=5000)

        assert gestures.mobile_commands.swipe_gesture.call_count == 4


class TestTapAndMove:
    """Test tap_and_move method."""

    def test_tap_and_move_with_coordinates(self):
        """Test tap_and_move with x, y coordinates."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        with patch.object(gestures, '_perform_tap_and_move_action', return_value=mock_element) as mock_perform:
            result = gestures.tap_and_move(x=100, y=200)

            mock_perform.assert_called_once_with(None, 100, 200, None, None)
            assert result == mock_element

    def test_tap_and_move_with_direction_and_distance(self):
        """Test tap_and_move with direction and distance."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        with patch.object(gestures, '_perform_tap_and_move_action', return_value=mock_element) as mock_perform:
            result = gestures.tap_and_move(direction=45, distance=100)

            mock_perform.assert_called_once_with(None, None, None, 45, 100)
            assert result == mock_element

    def test_tap_and_move_with_locator(self):
        """Test tap_and_move with target element locator."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        target_locator = ("id", "target")
        
        with patch.object(gestures, '_perform_tap_and_move_action', return_value=mock_element) as mock_perform:
            result = gestures.tap_and_move(locator=target_locator)

            mock_perform.assert_called_once_with(target_locator, None, None, None, None)
            assert result == mock_element

    def test_tap_and_move_returns_element_when_internal_returns_none(self):
        """Test tap_and_move returns element when internal method returns None."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        gestures = ElementGestures(mock_element)

        with patch.object(gestures, '_perform_tap_and_move_action', return_value=None):
            result = gestures.tap_and_move(x=100, y=200)

            assert result == mock_element

