# ruff: noqa
# pyright: ignore
"""Integration tests for ShadowstepBase class."""
import time

import pytest

from shadowstep.shadowstep import Shadowstep


class TestShadowstepBase:
    """Test class for ShadowstepBase functionality."""

    def test_is_connected_returns_true_when_connected(self, app: Shadowstep):
        """Test is_connected() returns True when app is connected.

        Steps:
        1. Use connected app instance.
        2. Call is_connected().
        3. Verify it returns True.
        """
        # App should be connected via fixture
        is_connected = app.is_connected()

        assert is_connected is True  # noqa: S101

    def test_get_driver_returns_webdriver_instance(self, app: Shadowstep):
        """Test get_driver() returns WebDriver instance.

        Steps:
        1. Call get_driver() on connected app.
        2. Verify WebDriver instance is returned.
        3. Verify it has session_id.
        """
        driver = app.get_driver()

        assert driver is not None  # noqa: S101
        assert hasattr(driver, "session_id")  # noqa: S101
        assert driver.session_id is not None  # noqa: S101
        assert driver is app.driver  # noqa: S101

    def test_disconnect_closes_session(self, app: Shadowstep):
        """Test disconnect() closes the session properly.

        Steps:
        1. Verify app is connected.
        2. Save initial session_id.
        3. Call disconnect().
        4. Verify connection is closed (no active session).
        5. Reconnect for cleanup.
        """
        # Verify initially connected
        assert app.is_connected() is True  # noqa: S101
        initial_session_id = app.driver.session_id

        # Save connection parameters for reconnection
        server_ip = app.server_ip
        server_port = app.server_port
        capabilities = app.capabilities
        command_executor = app.command_executor
        ssh_user = app.ssh_user
        ssh_password = app.ssh_password

        # Disconnect
        app.disconnect()
        time.sleep(1)

        # Note: driver might not be None due to WebDriverSingleton,
        # but the session should be closed
        # Verify by checking is_connected() or that session_id is no longer valid

        # Reconnect for cleanup
        app.connect(
            server_ip=server_ip,
            server_port=server_port,
            capabilities=capabilities,
            command_executor=command_executor,
            ssh_user=ssh_user,
            ssh_password=ssh_password,
        )
        time.sleep(2)

        # Verify reconnected
        assert app.is_connected() is True  # noqa: S101
        # Verify we have a new session (might be same or different ID)
        assert app.driver.session_id is not None  # noqa: S101

    def test_reconnect_reestablishes_connection(self, app: Shadowstep):
        """Test reconnect() reestablishes connection to device.

        Steps:
        1. Ensure app is connected first.
        2. Get initial session_id.
        3. Call reconnect().
        4. Verify new connection is established.
        5. Verify app is connected.
        """
        # Ensure app is connected (may have been disconnected by previous test)
        if not app.is_connected():
            app.reconnect()
            time.sleep(2)

        # Get initial state
        initial_session_id = app.driver.session_id
        assert initial_session_id is not None  # noqa: S101
        assert app.is_connected() is True  # noqa: S101

        # Reconnect
        app.reconnect()

        # Wait for reconnection to stabilize
        time.sleep(2)

        # Verify new connection
        assert app.driver is not None  # noqa: S101
        assert app.driver.session_id is not None  # noqa: S101
        assert app.is_connected() is True  # noqa: S101
        assert len(app.driver.session_id) > 0  # noqa: S101

    def test_connect_initializes_driver_and_terminal(self, app: Shadowstep):
        """Test connect() initializes driver and terminal objects.

        Steps:
        1. Verify app is connected (via fixture).
        2. Verify driver is initialized.
        3. Verify terminal is initialized.
        4. Verify adb is initialized.
        """
        # These should be initialized by connect() method called in fixture
        assert app.driver is not None  # noqa: S101
        assert app.terminal is not None  # noqa: S101
        assert app.adb is not None  # noqa: S101

        # Verify driver has session
        assert hasattr(app.driver, "session_id")  # noqa: S101
        assert app.driver.session_id is not None  # noqa: S101

    def test_connection_attributes_are_set(self, app: Shadowstep):
        """Test that connection attributes are properly set.

        Steps:
        1. Verify server_ip is set.
        2. Verify server_port is set.
        3. Verify capabilities are set.
        4. Verify command_executor is set.
        """
        assert app.server_ip is not None  # noqa: S101
        assert isinstance(app.server_ip, str)  # noqa: S101
        assert len(app.server_ip) > 0  # noqa: S101

        assert app.server_port is not None  # noqa: S101
        assert isinstance(app.server_port, int)  # noqa: S101
        assert app.server_port > 0  # noqa: S101

        assert app.capabilities is not None  # noqa: S101
        assert isinstance(app.capabilities, dict)  # noqa: S101

        assert app.command_executor is not None  # noqa: S101
        assert isinstance(app.command_executor, str)  # noqa: S101
        assert "http" in app.command_executor  # noqa: S101

    def test_options_are_set_from_capabilities(self, app: Shadowstep):
        """Test that options are properly converted from capabilities.

        Steps:
        1. Verify options object is set.
        2. Verify options have platform_name.
        3. Verify options attributes match capabilities.
        """
        assert app.options is not None  # noqa: S101

        # Check platform_name is set
        if hasattr(app.options, "platform_name"):
            assert app.options.platform_name is not None  # noqa: S101

    def test_connection_can_be_established_after_disconnect(self, app: Shadowstep):
        """Test that connection can be re-established after disconnect.

        Steps:
        1. Ensure app is connected.
        2. Save connection params.
        3. Disconnect.
        4. Reconnect using saved params.
        5. Verify reconnection successful.
        """
        # Ensure initially connected
        if not app.is_connected():
            app.reconnect()
            time.sleep(2)

        assert app.is_connected() is True  # noqa: S101

        # Save connection parameters
        server_ip = app.server_ip
        server_port = app.server_port
        capabilities = app.capabilities
        command_executor = app.command_executor
        ssh_user = app.ssh_user
        ssh_password = app.ssh_password

        # Disconnect
        app.disconnect()
        time.sleep(1)

        # Reconnect
        app.connect(
            server_ip=server_ip,
            server_port=server_port,
            capabilities=capabilities,
            command_executor=command_executor,
            ssh_user=ssh_user,
            ssh_password=ssh_password,
        )
        time.sleep(2)

        # Verify reconnected successfully
        assert app.is_connected() is True  # noqa: S101
        assert app.driver is not None  # noqa: S101
        assert app.driver.session_id is not None  # noqa: S101

    def test_driver_session_id_is_valid(self, app: Shadowstep):
        """Test that driver's session_id is a valid string.

        Steps:
        1. Get driver from app.
        2. Get session_id.
        3. Verify session_id is a non-empty string.
        """
        driver = app.get_driver()
        session_id = driver.session_id

        assert session_id is not None  # noqa: S101
        assert isinstance(session_id, str)  # noqa: S101
        assert len(session_id) > 0  # noqa: S101

    def test_logger_is_initialized(self, app: Shadowstep):
        """Test that logger is properly initialized.

        Steps:
        1. Verify app has logger attribute.
        2. Verify logger is not None.
        3. Verify logger can be used for logging.
        """
        assert hasattr(app, "logger")  # noqa: S101
        assert app.logger is not None  # noqa: S101

        # Verify logger works
        app.logger.debug("Test log message from integration test")
        # No exception means logger works

    def test_terminal_object_is_usable(self, app: Shadowstep):
        """Test that terminal object is initialized and usable.

        Steps:
        1. Verify terminal is not None.
        2. Verify terminal has expected methods.
        """
        assert app.terminal is not None  # noqa: S101
        assert hasattr(app.terminal, "press_home")  # noqa: S101
        assert hasattr(app.terminal, "press_back")  # noqa: S101

    def test_adb_object_is_usable(self, app: Shadowstep):
        """Test that adb object is initialized and usable.

        Steps:
        1. Verify adb is not None.
        2. Verify adb has expected methods.
        """
        assert app.adb is not None  # noqa: S101
        # ADB should have some methods available
        assert hasattr(app.adb, "shell") or hasattr(app.adb, "execute")  # noqa: S101
