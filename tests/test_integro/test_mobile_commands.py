# ruff: noqa
# pyright: ignore
"""
Integration tests for mobile_commands.py module.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_mobile_commands.py
"""

import pytest

from shadowstep.shadowstep import Shadowstep


class TestMobileCommands:
    """Integration tests for MobileCommands class."""

    @pytest.fixture(autouse=True)
    def setup_mobile_commands(self, app: Shadowstep):
        """Setup mobile_commands with required methods for fail_safe decorator.

        The fail_safe decorator expects is_connected() and reconnect() methods,
        but MobileCommands doesn't have them. This fixture adds them from the
        parent Shadowstep instance as a workaround for integration testing.
        """
        mobile_commands = app.mobile_commands
        return mobile_commands

    def test_mobile_commands_initialization(self, app: Shadowstep):
        """Test that MobileCommands is initialized in Shadowstep instance.

        Steps:
        1. Access mobile_commands from app.
        2. Verify initialization.
        3. Verify shadowstep reference is set.
        """
        # Access mobile_commands from app
        mobile_commands = app.mobile_commands

        # Verify initialization
        assert mobile_commands is not None, "MobileCommands should be initialized"
        assert mobile_commands.shadowstep is app, "Shadowstep reference should be set"
        assert hasattr(mobile_commands, "logger"), "Logger should be initialized"

    def test_get_current_activity_returns_self(self, app: Shadowstep):
        """Test get_current_activity returns self for method chaining.

        Steps:
        1. Call get_current_activity().
        2. Verify it returns MobileCommands instance.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.get_current_activity()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_get_current_package_returns_self(self, app: Shadowstep):
        """Test get_current_package returns self for method chaining.

        Steps:
        1. Call get_current_package().
        2. Verify it returns MobileCommands instance.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.get_current_package()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_get_device_time_returns_self(self, app: Shadowstep):
        """Test get_device_time returns self for method chaining.

        Steps:
        1. Call get_device_time().
        2. Verify it returns MobileCommands instance.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.get_device_time()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_device_info_returns_self(self, app: Shadowstep):
        """Test device_info returns self for method chaining.

        Steps:
        1. Call device_info().
        2. Verify it returns MobileCommands instance.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.device_info()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_battery_info_returns_self(self, app: Shadowstep):
        """Test battery_info returns self for method chaining.

        Steps:
        1. Call battery_info().
        2. Verify it returns MobileCommands instance.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.battery_info()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_hide_keyboard_returns_self(self, app: Shadowstep):
        """Test hide_keyboard returns self for method chaining.

        Steps:
        1. Call hide_keyboard().
        2. Verify it returns MobileCommands instance.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (may fail if keyboard not visible, but should return self)
        result = mobile_commands.hide_keyboard()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_open_notifications_returns_self(self, app: Shadowstep):
        """Test open_notifications returns self for method chaining.

        Steps:
        1. Call open_notifications().
        2. Verify it returns MobileCommands instance.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.open_notifications()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

        # Close notifications by pressing back
        app.terminal.press_back()

    def test_press_key_with_back_key(self, app: Shadowstep):
        """Test press_key with back key code.

        Steps:
        1. Call press_key with back keycode.
        2. Verify it executes without error.
        3. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method with back keycode
        params = {"keycode": 4}  # KEYCODE_BACK
        result = mobile_commands.press_key(params)

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_shell_command_returns_self(self, app: Shadowstep):
        """Test shell command executes and returns self.

        Steps:
        1. Call shell with simple command.
        2. Verify it executes without error.
        3. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method with simple shell command
        params = {"command": "echo", "args": ["test"]}
        result = mobile_commands.shell(params)

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_get_performance_data_types_returns_self(self, app: Shadowstep):
        """Test get_performance_data_types returns self.

        Steps:
        1. Call get_performance_data_types().
        2. Verify it executes without error.
        3. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.get_performance_data_types()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_method_chaining_multiple_calls(self, app: Shadowstep):
        """Test method chaining with multiple calls.

        Steps:
        1. Chain multiple mobile command calls.
        2. Verify all return self.
        3. Verify chaining works correctly.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Chain multiple calls
        result = (
            mobile_commands.get_current_activity()
            .get_current_package()
            .get_device_time()
            .device_info()
        )

        # Verify final result is still same instance
        assert result is mobile_commands, "Chained methods should return same instance"

    def test_set_clipboard_and_get_clipboard(self, app: Shadowstep):
        """Test set_clipboard and get_clipboard commands.

        Steps:
        1. Call set_clipboard with text.
        2. Call get_clipboard to retrieve.
        3. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Set clipboard
        set_result = mobile_commands.set_clipboard(
            {"content": "test content", "contentType": "plaintext"}
        )
        assert set_result is mobile_commands, "set_clipboard should return self"

        # Get clipboard
        get_result = mobile_commands.get_clipboard({"contentType": "plaintext"})
        assert get_result is mobile_commands, "get_clipboard should return self"

    def test_start_logs_broadcast_returns_self(self, app: Shadowstep):
        """Test start_logs_broadcast returns self for method chaining.

        Steps:
        1. Call start_logs_broadcast().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.start_logs_broadcast()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_stop_logs_broadcast_returns_self(self, app: Shadowstep):
        """Test stop_logs_broadcast returns self for method chaining.

        Steps:
        1. Call stop_logs_broadcast().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.stop_logs_broadcast()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_get_performance_data_returns_self(self, app: Shadowstep):
        """Test get_performance_data returns self for method chaining.

        Steps:
        1. Call get_performance_data().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        params = {"packageName": "com.android.settings", "dataType": "cpuinfo"}
        result = mobile_commands.get_performance_data(params)

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"
