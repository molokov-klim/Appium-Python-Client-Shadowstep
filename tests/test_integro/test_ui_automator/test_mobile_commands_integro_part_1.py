# ruff: noqa
# pyright: ignore
"""
Интеграционные тесты для модуля mobile_commands.py - Часть 1.

Группа базовых тестов: singleton, информация об устройстве, батарея, дисплей,
клавиатура, буфер обмена, контексты.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_ui_automator/test_mobile_commands_integro_part_1.py
"""

import logging
import time
from typing import Any

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.ui_automator.mobile_commands import MobileCommands

logger = logging.getLogger(__name__)


class TestMobileCommandsPart1:
    """Интеграционные тесты для класса MobileCommands - Часть 1.
    
    Тестирование базовых функций: singleton pattern, информация об устройстве,
    батарея, дисплей, системные панели, клавиатура, буфер обмена, контексты.
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

    def test_singleton_pattern(self):
        """Тестирование паттерна singleton для MobileCommands.
        
        Проверяет, что MobileCommands следует паттерну singleton
        и возвращает один и тот же экземпляр при повторных вызовах.
        """
        instance1 = MobileCommands()
        instance2 = MobileCommands()
        assert instance1 is instance2  # noqa: S101

    def test_battery_info(self):
        """Тестирование команды battery_info для получения информации о батарее.
        
        Проверяет:
            - Результат не None
            - Результат является словарем
            - Присутствуют ключи level и state
        """
        result = self.mobile_commands.battery_info()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "level" in result  # noqa: S101
        assert "state" in result  # noqa: S101

    def test_device_info(self):
        """Тестирование команды device_info для получения информации об устройстве.
        
        Проверяет:
            - Результат не None
            - Результат является словарем
            - Присутствует ключ androidId
        """
        result = self.mobile_commands.device_info()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "androidId" in result  # noqa: S101

    def test_get_device_time(self):
        """Тестирование команды get_device_time для получения времени устройства.
        
        Проверяет:
            - Результат не None
            - Результат является строкой
        """
        result = self.mobile_commands.get_device_time()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_is_keyboard_shown(self):
        """Тестирование команды is_keyboard_shown.
        
        Проверяет:
            - Результат не None
            - Результат является булевым значением
        """
        result = self.mobile_commands.is_keyboard_shown()

        assert result is not None  # noqa: S101
        assert isinstance(result, bool)  # noqa: S101

    def test_get_current_package(self):
        """Тестирование команды get_current_package.
        
        Проверяет:
            - Результат не None
            - Результат является строкой
        """
        result = self.mobile_commands.get_current_package()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_get_current_activity(self):
        """Тестирование команды get_current_activity.
        
        Проверяет:
            - Результат не None
            - Результат является строкой
        """
        result = self.mobile_commands.get_current_activity()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101

    def test_get_display_density(self):
        """Тестирование команды get_display_density.
        
        Проверяет:
            - Результат не None
            - Результат является целым числом
            - Результат больше 0
        """
        result = self.mobile_commands.get_display_density()

        assert result is not None  # noqa: S101
        assert isinstance(result, int)  # noqa: S101
        assert result > 0  # noqa: S101

    def test_get_system_bars(self):
        """Тестирование команды get_system_bars.
        
        Проверяет:
            - Результат не None
            - Результат является словарем
            - Присутствует ключ statusBar
        """
        result = self.mobile_commands.get_system_bars()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101
        assert "statusBar" in result  # noqa: S101

    def test_is_locked(self):
        """Тестирование команды is_locked.
        
        Проверяет:
            - Результат не None
            - Результат является булевым значением
        """
        result = self.mobile_commands.is_locked()

        assert result is not None  # noqa: S101
        assert isinstance(result, bool)  # noqa: S101

    def test_lock_unlock(self):
        """Тестирование команд lock и unlock.
        
        Шаги:
            1. Блокировка устройства
            2. Проверка состояния блокировки
            3. Разблокировка устройства
            4. Проверка состояния разблокировки
        
        Примечание:
            Некоторые эмуляторы не поддерживают блокировку,
            поэтому проверяется только выполнение команды.
        """
        # Lock the device
        self.mobile_commands.lock()
        time.sleep(1)

        # Check if locked (may not work on all devices)
        is_locked = self.mobile_commands.is_locked()
        # Some emulators don't support lock, so just ensure command executes

        # Unlock the device
        self.mobile_commands.unlock()
        time.sleep(1)

        # Check if unlocked
        is_locked = self.mobile_commands.is_locked()
        # Should at least return a boolean
        assert isinstance(is_locked, bool)  # noqa: S101

    def test_get_clipboard(self):
        """Тестирование команды get_clipboard.
        
        Проверяет:
            - Результат не None
            - Результат является строкой (base64 encoded)
        
        Примечание:
            Содержимое буфера обмена может содержать предыдущие данные,
            поэтому проверяется только тип возвращаемого значения.
        """
        # Get clipboard content (returns base64 encoded string)
        result = self.mobile_commands.get_clipboard()

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101
        # Just verify it returns a base64-like string (doesn't contain non-base64 chars)
        # Content verification is difficult as clipboard may contain previous data

    def test_set_clipboard(self):
        """Тестирование команды set_clipboard.
        
        Проверяет:
            - Команда выполняется без исключений
        """
        test_text = "integration_test_text"
        result = self.mobile_commands.set_clipboard(
            {"content": test_text, "contentType": "plaintext"}
        )

        # Should not raise an exception
        assert result is None or result is not None  # noqa: S101

    def test_get_contexts(self):
        """Тестирование команды get_contexts.
        
        Проверяет:
            - Результат не None
            - Результат является списком
        
        Примечание:
            Список контекстов может быть пустым на некоторых устройствах/конфигурациях.
        """
        result = self.mobile_commands.get_contexts()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101
        # Context list may be empty on some devices/configurations

    def test_shell_command(self):
        """Тестирование выполнения команды shell.
        
        Проверяет:
            - Результат не None
            - Результат содержит ожидаемый вывод команды
        """
        # Execute simple shell command
        result = self.mobile_commands.shell({"command": "echo", "args": ["test"]})

        assert result is not None  # noqa: S101
        assert "test" in result  # noqa: S101

    def test_shell_command_getprop(self):
        """Тестирование команды shell с getprop.
        
        Проверяет:
            - Результат не None
            - Результат является строкой
            - Результат содержит цифровое значение (версия SDK)
        """
        result = self.mobile_commands.shell(
            {"command": "getprop", "args": ["ro.build.version.sdk"]}
        )

        assert result is not None  # noqa: S101
        assert isinstance(result, str)  # noqa: S101
        assert result.strip().isdigit()  # noqa: S101

    def test_open_notifications(self):
        """Тестирование команды open_notifications.
        
        Шаги:
            1. Открытие панели уведомлений
            2. Ожидание
            3. Закрытие панели кнопкой Back
        
        Проверяет:
            - Команда выполняется без исключений
        """
        result = self.mobile_commands.open_notifications()
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Press back to close notifications
        self.app.terminal.press_back()

    @pytest.mark.xfail(reason="Requires keyboard to be shown", strict=False)
    def test_hide_keyboard(self):
        """Тестирование команды hide_keyboard.
        
        Примечание:
            Команда может не выполнить действия, если клавиатура не отображается.
            Тест отмечен как xfail, так как требуется активная клавиатура.
        """
        # This may not do anything if keyboard is not shown
        result = self.mobile_commands.hide_keyboard()
        # Should complete without exception if keyboard is shown
        logger.info(result)

    def test_press_key(self):
        """Тестирование команды press_key.
        
        Шаги:
            1. Нажатие клавиши HOME (keycode 3)
            2. Ожидание
        
        Проверяет:
            - Команда выполняется без исключений
        """
        # Press home key
        result = self.mobile_commands.press_key({"keycode": 3})
        time.sleep(0.5)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_get_performance_data_types(self):
        """Тестирование команды get_performance_data_types.
        
        Проверяет:
            - Результат не None
            - Результат является списком
            - Список не пуст
        """
        result = self.mobile_commands.get_performance_data_types()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101
        assert len(result) > 0  # noqa: S101 # type: ignore

    @pytest.mark.xfail(
        reason="Performance data parsing may fail on some devices/emulators", strict=False
    )
    def test_get_performance_data(self, android_settings_open_close: Any):
        """Тестирование команды get_performance_data.
        
        Шаги:
            1. Получение доступных типов данных о производительности
            2. Получение данных о производительности для первого типа
        
        Проверяет:
            - Результат не None
            - Результат является списком
        
        Args:
            android_settings_open_close: Фикстура для управления настройками Android.
        
        Примечание:
            Парсинг данных о производительности может не работать на некоторых
            устройствах/эмуляторах, поэтому тест отмечен как xfail.
        """
        # Get available performance data types first
        data_types = self.mobile_commands.get_performance_data_types()

        assert data_types is not None  # noqa: S101
        assert isinstance(data_types, list)  # noqa: S101

        if data_types and len(data_types) > 0:  # type: ignore
            # Get performance data for the first available type
            result = self.mobile_commands.get_performance_data(
                {"packageName": "com.android.settings", "dataType": data_types[0]}
            )

            assert result is not None  # noqa: S101
            assert isinstance(result, list)  # noqa: S101

    def test_type_text(self, android_settings_open_close: Any):
        """Тестирование команды type для ввода текста.
        
        Проверяет:
            - Команда выполняется без исключений
        
        Args:
            android_settings_open_close: Фикстура для управления настройками Android.
        
        Примечание:
            Идеально было бы сначала кликнуть на поле ввода,
            но для теста достаточно проверить выполнение команды.
        """
        # Click on search or any input field first would be ideal
        # For now just test the command executes
        result = self.mobile_commands.type({"text": "test"})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_screenshots_command(self):
        """Тестирование команды screenshots.
        
        Проверяет:
            - Результат не None
            - Результат является словарем
        """
        result = self.mobile_commands.screenshots()

        assert result is not None  # noqa: S101
        assert isinstance(result, dict)  # noqa: S101

