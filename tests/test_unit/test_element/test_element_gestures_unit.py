# ruff: noqa
# pyright: ignore
"""Unit tests for shadowstep/element/gestures.py module."""
from typing import Any
from unittest.mock import Mock, patch, MagicMock
import pytest

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.element.gestures import ElementGestures
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep


class TestElementGestures:
    """Test suite for ElementGestures class."""

    def _create_test_element(self, mock_driver: Mock, timeout: float = 1.0) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        el.timeout = timeout
        el.id = "element-123"
        return app, el

    # Tests for __init__ method
    @pytest.mark.unit
    def test_element_gestures_initialization(self):
        """Test ElementGestures initialization."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        gestures = ElementGestures(el)
        
        assert gestures.element is el
        assert gestures.shadowstep is el.shadowstep
        assert gestures.converter is el.converter
        assert gestures.utilities is el.utilities
        assert gestures.logger is not None
        assert gestures.mobile_commands is not None

    # Tests for tap method
    @pytest.mark.unit
    def test_tap_success(self):
        """Test successful tap operation."""
        mock_driver = Mock()
        mock_driver.tap = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            el.driver = mock_driver  # Set driver after get_driver
            with patch.object(el, 'get_center', return_value=(100, 200)):
                result = el.gestures.tap()
        
        assert result is el
        mock_driver.tap.assert_called_once_with(positions=[(100, 200)], duration=None)

    @pytest.mark.unit
    def test_tap_with_duration(self):
        """Test tap with custom duration."""
        mock_driver = Mock()
        mock_driver.tap = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            el.driver = mock_driver  # Set driver after get_driver
            with patch.object(el, 'get_center', return_value=(150, 250)):
                result = el.gestures.tap(duration=500)
        
        assert result is el
        mock_driver.tap.assert_called_once_with(positions=[(150, 250)], duration=500)

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_tap_handles_no_such_driver_exception(self, mock_handle_error):
        """Test tap handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=NoSuchDriverException("No driver")):
            result = el.gestures.tap()
        
        assert result is el
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_tap_handles_stale_element_reference_exception(self):
        """Test tap handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_driver.tap = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        call_count = [0]
        def mock_get_center():
            call_count[0] += 1
            if call_count[0] == 1:
                raise StaleElementReferenceException("Stale")
            return (100, 200)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            el.driver = mock_driver  # Set driver after get_driver
            with patch.object(el, 'get_center', side_effect=mock_get_center):
                with patch.object(el, 'get_native', return_value=Mock()):
                    result = el.gestures.tap()
        
        assert result is el
        mock_driver.tap.assert_called_once()

    # Tests for tap_and_move method
    @pytest.mark.unit
    def test_tap_and_move_with_coordinates(self):
        """Test tap_and_move with x,y coordinates."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.gestures, '_perform_tap_and_move_action', return_value=el):
            result = el.gestures.tap_and_move(x=200, y=300)
        
        assert result is el

    @pytest.mark.unit
    def test_tap_and_move_with_locator(self):
        """Test tap_and_move with locator."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        target_locator = ("xpath", "//target")
        
        with patch.object(el.gestures, '_perform_tap_and_move_action', return_value=el):
            result = el.gestures.tap_and_move(locator=target_locator)
        
        assert result is el

    # Tests for click method
    @pytest.mark.unit
    def test_click_success(self):
        """Test successful click operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'click_gesture', return_value=None) as mock_click:
                    result = el.gestures.click()
        
        assert result is el
        mock_click.assert_called_once()

    @pytest.mark.unit
    def test_click_with_duration(self):
        """Test click with duration (long click)."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'long_click_gesture', return_value=None) as mock_long_click:
                    result = el.gestures.click(duration=1000)
        
        assert result is el
        mock_long_click.assert_called_once()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_click_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test click handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=InvalidSessionIdException("Invalid session")):
            result = el.gestures.click()
        
        assert result is el
        mock_handle_error.assert_called()

    # Tests for click_double method
    @pytest.mark.unit
    def test_click_double_success(self):
        """Test successful double-click operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'double_click_gesture', return_value=None) as mock_double_click:
                    result = el.gestures.click_double()
        
        assert result is el
        mock_double_click.assert_called_once()

    # Tests for drag method
    @pytest.mark.unit
    def test_drag_success(self):
        """Test successful drag operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'drag_gesture', return_value=None) as mock_drag:
                    result = el.gestures.drag(end_x=300, end_y=400)
        
        assert result is el
        mock_drag.assert_called_once()

    @pytest.mark.unit
    def test_drag_with_custom_speed(self):
        """Test drag with custom speed."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'drag_gesture', return_value=None) as mock_drag:
                    result = el.gestures.drag(end_x=500, end_y=600, speed=5000)
        
        assert result is el
        call_args = mock_drag.call_args[0][0]
        assert call_args['speed'] == 5000

    # Tests for fling method
    @pytest.mark.unit
    def test_fling_success(self):
        """Test successful fling operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'fling_gesture', return_value=None) as mock_fling:
                    result = el.gestures.fling(speed=8000, direction="down")
        
        assert result is el
        mock_fling.assert_called_once()

    # Tests for scroll method
    @pytest.mark.unit
    def test_scroll_success(self):
        """Test successful scroll operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'scroll_gesture', return_value=True):
                    result = el.gestures.scroll(direction="down", percent=0.5, speed=5000, return_bool=False)
        
        assert result is el

    @pytest.mark.unit
    def test_scroll_returns_bool(self):
        """Test scroll returns boolean when return_bool=True."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'scroll_gesture', return_value=True):
                    result = el.gestures.scroll(direction="up", percent=0.7, speed=6000, return_bool=True)
        
        assert result is True

    # Tests for scroll_to_bottom method
    @pytest.mark.unit
    def test_scroll_to_bottom_success(self):
        """Test successful scroll_to_bottom operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        # Mock scroll_down to return False (can't scroll anymore)
        with patch.object(el, 'scroll_down', return_value=False):
            result = el.gestures.scroll_to_bottom()
        
        assert result is el

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_scroll_to_bottom_handles_attribute_error(self, mock_handle_error):
        """Test scroll_to_bottom handles AttributeError."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'scroll_down', side_effect=AttributeError("Attribute error")):
            result = el.gestures.scroll_to_bottom()
        
        assert result is el
        mock_handle_error.assert_called()

    # Tests for scroll_to_top method
    @pytest.mark.unit
    def test_scroll_to_top_success(self):
        """Test successful scroll_to_top operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        # Mock scroll_up to return False (can't scroll anymore)
        with patch.object(el, 'scroll_up', return_value=False):
            result = el.gestures.scroll_to_top()
        
        assert result is el

    # Tests for scroll_to_element method
    @pytest.mark.unit
    def test_scroll_to_element_success(self):
        """Test successful scroll_to_element operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        target_locator = ("xpath", "//target")
        target_element = Mock()
        
        with patch.object(el.gestures, '_execute_scroll_script', return_value=None):
            with patch.object(el.shadowstep, 'get_element', return_value=target_element):
                result = el.gestures.scroll_to_element(target_locator, max_swipes=20)
        
        assert result is target_element

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_scroll_to_element_handles_webdriver_exception(self, mock_handle_error):
        """Test scroll_to_element handles WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        target_locator = {"class": "target"}
        
        with patch.object(el.gestures, '_execute_scroll_script', 
                         side_effect=WebDriverException("Instrumentation process is not running")):
            result = el.gestures.scroll_to_element(target_locator)
        
        assert result is el
        mock_handle_error.assert_called()

    # Tests for zoom method
    @pytest.mark.unit
    def test_zoom_success(self):
        """Test successful zoom operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'pinch_open_gesture', return_value=None) as mock_zoom:
                    result = el.gestures.zoom()
        
        assert result is el
        mock_zoom.assert_called_once()

    @pytest.mark.unit
    def test_zoom_with_custom_parameters(self):
        """Test zoom with custom percent and speed."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'pinch_open_gesture', return_value=None) as mock_zoom:
                    result = el.gestures.zoom(percent=0.5, speed=3000)
        
        assert result is el
        call_args = mock_zoom.call_args[0][0]
        assert call_args['percent'] == 0.5
        assert call_args['speed'] == 3000

    # Tests for unzoom method
    @pytest.mark.unit
    def test_unzoom_success(self):
        """Test successful unzoom operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'pinch_close_gesture', return_value=None) as mock_unzoom:
                    result = el.gestures.unzoom()
        
        assert result is el
        mock_unzoom.assert_called_once()

    # Tests for swipe method
    @pytest.mark.unit
    def test_swipe_success(self):
        """Test successful swipe operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'swipe_gesture', return_value=None) as mock_swipe:
                    result = el.gestures.swipe(direction="left")
        
        assert result is el
        mock_swipe.assert_called_once()

    @pytest.mark.unit
    def test_swipe_converts_direction_to_lowercase(self):
        """Test swipe converts direction to lowercase."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'swipe_gesture', return_value=None) as mock_swipe:
                    result = el.gestures.swipe(direction="UP")
        
        assert result is el
        call_args = mock_swipe.call_args[0][0]
        assert call_args['direction'] == "up"

    # Tests for _execute_scroll_script method
    @pytest.mark.unit
    def test_execute_scroll_script_success(self):
        """Test successful _execute_scroll_script operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', return_value=Mock()):
                with patch.object(el.gestures.mobile_commands, 'scroll', return_value=None) as mock_scroll:
                    el.gestures._execute_scroll_script("new UiSelector().text('Test')", max_swipes=15)
        
        mock_scroll.assert_called_once()
        call_args = mock_scroll.call_args[0][0]
        assert call_args['maxSwipes'] == 15

    # Tests for _perform_tap_and_move_action method
    @pytest.mark.unit
    def test_perform_tap_and_move_with_coordinates(self):
        """Test _perform_tap_and_move_action with x,y coordinates."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_center', return_value=(100, 100)):
                with patch.object(el.gestures, '_create_touch_actions', return_value=Mock()) as mock_create:
                    with patch.object(el.gestures, '_execute_tap_and_move_to_coordinates', return_value=el):
                        result = el.gestures._perform_tap_and_move_action(x=200, y=300)
        
        assert result is el

    @pytest.mark.unit
    def test_perform_tap_and_move_with_direction_and_distance(self):
        """Test _perform_tap_and_move_action with direction and distance."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_center', return_value=(100, 100)):
                with patch.object(el.gestures, '_create_touch_actions', return_value=Mock()):
                    with patch.object(el.gestures, '_execute_tap_and_move_by_direction', return_value=el):
                        result = el.gestures._perform_tap_and_move_action(direction=90, distance=200)
        
        assert result is el

    # Tests for _create_touch_actions method
    @pytest.mark.unit
    def test_create_touch_actions_success(self):
        """Test successful _create_touch_actions operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        result = el.gestures._create_touch_actions(x1=150, y1=250)
        
        assert result is not None
        # ActionChains should be created
        assert hasattr(result, 'w3c_actions')

    # Tests for _execute_tap_and_move_to_coordinates method
    @pytest.mark.unit
    def test_execute_tap_and_move_to_coordinates_success(self):
        """Test successful _execute_tap_and_move_to_coordinates operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        mock_actions = Mock()
        mock_actions.w3c_actions = Mock()
        mock_actions.w3c_actions.pointer_action = Mock()
        mock_actions.perform = Mock()
        
        result = el.gestures._execute_tap_and_move_to_coordinates(mock_actions, x=300, y=400)
        
        assert result is el
        mock_actions.perform.assert_called_once()

    # Tests for _execute_tap_and_move_to_element method
    @pytest.mark.unit
    def test_execute_tap_and_move_to_element_success(self):
        """Test successful _execute_tap_and_move_to_element operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        mock_actions = Mock()
        target_locator = ("xpath", "//target")
        target_web_element = Mock()
        
        with patch.object(el, '_get_web_element', return_value=target_web_element):
            with patch.object(el, 'get_center', return_value=(200, 300)):
                with patch.object(el.gestures, '_execute_tap_and_move_to_coordinates', return_value=el):
                    result = el.gestures._execute_tap_and_move_to_element(mock_actions, target_locator)
        
        assert result is el

    # Tests for _execute_tap_and_move_by_direction method
    @pytest.mark.unit
    def test_execute_tap_and_move_by_direction_success(self):
        """Test successful _execute_tap_and_move_by_direction operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        el.shadowstep.terminal = Mock()
        el.shadowstep.terminal.get_screen_resolution = Mock(return_value=(1080, 1920))
        
        mock_actions = Mock()
        
        with patch('shadowstep.element.gestures.find_coordinates_by_vector', return_value=(300, 400)):
            with patch.object(el.gestures, '_execute_tap_and_move_to_coordinates', return_value=el):
                result = el.gestures._execute_tap_and_move_by_direction(
                    mock_actions, x1=100, y1=100, direction=45, distance=200
                )
        
        assert result is el

    # Additional edge case tests
    @pytest.mark.unit
    def test_tap_continues_when_coordinates_are_none(self):
        """Test tap continues when get_center returns None."""
        mock_driver = Mock()
        mock_driver.tap = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.2)
        
        call_count = [0]
        def mock_get_center():
            call_count[0] += 1
            if call_count[0] < 3:
                return (None, None)
            return (100, 200)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            el.driver = mock_driver  # Set driver after get_driver
            with patch.object(el, 'get_center', side_effect=mock_get_center):
                result = el.gestures.tap()
        
        assert result is el
        mock_driver.tap.assert_called_once()

    @pytest.mark.unit
    def test_click_handles_webdriver_exception_other_error(self):
        """Test click raises ShadowstepElementException for other WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Some other error")
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, '_get_web_element', side_effect=error):
                with pytest.raises(ShadowstepElementException):
                    el.gestures.click()

    @pytest.mark.unit
    def test_scroll_to_element_raises_exception_for_other_webdriver_error(self):
        """Test scroll_to_element raises exception for other WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        target_locator = {"class": "target"}
        
        with patch.object(el.gestures, '_execute_scroll_script', 
                         side_effect=WebDriverException("Some other error")):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.gestures.scroll_to_element(target_locator)
        
        assert "Failed to scroll to element" in str(exc_info.value)

