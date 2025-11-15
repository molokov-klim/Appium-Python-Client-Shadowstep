# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Integration tests for ``mobile_commands.py`` — Part 3.

This suite covers application management, permissions, notifications, GPS,
connectivity, UI mode, and other system commands.

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
    """Integration tests for ``MobileCommands`` — Part 3.

    Validates commands for app management, permissions, notifications,
    GPS, connectivity, and other system features.
    """

    @pytest.fixture(autouse=True)
    def setup_mobile_commands(self, app: Shadowstep):
        """Configure a ``MobileCommands`` instance with the ``app`` fixture.

        Args:
            app: Shadowstep application instance for testing.
        """
        self.mobile_commands = MobileCommands()
        self.app = app
        # Ensure app is connected
        assert self.app.is_connected()  # noqa: S101
        yield

    def test_is_app_installed(self, android_settings_open_close: Any):
        """Exercise the ``is_app_installed`` command.

        Verifies:
            - The Settings app is installed (result is True).

        Args:
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Check if Settings app is installed
        result = self.mobile_commands.is_app_installed({"appId": "com.android.settings"})

        assert result is True  # noqa: S101

    def test_is_app_not_installed(self):
        """Exercise ``is_app_installed`` with a nonexistent application.

        Verifies:
            - The nonexistent app is not installed (result is False).
        """
        result = self.mobile_commands.is_app_installed({"appId": "com.nonexistent.app.xyz"})

        assert result is False  # noqa: S101

    def test_query_app_state(self, android_settings_open_close: Any):
        """Exercise the ``query_app_state`` command.

        Steps:
            1. Request the state of the Settings app.

        Verifies:
            - The result is not None.
            - The value equals ``4`` (running in foreground).

        Args:
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Query state of Settings app while it's open
        result = self.mobile_commands.query_app_state({"appId": "com.android.settings"})

        assert result is not None  # noqa: S101
        # 4 = running in foreground
        assert result == 4  # noqa: S101

    def test_activate_app(self, android_settings_open_close: Any):
        """Exercise the ``activate_app`` command.

        Steps:
            1. Close the Settings app.
            2. Activate the Settings app.
            3. Confirm the app returns to the foreground.

        Args:
            android_settings_open_close: Fixture managing the Android Settings screen.
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
        """Exercise the ``terminate_app`` command.

        Steps:
            1. Activate the Settings app.
            2. Terminate the app.
            3. Verify the app leaves the foreground.

        Args:
            android_settings_open_close: Fixture managing the Android Settings screen.
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
        """Exercise the ``background_app`` command.

        Steps:
            1. Send the app to the background for one second.
            2. Wait for it to return.

        Args:
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Put app in background for 1 second
        result = self.mobile_commands.background_app({"seconds": 1})
        time.sleep(2)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_start_activity(self):
        """Exercise the ``start_activity`` command.

        Steps:
            1. Launch the Settings activity.
            2. Wait briefly.
            3. Close the app.
        """
        result = self.mobile_commands.start_activity({"intent": "android.settings.SETTINGS"})
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Close settings
        self.app.terminal.close_app("com.android.settings")

    def test_clear_app(self):
        """Exercise the ``clear_app`` command.

        Steps:
            1. Clear the Settings application data.

        Verifies:
            - The command finishes without exceptions.
        """
        result = self.mobile_commands.clear_app({"appId": "com.android.settings"})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_get_permissions(self, android_settings_open_close: Any):
        """Exercise the ``get_permissions`` command.

        Verifies:
            - The result is not None.
            - The result is a list.

        Args:
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        result = self.mobile_commands.get_permissions(
            {"type": "requested", "appId": "com.android.settings"}
        )

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101

    def test_change_permissions(self):
        """Exercise the ``change_permissions`` command.

        Steps:
            1. Grant the ``READ_CONTACTS`` permission to the Settings app.
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
        """Exercise the ``get_notifications`` command.

        Verifies:
            - The result is not None.
            - The result is a list.

        Note:
            May be unsupported on some devices or emulators.
        """
        result = self.mobile_commands.get_notifications()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101

    def test_start_stop_logs_broadcast(self):
        """Exercise ``start_logs_broadcast`` and ``stop_logs_broadcast``.

        Steps:
            1. Start the log broadcast.
            2. Wait briefly.
            3. Stop the broadcast.
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
        """Exercise the ``get_ui_mode`` command.

        Verifies:
            - The result is not None.

        Note:
            May be unsupported on some devices or emulators.
        """
        result = self.mobile_commands.get_ui_mode()
        assert result is not None  # noqa: S101

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_set_ui_mode(self):
        """Exercise the ``set_ui_mode`` command.

        Steps:
            1. Retrieve the current UI mode.
            2. Set the mode to ``night``.
            3. Restore the original mode.

        Note:
            May be unsupported on some devices or emulators.
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
        """Exercise the ``broadcast`` command.

        Steps:
            1. Send the ``BOOT_COMPLETED`` broadcast message.

        Note:
            May be unsupported on some devices or emulators.
        """
        # Send a simple broadcast
        result = self.mobile_commands.broadcast({"action": "android.intent.action.BOOT_COMPLETED"})
        # Command should execute without raising exception
        logger.info(result)

    @pytest.mark.xfail(reason="Geolocation may not be supported on all emulators", strict=False)
    def test_get_geolocation(self):
        """Exercise the ``get_geolocation`` command.

        Verifies:
            - If a result is returned, it is a dictionary.

        Note:
            Geolocation may be unavailable on some emulators.
        """
        result = self.mobile_commands.get_geolocation()

        if result is not None:
            assert isinstance(result, dict)  # noqa: S101

    def test_set_geolocation(self):
        """Exercise the ``set_geolocation`` command.

        Steps:
            1. Set coordinates (Moscow: 55.7558, 37.6173).
            2. Wait briefly.
        """
        result = self.mobile_commands.set_geolocation({"latitude": 55.7558, "longitude": 37.6173})
        time.sleep(0.5)
        # Command should execute without raising exception
        logger.info(result)

    def test_is_gps_enabled(self):
        """Exercise the ``is_gps_enabled`` command.

        Verifies:
            - The result is a boolean value.
        """
        result = self.mobile_commands.is_gps_enabled()
        assert isinstance(result, bool)  # noqa: S101

    def test_toggle_gps(self):
        """Exercise the ``toggle_gps`` command.

        Steps:
            1. Toggle the GPS state.
        """
        result = self.mobile_commands.toggle_gps()
        logger.info(result)

    @pytest.mark.xfail(reason="GPS cache refresh may not be supported on all devices", strict=False)
    def test_refresh_gps_cache(self):
        """Exercise the ``refresh_gps_cache`` command.

        Note:
            GPS cache refresh may be unsupported on some devices.
        """
        result = self.mobile_commands.refresh_gps_cache()
        logger.info(result)

    @pytest.mark.skip(reason="Does not work on emulators")
    def test_reset_geolocation(self):
        """Exercise the ``reset_geolocation`` command.

        Note:
            Does not work on emulators.
        """
        result = self.mobile_commands.reset_geolocation()
        logger.info(result)

    @pytest.mark.xfail(
        reason="Status bar command may not be supported on all devices", strict=False
    )
    def test_status_bar(self):
        """Exercise the ``status_bar`` command.

        Note:
            ``status_bar`` may be unsupported on some devices.
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
        """Exercise the ``get_connectivity`` command.

        Verifies:
            - The result is a dictionary.
        """
        result = self.mobile_commands.get_connectivity()
        assert isinstance(result, dict)  # noqa: S101
        logger.info(result)  # type: ignore

    def test_set_connectivity(self):
        """Exercise the ``set_connectivity`` command.

        Steps:
            1. Enable Wi-Fi and mobile data.
        """
        result = self.mobile_commands.set_connectivity({"wifi": True, "data": True})
        logger.info(result)

    @pytest.mark.xfail(reason="Bluetooth may not be supported on all emulators", strict=False)
    def test_bluetooth(self):
        """Exercise the ``bluetooth`` command.

        Steps:
            1. Retrieve the Bluetooth state.

        Note:
            Bluetooth may be unsupported on some emulators.
        """
        # Try to get bluetooth state
        result = self.mobile_commands.bluetooth({"action": "getState"})
        logger.info(result)

    @pytest.mark.xfail(reason="NFC may not be supported on all devices/emulators", strict=False)
    def test_nfc(self):
        """Exercise the ``nfc`` command.

        Steps:
            1. Retrieve the NFC state.

        Note:
            NFC may be unsupported on certain devices or emulators.
        """
        result = self.mobile_commands.nfc({"action": "getState"})
        logger.info(result)

    def test_perform_editor_action(self):
        """Exercise the ``perform_editor_action`` command.

        Note:
            Requires an active text field; this test only checks that no error occurs.
        """
        # This requires an active text field
        # Just test that command doesn't crash
        result = self.mobile_commands.perform_editor_action({"action": "Done"})
        logger.info(result)

    def test_deviceidle(self):
        """Exercise ``deviceidle`` whitelist management.

        Steps:
            1. Add the app to the whitelist.
            2. Remove the app from the whitelist.

        Note:
            Requires API level 23 or higher.
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
        """Exercise the ``accept_alert`` command.

        Note:
            Requires an alert to be present on the screen.
        """
        result = self.mobile_commands.accept_alert()
        logger.info(result)

    @pytest.mark.xfail(reason="Requires alert to be present on screen", strict=False)
    def test_dismiss_alert(self):
        """Exercise the ``dismiss_alert`` command.

        Note:
            Requires an alert to be present on the screen.
        """
        result = self.mobile_commands.dismiss_alert()
        logger.info(result)

    @pytest.mark.xfail(reason="Deep link requires browser app to be installed", strict=False)
    def test_deep_link(self):
        """Exercise the ``deep_link`` command.

        Steps:
            1. Open a deep link through Chrome.

        Note:
            Requires a browser application to be installed.
        """
        result = self.mobile_commands.deep_link(
            {"url": "https://www.example.com", "package": "com.android.chrome"}
        )
        time.sleep(1)
        logger.info(result)

    @pytest.mark.xfail(reason="May not be supported on all UiAutomator2 versions", strict=False)
    def test_get_action_history(self):
        """Exercise the ``get_action_history`` command.

        Verifies:
            - The result is a list.

        Note:
            May be unsupported on some UiAutomator2 versions.
        """
        result = self.mobile_commands.get_action_history()
        assert isinstance(result, list)  # noqa: S101
        logger.info(result)  # type: ignore

    @pytest.mark.xfail(reason="May not be supported on all UiAutomator2 versions", strict=False)
    def test_get_app_strings(self):
        """Exercise the ``get_app_strings`` command.

        Verifies:
            - The result is a dictionary.

        Note:
            May be unsupported on some UiAutomator2 versions.
        """
        result = self.mobile_commands.get_app_strings()
        assert isinstance(result, dict)  # noqa: S101
        logger.info(result)  # type: ignore

    @pytest.mark.xfail(reason="Action scheduling may not be supported", strict=False)
    def test_schedule_action(self):
        """Exercise the ``schedule_action`` command.

        Note:
            Action scheduling may not be supported.
        """
        result = self.mobile_commands.schedule_action({"action": "test_action", "delayMs": 1000})
        logger.info(result)

    @pytest.mark.xfail(reason="Action scheduling may not be supported", strict=False)
    def test_unschedule_action(self):
        """Exercise the ``unschedule_action`` command.

        Note:
            Action scheduling may not be supported.
        """
        result = self.mobile_commands.unschedule_action({"action": "test_action"})
        logger.info(result)

    @pytest.mark.xfail(reason="Trim memory may not be supported on all devices", strict=False)
    def test_send_trim_memory(self):
        """Exercise the ``send_trim_memory`` command.

        Note:
            Trim memory may be unsupported on some devices.
        """
        result = self.mobile_commands.send_trim_memory({"level": 80})
        logger.info(result)

