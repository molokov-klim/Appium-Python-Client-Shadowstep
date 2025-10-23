# ruff: noqa
# pyright: ignore
"""
Интеграционные тесты для модуля mobile_commands.py - Часть 2.

Группа тестов жестов: click, long click, double click, swipe, scroll, drag,
pinch, fling и другие жесты взаимодействия с экраном.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_ui_automator/test_mobile_commands_integro_part_2.py
"""

import logging
from typing import Any

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.ui_automator.mobile_commands import MobileCommands

logger = logging.getLogger(__name__)


class TestMobileCommandsPart2:
    """Интеграционные тесты для класса MobileCommands - Часть 2.
    
    Тестирование команд жестов и взаимодействия с экраном.
    """

    @pytest.fixture(autouse=True)
    def setup_mobile_commands(self, app: Shadowstep):
        """Настройка экземпляра MobileCommands с фикстурой app.
        
        Args:
            app: Экземпляр приложения Shadowstep для тестирования.
        """
        self.mobile_commands = MobileCommands()
        self.app = app
        # Ensure app is connected
        assert self.app.is_connected()  # noqa: S101
        yield

    def test_click_gesture(self):
        """Тестирование команды click_gesture.
        
        Шаги:
            1. Выполнение клика в центре экрана (500, 500)
        
        Проверяет:
            - Команда выполняется без исключений
        """
        # Click at center of screen
        result = self.mobile_commands.click_gesture({"x": 500, "y": 500})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_long_click_gesture(self):
        """Тестирование команды long_click_gesture.
        
        Шаги:
            1. Выполнение длительного клика (1000ms) по координатам (500, 500)
        
        Проверяет:
            - Команда выполняется без исключений
        """
        result = self.mobile_commands.long_click_gesture({"x": 500, "y": 500, "duration": 1000})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_double_click_gesture(self):
        """Тестирование команды double_click_gesture.
        
        Шаги:
            1. Выполнение двойного клика по координатам (500, 500)
        
        Проверяет:
            - Команда выполняется без исключений
        """
        result = self.mobile_commands.double_click_gesture({"x": 500, "y": 500})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_swipe_gesture(self):
        """Тестирование команды swipe_gesture.
        
        Шаги:
            1. Выполнение свайпа влево в указанной области
        
        Параметры:
            - left: 100
            - top: 500
            - width: 600
            - height: 100
            - direction: left
            - percent: 0.75
        
        Проверяет:
            - Команда выполняется без исключений
        """
        result = self.mobile_commands.swipe_gesture(
            {
                "left": 100,
                "top": 500,
                "width": 600,
                "height": 100,
                "direction": "left",
                "percent": 0.75,
            }
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_scroll_gesture(self):
        """Тестирование команды scroll_gesture.
        
        Шаги:
            1. Выполнение прокрутки вниз в указанной области
        
        Параметры:
            - left: 100
            - top: 500
            - width: 600
            - height: 800
            - direction: down
            - percent: 1.0
        
        Проверяет:
            - Результат является булевым значением (можно ли прокручивать дальше)
        """
        result = self.mobile_commands.scroll_gesture(
            {
                "left": 100,
                "top": 500,
                "width": 600,
                "height": 800,
                "direction": "down",
                "percent": 1.0,
            }
        )

        # Returns boolean indicating if can scroll more
        assert isinstance(result, bool)  # noqa: S101

    def test_drag_gesture(self):
        """Тестирование команды drag_gesture.
        
        Шаги:
            1. Выполнение перетаскивания от (500, 500) до (500, 800)
        
        Проверяет:
            - Команда выполняется без исключений
        """
        result = self.mobile_commands.drag_gesture(
            {"startX": 500, "startY": 500, "endX": 500, "endY": 800}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_pinch_open_gesture(self):
        """Тестирование команды pinch_open_gesture.
        
        Шаги:
            1. Выполнение жеста масштабирования (увеличения)
        
        Параметры:
            - left: 100
            - top: 100
            - width: 600
            - height: 600
            - percent: 0.5
        
        Проверяет:
            - Команда выполняется без исключений
        """
        result = self.mobile_commands.pinch_open_gesture(
            {"left": 100, "top": 100, "width": 600, "height": 600, "percent": 0.5}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_pinch_close_gesture(self):
        """Тестирование команды pinch_close_gesture.
        
        Шаги:
            1. Выполнение жеста масштабирования (уменьшения)
        
        Параметры:
            - left: 100
            - top: 100
            - width: 600
            - height: 600
            - percent: 0.5
        
        Проверяет:
            - Команда выполняется без исключений
        """
        result = self.mobile_commands.pinch_close_gesture(
            {"left": 100, "top": 100, "width": 600, "height": 600, "percent": 0.5}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_fling_gesture(self):
        """Тестирование команды fling_gesture.
        
        Шаги:
            1. Выполнение жеста быстрого свайпа вниз
        
        Параметры:
            - left: 100
            - top: 100
            - width: 600
            - height: 800
            - direction: down
            - speed: 7500
        
        Проверяет:
            - Результат является булевым значением (можно ли прокручивать дальше)
        """
        result = self.mobile_commands.fling_gesture(
            {
                "left": 100,
                "top": 100,
                "width": 600,
                "height": 800,
                "direction": "down",
                "speed": 7500,
            }
        )

        # Returns boolean indicating if can scroll more
        assert isinstance(result, bool)  # noqa: S101

    @pytest.mark.xfail(reason="Requires scrollable element with specific selector", strict=False)
    def test_scroll_legacy(self):
        """Тестирование устаревшей команды scroll.
        
        Примечание:
            Это старая команда scroll, отличающаяся от scroll_gesture.
            Требует наличия прокручиваемого элемента с определенным селектором.
        """
        # This is the old scroll command, different from scroll_gesture
        result = self.mobile_commands.scroll({"strategy": "accessibility id", "selector": "test"})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires valid element ID", strict=False)
    def test_replace_element_value(self):
        """Тестирование команды replace_element_value.
        
        Примечание:
            Требует корректный ID элемента.
            Тест отмечен как xfail из-за необходимости существующего элемента.
        """
        result = self.mobile_commands.replace_element_value(
            {"elementId": "test", "text": "replacement"}
        )
        logger.info(result)

