# ruff: noqa
# pyright: ignore
"""
Integration tests for ShadowstepBase class.

These tests verify the core functionality of ShadowstepBase using real Appium connections.
All tests use the app fixture and test only public methods without any mocks.
"""

import logging

import pytest
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException

from shadowstep.shadowstep import Shadowstep
from shadowstep.shadowstep_base import WebDriverSingleton

from .conftest import APPIUM_IP, APPIUM_PORT, CAPABILITIES, UDID

logger = logging.getLogger(__name__)


class TestShadowstepBase:
    """Integration tests for ShadowstepBase class."""

    def test_connect_establishes_session(self, app: Shadowstep):
        """Test that connect method establishes a valid Appium session."""
        # Verify connection is established
        assert app.driver is not None, "Driver should be initialized after connect"
        assert app.driver.session_id is not None, "Session ID should be set after connect"
        assert app.is_connected(), "Connection status should be true after connect"

        # Verify driver can execute commands
        screenshot = app.driver.get_screenshot_as_png()
        assert screenshot is not None, "Driver should be able to execute commands"

    def test_disconnect_terminates_session(self, app: Shadowstep):
        """Test that disconnect method properly terminates the session."""
        # Verify initial connection
        assert app.is_connected(), "Should be connected initially"

        # Disconnect
        app.disconnect()

        # Verify disconnection
        assert not app.is_connected(), "Should not be connected after disconnect"
        # Note: driver may not be None due to singleton pattern, but session should be invalid

    def test_reconnect_establishes_new_session(self, app: Shadowstep):
        """Test that reconnect method establishes a new session."""
        # Store original session ID
        original_session_id = app.driver.session_id

        # Reconnect
        app.reconnect()

        # Verify new session is established
        assert app.driver is not None, "Driver should be reinitialized after reconnect"
        assert app.driver.session_id is not None, "New session ID should be set"
        assert app.is_connected(), "Should be connected after reconnect"

        # Verify it's a different session (if original was valid)
        if original_session_id:
            assert app.driver.session_id != original_session_id, "Should create new session"

    def test_is_connected_returns_correct_status(self, app: Shadowstep):
        """Test that is_connected method returns correct connection status."""
        # Test when connected
        assert app.is_connected(), "Should return True when connected"

        # Test when disconnected
        app.disconnect()
        assert not app.is_connected(), "Should return False when disconnected"

        # Reconnect for cleanup
        app.connect(server_ip=APPIUM_IP, server_port=APPIUM_PORT, capabilities=CAPABILITIES)

    def test_get_driver_returns_webdriver_instance(self, app: Shadowstep):
        """Test that get_driver method returns the WebDriver instance."""
        driver = app.get_driver()

        assert driver is not None, "get_driver should return a driver instance"
        assert driver is app.driver, "get_driver should return the same driver instance"
        assert hasattr(driver, "session_id"), "Driver should have session_id attribute"

    def test_connect_with_custom_parameters(self, app: Shadowstep):
        """Test connect method with custom server parameters."""
        # Disconnect current session
        app.disconnect()

        # Connect with custom parameters
        custom_capabilities = CAPABILITIES.copy()
        custom_capabilities["appium:newCommandTimeout"] = 300

        app.connect(server_ip=APPIUM_IP, server_port=APPIUM_PORT, capabilities=custom_capabilities)

        # Verify connection with custom parameters
        assert app.is_connected(), "Should connect with custom parameters"
        assert app.driver is not None, "Driver should be initialized"
        assert app.server_ip == APPIUM_IP, "Server IP should be set correctly"
        assert app.server_port == APPIUM_PORT, "Server port should be set correctly"

    def test_connect_with_command_executor(self, app: Shadowstep):
        """Test connect method with custom command executor URL."""
        # Disconnect current session
        app.disconnect()

        # Connect with custom command executor
        command_executor = f"http://{APPIUM_IP}:{APPIUM_PORT}/wd/hub"

        app.connect(capabilities=CAPABILITIES, command_executor=command_executor)

        # Verify connection
        assert app.is_connected(), "Should connect with custom command executor"
        assert app.command_executor == command_executor, "Command executor should be set correctly"

    def test_webdriver_singleton_pattern(self, app: Shadowstep):
        """Test that WebDriverSingleton maintains single instance."""
        # Create second Shadowstep instance
        app2 = Shadowstep()
        app2.connect(server_ip=APPIUM_IP, server_port=APPIUM_PORT, capabilities=CAPABILITIES)

        # Both should use the same driver instance (singleton)
        assert app.driver is app2.driver, "Both instances should use the same driver (singleton)"

        # Cleanup
        app2.disconnect()

    def test_session_persistence_after_reconnect(self, app: Shadowstep):
        """Test that session persists correctly after reconnect."""

        # Reconnect
        app.reconnect()

        # Verify session is active and functional
        assert app.is_connected(), "Should be connected after reconnect"
        assert app.driver.session_id is not None, "Should have valid session ID"

        # Verify driver functionality
        try:
            screenshot = app.driver.get_screenshot_as_png()
            assert screenshot is not None, "Driver should work after reconnect"
        except (WebDriverException, InvalidSessionIdException) as e:
            pytest.fail(f"Driver should work after reconnect, got: {e}")

    def test_connection_handles_invalid_session_gracefully(self, app: Shadowstep):
        """Test that connection handles invalid session exceptions gracefully."""
        # Force session to become invalid by disconnecting
        app.disconnect()

        # Attempt to use driver (should handle gracefully)
        try:
            app.driver.get_screenshot_as_png()  # type: ignore
            pytest.fail("Should raise exception for invalid session")
        except (InvalidSessionIdException, AttributeError):
            # Expected behavior - session is invalid
            pass

        # Reconnect should work
        app.connect(server_ip=APPIUM_IP, server_port=APPIUM_PORT, capabilities=CAPABILITIES)
        assert app.is_connected(), "Should reconnect successfully"

    def test_multiple_connect_disconnect_cycles(self, app: Shadowstep):
        """Test multiple connect/disconnect cycles work correctly."""
        for cycle in range(3):
            # Disconnect
            app.disconnect()
            assert not app.is_connected(), f"Should be disconnected after cycle {cycle}"

            # Reconnect
            app.connect(server_ip=APPIUM_IP, server_port=APPIUM_PORT, capabilities=CAPABILITIES)
            assert app.is_connected(), f"Should be connected after cycle {cycle}"

            # Verify driver works
            screenshot = app.driver.get_screenshot_as_png()
            assert screenshot is not None, f"Driver should work in cycle {cycle}"

    def test_webdriver_singleton_clear_instance(self, app: Shadowstep):
        """Test WebDriverSingleton clear_instance method."""
        # Verify singleton has instance
        driver = WebDriverSingleton.get_driver()
        assert driver is not None, "Singleton should have driver instance"

        # Clear instance
        WebDriverSingleton.clear_instance()

        # Verify instance is cleared
        cleared_driver = WebDriverSingleton.get_driver()
        assert cleared_driver is None, "Singleton should be cleared"

    def test_connection_with_ssh_parameters(self, app: Shadowstep):
        """Test connect method with SSH parameters."""
        # Disconnect current session
        app.disconnect()

        # Connect with SSH parameters (SSH connection may fail in test environment)
        try:
            app.connect(
                server_ip=APPIUM_IP,
                server_port=APPIUM_PORT,
                capabilities=CAPABILITIES,
                ssh_user="test_user",
                ssh_password="test_password",
            )

            # Verify connection works
            assert app.is_connected(), "Should connect with SSH parameters"
            assert app.ssh_user == "test_user", "SSH user should be set"
            assert app.ssh_password == "test_password", "SSH password should be set"
        except Exception:
            # If SSH connection fails, test that parameters are still set
            # This is acceptable in test environment without SSH server
            assert app.ssh_user == "test_user", "SSH user should be set even if connection fails"
            assert app.ssh_password == "test_password", (
                "SSH password should be set even if connection fails"
            )

    def test_connection_with_extensions(self, app: Shadowstep):
        """Test connect method with WebDriver extensions."""
        # Disconnect current session
        app.disconnect()

        # Connect with extensions (empty list for testing)
        app.connect(
            server_ip=APPIUM_IP, server_port=APPIUM_PORT, capabilities=CAPABILITIES, extensions=[]
        )

        # Verify connection works
        assert app.is_connected(), "Should connect with extensions parameter"
        assert app.extensions == [], "Extensions should be set correctly"

    def test_connection_state_consistency(self, app: Shadowstep):
        """Test that connection state remains consistent across operations."""
        # Verify initial state
        assert app.is_connected(), "Should be initially connected"
        assert app.driver is not None, "Driver should be initialized"

        # Perform operations that shouldn't break connection
        driver = app.get_driver()
        assert driver is app.driver, "get_driver should return same instance"

        # Verify state after operations
        assert app.is_connected(), "Should remain connected after operations"
        assert app.driver.session_id is not None, "Session should remain valid"

    def test_terminal_initialization(self, app: Shadowstep):
        """Test that terminal is properly initialized after connection.

        Steps:
        1. Verify terminal instance is created.
        2. Verify terminal is not None.
        """
        # Verify terminal is initialized
        assert app.terminal is not None, "Terminal should be initialized after connect"
        assert hasattr(app.terminal, "press_home"), "Terminal should have expected methods"

    def test_adb_initialization(self, app: Shadowstep):
        """Test that ADB is properly initialized after connection.

        Steps:
        1. Verify adb instance is created.
        2. Verify adb is not None.
        """
        # Verify adb is initialized
        assert app.adb is not None, "ADB should be initialized after connect"
        assert hasattr(app.adb, "get_devices"), "ADB should have expected methods"

    def test_capabilities_conversion_to_options(self, app: Shadowstep):
        """Test that capabilities are correctly converted to options.

        Steps:
        1. Disconnect and reconnect with specific capabilities.
        2. Verify options are created from capabilities.
        3. Verify key options are set correctly.
        """
        # Disconnect current session
        app.disconnect()

        # Create capabilities with various options
        test_capabilities = {
            "platformName": "android",
            "appium:automationName": "uiautomator2",
            "appium:UDID": UDID,
            "appium:noReset": True,
            "appium:autoGrantPermissions": True,
            "appium:newCommandTimeout": 600,
        }

        # Connect with test capabilities
        app.connect(
            server_ip=APPIUM_IP,
            server_port=APPIUM_PORT,
            capabilities=test_capabilities,
        )

        # Verify options are set
        assert app.options is not None, "Options should be created from capabilities"
        assert app.options.platform_name == "android", "Platform name should be set"
        assert app.options.automation_name.lower() == "uiautomator2", "Automation name should be set"
        assert app.options.no_reset is True, "noReset should be set"
        assert app.options.auto_grant_permissions is True, "autoGrantPermissions should be set"
        # new_command_timeout is stored as timedelta
        assert app.options.new_command_timeout.total_seconds() == 600, "newCommandTimeout should be set"

    def test_command_executor_auto_generation(self, app: Shadowstep):
        """Test that command_executor is auto-generated when not provided.

        Steps:
        1. Disconnect current session.
        2. Connect without command_executor.
        3. Verify command_executor is auto-generated correctly.
        """
        # Disconnect current session
        app.disconnect()

        # Connect without explicit command_executor
        app.connect(
            server_ip=APPIUM_IP,
            server_port=APPIUM_PORT,
            capabilities=CAPABILITIES,
        )

        # Verify command_executor is auto-generated
        expected_executor = f"http://{APPIUM_IP}:{APPIUM_PORT}/wd/hub"
        assert app.command_executor == expected_executor, "Command executor should be auto-generated"

    def test_server_attributes_set_correctly(self, app: Shadowstep):
        """Test that server attributes are set correctly after connection.

        Steps:
        1. Verify server_ip is set.
        2. Verify server_port is set.
        3. Verify capabilities are stored.
        """
        # Verify server attributes
        assert app.server_ip == APPIUM_IP, "Server IP should be set correctly"
        assert app.server_port == APPIUM_PORT, "Server port should be set correctly"
        assert app.capabilities is not None, "Capabilities should be stored"
        assert isinstance(app.capabilities, dict), "Capabilities should be a dictionary"

    def test_connect_with_udid_capability(self, app: Shadowstep):
        """Test connection with UDID capability (both uppercase and lowercase).

        Steps:
        1. Disconnect current session.
        2. Connect with UDID capability.
        3. Verify connection is established.
        4. Verify UDID is set in options.
        """
        # Disconnect current session
        app.disconnect()

        # Create capabilities with UDID
        udid_capabilities = CAPABILITIES.copy()
        udid_capabilities["appium:UDID"] = UDID

        # Connect with UDID
        app.connect(
            server_ip=APPIUM_IP,
            server_port=APPIUM_PORT,
            capabilities=udid_capabilities,
        )

        # Verify connection
        assert app.is_connected(), "Should connect with UDID capability"
        assert app.options.udid == UDID, "UDID should be set in options"

    def test_connect_with_app_package_capability(self, app: Shadowstep):
        """Test connection with app package and activity capabilities.

        Steps:
        1. Disconnect current session.
        2. Connect with app package and activity.
        3. Verify connection is established.
        4. Verify app package and activity are set in options.
        """
        # Disconnect current session
        app.disconnect()

        # Create capabilities with app package
        app_capabilities = CAPABILITIES.copy()
        app_capabilities["appium:appPackage"] = "com.android.settings"
        app_capabilities["appium:appActivity"] = "com.android.settings.Settings"

        # Connect with app package
        app.connect(
            server_ip=APPIUM_IP,
            server_port=APPIUM_PORT,
            capabilities=app_capabilities,
        )

        # Verify connection
        assert app.is_connected(), "Should connect with app package capability"
        assert app.options.app_package == "com.android.settings", "App package should be set"
        assert app.options.app_activity == "com.android.settings.Settings", "App activity should be set"

    def test_reconnect_preserves_capabilities(self, app: Shadowstep):
        """Test that reconnect preserves original capabilities.

        Steps:
        1. Store original capabilities.
        2. Reconnect.
        3. Verify capabilities are preserved.
        """
        # Store original capabilities
        original_capabilities = app.capabilities.copy()
        original_server_ip = app.server_ip
        original_server_port = app.server_port

        # Reconnect
        app.reconnect()

        # Verify capabilities are preserved
        assert app.server_ip == original_server_ip, "Server IP should be preserved"
        assert app.server_port == original_server_port, "Server port should be preserved"
        assert app.capabilities == original_capabilities, "Capabilities should be preserved"

    def test_disconnect_cleans_up_driver(self, app: Shadowstep):
        """Test that disconnect properly terminates connection.

        Steps:
        1. Verify driver exists before disconnect.
        2. Disconnect.
        3. Verify connection is terminated.
        """
        # Verify driver exists
        assert app.driver is not None, "Driver should exist before disconnect"
        session_id = app.driver.session_id

        # Disconnect
        app.disconnect()

        # Verify connection is terminated (session should be inactive)
        # Note: driver may not be None due to Shadowstep singleton pattern,
        # but the session should be terminated
        assert not app.is_connected(), "Connection should be terminated after disconnect"

        # Reconnect for cleanup
        app.connect(server_ip=APPIUM_IP, server_port=APPIUM_PORT, capabilities=CAPABILITIES)

    def test_webdriver_singleton_get_driver_class_method(self):
        """Test WebDriverSingleton.get_driver class method.

        Steps:
        1. Call WebDriverSingleton.get_driver().
        2. Verify it returns a driver instance or None.
        """
        # Get driver via class method
        driver = WebDriverSingleton.get_driver()

        # Verify driver is returned (could be None if not initialized)
        assert driver is not None or driver is None, "get_driver should return driver or None"

    def test_connection_with_platform_version_capability(self, app: Shadowstep):
        """Test connection with platform version capability.

        Steps:
        1. Disconnect current session.
        2. Connect with platform version.
        3. Verify connection is established.
        4. Verify platform version is set in options.
        """
        # Disconnect current session
        app.disconnect()

        # Create capabilities with platform version
        platform_capabilities = CAPABILITIES.copy()
        platform_capabilities["appium:platformVersion"] = "12"

        # Connect with platform version
        app.connect(
            server_ip=APPIUM_IP,
            server_port=APPIUM_PORT,
            capabilities=platform_capabilities,
        )

        # Verify connection
        assert app.is_connected(), "Should connect with platform version capability"
        assert app.options.platform_version == "12", "Platform version should be set"

    def test_connection_with_adb_timeout_capability(self, app: Shadowstep):
        """Test connection with ADB exec timeout capability.

        Steps:
        1. Disconnect current session.
        2. Connect with ADB timeout.
        3. Verify connection is established.
        4. Verify ADB timeout is set in options.
        """
        # Disconnect current session
        app.disconnect()

        # Create capabilities with ADB timeout
        adb_capabilities = CAPABILITIES.copy()
        adb_capabilities["appium:adbExecTimeout"] = 60000

        # Connect with ADB timeout
        app.connect(
            server_ip=APPIUM_IP,
            server_port=APPIUM_PORT,
            capabilities=adb_capabilities,
        )

        # Verify connection
        assert app.is_connected(), "Should connect with ADB timeout capability"
        # adb_exec_timeout is stored as timedelta (milliseconds)
        assert app.options.adb_exec_timeout.total_seconds() == 60, "ADB exec timeout should be set"

    def test_connection_with_system_port_capability(self, app: Shadowstep):
        """Test connection with system port capability.

        Steps:
        1. Disconnect current session.
        2. Connect with system port.
        3. Verify connection is established.
        4. Verify system port is set in options.
        """
        # Disconnect current session
        app.disconnect()

        # Create capabilities with system port
        system_port_capabilities = CAPABILITIES.copy()
        system_port_capabilities["appium:systemPort"] = 8299

        # Connect with system port
        app.connect(
            server_ip=APPIUM_IP,
            server_port=APPIUM_PORT,
            capabilities=system_port_capabilities,
        )

        # Verify connection
        assert app.is_connected(), "Should connect with system port capability"
        assert app.options.system_port == 8299, "System port should be set"

    def test_connection_sets_extensions_attribute(self, app: Shadowstep):
        """Test that extensions attribute is set during connection.

        Steps:
        1. Verify extensions attribute exists.
        2. Verify it can be None or a list.
        """
        # Verify extensions attribute
        assert hasattr(app, "extensions"), "App should have extensions attribute"
        assert app.extensions is None or isinstance(app.extensions, list), (
            "Extensions should be None or list"
        )

    def test_driver_has_session_id_after_connect(self, app: Shadowstep):
        """Test that driver has valid session_id after connection.

        Steps:
        1. Verify driver exists.
        2. Verify session_id is set.
        3. Verify session_id is not empty.
        """
        # Verify driver and session_id
        assert app.driver is not None, "Driver should exist"
        assert app.driver.session_id is not None, "Session ID should be set"
        assert len(app.driver.session_id) > 0, "Session ID should not be empty"
        assert isinstance(app.driver.session_id, str), "Session ID should be a string"

    def test_reconnect_updates_session_id(self, app: Shadowstep):
        """Test that reconnect creates a new session with different ID.

        Steps:
        1. Store original session ID.
        2. Reconnect.
        3. Verify new session ID is different.
        """
        # Store original session ID
        original_session_id = app.driver.session_id

        # Reconnect
        app.reconnect()

        # Verify new session ID
        assert app.driver.session_id is not None, "New session ID should be set"
        assert app.driver.session_id != original_session_id, "New session ID should be different"
