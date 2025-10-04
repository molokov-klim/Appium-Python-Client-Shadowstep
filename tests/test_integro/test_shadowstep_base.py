"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/base/test_shadowstep_base.py
"""

import logging
import time
from datetime import timedelta

from appium.options.android.uiautomator2.base import UiAutomator2Options
from selenium.common.exceptions import (
    InvalidSessionIdException,
    WebDriverException,
)

from conftest import CAPABILITIES, APPIUM_IP, APPIUM_PORT
from shadowstep.shadowstep import Shadowstep

logger = logging.getLogger(__name__)


# type: ignore[reportPrivateUsage]
class TestShadowstepBase:
    def test_webdriver_singleton_creation(self, app: Shadowstep):
        """Test WebDriverSingleton creation and reuse"""

        # Create a new Shadowstep instance - it should reuse the same driver
        app2 = Shadowstep()
        app2.connect(server_ip=APPIUM_IP, server_port=APPIUM_PORT, capabilities=CAPABILITIES)

        # Both instances should have the same driver (singleton pattern)
        assert app.driver is not None  # noqa: S101
        assert app2.driver is app.driver  # noqa: S101

    def test_reconnect_after_session_disruption(self, app: Shadowstep):
        """Test automatic reconnection on broken session"""
        app.reconnect()  # Reconnection
        app.driver.get_screenshot_as_png()  # Attempt to execute command    # type: ignore
        assert app.driver.session_id is not None, "Failed to reconnect"  # noqa: S101    # type: ignore

    def test_disconnect_on_invalid_session_exception(self, app: Shadowstep):
        """Test InvalidSessionIdException handling on session break in disconnect"""
        app.disconnect()
        CAPABILITIES["appium:newCommandTimeout"] = 10
        app.connect(server_ip=APPIUM_IP, server_port=APPIUM_PORT, capabilities=CAPABILITIES)
        time.sleep(12)
        try:
            app.driver.get_screenshot_as_png()  # type: ignore
        except InvalidSessionIdException as error:
            assert isinstance(error, InvalidSessionIdException)  # noqa: S101, PT017
            CAPABILITIES["appium:newCommandTimeout"] = 900
            app.connect(server_ip=APPIUM_IP, server_port=APPIUM_PORT, capabilities=CAPABILITIES)
            return True
        except Exception as error:
            logger.error(error)
            raise AssertionError(f"Unknown error: {type(error)}") from error
        raise AssertionError("Test logic error, expected session break")  # ???

    def test_reconnect_without_active_session(self, app: Shadowstep):
        """Test reconnect call when no active session"""
        app.disconnect()
        app.reconnect()
        assert app.driver is not None, "Session was not created on reconnection"  # noqa: S101
        assert app.driver.session_id is not None, "Session was not created on reconnection"  # noqa: S101

    def test_session_state_before_command_execution(self, app: Shadowstep):
        """Test session state before executing WebDriver commands"""
        if app.driver.session_id is None:  # type: ignore
            app.reconnect()  # Reconnection when no active session
        try:
            app.driver.get_screenshot_as_png()  # type: ignore
        except WebDriverException as error:
            raise AssertionError(f"Command execution error: {error}") from error

    def test_handling_of_capabilities_option(self, app: Shadowstep):
        """Test correct capabilities parameter handling"""
        app.disconnect()  # End current session to check new settings
        new_caps = CAPABILITIES.copy()
        new_caps["appium:autoGrantPermissions"] = False  # Change capabilities
        app.connect(server_ip="127.0.0.1", server_port=4723, capabilities=new_caps)
        assert app.driver is not None, "Session was not created with new capabilities parameters"  # noqa: S101
        assert app.options.auto_grant_permissions is False, (  # type: ignore
            "autoGrantPermissions parameter was not applied"
        )  # noqa: S101    # type: ignore
        app.connect(server_ip="127.0.0.1", server_port=4723, capabilities=CAPABILITIES)

    def test_is_connected_when_connected(self, app: Shadowstep):
        app.reconnect()
        assert app.is_connected()  # noqa: S101

    def test_is_connected_when_disconnected(self, app: Shadowstep):
        app.disconnect()
        assert not app.is_connected()  # noqa: S101
        app.connect(CAPABILITIES)

    def test_capabilities_to_options_general_settings(self, app: Shadowstep):
        """Test _capabilities_to_options with general settings."""

        capabilities = {
            "platformName": "Android",
            "appium:automationName": "uiautomator2",
            "appium:deviceName": "Test Device",
            "appium:platformVersion": "11",
            "appium:UDID": "test_udid",
            "appium:noReset": True,
            "appium:fullReset": False,
            "appium:printPageSourceOnFindFailure": True,
        }

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

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
            "appium:enforceAppInstall": True,
        }

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.app == "/path/to/app.apk"
        assert app.options.browser_name == "Chrome"
        assert app.options.app_package == "com.test.app"
        assert app.options.app_activity == ".MainActivity"
        assert app.options.app_wait_activity == ".SplashActivity"
        assert app.options.app_wait_package == "com.test.app"

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
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert app.options is None

    def test_capabilities_to_options_with_existing_options(self, app: Shadowstep):
        """Test _capabilities_to_options with existing options."""

        existing_options = UiAutomator2Options()
        existing_options.platform_name = "iOS"

        app.capabilities = {"platformName": "Android"}
        app.options = existing_options
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        # Should not modify existing options
        assert app.options is existing_options
        assert app.options.platform_name == "iOS"  # type: ignore

    def test_capabilities_to_options_udid_lowercase(self, app: Shadowstep):
        """Test _capabilities_to_options with lowercase udid."""

        capabilities = {"appium:udid": "test_udid_lowercase"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.udid == "test_udid_lowercase"

    def test_capabilities_to_options_system_port(self, app: Shadowstep):
        """Test _capabilities_to_options with system port."""

        capabilities = {"appium:systemPort": 8201}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.system_port == 8201

    def test_capabilities_to_options_skip_server_installation(self, app: Shadowstep):
        """Test _capabilities_to_options with skip server installation."""

        capabilities = {"appium:skipServerInstallation": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.skip_server_installation is True

    def test_capabilities_to_options_uiautomator2_server_launch_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with uiautomator2 server launch timeout."""

        capabilities = {"appium:uiautomator2ServerLaunchTimeout": 60000}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.uiautomator2_server_launch_timeout == timedelta(seconds=60)

    def test_capabilities_to_options_uiautomator2_server_install_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with uiautomator2 server install timeout."""

        capabilities = {"appium:uiautomator2ServerInstallTimeout": 60000}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.uiautomator2_server_install_timeout == timedelta(seconds=60)

    def test_capabilities_to_options_uiautomator2_server_read_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with uiautomator2 server read timeout."""

        capabilities = {"appium:uiautomator2ServerReadTimeout": 60000}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.uiautomator2_server_read_timeout == timedelta(seconds=60)

    def test_capabilities_to_options_disable_window_animation(self, app: Shadowstep):
        """Test _capabilities_to_options with disable window animation."""

        capabilities = {"appium:disableWindowAnimation": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.disable_window_animation is True

    def test_capabilities_to_options_skip_device_initialization(self, app: Shadowstep):
        """Test _capabilities_to_options with skip device initialization."""

        capabilities = {"appium:skipDeviceInitialization": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.skip_device_initialization is True

    def test_capabilities_to_options_locale_script(self, app: Shadowstep):
        """Test _capabilities_to_options with locale script."""

        capabilities = {"appium:localeScript": "Latn"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.locale_script == "Latn"

    def test_capabilities_to_options_language(self, app: Shadowstep):
        """Test _capabilities_to_options with language."""

        capabilities = {"appium:language": "en"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.language == "en"

    def test_capabilities_to_options_locale(self, app: Shadowstep):
        """Test _capabilities_to_options with locale."""

        capabilities = {"appium:locale": "en_US"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.locale == "en_US"

    def test_capabilities_to_options_adb_port(self, app: Shadowstep):
        """Test _capabilities_to_options with adb port."""

        capabilities = {"appium:adbPort": 5037}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.adb_port == 5037

    def test_capabilities_to_options_remote_adb_host(self, app: Shadowstep):
        """Test _capabilities_to_options with remote adb host."""

        capabilities = {"appium:remoteAdbHost": "192.168.1.100"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.remote_adb_host == "192.168.1.100"

    def test_capabilities_to_options_adb_exec_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with adb exec timeout."""

        capabilities = {"appium:adbExecTimeout": 60000}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.adb_exec_timeout == timedelta(seconds=60)

    def test_capabilities_to_options_clear_device_logs_on_start(self, app: Shadowstep):
        """Test _capabilities_to_options with clear device logs on start."""

        capabilities = {"appium:clearDeviceLogsOnStart": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.clear_device_logs_on_start is True

    def test_capabilities_to_options_build_tools_version(self, app: Shadowstep):
        """Test _capabilities_to_options with build tools version."""

        capabilities = {"appium:buildToolsVersion": "30.0.3"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.build_tools_version == "30.0.3"

    def test_capabilities_to_options_skip_logcat_capture(self, app: Shadowstep):
        """Test _capabilities_to_options with skip logcat capture."""

        capabilities = {"appium:skipLogcatCapture": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.skip_logcat_capture is True

    def test_capabilities_to_options_suppress_kill_server(self, app: Shadowstep):
        """Test _capabilities_to_options with suppress kill server."""

        capabilities = {"appium:suppressKillServer": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.suppress_kill_server is True

    def test_capabilities_to_options_ignore_hidden_api_policy_error(self, app: Shadowstep):
        """Test _capabilities_to_options with ignore hidden api policy error."""

        capabilities = {"appium:ignoreHiddenApiPolicyError": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.ignore_hidden_api_policy_error is True

    def test_capabilities_to_options_mock_location_app(self, app: Shadowstep):
        """Test _capabilities_to_options with mock location app."""

        capabilities = {"appium:mockLocationApp": "com.example.mocklocation"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.mock_location_app == "com.example.mocklocation"

    def test_capabilities_to_options_logcat_format(self, app: Shadowstep):
        """Test _capabilities_to_options with logcat format."""

        capabilities = {"appium:logcatFormat": "time"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.logcat_format == "time"

    def test_capabilities_to_options_logcat_filter_specs(self, app: Shadowstep):
        """Test _capabilities_to_options with logcat filter specs."""

        capabilities = {"appium:logcatFilterSpecs": ["*:V"]}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.logcat_filter_specs == ["*:V"]

    def test_capabilities_to_options_allow_delay_adb(self, app: Shadowstep):
        """Test _capabilities_to_options with allow delay adb."""

        capabilities = {"appium:allowDelayAdb": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.allow_delay_adb is True

    def test_capabilities_to_options_avd(self, app: Shadowstep):
        """Test _capabilities_to_options with avd."""

        capabilities = {"appium:avd": "test_avd"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.avd == "test_avd"

    def test_capabilities_to_options_avd_launch_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with avd launch timeout."""

        capabilities = {"appium:avdLaunchTimeout": 120000}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.avd_launch_timeout == timedelta(seconds=120)

    def test_capabilities_to_options_avd_ready_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with avd ready timeout."""

        capabilities = {"appium:avdReadyTimeout": 120000}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.avd_ready_timeout == timedelta(seconds=120)

    def test_capabilities_to_options_avd_args(self, app: Shadowstep):
        """Test _capabilities_to_options with avd args."""

        capabilities = {"appium:avdArgs": "-no-snapshot-load"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.avd_args == "-no-snapshot-load"

    def test_capabilities_to_options_avd_env(self, app: Shadowstep):
        """Test _capabilities_to_options with avd env."""

        capabilities = {"appium:avdEnv": {"ANDROID_HOME": "/path/to/android"}}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.avd_env == {"ANDROID_HOME": "/path/to/android"}

    def test_capabilities_to_options_network_speed(self, app: Shadowstep):
        """Test _capabilities_to_options with network speed."""

        capabilities = {"appium:networkSpeed": "full"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.network_speed == "full"

    def test_capabilities_to_options_gps_enabled(self, app: Shadowstep):
        """Test _capabilities_to_options with gps enabled."""

        capabilities = {"appium:gpsEnabled": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.gps_enabled is True

    def test_capabilities_to_options_is_headless(self, app: Shadowstep):
        """Test _capabilities_to_options with is headless."""

        capabilities = {"appium:isHeadless": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.is_headless is True

    def test_capabilities_to_options_use_keystore(self, app: Shadowstep):
        """Test _capabilities_to_options with use keystore."""

        capabilities = {"appium:useKeystore": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.use_keystore is True

    def test_capabilities_to_options_keystore_path(self, app: Shadowstep):
        """Test _capabilities_to_options with keystore path."""

        capabilities = {"appium:keystorePath": "/path/to/keystore"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.keystore_path == "/path/to/keystore"

    def test_capabilities_to_options_keystore_password(self, app: Shadowstep):
        """Test _capabilities_to_options with keystore password."""

        capabilities = {"appium:keystorePassword": "password123"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.keystore_password == "password123"

    def test_capabilities_to_options_key_alias(self, app: Shadowstep):
        """Test _capabilities_to_options with key alias."""

        capabilities = {"appium:keyAlias": "mykey"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.key_alias == "mykey"

    def test_capabilities_to_options_key_password(self, app: Shadowstep):
        """Test _capabilities_to_options with key password."""

        capabilities = {"appium:keyPassword": "keypass123"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.key_password == "keypass123"

    def test_capabilities_to_options_no_sign(self, app: Shadowstep):
        """Test _capabilities_to_options with no sign."""

        capabilities = {"appium:noSign": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.no_sign is True

    def test_capabilities_to_options_skip_unlock(self, app: Shadowstep):
        """Test _capabilities_to_options with skip unlock."""

        capabilities = {"appium:skipUnlock": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.skip_unlock is True

    def test_capabilities_to_options_unlock_type(self, app: Shadowstep):
        """Test _capabilities_to_options with unlock type."""

        capabilities = {"appium:unlockType": "pin"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.unlock_type == "pin"

    def test_capabilities_to_options_unlock_key(self, app: Shadowstep):
        """Test _capabilities_to_options with unlock key."""

        capabilities = {"appium:unlockKey": "1234"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.unlock_key == "1234"

    def test_capabilities_to_options_unlock_strategy(self, app: Shadowstep):
        """Test _capabilities_to_options with unlock strategy."""

        capabilities = {"appium:unlockStrategy": "locksettings"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.unlock_strategy == "locksettings"

    def test_capabilities_to_options_unlock_success_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with unlock success timeout."""

        capabilities = {"appium:unlockSuccessTimeout": 30000}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.unlock_success_timeout == timedelta(seconds=30)

    def test_capabilities_to_options_mjpeg_server_port(self, app: Shadowstep):
        """Test _capabilities_to_options with mjpeg server port."""

        capabilities = {"appium:mjpegServerPort": 8080}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.mjpeg_server_port == 8080

    def test_capabilities_to_options_mjpeg_screenshot_url(self, app: Shadowstep):
        """Test _capabilities_to_options with mjpeg screenshot url."""

        capabilities = {"appium:mjpegScreenshotUrl": "http://localhost:8080/screenshot"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.mjpeg_screenshot_url == "http://localhost:8080/screenshot"

    def test_capabilities_to_options_auto_webview(self, app: Shadowstep):
        """Test _capabilities_to_options with auto webview."""

        capabilities = {"appium:autoWebview": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.auto_web_view is True

    def test_capabilities_to_options_auto_webview_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with auto webview timeout."""

        capabilities = {"appium:autoWebviewTimeout": 30000}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.auto_webview_timeout == timedelta(seconds=30)

    def test_capabilities_to_options_webview_devtools_port(self, app: Shadowstep):
        """Test _capabilities_to_options with webview devtools port."""

        capabilities = {"appium:webviewDevtoolsPort": 9222}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.webview_devtools_port == 9222

    def test_capabilities_to_options_ensure_webviews_have_pages(self, app: Shadowstep):
        """Test _capabilities_to_options with ensure webviews have pages."""

        capabilities = {"appium:ensureWebviewsHavePages": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.ensure_webviews_have_pages is True

    def test_capabilities_to_options_chromedriver_port(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver port."""

        capabilities = {"appium:chromedriverPort": 9515}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_port == 9515

    def test_capabilities_to_options_chromedriver_ports(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver ports."""

        capabilities = {"appium:chromedriverPorts": [9515, 9516]}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_ports == [9515, 9516]

    def test_capabilities_to_options_chromedriver_args(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver args."""

        capabilities = {"appium:chromedriverArgs": ["--no-sandbox"]}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_args == ["--no-sandbox"]

    def test_capabilities_to_options_chromedriver_executable(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver executable."""

        capabilities = {"appium:chromedriverExecutable": "/path/to/chromedriver"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_executable == "/path/to/chromedriver"

    def test_capabilities_to_options_chromedriver_executable_dir(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver executable dir."""

        capabilities = {"appium:chromedriverExecutableDir": "/path/to/chromedriver/dir"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_executable_dir == "/path/to/chromedriver/dir"

    def test_capabilities_to_options_chromedriver_chrome_mapping_file(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver chrome mapping file."""

        capabilities = {"appium:chromedriverChromeMappingFile": "/path/to/mapping.json"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_chrome_mapping_file == "/path/to/mapping.json"

    def test_capabilities_to_options_chromedriver_use_system_executable(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver use system executable."""

        capabilities = {"appium:chromedriverUseSystemExecutable": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_use_system_executable is True

    def test_capabilities_to_options_chromedriver_disable_build_check(self, app: Shadowstep):
        """Test _capabilities_to_options with chromedriver disable build check."""

        capabilities = {"appium:chromedriverDisableBuildCheck": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chromedriver_disable_build_check is True

    def test_capabilities_to_options_recreate_chrome_driver_sessions(self, app: Shadowstep):
        """Test _capabilities_to_options with recreate chrome driver sessions."""

        capabilities = {"appium:recreateChromeDriverSessions": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.recreate_chrome_driver_sessions is True

    def test_capabilities_to_options_native_web_screenshot(self, app: Shadowstep):
        """Test _capabilities_to_options with native web screenshot."""

        capabilities = {"appium:nativeWebScreenshot": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.native_web_screenshot is True

    def test_capabilities_to_options_extract_chrome_android_package_from_context_name(
        self, app: Shadowstep
    ):
        """Test _capabilities_to_options with extract chrome android package from context name."""

        capabilities = {"appium:extractChromeAndroidPackageFromContextName": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.extract_chrome_android_package_from_context_name is True

    def test_capabilities_to_options_show_chromedriver_log(self, app: Shadowstep):
        """Test _capabilities_to_options with show chromedriver log."""

        capabilities = {"appium:showChromedriverLog": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.show_chromedriver_log is True

    def test_capabilities_to_options_page_load_strategy(self, app: Shadowstep):
        """Test _capabilities_to_options with page load strategy."""

        capabilities = {"pageLoadStrategy": "eager"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.page_load_strategy == "eager"

    def test_capabilities_to_options_chrome_options(self, app: Shadowstep):
        """Test _capabilities_to_options with chrome options."""

        capabilities = {"appium:chromeOptions": {"args": ["--no-sandbox"]}}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chrome_options == {"args": ["--no-sandbox"]}

    def test_capabilities_to_options_chrome_logging_prefs(self, app: Shadowstep):
        """Test _capabilities_to_options with chrome logging prefs."""

        capabilities = {"appium:chromeLoggingPrefs": {"browser": "ALL"}}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.chrome_logging_prefs == {"browser": "ALL"}

    def test_capabilities_to_options_disable_suppress_accessibility_service(self, app: Shadowstep):
        """Test _capabilities_to_options with disable suppress accessibility service."""

        capabilities = {"appium:disableSuppressAccessibilityService": True}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.disable_suppress_accessibility_service is True

    def test_capabilities_to_options_user_profile(self, app: Shadowstep):
        """Test _capabilities_to_options with user profile."""

        capabilities = {"appium:userProfile": "test_profile"}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.user_profile == "test_profile"

    def test_capabilities_to_options_new_command_timeout(self, app: Shadowstep):
        """Test _capabilities_to_options with new command timeout."""

        capabilities = {"appium:newCommandTimeout": 300}

        app.capabilities = capabilities
        app.options = None
        app._capabilities_to_options()  # type: ignore[reportPrivateUsage]

        assert isinstance(app.options, UiAutomator2Options)
        assert app.options.new_command_timeout == timedelta(seconds=300)

    # ====================================================================================
    # Missing integration tests - stubs below
    # ====================================================================================

    def test_appium_disconnected_error_creation(self, app: Shadowstep):
        """Test AppiumDisconnectedError exception creation and handling.

        Steps:
        1. Create an instance of AppiumDisconnectedError with message, screen, and stacktrace.
        2. Verify that the exception is created correctly.
        3. Verify that the exception can be raised and caught.
        4. Verify that exception attributes are accessible.

        Тест создания исключения AppiumDisconnectedError:
        1. Создать экземпляр AppiumDisconnectedError с сообщением, скриншотом и стектрейсом.
        2. Проверить, что исключение создано корректно.
        3. Проверить, что исключение можно поднять и поймать.
        4. Проверить доступность атрибутов исключения.
        """
        pass

    def test_webdriver_singleton_get_session_id_success(self, app: Shadowstep):
        """Test WebDriverSingleton._get_session_id() successfully retrieves session ID.

        Steps:
        1. Connect to Appium server and establish a session.
        2. Call WebDriverSingleton._get_session_id() with command_executor kwargs.
        3. Verify that a valid session_id string is returned.
        4. Verify that the session_id matches the current driver's session_id.

        Тест успешного получения session_id через WebDriverSingleton._get_session_id():
        1. Подключиться к Appium серверу и установить сессию.
        2. Вызвать WebDriverSingleton._get_session_id() с параметрами command_executor.
        3. Проверить, что возвращается валидный session_id.
        4. Проверить, что session_id соответствует текущему session_id драйвера.
        """
        pass

    def test_webdriver_singleton_get_session_id_no_sessions(self, app: Shadowstep):
        """Test WebDriverSingleton._get_session_id() when no sessions exist.

        Steps:
        1. Disconnect all active sessions.
        2. Call WebDriverSingleton._get_session_id() with command_executor kwargs.
        3. Verify that "unknown_session_id" is returned.
        4. Verify no exceptions are raised.

        Тест получения session_id когда сессий нет:
        1. Отключить все активные сессии.
        2. Вызвать WebDriverSingleton._get_session_id() с параметрами command_executor.
        3. Проверить, что возвращается "unknown_session_id".
        4. Проверить, что не возникает исключений.
        """
        pass

    def test_webdriver_singleton_get_session_id_request_timeout(self, app: Shadowstep):
        """Test WebDriverSingleton._get_session_id() with network timeout.

        Steps:
        1. Mock or simulate a network timeout scenario.
        2. Call WebDriverSingleton._get_session_id() with invalid/unreachable server.
        3. Verify that a timeout exception is raised or handled gracefully.

        Тест получения session_id при таймауте сети:
        1. Замокать или симулировать таймаут сети.
        2. Вызвать WebDriverSingleton._get_session_id() с недоступным сервером.
        3. Проверить, что возникает исключение таймаута или оно обрабатывается корректно.
        """
        pass

    def test_webdriver_singleton_clear_instance_explicit(self, app: Shadowstep):
        """Test WebDriverSingleton.clear_instance() explicitly clears resources.

        Steps:
        1. Ensure a WebDriver session is active.
        2. Call WebDriverSingleton.clear_instance() explicitly.
        3. Verify that _driver is set to None.
        4. Verify that _instance is set to None.
        5. Verify that garbage collection is triggered.

        Тест явной очистки WebDriverSingleton.clear_instance():
        1. Убедиться, что активна сессия WebDriver.
        2. Вызвать WebDriverSingleton.clear_instance() явно.
        3. Проверить, что _driver установлен в None.
        4. Проверить, что _instance установлен в None.
        5. Проверить, что запущен сборщик мусора.
        """
        pass

    def test_is_session_active_on_grid_success(self, app: Shadowstep):
        """Test _is_session_active_on_grid() returns True when session found in Grid.

        Steps:
        1. Connect to a Selenium Grid (or mock Grid endpoint).
        2. Establish a session.
        3. Call _is_session_active_on_grid().
        4. Verify that True is returned when session is found in Grid slots.

        Тест _is_session_active_on_grid() возвращает True при наличии сессии в Grid:
        1. Подключиться к Selenium Grid (или замокать Grid endpoint).
        2. Установить сессию.
        3. Вызвать _is_session_active_on_grid().
        4. Проверить, что возвращается True когда сессия найдена в слотах Grid.
        """
        pass

    def test_is_session_active_on_grid_not_found(self, app: Shadowstep):
        """Test _is_session_active_on_grid() returns False when session not in Grid.

        Steps:
        1. Connect to a standalone server (not Grid).
        2. Call _is_session_active_on_grid().
        3. Verify that False is returned.
        4. Verify no exceptions are raised.

        Тест _is_session_active_on_grid() возвращает False когда сессия не в Grid:
        1. Подключиться к standalone серверу (не Grid).
        2. Вызвать _is_session_active_on_grid().
        3. Проверить, что возвращается False.
        4. Проверить, что не возникает исключений.
        """
        pass

    def test_is_session_active_on_grid_request_failure(self, app: Shadowstep):
        """Test _is_session_active_on_grid() handles request failures gracefully.

        Steps:
        1. Mock or simulate a failed HTTP request to /status endpoint.
        2. Call _is_session_active_on_grid().
        3. Verify that False is returned (exception caught internally).
        4. Verify that a warning is logged.

        Тест _is_session_active_on_grid() обрабатывает сбой запроса корректно:
        1. Замокать или симулировать неудачный HTTP запрос к /status endpoint.
        2. Вызвать _is_session_active_on_grid().
        3. Проверить, что возвращается False (исключение перехвачено внутри).
        4. Проверить, что записано предупреждение в лог.
        """
        pass

    def test_is_session_active_on_standalone_legacy_success(self, app: Shadowstep):
        """Test _is_session_active_on_standalone() finds session via legacy /sessions.

        Steps:
        1. Connect to standalone Appium server.
        2. Call _is_session_active_on_standalone().
        3. Verify that True is returned when session_id matches.
        4. Verify the correct endpoint (/sessions) is queried.

        Тест _is_session_active_on_standalone() находит сессию через legacy /sessions:
        1. Подключиться к standalone Appium серверу.
        2. Вызвать _is_session_active_on_standalone().
        3. Проверить, что возвращается True когда session_id совпадает.
        4. Проверить, что запрашивается правильный endpoint (/sessions).
        """
        pass

    def test_is_session_active_on_standalone_legacy_not_found(self, app: Shadowstep):
        """Test _is_session_active_on_standalone() returns False when no session found.

        Steps:
        1. Disconnect from server or ensure no matching session.
        2. Call _is_session_active_on_standalone().
        3. Verify that False is returned.
        4. Verify no exceptions are raised.

        Тест _is_session_active_on_standalone() возвращает False когда сессия не найдена:
        1. Отключиться от сервера или убедиться, что нет совпадающей сессии.
        2. Вызвать _is_session_active_on_standalone().
        3. Проверить, что возвращается False.
        4. Проверить, что не возникает исключений.
        """
        pass

    def test_is_session_active_on_standalone_legacy_request_exception(self, app: Shadowstep):
        """Test _is_session_active_on_standalone() handles exceptions gracefully.

        Steps:
        1. Mock or cause a request exception (network error, timeout).
        2. Call _is_session_active_on_standalone().
        3. Verify that False is returned.
        4. Verify exception is logged and caught.

        Тест _is_session_active_on_standalone() обрабатывает исключения корректно:
        1. Замокать или вызвать исключение запроса (ошибка сети, таймаут).
        2. Вызвать _is_session_active_on_standalone().
        3. Проверить, что возвращается False.
        4. Проверить, что исключение залогировано и перехвачено.
        """
        pass

    def test_is_session_active_on_standalone_new_style_success(self, app: Shadowstep):
        """Test _is_session_active_on_standalone_new_style() with /appium/sessions.

        Steps:
        1. Connect to Appium server supporting new-style endpoint.
        2. Call _is_session_active_on_standalone_new_style().
        3. Verify that True is returned when session is found.
        4. Verify the /appium/sessions endpoint is queried.

        Тест _is_session_active_on_standalone_new_style() с /appium/sessions:
        1. Подключиться к Appium серверу, поддерживающему новый endpoint.
        2. Вызвать _is_session_active_on_standalone_new_style().
        3. Проверить, что возвращается True когда сессия найдена.
        4. Проверить, что запрашивается endpoint /appium/sessions.
        """
        pass

    def test_is_session_active_on_standalone_new_style_not_found(self, app: Shadowstep):
        """Test _is_session_active_on_standalone_new_style() when no session exists.

        Steps:
        1. Disconnect or ensure no matching session.
        2. Call _is_session_active_on_standalone_new_style().
        3. Verify that False is returned.
        4. Verify no exceptions are raised.

        Тест _is_session_active_on_standalone_new_style() когда сессии нет:
        1. Отключиться или убедиться, что нет совпадающей сессии.
        2. Вызвать _is_session_active_on_standalone_new_style().
        3. Проверить, что возвращается False.
        4. Проверить, что не возникает исключений.
        """
        pass

    def test_is_session_active_on_standalone_new_style_request_exception(self, app: Shadowstep):
        """Test _is_session_active_on_standalone_new_style() handles exceptions.

        Steps:
        1. Mock or cause a network/timeout exception.
        2. Call _is_session_active_on_standalone_new_style().
        3. Verify that False is returned.
        4. Verify exception is logged.

        Тест _is_session_active_on_standalone_new_style() обрабатывает исключения:
        1. Замокать или вызвать исключение сети/таймаута.
        2. Вызвать _is_session_active_on_standalone_new_style().
        3. Проверить, что возвращается False.
        4. Проверить, что исключение залогировано.
        """
        pass

    def test_wait_for_session_id_success(self, app: Shadowstep):
        """Test _wait_for_session_id() successfully waits for session_id assignment.

        Steps:
        1. Connect to Appium and trigger _wait_for_session_id().
        2. Verify that method returns when session_id is assigned.
        3. Verify that the session_id is not None.
        4. Verify that the timeout is not exceeded.

        Тест _wait_for_session_id() успешно ждёт назначения session_id:
        1. Подключиться к Appium и запустить _wait_for_session_id().
        2. Проверить, что метод возвращает результат когда session_id назначен.
        3. Проверить, что session_id не None.
        4. Проверить, что таймаут не превышен.
        """
        pass

    def test_wait_for_session_id_timeout(self, app: Shadowstep):
        """Test _wait_for_session_id() raises RuntimeError on timeout.

        Steps:
        1. Mock a scenario where session_id is never assigned.
        2. Call _wait_for_session_id() with a short timeout.
        3. Verify that RuntimeError is raised with appropriate message.
        4. Verify that the error message mentions timeout.

        Тест _wait_for_session_id() выбрасывает RuntimeError при таймауте:
        1. Замокать сценарий, где session_id никогда не назначается.
        2. Вызвать _wait_for_session_id() с коротким таймаутом.
        3. Проверить, что возникает RuntimeError с соответствующим сообщением.
        4. Проверить, что сообщение об ошибке упоминает таймаут.
        """
        pass

    def test_wait_for_session_id_custom_timeout(self, app: Shadowstep):
        """Test _wait_for_session_id() respects custom timeout value.

        Steps:
        1. Call _wait_for_session_id() with a custom timeout (e.g., 5 seconds).
        2. Verify that method waits for the specified duration before timing out.
        3. Verify that timeout value is honored.

        Тест _wait_for_session_id() учитывает кастомное значение таймаута:
        1. Вызвать _wait_for_session_id() с кастомным таймаутом (например, 5 секунд).
        2. Проверить, что метод ожидает указанную длительность до таймаута.
        3. Проверить, что значение таймаута учитывается.
        """
        pass

    def test_get_ignored_dirs_returns_system_paths(self, app: Shadowstep):
        """Test _get_ignored_dirs() returns system and virtual environment paths.

        Steps:
        1. Call _get_ignored_dirs().
        2. Verify that the returned set contains typical system directories.
        3. Verify that virtual environment paths are included.
        4. Verify that common directories like __pycache__, .venv, .idea are included.

        Тест _get_ignored_dirs() возвращает системные пути и пути виртуального окружения:
        1. Вызвать _get_ignored_dirs().
        2. Проверить, что возвращаемое множество содержит типичные системные директории.
        3. Проверить, что пути виртуального окружения включены.
        4. Проверить, что общие директории типа __pycache__, .venv, .idea включены.
        """
        pass

    def test_get_ignored_dirs_handles_invalid_paths(self, app: Shadowstep):
        """Test _get_ignored_dirs() handles invalid or non-existent paths gracefully.

        Steps:
        1. Mock sys.path to include non-existent or invalid paths.
        2. Call _get_ignored_dirs().
        3. Verify that no exceptions are raised.
        4. Verify that only valid paths are processed.

        Тест _get_ignored_dirs() обрабатывает невалидные или несуществующие пути:
        1. Замокать sys.path чтобы включить несуществующие или невалидные пути.
        2. Вызвать _get_ignored_dirs().
        3. Проверить, что не возникает исключений.
        4. Проверить, что обрабатываются только валидные пути.
        """
        pass

    def test_connect_with_invalid_ip_address(self, app: Shadowstep):
        """Test connect() with invalid IP address raises appropriate exception.

        Steps:
        1. Attempt to connect with an invalid IP address (e.g., "999.999.999.999").
        2. Verify that an exception is raised (WebDriverException or similar).
        3. Verify that driver remains None or is not initialized.
        4. Verify that connection state is not established.

        Тест connect() с невалидным IP адресом выбрасывает соответствующее исключение:
        1. Попытаться подключиться с невалидным IP адресом (например, "999.999.999.999").
        2. Проверить, что возникает исключение (WebDriverException или подобное).
        3. Проверить, что driver остаётся None или не инициализирован.
        4. Проверить, что состояние подключения не установлено.
        """
        pass

    def test_connect_with_unreachable_server(self, app: Shadowstep):
        """Test connect() when Appium server is unreachable.

        Steps:
        1. Attempt to connect to a non-existent server (e.g., wrong port).
        2. Verify that a connection exception is raised.
        3. Verify that driver is not initialized.
        4. Verify that appropriate error message is present.

        Тест connect() когда Appium сервер недоступен:
        1. Попытаться подключиться к несуществующему серверу (например, неправильный порт).
        2. Проверить, что возникает исключение подключения.
        3. Проверить, что driver не инициализирован.
        4. Проверить, что присутствует соответствующее сообщение об ошибке.
        """
        pass

    def test_connect_with_invalid_capabilities(self, app: Shadowstep):
        """Test connect() with invalid or malformed capabilities.

        Steps:
        1. Attempt to connect with invalid capabilities (e.g., missing required fields).
        2. Verify that an exception is raised during connection.
        3. Verify that driver is not successfully initialized.
        4. Verify error message indicates capability issue.

        Тест connect() с невалидными или неправильно сформированными capabilities:
        1. Попытаться подключиться с невалидными capabilities (например, отсутствуют обязательные поля).
        2. Проверить, что возникает исключение при подключении.
        3. Проверить, что driver не инициализирован успешно.
        4. Проверить, что сообщение об ошибке указывает на проблему с capabilities.
        """
        pass

    def test_connect_with_ssh_credentials(self, app: Shadowstep):
        """Test connect() with SSH user and password initializes Transport, Terminal, Adb.

        Steps:
        1. Disconnect if already connected.
        2. Connect with ssh_user and ssh_password parameters.
        3. Verify that self.transport is initialized and not None.
        4. Verify that self.terminal is initialized and not None.
        5. Verify that self.adb is initialized and not None.
        6. Verify that Transport is initialized with correct credentials.

        Тест connect() с SSH credentials инициализирует Transport, Terminal, Adb:
        1. Отключиться если уже подключены.
        2. Подключиться с параметрами ssh_user и ssh_password.
        3. Проверить, что self.transport инициализирован и не None.
        4. Проверить, что self.terminal инициализирован и не None.
        5. Проверить, что self.adb инициализирован и не None.
        6. Проверить, что Transport инициализирован с правильными credentials.
        """
        pass

    def test_connect_with_custom_command_executor(self, app: Shadowstep):
        """Test connect() with custom command_executor URL.

        Steps:
        1. Disconnect if connected.
        2. Connect with a custom command_executor URL.
        3. Verify that self.command_executor matches the provided URL.
        4. Verify that connection is established successfully.
        5. Verify that driver uses the custom command_executor.

        Тест connect() с кастомным command_executor URL:
        1. Отключиться если подключены.
        2. Подключиться с кастомным command_executor URL.
        3. Проверить, что self.command_executor совпадает с предоставленным URL.
        4. Проверить, что подключение установлено успешно.
        5. Проверить, что driver использует кастомный command_executor.
        """
        pass

    def test_connect_without_ssh_credentials_no_transport(self, app: Shadowstep):
        """Test connect() without SSH credentials does not initialize Transport.

        Steps:
        1. Disconnect if connected.
        2. Connect without ssh_user and ssh_password.
        3. Verify that self.transport remains None.
        4. Verify that self.terminal is still initialized (doesn't require Transport).
        5. Verify that self.adb is still initialized (doesn't require Transport).

        Тест connect() без SSH credentials не инициализирует Transport:
        1. Отключиться если подключены.
        2. Подключиться без ssh_user и ssh_password.
        3. Проверить, что self.transport остаётся None.
        4. Проверить, что self.terminal всё равно инициализирован (не требует Transport).
        5. Проверить, что self.adb всё равно инициализирован (не требует Transport).
        """
        pass

    def test_disconnect_with_no_driver(self, app: Shadowstep):
        """Test disconnect() when driver is None or already disconnected.

        Steps:
        1. Ensure driver is None (disconnect first if needed).
        2. Call disconnect().
        3. Verify that no exceptions are raised.
        4. Verify that the method completes successfully.

        Тест disconnect() когда driver равен None или уже отключен:
        1. Убедиться, что driver равен None (сначала отключиться если нужно).
        2. Вызвать disconnect().
        3. Проверить, что не возникает исключений.
        4. Проверить, что метод завершается успешно.
        """
        pass

    def test_disconnect_handles_no_such_driver_exception(self, app: Shadowstep):
        """Test disconnect() handles NoSuchDriverException gracefully.

        Steps:
        1. Mock or simulate a scenario where NoSuchDriverException is raised.
        2. Call disconnect().
        3. Verify that exception is caught and handled.
        4. Verify that driver is set to None.
        5. Verify that WebDriverSingleton is cleared.

        Тест disconnect() обрабатывает NoSuchDriverException корректно:
        1. Замокать или симулировать сценарий, где возникает NoSuchDriverException.
        2. Вызвать disconnect().
        3. Проверить, что исключение перехвачено и обработано.
        4. Проверить, что driver установлен в None.
        5. Проверить, что WebDriverSingleton очищен.
        """
        pass

    def test_disconnect_request_failure(self, app: Shadowstep):
        """Test disconnect() when DELETE request to session fails.

        Steps:
        1. Establish a connection.
        2. Mock or simulate a failed DELETE request.
        3. Call disconnect().
        4. Verify that exception is handled appropriately.
        5. Verify that driver.quit() is still called.
        6. Verify that cleanup occurs despite request failure.

        Тест disconnect() когда DELETE запрос к сессии не удаётся:
        1. Установить подключение.
        2. Замокать или симулировать неудачный DELETE запрос.
        3. Вызвать disconnect().
        4. Проверить, что исключение обработано соответствующим образом.
        5. Проверить, что driver.quit() всё равно вызван.
        6. Проверить, что очистка происходит несмотря на сбой запроса.
        """
        pass

    def test_reconnect_without_initial_connect(self, app: Shadowstep):
        """Test reconnect() behavior when no previous connection parameters exist.

        Steps:
        1. Create a fresh Shadowstep instance without calling connect().
        2. Call reconnect().
        3. Verify that reconnect handles missing connection parameters gracefully.
        4. Verify appropriate behavior (no-op or exception).

        Тест reconnect() когда отсутствуют параметры предыдущего подключения:
        1. Создать новый экземпляр Shadowstep без вызова connect().
        2. Вызвать reconnect().
        3. Проверить, что reconnect корректно обрабатывает отсутствующие параметры подключения.
        4. Проверить соответствующее поведение (no-op или исключение).
        """
        pass

    def test_reconnect_when_server_becomes_unavailable(self, app: Shadowstep):
        """Test reconnect() when Appium server becomes unavailable.

        Steps:
        1. Establish initial connection.
        2. Simulate server becoming unavailable (stop server or block connection).
        3. Call reconnect().
        4. Verify that appropriate exception is raised.
        5. Verify that connection state reflects failure.

        Тест reconnect() когда Appium сервер становится недоступным:
        1. Установить начальное подключение.
        2. Симулировать недоступность сервера (остановить сервер или блокировать подключение).
        3. Вызвать reconnect().
        4. Проверить, что возникает соответствующее исключение.
        5. Проверить, что состояние подключения отражает сбой.
        """
        pass

    def test_reconnect_preserves_all_connection_parameters(self, app: Shadowstep):
        """Test reconnect() preserves all original connection parameters.

        Steps:
        1. Connect with specific parameters (server_ip, port, capabilities, options, etc.).
        2. Call reconnect().
        3. Verify that all parameters are preserved in the new connection.
        4. Verify that server_ip, server_port, capabilities, options match original values.
        5. Verify that SSH credentials are preserved if provided.

        Тест reconnect() сохраняет все исходные параметры подключения:
        1. Подключиться с определёнными параметрами (server_ip, port, capabilities, options и т.д.).
        2. Вызвать reconnect().
        3. Проверить, что все параметры сохранены в новом подключении.
        4. Проверить, что server_ip, server_port, capabilities, options совпадают с исходными значениями.
        5. Проверить, что SSH credentials сохранены если были предоставлены.
        """
        pass

    def test_is_connected_with_multiple_check_methods(self, app: Shadowstep):
        """Test is_connected() correctly evaluates all three check methods.

        Steps:
        1. Connect to server (Grid, standalone legacy, or standalone new style).
        2. Call is_connected().
        3. Verify that method returns True when any of the three checks succeeds.
        4. Mock scenarios where each method returns False/True individually.
        5. Verify logical OR behavior across all three checks.

        Тест is_connected() корректно оценивает все три метода проверки:
        1. Подключиться к серверу (Grid, standalone legacy или standalone new style).
        2. Вызвать is_connected().
        3. Проверить, что метод возвращает True когда любая из трёх проверок успешна.
        4. Замокать сценарии, где каждый метод возвращает False/True индивидуально.
        5. Проверить поведение логического ИЛИ для всех трёх проверок.
        """
        pass

    def test_get_driver_returns_singleton_instance(self, app: Shadowstep):
        """Test get_driver() returns the singleton WebDriver instance.

        Steps:
        1. Establish connection.
        2. Call get_driver() multiple times.
        3. Verify that the same instance is returned each time.
        4. Verify that the instance matches WebDriverSingleton.get_driver().

        Тест get_driver() возвращает singleton экземпляр WebDriver:
        1. Установить подключение.
        2. Вызвать get_driver() несколько раз.
        3. Проверить, что каждый раз возвращается один и тот же экземпляр.
        4. Проверить, что экземпляр совпадает с WebDriverSingleton.get_driver().
        """
        pass

    def test_capabilities_to_options_boundary_timeout_values(self, app: Shadowstep):
        """Test _capabilities_to_options with boundary timeout values (0, max int).

        Steps:
        1. Set capabilities with boundary timeout values (0, very large numbers).
        2. Call _capabilities_to_options().
        3. Verify that boundary values are converted correctly.
        4. Verify that no overflow or conversion errors occur.

        Тест _capabilities_to_options с граничными значениями таймаутов (0, max int):
        1. Установить capabilities с граничными значениями таймаутов (0, очень большие числа).
        2. Вызвать _capabilities_to_options().
        3. Проверить, что граничные значения конвертируются корректно.
        4. Проверить, что не возникает переполнений или ошибок конвертации.
        """
        pass

    def test_capabilities_to_options_with_empty_capabilities(self, app: Shadowstep):
        """Test _capabilities_to_options with empty capabilities dictionary.

        Steps:
        1. Set app.capabilities to an empty dictionary {}.
        2. Set app.options to None.
        3. Call _capabilities_to_options().
        4. Verify that options is initialized to UiAutomator2Options instance.
        5. Verify that no errors occur with empty capabilities.

        Тест _capabilities_to_options с пустым словарём capabilities:
        1. Установить app.capabilities в пустой словарь {}.
        2. Установить app.options в None.
        3. Вызвать _capabilities_to_options().
        4. Проверить, что options инициализирован экземпляром UiAutomator2Options.
        5. Проверить, что не возникает ошибок при пустых capabilities.
        """
        pass

    def test_capabilities_to_options_with_unknown_capability(self, app: Shadowstep):
        """Test _capabilities_to_options with unknown/unsupported capability keys.

        Steps:
        1. Set capabilities with unknown keys (e.g., "appium:unknownKey": "value").
        2. Call _capabilities_to_options().
        3. Verify that method completes without errors.
        4. Verify that unknown keys are ignored gracefully.

        Тест _capabilities_to_options с неизвестными/неподдерживаемыми ключами capability:
        1. Установить capabilities с неизвестными ключами (например, "appium:unknownKey": "value").
        2. Вызвать _capabilities_to_options().
        3. Проверить, что метод завершается без ошибок.
        4. Проверить, что неизвестные ключи игнорируются корректно.
        """
        pass
