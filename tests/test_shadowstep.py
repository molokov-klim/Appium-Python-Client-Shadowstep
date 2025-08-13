import os
import subprocess
import threading
import time

import pytest

from shadowstep.element.element import Element
from shadowstep.shadowstep import Shadowstep
import time
from pathlib import Path


class TestShadowstep:
    """
    A class to test various functionalities of the Shadowstep application.
    """

    def test_get_element(self, app: Shadowstep) -> None:
        """
        Test retrieving an element from the Shadowstep application.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.

        Asserts:
            Asserts that the locator of the retrieved element matches the expected locator.
        """
        element = app.get_element(locator={'content-desc': 'Phone'},
                                  timeout=29,
                                  poll_frequency=0.7,
                                  ignored_exceptions=[TimeoutError],
                                  contains=True)
        assert element.locator == {'content-desc': 'Phone'}
        assert isinstance(element, Element)
        assert element.driver is None
        assert element.base is not None
        assert element.timeout == 29
        assert element.poll_frequency == 0.7
        assert element.ignored_exceptions == [TimeoutError]
        assert element.contains is True
        element.tap()
        assert element.driver is not None

    def test_find_and_get_element(self, app: Shadowstep, android_settings):
        el = app.find_and_get_element({'text': 'System'})
        assert el.get_attribute('text') == 'System'

class TestShadowstepLogcat:

    def test_start_logcat_is_non_blocking(self, app):
        # подготавливаем файл
        log_file = Path("logcat_test.log")
        if log_file.exists():
            log_file.unlink()

        # замер времени вызова start_logcat
        t0 = time.perf_counter()
        app.start_logcat(str(log_file))
        delta = time.perf_counter() - t0

        # допускаем, что старт может занять до 100 мс,
        # но явно не больше секунды
        assert delta < 0.1, f"start_logcat слишком долго блокирует main thread: {delta:.3f}s"

        # а теперь проверим, что логи действительно пишутся в фоне,
        # не дожидаясь возвращения из start_logcat
        # для этого заодно пойдёт наш основной цикл навигации
        for _ in range(5):
            app.terminal.start_activity(
                package="com.android.settings",
                activity="com.android.settings.Settings"
            )
            time.sleep(0.5)
            app.terminal.press_back()

        # останавливаем приём в фоне
        app.stop_logcat()

    def test_shadowstep_logcat_records_and_stops(self, app):
        log_file = Path("logcat_test.log")
        if log_file.exists():
            log_file.unlink()

        app.start_logcat(str(log_file))
        for _ in range(9):
            app.terminal.start_activity(
                package="com.android.settings",
                activity="com.android.settings.Settings"
            )
            time.sleep(1)
            app.terminal.press_back()
        app.stop_logcat()

        assert log_file.exists(), "Logcat file was not создан"
        content = log_file.read_text(encoding="utf-8")
        assert (
            "ActivityManager" in content
            or "Displayed" in content
            or len(content.strip()) > 0
        ), "Logcat file пустой"

    def test_start_logcat_is_non_blocking_and_writes_logs(self, app):
        log_file = Path("logcat_test.log")
        if log_file.exists():
            log_file.unlink()

        # 1) старт логкат–приёмника должен вернуть ≲1 s
        t0 = time.perf_counter()
        app.start_logcat(str(log_file))
        delta = time.perf_counter() - t0
        assert delta < 1.0, f"start_logcat блокирует основной поток слишком долго: {delta:.3f}s"

        # 2) среди живых потоков должен быть ShadowstepLogcat
        names = [t.name for t in threading.enumerate()]
        assert any("ShadowstepLogcat" in n for n in names), f"Не найден поток логката: {names}"

        # 3) несколько быстрых действий (<2 s каждое)
        durations = []
        for _ in range(5):
            d0 = time.perf_counter()
            for _ in range(5):
                app.terminal.start_activity(
                    package="com.android.settings",
                    activity="com.android.settings.Settings"
                )
                app.terminal.press_back()
            durations.append(time.perf_counter() - d0)
        for i, d in enumerate(durations, 1):
            assert d < 3.0, f"Итерация #{i} заняла {d:.3f}s — блокировка!"

        # 4) дождаться первых байт в файле (≤10 s)
        deadline = time.time() + 10
        while time.time() < deadline:
            if log_file.exists() and log_file.stat().st_size > 0:
                break
            time.sleep(0.5)
        else:
            pytest.fail("Лог-файл пустой — фон не пишет данные")

        # 5) остановка приёма
        app.stop_logcat()

        # 6) дать потоку пару секунд на завершение
        time.sleep(2.0)
        names_after = [t.name for t in threading.enumerate()]
        assert not any("ShadowstepLogcat" in n for n in names_after), f"Поток не остановлен: {names_after}"

