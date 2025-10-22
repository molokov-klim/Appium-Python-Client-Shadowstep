# ruff: noqa
# pyright: ignore
import time

from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_gestures_integro_part_4.py
"""


class TestElementGesturesPart4:
    """Тесты специальных жестов взаимодействия с элементами.

    Данный класс содержит тесты для специальных жестов взаимодействия с элементами,
    включая zoom и unzoom операции.
    """

    def test_zoom(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Тест увеличения масштаба элемента.

        Проверяет корректность выполнения операции увеличения масштаба
        элемента "Network & internet".

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_network.zoom()
        time.sleep(3)

    def test_unzoom(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Тест уменьшения масштаба элемента.

        Проверяет корректность выполнения операции уменьшения масштаба
        элемента "Network & internet".

        Args:
            app: Экземпляр Shadowstep для взаимодействия с приложением.
            android_settings_open_close: Фикстура для открытия и закрытия настроек Android.
        """
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_network.unzoom()
        time.sleep(3)
