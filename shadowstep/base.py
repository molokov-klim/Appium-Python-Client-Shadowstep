# shadowstep/base.py
from __future__ import annotations

import gc
import json
import logging
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import requests
from appium.options.android.uiautomator2.base import UiAutomator2Options
from appium.options.common.base import AppiumOptions
from appium.webdriver.webdriver import WebDriver
from selenium.common import WebDriverException
from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
)

from shadowstep.terminal.adb import Adb
from shadowstep.terminal.terminal import Terminal
from shadowstep.terminal.transport import Transport
from shadowstep.utils.utils import get_current_func_name

logger = logging.getLogger(__name__)


class AppiumDisconnectedError(WebDriverException):
    def __init__(
            self, msg: str | None = None, screen: str | None = None,
            stacktrace: Sequence[str] | None = None
    ) -> None:
        super().__init__(msg, screen, stacktrace)


class WebDriverSingleton(WebDriver):
    _instance = None
    _driver = None
    _command_executor = None

    def __new__(cls, *args: Any, **kwargs: Any):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._driver = WebDriver(*args, **kwargs)
            cls._command_executor = kwargs['command_executor']
        return cls._driver

    @classmethod
    def _get_session_id(cls, kwargs: Any) -> str:
        logger.debug(f"{get_current_func_name()}")
        res = requests.get(kwargs['command_executor'] + '/sessions')
        res_json = json.loads(res.text)
        sessions = res_json.get("value", [])
        if sessions:
            for session in sessions:
                session_id = session.get("id")
                if session_id:
                    return str(session_id)
        return "unknown_session_id"

    @classmethod
    def clear_instance(cls) -> None:
        """Удаляет текущий экземпляр и очищает ресурсы WebDriverSingleton."""
        logger.debug(f"{get_current_func_name()}")
        cls._driver = None
        cls._instance = None  # Убирает ссылку на экземпляр для высвобождения памяти
        gc.collect()

    @classmethod
    def get_driver(cls) -> WebDriver | None:
        """
        Get the WebDriver instance.

        Returns:
            WebDriver
                The current WebDriver instance.
        """
        logger.debug(f"{get_current_func_name()}")
        return cls._driver


class ShadowstepBase:

    def __init__(self):
        self.logger = logger
        self.driver: WebDriver = None
        self.server_ip: str = None
        self.server_port: int = None
        self.capabilities: dict[str, Any] = None
        self.options: UiAutomator2Options = None
        self.extensions: list[WebDriver] = None
        self.ssh_password: str = None
        self.ssh_user: str = None
        self.ssh_port = 22
        self.command_executor: str = None
        self.transport: Transport = None
        self.terminal: Terminal = None
        self.adb: Adb = None
        self._ignored_auto_discover_dirs = {"__pycache__", ".venv", "venv", "site-packages", "dist-packages", ".git",
                                            "build", "dist", ".idea", ".pytest_cache", "results"}
        self._ignored_base_path_parts = self._get_ignored_dirs()

    def connect(self,
                server_ip: str = '127.0.0.1',
                server_port: int = 4723,
                capabilities: dict[str, Any] = None,
                options: AppiumOptions | list[AppiumOptions] | None = None,
                extensions: list[WebDriver] | None = None,
                ssh_user: str = None,
                ssh_password: str = None,
                command_executor: str = None,
                ) -> None:
        """
        Connect to a device using the Appium server and initialize the driver.

        Args:
            server_ip : str, optional
                The IP address of the Appium server. Defaults to '127.0.0.1'.
            server_port : int, optional
                The port of the Appium server. Defaults to 4723.
            capabilities : dict, optional
                A dictionary specifying the desired capabilities for the session.
            options : Union[AppiumOptions, List[AppiumOptions], None], optional
                An instance or a list of instances of AppiumOptions to configure the Appium session.
            extensions : Optional[List[WebDriver]], optional
                An optional list of WebDriver extensions.
            ssh_user : str, optional
                The SSH username for connecting via SSH, if applicable.
            ssh_password : str, optional
                The SSH password for connecting via SSH, if applicable.
            command_executor: str
                URL address of appium server entry point

        Returns:
            None
        """
        self.logger.debug(f"{get_current_func_name()}")
        self.server_ip = server_ip
        self.server_port = server_port
        self.capabilities = capabilities
        self.options = options
        self.extensions = extensions
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.command_executor = command_executor

        self._capabilities_to_options()
        self.command_executor = f'http://{server_ip}:{str(server_port)}/wd/hub' if self.command_executor is None else self.command_executor

        self.logger.info(f"Подключение к серверу: {self.command_executor}")
        self.driver = WebDriverSingleton(command_executor=self.command_executor,
                                         options=self.options,
                                         extensions=self.extensions)
        self._wait_for_session_id()
        self.logger.info("Подключение установлено")
        self.driver.update_settings(settings={"enforceXPath1": True})  # support for others is currently not provided

        # init here because need server ip, port and credentials, refactor it later
        if self.ssh_user and self.ssh_password:
            self.transport = Transport(server=self.server_ip,
                                       port=self.ssh_port,
                                       user=self.ssh_user,
                                       password=self.ssh_password)
        self.terminal = Terminal(base=self)
        self.adb = Adb(base=self)

    def disconnect(self) -> None:
        """
        Disconnect from the device using the Appium server.

        Returns:
            None
        """
        self.logger.debug(f"{get_current_func_name()}")
        try:
            if self.driver:
                response = requests.delete(f"{self.command_executor}/session/{self.driver.session_id}")
                self.logger.info(f"{response=}")
                self.driver.quit()
                self.driver = None
        except InvalidSessionIdException:
            self.logger.debug(f"{get_current_func_name()} InvalidSessionIdException")
            pass
        except NoSuchDriverException:
            self.logger.debug(f"{get_current_func_name()} NoSuchDriverException")
            pass

    def reconnect(self):
        """
        Reconnect to the device using the Appium server.

        Returns:
            None
        """
        self.logger.debug(f"{get_current_func_name()}")
        self.disconnect()
        WebDriverSingleton.clear_instance()
        self.connect(command_executor=self.command_executor,
                     server_ip=self.server_ip,
                     server_port=self.server_port,
                     capabilities=self.capabilities,
                     options=self.options,
                     extensions=self.extensions,
                     ssh_user=self.ssh_user,
                     ssh_password=self.ssh_password
                     )
        time.sleep(3)
        self.driver.update_settings(settings={"enforceXPath1": True})

    def is_connected(self) -> bool:
        """
        Checks whether the current Appium session is active on the grid or standalone server.

        Returns:
            bool: True if the session is active, False otherwise.
        """
        self.logger.debug(f"{get_current_func_name()}")

        step = "Checking session status"
        self.logger.debug(f"[{step}] started")
        return bool(
            self._is_session_active_on_grid() or self._is_session_active_on_standalone() or self._is_session_active_on_standalone_new_style())

    def get_driver(self):
        self.logger.debug(f"{get_current_func_name()}")
        return WebDriverSingleton.get_driver()

    def _is_session_active_on_grid(self) -> bool:
        """
        Checks if the current session is active in the Selenium Grid.

        Returns:
            bool: True if session is active in any slot on the grid, False otherwise.
        """
        self.logger.debug(f"{get_current_func_name()}")

        try:
            step = "Fetching Grid /status"
            self.logger.debug(f"[{step}] started")

            url = f"{self.command_executor}/status"
            response = requests.get(url, timeout=5, verify=False)
            response.raise_for_status()

            grid = response.json()
            nodes = grid.get("value", {}).get("nodes", [])

            step = "Iterating nodes and slots"
            self.logger.debug(f"[{step}] started")
            for node in nodes:
                for slot in node.get("slots", []):
                    session = slot.get("session")
                    if not session:
                        continue
                    session_id = session.get("sessionId")
                    if session_id == self.driver.session_id:
                        self.logger.debug(f"Session found in Grid: {session_id}")
                        return True

            self.logger.debug("Session not found in any Grid slot")
            return False

        except Exception as error:
            self.logger.warning(f"_is_session_active_on_grid failed: {error}")
            return False

    def _is_session_active_on_standalone(self) -> bool:
        """
        Fallback check for standalone Appium server via /sessions endpoint (legacy support).

        Returns:
            bool: True if session is active on standalone Appium, False otherwise.
        """
        self.logger.debug(f"{get_current_func_name()}")
        try:
            response = requests.get(f"{self.command_executor}/sessions")
            response_json = response.json().get("value", {})
            response.raise_for_status()
            nodes = response_json
            for node in nodes:
                session_id = node.get("id", None)
                node.get("ready", False)
                if self.driver.session_id == session_id:
                    self.logger.debug(f"Found session_id on standalone: {session_id}")
                    return True
            return False
        except Exception as error:
            self.logger.debug(f"{get_current_func_name()}: {error}")
            return False

    def _is_session_active_on_standalone_new_style(self) -> bool:
        """
        Fallback check for standalone Appium server via /sessions endpoint (legacy support).

        Returns:
            bool: True if session is active on standalone Appium, False otherwise.
        """
        self.logger.debug(f"{get_current_func_name()}")
        try:
            response = requests.get(f"{self.command_executor}/appium/sessions")
            response_json = response.json().get("value", {})
            response.raise_for_status()
            nodes = response_json
            for node in nodes:
                session_id = node.get("id", None)
                node.get("ready", False)
                if self.driver.session_id == session_id:
                    self.logger.debug(f"Found session_id on standalone: {session_id}")
                    return True
            return False
        except Exception as error:
            self.logger.debug(f"{get_current_func_name()}: {error}")
            return False

    def _wait_for_session_id(self, timeout: int = 30) -> None:
        """
        Waits until WebDriver's session_id is set or times out.

        Args:
            timeout (int): How many seconds to wait before giving up.

        Raises:
            RuntimeError: If session_id was not set within timeout.
        """
        self.logger.info(f"{get_current_func_name()}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            session_id = getattr(self.driver, "session_id", None)
            self.logger.info(f"{self.driver=}")
            self.logger.info(f"{session_id=}")
            if session_id:
                return
            time.sleep(0.5)
            self.driver = WebDriverSingleton.get_driver()
        raise RuntimeError("WebDriver session_id was not assigned in time.")

    def _capabilities_to_options(self):  # noqa: C901
        # if provided caps instead options, redeclare caps to options
        # see https://github.com/appium/appium-uiautomator2-driver
        if self.capabilities is not None and self.options is None:
            self.options = UiAutomator2Options()

            # General
            if "platformName" in self.capabilities.keys():
                self.options.platform_name = self.capabilities["platformName"]
            if "appium:automationName" in self.capabilities.keys():
                self.options.automation_name = self.capabilities["appium:automationName"]
            if "appium:deviceName" in self.capabilities.keys():
                self.options.device_name = self.capabilities["appium:deviceName"]
            if "appium:platformVersion" in self.capabilities.keys():
                self.options.platform_version = self.capabilities["appium:platformVersion"]
            if "appium:UDID" in self.capabilities.keys():
                self.options.udid = self.capabilities["appium:UDID"]
            if "appium:udid" in self.capabilities.keys():
                self.options.udid = self.capabilities["appium:udid"]
            if "appium:noReset" in self.capabilities.keys():
                self.options.no_reset = self.capabilities["appium:noReset"]
            if "appium:fullReset" in self.capabilities.keys():
                self.options.full_reset = self.capabilities["appium:fullReset"]
            if "appium:printPageSourceOnFindFailure" in self.capabilities.keys():
                self.options.print_page_source_on_find_failure = self.capabilities[
                    "appium:printPageSourceOnFindFailure"]

            # Driver/Server
            if "appium:systemPort" in self.capabilities.keys():
                self.options.system_port = self.capabilities["appium:systemPort"]
            if "appium:skipServerInstallation" in self.capabilities.keys():
                self.options.skip_server_installation = self.capabilities["appium:skipServerInstallation"]
            if "appium:uiautomator2ServerLaunchTimeout" in self.capabilities.keys():
                self.options.uiautomator2_server_launch_timeout = self.capabilities[
                    "appium:uiautomator2ServerLaunchTimeout"]
            if "appium:uiautomator2ServerInstallTimeout" in self.capabilities.keys():
                self.options.uiautomator2_server_install_timeout = self.capabilities[
                    "appium:uiautomator2ServerInstallTimeout"]
            if "appium:uiautomator2ServerReadTimeout" in self.capabilities.keys():
                self.options.uiautomator2_server_read_timeout = self.capabilities[
                    "appium:uiautomator2ServerReadTimeout"]
            if "appium:disableWindowAnimation" in self.capabilities.keys():
                self.options.disable_window_animation = self.capabilities["appium:disableWindowAnimation"]
            if "appium:skipDeviceInitialization" in self.capabilities.keys():
                self.options.skip_device_initialization = self.capabilities["appium:skipDeviceInitialization"]

            # App
            "appium:dontStopAppOnReset"  # didn't find it in options
            "appium:forceAppLaunch"
            "appium:shouldTerminateApp"
            "appium:autoLaunch"

            if "appium:app" in self.capabilities.keys():
                self.options.app = self.capabilities["appium:app"]
            if "browserName" in self.capabilities.keys():
                self.options.browser_name = self.capabilities["browserName"]
            if "appium:appPackage" in self.capabilities.keys():
                self.options.app_package = self.capabilities["appium:appPackage"]
            if "appium:appActivity" in self.capabilities.keys():
                self.options.app_activity = self.capabilities["appium:appActivity"]
            if "appium:appWaitActivity" in self.capabilities.keys():
                self.options.app_wait_activity = self.capabilities["appium:appWaitActivity"]
            if "appium:appWaitPackage" in self.capabilities.keys():
                self.options.app_wait_package = self.capabilities["appium:appWaitPackage"]
            if "appium:appWaitDuration" in self.capabilities.keys():
                self.options.app_wait_duration = self.capabilities["appium:appWaitDuration"]
            if "appium:androidInstallTimeout" in self.capabilities.keys():
                self.options.android_install_timeout = self.capabilities["appium:androidInstallTimeout"]
            if "appium:appWaitForLaunch" in self.capabilities.keys():
                self.options.app_wait_for_launch = self.capabilities["appium:appWaitForLaunch"]
            if "appium:intentCategory" in self.capabilities.keys():
                self.options.intent_category = self.capabilities["appium:intentCategory"]
            if "appium:intentAction" in self.capabilities.keys():
                self.options.intent_action = self.capabilities["appium:intentAction"]
            if "appium:intentFlags" in self.capabilities.keys():
                self.options.intent_flags = self.capabilities["appium:intentFlags"]
            if "appium:optionalIntentArguments" in self.capabilities.keys():
                self.options.optional_intent_arguments = self.capabilities["appium:optionalIntentArguments"]
            if "appium:autoGrantPermissions" in self.capabilities.keys():
                self.options.auto_grant_permissions = self.capabilities["appium:autoGrantPermissions"]
            if "appium:otherApps" in self.capabilities.keys():
                self.options.other_apps = self.capabilities["appium:otherApps"]
            if "appium:uninstallOtherPackages" in self.capabilities.keys():
                self.options.uninstall_other_packages = self.capabilities["appium:uninstallOtherPackages"]
            if "appium:allowTestPackages" in self.capabilities.keys():
                self.options.allow_test_packages = self.capabilities["appium:allowTestPackages"]
            if "appium:remoteAppsCacheLimit" in self.capabilities.keys():
                self.options.remote_apps_cache_limit = self.capabilities["appium:remoteAppsCacheLimit"]
            if "appium:enforceAppInstall" in self.capabilities.keys():
                self.options.enforce_app_install = self.capabilities["appium:enforceAppInstall"]

            # App Localization
            if "appium:localeScript" in self.capabilities.keys():
                self.options.locale_script = self.capabilities["appium:localeScript"]
            if "appium:language" in self.capabilities.keys():
                self.options.language = self.capabilities["appium:language"]
            if "appium:locale" in self.capabilities.keys():
                self.options.locale = self.capabilities["appium:locale"]

            # ADB
            "appium:hideKeyboard"  # didn't find it in options

            if "appium:adbPort" in self.capabilities.keys():
                self.options.adb_port = self.capabilities["appium:adbPort"]
            if "appium:remoteAdbHost" in self.capabilities.keys():
                self.options.remote_adb_host = self.capabilities["appium:remoteAdbHost"]
            if "appium:adbExecTimeout" in self.capabilities.keys():
                self.options.adb_exec_timeout = self.capabilities["appium:adbExecTimeout"]
            if "appium:clearDeviceLogsOnStart" in self.capabilities.keys():
                self.options.clear_device_logs_on_start = self.capabilities["appium:clearDeviceLogsOnStart"]
            if "appium:buildToolsVersion" in self.capabilities.keys():
                self.options.build_tools_version = self.capabilities["appium:buildToolsVersion"]
            if "appium:skipLogcatCapture" in self.capabilities.keys():
                self.options.skip_logcat_capture = self.capabilities["appium:skipLogcatCapture"]
            if "appium:suppressKillServer" in self.capabilities.keys():
                self.options.suppress_kill_server = self.capabilities["appium:suppressKillServer"]
            if "appium:ignoreHiddenApiPolicyError" in self.capabilities.keys():
                self.options.ignore_hidden_api_policy_error = self.capabilities["appium:ignoreHiddenApiPolicyError"]
            if "appium:mockLocationApp" in self.capabilities.keys():
                self.options.mock_location_app = self.capabilities["appium:mockLocationApp"]
            if "appium:logcatFormat" in self.capabilities.keys():
                self.options.logcat_format = self.capabilities["appium:logcatFormat"]
            if "appium:logcatFilterSpecs" in self.capabilities.keys():
                self.options.logcat_filter_specs = self.capabilities["appium:logcatFilterSpecs"]
            if "appium:allowDelayAdb" in self.capabilities.keys():
                self.options.allow_delay_adb = self.capabilities["appium:allowDelayAdb"]

            # Emulator (Android Virtual Device)
            "appium:injectedImageProperties"  # didn't find it in options

            if "appium:avd" in self.capabilities.keys():
                self.options.avd = self.capabilities["appium:avd"]
            if "appium:avdLaunchTimeout" in self.capabilities.keys():
                self.options.avd_launch_timeout = self.capabilities["appium:avdLaunchTimeout"]
            if "appium:avdReadyTimeout" in self.capabilities.keys():
                self.options.avd_ready_timeout = self.capabilities["appium:avdReadyTimeout"]
            if "appium:avdArgs" in self.capabilities.keys():
                self.options.avd_args = self.capabilities["appium:avdArgs"]
            if "appium:avdEnv" in self.capabilities.keys():
                self.options.avd_env = self.capabilities["appium:avdEnv"]
            if "appium:networkSpeed" in self.capabilities.keys():
                self.options.network_speed = self.capabilities["appium:networkSpeed"]
            if "appium:gpsEnabled" in self.capabilities.keys():
                self.options.gps_enabled = self.capabilities["appium:gpsEnabled"]
            if "appium:isHeadless" in self.capabilities.keys():
                self.options.is_headless = self.capabilities["appium:isHeadless"]

            # App Signing
            if "appium:useKeystore" in self.capabilities.keys():
                self.options.use_keystore = self.capabilities["appium:useKeystore"]
            if "appium:keystorePath" in self.capabilities.keys():
                self.options.keystore_path = self.capabilities["appium:keystorePath"]
            if "appium:keystorePassword" in self.capabilities.keys():
                self.options.keystore_password = self.capabilities["appium:keystorePassword"]
            if "appium:keyAlias" in self.capabilities.keys():
                self.options.key_alias = self.capabilities["appium:keyAlias"]
            if "appium:keyPassword" in self.capabilities.keys():
                self.options.key_password = self.capabilities["appium:keyPassword"]
            if "appium:noSign" in self.capabilities.keys():
                self.options.no_sign = self.capabilities["appium:noSign"]

            # Device Locking
            if "appium:skipUnlock" in self.capabilities.keys():
                self.options.skip_unlock = self.capabilities["appium:skipUnlock"]
            if "appium:unlockType" in self.capabilities.keys():
                self.options.unlock_type = self.capabilities["appium:unlockType"]
            if "appium:unlockKey" in self.capabilities.keys():
                self.options.unlock_key = self.capabilities["appium:unlockKey"]
            if "appium:unlockStrategy" in self.capabilities.keys():
                self.options.unlock_strategy = self.capabilities["appium:unlockStrategy"]
            if "appium:unlockSuccessTimeout" in self.capabilities.keys():
                self.options.unlock_success_timeout = self.capabilities["appium:unlockSuccessTimeout"]

            # MJPEG
            if "appium:mjpegServerPort" in self.capabilities.keys():
                self.options.mjpeg_server_port = self.capabilities["appium:mjpegServerPort"]
            if "appium:mjpegScreenshotUrl" in self.capabilities.keys():
                self.options.mjpeg_screenshot_url = self.capabilities["appium:mjpegScreenshotUrl"]

            # Web Context
            "appium:autoWebviewName"  # didn't find it in options
            "appium:enableWebviewDetailsCollection"

            if "appium:autoWebview" in self.capabilities.keys():
                self.options.auto_web_view = self.capabilities["appium:autoWebview"]
            if "appium:autoWebviewTimeout" in self.capabilities.keys():
                self.options.auto_webview_timeout = self.capabilities["appium:autoWebviewTimeout"]
            if "appium:webviewDevtoolsPort" in self.capabilities.keys():
                self.options.webview_devtools_port = self.capabilities["appium:webviewDevtoolsPort"]
            if "appium:ensureWebviewsHavePages" in self.capabilities.keys():
                self.options.ensure_webviews_have_pages = self.capabilities["appium:ensureWebviewsHavePages"]
            if "appium:chromedriverPort" in self.capabilities.keys():
                self.options.chromedriver_port = self.capabilities["appium:chromedriverPort"]
            if "appium:chromedriverPorts" in self.capabilities.keys():
                self.options.chromedriver_ports = self.capabilities["appium:chromedriverPorts"]
            if "appium:chromedriverArgs" in self.capabilities.keys():
                self.options.chromedriver_args = self.capabilities["appium:chromedriverArgs"]
            if "appium:chromedriverExecutable" in self.capabilities.keys():
                self.options.chromedriver_executable = self.capabilities["appium:chromedriverExecutable"]
            if "appium:chromedriverExecutableDir" in self.capabilities.keys():
                self.options.chromedriver_executable_dir = self.capabilities["appium:chromedriverExecutableDir"]
            if "appium:chromedriverChromeMappingFile" in self.capabilities.keys():
                self.options.chromedriver_chrome_mapping_file = self.capabilities[
                    "appium:chromedriverChromeMappingFile"]
            if "appium:chromedriverUseSystemExecutable" in self.capabilities.keys():
                self.options.chromedriver_use_system_executable = self.capabilities[
                    "appium:chromedriverUseSystemExecutable"]
            if "appium:chromedriverDisableBuildCheck" in self.capabilities.keys():
                self.options.chromedriver_disable_build_check = self.capabilities[
                    "appium:chromedriverDisableBuildCheck"]
            if "appium:recreateChromeDriverSessions" in self.capabilities.keys():
                self.options.recreate_chrome_driver_sessions = self.capabilities["appium:recreateChromeDriverSessions"]
            if "appium:nativeWebScreenshot" in self.capabilities.keys():
                self.options.native_web_screenshot = self.capabilities["appium:nativeWebScreenshot"]
            if "appium:extractChromeAndroidPackageFromContextName" in self.capabilities.keys():
                self.options.extract_chrome_android_package_from_context_name = self.capabilities[
                    "appium:extractChromeAndroidPackageFromContextName"]
            if "appium:showChromedriverLog" in self.capabilities.keys():
                self.options.show_chromedriver_log = self.capabilities["appium:showChromedriverLog"]
            if "pageLoadStrategy" in self.capabilities.keys():
                self.options.page_load_strategy = self.capabilities["pageLoadStrategy"]
            if "appium:chromeOptions" in self.capabilities.keys():
                self.options.chrome_options = self.capabilities["appium:chromeOptions"]
            if "appium:chromeLoggingPrefs" in self.capabilities.keys():
                self.options.chrome_logging_prefs = self.capabilities["appium:chromeLoggingPrefs"]

            # Other
            "appium:timeZone"  # didn't find it in options

            if "appium:disableSuppressAccessibilityService" in self.capabilities.keys():
                self.options.disable_suppress_accessibility_service = self.capabilities[
                    "appium:disableSuppressAccessibilityService"]
            if "appium:userProfile" in self.capabilities.keys():
                self.options.user_profile = self.capabilities["appium:userProfile"]
            if "appium:newCommandTimeout" in self.capabilities.keys():
                self.options.new_command_timeout = self.capabilities["appium:newCommandTimeout"]
            if "appium:skipLogcatCapture" in self.capabilities.keys():
                self.options.skip_logcat_capture = self.capabilities["appium:skipLogcatCapture"]

    def _get_ignored_dirs(self):
        self.logger.debug(get_current_func_name())
        system_paths = {Path(p).resolve().name for p in sys.path if p}
        ignored_names = {
            "venv", ".venv", "env", ".env", "Scripts", "bin", "lib", "include",
            "__pycache__", ".idea", ".vscode", "build", "dist", "dlls"
        }
        return system_paths.union(ignored_names)
