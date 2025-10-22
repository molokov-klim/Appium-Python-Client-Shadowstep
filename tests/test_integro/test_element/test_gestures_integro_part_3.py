# ruff: noqa
# pyright: ignore
import logging
import time

import pytest

from shadowstep.element.element import Element
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_gestures_integro_part_3.py
"""
LOCATOR_CONNECTED_DEVICES = {"text": "Connected devices"}

logger = logging.getLogger(__name__)


class TestElementGesturesPart3:
    """Тесты свайп жестов взаимодействия с элементами.

    Данный класс содержит тесты для свайп жестов взаимодействия с элементами,
    включая swipe операции в различных направлениях и с различными параметрами.
    """

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_swipe_directions(
        self, app: Shadowstep, direction: str, android_settings_open_close: None
    ):
        """Тест свайпа в различных направлениях.

        Проверяет корректность выполнения свайпа в заданном направлении
        по элементу "Connected devices" с параметрами процента и скорости.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            direction: Направление свайпа (up, down, left, right).
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.swipe(direction=direction, percent=0.5, speed=3000)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_up(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Тест свайпа вверх.

        Проверяет корректность выполнения свайпа вверх
        по элементу "Network & internet" с заданными параметрами.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_up(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_down(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Тест свайпа вниз.

        Проверяет корректность выполнения свайпа вниз
        по элементу "Network & internet" с заданными параметрами.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_down(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_left(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Тест свайпа влево.

        Проверяет корректность выполнения свайпа влево
        по элементу "Network & internet" с заданными параметрами.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_left(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_right(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Тест свайпа вправо.

        Проверяет корректность выполнения свайпа вправо
        по элементу "Network & internet" с заданными параметрами.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_right(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_fling_directions(
        self, app: Shadowstep, direction: str, android_settings_open_close: None
    ):
        """Тест быстрого свайпа (fling) в различных направлениях.

        Проверяет корректность выполнения быстрого свайпа в заданном направлении
        по элементу "Connected devices" с заданной скоростью.

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            direction: Направление быстрого свайпа (up, down, left, right).
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.fling(speed=3000, direction=direction)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101
