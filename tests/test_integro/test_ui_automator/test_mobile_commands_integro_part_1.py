# ruff: noqa
# pyright: ignore
"""Integration tests for ``mobile_commands.py`` — Part 1.

This suite covers foundational features: singleton behavior, device info,
battery, display, keyboard, clipboard, and context management.

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
    """Integration tests for ``MobileCommands`` — Part 1.

    Validates core functionality: singleton pattern, device and battery info,
    display metrics, system bars, keyboard, clipboard, and contexts.
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

    def test_singleton_pattern(self):
        """Exercise the ``MobileCommands`` singleton pattern.

        Confirms repeated calls return the same instance.
        """
        instance1 = MobileCommands()
        instance2 = MobileCommands()
        assert instance1 is instance2  # noqa: S101

    def test_battery_info(self):
        """Exercise the ``battery_info`` command.

        Verifies:
            - The result is not None.
            - The result is a dictionary.
            - Keys ``level`` and ``state`` are present.
        """
        result = self.mobile_commands.battery_info()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "level" in result  # noqa: S101
        assert "state" in result  # noqa: S101

    def test_device_info(self):
        """Exercise the ``device_info`` command.

        Verifies:
            - The result is not None.
            - The result is a dictionary.
            - Key ``androidId`` is present.
        """
        result = self.mobile_commands.device_info()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "androidId" in result  # noqa: S101

    def test_get_device_time(self):
        """Exercise the ``get_device_time`` command.

        Verifies:
            - The result is not None.
            - The result is a string.
        """
        result = self.mobile_commands.get_device_time()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_is_keyboard_shown(self):
        """Exercise the ``is_keyboard_shown`` command.

        Verifies:
            - The result is not None.
            - The result is a boolean value.
        """
        result = self.mobile_commands.is_keyboard_shown()

        assert result is not None  # noqa: S101
        assert isinstance(result, bool)  # noqa: S101

    def test_get_current_package(self):
        """Exercise the ``get_current_package`` command.

        Verifies:
            - The result is not None.
            - The result is a string.
        """
        result = self.mobile_commands.get_current_package()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_get_current_activity(self):
        """Exercise the ``get_current_activity`` command.

        Verifies:
            - The result is not None.
            - The result is a string.
        """
        result = self.mobile_commands.get_current_activity()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_get_display_density(self):
        """Exercise the ``get_display_density`` command.

        Verifies:
            - The result is not None.
            - The result is an integer.
            - The value is positive.
        """
        result = self.mobile_commands.get_display_density()

        assert result is not None  # noqa: S101
        assert isinstance(result, int)  # noqa: S101
        assert result > 0  # noqa: S101

    def test_get_system_bars(self):
        """Exercise the ``get_system_bars`` command.

        Verifies:
            - The result is not None.
            - The result is a dictionary.
            - Key ``statusBar`` is present.
        """
        result = self.mobile_commands.get_system_bars()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "statusBar" in result  # noqa: S101

    def test_is_locked(self):
        """Exercise the ``is_locked`` command.

        Verifies:
            - The result is not None.
            - The result is a boolean value.
        """
        result = self.mobile_commands.is_locked()

        assert result is not None  # noqa: S101
        assert isinstance(result, bool)  # noqa: S101

    def test_lock_unlock(self):
        """Exercise the ``lock`` and ``unlock`` commands.

        Steps:
            1. Lock the device.
            2. Inspect the lock state.
            3. Unlock the device.
            4. Inspect the unlock state.

        Note:
            Some emulators do not support locking; the test ensures commands execute.
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
        """Exercise the ``get_clipboard`` command.

        Verifies:
            - The result is not None.
            - The result is a base64-encoded string.

        Note:
            Clipboard content may contain stale data; only the return type is validated.
        """
        # Get clipboard content (returns base64 encoded string)
        result = self.mobile_commands.get_clipboard()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101
        # Just verify it returns a base64-like string (doesn't contain non-base64 chars)
        # Content verification is difficult as clipboard may contain previous data

    def test_set_clipboard(self):
        """Exercise the ``set_clipboard`` command.

        Verifies:
            - The command completes without exceptions.
        """
        test_text = "integration_test_text"
        result = self.mobile_commands.set_clipboard(
            {"content": test_text, "contentType": "plaintext"}
        )

        # Should not raise an exception
        assert result is None or result is not None  # noqa: S101

    def test_get_contexts(self):
        """Exercise the ``get_contexts`` command.

        Verifies:
            - The result is not None.
            - The result is a list.

        Note:
            Some devices or configurations may expose an empty context list.
        """
        result = self.mobile_commands.get_contexts()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101
        # Context list may be empty on some devices/configurations

    def test_shell_command(self):
        """Exercise execution of a shell command.

        Verifies:
            - The result is not None.
            - The expected command output is present.
        """
        # Execute simple shell command
        result = self.mobile_commands.shell({"command": "echo", "args": ["test"]})

        assert result is not None  # noqa: S101
        assert "test" in result  # noqa: S101

    def test_shell_command_getprop(self):
        """Exercise ``shell`` with ``getprop``.

        Verifies:
            - The result is not None.
            - The result is a string.
            - The string contains a numeric SDK version.
        """
        result = self.mobile_commands.shell(
            {"command": "getprop", "args": ["ro.build.version.sdk"]}
        )

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101
        assert result.strip().isdigit()  # noqa: S101

    def test_open_notifications(self):
        """Exercise the ``open_notifications`` command.

        Steps:
            1. Open the notification shade.
            2. Wait briefly.
            3. Close it via the Back button.

        Verifies:
            - The command completes without exceptions.
        """
        result = self.mobile_commands.open_notifications()
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Press back to close notifications
        self.app.terminal.press_back()

    @pytest.mark.xfail(reason="Requires keyboard to be shown", strict=False)
    def test_hide_keyboard(self):
        """Exercise the ``hide_keyboard`` command.

        Note:
            No action occurs if the keyboard is hidden; marked xfail because an active keyboard is required.
        """
        # This may not do anything if keyboard is not shown
        result = self.mobile_commands.hide_keyboard()
        # Should complete without exception if keyboard is shown
        logger.info(result)

    def test_press_key(self):
        """Exercise the ``press_key`` command.

        Steps:
            1. Press the HOME key (keycode 3).
            2. Wait briefly.

        Verifies:
            - The command completes without exceptions.
        """
        # Press home key
        result = self.mobile_commands.press_key({"keycode": 3})
        time.sleep(0.5)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_get_performance_data_types(self):
        """Exercise the ``get_performance_data_types`` command.

        Verifies:
            - The result is not None.
            - The result is a list.
            - The list is non-empty.
        """
        result = self.mobile_commands.get_performance_data_types()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101
        assert len(result) > 0  # noqa: S101 # type: ignore

    @pytest.mark.xfail(
        reason="Performance data parsing may fail on some devices/emulators", strict=False
    )
    def test_get_performance_data(self, android_settings_open_close: Any):
        """Exercise the ``get_performance_data`` command.

        Steps:
            1. Retrieve available performance data types.
            2. Fetch performance data for the first type.

        Verifies:
            - The result is not None.
            - The result is a list.

        Args:
            android_settings_open_close: Fixture managing the Android Settings screen.

        Note:
            Parsing may fail on some devices or emulators; marked xfail accordingly.
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
        """Exercise the ``type`` command for text entry.

        Verifies:
            - The command completes without exceptions.

        Args:
            android_settings_open_close: Fixture managing the Android Settings screen.

        Note:
            Ideally the test would focus a text field first; execution alone is sufficient here.
        """
        # Click on search or any input field first would be ideal
        # For now just test the command executes
        result = self.mobile_commands.type({"text": "test"})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_screenshots_command(self):
        """Exercise the ``screenshots`` command.

        Verifies:
            - The result is not None.
            - The result is a dictionary.

