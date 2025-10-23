# ruff: noqa
# pyright: ignore
import logging
import time

import pytest

from shadowstep.element.element import Element
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_gestures_integro_part_2.py
"""
LOCATOR_CONNECTED_DEVICES = {"text": "Connected devices"}
LOCATOR_RECYCLER = {"resource-id": "com.android.settings:id/main_content_scrollable_container"}
LOCATOR_BOTTOM_ELEMENT = {"textContains": "About"}

logger = logging.getLogger(__name__)


class TestElementGesturesPart2:
    """Тесты продвинутых жестов взаимодействия с элементами.

    Данный класс содержит тесты для продвинутых жестов взаимодействия с элементами,
    включая drag, fling и scroll операции с различными параметрами.
    """

    def test_drag(self, app: Shadowstep, android_settings_open_close: None):
        """Тест перетаскивания элемента.

        Проверяет корректность выполнения операции перетаскивания элемента
        "Connected devices" на новые координаты.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        gallery = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        center_x1, center_y1 = gallery.get_center()
        gallery.drag(end_x=center_x1 - 500, end_y=center_y1 - 500)
        assert gallery.get_center() != center_x1, center_y1

    def test_fling(self, app: Shadowstep, android_settings_open_close: None):
        """Тест быстрого свайпа (fling) вниз.

        Проверяет корректность выполнения быстрого свайпа вниз
        по элементу "Connected devices" с изменением границ элемента.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        bounds_1 = element.bounds
        element.fling_down(speed=3000)
        bounds_2 = element.bounds
        assert bounds_1 != bounds_2

    def test_scroll(self, app: Shadowstep, android_settings_open_close: None):
        """Тест прокрутки контейнера вниз.

        Проверяет корректность выполнения прокрутки контейнера настроек
        вниз до появления элемента "About".

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        logger.info(app.driver.page_source)
        logger.info("+++++++++++++++++++")
        logger.info("+++++++++++++++++++")
        logger.info("+++++++++++++++++++")
        logger.info("+++++++++++++++++++")

        while settings_recycler.scroll_down(percent=10, speed=2000, return_bool=True):
            time.sleep(1)
        logger.info(app.driver.page_source)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    def test_scroll_to_element_not_found(self, app: Shadowstep, android_settings_open_close: None):
        """Тест прокрутки к несуществующему элементу.

        Проверяет корректность обработки исключения при попытке
        прокрутки к несуществующему элементу.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        container = app.get_element({"text": "not existing element"})
        with pytest.raises(ShadowstepElementException):
            container.scroll_to_element(locator={"text": "Element That Does Not Exist"})

    def test_scroll_to_bottom(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Тест прокрутки до нижней части контейнера.

        Проверяет корректность выполнения прокрутки до нижней части
        контейнера настроек и появления элемента "About".

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_bottom()
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    def test_scroll_to_top(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Тест прокрутки до верхней части контейнера.

        Проверяет корректность выполнения прокрутки до верхней части
        контейнера настроек после прокрутки вниз.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_bottom()
        time.sleep(3)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101
        settings_recycler.scroll_to_top()
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101

    def test_scroll_to_element(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Тест прокрутки к конкретному элементу.

        Проверяет корректность выполнения прокрутки к конкретному элементу
        в контейнере настроек.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/settings_homepage_container"}
        )
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_element(locator=settings_about_phone.locator)  # type: ignore
        time.sleep(3)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101
        settings_recycler.scroll_to_element(locator=settings_network)
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101
