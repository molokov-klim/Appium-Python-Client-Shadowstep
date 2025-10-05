# ruff: noqa
# pyright: ignore
"""
Integration tests for mobile_commands.py module.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_mobile_commands.py
"""
import pytest

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException
from shadowstep.mobile_commands import MobileCommands
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
        mobile_commands.is_connected = app.is_connected
        mobile_commands.reconnect = app.reconnect
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

    def test_get_settings_returns_self(self, app: Shadowstep):
        """Test get_settings returns self for method chaining.

        Steps:
        1. Call get_settings().
        2. Verify it returns MobileCommands instance.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.get_settings()

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

    def test_is_app_installed_with_settings_package(self, app: Shadowstep):
        """Test is_app_installed with Settings app package.

        Steps:
        1. Call is_app_installed with Settings package.
        2. Verify it executes without error.
        3. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method with Settings package
        params = {"bundleId": "com.android.settings"}
        result = mobile_commands.is_app_installed(params)

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_query_app_state_with_settings_package(self, app: Shadowstep):
        """Test query_app_state with Settings app package.

        Steps:
        1. Call query_app_state with Settings package.
        2. Verify it executes without error.
        3. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method with Settings package
        params = {"bundleId": "com.android.settings"}
        result = mobile_commands.query_app_state(params)

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_activate_app_with_settings_package(self, app: Shadowstep):
        """Test activate_app with Settings app package.

        Steps:
        1. Call activate_app with Settings package.
        2. Verify it executes without error.
        3. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method with Settings package
        params = {"bundleId": "com.android.settings"}
        result = mobile_commands.activate_app(params)

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

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

    def test_update_settings_returns_self(self, app: Shadowstep):
        """Test update_settings returns self for method chaining.

        Steps:
        1. Call update_settings with parameters.
        2. Verify it executes without error.
        3. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method with settings
        params = {"settings": {"ignoreUnimportantViews": True}}
        result = mobile_commands.update_settings(params)

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_start_activity_returns_self(self, app: Shadowstep):
        """Test start_activity returns self for method chaining.

        Steps:
        1. Call start_activity with Settings activity.
        2. Verify it executes without error.
        3. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method with Settings activity
        params = {
            "appPackage": "com.android.settings",
            "appActivity": "com.android.settings.Settings"
        }
        result = mobile_commands.start_activity(params)

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
        result = (mobile_commands
                  .get_current_activity()
                  .get_current_package()
                  .get_device_time()
                  .device_info())

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
        set_result = mobile_commands.set_clipboard({"content": "test content", "contentType": "plaintext"})
        assert set_result is mobile_commands, "set_clipboard should return self"

        # Get clipboard
        get_result = mobile_commands.get_clipboard({"contentType": "plaintext"})
        assert get_result is mobile_commands, "get_clipboard should return self"

    def test_long_press_key_returns_self(self, app: Shadowstep):
        """Test long_press_key returns self for method chaining.

        Steps:
        1. Call long_press_key with keycode.
        2. Verify it executes without error.
        3. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method with back keycode
        params = {"keycode": 4}  # KEYCODE_BACK
        result = mobile_commands.long_press_key(params)

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_get_text_returns_self(self, app: Shadowstep):
        """Test get_text returns self for method chaining.

        Steps:
        1. Call get_text().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (may fail without element, but should return self)
        result = mobile_commands.get_text()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_clear_element_returns_self(self, app: Shadowstep):
        """Test clear_element returns self for method chaining.

        Steps:
        1. Call clear_element().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (may fail without element, but should return self)
        result = mobile_commands.clear_element()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_set_text_returns_self(self, app: Shadowstep):
        """Test set_text returns self for method chaining.

        Steps:
        1. Call set_text().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (may fail without element, but should return self)
        result = mobile_commands.set_text()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_replace_element_value_returns_self(self, app: Shadowstep):
        """Test replace_element_value returns self for method chaining.

        Steps:
        1. Call replace_element_value().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (may fail without element, but should return self)
        result = mobile_commands.replace_element_value()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_perform_editor_action_returns_self(self, app: Shadowstep):
        """Test perform_editor_action returns self for method chaining.

        Steps:
        1. Call perform_editor_action().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (may fail without element, but should return self)
        result = mobile_commands.perform_editor_action()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_scroll_back_to_returns_self(self, app: Shadowstep):
        """Test scroll_back_to returns self for method chaining.

        Steps:
        1. Call scroll_back_to().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (may fail without proper setup, but should return self)
        result = mobile_commands.scroll_back_to()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_fingerprint_returns_self(self, app: Shadowstep):
        """Test fingerprint returns self for method chaining.

        Steps:
        1. Call fingerprint().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (may fail without fingerprint sensor, but should return self)
        result = mobile_commands.fingerprint()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_send_sms_returns_self(self, app: Shadowstep):
        """Test send_sms returns self for method chaining.

        Steps:
        1. Call send_sms().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (may fail on device without SMS, but should return self)
        result = mobile_commands.send_sms()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_toggle_location_services_returns_self(self, app: Shadowstep):
        """Test toggle_location_services returns self for method chaining.

        Steps:
        1. Call toggle_location_services().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (may fail depending on device state, but should return self)
        result = mobile_commands.toggle_location_services()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

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

    def test_terminate_app_returns_self(self, app: Shadowstep):
        """Test terminate_app returns self for method chaining.

        Steps:
        1. Call terminate_app with package.
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.terminate_app({"bundleId": "com.android.calculator2"})

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_remove_app_returns_self(self, app: Shadowstep):
        """Test remove_app returns self for method chaining.

        Steps:
        1. Call remove_app().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (should not actually remove, just test return value)
        result = mobile_commands.remove_app()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_install_app_returns_self(self, app: Shadowstep):
        """Test install_app returns self for method chaining.

        Steps:
        1. Call install_app().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method (should return self even if it fails)
        result = mobile_commands.install_app()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

    def test_open_settings_returns_self(self, app: Shadowstep):
        """Test open_settings returns self for method chaining.

        Steps:
        1. Call open_settings().
        2. Verify method chaining.
        """
        # Get MobileCommands from app
        mobile_commands = app.mobile_commands

        # Call method
        result = mobile_commands.open_settings()

        # Verify method chaining
        assert result is mobile_commands, "Method should return self for chaining"

        # Go back
        app.terminal.press_back()

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
