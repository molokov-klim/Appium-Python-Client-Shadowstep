import inspect
import logging
from typing import Union, List, Optional

from appium.options.android import UiAutomator2Options
from appium.options.common import AppiumOptions

from appium import webdriver
from appium.webdriver.webdriver import WebDriver

from shadowstep.terminal.adb import Adb
from shadowstep.terminal.terminal import Terminal
from shadowstep.terminal.transport import Transport


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
        """
        Get the WebDriver instance.

        Returns:
            WebDriver
                The current WebDriver instance.
        """
        return cls._driver


class SBase:
    """
    A base class for interacting with an Appium server and managing the WebDriver instance.
    """
    def __init__(self):
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

        self.adb: Adb = None
        self.transport: Transport = None
        self.terminal: Terminal = None

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
                ssh_password: str = None
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

        Returns:
            None
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
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password

        if ssh_user and ssh_password:
            self.transport = Transport(server=self.server_ip,
                                       port=self.server_port,
                                       user=self.ssh_user,
                                       password=self.ssh_password)
        self.terminal = Terminal(base=self)
        self.adb = Adb()

    def disconnect(self) -> None:
        """
        Disconnect from the device using the Appium server.

        Returns:
            None
        """
        if self.driver:
            logging.debug(f"Отключение от сессии №: {self.driver.session_id}")
            self.driver.quit()
            self.driver = None

    def reconnect(self):
        """
        Reconnect to the device using the Appium server.

        Returns:
            None
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
