# ruff: noqa
# pyright: ignore
"""Tests for MobileCommands class."""
from typing import Any

import pytest
from unittest.mock import Mock, patch
from shadowstep.ui_automator.mobile_commands import MobileCommands
from selenium.common.exceptions import (
    NoSuchDriverException,
    InvalidSessionIdException,
    StaleElementReferenceException,
)


class TestMobileCommands:
    """Test cases for MobileCommands class."""

    @pytest.fixture(autouse=True)
    def setup_mobile_commands(self):
        """Setup MobileCommands with required methods for fail_safe decorator."""
        MobileCommands._instance = None
        mobile = MobileCommands()
        mobile.is_connected = Mock(return_value=True)
        mobile.reconnect = Mock()
        yield mobile
        MobileCommands._instance = None

    def test_singleton_pattern_returns_same_instance(self):
        """Test that MobileCommands follows singleton pattern."""
        instance1 = MobileCommands()
        instance2 = MobileCommands()

        assert instance1 is instance2

    def test_singleton_pattern_with_multiple_calls(self):
        """Test singleton pattern with multiple instantiations."""
        instances = [MobileCommands() for _ in range(5)]

        assert all(instance is instances[0] for instance in instances)

    def test_logger_initialization_happens_once(self):
        """Test that logger is initialized only once."""
        instance1 = MobileCommands()
        logger1 = instance1.logger

        instance2 = MobileCommands()
        logger2 = instance2.logger

        assert logger1 is logger2
        assert logger1.name == "shadowstep.ui_automator.mobile_commands.MobileCommands"

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_execute_with_dict_params(self, mock_get_driver: Any):
        """Test _execute method with dict parameters."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "result"
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        params = {"key": "value"}
        result = mobile._execute("mobile: test", params)

        mock_driver.execute_script.assert_called_once_with("mobile: test", params)
        assert result == "result"

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_execute_with_list_params(self, mock_get_driver: Any):
        """Test _execute method with list parameters."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = [1, 2, 3]
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        params = ["item1", "item2"]
        result = mobile._execute("mobile: test", params)

        mock_driver.execute_script.assert_called_once_with("mobile: test", params)
        assert result == [1, 2, 3]

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_execute_with_none_params(self, mock_get_driver: Any):
        """Test _execute method converts None params to empty dict."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "result"
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        result = mobile._execute("mobile: test", None)

        mock_driver.execute_script.assert_called_once_with("mobile: test", {})
        assert result == "result"

    @pytest.mark.parametrize(
        "method_name,command_name",
        [
            ("accept_alert", "mobile: acceptAlert"),
            ("activate_app", "mobile: activateApp"),
            ("background_app", "mobile: backgroundApp"),
            ("battery_info", "mobile: batteryInfo"),
            ("bluetooth", "mobile: bluetooth"),
            ("broadcast", "mobile: broadcast"),
            ("change_permissions", "mobile: changePermissions"),
            ("clear_app", "mobile: clearApp"),
            ("click_gesture", "mobile: clickGesture"),
            ("deep_link", "mobile: deepLink"),
            ("delete_file", "mobile: deleteFile"),
            ("deviceidle", "mobile: deviceidle"),
            ("device_info", "mobile: deviceInfo"),
            ("dismiss_alert", "mobile: dismissAlert"),
            ("double_click_gesture", "mobile: doubleClickGesture"),
            ("drag_gesture", "mobile: dragGesture"),
            ("exec_emu_console_command", "mobile: execEmuConsoleCommand"),
            ("fingerprint", "mobile: fingerprint"),
            ("fling_gesture", "mobile: flingGesture"),
            ("get_action_history", "mobile: getActionHistory"),
            ("get_app_strings", "mobile: getAppStrings"),
            ("get_clipboard", "mobile: getClipboard"),
            ("get_connectivity", "mobile: getConnectivity"),
            ("get_contexts", "mobile: getContexts"),
            ("get_current_activity", "mobile: getCurrentActivity"),
            ("get_current_package", "mobile: getCurrentPackage"),
            ("get_device_time", "mobile: getDeviceTime"),
            ("get_display_density", "mobile: getDisplayDensity"),
            ("get_geolocation", "mobile: getGeolocation"),
            ("get_notifications", "mobile: getNotifications"),
            ("get_performance_data", "mobile: getPerformanceData"),
            ("get_performance_data_types", "mobile: getPerformanceDataTypes"),
            ("get_permissions", "mobile: getPermissions"),
            ("get_system_bars", "mobile: getSystemBars"),
            ("get_ui_mode", "mobile: getUiMode"),
            ("gsm_call", "mobile: gsmCall"),
            ("gsm_signal", "mobile: gsmSignal"),
            ("gsm_voice", "mobile: gsmVoice"),
            ("hide_keyboard", "mobile: hideKeyboard"),
            ("inject_emulator_camera_image", "mobile: injectEmulatorCameraImage"),
            ("install_app", "mobile: installApp"),
            ("install_multiple_apks", "mobile: installMultipleApks"),
            ("is_app_installed", "mobile: isAppInstalled"),
            ("is_gps_enabled", "mobile: isGpsEnabled"),
            ("is_keyboard_shown", "mobile: isKeyboardShown"),
            ("is_locked", "mobile: isLocked"),
            ("is_media_projection_recording_running", "mobile: isMediaProjectionRecordingRunning"),
            ("list_sms", "mobile: listSms"),
            ("lock", "mobile: lock"),
            ("long_click_gesture", "mobile: longClickGesture"),
            ("network_speed", "mobile: networkSpeed"),
            ("nfc", "mobile: nfc"),
            ("open_notifications", "mobile: openNotifications"),
            ("perform_editor_action", "mobile: performEditorAction"),
            ("pinch_close_gesture", "mobile: pinchCloseGesture"),
            ("pinch_open_gesture", "mobile: pinchOpenGesture"),
            ("power_ac", "mobile: powerAC"),
            ("power_capacity", "mobile: powerCapacity"),
            ("press_key", "mobile: pressKey"),
            ("pull_file", "mobile: pullFile"),
            ("pull_folder", "mobile: pullFolder"),
            ("push_file", "mobile: pushFile"),
            ("query_app_state", "mobile: queryAppState"),
            ("refresh_gps_cache", "mobile: refreshGpsCache"),
            ("remove_app", "mobile: removeApp"),
            ("replace_element_value", "mobile: replaceElementValue"),
            ("reset_geolocation", "mobile: resetGeolocation"),
            ("schedule_action", "mobile: scheduleAction"),
            ("screenshots", "mobile: screenshots"),
            ("scroll", "mobile: scroll"),
            ("scroll_gesture", "mobile: scrollGesture"),
            ("send_sms", "mobile: sendSms"),
            ("send_trim_memory", "mobile: sendTrimMemory"),
            ("sensor_set", "mobile: sensorSet"),
            ("set_clipboard", "mobile: setClipboard"),
            ("set_connectivity", "mobile: setConnectivity"),
            ("set_geolocation", "mobile: setGeolocation"),
            ("set_ui_mode", "mobile: setUiMode"),
            ("shell", "mobile: shell"),
            ("start_activity", "mobile: startActivity"),
            ("start_logs_broadcast", "mobile: startLogsBroadcast"),
            ("start_media_projection_recording", "mobile: startMediaProjectionRecording"),
            ("start_screen_streaming", "mobile: startScreenStreaming"),
            ("start_service", "mobile: startService"),
            ("status_bar", "mobile: statusBar"),
            ("stop_logs_broadcast", "mobile: stopLogsBroadcast"),
            ("stop_media_projection_recording", "mobile: stopMediaProjectionRecording"),
            ("stop_screen_streaming", "mobile: stopScreenStreaming"),
            ("stop_service", "mobile: stopService"),
            ("swipe_gesture", "mobile: swipeGesture"),
            ("terminate_app", "mobile: terminateApp"),
            ("toggle_gps", "mobile: toggleGps"),
            ("type", "mobile: type"),
            ("unlock", "mobile: unlock"),
            ("unschedule_action", "mobile: unscheduleAction"),
        ],
    )
    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_mobile_command_calls_execute_with_correct_command(
        self, mock_get_driver, method_name, command_name
    ):
        """Test that mobile command method calls _execute with correct command name."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "test_result"
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        method = getattr(mobile, method_name)
        params = {"test": "param"}
        result = method(params)

        mock_driver.execute_script.assert_called_once_with(command_name, params)
        assert result == "test_result"

    @pytest.mark.parametrize(
        "method_name,command_name",
        [
            ("shell", "mobile: shell"),
            ("battery_info", "mobile: batteryInfo"),
            ("get_clipboard", "mobile: getClipboard"),
        ],
    )
    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_mobile_command_with_none_params(
        self, mock_get_driver, method_name, command_name
    ):
        """Test mobile command methods with None parameters."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "result"
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        method = getattr(mobile, method_name)
        result = method(None)

        mock_driver.execute_script.assert_called_once_with(command_name, {})
        assert result == "result"

    @pytest.mark.parametrize(
        "method_name,command_name",
        [
            ("shell", "mobile: shell"),
            ("battery_info", "mobile: batteryInfo"),
            ("get_clipboard", "mobile: getClipboard"),
        ],
    )
    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_mobile_command_without_params(
        self, mock_get_driver, method_name, command_name
    ):
        """Test mobile command methods called without parameters."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "result"
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        method = getattr(mobile, method_name)
        result = method()

        mock_driver.execute_script.assert_called_once_with(command_name, {})
        assert result == "result"

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_fail_safe_decorator_handles_no_such_driver_exception(
        self, mock_get_driver
    ):
        """Test that _execute propagates NoSuchDriverException."""
        mock_driver = Mock()
        mock_driver.execute_script.side_effect = NoSuchDriverException("Driver not found")
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        with pytest.raises(NoSuchDriverException):
            mobile.shell({"command": "ls"})

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_fail_safe_decorator_handles_invalid_session_exception(
        self, mock_get_driver
    ):
        """Test that _execute propagates InvalidSessionIdException."""
        mock_driver = Mock()
        mock_driver.execute_script.side_effect = InvalidSessionIdException(
            "Invalid session"
        )
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        with pytest.raises(InvalidSessionIdException):
            mobile.battery_info()

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_fail_safe_decorator_handles_stale_element_exception(
        self, mock_get_driver
    ):
        """Test that _execute propagates StaleElementReferenceException."""
        mock_driver = Mock()
        mock_driver.execute_script.side_effect = StaleElementReferenceException(
            "Stale element"
        )
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        with pytest.raises(StaleElementReferenceException):
            mobile.get_device_time()

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_mobile_command_returns_dict_result(self, mock_get_driver: Any):
        """Test mobile command method returns dict result."""
        mock_driver = Mock()
        expected_result = {"status": "success", "data": "value"}
        mock_driver.execute_script.return_value = expected_result
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        result = mobile.device_info()

        assert result == expected_result

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_mobile_command_returns_list_result(self, mock_get_driver: Any):
        """Test mobile command method returns list result."""
        mock_driver = Mock()
        expected_result = ["context1", "context2"]
        mock_driver.execute_script.return_value = expected_result
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        result = mobile.get_contexts()

        assert result == expected_result

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_mobile_command_returns_boolean_result(self, mock_get_driver: Any):
        """Test mobile command method returns boolean result."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = True
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        result = mobile.is_locked()

        assert result is True

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_mobile_command_returns_string_result(self, mock_get_driver: Any):
        """Test mobile command method returns string result."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "MainActivity"
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        result = mobile.get_current_activity()

        assert result == "MainActivity"

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_mobile_command_returns_integer_result(self, mock_get_driver: Any):
        """Test mobile command method returns integer result."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = 420
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        result = mobile.get_display_density()

        assert result == 420

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_execute_called_by_get_driver(self, mock_get_driver: Any):
        """Test that _execute calls WebDriverSingleton.get_driver."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "result"
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        mobile._execute("mobile: test", {"param": "value"})

        mock_get_driver.assert_called_once()

    @patch("shadowstep.ui_automator.mobile_commands.WebDriverSingleton.get_driver")
    def test_multiple_commands_use_same_driver(self, mock_get_driver: Any):
        """Test that multiple commands use the same driver instance."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "result"
        mock_get_driver.return_value = mock_driver

        mobile = MobileCommands()

        mobile.shell({"command": "ls"})
        mobile.battery_info()
        mobile.device_info()

        assert mock_get_driver.call_count == 3
        assert mock_driver.execute_script.call_count == 3
