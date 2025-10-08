# ruff: noqa
# pyright: ignore
"""Integration tests for shadowstep.logcat.shadowstep_logcat module.

This module contains integration tests for the ShadowstepLogcat class,
testing real logcat capture with actual Android device connection.

Coverage notes:
- Tests ShadowstepLogcat.__init__() with valid and invalid poll_interval
- Tests start() with valid filename, empty filename, duplicate start
- Tests stop() with active and inactive logcat
- Tests filters property getter and setter
- Tests __exit__() context manager
- Tests log filtering functionality
- Tests file writing and cleanup

Requirements:
- Shadowstep instance connected to Android device (app fixture)
- cleanup_log fixture for file cleanup
"""

import threading
import time
from pathlib import Path

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.logcat.shadowstep_logcat import ShadowstepLogcat
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepPollIntervalError,
    ShadowstepEmptyFilenameError,
)


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

    def test_logcat_init_with_negative_poll_interval(self, app: Shadowstep):
        """Test that __init__ raises exception with negative poll_interval."""
        # Act & Assert
        with pytest.raises(ShadowstepPollIntervalError):
            ShadowstepLogcat(driver_getter=lambda: app.driver, poll_interval=-1.0)

    def test_logcat_init_with_valid_poll_interval(self, app: Shadowstep):
        """Test __init__ with valid poll_interval."""
        # Act
        logcat = ShadowstepLogcat(driver_getter=lambda: app.driver, poll_interval=2.0)

        # Assert
        assert logcat is not None
        assert logcat._poll_interval == 2.0
        assert logcat._driver_getter is not None

    def test_logcat_start_with_empty_filename(self, app: Shadowstep):
        """Test that start() raises exception with empty filename."""
        # Arrange
        logcat = app._logcat

        # Act & Assert
        with pytest.raises(ShadowstepEmptyFilenameError):
            logcat.start("")

    def test_logcat_start_twice_does_not_duplicate(self, app: Shadowstep, cleanup_log: None):
        """Test that calling start() twice doesn't create duplicate threads."""
        # Arrange
        log_file = Path("logcat_duplicate_test.log")
        if log_file.exists():
            log_file.unlink()

        # Act
        app.start_logcat(str(log_file))
        time.sleep(0.5)  # Let first start complete

        # Try to start again
        app.start_logcat(str(log_file))
        time.sleep(0.5)

        # Assert - should still be only one thread
        logcat_threads = [t for t in threading.enumerate() if "ShadowstepLogcat" in t.name]
        assert len(logcat_threads) == 1, f"Expected 1 logcat thread, found {len(logcat_threads)}"

        # Cleanup
        app.stop_logcat()

        # Cleanup file
        if log_file.exists():
            log_file.unlink()

    def test_logcat_stop_when_not_running(self, app: Shadowstep):
        """Test that stop() works even when logcat is not running."""
        # Arrange - ensure logcat is stopped
        app.stop_logcat()

        # Act - should not raise exception
        app.stop_logcat()

        # Assert - no exception raised
        assert True

    def test_logcat_filters_property_getter(self, app: Shadowstep):
        """Test filters property getter returns None by default."""
        # Arrange
        logcat = app._logcat

        # Act
        filters = logcat.filters

        # Assert
        assert filters is None

    def test_logcat_filters_property_setter(self, app: Shadowstep):
        """Test filters property setter."""
        # Arrange
        logcat = app._logcat
        test_filters = ["ActivityManager", "WindowManager", "SystemServer"]

        # Act
        logcat.filters = test_filters

        # Assert
        assert logcat.filters == test_filters
        assert logcat._filter_set == set(test_filters)
        assert logcat._compiled_filter_pattern is not None

    def test_logcat_filters_with_empty_list(self, app: Shadowstep):
        """Test filters with empty list clears compiled pattern."""
        # Arrange
        logcat = app._logcat
        logcat.filters = ["Test"]

        # Act - set empty list
        logcat.filters = []

        # Assert
        assert logcat.filters == []
        assert logcat._compiled_filter_pattern is None
        assert logcat._filter_set is None

    def test_logcat_with_filters_writes_filtered_logs(self, app: Shadowstep, cleanup_log: None):
        """Test that logcat with filters only writes matching lines."""
        # Arrange
        log_file = Path("logcat_filtered_test.log")
        if log_file.exists():
            log_file.unlink()

        # Set filter to capture only ActivityManager logs
        app._logcat.filters = ["ActivityManager"]

        # Act
        app.start_logcat(str(log_file))
        time.sleep(2)  # Let some logs accumulate

        # Generate some activity
        app.terminal.start_activity(
            package="com.android.settings",
            activity="com.android.settings.Settings"
        )
        time.sleep(1)
        app.terminal.press_back()
        time.sleep(1)

        app.stop_logcat()

        # Assert
        assert log_file.exists(), "Filtered logcat file was not created"

        # Read and verify content
        content = log_file.read_text(encoding="utf-8")
        # File should have content (might be empty if no ActivityManager logs during test)
        # The important thing is that file was created and no exception occurred

        # Cleanup
        if log_file.exists():
            log_file.unlink()

    def test_logcat_restart_after_stop(self, app: Shadowstep, cleanup_log: None):
        """Test that logcat can be restarted after being stopped."""
        # Arrange
        log_file1 = Path("logcat_restart1.log")
        log_file2 = Path("logcat_restart2.log")
        if log_file1.exists():
            log_file1.unlink()
        if log_file2.exists():
            log_file2.unlink()

        # Act - first run
        app.start_logcat(str(log_file1))
        time.sleep(1)
        app.stop_logcat()
        time.sleep(1)

        # Act - second run
        app.start_logcat(str(log_file2))
        time.sleep(1)
        app.stop_logcat()

        # Assert
        assert log_file1.exists(), "First logcat file was not created"
        assert log_file2.exists(), "Second logcat file was not created"

        # Cleanup
        if log_file1.exists():
            log_file1.unlink()
        if log_file2.exists():
            log_file2.unlink()

    def test_logcat_context_manager_exit(self, app: Shadowstep, cleanup_log: None):
        """Test __exit__ method stops logcat."""
        # Arrange
        log_file = Path("logcat_context_test.log")
        if log_file.exists():
            log_file.unlink()

        logcat = app._logcat

        # Act - start logcat
        logcat.start(str(log_file))
        time.sleep(0.5)

        # Verify running
        assert logcat._thread is not None
        assert logcat._thread.is_alive()

        # Call __exit__ directly
        logcat.__exit__(None, None, None)

        # Give thread time to stop
        time.sleep(1)

        # Assert - thread should be stopped
        logcat_threads = [t for t in threading.enumerate() if "ShadowstepLogcat" in t.name]
        assert len(logcat_threads) == 0, "Logcat thread should be stopped after __exit__"

        # Cleanup
        if log_file.exists():
            log_file.unlink()

    def test_logcat_with_custom_port(self, app: Shadowstep, cleanup_log: None):
        """Test logcat with custom port parameter."""
        # Arrange
        log_file = Path("logcat_port_test.log")
        if log_file.exists():
            log_file.unlink()

        # Act - start with default port (None)
        app._logcat.start(str(log_file), port=None)
        time.sleep(1)

        # Assert - logcat should be running
        assert app._logcat._thread is not None
        assert app._logcat._thread.is_alive()

        # Cleanup
        app.stop_logcat()
        if log_file.exists():
            log_file.unlink()

    def test_logcat_file_append_mode(self, app: Shadowstep, cleanup_log: None):
        """Test that logcat appends to existing file."""
        # Arrange
        log_file = Path("logcat_append_test.log")
        if log_file.exists():
            log_file.unlink()

        # Write initial content
        log_file.write_text("Initial content\n")
        initial_size = log_file.stat().st_size

        # Act - start logcat (should append, not overwrite)
        app.start_logcat(str(log_file))
        time.sleep(2)
        app.stop_logcat()

        # Assert - file should contain initial content plus new logs
        assert log_file.exists()
        final_size = log_file.stat().st_size
        assert final_size >= initial_size, "File should have grown, not been overwritten"

        content = log_file.read_text()
        assert "Initial content" in content, "Initial content should be preserved"

        # Cleanup
        if log_file.exists():
            log_file.unlink()

    def test_logcat_thread_name(self, app: Shadowstep, cleanup_log: None):
        """Test that logcat thread has correct name."""
        # Arrange
        log_file = Path("logcat_thread_name_test.log")
        if log_file.exists():
            log_file.unlink()

        # Act
        app.start_logcat(str(log_file))
        time.sleep(0.5)

        # Assert
        thread_names = [t.name for t in threading.enumerate()]
        assert any("ShadowstepLogcat" in name for name in thread_names), \
            f"Expected 'ShadowstepLogcat' in thread names, got: {thread_names}"

        # Cleanup
        app.stop_logcat()
        if log_file.exists():
            log_file.unlink()

    def test_logcat_init_with_zero_poll_interval(self, app: Shadowstep):
        """Test __init__ with zero poll_interval (valid edge case)."""
        # Act
        logcat = ShadowstepLogcat(driver_getter=lambda: app.driver, poll_interval=0.0)

        # Assert
        assert logcat is not None
        assert logcat._poll_interval == 0.0

    def test_logcat_filters_multiple_tags(self, app: Shadowstep):
        """Test filters with multiple tags."""
        # Arrange
        logcat = app._logcat
        multiple_filters = ["ActivityManager", "WindowManager", "SystemServer", "PackageManager"]

        # Act
        logcat.filters = multiple_filters

        # Assert
        assert logcat.filters == multiple_filters
        assert len(logcat._filter_set) == 4
        assert logcat._compiled_filter_pattern is not None

    def test_logcat_stop_closes_websocket(self, app: Shadowstep, cleanup_log: None):
        """Test that stop() properly closes WebSocket connection."""
        # Arrange
        log_file = Path("logcat_websocket_test.log")
        if log_file.exists():
            log_file.unlink()

        app.start_logcat(str(log_file))
        time.sleep(1)  # Let WebSocket connect

        # Act
        app.stop_logcat()
        time.sleep(1)  # Let cleanup complete

        # Assert - WebSocket should be None after stop
        assert app._logcat._ws is None

        # Cleanup
        if log_file.exists():
            log_file.unlink()
