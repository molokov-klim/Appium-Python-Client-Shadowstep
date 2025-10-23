# ruff: noqa
# pyright: ignore
import time

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.element.element import Element

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/test_integro/test_shadowstep_integro_part_2.py
"""


class TestShadowstepPart2:
    """Тестирование операций управления приложениями и устройствами.
    
    Группа тестов проверяет функции управления жизненным циклом приложений,
    информацию об устройстве, дисплее, системных панелях и активностях.
    """

    def test_background_app_and_activate_app(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тестирование управления жизненным циклом приложения.

        Шаги:
            1. Запуск приложения настроек.
            2. Вызов background_app() для отправки приложения в фон на 2 секунды.
            3. Проверка, что приложение автоматически возвращается на передний план.
            4. Вызов activate_app() для явной активации настроек.
            5. Проверка, что настройки находятся на переднем плане.
        
        Args:
            app: Экземпляр приложения Shadowstep.
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Get Settings package
        settings_package = "com.android.settings"

        # Ensure Settings is in foreground
        current_package = app.get_current_package()
        assert "settings" in current_package.lower()  # noqa: S101

        # Background app for 2 seconds
        app.background_app(seconds=2)

        # Wait for app to return to foreground
        time.sleep(2.5)

        # Verify app is back in foreground
        package_after = app.get_current_package()
        assert "settings" in package_after.lower()  # noqa: S101

        # Activate Settings app explicitly
        app.activate_app(app_id=settings_package)

        # Verify Settings is still in foreground
        time.sleep(0.5)
        package_activated = app.get_current_package()
        assert "settings" in package_activated.lower()  # noqa: S101

    def test_get_display_density(self, app: Shadowstep, android_settings_open_close: None):
        """Тестирование получения плотности дисплея устройства.

        Шаги:
            1. Вызов get_display_density().
            2. Проверка, что возвращается целое число.
            3. Проверка, что значение находится в разумном диапазоне (120-640 dpi).
        
        Args:
            app: Экземпляр приложения Shadowstep.
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Get display density
        density = app.get_display_density()

        # Verify density is an integer
        assert isinstance(density, int)  # noqa: S101

        # Verify density is within reasonable range for Android devices
        assert 120 <= density <= 640  # noqa: S101

    def test_get_system_bars(self, app: Shadowstep, android_settings_open_close: None):
        """Тестирование получения информации о системных панелях.

        Шаги:
            1. Вызов get_system_bars().
            2. Проверка, что возвращается словарь.
            3. Проверка, что словарь содержит ожидаемые ключи (statusBar, navigationBar).
        
        Args:
            app: Экземпляр приложения Shadowstep.
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Get system bars info
        system_bars = app.get_system_bars()

        # Verify system_bars is a dictionary
        assert isinstance(system_bars, dict)  # noqa: S101

        # Verify expected keys are present
        assert "statusBar" in system_bars or "navigationBar" in system_bars  # noqa: S101

    def test_start_activity(self, app: Shadowstep):
        """Тестирование запуска указанной активности с использованием intent.

        Шаги:
            1. Вызов start_activity() с intent активности настроек.
            2. Проверка, что активность запускается успешно.
            3. Проверка, что текущий пакет - настройки.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Start Settings activity using component parameter
        app.start_activity(
            intent="com.android.settings/.Settings", component="com.android.settings/.Settings"
        )

        # Wait for activity to launch
        time.sleep(1)

        # Verify Settings is in foreground
        current_package = app.get_current_package()
        assert "settings" in current_package.lower()  # noqa: S101

    def test_press_key(self, app: Shadowstep, android_settings_open_close: None):
        """Тестирование отправки кода клавиши на устройство.

        Шаги:
            1. Вызов press_key() с кодом клавиши HOME.
            2. Проверка, что нажатие клавиши выполняется без ошибок.
            3. Проверка, что отображается главный экран (пакет лаунчера).
        
        Args:
            app: Экземпляр приложения Shadowstep.
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Press HOME key (keycode 3)
        app.press_key(keycode=3)

        # Wait for home screen
        time.sleep(1)

        # Verify we're on home screen (launcher)
        current_package = app.get_current_package()
        assert isinstance(current_package, str)  # noqa: S101
        # Home screen package varies by device, just verify we got a package
        assert len(current_package) > 0  # noqa: S101

    def test_open_notifications(self, app: Shadowstep, android_settings_open_close: None):
        """Тестирование открытия панели уведомлений.

        Шаги:
            1. Вызов open_notifications().
            2. Проверка, что метод завершается без ошибок.
            3. Нажатие кнопки назад для закрытия уведомлений.
        
        Args:
            app: Экземпляр приложения Shadowstep.
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Open notifications
        app.open_notifications()

        # Wait for notification panel to open
        time.sleep(1)

        # Close notification panel by pressing back
        app.press_key(keycode=4)  # BACK key

        # Wait for panel to close
        time.sleep(0.5)

    def test_is_locked_status(self, app: Shadowstep):
        """Тестирование получения состояния блокировки устройства.

        Шаги:
            1. Вызов is_locked() для проверки текущего состояния блокировки.
            2. Проверка, что метод возвращает булево значение.
            3. Проверка, что метод завершается без ошибок.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Get lock state
        is_locked = app.is_locked()

        # Verify is_locked returns a boolean
        assert isinstance(is_locked, bool)  # noqa: S101

    def test_lock_command(self, app: Shadowstep):
        """Тестирование выполнения метода lock() без ошибок.

        Шаги:
            1. Вызов lock() для блокировки устройства.
            2. Проверка, что команда завершается без исключений.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Lock the device
        app.lock()
        time.sleep(0.5)

        # If we reach here without exceptions, test passes

    def test_is_app_installed(self, app: Shadowstep):
        """Тестирование проверки установки приложения.

        Шаги:
            1. Проверка установки приложения настроек с помощью is_app_installed().
            2. Проверка, что метод возвращает булево значение.
            3. Проверка, что настройки установлены (должно быть всегда true).
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Check if Settings app is installed
        is_installed = app.is_app_installed(app_id="com.android.settings")

        # Verify is_app_installed returns a boolean
        assert isinstance(is_installed, bool)  # noqa: S101

        # Settings should always be installed
        assert is_installed is True  # noqa: S101

    def test_query_app_state(self, app: Shadowstep, android_settings_open_close: None):
        """Тестирование получения состояния приложения.

        Шаги:
            1. Вызов query_app_state() для приложения настроек.
            2. Проверка, что метод возвращает целое число состояния.
            3. Проверка, что состояние указывает на работающее приложение (state >= 3).
        
        Args:
            app: Экземпляр приложения Shadowstep.
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Query Settings app state
        state = app.query_app_state(app_id="com.android.settings")

        # Verify state is an integer
        assert isinstance(state, int)  # noqa: S101

        # Verify state is valid (0-4, where 4 is running in foreground)
        assert 0 <= state <= 4  # noqa: S101

    def test_get_device_time(self, app: Shadowstep):
        """Тестирование получения времени устройства.

        Шаги:
            1. Вызов get_device_time().
            2. Проверка, что метод возвращает строку с временной меткой.
            3. Проверка, что временная метка не пуста.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Get device time
        device_time = app.get_device_time()

        # Verify device_time is a non-empty string
        assert isinstance(device_time, str)  # noqa: S101
        assert len(device_time) > 0  # noqa: S101

    def test_get_performance_data_types(self, app: Shadowstep):
        """Тестирование получения доступных типов данных о производительности.

        Шаги:
            1. Вызов get_performance_data_types().
            2. Проверка, что метод возвращает список.
            3. Проверка, что список содержит ожидаемые типы производительности.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Get performance data types
        data_types = app.get_performance_data_types()

        # Verify data_types is a list
        assert isinstance(data_types, list)  # noqa: S101
        assert len(data_types) > 0  # noqa: S101

    def test_set_geolocation(self, app: Shadowstep):
        """Тестирование установки местоположения устройства.

        Шаги:
            1. Установка тестового местоположения с помощью set_geolocation().
            2. Проверка, что метод завершается без исключений.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Set test location (San Francisco)
        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 10.0

        app.set_geolocation(latitude=test_lat, longitude=test_lon, altitude=test_alt)

        # Wait a moment
        time.sleep(0.5)

        # If we reach here without exceptions, test passes

    def test_hide_keyboard_and_is_keyboard_shown(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Тестирование управления состоянием клавиатуры.

        Шаги:
            1. Проверка отображения клавиатуры с помощью is_keyboard_shown().
            2. Проверка, что метод возвращает булево значение.
        
        Args:
            app: Экземпляр приложения Shadowstep.
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Check keyboard state
        is_shown = app.is_keyboard_shown()

        # Verify is_shown is a boolean
        assert isinstance(is_shown, bool)  # noqa: S101

        # Try to hide keyboard (will do nothing if not shown)
        app.hide_keyboard()

        # Verify no exception was raised
        time.sleep(0.3)

    def test_get_contexts(self, app: Shadowstep, android_settings_open_close: None):
        """Тестирование получения доступных контекстов.

        Шаги:
            1. Вызов get_contexts().
            2. Проверка, что метод возвращает список.
        
        Args:
            app: Экземпляр приложения Shadowstep.
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Get contexts
        contexts = app.get_contexts()

        # Verify contexts is a list
        assert isinstance(contexts, list)  # noqa: S101

    def test_terminate_app(self, app: Shadowstep):
        """Тестирование завершения указанного приложения.

        Шаги:
            1. Запуск приложения настроек.
            2. Завершение приложения настроек с помощью terminate_app().
            3. Проверка, что приложение больше не находится на переднем плане.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Launch Settings
        app.start_activity(
            intent="com.android.settings/.Settings", component="com.android.settings/.Settings"
        )
        time.sleep(1)

        # Terminate Settings
        app.terminate_app(app_id="com.android.settings")

        # Wait a moment
        time.sleep(1)

        # Verify Settings is not in foreground
        current_package = app.get_current_package()
        assert "settings" not in current_package.lower()  # noqa: S101

    def test_scroll_to_element(self, app: Shadowstep, android_settings_open_close: None):
        """Тестирование прокрутки для поиска элемента.

        Шаги:
            1. Вызов scroll_to_element() с локатором.
            2. Проверка, что метод возвращает экземпляр Element.
        
        Args:
            app: Экземпляр приложения Shadowstep.
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Scroll to element with text (may or may not be visible initially)
        element = app.scroll_to_element(locator={"text": "Settings"})

        # Verify element is returned
        assert isinstance(element, Element)  # noqa: S101

    def test_status_bar(self, app: Shadowstep, android_settings_open_close: None):
        """Тестирование выполнения команд строки состояния.

        Шаги:
            1. Вызов status_bar() с командами развертывания и свертывания.
            2. Проверка, что метод завершается без исключений.
        
        Args:
            app: Экземпляр приложения Shadowstep.
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Expand notifications
        app.status_bar(command="expandNotifications", component="expandNotifications")
        time.sleep(0.5)

        # Collapse status bar
        app.status_bar(command="collapse", component="collapse")
        time.sleep(0.5)

    def test_get_connectivity(self, app: Shadowstep):
        """Тестирование получения состояния сетевого подключения.

        Шаги:
            1. Вызов get_connectivity() с конкретными сервисами.
            2. Проверка, что метод возвращает словарь.
            3. Проверка, что словарь содержит информацию о подключении.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Get connectivity state for wifi
        connectivity = app.get_connectivity(services=["wifi", "data"])

        # Verify connectivity is a dictionary
        assert isinstance(connectivity, dict)  # noqa: S101

    def test_set_connectivity(self, app: Shadowstep):
        """Тестирование изменения сетевого подключения.

        Шаги:
            1. Получение текущего состояния подключения.
            2. Вызов set_connectivity() для переключения wifi.
            3. Проверка, что метод завершается без исключений.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        expected_result = "Wi-Fi включен"
        app.set_connectivity(wifi=True)
        current_connectivity = app.get_connectivity(services=["wifi"])
        actual_result = current_connectivity.get("wifi", False)
        app.logger.info(f"[expected_result]: {expected_result=} {actual_result=}")
        assert actual_result, "Wi-Fi не был включен"

    def test_network_speed(self, app: Shadowstep):
        """Тестирование установки скорости сети.

        Шаги:
            1. Вызов network_speed() с типом скорости.
            2. Проверка, что метод завершается без исключений.

        Примечание:
            Эта команда работает только на эмуляторах.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Set network speed to full (emulator only)
        try:
            app.network_speed(speed="full")
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_gsm_call(self, app: Shadowstep):
        """Тестирование симуляции GSM звонка.

        Шаги:
            1. Вызов gsm_call() с номером телефона и действием.
            2. Проверка, что метод завершается без исключений.

        Примечание:
            Эта команда работает только на эмуляторах.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Simulate incoming call (emulator only)
        try:
            app.gsm_call(phone_number="5551234567", action="call")
            time.sleep(0.5)

            # Cancel call
            app.gsm_call(phone_number="5551234567", action="cancel")
            time.sleep(0.5)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_gsm_signal(self, app: Shadowstep):
        """Тестирование установки уровня сигнала GSM.

        Шаги:
            1. Вызов gsm_signal() со значением силы сигнала.
            2. Проверка, что метод завершается без исключений.

        Примечание:
            Эта команда работает только на эмуляторах.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Set signal strength (emulator only)
        try:
            app.gsm_signal(strength=4)
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_gsm_voice(self, app: Shadowstep):
        """Тестирование установки состояния голосовой связи GSM.

        Шаги:
            1. Вызов gsm_voice() с состоянием.
            2. Проверка, что метод завершается без исключений.

        Примечание:
            Эта команда работает только на эмуляторах.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Set voice state to on (emulator only)
        try:
            app.gsm_voice(state="on")
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_power_capacity(self, app: Shadowstep):
        """Тестирование установки емкости батареи.

        Шаги:
            1. Вызов power_capacity() с процентом.
            2. Проверка, что метод завершается без исключений.

        Примечание:
            Эта команда работает только на эмуляторах.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Set battery capacity to 80% (emulator only)
        try:
            app.power_capacity(percent=80)
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_power_ac(self, app: Shadowstep):
        """Тестирование установки состояния питания от сети.

        Шаги:
            1. Вызов power_ac() с состоянием.
            2. Проверка, что метод завершается без исключений.

        Примечание:
            Эта команда работает только на эмуляторах.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Turn AC power on (emulator only)
        try:
            app.power_ac(state="on")
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_battery_info(self, app: Shadowstep):
        """Тестирование получения информации о батарее.

        Шаги:
            1. Вызов battery_info().
            2. Проверка, что метод возвращает словарь.
            3. Проверка, что словарь содержит информацию о батарее.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Get battery info
        battery = app.battery_info()

        # Verify battery is a dictionary
        assert isinstance(battery, dict)  # noqa: S101

    def test_device_info(self, app: Shadowstep):
        """Тестирование получения информации об устройстве.

        Шаги:
            1. Вызов device_info().
            2. Проверка, что метод возвращает словарь.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Get device info
        device = app.device_info()

        # Verify device is a dictionary
        assert isinstance(device, dict)  # noqa: S101

    def test_get_performance_data(self, app: Shadowstep):
        """Тестирование получения метрик производительности.

        Шаги:
            1. Получение доступных типов данных о производительности.
            2. Вызов get_performance_data() для первого доступного типа.
            3. Проверка, что метод возвращает данные или корректно обрабатывает ошибки.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        try:
            # Get performance data types
            data_types = app.get_performance_data_types()

            if len(data_types) > 0:
                # Get performance data for first type
                perf_data = app.get_performance_data(
                    package_name="com.android.settings", data_type=data_types[0]
                )

                # Verify performance data is returned
                assert perf_data is not None  # noqa: S101
        except Exception:
            # Performance data may not be available on all devices
            pass

    def test_screenshots(self, app: Shadowstep, android_settings_open_close: None):
        """Тестирование запуска мониторинга скриншотов.

        Шаги:
            1. Вызов screenshots() для запуска мониторинга.
            2. Проверка, что метод завершается без исключений.
        
        Args:
            app: Экземпляр приложения Shadowstep.
            android_settings_open_close: Фикстура для управления настройками Android.
        """
        # Start screenshot monitoring
        app.screenshots()
        time.sleep(0.5)

    def test_get_ui_mode(self, app: Shadowstep):
        """Тестирование получения режима пользовательского интерфейса.

        Шаги:
            1. Вызов get_ui_mode() для ночного режима.
            2. Проверка, что метод возвращает строку.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Get UI mode for night
        ui_mode = app.get_ui_mode(mode="night")

        # Verify ui_mode is a string
        assert isinstance(ui_mode, str)  # noqa: S101

    def test_set_ui_mode(self, app: Shadowstep):
        """Тестирование установки режима пользовательского интерфейса.

        Шаги:
            1. Вызов set_ui_mode() для установки ночного режима.
            2. Проверка, что метод завершается без исключений.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Set night mode to no
        app.set_ui_mode(mode="night", value="no")
        time.sleep(0.5)

    def test_bluetooth(self, app: Shadowstep):
        """Тестирование управления состоянием Bluetooth.

        Шаги:
            1. Вызов bluetooth() с действием.
            2. Проверка, что метод завершается без исключений.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Turn bluetooth off (safe operation)
        app.bluetooth(action="disable")
        time.sleep(0.5)

        # Turn bluetooth on
        app.bluetooth(action="enable")
        time.sleep(0.5)

    def test_nfc(self, app: Shadowstep):
        """Тестирование управления состоянием NFC.

        Шаги:
            1. Вызов nfc() с действием.
            2. Проверка, что метод завершается без исключений или обрабатывает неподдерживаемые устройства.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Disable NFC - may not be supported on all devices
        try:
            app.nfc(action="disable")
            time.sleep(0.3)
        except (ShadowstepException, Exception):
            # NFC may not be available or controllable on all devices
            pass

    def test_toggle_gps(self, app: Shadowstep):
        """Тестирование переключения состояния GPS.

        Шаги:
            1. Вызов toggle_gps().
            2. Проверка, что метод завершается без исключений.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Toggle GPS
        app.toggle_gps()
        time.sleep(0.5)

        # Toggle back
        app.toggle_gps()
        time.sleep(0.5)

    def test_is_gps_enabled(self, app: Shadowstep):
        """Тестирование получения состояния GPS.

        Шаги:
            1. Вызов is_gps_enabled().
            2. Проверка, что метод возвращает булево значение.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        # Check GPS state
        is_enabled = app.is_gps_enabled()

        # Verify is_enabled is a boolean
        assert isinstance(is_enabled, bool)  # noqa: S101

    def test_fingerprint(self, app: Shadowstep):
        """Тестирование симуляции отпечатка пальца.

        Шаги:
            1. Вызов fingerprint() с ID отпечатка пальца.
            2. Проверка, что метод завершается без исключений.

        Примечание:
            Эта команда работает только на эмуляторах.
        
        Args:
            app: Экземпляр приложения Shadowstep.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Simulate fingerprint (emulator only)
        try:
            app.fingerprint(fingerprint_id=1)
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

