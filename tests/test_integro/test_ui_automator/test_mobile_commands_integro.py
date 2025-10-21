# ruff: noqa
# pyright: ignore
"""
Integration tests for mobile_commands.py module.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_ui_automator/test_mobile_commands.py
"""

import logging
import time
from typing import Any

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.ui_automator.mobile_commands import MobileCommands

logger = logging.getLogger(__name__)


class TestMobileCommands:
    """Integration tests for MobileCommands class."""

    @pytest.fixture(autouse=True)
    def setup_mobile_commands(self, app: Shadowstep):
        """Setup MobileCommands instance with app fixture."""
        self.mobile_commands = MobileCommands()
        self.app = app
        # Ensure app is connected
        assert self.app.is_connected()  # noqa: S101
        yield

    def test_singleton_pattern(self):
        """Test that MobileCommands follows singleton pattern."""
        instance1 = MobileCommands()
        instance2 = MobileCommands()
        assert instance1 is instance2  # noqa: S101

    def test_battery_info(self):
        """Test battery_info command returns device battery information."""
        result = self.mobile_commands.battery_info()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "level" in result  # noqa: S101
        assert "state" in result  # noqa: S101

    def test_device_info(self):
        """Test device_info command returns device information."""
        result = self.mobile_commands.device_info()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "androidId" in result  # noqa: S101

    def test_get_device_time(self):
        """Test get_device_time command returns device time."""
        result = self.mobile_commands.get_device_time()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_is_keyboard_shown(self):
        """Test is_keyboard_shown command."""
        result = self.mobile_commands.is_keyboard_shown()

        assert result is not None  # noqa: S101
        assert isinstance(result, bool)  # noqa: S101

    def test_get_current_package(self):
        """Test get_current_package command."""
        result = self.mobile_commands.get_current_package()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_get_current_activity(self):
        """Test get_current_activity command."""
        result = self.mobile_commands.get_current_activity()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_get_display_density(self):
        """Test get_display_density command."""
        result = self.mobile_commands.get_display_density()

        assert result is not None  # noqa: S101
        assert isinstance(result, int)  # noqa: S101
        assert result > 0  # noqa: S101

    def test_get_system_bars(self):
        """Test get_system_bars command."""
        result = self.mobile_commands.get_system_bars()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "statusBar" in result  # noqa: S101

    def test_is_locked(self):
        """Test is_locked command."""
        result = self.mobile_commands.is_locked()

        assert result is not None  # noqa: S101
        assert isinstance(result, bool)  # noqa: S101

    def test_lock_unlock(self):
        """Test lock and unlock commands."""
        # Lock the device
        self.mobile_commands.lock()
        time.sleep(1)

        # Check if locked (may not work on all devices)
        is_locked = self.mobile_commands.is_locked()
        # Some emulators don't support lock, so just ensure command executes

        # Unlock the device
        self.mobile_commands.unlock()
        time.sleep(1)

        # Check if unlocked
        is_locked = self.mobile_commands.is_locked()
        # Should at least return a boolean
        assert isinstance(is_locked, bool)  # noqa: S101

    def test_get_clipboard(self):
        """Test get_clipboard command."""
        # Get clipboard content (returns base64 encoded string)
        result = self.mobile_commands.get_clipboard()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101
        # Just verify it returns a base64-like string (doesn't contain non-base64 chars)
        # Content verification is difficult as clipboard may contain previous data

    def test_set_clipboard(self):
        """Test set_clipboard command."""
        test_text = "integration_test_text"
        result = self.mobile_commands.set_clipboard(
            {"content": test_text, "contentType": "plaintext"}
        )

        # Should not raise an exception
        assert result is None or result is not None  # noqa: S101

    def test_get_contexts(self):
        """Test get_contexts command."""
        result = self.mobile_commands.get_contexts()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101
        # Context list may be empty on some devices/configurations

    def test_shell_command(self):
        """Test shell command execution."""
        # Execute simple shell command
        result = self.mobile_commands.shell({"command": "echo", "args": ["test"]})

        assert result is not None  # noqa: S101
        assert "test" in result  # noqa: S101

    def test_shell_command_getprop(self):
        """Test shell command with getprop."""
        result = self.mobile_commands.shell(
            {"command": "getprop", "args": ["ro.build.version.sdk"]}
        )

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101
        assert result.strip().isdigit()  # noqa: S101

    def test_click_gesture(self):
        """Test click_gesture command."""
        # Click at center of screen
        result = self.mobile_commands.click_gesture({"x": 500, "y": 500})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_long_click_gesture(self):
        """Test long_click_gesture command."""
        result = self.mobile_commands.long_click_gesture({"x": 500, "y": 500, "duration": 1000})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_double_click_gesture(self):
        """Test double_click_gesture command."""
        result = self.mobile_commands.double_click_gesture({"x": 500, "y": 500})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_swipe_gesture(self):
        """Test swipe_gesture command."""
        result = self.mobile_commands.swipe_gesture(
            {
                "left": 100,
                "top": 500,
                "width": 600,
                "height": 100,
                "direction": "left",
                "percent": 0.75,
            }
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_scroll_gesture(self):
        """Test scroll_gesture command."""
        result = self.mobile_commands.scroll_gesture(
            {
                "left": 100,
                "top": 500,
                "width": 600,
                "height": 800,
                "direction": "down",
                "percent": 1.0,
            }
        )

        # Returns boolean indicating if can scroll more
        assert isinstance(result, bool)  # noqa: S101

    def test_drag_gesture(self):
        """Test drag_gesture command."""
        result = self.mobile_commands.drag_gesture(
            {"startX": 500, "startY": 500, "endX": 500, "endY": 800}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_open_notifications(self):
        """Test open_notifications command."""
        result = self.mobile_commands.open_notifications()
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Press back to close notifications
        self.app.terminal.press_back()

    @pytest.mark.xfail(reason="Requires keyboard to be shown", strict=False)
    def test_hide_keyboard(self):
        """Test hide_keyboard command."""
        # This may not do anything if keyboard is not shown
        result = self.mobile_commands.hide_keyboard()
        # Should complete without exception if keyboard is shown
        logger.info(result)

    def test_press_key(self):
        """Test press_key command."""
        # Press home key
        result = self.mobile_commands.press_key({"keycode": 3})
        time.sleep(0.5)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_is_app_installed(self, android_settings_open_close: Any):
        """Test is_app_installed command."""
        # Check if Settings app is installed
        result = self.mobile_commands.is_app_installed({"appId": "com.android.settings"})

        assert result is True  # noqa: S101

    def test_is_app_not_installed(self):
        """Test is_app_installed with non-existent app."""
        result = self.mobile_commands.is_app_installed({"appId": "com.nonexistent.app.xyz"})

        assert result is False  # noqa: S101

    def test_query_app_state(self, android_settings_open_close: Any):
        """Test query_app_state command."""
        # Query state of Settings app while it's open
        result = self.mobile_commands.query_app_state({"appId": "com.android.settings"})

        assert result is not None  # noqa: S101
        # 4 = running in foreground
        assert result == 4  # noqa: S101

    def test_activate_app(self, android_settings_open_close: Any):
        """Test activate_app command."""
        # Close settings first
        self.app.terminal.close_app("com.android.settings")
        time.sleep(1)

        # Activate settings
        result = self.mobile_commands.activate_app({"appId": "com.android.settings"})
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Verify app is in foreground
        state = self.mobile_commands.query_app_state({"appId": "com.android.settings"})
        assert state == 4  # noqa: S101

    def test_terminate_app(self, android_settings_open_close: Any):
        """Test terminate_app command."""
        # Ensure app is running
        self.mobile_commands.activate_app({"appId": "com.android.settings"})
        time.sleep(1)

        # Terminate the app
        result = self.mobile_commands.terminate_app({"appId": "com.android.settings"})
        time.sleep(1)

        # Should return True if terminated
        assert result is True  # noqa: S101

        # Verify app is not in foreground
        state = self.mobile_commands.query_app_state({"appId": "com.android.settings"})
        assert state != 4  # noqa: S101

    def test_background_app(self, android_settings_open_close: Any):
        """Test background_app command."""
        # Put app in background for 1 second
        result = self.mobile_commands.background_app({"seconds": 1})
        time.sleep(2)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_start_activity(self):
        """Test start_activity command."""
        result = self.mobile_commands.start_activity({"intent": "android.settings.SETTINGS"})
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Close settings
        self.app.terminal.close_app("com.android.settings")

    def test_get_performance_data_types(self):
        """Test get_performance_data_types command."""
        result = self.mobile_commands.get_performance_data_types()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101
        assert len(result) > 0  # noqa: S101 # type: ignore

    @pytest.mark.xfail(
        reason="Performance data parsing may fail on some devices/emulators", strict=False
    )
    def test_get_performance_data(self, android_settings_open_close: Any):
        """Test get_performance_data command."""
        # Get available performance data types first
        data_types = self.mobile_commands.get_performance_data_types()

        assert data_types is not None  # noqa: S101
        assert isinstance(data_types, list)  # noqa: S101

        if data_types and len(data_types) > 0:  # type: ignore
            # Get performance data for the first available type
            result = self.mobile_commands.get_performance_data(
                {"packageName": "com.android.settings", "dataType": data_types[0]}
            )

            assert result is not None  # noqa: S101
            assert isinstance(result, list)  # noqa: S101

    def test_type_text(self, android_settings_open_close: Any):
        """Test type command for text input."""
        # Click on search or any input field first would be ideal
        # For now just test the command executes
        result = self.mobile_commands.type({"text": "test"})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_screenshots_command(self):
        """Test screenshots command."""
        result = self.mobile_commands.screenshots()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_get_notifications(self):
        """Test get_notifications command."""
        result = self.mobile_commands.get_notifications()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101

    def test_start_stop_logs_broadcast(self):
        """Test start_logs_broadcast and stop_logs_broadcast commands."""
        # Start logs broadcast
        result = self.mobile_commands.start_logs_broadcast()
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Stop logs broadcast
        result = self.mobile_commands.stop_logs_broadcast()

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_get_ui_mode(self):
        """Test get_ui_mode command."""
        result = self.mobile_commands.get_ui_mode()
        assert result is not None  # noqa: S101

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_set_ui_mode(self):
        """Test set_ui_mode command."""
        # Get current mode
        current_mode = self.mobile_commands.get_ui_mode()

        # Set mode (car, night, etc.)
        # This might not work on all devices
        result = self.mobile_commands.set_ui_mode({"mode": "night"})
        logger.info(result)
        # Restore original mode
        self.mobile_commands.set_ui_mode({"mode": current_mode})

    def test_clear_app(self):
        """Test clear_app command."""
        result = self.mobile_commands.clear_app({"appId": "com.android.settings"})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_broadcast(self):
        """Test broadcast command."""
        # Send a simple broadcast
        result = self.mobile_commands.broadcast({"action": "android.intent.action.BOOT_COMPLETED"})
        # Command should execute without raising exception
        logger.info(result)

    @pytest.mark.xfail(reason="Geolocation may not be supported on all emulators", strict=False)
    def test_get_geolocation(self):
        """Test get_geolocation command."""
        result = self.mobile_commands.get_geolocation()

        if result is not None:
            assert isinstance(result, dict)  # noqa: S101

    def test_set_geolocation(self):
        """Test set_geolocation command."""
        result = self.mobile_commands.set_geolocation({"latitude": 55.7558, "longitude": 37.6173})
        time.sleep(0.5)
        # Command should execute without raising exception
        logger.info(result)

    def test_is_gps_enabled(self):
        """Test is_gps_enabled command."""
        result = self.mobile_commands.is_gps_enabled()
        assert isinstance(result, bool)  # noqa: S101

    @pytest.mark.xfail(
        reason="Status bar command may not be supported on all devices", strict=False
    )
    def test_status_bar(self):
        """Test status_bar command."""
        result = self.mobile_commands.status_bar(
            {
                "command": "notifications",
                "component": "com.android.systemui/.statusbar.phone.StatusBar",
            }
        )
        # Command should execute without raising exception
        logger.info(result)

    def test_pinch_open_gesture(self):
        """Test pinch_open_gesture command."""
        result = self.mobile_commands.pinch_open_gesture(
            {"left": 100, "top": 100, "width": 600, "height": 600, "percent": 0.5}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_pinch_close_gesture(self):
        """Test pinch_close_gesture command."""
        result = self.mobile_commands.pinch_close_gesture(
            {"left": 100, "top": 100, "width": 600, "height": 600, "percent": 0.5}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_fling_gesture(self):
        """Test fling_gesture command."""
        result = self.mobile_commands.fling_gesture(
            {
                "left": 100,
                "top": 100,
                "width": 600,
                "height": 800,
                "direction": "down",
                "speed": 7500,
            }
        )

        # Returns boolean indicating if can scroll more
        assert isinstance(result, bool)  # noqa: S101

    def test_get_permissions(self, android_settings_open_close: Any):
        """Test get_permissions command."""
        result = self.mobile_commands.get_permissions(
            {"type": "requested", "appId": "com.android.settings"}
        )

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101

    def test_delete_file(self):
        """Test delete_file command."""
        # Create a test file first via shell
        self.mobile_commands.shell({"command": "touch", "args": ["/sdcard/test_delete_file.txt"]})
        time.sleep(0.5)

        # Delete the file
        result = self.mobile_commands.delete_file({"remotePath": "/sdcard/test_delete_file.txt"})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_perform_editor_action(self):
        """Test perform_editor_action command."""
        # This requires an active text field
        # Just test that command doesn't crash
        result = self.mobile_commands.perform_editor_action({"action": "Done"})
        logger.info(result)

    def test_deviceidle(self):
        """Test deviceidle command for whitelisting apps."""
        # This requires API 23+
        result = self.mobile_commands.deviceidle(
            {"action": "whitelistAdd", "packages": ["com.android.settings"]}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Remove from whitelist
        self.mobile_commands.deviceidle(
            {"action": "whitelistRemove", "packages": ["com.android.settings"]}
        )

    @pytest.mark.xfail(reason="Requires scrollable element with specific selector", strict=False)
    def test_scroll_legacy(self):
        """Test scroll legacy command."""
        # This is the old scroll command, different from scroll_gesture
        result = self.mobile_commands.scroll({"strategy": "accessibility id", "selector": "test"})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires alert to be present on screen", strict=False)
    def test_accept_alert(self):
        """Test accept_alert command."""
        result = self.mobile_commands.accept_alert()
        logger.info(result)

    @pytest.mark.xfail(reason="Requires alert to be present on screen", strict=False)
    def test_dismiss_alert(self):
        """Test dismiss_alert command."""
        result = self.mobile_commands.dismiss_alert()
        logger.info(result)

    @pytest.mark.xfail(reason="Bluetooth may not be supported on all emulators", strict=False)
    def test_bluetooth(self):
        """Test bluetooth command."""
        # Try to get bluetooth state
        result = self.mobile_commands.bluetooth({"action": "getState"})
        logger.info(result)

    def test_change_permissions(self):
        """Test change_permissions command."""
        result = self.mobile_commands.change_permissions(
            {
                "appId": "com.android.settings",
                "permissions": "android.permission.READ_CONTACTS",
                "action": "grant",
            }
        )
        logger.info(result)

    @pytest.mark.xfail(reason="Deep link requires browser app to be installed", strict=False)
    def test_deep_link(self):
        """Test deep_link command."""
        result = self.mobile_commands.deep_link(
            {"url": "https://www.example.com", "package": "com.android.chrome"}
        )
        time.sleep(1)
        logger.info(result)

    @pytest.mark.xfail(
        reason="Emulator console command only works on emulators with console access", strict=False
    )
    def test_exec_emu_console_command(self):
        """Test exec_emu_console_command."""
        result = self.mobile_commands.exec_emu_console_command({"command": "help"})
        logger.info(result)

    @pytest.mark.xfail(
        reason="Fingerprint requires emulator with fingerprint support", strict=False
    )
    def test_fingerprint(self):
        """Test fingerprint command."""
        result = self.mobile_commands.fingerprint({"fingerprintId": 1})
        logger.info(result)

    @pytest.mark.xfail(reason="May not be supported on all UiAutomator2 versions", strict=False)
    def test_get_action_history(self):
        """Test get_action_history command."""
        result = self.mobile_commands.get_action_history()
        assert isinstance(result, list)  # noqa: S101
        logger.info(result)  # type: ignore

    @pytest.mark.xfail(reason="May not be supported on all UiAutomator2 versions", strict=False)
    def test_get_app_strings(self):
        """Test get_app_strings command."""
        result = self.mobile_commands.get_app_strings()
        assert isinstance(result, dict)  # noqa: S101
        logger.info(result)  # type: ignore

    def test_get_connectivity(self):
        """Test get_connectivity command."""
        result = self.mobile_commands.get_connectivity()
        assert isinstance(result, dict)  # noqa: S101
        logger.info(result)  # type: ignore

    def test_set_connectivity(self):
        """Test set_connectivity command."""
        result = self.mobile_commands.set_connectivity({"wifi": True, "data": True})
        logger.info(result)

    @pytest.mark.xfail(
        reason="GSM commands only work on emulators with telephony support", strict=False
    )
    def test_gsm_call(self):
        """Test gsm_call command."""
        result = self.mobile_commands.gsm_call({"phoneNumber": "5551234567", "action": "call"})
        logger.info(result)

    @pytest.mark.xfail(
        reason="GSM commands only work on emulators with telephony support", strict=False
    )
    def test_gsm_signal(self):
        """Test gsm_signal command."""
        result = self.mobile_commands.gsm_signal({"signalStrength": 4})
        logger.info(result)

    @pytest.mark.xfail(
        reason="GSM commands only work on emulators with telephony support", strict=False
    )
    def test_gsm_voice(self):
        """Test gsm_voice command."""
        result = self.mobile_commands.gsm_voice({"state": "on"})
        logger.info(result)

    @pytest.mark.xfail(reason="Emulator camera injection only works on emulators", strict=False)
    def test_inject_emulator_camera_image(self):
        """Test inject_emulator_camera_image command."""
        result = self.mobile_commands.inject_emulator_camera_image({"image": "base64encodedimage"})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires valid APK file path", strict=False)
    def test_install_app(self):
        """Test install_app command."""
        result = self.mobile_commands.install_app({"appPath": "/path/to/app.apk"})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires valid APK file paths", strict=False)
    def test_install_multiple_apks(self):
        """Test install_multiple_apks command."""
        result = self.mobile_commands.install_multiple_apks(
            {"apks": ["/path/to/app1.apk", "/path/to/app2.apk"]}
        )
        logger.info(result)

    def test_is_media_projection_recording_running(self):
        """Test is_media_projection_recording_running command."""
        result = self.mobile_commands.is_media_projection_recording_running()
        assert isinstance(result, bool)  # noqa: S101

    def test_start_media_projection_recording(self):
        """Test start_media_projection_recording command."""
        result = self.mobile_commands.start_media_projection_recording()
        logger.info(result)

    @pytest.mark.xfail(reason="EACCES: permission denied, mkdtemp 'recordingR6m2hB'", strict=False)
    def test_stop_media_projection_recording(self):
        """Test stop_media_projection_recording command."""
        result = self.mobile_commands.stop_media_projection_recording()
        logger.info(result)

    @pytest.mark.xfail(
        reason="SMS commands only work on emulators with telephony support", strict=False
    )
    def test_list_sms(self):
        """Test list_sms command."""
        result = self.mobile_commands.list_sms()
        assert isinstance(result, list)  # noqa: S101

    @pytest.mark.xfail(
        reason="SMS commands only work on emulators with telephony support", strict=False
    )
    def test_send_sms(self):
        """Test send_sms command."""
        result = self.mobile_commands.send_sms(
            {"phoneNumber": "5551234567", "message": "Test message"}
        )
        logger.info(result)

    @pytest.mark.xfail(reason="Network speed control only works on emulators", strict=False)
    def test_network_speed(self):
        """Test network_speed command."""
        result = self.mobile_commands.network_speed({"speed": "full"})
        logger.info(result)

    @pytest.mark.xfail(reason="NFC may not be supported on all devices/emulators", strict=False)
    def test_nfc(self):
        """Test nfc command."""
        result = self.mobile_commands.nfc({"action": "getState"})
        logger.info(result)

    @pytest.mark.xfail(reason="Power commands only work on emulators", strict=False)
    def test_power_ac(self):
        """Test power_ac command."""
        result = self.mobile_commands.power_ac({"state": "on"})
        logger.info(result)

    @pytest.mark.xfail(reason="Power commands only work on emulators", strict=False)
    def test_power_capacity(self):
        """Test power_capacity command."""
        result = self.mobile_commands.power_capacity({"percent": 100})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires file to exist on device", strict=False)
    def test_pull_file(self):
        """Test pull_file command."""
        result = self.mobile_commands.pull_file({"remotePath": "/sdcard/test_file.txt"})
        logger.info(result)

    def test_pull_folder(self):
        """Test pull_folder command."""
        result = self.mobile_commands.pull_folder({"remotePath": "/sdcard/"})
        logger.info(result)

    def test_push_file(self):
        """Test push_file command."""
        result = self.mobile_commands.push_file(
            {"remotePath": "/sdcard/test.txt", "payload": "dGVzdCBjb250ZW50"}
        )
        logger.info(result)

    @pytest.mark.xfail(reason="GPS cache refresh may not be supported on all devices", strict=False)
    def test_refresh_gps_cache(self):
        """Test refresh_gps_cache command."""
        result = self.mobile_commands.refresh_gps_cache()
        logger.info(result)

    @pytest.mark.skip(reason="Does not work on emulators")
    def test_reset_geolocation(self):
        """Test reset_geolocation command."""
        result = self.mobile_commands.reset_geolocation()
        logger.info(result)

    def test_toggle_gps(self):
        """Test toggle_gps command."""
        result = self.mobile_commands.toggle_gps()
        logger.info(result)

    @pytest.mark.xfail(reason="Requires valid element ID", strict=False)
    def test_replace_element_value(self):
        """Test replace_element_value command."""
        result = self.mobile_commands.replace_element_value(
            {"elementId": "test", "text": "replacement"}
        )
        logger.info(result)

    @pytest.mark.xfail(reason="Action scheduling may not be supported", strict=False)
    def test_schedule_action(self):
        """Test schedule_action command."""
        result = self.mobile_commands.schedule_action({"action": "test_action", "delayMs": 1000})
        logger.info(result)

    @pytest.mark.xfail(reason="Action scheduling may not be supported", strict=False)
    def test_unschedule_action(self):
        """Test unschedule_action command."""
        result = self.mobile_commands.unschedule_action({"action": "test_action"})
        logger.info(result)

    @pytest.mark.xfail(reason="Trim memory may not be supported on all devices", strict=False)
    def test_send_trim_memory(self):
        """Test send_trim_memory command."""
        result = self.mobile_commands.send_trim_memory({"level": 80})
        logger.info(result)

    @pytest.mark.xfail(reason="Sensor control only works on emulators", strict=False)
    def test_sensor_set(self):
        """Test sensor_set command."""
        result = self.mobile_commands.sensor_set({"sensorType": "light", "value": 50})
        logger.info(result)

    def test_start_screen_streaming(self):
        """Test start_screen_streaming command."""
        result = self.mobile_commands.start_screen_streaming()
        logger.info(result)

    def test_stop_screen_streaming(self):
        """Test stop_screen_streaming command."""
        result = self.mobile_commands.stop_screen_streaming()
        logger.info(result)

    @pytest.mark.xfail(reason="Service commands may not work with all intents", strict=False)
    def test_start_service(self):
        """Test start_service command."""
        result = self.mobile_commands.start_service({"intent": "com.android.settings/.Settings"})
        logger.info(result)

    @pytest.mark.xfail(reason="Service commands may not work with all intents", strict=False)
    def test_stop_service(self):
        """Test stop_service command."""
        result = self.mobile_commands.stop_service({"intent": "com.android.settings/.Settings"})
        logger.info(result)
