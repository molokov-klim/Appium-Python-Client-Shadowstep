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


class TestBase:

    def test_webdriver_singleton_creation(self, app: Shadowstep):
        """Тест создания и повторного использования WebDriverSingleton"""
        app2 = Shadowstep()
        app2.connect(server_ip=APPIUM_IP,
                     server_port=APPIUM_PORT,
                     capabilities=CAPABILITIES)
        assert app2.driver == app.driver

    def test_reconnect_after_session_disruption(self, app: Shadowstep):
        """Тест автоматического переподключения при разорванной сессии"""
        app.reconnect()  # Переподключение
        try:
            app.driver.get_screenshot_as_png()  # Попытка выполнить команду
            assert app.driver.session_id is not None, "Не удалось переподключиться"
        except NoSuchDriverException as error:
            raise AssertionError("Ошибка: не удалось инициализировать WebDriver после переподключения") from error
        except InvalidSessionIdException as error:
            raise AssertionError("Ошибка: не удалось инициализировать WebDriver после переподключения") from error

    def test_disconnect_on_invalid_session_exception(self, app: Shadowstep):
        """Тест обработки InvalidSessionIdException при разрыве сессии в disconnect"""
        app.disconnect()
        CAPABILITIES["appium:newCommandTimeout"] = 10
        app.connect(server_ip=APPIUM_IP,
                    server_port=APPIUM_PORT,
                    capabilities=CAPABILITIES)
        time.sleep(12)
        try:
            app.driver.get_screenshot_as_png()
        except InvalidSessionIdException as error:
            assert isinstance(error, InvalidSessionIdException)
            CAPABILITIES["appium:newCommandTimeout"] = 900
            app.connect(server_ip=APPIUM_IP,
                        server_port=APPIUM_PORT,
                        capabilities=CAPABILITIES)
            return True
        except Exception as error:
            logger.error(error)
            raise AssertionError(f"Неизвестная ошибка: {type(error)}") from error
        raise AssertionError("Ошибка логики теста, ожидался разрыв сессии")

    def test_reconnect_without_active_session(self, app: Shadowstep):
        """Тест вызова reconnect при отсутствии активной сессии"""
        app.disconnect()
        app.reconnect()
        assert app.driver is not None, "Сессия не была создана при переподключении"
        assert app.driver.session_id is not None, "Сессия не была создана при переподключении"

    def test_session_state_before_command_execution(self, app: Shadowstep):
        """Тест состояния сессии перед выполнением WebDriver команд"""
        if app.driver.session_id is None:
            app.reconnect()  # Переподключение при отсутствии активной сессии
        try:
            app.driver.get_screenshot_as_png()
        except WebDriverException as error:
            raise AssertionError(f"Ошибка выполнения команды: {error}") from error

    def test_handling_of_capabilities_option(self, app: Shadowstep):
        """Тест корректной обработки параметров capabilities"""
        app.disconnect()  # Завершаем текущую сессию для проверки новых настроек
        new_caps = CAPABILITIES.copy()
        new_caps["appium:autoGrantPermissions"] = False  # Изменяем capabilities
        app.connect(server_ip="127.0.0.1", server_port=4723, capabilities=new_caps)
        assert app.driver is not None, "Сессия не была создана с новыми параметрами capabilities"
        assert app.options.auto_grant_permissions is False, "Параметр autoGrantPermissions не применился"
        app.connect(server_ip="127.0.0.1", server_port=4723, capabilities=CAPABILITIES)

    def test_is_connected_when_connected(self, app: Shadowstep):
        app.reconnect()
        assert app.is_connected()

    def test_is_connected_when_disconnected(self, app: Shadowstep):
        app.disconnect()
        assert not app.is_connected()
        app.connect(CAPABILITIES)
