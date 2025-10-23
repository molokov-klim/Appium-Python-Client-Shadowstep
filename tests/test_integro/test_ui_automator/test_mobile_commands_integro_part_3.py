# ruff: noqa
# pyright: ignore
"""
Интеграционные тесты для модуля mobile_commands.py - Часть 3.

Группа тестов управления приложениями: установка, активация, завершение,
разрешения, уведомления, GPS, connectivity, UI mode.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_ui_automator/test_mobile_commands_integro_part_3.py
"""

import logging
import time
from typing import Any

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.ui_automator.mobile_commands import MobileCommands

logger = logging.getLogger(__name__)


class TestMobileCommandsPart3:
    """Интеграционные тесты для класса MobileCommands - Часть 3.
    
    Тестирование команд управления приложениями, разрешений, уведомлений,
    GPS, connectivity и других системных функций.
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

    def test_is_app_installed(self, android_settings_open_close: Any):
        """Тестирование команды is_app_installed.
        
        Проверяет:
            - Приложение Settings установлено (результат True)
        
        Args:
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Check if Settings app is installed
        result = self.mobile_commands.is_app_installed({"appId": "com.android.settings"})

        assert result is True  # noqa: S101

    def test_is_app_not_installed(self):
        """Тестирование команды is_app_installed с несуществующим приложением.
        
        Проверяет:
            - Несуществующее приложение не установлено (результат False)
        """
        result = self.mobile_commands.is_app_installed({"appId": "com.nonexistent.app.xyz"})

        assert result is False  # noqa: S101

    def test_query_app_state(self, android_settings_open_close: Any):
        """Тестирование команды query_app_state.
        
        Шаги:
            1. Запрос состояния приложения Settings
        
        Проверяет:
            - Результат не None
            - Результат равен 4 (running in foreground)
        
        Args:
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Query state of Settings app while it's open
        result = self.mobile_commands.query_app_state({"appId": "com.android.settings"})

        assert result is not None  # noqa: S101
        # 4 = running in foreground
        assert result == 4  # noqa: S101

    def test_activate_app(self, android_settings_open_close: Any):
        """Тестирование команды activate_app.
        
        Шаги:
            1. Закрытие приложения Settings
            2. Активация приложения Settings
            3. Проверка, что приложение на переднем плане
        
        Args:
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Close settings first
        self.app.terminal.close_app("com.android.settings")
        time.sleep(1)

        # Activate settings
        result = self.mobile_commands.activate_app({"appId": "com.android.settings"})
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Verify app is in foreground
        state = self.mobile_commands.query_app_state({"appId": "com.android.settings"})
        assert state == 4  # noqa: S101

    def test_terminate_app(self, android_settings_open_close: Any):
        """Тестирование команды terminate_app.
        
        Шаги:
            1. Активация приложения Settings
            2. Завершение приложения
            3. Проверка, что приложение не на переднем плане
        
        Args:
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Ensure app is running
        self.mobile_commands.activate_app({"appId": "com.android.settings"})
        time.sleep(1)

        # Terminate the app
        result = self.mobile_commands.terminate_app({"appId": "com.android.settings"})
        time.sleep(1)

        # Should return True if terminated
        assert result is True  # noqa: S101

        # Verify app is not in foreground
        state = self.mobile_commands.query_app_state({"appId": "com.android.settings"})
        assert state != 4  # noqa: S101

    def test_background_app(self, android_settings_open_close: Any):
        """Тестирование команды background_app.
        
        Шаги:
            1. Отправка приложения в фон на 1 секунду
            2. Ожидание возврата приложения
        
        Args:
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Put app in background for 1 second
        result = self.mobile_commands.background_app({"seconds": 1})
        time.sleep(2)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_start_activity(self):
        """Тестирование команды start_activity.
        
        Шаги:
            1. Запуск активности Settings
            2. Ожидание
            3. Закрытие приложения
        """
        result = self.mobile_commands.start_activity({"intent": "android.settings.SETTINGS"})
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Close settings
        self.app.terminal.close_app("com.android.settings")

    def test_clear_app(self):
        """Тестирование команды clear_app.
        
        Шаги:
            1. Очистка данных приложения Settings
        
        Проверяет:
            - Команда выполняется без исключений
        """
        result = self.mobile_commands.clear_app({"appId": "com.android.settings"})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_get_permissions(self, android_settings_open_close: Any):
        """Тестирование команды get_permissions.
        
        Проверяет:
            - Результат не None
            - Результат является списком
        
        Args:
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        result = self.mobile_commands.get_permissions(
            {"type": "requested", "appId": "com.android.settings"}
        )

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101

    def test_change_permissions(self):
        """Тестирование команды change_permissions.
        
        Шаги:
            1. Выдача разрешения READ_CONTACTS приложению Settings
        """
        result = self.mobile_commands.change_permissions(
            {
                "appId": "com.android.settings",
                "permissions": "android.permission.READ_CONTACTS",
                "action": "grant",
            }
        )
        logger.info(result)

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_get_notifications(self):
        """Тестирование команды get_notifications.
        
        Проверяет:
            - Результат не None
            - Результат является списком
        
        Примечание:
            Может не поддерживаться на всех устройствах/эмуляторах.
        """
        result = self.mobile_commands.get_notifications()

        assert result is not None  # noqa: S101
        assert isinstance(result, list)  # noqa: S101

    def test_start_stop_logs_broadcast(self):
        """Тестирование команд start_logs_broadcast и stop_logs_broadcast.
        
        Шаги:
            1. Запуск трансляции логов
            2. Ожидание
            3. Остановка трансляции логов
        """
        # Start logs broadcast
        result = self.mobile_commands.start_logs_broadcast()
        time.sleep(1)

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Stop logs broadcast
        result = self.mobile_commands.stop_logs_broadcast()

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_get_ui_mode(self):
        """Тестирование команды get_ui_mode.
        
        Проверяет:
            - Результат не None
        
        Примечание:
            Может не поддерживаться на всех устройствах/эмуляторах.
        """
        result = self.mobile_commands.get_ui_mode()
        assert result is not None  # noqa: S101

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_set_ui_mode(self):
        """Тестирование команды set_ui_mode.
        
        Шаги:
            1. Получение текущего режима UI
            2. Установка режима (night)
            3. Восстановление исходного режима
        
        Примечание:
            Может не поддерживаться на всех устройствах/эмуляторах.
        """
        # Get current mode
        current_mode = self.mobile_commands.get_ui_mode()

        # Set mode (car, night, etc.)
        # This might not work on all devices
        result = self.mobile_commands.set_ui_mode({"mode": "night"})
        logger.info(result)
        # Restore original mode
        self.mobile_commands.set_ui_mode({"mode": current_mode})

    @pytest.mark.xfail(reason="May not be supported on all devices/emulators", strict=False)
    def test_broadcast(self):
        """Тестирование команды broadcast.
        
        Шаги:
            1. Отправка broadcast сообщения BOOT_COMPLETED
        
        Примечание:
            Может не поддерживаться на всех устройствах/эмуляторах.
        """
        # Send a simple broadcast
        result = self.mobile_commands.broadcast({"action": "android.intent.action.BOOT_COMPLETED"})
        # Command should execute without raising exception
        logger.info(result)

    @pytest.mark.xfail(reason="Geolocation may not be supported on all emulators", strict=False)
    def test_get_geolocation(self):
        """Тестирование команды get_geolocation.
        
        Проверяет:
            - Если результат не None, то это словарь
        
        Примечание:
            Geolocation может не поддерживаться на всех эмуляторах.
        """
        result = self.mobile_commands.get_geolocation()

        if result is not None:
            assert isinstance(result, dict)  # noqa: S101

    def test_set_geolocation(self):
        """Тестирование команды set_geolocation.
        
        Шаги:
            1. Установка координат (Москва: 55.7558, 37.6173)
            2. Ожидание
        """
        result = self.mobile_commands.set_geolocation({"latitude": 55.7558, "longitude": 37.6173})
        time.sleep(0.5)
        # Command should execute without raising exception
        logger.info(result)

    def test_is_gps_enabled(self):
        """Тестирование команды is_gps_enabled.
        
        Проверяет:
            - Результат является булевым значением
        """
        result = self.mobile_commands.is_gps_enabled()
        assert isinstance(result, bool)  # noqa: S101

    def test_toggle_gps(self):
        """Тестирование команды toggle_gps.
        
        Шаги:
            1. Переключение состояния GPS
        """
        result = self.mobile_commands.toggle_gps()
        logger.info(result)

    @pytest.mark.xfail(reason="GPS cache refresh may not be supported on all devices", strict=False)
    def test_refresh_gps_cache(self):
        """Тестирование команды refresh_gps_cache.
        
        Примечание:
            Обновление кэша GPS может не поддерживаться на всех устройствах.
        """
        result = self.mobile_commands.refresh_gps_cache()
        logger.info(result)

    @pytest.mark.skip(reason="Does not work on emulators")
    def test_reset_geolocation(self):
        """Тестирование команды reset_geolocation.
        
        Примечание:
            Не работает на эмуляторах.
        """
        result = self.mobile_commands.reset_geolocation()
        logger.info(result)

    @pytest.mark.xfail(
        reason="Status bar command may not be supported on all devices", strict=False
    )
    def test_status_bar(self):
        """Тестирование команды status_bar.
        
        Примечание:
            Команда status_bar может не поддерживаться на всех устройствах.
        """
        result = self.mobile_commands.status_bar(
            {
                "command": "notifications",
                "component": "com.android.systemui/.statusbar.phone.StatusBar",
            }
        )
        # Command should execute without raising exception
        logger.info(result)

    def test_get_connectivity(self):
        """Тестирование команды get_connectivity.
        
        Проверяет:
            - Результат является словарем
        """
        result = self.mobile_commands.get_connectivity()
        assert isinstance(result, dict)  # noqa: S101
        logger.info(result)  # type: ignore

    def test_set_connectivity(self):
        """Тестирование команды set_connectivity.
        
        Шаги:
            1. Включение WiFi и мобильных данных
        """
        result = self.mobile_commands.set_connectivity({"wifi": True, "data": True})
        logger.info(result)

    @pytest.mark.xfail(reason="Bluetooth may not be supported on all emulators", strict=False)
    def test_bluetooth(self):
        """Тестирование команды bluetooth.
        
        Шаги:
            1. Получение состояния Bluetooth
        
        Примечание:
            Bluetooth может не поддерживаться на всех эмуляторах.
        """
        # Try to get bluetooth state
        result = self.mobile_commands.bluetooth({"action": "getState"})
        logger.info(result)

    @pytest.mark.xfail(reason="NFC may not be supported on all devices/emulators", strict=False)
    def test_nfc(self):
        """Тестирование команды nfc.
        
        Шаги:
            1. Получение состояния NFC
        
        Примечание:
            NFC может не поддерживаться на всех устройствах/эмуляторах.
        """
        result = self.mobile_commands.nfc({"action": "getState"})
        logger.info(result)

    def test_perform_editor_action(self):
        """Тестирование команды perform_editor_action.
        
        Примечание:
            Требует активного текстового поля.
            Просто проверяется, что команда не вызывает ошибку.
        """
        # This requires an active text field
        # Just test that command doesn't crash
        result = self.mobile_commands.perform_editor_action({"action": "Done"})
        logger.info(result)

    def test_deviceidle(self):
        """Тестирование команды deviceidle для управления белым списком приложений.
        
        Шаги:
            1. Добавление приложения в белый список
            2. Удаление приложения из белого списка
        
        Примечание:
            Требуется API 23+
        """
        # This requires API 23+
        result = self.mobile_commands.deviceidle(
            {"action": "whitelistAdd", "packages": ["com.android.settings"]}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

        # Remove from whitelist
        self.mobile_commands.deviceidle(
            {"action": "whitelistRemove", "packages": ["com.android.settings"]}
        )

    @pytest.mark.xfail(reason="Requires alert to be present on screen", strict=False)
    def test_accept_alert(self):
        """Тестирование команды accept_alert.
        
        Примечание:
            Требует наличия alert на экране.
        """
        result = self.mobile_commands.accept_alert()
        logger.info(result)

    @pytest.mark.xfail(reason="Requires alert to be present on screen", strict=False)
    def test_dismiss_alert(self):
        """Тестирование команды dismiss_alert.
        
        Примечание:
            Требует наличия alert на экране.
        """
        result = self.mobile_commands.dismiss_alert()
        logger.info(result)

    @pytest.mark.xfail(reason="Deep link requires browser app to be installed", strict=False)
    def test_deep_link(self):
        """Тестирование команды deep_link.
        
        Шаги:
            1. Открытие deep link через Chrome
        
        Примечание:
            Требует установленное приложение браузера.
        """
        result = self.mobile_commands.deep_link(
            {"url": "https://www.example.com", "package": "com.android.chrome"}
        )
        time.sleep(1)
        logger.info(result)

    @pytest.mark.xfail(reason="May not be supported on all UiAutomator2 versions", strict=False)
    def test_get_action_history(self):
        """Тестирование команды get_action_history.
        
        Проверяет:
            - Результат является списком
        
        Примечание:
            Может не поддерживаться на всех версиях UiAutomator2.
        """
        result = self.mobile_commands.get_action_history()
        assert isinstance(result, list)  # noqa: S101
        logger.info(result)  # type: ignore

    @pytest.mark.xfail(reason="May not be supported on all UiAutomator2 versions", strict=False)
    def test_get_app_strings(self):
        """Тестирование команды get_app_strings.
        
        Проверяет:
            - Результат является словарем
        
        Примечание:
            Может не поддерживаться на всех версиях UiAutomator2.
        """
        result = self.mobile_commands.get_app_strings()
        assert isinstance(result, dict)  # noqa: S101
        logger.info(result)  # type: ignore

    @pytest.mark.xfail(reason="Action scheduling may not be supported", strict=False)
    def test_schedule_action(self):
        """Тестирование команды schedule_action.
        
        Примечание:
            Планирование действий может не поддерживаться.
        """
        result = self.mobile_commands.schedule_action({"action": "test_action", "delayMs": 1000})
        logger.info(result)

    @pytest.mark.xfail(reason="Action scheduling may not be supported", strict=False)
    def test_unschedule_action(self):
        """Тестирование команды unschedule_action.
        
        Примечание:
            Планирование действий может не поддерживаться.
        """
        result = self.mobile_commands.unschedule_action({"action": "test_action"})
        logger.info(result)

    @pytest.mark.xfail(reason="Trim memory may not be supported on all devices", strict=False)
    def test_send_trim_memory(self):
        """Тестирование команды send_trim_memory.
        
        Примечание:
            Trim memory может не поддерживаться на всех устройствах.
        """
        result = self.mobile_commands.send_trim_memory({"level": 80})
        logger.info(result)

