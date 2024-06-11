import inspect
import logging
from typing import Union, List, Optional

from appium.options.android import UiAutomator2Options
from appium.options.common import AppiumOptions

from appium import webdriver
from appium.webdriver.webdriver import WebDriver

from shadowstep.terminal.terminal import Terminal


class WebDriverSingleton(WebDriver):
    _instance = None
    _driver = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._driver = webdriver.Remote(*args, **kwargs)
        return cls._driver

    @classmethod
    def get_driver(cls):
        return cls._driver


class SBase:
    def __init__(self):
        self.driver = None

        self.server_ip = None
        self.server_port = None
        self.capabilities = None
        self.options = None
        self.keep_alive = None
        self.direct_connection = None
        self.extensions = None
        self.strict_ssl = None

        self.terminal = None

    def connect(self,
                server_ip: str = '127.0.0.1',
                server_port: int = 4723,
                capabilities: dict = None,
                options: Union[AppiumOptions, List[AppiumOptions], None] = None,
                keep_alive: bool = True,
                direct_connection: bool = True,
                extensions: Optional[List['WebDriver']] = None,
                strict_ssl: bool = True
                ) -> None:
        """
        Connect to a device using Appium server. Provide driver attribute after connect.

        :param server_ip: The IP address of the Appium server. Defaults to '127.0.0.1'.
        :param server_port: The port of the Appium server. Defaults to 4723.
        :param capabilities: A dictionary specifying the desired capabilities for the session.
        :param options: An instance or a list of instances of AppiumOptions to configure the Appium session.
        :param keep_alive: Whether to keep the connection alive after a session ends. Defaults to True.
        Inherited from WebDriver.
        :param direct_connection:
        Whether to use direct connection without intermediate proxies. Defaults to True. Inherited from WebDriver.
        :param extensions: Optional list of WebDriver extensions. Inherited from WebDriver.
        :param strict_ssl: Whether to enforce strict SSL certificates handling. Defaults to True.
        Inherited from WebDriver.
        :return: None
        """
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        if capabilities is not None and options is None:
            options = UiAutomator2Options()
            if "platformName" in capabilities.keys():
                options.platform_name = capabilities["platformName"]
            if "appium:automationName" in capabilities.keys():
                options.automation_name = capabilities["appium:automationName"]
            if "appium:deviceName" in capabilities.keys():
                options.device_name = capabilities["appium:deviceName"]
            if "appium:UDID" in capabilities.keys():
                options.udid = capabilities["appium:UDID"]
            if "appium:app" in capabilities.keys():
                options.app = capabilities["appium:app"]
            if "appium:appPackage" in capabilities.keys():
                options.app_package = capabilities["appium:appPackage"]
            if "appium:appWaitActivity" in capabilities.keys():
                options.app_wait_activity = capabilities["appium:appWaitActivity"]
            if "appium:autoGrantPermissions" in capabilities.keys():
                options.auto_grant_permissions = capabilities["appium:autoGrantPermissions"]
            if "appium:newCommandTimeout" in capabilities.keys():
                options.new_command_timeout = capabilities["appium:newCommandTimeout"]
        url = f'http://{server_ip}:{str(server_port)}/wd/hub'
        logging.info(f"Подключение к серверу: {url}")
        self.driver = WebDriverSingleton(command_executor=url,
                                         options=options,
                                         keep_alive=keep_alive,
                                         direct_connection=direct_connection,
                                         extensions=extensions,
                                         strict_ssl=strict_ssl)
        self.server_ip = server_ip
        self.server_port = server_port
        self.capabilities = capabilities
        self.options = options
        self.keep_alive = keep_alive
        self.direct_connection = direct_connection
        self.extensions = extensions
        self.strict_ssl = strict_ssl

        self.terminal = Terminal(base=self)

    def disconnect(self) -> None:
        """
        Disconnect from device using Appium server.
        :return: None
        """
        if self.driver:
            logging.debug(f"Отключение от сессии №: {self.driver.session_id}")
            self.driver.quit()
            self.driver = None

    def reconnect(self):
        """
        Reconnect to device using Appium server.
        :return: None
        """
        logging.error("Reconnecting")
        self.connect(server_ip=self.server_ip,
                     server_port=self.server_port,
                     capabilities=self.capabilities,
                     options=self.options,
                     keep_alive=self.keep_alive,
                     direct_connection=self.direct_connection,
                     extensions=self.extensions,
                     strict_ssl=self.strict_ssl
                     )
