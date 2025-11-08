# ruff: noqa
# pyright: ignore
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock

import pytest
from selenium.common.exceptions import InvalidSessionIdException, NoSuchDriverException

from shadowstep.shadowstep import Shadowstep

# Test capabilities for testing
CAPABILITIES = {"platformName": "Android", "deviceName": "test_device", "app": "test_app.apk"}

app = Shadowstep()


class TestShadowstepBaseUnit:
    def test_get_driver_method(self):
        """Test get_driver method."""

        with patch("shadowstep.shadowstep_base.WebDriverSingleton.get_driver") as mock_get_driver:
            mock_get_driver.return_value = "test_driver"
            result = app.get_driver()
            assert result == "test_driver"
            mock_get_driver.assert_called_once()

    def test_is_session_active_on_grid_success(self):
        """Test _is_session_active_on_grid with successful response."""

        mock_driver = Mock()
        mock_driver.session_id = "test_session_id"
        app.driver = mock_driver

        mock_response = Mock()
        mock_response.json.return_value = {
            "value": {"nodes": [{"slots": [{"session": {"sessionId": "test_session_id"}}]}]}
        }
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.return_value = mock_response
            result = app._is_session_active_on_grid()
            assert result is True

    def test_is_session_active_on_grid_no_session(self):
        """Test _is_session_active_on_grid with no matching session."""

        mock_response = Mock()
        mock_response.json.return_value = {
            "value": {"nodes": [{"slots": [{"session": {"sessionId": "different_session_id"}}]}]}
        }
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.return_value = mock_response
            result = app._is_session_active_on_grid()
            assert result is False

    def test_is_session_active_on_grid_exception(self):
        """Test _is_session_active_on_grid with exception."""

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.side_effect = Exception("Network error")
            result = app._is_session_active_on_grid()
            assert result is False

    def test_is_session_active_on_standalone_success(self):
        """Test _is_session_active_on_standalone with successful response."""

        mock_driver = Mock()
        mock_driver.session_id = "test_session_id"
        app.driver = mock_driver

        mock_response = Mock()
        mock_response.json.return_value = {"value": [{"id": "test_session_id", "ready": True}]}
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.return_value = mock_response
            result = app._is_session_active_on_standalone()
            assert result is True

    def test_is_session_active_on_standalone_no_match(self):
        """Test _is_session_active_on_standalone with no matching session."""

        mock_response = Mock()
        mock_response.json.return_value = {"value": [{"id": "different_session_id", "ready": True}]}
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.return_value = mock_response
            result = app._is_session_active_on_standalone()
            assert result is False

    def test_is_session_active_on_standalone_exception(self):
        """Test _is_session_active_on_standalone with exception."""

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.side_effect = Exception("Network error")
            result = app._is_session_active_on_standalone()
            assert result is False

    def test_is_session_active_on_standalone_new_style_success(self):
        """Test _is_session_active_on_standalone_new_style with successful response."""

        mock_driver = Mock()
        mock_driver.session_id = "test_session_id"
        app.driver = mock_driver

        mock_response = Mock()
        mock_response.json.return_value = {"value": [{"id": "test_session_id", "ready": True}]}
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.return_value = mock_response
            result = app._is_session_active_on_standalone_new_style()
            assert result is True

    def test_is_session_active_on_standalone_new_style_no_match(self):
        """Test _is_session_active_on_standalone_new_style with no matching session."""

        mock_response = Mock()
        mock_response.json.return_value = {"value": [{"id": "different_session_id", "ready": True}]}
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.return_value = mock_response
            result = app._is_session_active_on_standalone_new_style()
            assert result is False

    def test_is_session_active_on_standalone_new_style_exception(self):
        """Test _is_session_active_on_standalone_new_style with exception."""

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.side_effect = Exception("Network error")
            result = app._is_session_active_on_standalone_new_style()
            assert result is False

    def test_wait_for_session_id_success(self):
        """Test _wait_for_session_id with successful session ID assignment."""

        mock_driver = MagicMock()
        mock_driver.session_id = "test_session_id"
        with patch.object(app, "driver", mock_driver):
            with patch("time.time", side_effect=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
                with patch("time.sleep"):
                    # Should not raise exception
                    result = app._wait_for_session_id(timeout=5)
                    assert result == "test_session_id"

    def test_wait_for_session_id_timeout(self):
        """Test _wait_for_session_id with timeout."""

        import pytest

        mock_driver = MagicMock()
        mock_driver.session_id = None
        with patch.object(app, "driver", mock_driver):
            with patch("time.time", side_effect=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
                with patch("time.sleep"):
                    with patch(
                        "shadowstep.shadowstep_base.WebDriverSingleton.get_driver",
                        return_value=mock_driver,
                    ):
                        with pytest.raises(
                            RuntimeError, match="WebDriver session_id was not assigned in time"
                        ):
                            app._wait_for_session_id(timeout=5)

    def test_connect_with_ssh_credentials(self):
        """Test connect method with SSH credentials."""

        # Mock the WebDriver and Transport
        with patch("shadowstep.shadowstep_base.WebDriverSingleton") as mock_singleton:
            with patch("shadowstep.shadowstep_base.Transport") as mock_transport:
                with patch("shadowstep.shadowstep_base.Terminal") as mock_terminal:
                    with patch("shadowstep.shadowstep_base.Adb") as mock_adb:
                        with patch("requests.Session") as mock_session:
                            session_mock = mock_session.return_value.__enter__.return_value
                            session_mock.delete.return_value = Mock()
                            # Disconnect first
                            app.disconnect()
                            session_mock.delete.reset_mock()

                            mock_driver = MagicMock()
                            mock_driver.session_id = "test_session_id"
                            mock_singleton.return_value = mock_driver

                            app.connect(
                                capabilities=CAPABILITIES,
                                server_ip="127.0.0.1",
                                server_port=4723,
                                ssh_user="test_user",
                                ssh_password="test_password",
                            )

                            # Verify SSH transport was created
                            mock_transport.assert_called_once_with(
                                server="127.0.0.1",
                                port=22,
                                user="test_user",
                                password="test_password",
                            )
                            mock_terminal.assert_called_once()
                            mock_adb.assert_called_once()

    def test_disconnect_with_invalid_session_exception(self):
        """Test disconnect method with InvalidSessionIdException."""

        # Mock driver and requests.Session.delete to raise InvalidSessionIdException
        mock_driver = MagicMock()
        mock_driver.session_id = "test_session_id"
        app.driver = mock_driver

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.delete.side_effect = InvalidSessionIdException("Invalid session")
            app.disconnect()
            # Should not raise exception, just log debug message

    def test_disconnect_with_no_such_driver_exception(self):
        """Test disconnect method with NoSuchDriverException."""

        # Mock driver and requests.Session.delete to raise NoSuchDriverException
        mock_driver = MagicMock()
        mock_driver.session_id = "test_session_id"
        app.driver = mock_driver

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.delete.side_effect = NoSuchDriverException("No such driver")
            app.disconnect()
            # Should not raise exception, just log debug message

    def test_is_session_active_on_grid_no_slots(self):
        """Test _is_session_active_on_grid with nodes but no slots."""

        mock_response = Mock()
        mock_response.json.return_value = {"value": {"nodes": [{"slots": []}]}}
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.return_value = mock_response
            result = app._is_session_active_on_grid()
            assert result is False

    def test_is_session_active_on_grid_no_session_in_slot(self):
        """Test _is_session_active_on_grid with slots but no session."""

        mock_response = Mock()
        mock_response.json.return_value = {"value": {"nodes": [{"slots": [{"session": None}]}]}}
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.return_value = mock_response
            result = app._is_session_active_on_grid()
            assert result is False

    @pytest.mark.unit
    def test_webdriver_singleton_get_session_id_with_sessions(self):
        """Test WebDriverSingleton._get_session_id with available sessions."""
        from shadowstep.web_driver.web_driver_singleton import WebDriverSingleton
        from unittest.mock import patch, Mock

        mock_response = Mock()
        mock_response.text = '{"value": [{"id": "session123"}]}'

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.return_value = mock_response
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "session123"

    @pytest.mark.unit
    def test_webdriver_singleton_get_session_id_no_sessions(self):
        """Test WebDriverSingleton._get_session_id with no sessions."""
        from shadowstep.web_driver.web_driver_singleton import WebDriverSingleton
        from unittest.mock import patch, Mock

        mock_response = Mock()
        mock_response.text = '{"value": []}'

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.return_value = mock_response
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "unknown_session_id"

    @pytest.mark.unit
    def test_webdriver_singleton_get_session_id_no_value_key(self):
        """Test WebDriverSingleton._get_session_id with no value key."""
        from shadowstep.web_driver.web_driver_singleton import WebDriverSingleton
        from unittest.mock import patch, Mock

        mock_response = Mock()
        mock_response.text = '{"other": []}'

        with patch("requests.Session") as mock_session:
            session_mock = mock_session.return_value.__enter__.return_value
            session_mock.get.return_value = mock_response
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "unknown_session_id"

    @pytest.mark.unit
    def test_webdriver_singleton_clear_instance(self):
        """Test WebDriverSingleton.clear_instance method."""
        from shadowstep.web_driver.web_driver_singleton import WebDriverSingleton

        # Set some values
        WebDriverSingleton._instance = "test_instance"
        WebDriverSingleton._driver = "test_driver"

        WebDriverSingleton.clear_instance()

        assert WebDriverSingleton._instance is None
        assert WebDriverSingleton._driver is None

    @pytest.mark.unit
    def test_webdriver_singleton_get_driver(self):
        """Test WebDriverSingleton.get_driver method."""
        from shadowstep.web_driver.web_driver_singleton import WebDriverSingleton
        from unittest.mock import patch, MagicMock

        # Clear any existing instance
        WebDriverSingleton._instance = None
        WebDriverSingleton._driver = None

        mock_driver = MagicMock()
        WebDriverSingleton._driver = mock_driver

        result = WebDriverSingleton.get_driver()
        assert result == mock_driver

        # Cleanup
        WebDriverSingleton.clear_instance()

    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_webdriver_singleton_new_creates_instance(self):
        """Test WebDriverSingleton.__new__ creates new instance when none exists."""
        from shadowstep.web_driver.web_driver_singleton import WebDriverSingleton
        from unittest.mock import patch, MagicMock

        # Clear any existing instance
        WebDriverSingleton._instance = None
        WebDriverSingleton._driver = None

        mock_webdriver = MagicMock()
        mock_webdriver.session_id = "test_session"

        with patch(
            "shadowstep.web_driver.web_driver_singleton.WebDriver", return_value=mock_webdriver
        ):
            result = WebDriverSingleton(command_executor="http://test:4723/wd/hub", options=None)
            assert result == mock_webdriver
            assert WebDriverSingleton._instance is not None
            assert WebDriverSingleton._driver == mock_webdriver
            assert WebDriverSingleton._command_executor == "http://test:4723/wd/hub"

        # Cleanup
        WebDriverSingleton.clear_instance()

    @pytest.mark.unit
    def test_webdriver_singleton_new_returns_existing_instance(self):
        """Test WebDriverSingleton.__new__ returns existing instance when one exists."""
        from shadowstep.web_driver.web_driver_singleton import WebDriverSingleton
        from unittest.mock import patch, MagicMock

        # Clear and set up existing instance
        WebDriverSingleton._instance = None
        WebDriverSingleton._driver = None

        mock_webdriver = MagicMock()
        mock_webdriver.session_id = "test_session"

        with patch(
            "shadowstep.web_driver.web_driver_singleton.WebDriver", return_value=mock_webdriver
        ):
            first_result = WebDriverSingleton(
                command_executor="http://test:4723/wd/hub", options=None
            )
            # Second call should return same instance
            second_result = WebDriverSingleton(
                command_executor="http://test2:4723/wd/hub", options=None
            )
            assert first_result == second_result
            assert WebDriverSingleton._driver == mock_webdriver

        # Cleanup
        WebDriverSingleton.clear_instance()

    @pytest.mark.unit
    def test_reconnect_success(self):
        """Test reconnect method successfully reconnects to Appium server."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        mock_driver = MagicMock()
        mock_driver.session_id = "test_session_id"

        base.driver = mock_driver
        base.server_ip = "127.0.0.1"
        base.server_port = 4723
        base.capabilities = CAPABILITIES
        base.command_executor = "http://127.0.0.1:4723/wd/hub"
        base.options = None
        base.extensions = None
        base.ssh_user = None
        base.ssh_password = None

        with patch.object(base, "disconnect") as mock_disconnect:
            with patch(
                "shadowstep.shadowstep_base.WebDriverSingleton.clear_instance"
            ) as mock_clear:
                with patch.object(base, "connect") as mock_connect:
                    with patch("time.sleep"):
                        base.reconnect()

                        mock_disconnect.assert_called_once()
                        mock_clear.assert_called_once()
                        mock_connect.assert_called_once_with(
                            command_executor="http://127.0.0.1:4723/wd/hub",
                            server_ip="127.0.0.1",
                            server_port=4723,
                            capabilities=CAPABILITIES,
                            options=None,
                            extensions=None,
                            ssh_user=None,
                            ssh_password=None,
                        )

    @pytest.mark.unit
    def test_reconnect_without_connection_params(self):
        """Test reconnect when connection parameters are not set."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.driver = None
        base.server_ip = None
        base.server_port = None
        base.capabilities = None

        with patch.object(base, "disconnect") as mock_disconnect:
            with patch(
                "shadowstep.shadowstep_base.WebDriverSingleton.clear_instance"
            ) as mock_clear:
                with patch.object(base, "connect") as mock_connect:
                    with patch("time.sleep"):
                        base.reconnect()

                        mock_disconnect.assert_called_once()
                        mock_clear.assert_called_once()
                        # connect is always called with stored parameters (even if None)
                        mock_connect.assert_called_once_with(
                            command_executor=None,
                            server_ip=None,
                            server_port=None,
                            capabilities=None,
                            options=None,
                            extensions=None,
                            ssh_user=None,
                            ssh_password=None,
                        )

    @pytest.mark.unit
    def test_is_connected_returns_true_when_session_active_on_grid(self):
        """Test is_connected returns True when session is active on grid."""
        with patch.object(app, "_is_session_active_on_grid", return_value=True):
            with patch.object(app, "_is_session_active_on_standalone", return_value=False):
                with patch.object(
                    app, "_is_session_active_on_standalone_new_style", return_value=False
                ):
                    result = app.is_connected()
                    assert result is True

    @pytest.mark.unit
    def test_is_connected_returns_true_when_session_active_on_standalone(self):
        """Test is_connected returns True when session is active on standalone server."""
        with patch.object(app, "_is_session_active_on_grid", return_value=False):
            with patch.object(app, "_is_session_active_on_standalone", return_value=True):
                with patch.object(
                    app, "_is_session_active_on_standalone_new_style", return_value=False
                ):
                    result = app.is_connected()
                    assert result is True

    @pytest.mark.unit
    def test_is_connected_returns_true_when_session_active_on_standalone_new_style(self):
        """Test is_connected returns True when session is active on standalone server (new style)."""
        with patch.object(app, "_is_session_active_on_grid", return_value=False):
            with patch.object(app, "_is_session_active_on_standalone", return_value=False):
                with patch.object(
                    app, "_is_session_active_on_standalone_new_style", return_value=True
                ):
                    result = app.is_connected()
                    assert result is True

    @pytest.mark.unit
    def test_is_connected_returns_false_when_no_session_active(self):
        """Test is_connected returns False when no session is active."""
        with patch.object(app, "_is_session_active_on_grid", return_value=False):
            with patch.object(app, "_is_session_active_on_standalone", return_value=False):
                with patch.object(
                    app, "_is_session_active_on_standalone_new_style", return_value=False
                ):
                    result = app.is_connected()
                    assert result is False

    @pytest.mark.unit
    def test_capabilities_to_options_general_capabilities(self):
        """Test _capabilities_to_options with general capabilities."""
        from shadowstep.shadowstep_base import ShadowstepBase
        from appium.options.android.uiautomator2.base import UiAutomator2Options

        base = ShadowstepBase()
        base.capabilities = {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": "TestDevice",
            "appium:platformVersion": "11.0",
            "appium:udid": "test-udid-123",
            "appium:noReset": True,
            "appium:fullReset": False,
            "appium:printPageSourceOnFindFailure": False,
        }
        base.options = None

        base._capabilities_to_options()

        assert isinstance(base.options, UiAutomator2Options)
        assert base.options.platform_name == "Android"
        # Note: Appium normalizes "UiAutomator2" to "UIAutomator2"
        assert base.options.automation_name == "UIAutomator2"
        assert base.options.device_name == "TestDevice"
        assert base.options.platform_version == "11.0"
        assert base.options.udid == "test-udid-123"
        assert base.options.no_reset is True
        assert base.options.full_reset is False
        assert base.options.print_page_source_on_find_failure is False

    @pytest.mark.unit
    def test_capabilities_to_options_udid_uppercase(self):
        """Test _capabilities_to_options with UDID in uppercase."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = {
            "appium:UDID": "test-udid-uppercase",
        }
        base.options = None

        base._capabilities_to_options()

        assert base.options.udid == "test-udid-uppercase"

    @pytest.mark.unit
    def test_capabilities_to_options_driver_server_capabilities(self):
        """Test _capabilities_to_options with driver/server capabilities."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = {
            "appium:systemPort": 8200,
            "appium:skipServerInstallation": True,
            "appium:uiautomator2ServerLaunchTimeout": 30000,
            "appium:uiautomator2ServerInstallTimeout": 20000,
            "appium:uiautomator2ServerReadTimeout": 10000,
            "appium:disableWindowAnimation": True,
            "appium:skipDeviceInitialization": True,
        }
        base.options = None

        base._capabilities_to_options()

        assert base.options.system_port == 8200
        assert base.options.skip_server_installation is True
        # Timeout values are stored as timedelta (milliseconds converted to seconds)
        assert base.options.uiautomator2_server_launch_timeout.total_seconds() == 30
        assert base.options.uiautomator2_server_install_timeout.total_seconds() == 20
        assert base.options.uiautomator2_server_read_timeout.total_seconds() == 10
        assert base.options.disable_window_animation is True
        assert base.options.skip_device_initialization is True

    @pytest.mark.unit
    def test_capabilities_to_options_app_capabilities(self):
        """Test _capabilities_to_options with app capabilities."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = {
            "appium:app": "/path/to/app.apk",
            "browserName": "Chrome",
            "appium:appPackage": "com.example.app",
            "appium:appActivity": ".MainActivity",
            "appium:appWaitActivity": ".SplashActivity",
            "appium:appWaitPackage": "com.example.app",
            "appium:appWaitDuration": 20000,
            "appium:androidInstallTimeout": 90000,
            "appium:appWaitForLaunch": True,
            "appium:intentCategory": "android.intent.category.LAUNCHER",
            "appium:intentAction": "android.intent.action.MAIN",
            "appium:intentFlags": "0x10200000",
            "appium:optionalIntentArguments": "--flag value",
            "appium:autoGrantPermissions": True,
            "appium:otherApps": "/path/to/helper.apk",
            "appium:uninstallOtherPackages": "com.example.old",
            "appium:allowTestPackages": True,
            "appium:remoteAppsCacheLimit": 10,
            "appium:enforceAppInstall": True,
        }
        base.options = None

        base._capabilities_to_options()

        assert base.options.app == "/path/to/app.apk"
        assert base.options.browser_name == "Chrome"
        assert base.options.app_package == "com.example.app"
        assert base.options.app_activity == ".MainActivity"
        assert base.options.app_wait_activity == ".SplashActivity"
        assert base.options.app_wait_package == "com.example.app"
        # Timeout values are stored as timedelta (milliseconds converted to seconds)
        assert base.options.app_wait_duration.total_seconds() == 20
        assert base.options.android_install_timeout.total_seconds() == 90
        assert base.options.app_wait_for_launch is True
        assert base.options.intent_category == "android.intent.category.LAUNCHER"
        assert base.options.intent_action == "android.intent.action.MAIN"
        assert base.options.intent_flags == "0x10200000"
        assert base.options.optional_intent_arguments == "--flag value"
        assert base.options.auto_grant_permissions is True
        assert base.options.other_apps == "/path/to/helper.apk"
        assert base.options.uninstall_other_packages == "com.example.old"
        assert base.options.allow_test_packages is True
        assert base.options.remote_apps_cache_limit == 10
        assert base.options.enforce_app_install is True

    @pytest.mark.unit
    def test_capabilities_to_options_localization_capabilities(self):
        """Test _capabilities_to_options with app localization capabilities."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = {
            "appium:localeScript": "Cyrl",
            "appium:language": "ru",
            "appium:locale": "RU",
        }
        base.options = None

        base._capabilities_to_options()

        assert base.options.locale_script == "Cyrl"
        assert base.options.language == "ru"
        assert base.options.locale == "RU"

    @pytest.mark.unit
    def test_capabilities_to_options_adb_capabilities(self):
        """Test _capabilities_to_options with ADB capabilities."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = {
            "appium:adbPort": 5037,
            "appium:remoteAdbHost": "192.168.1.100",
            "appium:adbExecTimeout": 20000,
            "appium:clearDeviceLogsOnStart": True,
            "appium:buildToolsVersion": "30.0.3",
            "appium:skipLogcatCapture": False,
            "appium:suppressKillServer": True,
            "appium:ignoreHiddenApiPolicyError": True,
            "appium:mockLocationApp": "io.appium.settings",
            "appium:logcatFormat": "threadtime",
            "appium:logcatFilterSpecs": ["*:D"],
            "appium:allowDelayAdb": True,
        }
        base.options = None

        base._capabilities_to_options()

        assert base.options.adb_port == 5037
        assert base.options.remote_adb_host == "192.168.1.100"
        # Timeout values are stored as timedelta (milliseconds converted to seconds)
        assert base.options.adb_exec_timeout.total_seconds() == 20
        assert base.options.clear_device_logs_on_start is True
        assert base.options.build_tools_version == "30.0.3"
        assert base.options.skip_logcat_capture is False
        assert base.options.suppress_kill_server is True
        assert base.options.ignore_hidden_api_policy_error is True
        assert base.options.mock_location_app == "io.appium.settings"
        assert base.options.logcat_format == "threadtime"
        assert base.options.logcat_filter_specs == ["*:D"]
        assert base.options.allow_delay_adb is True

    @pytest.mark.unit
    def test_capabilities_to_options_emulator_capabilities(self):
        """Test _capabilities_to_options with emulator (AVD) capabilities."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = {
            "appium:avd": "Pixel_6_API_34",
            "appium:avdLaunchTimeout": 120000,
            "appium:avdReadyTimeout": 60000,
            "appium:avdArgs": ["-no-snapshot-load"],
            "appium:avdEnv": {"LANG": "en_US"},
            "appium:networkSpeed": "full",
            "appium:gpsEnabled": True,
            "appium:isHeadless": False,
        }
        base.options = None

        base._capabilities_to_options()

        assert base.options.avd == "Pixel_6_API_34"
        # Timeout values are stored as timedelta (milliseconds converted to seconds)
        assert base.options.avd_launch_timeout.total_seconds() == 120
        assert base.options.avd_ready_timeout.total_seconds() == 60
        assert base.options.avd_args == ["-no-snapshot-load"]
        assert base.options.avd_env == {"LANG": "en_US"}
        assert base.options.network_speed == "full"
        assert base.options.gps_enabled is True
        assert base.options.is_headless is False

    @pytest.mark.unit
    def test_capabilities_to_options_app_signing_capabilities(self):
        """Test _capabilities_to_options with app signing capabilities."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = {
            "appium:useKeystore": True,
            "appium:keystorePath": "/path/to/keystore.jks",
            "appium:keystorePassword": "keystorepass",
            "appium:keyAlias": "mykey",
            "appium:keyPassword": "keypass",
            "appium:noSign": False,
        }
        base.options = None

        base._capabilities_to_options()

        assert base.options.use_keystore is True
        assert base.options.keystore_path == "/path/to/keystore.jks"
        assert base.options.keystore_password == "keystorepass"
        assert base.options.key_alias == "mykey"
        assert base.options.key_password == "keypass"
        assert base.options.no_sign is False

    @pytest.mark.unit
    def test_capabilities_to_options_device_locking_capabilities(self):
        """Test _capabilities_to_options with device locking capabilities."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = {
            "appium:skipUnlock": False,
            "appium:unlockType": "pin",
            "appium:unlockKey": "1234",
            "appium:unlockStrategy": "uiautomator",
            "appium:unlockSuccessTimeout": 2000,
        }
        base.options = None

        base._capabilities_to_options()

        assert base.options.skip_unlock is False
        assert base.options.unlock_type == "pin"
        assert base.options.unlock_key == "1234"
        assert base.options.unlock_strategy == "uiautomator"
        # Timeout values are stored as timedelta (milliseconds converted to seconds)
        assert base.options.unlock_success_timeout.total_seconds() == 2

    @pytest.mark.unit
    def test_capabilities_to_options_mjpeg_capabilities(self):
        """Test _capabilities_to_options with MJPEG capabilities."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = {
            "appium:mjpegServerPort": 7810,
            "appium:mjpegScreenshotUrl": "http://localhost:7810/screenshot.jpg",
        }
        base.options = None

        base._capabilities_to_options()

        assert base.options.mjpeg_server_port == 7810
        assert base.options.mjpeg_screenshot_url == "http://localhost:7810/screenshot.jpg"

    @pytest.mark.unit
    def test_capabilities_to_options_web_context_capabilities(self):
        """Test _capabilities_to_options with web context capabilities."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = {
            "appium:autoWebview": True,
            "appium:autoWebviewTimeout": 2000,
            "appium:webviewDevtoolsPort": 9222,
            "appium:ensureWebviewsHavePages": True,
            "appium:chromedriverPort": 9515,
            "appium:chromedriverPorts": [9515, 9516],
            "appium:chromedriverArgs": ["--verbose"],
            "appium:chromedriverExecutable": "/path/to/chromedriver",
            "appium:chromedriverExecutableDir": "/path/to/chromedrivers",
            "appium:chromedriverChromeMappingFile": "/path/to/mapping.json",
            "appium:chromedriverUseSystemExecutable": True,
            "appium:chromedriverDisableBuildCheck": True,
            "appium:recreateChromeDriverSessions": True,
            "appium:nativeWebScreenshot": False,
            "appium:extractChromeAndroidPackageFromContextName": True,
            "appium:showChromedriverLog": True,
            "pageLoadStrategy": "normal",
            "appium:chromeOptions": {"w3c": False},
            "appium:chromeLoggingPrefs": {"browser": "ALL"},
        }
        base.options = None

        base._capabilities_to_options()

        assert base.options.auto_web_view is True
        # Timeout values are stored as timedelta (milliseconds converted to seconds)
        assert base.options.auto_webview_timeout.total_seconds() == 2
        assert base.options.webview_devtools_port == 9222
        assert base.options.ensure_webviews_have_pages is True
        assert base.options.chromedriver_port == 9515
        assert base.options.chromedriver_ports == [9515, 9516]
        assert base.options.chromedriver_args == ["--verbose"]
        assert base.options.chromedriver_executable == "/path/to/chromedriver"
        assert base.options.chromedriver_executable_dir == "/path/to/chromedrivers"
        assert base.options.chromedriver_chrome_mapping_file == "/path/to/mapping.json"
        assert base.options.chromedriver_use_system_executable is True
        assert base.options.chromedriver_disable_build_check is True
        assert base.options.recreate_chrome_driver_sessions is True
        assert base.options.native_web_screenshot is False
        assert base.options.extract_chrome_android_package_from_context_name is True
        assert base.options.show_chromedriver_log is True
        assert base.options.page_load_strategy == "normal"
        assert base.options.chrome_options == {"w3c": False}
        assert base.options.chrome_logging_prefs == {"browser": "ALL"}

    @pytest.mark.unit
    def test_capabilities_to_options_other_capabilities(self):
        """Test _capabilities_to_options with other capabilities."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = {
            "appium:disableSuppressAccessibilityService": True,
            "appium:userProfile": 10,
            "appium:newCommandTimeout": 60,
        }
        base.options = None

        base._capabilities_to_options()

        assert base.options.disable_suppress_accessibility_service is True
        assert base.options.user_profile == 10
        # Timeout values are stored as timedelta (seconds)
        assert base.options.new_command_timeout.total_seconds() == 60

    @pytest.mark.unit
    def test_capabilities_to_options_when_options_already_provided(self):
        """Test _capabilities_to_options when options are already provided."""
        from shadowstep.shadowstep_base import ShadowstepBase
        from appium.options.android.uiautomator2.base import UiAutomator2Options

        base = ShadowstepBase()
        existing_options = UiAutomator2Options()
        existing_options.platform_name = "Android"
        existing_options.device_name = "ExistingDevice"

        base.capabilities = {
            "platformName": "iOS",
            "appium:deviceName": "NewDevice",
        }
        base.options = existing_options

        base._capabilities_to_options()

        # Options should remain unchanged
        assert base.options == existing_options
        assert base.options.platform_name == "Android"
        assert base.options.device_name == "ExistingDevice"

    @pytest.mark.unit
    def test_capabilities_to_options_with_none_capabilities(self):
        """Test _capabilities_to_options when capabilities is None."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        base.capabilities = None
        base.options = None

        base._capabilities_to_options()

        # Should not create options if capabilities is None
        assert base.options is None
