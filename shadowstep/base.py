import inspect
import logging
from typing import Union, List, Optional

from appium.options.android import UiAutomator2Options
from appium.options.common import AppiumOptions

from appium import webdriver
from appium.webdriver.webdriver import WebDriver


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
        Подключение к устройству
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

    def disconnect(self) -> None:
        """
        Отключение от устройства
        """
        if self.driver:
            logging.debug(f"Отключение от сессии №: {self.driver.session_id}")
            self.driver.quit()
            self.driver = None
