import gc
import importlib
import json
import os
import sys
import time
import typing
from pathlib import Path
from types import ModuleType

import requests
import inspect
from loguru import logger
from typing import Union, List, Optional, Set

from appium.options.android import UiAutomator2Options
from appium.options.common import AppiumOptions

from appium import webdriver
from appium.webdriver.webdriver import WebDriver
from icecream import ic
from selenium.common.exceptions import NoSuchDriverException, WebDriverException, InvalidSessionIdException

from shadowstep.navigator.navigator import PageNavigator
from shadowstep.page_base import PageBase
from shadowstep.terminal.adb import Adb
from shadowstep.terminal.terminal import Terminal
from shadowstep.terminal.transport import Transport


class AppiumDisconnectedError(Exception):
    def __init__(
            self, msg: Optional[str] = None, screen: Optional[str] = None,
            stacktrace: Optional[typing.Sequence[str]] = None
    ) -> None:
        super().__init__(msg, screen, stacktrace)


class WebDriverSingleton(WebDriver):
    _instance = None
    _driver = None
    _command_executor = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._driver = webdriver.Remote(*args, **kwargs)
            cls._command_executor = kwargs['command_executor']
        return cls._driver

    @classmethod
    def _get_session_id(cls, kwargs):
        logger.info(f"{inspect.currentframe().f_code.co_name}")
        res = requests.get(kwargs['command_executor'] + '/sessions')
        res_json = json.loads(res.text)
        sessions = res_json.get("value", [])
        if sessions:
            for session in sessions:
                return session["id"]

    @classmethod
    def clear_instance(cls):
        """Удаляет текущий экземпляр и очищает ресурсы WebDriverSingleton."""
        logger.info(f"{inspect.currentframe().f_code.co_name}")
        cls._driver = None
        cls._instance = None  # Убирает ссылку на экземпляр для высвобождения памяти
        gc.collect()

    @classmethod
    def get_driver(cls):
        """
        Get the WebDriver instance.

        Returns:
            WebDriver
                The current WebDriver instance.
        """
        logger.info(f"{inspect.currentframe().f_code.co_name}")
        return cls._driver


class ShadowstepBase:
    pages: typing.Dict[str, typing.Type[PageBase]] = {}

    def __init__(self):
        self.adb = Adb()
        self.navigator = PageNavigator(self)
        self.logger = logger
        self.driver: WebDriver = None
        self.server_ip: str = None
        self.server_port: int = None
        self.capabilities: dict = None
        self.options: UiAutomator2Options = None
        self.keep_alive: bool = None
        self.direct_connection: bool = None
        self.extensions: Optional[List['WebDriver']] = None
        self.strict_ssl: bool = None
        self.ssh_password: str = None
        self.ssh_user: str = None
        self.ssh_port = 22
        self.command_executor: str = None
        self.transport: Transport = None
        self.terminal: Terminal = None
        self._ignored_auto_discover_dirs = {"__pycache__", ".venv", "venv", "site-packages", "dist-packages", ".git", "build", "dist", ".idea", ".pytest_cache", "results"}
        self._ignored_base_path_parts = {"site-packages", "dist-packages", ".venv", "venv", "python", "Python", "Python39"}
        self._auto_discover_pages()

    def _auto_discover_pages(self):
        """Automatically import and register all PageBase subclasses from all 'pages' directories in sys.path."""
        self.logger.debug(f"📂 sys.path: {list(set(sys.path))}")
        for base_path in map(Path, list(set(sys.path))):
            base_str = str(base_path).lower()
            # ❌ фильтруем вредные base_path
            if any(part in base_str for part in self._ignored_base_path_parts):
                self.logger.debug(f"⛔ Пропуск base_path (из IGNORED_BASE_PATH_PARTS): {base_path}")
                continue
            if not base_path.exists() or not base_path.is_dir():
                continue
            self.logger.debug(f"📂 base_path: base_path={base_path}")
            for dirpath, dirs, filenames in os.walk(base_path):
                dir_name = Path(dirpath).name
                # ❌ исключаем вложенные директории
                dirs[:] = [d for d in dirs if d not in self._ignored_auto_discover_dirs]
                self.logger.debug(f"📂 Обход директории: {dirpath}")
                if dir_name in self._ignored_auto_discover_dirs:
                    self.logger.debug(f"⏭ Пропуск (игнорируемая директория): {dirpath}")
                    continue
                for file in filenames:
                    if file.startswith("page") and file.endswith(".py"):
                        try:
                            file_path = Path(dirpath) / file
                            rel_path = file_path.relative_to(base_path).with_suffix('')
                            module_name = ".".join(rel_path.parts)

                            self.logger.debug(f"📦 Импорт модуля: {module_name}")
                            module = importlib.import_module(module_name)
                            self._register_pages_from_module(module)
                        except Exception as e:
                            self.logger.warning(f"⚠️ Ошибка импорта {file}: {e}")


    def _register_pages_from_module(self, module: ModuleType):
        self.logger.debug(f"📥 Регистрация страниц из модуля: {module.__name__}")
        try:
            members = inspect.getmembers(module)
            self.logger.debug(f"🔍 Найдено членов в модуле: {len(members)}")
            for name, obj in members:
                self.logger.debug(f"➡️ Проверка: {name} ({type(obj)})")
                if not inspect.isclass(obj):
                    self.logger.debug(f"⏭ Пропуск — не класс: {name}")
                    continue
                if not issubclass(obj, PageBase):
                    self.logger.debug(f"⏭ Пропуск — не наследует PageBase: {name}")
                    continue
                if obj is PageBase:
                    self.logger.debug(f"⏭ Пропуск — базовый абстрактный PageBase: {name}")
                    continue
                if not name.startswith("Page"):
                    self.logger.debug(f"⏭ Пропуск — имя не начинается с 'Page': {name}")
                    continue
                self.logger.debug(f"✅ Подходит: {name} — регистрация")
                self.pages[name] = obj
                page_instance = obj(app=self)
                edges = list(page_instance.edges.keys())
                self.logger.debug(f"🔗 Навигационные связи: {edges}")
                self.navigator.add_page(page_instance, edges)
        except Exception as e:
            self.logger.error(f"❌ Ошибка при регистрации страниц из модуля {module.__name__}: {e}")

    def list_registered_pages(self) -> None:
        """Log all registered page classes."""
        self.logger.info("=== Registered Pages ===")
        for name, cls in self.pages.items():
            self.logger.info(f"{name}: {cls.__module__}.{cls.__name__}")

    def get_page(self, name: str) -> PageBase:
        cls = self.pages.get(name)
        if not cls:
            raise ValueError(f"Page '{name}' not found in registered pages.")
        return cls(app=self)

    def resolve_page(self, name: str) -> PageBase:
        cls = self.pages.get(name)
        if cls:
            return cls(app=self)
        raise ValueError(f"Page '{name}' not found.")

    def connect(self,
                server_ip: str = '127.0.0.1',
                server_port: int = 4723,
                capabilities: dict = None,
                options: Union[AppiumOptions, List[AppiumOptions], None] = None,
                keep_alive: bool = True,
                direct_connection: bool = True,
                extensions: Optional[List['WebDriver']] = None,
                strict_ssl: bool = True,
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
            keep_alive : bool, optional
                Whether to keep the connection alive after a session ends. Defaults to True.
            direct_connection : bool, optional
                Whether to use direct connection without intermediate proxies. Defaults to True.
            extensions : Optional[List[WebDriver]], optional
                An optional list of WebDriver extensions.
            strict_ssl : bool, optional
                Whether to enforce strict SSL certificates handling. Defaults to True.
            ssh_user : str, optional
                The SSH username for connecting via SSH, if applicable.
            ssh_password : str, optional
                The SSH password for connecting via SSH, if applicable.
            command_executor: str
                URL address of appium server entry point

        Returns:
            None
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        # if provided caps instead options, redeclare caps to options
        # see https://github.com/appium/appium-uiautomator2-driver
        if capabilities is not None and options is None:
            options = UiAutomator2Options()

            # General

            if "platformName" in capabilities.keys():
                options.platform_name = capabilities["platformName"]
            if "appium:automationName" in capabilities.keys():
                options.automation_name = capabilities["appium:automationName"]
            if "appium:deviceName" in capabilities.keys():
                options.device_name = capabilities["appium:deviceName"]
            if "appium:platformVersion" in capabilities.keys():
                options.platform_version = capabilities["appium:platformVersion"]
            if "appium:UDID" in capabilities.keys():
                options.udid = capabilities["appium:UDID"]
            if "appium:udid" in capabilities.keys():
                options.udid = capabilities["appium:udid"]
            if "appium:noReset" in capabilities.keys():
                options.no_reset = capabilities["appium:noReset"]
            if "appium:fullReset" in capabilities.keys():
                options.full_reset = capabilities["appium:fullReset"]
            if "appium:printPageSourceOnFindFailure" in capabilities.keys():
                options.print_page_source_on_find_failure = capabilities["appium:printPageSourceOnFindFailure"]

            # Driver/Server

            if "appium:systemPort" in capabilities.keys():
                options.system_port = capabilities["appium:systemPort"]
            if "appium:skipServerInstallation" in capabilities.keys():
                options.skip_server_installation = capabilities["appium:skipServerInstallation"]
            if "appium:uiautomator2ServerLaunchTimeout" in capabilities.keys():
                options.uiautomator2_server_launch_timeout = capabilities["appium:uiautomator2ServerLaunchTimeout"]
            if "appium:uiautomator2ServerInstallTimeout" in capabilities.keys():
                options.uiautomator2_server_install_timeout = capabilities["appium:uiautomator2ServerInstallTimeout"]
            if "appium:uiautomator2ServerReadTimeout" in capabilities.keys():
                options.uiautomator2_server_read_timeout = capabilities["appium:uiautomator2ServerReadTimeout"]
            if "appium:disableWindowAnimation" in capabilities.keys():
                options.disable_window_animation = capabilities["appium:disableWindowAnimation"]
            if "appium:skipDeviceInitialization" in capabilities.keys():
                options.skip_device_initialization = capabilities["appium:skipDeviceInitialization"]

            # App
            "appium:dontStopAppOnReset"  # didn't find it in options
            "appium:forceAppLaunch"
            "appium:shouldTerminateApp"
            "appium:autoLaunch"

            if "appium:app" in capabilities.keys():
                options.app = capabilities["appium:app"]
            if "browserName" in capabilities.keys():
                options.browser_name = capabilities["browserName"]
            if "appium:appPackage" in capabilities.keys():
                options.app_package = capabilities["appium:appPackage"]
            if "appium:appActivity" in capabilities.keys():
                options.app_activity = capabilities["appium:appActivity"]
            if "appium:appWaitActivity" in capabilities.keys():
                options.app_wait_activity = capabilities["appium:appWaitActivity"]
            if "appium:appWaitPackage" in capabilities.keys():
                options.app_wait_package = capabilities["appium:appWaitPackage"]
            if "appium:appWaitDuration" in capabilities.keys():
                options.app_wait_duration = capabilities["appium:appWaitDuration"]
            if "appium:androidInstallTimeout" in capabilities.keys():
                options.android_install_timeout = capabilities["appium:androidInstallTimeout"]
            if "appium:appWaitForLaunch" in capabilities.keys():
                options.app_wait_for_launch = capabilities["appium:appWaitForLaunch"]
            if "appium:intentCategory" in capabilities.keys():
                options.intent_category = capabilities["appium:intentCategory"]
            if "appium:intentAction" in capabilities.keys():
                options.intent_action = capabilities["appium:intentAction"]
            if "appium:intentFlags" in capabilities.keys():
                options.intent_flags = capabilities["appium:intentFlags"]
            if "appium:optionalIntentArguments" in capabilities.keys():
                options.optional_intent_arguments = capabilities["appium:optionalIntentArguments"]
            if "appium:autoGrantPermissions" in capabilities.keys():
                options.auto_grant_permissions = capabilities["appium:autoGrantPermissions"]
            if "appium:otherApps" in capabilities.keys():
                options.other_apps = capabilities["appium:otherApps"]
            if "appium:uninstallOtherPackages" in capabilities.keys():
                options.uninstall_other_packages = capabilities["appium:uninstallOtherPackages"]
            if "appium:allowTestPackages" in capabilities.keys():
                options.allow_test_packages = capabilities["appium:allowTestPackages"]
            if "appium:remoteAppsCacheLimit" in capabilities.keys():
                options.remote_apps_cache_limit = capabilities["appium:remoteAppsCacheLimit"]
            if "appium:enforceAppInstall" in capabilities.keys():
                options.enforce_app_install = capabilities["appium:enforceAppInstall"]

            # App Localization

            if "appium:localeScript" in capabilities.keys():
                options.locale_script = capabilities["appium:localeScript"]
            if "appium:language" in capabilities.keys():
                options.language = capabilities["appium:language"]
            if "appium:locale" in capabilities.keys():
                options.locale = capabilities["appium:locale"]

            # ADB
            "appium:hideKeyboard"  # didn't find it in options

            if "appium:adbPort" in capabilities.keys():
                options.adb_port = capabilities["appium:adbPort"]
            if "appium:remoteAdbHost" in capabilities.keys():
                options.remote_adb_host = capabilities["appium:remoteAdbHost"]
            if "appium:adbExecTimeout" in capabilities.keys():
                options.adb_exec_timeout = capabilities["appium:adbExecTimeout"]
            if "appium:clearDeviceLogsOnStart" in capabilities.keys():
                options.clear_device_logs_on_start = capabilities["appium:clearDeviceLogsOnStart"]
            if "appium:buildToolsVersion" in capabilities.keys():
                options.build_tools_version = capabilities["appium:buildToolsVersion"]
            if "appium:skipLogcatCapture" in capabilities.keys():
                options.skip_logcat_capture = capabilities["appium:skipLogcatCapture"]
            if "appium:suppressKillServer" in capabilities.keys():
                options.suppress_kill_server = capabilities["appium:suppressKillServer"]
            if "appium:ignoreHiddenApiPolicyError" in capabilities.keys():
                options.ignore_hidden_api_policy_error = capabilities["appium:ignoreHiddenApiPolicyError"]
            if "appium:mockLocationApp" in capabilities.keys():
                options.mock_location_app = capabilities["appium:mockLocationApp"]
            if "appium:logcatFormat" in capabilities.keys():
                options.logcat_format = capabilities["appium:logcatFormat"]
            if "appium:logcatFilterSpecs" in capabilities.keys():
                options.logcat_filter_specs = capabilities["appium:logcatFilterSpecs"]
            if "appium:allowDelayAdb" in capabilities.keys():
                options.allow_delay_adb = capabilities["appium:allowDelayAdb"]

            # Emulator (Android Virtual Device)
            "appium:injectedImageProperties"  # didn't find it in options

            if "appium:avd" in capabilities.keys():
                options.avd = capabilities["appium:avd"]
            if "appium:avdLaunchTimeout" in capabilities.keys():
                options.avd_launch_timeout = capabilities["appium:avdLaunchTimeout"]
            if "appium:avdReadyTimeout" in capabilities.keys():
                options.avd_ready_timeout = capabilities["appium:avdReadyTimeout"]
            if "appium:avdArgs" in capabilities.keys():
                options.avd_args = capabilities["appium:avdArgs"]
            if "appium:avdEnv" in capabilities.keys():
                options.avd_env = capabilities["appium:avdEnv"]
            if "appium:networkSpeed" in capabilities.keys():
                options.network_speed = capabilities["appium:networkSpeed"]
            if "appium:gpsEnabled" in capabilities.keys():
                options.gps_enabled = capabilities["appium:gpsEnabled"]
            if "appium:isHeadless" in capabilities.keys():
                options.is_headless = capabilities["appium:isHeadless"]

            # App Signing

            if "appium:useKeystore" in capabilities.keys():
                options.use_keystore = capabilities["appium:useKeystore"]
            if "appium:keystorePath" in capabilities.keys():
                options.keystore_path = capabilities["appium:keystorePath"]
            if "appium:keystorePassword" in capabilities.keys():
                options.keystore_password = capabilities["appium:keystorePassword"]
            if "appium:keyAlias" in capabilities.keys():
                options.key_alias = capabilities["appium:keyAlias"]
            if "appium:keyPassword" in capabilities.keys():
                options.key_password = capabilities["appium:keyPassword"]
            if "appium:noSign" in capabilities.keys():
                options.no_sign = capabilities["appium:noSign"]

            # Device Locking

            if "appium:skipUnlock" in capabilities.keys():
                options.skip_unlock = capabilities["appium:skipUnlock"]
            if "appium:unlockType" in capabilities.keys():
                options.unlock_type = capabilities["appium:unlockType"]
            if "appium:unlockKey" in capabilities.keys():
                options.unlock_key = capabilities["appium:unlockKey"]
            if "appium:unlockStrategy" in capabilities.keys():
                options.unlock_strategy = capabilities["appium:unlockStrategy"]
            if "appium:unlockSuccessTimeout" in capabilities.keys():
                options.unlock_success_timeout = capabilities["appium:unlockSuccessTimeout"]

            # MJPEG

            if "appium:mjpegServerPort" in capabilities.keys():
                options.mjpeg_server_port = capabilities["appium:mjpegServerPort"]
            if "appium:mjpegScreenshotUrl" in capabilities.keys():
                options.mjpeg_screenshot_url = capabilities["appium:mjpegScreenshotUrl"]

            # Web Context
            "appium:autoWebviewName"  # didn't find it in options
            "appium:enableWebviewDetailsCollection"

            if "appium:autoWebview" in capabilities.keys():
                options.auto_web_view = capabilities["appium:autoWebview"]
            if "appium:autoWebviewTimeout" in capabilities.keys():
                options.auto_webview_timeout = capabilities["appium:autoWebviewTimeout"]
            if "appium:webviewDevtoolsPort" in capabilities.keys():
                options.webview_devtools_port = capabilities["appium:webviewDevtoolsPort"]
            if "appium:ensureWebviewsHavePages" in capabilities.keys():
                options.ensure_webviews_have_pages = capabilities["appium:ensureWebviewsHavePages"]
            if "appium:chromedriverPort" in capabilities.keys():
                options.chromedriver_port = capabilities["appium:chromedriverPort"]
            if "appium:chromedriverPorts" in capabilities.keys():
                options.chromedriver_ports = capabilities["appium:chromedriverPorts"]
            if "appium:chromedriverArgs" in capabilities.keys():
                options.chromedriver_args = capabilities["appium:chromedriverArgs"]
            if "appium:chromedriverExecutable" in capabilities.keys():
                options.chromedriver_executable = capabilities["appium:chromedriverExecutable"]
            if "appium:chromedriverExecutableDir" in capabilities.keys():
                options.chromedriver_executable_dir = capabilities["appium:chromedriverExecutableDir"]
            if "appium:chromedriverChromeMappingFile" in capabilities.keys():
                options.chromedriver_chrome_mapping_file = capabilities["appium:chromedriverChromeMappingFile"]
            if "appium:chromedriverUseSystemExecutable" in capabilities.keys():
                options.chromedriver_use_system_executable = capabilities["appium:chromedriverUseSystemExecutable"]
            if "appium:chromedriverDisableBuildCheck" in capabilities.keys():
                options.chromedriver_disable_build_check = capabilities["appium:chromedriverDisableBuildCheck"]
            if "appium:recreateChromeDriverSessions" in capabilities.keys():
                options.recreate_chrome_driver_sessions = capabilities["appium:recreateChromeDriverSessions"]
            if "appium:nativeWebScreenshot" in capabilities.keys():
                options.native_web_screenshot = capabilities["appium:nativeWebScreenshot"]
            if "appium:extractChromeAndroidPackageFromContextName" in capabilities.keys():
                options.extract_chrome_android_package_from_context_name = capabilities[
                    "appium:extractChromeAndroidPackageFromContextName"]
            if "appium:showChromedriverLog" in capabilities.keys():
                options.show_chromedriver_log = capabilities["appium:showChromedriverLog"]
            if "pageLoadStrategy" in capabilities.keys():
                options.page_load_strategy = capabilities["pageLoadStrategy"]
            if "appium:chromeOptions" in capabilities.keys():
                options.chrome_options = capabilities["appium:chromeOptions"]
            if "appium:chromeLoggingPrefs" in capabilities.keys():
                options.chrome_logging_prefs = capabilities["appium:chromeLoggingPrefs"]

            # Other
            "appium:timeZone"  # didn't find it in options

            if "appium:disableSuppressAccessibilityService" in capabilities.keys():
                options.disable_suppress_accessibility_service = capabilities[
                    "appium:disableSuppressAccessibilityService"]
            if "appium:userProfile" in capabilities.keys():
                options.user_profile = capabilities["appium:userProfile"]
            if "appium:newCommandTimeout" in capabilities.keys():
                options.new_command_timeout = capabilities["appium:newCommandTimeout"]
            if "appium:skipLogcatCapture" in capabilities.keys():
                options.skip_logcat_capture = capabilities["appium:skipLogcatCapture"]
        command_executor = f'http://{server_ip}:{str(server_port)}/wd/hub' if command_executor is None else command_executor
        self.logger.info(f"Подключение к серверу: {command_executor}")
        self.server_ip = server_ip
        self.server_port = server_port
        self.capabilities = capabilities
        self.options = options
        self.keep_alive = keep_alive
        self.direct_connection = direct_connection
        self.extensions = extensions
        self.strict_ssl = strict_ssl
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.command_executor = command_executor
        self.driver = WebDriverSingleton(command_executor=self.command_executor,
                                         options=self.options,
                                         keep_alive=self.keep_alive,
                                         direct_connection=self.direct_connection,
                                         extensions=self.extensions,
                                         strict_ssl=self.strict_ssl)
        if ssh_user and ssh_password:
            self.transport = Transport(server=self.server_ip,
                                       port=self.ssh_port,
                                       user=self.ssh_user,
                                       password=self.ssh_password)
        self.terminal = Terminal(base=self)


    def disconnect(self) -> None:
        """
        Disconnect from the device using the Appium server.

        Returns:
            None
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            if self.driver:
                response = requests.delete(f"{self.command_executor}/session/{self.driver.session_id}")
                self.logger.info(f"{response=}")
                self.driver.quit()
                self.driver = None
        except InvalidSessionIdException as error:
            self.logger.debug(f"{inspect.currentframe().f_code.co_name} {error}")
            pass
        except NoSuchDriverException as error:
            self.logger.debug(f"{inspect.currentframe().f_code.co_name} {error}")
            pass

    def reconnect(self):
        """
        Reconnect to the device using the Appium server.

        Returns:
            None
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        self.disconnect()
        WebDriverSingleton.clear_instance()
        self.connect(command_executor=self.command_executor,
                     server_ip=self.server_ip,
                     server_port=self.server_port,
                     capabilities=self.capabilities,
                     options=self.options,
                     keep_alive=self.keep_alive,
                     direct_connection=self.direct_connection,
                     extensions=self.extensions,
                     strict_ssl=self.strict_ssl
                     )
        time.sleep(3)

    def is_connected(self) -> bool:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            response = requests.get(f"{self.command_executor}/sessions")
            response_json = response.json().get("value", {})
            response.raise_for_status()
            nodes = response_json
            for node in nodes:
                session_id = node.get("id", None)
                node.get("ready", False)
                if self.driver.session_id == session_id:
                    return True
            return False
        except Exception as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} {error}")
            return False
