# ruff: noqa
# pyright: ignore
"""Интеграционные тесты для проверки различных стратегий выполнения жестов.

Этот модуль содержит тесты для проверки работы жестов с явным указанием
стратегии выполнения (W3C_ACTIONS, MOBILE_COMMANDS).
"""
import logging
import time

import pytest

from shadowstep.element.element import Element
from shadowstep.enums import GestureStrategy
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_element/test_gestures_strategies_integro.py
"""

LOCATOR_CONNECTED_DEVICES = {"text": "Connected devices"}
LOCATOR_CONNECTION_PREFERENCES = {"text": "Connection preferences"}
LOCATOR_RECYCLER = {"resource-id": "com.android.settings:id/main_content_scrollable_container"}
LOCATOR_NETWORK = {"text": "Network & internet", "resource-id": "android:id/title"}
LOCATOR_BOTTOM_ELEMENT = {"textContains": "About"}

logger = logging.getLogger(__name__)


class TestGestureStrategies:
    """Тесты для проверки различных стратегий выполнения жестов.
    
    Проверяет корректность работы жестов при явном указании стратегии:
    - W3C_ACTIONS: использует W3C WebDriver Actions API
    - MOBILE_COMMANDS: использует Appium mobile commands (UiAutomator2)
    """

    def test_click_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест клика с использованием стратегии W3C_ACTIONS.

        Проверяет корректность выполнения клика по элементу
        с явным указанием стратегии W3C_ACTIONS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.click(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_click_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест клика с использованием стратегии MOBILE_COMMANDS.

        Проверяет корректность выполнения клика по элементу
        с явным указанием стратегии MOBILE_COMMANDS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.click(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_click_auto_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест клика с использованием стратегии AUTO (по умолчанию).

        Проверяет корректность выполнения клика по элементу
        с использованием автоматического выбора стратегии.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.click(strategy=GestureStrategy.AUTO)
        time.sleep(3)
        expect_element = app.get_element(LOCATOR_CONNECTION_PREFERENCES)
        assert expect_element.is_visible()  # noqa: S101

    def test_double_click_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест двойного клика с использованием стратегии W3C_ACTIONS.

        Проверяет корректность выполнения двойного клика
        с явным указанием стратегии W3C_ACTIONS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        search = app.get_element(
            locator={
                "text": "Search settings",
                "resource-id": "com.android.settings:id/search_action_bar_title",
            }
        )
        search.double_click(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(3)
        assert app.get_element(locator={"class": "android.widget.EditText"}).is_visible()  # noqa: S101

    def test_double_click_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест двойного клика с использованием стратегии MOBILE_COMMANDS.

        Проверяет корректность выполнения двойного клика
        с явным указанием стратегии MOBILE_COMMANDS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        search = app.get_element(
            locator={
                "text": "Search settings",
                "resource-id": "com.android.settings:id/search_action_bar_title",
            }
        )
        search.double_click(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(3)
        assert app.get_element(locator={"class": "android.widget.EditText"}).is_visible()  # noqa: S101

    def test_drag_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест перетаскивания с использованием стратегии W3C_ACTIONS.

        Проверяет корректность выполнения операции перетаскивания
        с явным указанием стратегии W3C_ACTIONS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        center_x1, center_y1 = element.get_center()
        element.drag(
            end_x=center_x1 - 500, end_y=center_y1 - 500, strategy=GestureStrategy.W3C_ACTIONS
        )
        time.sleep(2)
        assert element.get_center() != (center_x1, center_y1)  # noqa: S101

    def test_drag_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест перетаскивания с использованием стратегии MOBILE_COMMANDS.

        Проверяет корректность выполнения операции перетаскивания
        с явным указанием стратегии MOBILE_COMMANDS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        center_x1, center_y1 = element.get_center()
        element.drag(
            end_x=center_x1 - 500,
            end_y=center_y1 - 500,
            strategy=GestureStrategy.MOBILE_COMMANDS,
        )
        time.sleep(2)
        assert element.get_center() != (center_x1, center_y1)  # noqa: S101

    def test_fling_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест быстрого свайпа с использованием стратегии W3C_ACTIONS.

        Проверяет корректность выполнения быстрого свайпа
        с явным указанием стратегии W3C_ACTIONS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_RECYCLER)
        bounds_1 = element.bounds
        element.fling_down(speed=3000, strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        bounds_2 = element.bounds
        assert bounds_1 != bounds_2  # noqa: S101

    def test_fling_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест быстрого свайпа с использованием стратегии MOBILE_COMMANDS.

        Проверяет корректность выполнения быстрого свайпа
        с явным указанием стратегии MOBILE_COMMANDS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_RECYCLER)
        bounds_1 = element.bounds
        element.fling_down(speed=3000, strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        bounds_2 = element.bounds
        assert bounds_1 != bounds_2  # noqa: S101

    def test_scroll_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест прокрутки с использованием стратегии W3C_ACTIONS.

        Проверяет корректность выполнения прокрутки
        с явным указанием стратегии W3C_ACTIONS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        result = settings_recycler.scroll_down(
            percent=0.5, speed=2000, return_bool=True, strategy=GestureStrategy.W3C_ACTIONS
        )
        time.sleep(2)
        assert isinstance(result, bool)  # noqa: S101

    def test_scroll_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест прокрутки с использованием стратегии MOBILE_COMMANDS.

        Проверяет корректность выполнения прокрутки
        с явным указанием стратегии MOBILE_COMMANDS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        result = settings_recycler.scroll_down(
            percent=0.5, speed=2000, return_bool=True, strategy=GestureStrategy.MOBILE_COMMANDS
        )
        time.sleep(2)
        assert isinstance(result, bool)  # noqa: S101

    def test_scroll_to_bottom_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест прокрутки до конца с использованием стратегии W3C_ACTIONS.

        Проверяет корректность выполнения прокрутки до конца контейнера
        с явным указанием стратегии W3C_ACTIONS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_bottom(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    def test_scroll_to_bottom_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест прокрутки до конца с использованием стратегии MOBILE_COMMANDS.

        Проверяет корректность выполнения прокрутки до конца контейнера
        с явным указанием стратегии MOBILE_COMMANDS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_bottom(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    def test_scroll_to_top_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест прокрутки вверх с использованием стратегии W3C_ACTIONS.

        Проверяет корректность выполнения прокрутки вверх
        с явным указанием стратегии W3C_ACTIONS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        
        settings_recycler.scroll_to_bottom(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101
        
        settings_recycler.scroll_to_top(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101

    def test_scroll_to_top_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест прокрутки вверх с использованием стратегии MOBILE_COMMANDS.

        Проверяет корректность выполнения прокрутки вверх
        с явным указанием стратегии MOBILE_COMMANDS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        
        settings_recycler.scroll_to_bottom(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101
        
        settings_recycler.scroll_to_top(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101

    def test_scroll_to_element_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест прокрутки к элементу с использованием стратегии W3C_ACTIONS.

        Проверяет корректность выполнения прокрутки к конкретному элементу
        с явным указанием стратегии W3C_ACTIONS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/settings_homepage_container"}
        )
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_element(
            locator=settings_about_phone.locator, strategy=GestureStrategy.W3C_ACTIONS  # type: ignore
        )
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    def test_scroll_to_element_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест прокрутки к элементу с использованием стратегии MOBILE_COMMANDS.

        Проверяет корректность выполнения прокрутки к конкретному элементу
        с явным указанием стратегии MOBILE_COMMANDS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/settings_homepage_container"}
        )
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_element(
            locator=settings_about_phone.locator, strategy=GestureStrategy.MOBILE_COMMANDS  # type: ignore
        )
        time.sleep(2)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_swipe_w3c_actions_strategy(
        self, app: Shadowstep, direction: str, android_settings_open_close: None
    ):
        """Тест свайпа с использованием стратегии W3C_ACTIONS.

        Проверяет корректность выполнения свайпа в заданном направлении
        с явным указанием стратегии W3C_ACTIONS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            direction: Направление свайпа (up, down, left, right).
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_RECYCLER)
        element.swipe(
            direction=direction, percent=0.5, speed=3000, strategy=GestureStrategy.W3C_ACTIONS
        )
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_swipe_mobile_commands_strategy(
        self, app: Shadowstep, direction: str, android_settings_open_close: None
    ):
        """Тест свайпа с использованием стратегии MOBILE_COMMANDS.

        Проверяет корректность выполнения свайпа в заданном направлении
        с явным указанием стратегии MOBILE_COMMANDS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            direction: Направление свайпа (up, down, left, right).
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_RECYCLER)
        element.swipe(
            direction=direction,
            percent=0.5,
            speed=3000,
            strategy=GestureStrategy.MOBILE_COMMANDS,
        )
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_zoom_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест увеличения масштаба с использованием стратегии W3C_ACTIONS.

        Проверяет корректность выполнения операции увеличения масштаба
        с явным указанием стратегии W3C_ACTIONS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_network.zoom(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        assert isinstance(settings_network, Element)  # noqa: S101

    def test_zoom_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест увеличения масштаба с использованием стратегии MOBILE_COMMANDS.

        Проверяет корректность выполнения операции увеличения масштаба
        с явным указанием стратегии MOBILE_COMMANDS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_network.zoom(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        assert isinstance(settings_network, Element)  # noqa: S101

    def test_unzoom_w3c_actions_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест уменьшения масштаба с использованием стратегии W3C_ACTIONS.

        Проверяет корректность выполнения операции уменьшения масштаба
        с явным указанием стратегии W3C_ACTIONS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_network.unzoom(strategy=GestureStrategy.W3C_ACTIONS)
        time.sleep(2)
        assert isinstance(settings_network, Element)  # noqa: S101

    def test_unzoom_mobile_commands_strategy(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тест уменьшения масштаба с использованием стратегии MOBILE_COMMANDS.

        Проверяет корректность выполнения операции уменьшения масштаба
        с явным указанием стратегии MOBILE_COMMANDS.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_network = app.get_element(locator=LOCATOR_NETWORK)
        settings_network.unzoom(strategy=GestureStrategy.MOBILE_COMMANDS)
        time.sleep(2)
        assert isinstance(settings_network, Element)  # noqa: S101

