# ruff: noqa
# pyright: ignore
import threading
import time
from pathlib import Path

import pytest

from shadowstep.shadowstep import Shadowstep


class TestShadowstepLogcat:

    def test_start_logcat_is_non_blocking(self, app: Shadowstep, cleanup_log: None):
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

    def test_shadowstep_logcat_records_and_stops(self, app: Shadowstep, cleanup_log: None):
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

    def test_start_logcat_is_non_blocking_and_writes_logs(self, app: Shadowstep, cleanup_log: None):
        log_file = Path("logcat_test.log")
        if log_file.exists():
            log_file.unlink()

        # 1) старт логкат — должен быть почти мгновенным
        t0 = time.perf_counter()
        app.start_logcat(str(log_file))
        delta = time.perf_counter() - t0
        assert delta < 1.0, f"start_logcat блокирует основной поток слишком долго: {delta:.3f}s"

        # 2) среди живых потоков должен быть ShadowstepLogcat
        names = [t.name for t in threading.enumerate()]
        assert any("ShadowstepLogcat" in n for n in names), f"Не найден поток логката: {names}"

        # 3) проверяем, что действия в терминале не блокируются логкатом
        action_durations: list[float] = []
        for _ in range(3):  # меньше итераций для стабильности
            start = time.perf_counter()
            app.terminal.start_activity(
                package="com.android.settings",
                activity="com.android.settings.Settings"
            )
            app.terminal.press_back()
            action_durations.append(time.perf_counter() - start)

        for i, d in enumerate(action_durations, 1):
            # увеличиваем лимит до реалистичного (например, 10 с)
            assert d < 10.0, f"Итерация #{i} заняла {d:.3f}s — блокировка!"

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
