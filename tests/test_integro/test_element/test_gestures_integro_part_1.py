# ruff: noqa
# pyright: ignore
import logging
import time
from typing import Any

import pytest

from shadowstep.element.element import Element
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_gestures_integro_part_1.py
"""
LOCATOR_CONNECTED_DEVICES = {"text": "Connected devices"}
LOCATOR_CONNECTION_PREFERENCES = {"text": "Connection preferences"}
LOCATOR_SEARCH_SETTINGS = {
    "text": "Search settings",
    "resource-id": "com.android.settings:id/search_action_bar_title",
    "class": "android.widget.TextView",
}
SEARCH_SETTINGS_EXPECTED_TEXT = "Search settings"
LOCATOR_SEARCH_EDIT_TEXT = {
    "class": "android.widget.EditText",
}
LOCATOR_PHONE = {"text": "Phone"}
LOCATOR_BUBBLE = {
    "text": "App info",
}

logger = logging.getLogger(__name__)


class TestElementGesturesPart1:
    """Тесты базовых жестов взаимодействия с элементами.

    Данный класс содержит тесты для базовых жестов взаимодействия с элементами,
    включая tap и click операции с различными параметрами и обработкой исключений.
    """

    def test_tap(self, app: Shadowstep, android_settings_open_close: None):
        """Тест базового тапа по элементу.

        Проверяет корректность выполнения тапа по элементу "Connected devices"
        и ожидаемое появление элемента "Connection preferences".

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.tap()
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_tap_duration(self, app: Shadowstep, press_home: None, stability: None):
        """Тест тапа с заданной продолжительностью.

        Проверяет корректность выполнения тапа с длительностью 3000мс
        по элементу "Phone" и ожидаемое появление элемента "App info".

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            press_home: Фикстура для нажатия кнопки Home.
            stability: Фикстура для обеспечения стабильности теста.
        """
        phone = app.get_element(locator=LOCATOR_PHONE)
        phone.tap(duration=3000)
        bubble = app.get_element(locator=LOCATOR_BUBBLE)
        logger.info(app.driver.page_source)
        assert bubble.is_visible()

    def test_tap_no_such_driver_exception(self, app: Shadowstep, android_settings_open_close: None):
        """Тест обработки исключения при отсутствии драйвера.

        Проверяет корректность обработки исключения NoSuchDriverException
        при выполнении тапа после отключения от драйвера.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        app.disconnect()
        assert not app.is_connected()  # noqa: S101
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.tap()
        assert app.is_connected()  # noqa: S101

    def test_tap_invalid_session_id_exception(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест обработки исключения при неверном ID сессии.

        Проверяет корректность обработки исключения InvalidSessionIdException
        при выполнении тапа с неверным ID сессии.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        app.driver.session_id = "12345"
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.tap()
        assert app.is_connected()  # noqa: S101
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_tap_no_such_element_exception(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест обработки исключения при отсутствии элемента.

        Проверяет корректность обработки исключения NoSuchElementException
        при попытке выполнить тап по несуществующему элементу.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        try:
            element = app.get_element(locator={"content-desc": "no_such_element"})
            element.timeout = 3
            element.tap()
        except Exception as error:
            print(error)
            assert isinstance(error, ShadowstepElementException)  # noqa: S101, PT017

    @pytest.mark.parametrize(
        "params",
        [
            {"x": 100, "y": 500},  # Direct coordinates
            {"locator": LOCATOR_SEARCH_SETTINGS},  # Locator
            {"direction": 0, "distance": 1000},  # Up
        ],
    )
    def test_tap_and_move(self, app: Shadowstep, android_settings_open_close: None, params: Any):
        """Тест тапа с перемещением в различных направлениях.

        Проверяет корректность выполнения тапа с последующим перемещением
        с использованием различных параметров (координаты, локатор, направление).

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
            params: Параметры для выполнения тапа с перемещением.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        target_element = app.get_element(locator=LOCATOR_SEARCH_SETTINGS)
        element.tap_and_move(**params)
        time.sleep(5)
        assert target_element.text == SEARCH_SETTINGS_EXPECTED_TEXT  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101

    def test_click(self, app: Shadowstep, android_settings_open_close: None):
        """Тест базового клика по элементу.

        Проверяет корректность выполнения клика по элементу "Connected devices"
        и ожидаемое появление элемента "Connection preferences".

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.click()
        time.sleep(5)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_click_duration(self, app: Shadowstep, press_home: None):
        """Тест клика с заданной продолжительностью.

        Проверяет корректность выполнения клика с длительностью 3000мс
        по элементу "Phone" и ожидаемое появление элемента "App info".

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            press_home: Фикстура для нажатия кнопки Home.
        """
        phone = app.get_element(locator=LOCATOR_PHONE)
        phone.click(duration=3000)
        bubble = app.get_element(locator=LOCATOR_BUBBLE)
        assert bubble.is_visible()

    def test_click_double(self, app: Shadowstep, android_settings_open_close: None):
        """Тест двойного клика по элементу.

        Проверяет корректность выполнения двойного клика по элементу
        "Search settings" и ожидаемое появление поля ввода поиска.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        search = app.get_element(locator=LOCATOR_SEARCH_SETTINGS)
        search.click_double()
        time.sleep(5)
        logger.info(app.driver.page_source)
        assert app.get_element(locator=LOCATOR_SEARCH_EDIT_TEXT).is_visible()
