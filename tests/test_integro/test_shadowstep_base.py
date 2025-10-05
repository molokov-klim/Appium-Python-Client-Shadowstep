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

from .conftest import APPIUM_IP, APPIUM_PORT, CAPABILITIES

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
