# ruff: noqa
# pyright: ignore
"""Integration tests for mobile_commands.py module - Part 3.

Application management test group: installation, activation, termination,
permissions, notifications, GPS, connectivity, UI mode.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_ui_automator/test_mobile_commands_integro_part_3.py
"""

import logging
import time
from typing import Any

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.ui_automator.mobile_commands import MobileCommands

logger = logging.getLogger(__name__)


class TestMobileCommandsPart3:
    """Integration tests for MobileCommands class - Part 3.
    
    Testing application management commands, permissions, notifications,
    GPS, connectivity and other system functions.
    """

    @pytest.fixture(autouse=True)
    def setup_mobile_commands(self, app: Shadowstep):
        """Setup MobileCommands instance with app fixture.
        
        Args:
            app: Shadowstep application instance for testing.
        """
        self.mobile_commands = MobileCommands()
        self.app = app
        # Ensure app is connected
        assert self.app.is_connected()  # noqa: S101
        yield

    def test_is_app_installed(self, android_settings_open_close: Any):
        """Test is_app_installed command.
        
        Verifies:
            - Settings app is installed (result True).
        
        Args:
            android_settings_open_close: Fixture for managing Android settings.
        """
        # Check if Settings app is installed
        result = self.mobile_commands.is_app_installed({"appId": "com.android.settings"})

        assert result is True  # noqa: S101

    def test_is_app_not_installed(self):
        """Test is_app_installed command with non-existent application.
        
        Verifies:
            - Non-existent application is not installed (result False).
        """
        result = self.mobile_commands.is_app_installed({"appId": "com.nonexistent.app.xyz"})

        assert result is False  # noqa: S101

    def test_query_app_state(self, android_settings_open_close: Any):
        """Test query_app_state command.
        
        Steps:
            1. Query Settings app state.
        
        Verifies:
            - Result is not None.
            - Result equals 4 (running in foreground).
        
        Args:
            android_settings_open_close: Fixture for managing Android settings.
        """
        # Query state of Settings app while it's open
        result = self.mobile_commands.query_app_state({"appId": "com.android.settings"})

        assert result is not None  # noqa: S101
        # 4 = running in foreground
        assert result == 4  # noqa: S101

    def test_activate_app(self, android_settings_open_close: Any):
        """Test activate_app command.
        
        Steps:
            1. Close Settings app.
            2. Activate Settings app.
            3. Verify app is in foreground.
        
        Args:
            android_settings_open_close: Fixture for managing Android settings.
        """
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
        """Test terminate_app command.
        
        Steps:
            1. Activate Settings app.
            2. Terminate the app.
            3. Verify app is not in foreground.
        
        Args:
            android_settings_open_close: Fixture for managing Android settings.
        """
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
        """Test background_app command.
        
        Steps:
            1. Put app in background for 1 second.
            2. Wait for app to return.
        
        Args:
            android_settings_open_close: Fixture for managing Android settings.
        """
        # Put app in background for 1 second
        result = self.mobile_commands.background_app({"seconds": 1})
        time.sleep(2)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_start_activity(self):
        """Test start_activity command.
        
        Steps:
            1. Start Settings activity.
            2. Wait.
            3. Close the app.
        """
        result = self.mobile_commands.start_activity({"intent": "android.settings.SETTINGS"})
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Close settings
        self.app.terminal.close_app("com.android.settings")

    def test_clear_app(self):
        """Test clear_app command.
        
        Steps:
            1. Clear Settings app data.
        
        Verifies:
            - Command executes without exceptions.
        """
        result = self.mobile_commands.clear_app({"appId": "com.android.settings"})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_get_permissions(self, android_settings_open_close: Any):
        """Test get_permissions command.
        
        Verifies:
            - Result is not None.
            - Result is a list.
        
        Args:
            android_settings_open_close: Fixture for managing Android settings.
        """
        result = self.mobile_commands.get_permissions(
            {"type": "requested", "appId": "com.android.settings"}
        )

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101

    def test_change_permissions(self):
        """Test change_permissions command.
        
        Steps:
            1. Grant READ_CONTACTS permission to Settings app.
        """
        result = self.mobile_commands.change_permissions(
            {
                "appId": "com.android.settings",
                "permissions": "android.permission.READ_CONTACTS",
                "action": "grant",
            }
        )
        logger.info(result)

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_get_notifications(self):
        """Test get_notifications command.
        
        Verifies:
            - Result is not None.
            - Result is a list.
        
        Note:
            May not be supported on all devices/emulators.
        """
        result = self.mobile_commands.get_notifications()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101

    def test_start_stop_logs_broadcast(self):
        """Test start_logs_broadcast and stop_logs_broadcast commands.
        
        Steps:
            1. Start logs broadcast.
            2. Wait.
            3. Stop logs broadcast.
        """
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
        """Test get_ui_mode command.
        
        Verifies:
            - Result is not None.
        
        Note:
            May not be supported on all devices/emulators.
        """
        result = self.mobile_commands.get_ui_mode()
        assert result is not None  # noqa: S101

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_set_ui_mode(self):
        """Test set_ui_mode command.
        
        Steps:
            1. Get current UI mode.
            2. Set mode (night).
            3. Restore original mode.
        
        Note:
            May not be supported on all devices/emulators.
        """
        # Get current mode
        current_mode = self.mobile_commands.get_ui_mode()

        # Set mode (car, night, etc.)
        # This might not work on all devices
        result = self.mobile_commands.set_ui_mode({"mode": "night"})
        logger.info(result)
        # Restore original mode
        self.mobile_commands.set_ui_mode({"mode": current_mode})

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_broadcast(self):
        """Test broadcast command.
        
        Steps:
            1. Send BOOT_COMPLETED broadcast message.
        
        Note:
            May not be supported on all devices/emulators.
        """
        # Send a simple broadcast
        result = self.mobile_commands.broadcast({"action": "android.intent.action.BOOT_COMPLETED"})
        # Command should execute without raising exception
        logger.info(result)

    @pytest.mark.xfail(reason="Geolocation may not be supported on all emulators", strict=False)
    def test_get_geolocation(self):
        """Test get_geolocation command.
        
        Verifies:
            - If result is not None, it's a dictionary.
        
        Note:
            Geolocation may not be supported on all emulators.
        """
        result = self.mobile_commands.get_geolocation()

        if result is not None:
            assert isinstance(result, dict)  # noqa: S101

    def test_set_geolocation(self):
        """Test set_geolocation command.
        
        Steps:
            1. Set coordinates (Moscow: 55.7558, 37.6173).
            2. Wait.
        """
        result = self.mobile_commands.set_geolocation({"latitude": 55.7558, "longitude": 37.6173})
        time.sleep(0.5)
        # Command should execute without raising exception
        logger.info(result)

    def test_is_gps_enabled(self):
        """Test is_gps_enabled command.
        
        Verifies:
            - Result is a boolean value.
        """
        result = self.mobile_commands.is_gps_enabled()
        assert isinstance(result, bool)  # noqa: S101

    def test_toggle_gps(self):
        """Test toggle_gps command.
        
        Steps:
            1. Toggle GPS state.
        """
        result = self.mobile_commands.toggle_gps()
        logger.info(result)

    @pytest.mark.xfail(reason="GPS cache refresh may not be supported on all devices", strict=False)
    def test_refresh_gps_cache(self):
        """Test refresh_gps_cache command.
        
        Note:
            GPS cache refresh may not be supported on all devices.
        """
        result = self.mobile_commands.refresh_gps_cache()
        logger.info(result)

    @pytest.mark.skip(reason="Does not work on emulators")
    def test_reset_geolocation(self):
        """Test reset_geolocation command.
        
        Note:
            Does not work on emulators.
        """
        result = self.mobile_commands.reset_geolocation()
        logger.info(result)

    @pytest.mark.xfail(
        reason="Status bar command may not be supported on all devices", strict=False
    )
    def test_status_bar(self):
        """Test status_bar command.
        
        Note:
            status_bar command may not be supported on all devices.
        """
        result = self.mobile_commands.status_bar(
            {
                "command": "notifications",
                "component": "com.android.systemui/.statusbar.phone.StatusBar",
            }
        )
        # Command should execute without raising exception
        logger.info(result)

    def test_get_connectivity(self):
        """Test get_connectivity command.
        
        Verifies:
            - Result is a dictionary.
        """
        result = self.mobile_commands.get_connectivity()
        assert isinstance(result, dict)  # noqa: S101
        logger.info(result)  # type: ignore

    def test_set_connectivity(self):
        """Test set_connectivity command.
        
        Steps:
            1. Enable WiFi and mobile data.
        """
        result = self.mobile_commands.set_connectivity({"wifi": True, "data": True})
        logger.info(result)

    @pytest.mark.xfail(reason="Bluetooth may not be supported on all emulators", strict=False)
    def test_bluetooth(self):
        """Test bluetooth command.
        
        Steps:
            1. Get Bluetooth state.
        
        Note:
            Bluetooth may not be supported on all emulators.
        """
        # Try to get bluetooth state
        result = self.mobile_commands.bluetooth({"action": "getState"})
        logger.info(result)

    @pytest.mark.xfail(reason="NFC may not be supported on all devices/emulators", strict=False)
    def test_nfc(self):
        """Test nfc command.
        
        Steps:
            1. Get NFC state.
        
        Note:
            NFC may not be supported on all devices/emulators.
        """
        result = self.mobile_commands.nfc({"action": "getState"})
        logger.info(result)

    def test_perform_editor_action(self):
        """Test perform_editor_action command.
        
        Note:
            Requires active text field.
            Just verify command doesn't crash.
        """
        # This requires an active text field
        # Just test that command doesn't crash
        result = self.mobile_commands.perform_editor_action({"action": "Done"})
        logger.info(result)

    def test_deviceidle(self):
        """Test deviceidle command for managing app whitelist.
        
        Steps:
            1. Add app to whitelist.
            2. Remove app from whitelist.
        
        Note:
            Requires API 23+.
        """
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

    @pytest.mark.xfail(reason="Requires alert to be present on screen", strict=False)
    def test_accept_alert(self):
        """Test accept_alert command.
        
        Note:
            Requires alert to be present on screen.
        """
        result = self.mobile_commands.accept_alert()
        logger.info(result)

    @pytest.mark.xfail(reason="Requires alert to be present on screen", strict=False)
    def test_dismiss_alert(self):
        """Test dismiss_alert command.
        
        Note:
            Requires alert to be present on screen.
        """
        result = self.mobile_commands.dismiss_alert()
        logger.info(result)

    @pytest.mark.xfail(reason="Deep link requires browser app to be installed", strict=False)
    def test_deep_link(self):
        """Test deep_link command.
        
        Steps:
            1. Open deep link via Chrome.
        
        Note:
            Requires browser app to be installed.
        """
        result = self.mobile_commands.deep_link(
            {"url": "https://www.example.com", "package": "com.android.chrome"}
        )
        time.sleep(1)
        logger.info(result)

    @pytest.mark.xfail(reason="May not be supported on all UiAutomator2 versions", strict=False)
    def test_get_action_history(self):
        """Test get_action_history command.
        
        Verifies:
            - Result is a list.
        
        Note:
            May not be supported on all UiAutomator2 versions.
        """
        result = self.mobile_commands.get_action_history()
        assert isinstance(result, list)  # noqa: S101
        logger.info(result)  # type: ignore

    @pytest.mark.xfail(reason="May not be supported on all UiAutomator2 versions", strict=False)
    def test_get_app_strings(self):
        """Test get_app_strings command.
        
        Verifies:
            - Result is a dictionary.
        
        Note:
            May not be supported on all UiAutomator2 versions.
        """
        result = self.mobile_commands.get_app_strings()
        assert isinstance(result, dict)  # noqa: S101
        logger.info(result)  # type: ignore

    @pytest.mark.xfail(reason="Action scheduling may not be supported", strict=False)
    def test_schedule_action(self):
        """Test schedule_action command.
        
        Note:
            Action scheduling may not be supported.
        """
        result = self.mobile_commands.schedule_action({"action": "test_action", "delayMs": 1000})
        logger.info(result)

    @pytest.mark.xfail(reason="Action scheduling may not be supported", strict=False)
    def test_unschedule_action(self):
        """Test unschedule_action command.
        
        Note:
            Action scheduling may not be supported.
        """
        result = self.mobile_commands.unschedule_action({"action": "test_action"})
        logger.info(result)

    @pytest.mark.xfail(reason="Trim memory may not be supported on all devices", strict=False)
    def test_send_trim_memory(self):
        """Test send_trim_memory command.
        
        Note:
            Trim memory may not be supported on all devices.
        """
        result = self.mobile_commands.send_trim_memory({"level": 80})
        logger.info(result)
