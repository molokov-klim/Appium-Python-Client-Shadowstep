import logging

from appium import webdriver
from appium.options.android import UiAutomator2Options


class SBase:
    def __init__(self):
        self.driver = None

    def connect(self,
                capabilities: dict = None,
                options: UiAutomator2Options = None,
                server_ip: str = '127.0.0.1',
                server_port: int = 4723) -> None:
        """
        Подключение к устройству
        """
        if not options:
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
        self.driver = webdriver.Remote(command_executor=url,
                                       desired_capabilities=capabilities,
                                       options=options,
                                       keep_alive=True)

    def disconnect(self) -> None:
        """
        Отключение от устройства
        """
        if self.driver:
            logging.debug(f"Отключение от сессии №: {self.driver.session_id}")
            self.driver.quit()
            self.driver = None

