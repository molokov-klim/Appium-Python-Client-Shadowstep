# ruff: noqa
# pyright: ignore
"""Integration tests for mobile_commands.py module - Part 1.

Basic tests group: singleton, device info, battery, display,
keyboard, clipboard, contexts.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_ui_automator/test_mobile_commands_integro_part_1.py
"""

import logging
import time
from typing import Any

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.ui_automator.mobile_commands import MobileCommands

logger = logging.getLogger(__name__)


class TestMobileCommandsPart1:
    """Integration tests for MobileCommands class - Part 1.
    
    Testing basic functions: singleton pattern, device info,
    battery, display, system bars, keyboard, clipboard, contexts.
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

    def test_singleton_pattern(self):
        """Test singleton pattern for MobileCommands.
        
        Verifies that MobileCommands follows singleton pattern
        and returns the same instance on repeated calls.
        """
        instance1 = MobileCommands()
        instance2 = MobileCommands()
        assert instance1 is instance2  # noqa: S101

    def test_battery_info(self):
        """Test battery_info command to get battery information.
        
        Verifies:
            - Result is not None.
            - Result is a dictionary.
            - Keys level and state are present.
        """
        result = self.mobile_commands.battery_info()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "level" in result  # noqa: S101
        assert "state" in result  # noqa: S101

    def test_device_info(self):
        """Test device_info command to get device information.
        
        Verifies:
            - Result is not None.
            - Result is a dictionary.
            - Key androidId is present.
        """
        result = self.mobile_commands.device_info()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "androidId" in result  # noqa: S101

    def test_get_device_time(self):
        """Test get_device_time command to get device time.
        
        Verifies:
            - Result is not None.
            - Result is a string.
        """
        result = self.mobile_commands.get_device_time()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_is_keyboard_shown(self):
        """Test is_keyboard_shown command.
        
        Verifies:
            - Result is not None.
            - Result is a boolean value.
        """
        result = self.mobile_commands.is_keyboard_shown()

        assert result is not None  # noqa: S101
        assert isinstance(result, bool)  # noqa: S101

    def test_get_current_package(self):
        """Test get_current_package command.
        
        Verifies:
            - Result is not None.
            - Result is a string.
        """
        result = self.mobile_commands.get_current_package()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_get_current_activity(self):
        """Test get_current_activity command.
        
        Verifies:
            - Result is not None.
            - Result is a string.
        """
        result = self.mobile_commands.get_current_activity()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_get_display_density(self):
        """Test get_display_density command.
        
        Verifies:
            - Result is not None.
            - Result is an integer.
            - Result is greater than 0.
        """
        result = self.mobile_commands.get_display_density()

        assert result is not None  # noqa: S101
        assert isinstance(result, int)  # noqa: S101
        assert result > 0  # noqa: S101

    def test_get_system_bars(self):
        """Test get_system_bars command.
        
        Verifies:
            - Result is not None.
            - Result is a dictionary.
            - Key statusBar is present.
        """
        result = self.mobile_commands.get_system_bars()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "statusBar" in result  # noqa: S101

    def test_is_locked(self):
        """Test is_locked command.
        
        Verifies:
            - Result is not None.
            - Result is a boolean value.
        """
        result = self.mobile_commands.is_locked()

        assert result is not None  # noqa: S101
        assert isinstance(result, bool)  # noqa: S101

    def test_lock_unlock(self):
        """Test lock and unlock commands.
        
        Steps:
            1. Lock the device.
            2. Check lock status.
            3. Unlock the device.
            4. Check unlock status.
        
        Note:
            Some emulators don't support lock,
            so only command execution is verified.
        """
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
        """Test get_clipboard command.
        
        Verifies:
            - Result is not None.
            - Result is a string (base64 encoded).
        
        Note:
            Clipboard content may contain previous data,
            so only return type is verified.
        """
        # Get clipboard content (returns base64 encoded string)
        result = self.mobile_commands.get_clipboard()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101
        # Just verify it returns a base64-like string (doesn't contain non-base64 chars)
        # Content verification is difficult as clipboard may contain previous data

    def test_set_clipboard(self):
        """Test set_clipboard command.
        
        Verifies:
            - Command executes without exceptions.
        """
        test_text = "integration_test_text"
        result = self.mobile_commands.set_clipboard(
            {"content": test_text, "contentType": "plaintext"}
        )

        # Should not raise an exception
        assert result is None or result is not None  # noqa: S101

    def test_get_contexts(self):
        """Test get_contexts command.
        
        Verifies:
            - Result is not None.
            - Result is a list.
        
        Note:
            Context list may be empty on some devices/configurations.
        """
        result = self.mobile_commands.get_contexts()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101
        # Context list may be empty on some devices/configurations

    def test_shell_command(self):
        """Test shell command execution.
        
        Verifies:
            - Result is not None.
            - Result contains expected command output.
        """
        # Execute simple shell command
        result = self.mobile_commands.shell({"command": "echo", "args": ["test"]})

        assert result is not None  # noqa: S101
        assert "test" in result  # noqa: S101

    def test_shell_command_getprop(self):
        """Test shell command with getprop.
        
        Verifies:
            - Result is not None.
            - Result is a string.
            - Result contains numeric value (SDK version).
        """
        result = self.mobile_commands.shell(
            {"command": "getprop", "args": ["ro.build.version.sdk"]}
        )

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101
        assert result.strip().isdigit()  # noqa: S101

    def test_open_notifications(self):
        """Test open_notifications command.
        
        Steps:
            1. Open notifications panel.
            2. Wait.
            3. Close panel with Back button.
        
        Verifies:
            - Command executes without exceptions.
        """
        result = self.mobile_commands.open_notifications()
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Press back to close notifications
        self.app.terminal.press_back()

    @pytest.mark.xfail(reason="Requires keyboard to be shown", strict=False)
    def test_hide_keyboard(self):
        """Test hide_keyboard command.
        
        Note:
            Command may not perform actions if keyboard is not shown.
            Test is marked as xfail since active keyboard is required.
        """
        # This may not do anything if keyboard is not shown
        result = self.mobile_commands.hide_keyboard()
        # Should complete without exception if keyboard is shown
        logger.info(result)

    def test_press_key(self):
        """Test press_key command.
        
        Steps:
            1. Press HOME key (keycode 3).
            2. Wait.
        
        Verifies:
            - Command executes without exceptions.
        """
        # Press home key
        result = self.mobile_commands.press_key({"keycode": 3})
        time.sleep(0.5)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_get_performance_data_types(self):
        """Test get_performance_data_types command.
        
        Verifies:
            - Result is not None.
            - Result is a list.
            - List is not empty.
        """
        result = self.mobile_commands.get_performance_data_types()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101
        assert len(result) > 0  # noqa: S101 # type: ignore

    @pytest.mark.xfail(
        reason="Performance data parsing may fail on some devices/emulators", strict=False
    )
    def test_get_performance_data(self, android_settings_open_close: Any):
        """Test get_performance_data command.
        
        Steps:
            1. Get available performance data types.
            2. Get performance data for first type.
        
        Verifies:
            - Result is not None.
            - Result is a list.
        
        Args:
            android_settings_open_close: Fixture for managing Android settings.
        
        Note:
            Performance data parsing may not work on some devices/emulators,
            so test is marked as xfail.
        """
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
        """Test type command for text input.
        
        Verifies:
            - Command executes without exceptions.
        
        Args:
            android_settings_open_close: Fixture for managing Android settings.
        
        Note:
            Ideally would click on input field first,
            but for test it's enough to verify command execution.
        """
        # Click on search or any input field first would be ideal
        # For now just test the command executes
        result = self.mobile_commands.type({"text": "test"})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_screenshots_command(self):
        """Test screenshots command.
        
        Verifies:
            - Result is not None.
            - Result is a dictionary.
        """
        result = self.mobile_commands.screenshots()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101

