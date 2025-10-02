import logging
import time

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    WebDriverException,
)

from conftest import CAPABILITIES, APPIUM_IP, APPIUM_PORT
from shadowstep.shadowstep import Shadowstep

logger = logging.getLogger(__name__)

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/base/test_shadowstep_base.py
"""


class TestBase:

    def test_webdriver_singleton_creation(self, app: Shadowstep):
        """Test WebDriverSingleton creation and reuse"""
        # Get the current driver instance
        current_driver = app.driver
        
        # Create a new Shadowstep instance - it should reuse the same driver
        app2 = Shadowstep()
        app2.connect(server_ip=APPIUM_IP,
                     server_port=APPIUM_PORT,
                     capabilities=CAPABILITIES)
        
        # Both instances should have the same driver (singleton pattern)
        assert app2.driver is not None  # noqa: S101
        assert app.driver is not None  # noqa: S101

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

    def test_appium_disconnected_error_initialization(self):
        """Test AppiumDisconnectedError initialization with parameters."""
        from shadowstep.shadowstep_base import AppiumDisconnectedError
        
        error = AppiumDisconnectedError("Test error", "screenshot_data", ["trace1", "trace2"])
        assert error.msg == "Test error"
        assert error.screen == "screenshot_data"
        assert error.stacktrace == ["trace1", "trace2"]

    def test_appium_disconnected_error_default_initialization(self):
        """Test AppiumDisconnectedError initialization with default parameters."""
        from shadowstep.shadowstep_base import AppiumDisconnectedError
        
        error = AppiumDisconnectedError()
        assert error.msg is None
        assert error.screen is None
        assert error.stacktrace is None

    def test_webdriver_singleton_get_session_id_with_sessions(self):
        """Test WebDriverSingleton._get_session_id with available sessions."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        from unittest.mock import patch, Mock
        
        mock_response = Mock()
        mock_response.text = '{"value": [{"id": "session123"}]}'
        
        with patch('requests.get', return_value=mock_response):
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "session123"

    def test_webdriver_singleton_get_session_id_no_sessions(self):
        """Test WebDriverSingleton._get_session_id with no sessions."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        from unittest.mock import patch, Mock
        
        mock_response = Mock()
        mock_response.text = '{"value": []}'
        
        with patch('requests.get', return_value=mock_response):
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "unknown_session_id"

    def test_webdriver_singleton_get_session_id_no_value_key(self):
        """Test WebDriverSingleton._get_session_id with no value key."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        from unittest.mock import patch, Mock
        
        mock_response = Mock()
        mock_response.text = '{"other": []}'
        
        with patch('requests.get', return_value=mock_response):
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "unknown_session_id"

    def test_webdriver_singleton_clear_instance(self):
        """Test WebDriverSingleton.clear_instance method."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        
        # Set some values
        WebDriverSingleton._instance = "test_instance"
        WebDriverSingleton._driver = "test_driver"
        
        WebDriverSingleton.clear_instance()
        
        assert WebDriverSingleton._instance is None
        assert WebDriverSingleton._driver is None

    def test_webdriver_singleton_get_driver(self):
        """Test WebDriverSingleton.get_driver method."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        from unittest.mock import patch
        
        with patch('shadowstep.shadowstep_base.cast') as mock_cast:
            mock_cast.return_value = "test_driver"
            WebDriverSingleton._driver = "test_driver"
            
            result = WebDriverSingleton.get_driver()
            assert result == "test_driver"
            mock_cast.assert_called_once_with("WebDriver", "test_driver")

    def test_shadowstep_base_initialization(self):
        """Test ShadowstepBase initialization."""
        from shadowstep.shadowstep_base import ShadowstepBase
        
        base = ShadowstepBase()
        assert base.logger is not None
        assert base.driver is None
        assert base.server_ip is None
        assert base.server_port is None
        assert base.capabilities is None
        assert base.options is None
        assert base.extensions is None
        assert base.ssh_password is None
        assert base.ssh_user is None
        assert base.ssh_port == 22
        assert base.command_executor is None
        assert base.transport is None
        assert base.terminal is None
        assert base.adb is None
        assert isinstance(base._ignored_auto_discover_dirs, set)
        assert isinstance(base._ignored_base_path_parts, set)

    def test_get_driver_method(self, app: Shadowstep):
        """Test get_driver method."""
        from unittest.mock import patch
        
        with patch('shadowstep.shadowstep_base.WebDriverSingleton.get_driver') as mock_get_driver:
            mock_get_driver.return_value = "test_driver"
            result = app.get_driver()
            assert result == "test_driver"
            mock_get_driver.assert_called_once()

    def test_is_session_active_on_grid_success(self, app: Shadowstep):
        """Test _is_session_active_on_grid with successful response."""
        from unittest.mock import patch, Mock
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": {
                "nodes": [{
                    "slots": [{
                        "session": {
                            "sessionId": app.driver.session_id
                        }
                    }]
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get', return_value=mock_response):
            result = app._is_session_active_on_grid()
            assert result is True

    def test_is_session_active_on_grid_no_session(self, app: Shadowstep):
        """Test _is_session_active_on_grid with no matching session."""
        from unittest.mock import patch, Mock
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": {
                "nodes": [{
                    "slots": [{
                        "session": {
                            "sessionId": "different_session_id"
                        }
                    }]
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get', return_value=mock_response):
            result = app._is_session_active_on_grid()
            assert result is False

    def test_is_session_active_on_grid_exception(self, app: Shadowstep):
        """Test _is_session_active_on_grid with exception."""
        from unittest.mock import patch
        
        with patch('requests.get', side_effect=Exception("Network error")):
            result = app._is_session_active_on_grid()
            assert result is False

    def test_is_session_active_on_standalone_success(self, app: Shadowstep):
        """Test _is_session_active_on_standalone with successful response."""
        from unittest.mock import patch, Mock
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": [{
                "id": app.driver.session_id,
                "ready": True
            }]
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get', return_value=mock_response):
            result = app._is_session_active_on_standalone()
            assert result is True

    def test_is_session_active_on_standalone_no_match(self, app: Shadowstep):
        """Test _is_session_active_on_standalone with no matching session."""
        from unittest.mock import patch, Mock
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": [{
                "id": "different_session_id",
                "ready": True
            }]
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get', return_value=mock_response):
            result = app._is_session_active_on_standalone()
            assert result is False

    def test_is_session_active_on_standalone_exception(self, app: Shadowstep):
        """Test _is_session_active_on_standalone with exception."""
        from unittest.mock import patch
        
        with patch('requests.get', side_effect=Exception("Network error")):
            result = app._is_session_active_on_standalone()
            assert result is False

    def test_is_session_active_on_standalone_new_style_success(self, app: Shadowstep):
        """Test _is_session_active_on_standalone_new_style with successful response."""
        from unittest.mock import patch, Mock
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": [{
                "id": app.driver.session_id,
                "ready": True
            }]
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get', return_value=mock_response):
            result = app._is_session_active_on_standalone_new_style()
            assert result is True

    def test_is_session_active_on_standalone_new_style_no_match(self, app: Shadowstep):
        """Test _is_session_active_on_standalone_new_style with no matching session."""
        from unittest.mock import patch, Mock
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": [{
                "id": "different_session_id",
                "ready": True
            }]
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get', return_value=mock_response):
            result = app._is_session_active_on_standalone_new_style()
            assert result is False

    def test_is_session_active_on_standalone_new_style_exception(self, app: Shadowstep):
        """Test _is_session_active_on_standalone_new_style with exception."""
        from unittest.mock import patch
        
        with patch('requests.get', side_effect=Exception("Network error")):
            result = app._is_session_active_on_standalone_new_style()
            assert result is False

    def test_wait_for_session_id_success(self, app: Shadowstep):
        """Test _wait_for_session_id with successful session ID assignment."""
        from unittest.mock import patch, MagicMock
        
        mock_driver = MagicMock()
        mock_driver.session_id = 'test_session_id'
        with patch.object(app, 'driver', mock_driver):
            with patch('time.time', side_effect=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
                with patch('time.sleep'):
                    # Should not raise exception
                    result = app._wait_for_session_id(timeout=5)
                    assert result == 'test_session_id'

    def test_wait_for_session_id_timeout(self, app: Shadowstep):
        """Test _wait_for_session_id with timeout."""
        from unittest.mock import patch, MagicMock
        import pytest
        
        mock_driver = MagicMock()
        mock_driver.session_id = None
        with patch.object(app, 'driver', mock_driver):
            with patch('time.time', side_effect=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
                with patch('time.sleep'):
                    with patch('shadowstep.shadowstep_base.WebDriverSingleton.get_driver', return_value=mock_driver):
                        with pytest.raises(RuntimeError, match="WebDriver session_id was not assigned in time"):
                            app._wait_for_session_id(timeout=5)

    def test_capabilities_to_options_general_settings(self, app: Shadowstep):
        """Test _capabilities_to_options with general settings."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "platformName": "Android",
            "appium:automationName": "uiautomator2",
            "appium:deviceName": "Test Device",
            "appium:platformVersion": "11",
            "appium:UDID": "test_udid",
            "appium:noReset": True,
            "appium:fullReset": False,
            "appium:printPageSourceOnFindFailure": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.platform_name == "Android"
        assert app.options.automation_name == "UIAutomator2"
        assert app.options.device_name == "Test Device"
        assert app.options.platform_version == "11"
        assert app.options.udid == "test_udid"
        assert app.options.no_reset is True
        assert app.options.full_reset is False
        assert app.options.print_page_source_on_find_failure is True

    def test_capabilities_to_options_app_settings(self, app: Shadowstep):
        """Test _capabilities_to_options with app settings."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:app": "/path/to/app.apk",
            "browserName": "Chrome",
            "appium:appPackage": "com.test.app",
            "appium:appActivity": ".MainActivity",
            "appium:appWaitActivity": ".SplashActivity",
            "appium:appWaitPackage": "com.test.app",
            "appium:appWaitDuration": 30000,
            "appium:androidInstallTimeout": 60000,
            "appium:appWaitForLaunch": True,
            "appium:intentCategory": "android.intent.category.LAUNCHER",
            "appium:intentAction": "android.intent.action.MAIN",
            "appium:intentFlags": "0x10200000",
            "appium:optionalIntentArguments": "--es test_key test_value",
            "appium:autoGrantPermissions": True,
            "appium:otherApps": ["/path/to/other.apk"],
            "appium:uninstallOtherPackages": ["com.other.app"],
            "appium:allowTestPackages": True,
            "appium:remoteAppsCacheLimit": 10,
            "appium:enforceAppInstall": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.app == "/path/to/app.apk"
        assert app.options.browser_name == "Chrome"
        assert app.options.app_package == "com.test.app"
        assert app.options.app_activity == ".MainActivity"
        assert app.options.app_wait_activity == ".SplashActivity"
        assert app.options.app_wait_package == "com.test.app"
        from datetime import timedelta
        assert app.options.app_wait_duration == timedelta(seconds=30)
        assert app.options.android_install_timeout == timedelta(seconds=60)
        assert app.options.app_wait_for_launch is True
        assert app.options.intent_category == "android.intent.category.LAUNCHER"
        assert app.options.intent_action == "android.intent.action.MAIN"
        assert app.options.intent_flags == "0x10200000"
        assert app.options.optional_intent_arguments == "--es test_key test_value"
        assert app.options.auto_grant_permissions is True
        assert app.options.other_apps == ["/path/to/other.apk"]
        assert app.options.uninstall_other_packages == ["com.other.app"]
        assert app.options.allow_test_packages is True
        assert app.options.remote_apps_cache_limit == 10
        assert app.options.enforce_app_install is True

    def test_capabilities_to_options_no_capabilities(self, app: Shadowstep):
        """Test _capabilities_to_options with no capabilities."""
        app.capabilities = None
        app.options = None
        app._capabilities_to_options()
        
        assert app.options is None

    def test_capabilities_to_options_with_existing_options(self, app: Shadowstep):
        """Test _capabilities_to_options with existing options."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        existing_options = UiAutomator2Options()
        existing_options.platform_name = "iOS"
        
        app.capabilities = {"platformName": "Android"}
        app.options = existing_options
        app._capabilities_to_options()
        
        # Should not modify existing options
        assert app.options is existing_options
        assert app.options.platform_name == "iOS"

    def test_get_ignored_dirs(self, app: Shadowstep):
        """Test _get_ignored_dirs method."""
        from unittest.mock import patch
        
        with patch('sys.base_prefix', '/usr/local/python'):
            with patch('site.getsitepackages', return_value=['/usr/local/python/lib/python3.9/site-packages']):
                with patch('sys.path', ['/usr/local/python/lib/python3.9/site-packages', '/usr/local/python/lib']):
                    result = app._get_ignored_dirs()
                    assert isinstance(result, set)
                    assert 'venv' in result
                    assert '.venv' in result
                    assert '__pycache__' in result

    def test_connect_with_ssh_credentials(self, app: Shadowstep):
        """Test connect method with SSH credentials."""
        from unittest.mock import patch, MagicMock
        
        # Disconnect first
        app.disconnect()
        
        # Mock the WebDriver and Transport
        with patch('shadowstep.shadowstep_base.WebDriverSingleton') as mock_singleton:
            with patch('shadowstep.shadowstep_base.Transport') as mock_transport:
                with patch('shadowstep.shadowstep_base.Terminal') as mock_terminal:
                    with patch('shadowstep.shadowstep_base.Adb') as mock_adb:
                        mock_driver = MagicMock()
                        mock_driver.session_id = 'test_session_id'
                        mock_singleton.return_value = mock_driver
                        
                        app.connect(
                            capabilities=CAPABILITIES,
                            server_ip="127.0.0.1",
                            server_port=4723,
                            ssh_user="test_user",
                            ssh_password="test_password"
                        )
                        
                        # Verify SSH transport was created
                        mock_transport.assert_called_once_with(
                            server="127.0.0.1",
                            port=22,
                            user="test_user",
                            password="test_password"
                        )
                        mock_terminal.assert_called_once()
                        mock_adb.assert_called_once()

    def test_disconnect_with_invalid_session_exception(self, app: Shadowstep):
        """Test disconnect method with InvalidSessionIdException."""
        from unittest.mock import patch, MagicMock
        
        # Mock driver and requests.delete to raise InvalidSessionIdException
        mock_driver = MagicMock()
        mock_driver.session_id = 'test_session_id'
        app.driver = mock_driver
        
        with patch('requests.delete', side_effect=InvalidSessionIdException("Invalid session")):
            app.disconnect()
            # Should not raise exception, just log debug message

    def test_disconnect_with_no_such_driver_exception(self, app: Shadowstep):
        """Test disconnect method with NoSuchDriverException."""
        from unittest.mock import patch, MagicMock
        
        # Mock driver and requests.delete to raise NoSuchDriverException
        mock_driver = MagicMock()
        mock_driver.session_id = 'test_session_id'
        app.driver = mock_driver
        
        with patch('requests.delete', side_effect=NoSuchDriverException("No such driver")):
            app.disconnect()
            # Should not raise exception, just log debug message

    def test_is_session_active_on_grid_no_slots(self, app: Shadowstep):
        """Test _is_session_active_on_grid with nodes but no slots."""
        from unittest.mock import patch, Mock
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": {
                "nodes": [{
                    "slots": []
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get', return_value=mock_response):
            result = app._is_session_active_on_grid()
            assert result is False

    def test_is_session_active_on_grid_no_session_in_slot(self, app: Shadowstep):
        """Test _is_session_active_on_grid with slots but no session."""
        from unittest.mock import patch, Mock
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": {
                "nodes": [{
                    "slots": [{
                        "session": None
                    }]
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get', return_value=mock_response):
            result = app._is_session_active_on_grid()
            assert result is False

    def test_capabilities_to_options_udid_lowercase(self, app: Shadowstep):
        """Test _capabilities_to_options with lowercase udid."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:udid": "test_udid_lowercase"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.udid == "test_udid_lowercase"

    def test_capabilities_to_options_system_port(self, app: Shadowstep):
        """Test _capabilities_to_options with system port."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:systemPort": 8201
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.system_port == 8201

    def test_capabilities_to_options_skip_server_installation(self, app: Shadowstep):
        """Test _capabilities_to_options with skip server installation."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:skipServerInstallation": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.skip_server_installation is True

    def test_capabilities_to_options_uiautomator2_server_launch_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with uiautomator2 server launch timeout."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        from datetime import timedelta
        
        capabilities = {
            "appium:uiautomator2ServerLaunchTimeout": 60000
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.uiautomator2_server_launch_timeout == timedelta(seconds=60)

    def test_capabilities_to_options_uiautomator2_server_install_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with uiautomator2 server install timeout."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        from datetime import timedelta
        
        capabilities = {
            "appium:uiautomator2ServerInstallTimeout": 60000
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.uiautomator2_server_install_timeout == timedelta(seconds=60)

    def test_capabilities_to_options_uiautomator2_server_read_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with uiautomator2 server read timeout."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        from datetime import timedelta
        
        capabilities = {
            "appium:uiautomator2ServerReadTimeout": 60000
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.uiautomator2_server_read_timeout == timedelta(seconds=60)

    def test_capabilities_to_options_disable_window_animation(self, app: Shadowstep):
        """Test _capabilities_to_options with disable window animation."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:disableWindowAnimation": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.disable_window_animation is True

    def test_capabilities_to_options_skip_device_initialization(self, app: Shadowstep):
        """Test _capabilities_to_options with skip device initialization."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:skipDeviceInitialization": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.skip_device_initialization is True

    def test_capabilities_to_options_locale_script(self, app: Shadowstep):
        """Test _capabilities_to_options with locale script."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:localeScript": "Latn"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.locale_script == "Latn"

    def test_capabilities_to_options_language(self, app: Shadowstep):
        """Test _capabilities_to_options with language."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:language": "en"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.language == "en"

    def test_capabilities_to_options_locale(self, app: Shadowstep):
        """Test _capabilities_to_options with locale."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:locale": "en_US"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.locale == "en_US"

    def test_capabilities_to_options_adb_port(self, app: Shadowstep):
        """Test _capabilities_to_options with adb port."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:adbPort": 5037
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.adb_port == 5037

    def test_capabilities_to_options_remote_adb_host(self, app: Shadowstep):
        """Test _capabilities_to_options with remote adb host."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:remoteAdbHost": "192.168.1.100"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.remote_adb_host == "192.168.1.100"

    def test_capabilities_to_options_adb_exec_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with adb exec timeout."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        from datetime import timedelta
        
        capabilities = {
            "appium:adbExecTimeout": 60000
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.adb_exec_timeout == timedelta(seconds=60)

    def test_capabilities_to_options_clear_device_logs_on_start(self, app: Shadowstep):
        """Test _capabilities_to_options with clear device logs on start."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:clearDeviceLogsOnStart": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.clear_device_logs_on_start is True

    def test_capabilities_to_options_build_tools_version(self, app: Shadowstep):
        """Test _capabilities_to_options with build tools version."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:buildToolsVersion": "30.0.3"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.build_tools_version == "30.0.3"

    def test_capabilities_to_options_skip_logcat_capture(self, app: Shadowstep):
        """Test _capabilities_to_options with skip logcat capture."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:skipLogcatCapture": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.skip_logcat_capture is True

    def test_capabilities_to_options_suppress_kill_server(self, app: Shadowstep):
        """Test _capabilities_to_options with suppress kill server."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:suppressKillServer": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.suppress_kill_server is True

    def test_capabilities_to_options_ignore_hidden_api_policy_error(self, app: Shadowstep):
        """Test _capabilities_to_options with ignore hidden api policy error."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:ignoreHiddenApiPolicyError": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.ignore_hidden_api_policy_error is True

    def test_capabilities_to_options_mock_location_app(self, app: Shadowstep):
        """Test _capabilities_to_options with mock location app."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:mockLocationApp": "com.example.mocklocation"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.mock_location_app == "com.example.mocklocation"

    def test_capabilities_to_options_logcat_format(self, app: Shadowstep):
        """Test _capabilities_to_options with logcat format."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:logcatFormat": "time"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.logcat_format == "time"

    def test_capabilities_to_options_logcat_filter_specs(self, app: Shadowstep):
        """Test _capabilities_to_options with logcat filter specs."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:logcatFilterSpecs": ["*:V"]
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.logcat_filter_specs == ["*:V"]

    def test_capabilities_to_options_allow_delay_adb(self, app: Shadowstep):
        """Test _capabilities_to_options with allow delay adb."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:allowDelayAdb": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.allow_delay_adb is True

    def test_capabilities_to_options_avd(self, app: Shadowstep):
        """Test _capabilities_to_options with avd."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:avd": "test_avd"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.avd == "test_avd"

    def test_capabilities_to_options_avd_launch_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with avd launch timeout."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        from datetime import timedelta
        
        capabilities = {
            "appium:avdLaunchTimeout": 120000
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.avd_launch_timeout == timedelta(seconds=120)

    def test_capabilities_to_options_avd_ready_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with avd ready timeout."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        from datetime import timedelta
        
        capabilities = {
            "appium:avdReadyTimeout": 120000
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.avd_ready_timeout == timedelta(seconds=120)

    def test_capabilities_to_options_avd_args(self, app: Shadowstep):
        """Test _capabilities_to_options with avd args."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:avdArgs": "-no-snapshot-load"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.avd_args == "-no-snapshot-load"

    def test_capabilities_to_options_avd_env(self, app: Shadowstep):
        """Test _capabilities_to_options with avd env."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:avdEnv": {"ANDROID_HOME": "/path/to/android"}
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.avd_env == {"ANDROID_HOME": "/path/to/android"}

    def test_capabilities_to_options_network_speed(self, app: Shadowstep):
        """Test _capabilities_to_options with network speed."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:networkSpeed": "full"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.network_speed == "full"

    def test_capabilities_to_options_gps_enabled(self, app: Shadowstep):
        """Test _capabilities_to_options with gps enabled."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:gpsEnabled": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.gps_enabled is True

    def test_capabilities_to_options_is_headless(self, app: Shadowstep):
        """Test _capabilities_to_options with is headless."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:isHeadless": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.is_headless is True

    def test_capabilities_to_options_use_keystore(self, app: Shadowstep):
        """Test _capabilities_to_options with use keystore."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:useKeystore": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.use_keystore is True

    def test_capabilities_to_options_keystore_path(self, app: Shadowstep):
        """Test _capabilities_to_options with keystore path."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:keystorePath": "/path/to/keystore"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.keystore_path == "/path/to/keystore"

    def test_capabilities_to_options_keystore_password(self, app: Shadowstep):
        """Test _capabilities_to_options with keystore password."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:keystorePassword": "password123"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.keystore_password == "password123"

    def test_capabilities_to_options_key_alias(self, app: Shadowstep):
        """Test _capabilities_to_options with key alias."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:keyAlias": "mykey"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.key_alias == "mykey"

    def test_capabilities_to_options_key_password(self, app: Shadowstep):
        """Test _capabilities_to_options with key password."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:keyPassword": "keypass123"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.key_password == "keypass123"

    def test_capabilities_to_options_no_sign(self, app: Shadowstep):
        """Test _capabilities_to_options with no sign."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:noSign": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.no_sign is True

    def test_capabilities_to_options_skip_unlock(self, app: Shadowstep):
        """Test _capabilities_to_options with skip unlock."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:skipUnlock": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.skip_unlock is True

    def test_capabilities_to_options_unlock_type(self, app: Shadowstep):
        """Test _capabilities_to_options with unlock type."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:unlockType": "pin"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.unlock_type == "pin"

    def test_capabilities_to_options_unlock_key(self, app: Shadowstep):
        """Test _capabilities_to_options with unlock key."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:unlockKey": "1234"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.unlock_key == "1234"

    def test_capabilities_to_options_unlock_strategy(self, app: Shadowstep):
        """Test _capabilities_to_options with unlock strategy."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:unlockStrategy": "locksettings"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.unlock_strategy == "locksettings"

    def test_capabilities_to_options_unlock_success_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with unlock success timeout."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        from datetime import timedelta
        
        capabilities = {
            "appium:unlockSuccessTimeout": 30000
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.unlock_success_timeout == timedelta(seconds=30)

    def test_capabilities_to_options_mjpeg_server_port(self, app: Shadowstep):
        """Test _capabilities_to_options with mjpeg server port."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:mjpegServerPort": 8080
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.mjpeg_server_port == 8080

    def test_capabilities_to_options_mjpeg_screenshot_url(self, app: Shadowstep):
        """Test _capabilities_to_options with mjpeg screenshot url."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:mjpegScreenshotUrl": "http://localhost:8080/screenshot"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.mjpeg_screenshot_url == "http://localhost:8080/screenshot"

    def test_capabilities_to_options_auto_webview(self, app: Shadowstep):
        """Test _capabilities_to_options with auto webview."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:autoWebview": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.auto_web_view is True

    def test_capabilities_to_options_auto_webview_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with auto webview timeout."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        from datetime import timedelta
        
        capabilities = {
            "appium:autoWebviewTimeout": 30000
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.auto_webview_timeout == timedelta(seconds=30)

    def test_capabilities_to_options_webview_devtools_port(self, app: Shadowstep):
        """Test _capabilities_to_options with webview devtools port."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:webviewDevtoolsPort": 9222
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.webview_devtools_port == 9222

    def test_capabilities_to_options_ensure_webviews_have_pages(self, app: Shadowstep):
        """Test _capabilities_to_options with ensure webviews have pages."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:ensureWebviewsHavePages": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.ensure_webviews_have_pages is True

    def test_capabilities_to_options_chromedriver_port(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver port."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:chromedriverPort": 9515
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_port == 9515

    def test_capabilities_to_options_chromedriver_ports(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver ports."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:chromedriverPorts": [9515, 9516]
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_ports == [9515, 9516]

    def test_capabilities_to_options_chromedriver_args(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver args."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:chromedriverArgs": ["--no-sandbox"]
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_args == ["--no-sandbox"]

    def test_capabilities_to_options_chromedriver_executable(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver executable."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:chromedriverExecutable": "/path/to/chromedriver"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_executable == "/path/to/chromedriver"

    def test_capabilities_to_options_chromedriver_executable_dir(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver executable dir."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:chromedriverExecutableDir": "/path/to/chromedriver/dir"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_executable_dir == "/path/to/chromedriver/dir"

    def test_capabilities_to_options_chromedriver_chrome_mapping_file(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver chrome mapping file."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:chromedriverChromeMappingFile": "/path/to/mapping.json"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_chrome_mapping_file == "/path/to/mapping.json"

    def test_capabilities_to_options_chromedriver_use_system_executable(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver use system executable."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:chromedriverUseSystemExecutable": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_use_system_executable is True

    def test_capabilities_to_options_chromedriver_disable_build_check(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver disable build check."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:chromedriverDisableBuildCheck": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_disable_build_check is True

    def test_capabilities_to_options_recreate_chrome_driver_sessions(self, app: Shadowstep):
        """Test _capabilities_to_options with recreate chrome driver sessions."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:recreateChromeDriverSessions": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.recreate_chrome_driver_sessions is True

    def test_capabilities_to_options_native_web_screenshot(self, app: Shadowstep):
        """Test _capabilities_to_options with native web screenshot."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:nativeWebScreenshot": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.native_web_screenshot is True

    def test_capabilities_to_options_extract_chrome_android_package_from_context_name(self, app: Shadowstep):
        """Test _capabilities_to_options with extract chrome android package from context name."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:extractChromeAndroidPackageFromContextName": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.extract_chrome_android_package_from_context_name is True

    def test_capabilities_to_options_show_chromedriver_log(self, app: Shadowstep):
        """Test _capabilities_to_options with show chromedriver log."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:showChromedriverLog": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.show_chromedriver_log is True

    def test_capabilities_to_options_page_load_strategy(self, app: Shadowstep):
        """Test _capabilities_to_options with page load strategy."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "pageLoadStrategy": "eager"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.page_load_strategy == "eager"

    def test_capabilities_to_options_chrome_options(self, app: Shadowstep):
        """Test _capabilities_to_options with chrome options."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:chromeOptions": {"args": ["--no-sandbox"]}
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chrome_options == {"args": ["--no-sandbox"]}

    def test_capabilities_to_options_chrome_logging_prefs(self, app: Shadowstep):
        """Test _capabilities_to_options with chrome logging prefs."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:chromeLoggingPrefs": {"browser": "ALL"}
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chrome_logging_prefs == {"browser": "ALL"}

    def test_capabilities_to_options_disable_suppress_accessibility_service(self, app: Shadowstep):
        """Test _capabilities_to_options with disable suppress accessibility service."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:disableSuppressAccessibilityService": True
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.disable_suppress_accessibility_service is True

    def test_capabilities_to_options_user_profile(self, app: Shadowstep):
        """Test _capabilities_to_options with user profile."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        
        capabilities = {
            "appium:userProfile": "test_profile"
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.user_profile == "test_profile"

    def test_capabilities_to_options_new_command_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with new command timeout."""
        from appium.options.android.uiautomator2.base import UiAutomator2Options
        from datetime import timedelta
        
        capabilities = {
            "appium:newCommandTimeout": 300
        }
        
        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()
        
        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.new_command_timeout == timedelta(seconds=300)

    def test_get_ignored_dirs_with_exception(self, app: Shadowstep):
        """Test _get_ignored_dirs with path resolution exception."""
        from unittest.mock import patch, MagicMock
        from pathlib import Path

        # Mock Path.resolve to raise an exception for specific paths
        original_resolve = Path.resolve
        
        def mock_resolve(self):
            if str(self) == '/problematic/path':
                raise Exception("Path resolution failed")
            return original_resolve(self)
        
        with patch('pathlib.Path.resolve', mock_resolve):
            with patch('sys.path', ['/problematic/path']):
                result = app._get_ignored_dirs()
                assert isinstance(result, set)
                # Should still return the basic ignored names even if path resolution fails
                assert 'venv' in result
                assert '.venv' in result
                assert '__pycache__' in result

    def test_get_ignored_dirs_with_path_resolution_exception(self, app: Shadowstep):
        """Test _get_ignored_dirs with path resolution exception in is_system_path."""
        from unittest.mock import patch, MagicMock
        from pathlib import Path

        # Mock Path.resolve to raise an exception for specific paths
        original_resolve = Path.resolve
        
        def mock_resolve(self):
            if str(self) == '/problematic/path':
                raise Exception("Path resolution failed")
            return original_resolve(self)
        
        with patch('pathlib.Path.resolve', mock_resolve):
            with patch('sys.path', ['/problematic/path']):
                result = app._get_ignored_dirs()
                assert isinstance(result, set)
                # Should still return the basic ignored names even if path resolution fails
                assert 'venv' in result
                assert '.venv' in result
                assert '__pycache__' in result
