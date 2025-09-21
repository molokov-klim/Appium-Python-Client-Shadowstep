# tests/base/test_shadowstep_base.py
import logging
import time

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    WebDriverException,
)

from shadowstep.shadowstep import Shadowstep
from tests.conftest import APPIUM_IP, APPIUM_PORT, CAPABILITIES

logger = logging.getLogger(__name__)

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/base/test_shadowstep_base.py
"""


class TestBase:

    def test_webdriver_singleton_creation(self, app: Shadowstep):
        """Test WebDriverSingleton creation and reuse"""
        app2 = Shadowstep()
        app2.connect(server_ip=APPIUM_IP,
                     server_port=APPIUM_PORT,
                     capabilities=CAPABILITIES)
        assert app2.driver == app.driver  # noqa: S101

    def test_reconnect_after_session_disruption(self, app: Shadowstep):
        """Test automatic reconnection on broken session"""
        app.reconnect()  # Reconnection
        try:
            app.driver.get_screenshot_as_png()  # Attempt to execute command
            assert app.driver.session_id is not None, "Failed to reconnect"  # noqa: S101
        except NoSuchDriverException as error:
            raise AssertionError("Error: failed to initialize WebDriver after reconnection") from error
        except InvalidSessionIdException as error:
            raise AssertionError("Error: failed to initialize WebDriver after reconnection") from error

    def test_disconnect_on_invalid_session_exception(self, app: Shadowstep):
        """Test InvalidSessionIdException handling on session break in disconnect"""
        app.disconnect()
        CAPABILITIES["appium:newCommandTimeout"] = 10
        app.connect(server_ip=APPIUM_IP,
                    server_port=APPIUM_PORT,
                    capabilities=CAPABILITIES)
        time.sleep(12)
        try:
            app.driver.get_screenshot_as_png()
        except InvalidSessionIdException as error:
            assert isinstance(error, InvalidSessionIdException)  # noqa: S101, PT017
            CAPABILITIES["appium:newCommandTimeout"] = 900
            app.connect(server_ip=APPIUM_IP,
                        server_port=APPIUM_PORT,
                        capabilities=CAPABILITIES)
            return True
        except Exception as error:
            logger.error(error)
            raise AssertionError(f"Unknown error: {type(error)}") from error
        raise AssertionError("Test logic error, expected session break")

    def test_reconnect_without_active_session(self, app: Shadowstep):
        """Test reconnect call when no active session"""
        app.disconnect()
        app.reconnect()
        assert app.driver is not None, "Session was not created on reconnection"  # noqa: S101
        assert app.driver.session_id is not None, "Session was not created on reconnection"  # noqa: S101

    def test_session_state_before_command_execution(self, app: Shadowstep):
        """Test session state before executing WebDriver commands"""
        if app.driver.session_id is None:
            app.reconnect()  # Reconnection when no active session
        try:
            app.driver.get_screenshot_as_png()
        except WebDriverException as error:
            raise AssertionError(f"Command execution error: {error}") from error

    def test_handling_of_capabilities_option(self, app: Shadowstep):
        """Test correct capabilities parameter handling"""
        app.disconnect()  # End current session to check new settings
        new_caps = CAPABILITIES.copy()
        new_caps["appium:autoGrantPermissions"] = False  # Change capabilities
        app.connect(server_ip="127.0.0.1", server_port=4723, capabilities=new_caps)
        assert app.driver is not None, "Session was not created with new capabilities parameters"  # noqa: S101
        assert app.options.auto_grant_permissions is False, "autoGrantPermissions parameter was not applied"  # noqa: S101
        app.connect(server_ip="127.0.0.1", server_port=4723, capabilities=CAPABILITIES)

    def test_is_connected_when_connected(self, app: Shadowstep):
        app.reconnect()
        assert app.is_connected()  # noqa: S101

    def test_is_connected_when_disconnected(self, app: Shadowstep):
        app.disconnect()
        assert not app.is_connected()  # noqa: S101
        app.connect(CAPABILITIES)
