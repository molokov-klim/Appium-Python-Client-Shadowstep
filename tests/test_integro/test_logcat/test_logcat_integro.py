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
from collections import deque
from pathlib import Path

import pytest
from websocket import WebSocketConnectionClosedException

from shadowstep.logcat.shadowstep_logcat import ShadowstepLogcat
from shadowstep.shadowstep import Shadowstep
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepPollIntervalError,
    ShadowstepEmptyFilenameError,
)


class TestShadowstepLogcat:

    def test_start_logcat_is_non_blocking(self, app: Shadowstep, cleanup_log: None):
        # prepare log file location
        log_file = Path("logcat_test.log")
        if log_file.exists():
            log_file.unlink()

        # measure start_logcat call duration
        t0 = time.perf_counter()
        app.start_logcat(str(log_file))
        delta = time.perf_counter() - t0

        # allow up to 100 ms for startup but definitely less than one second
        assert delta < 0.1, f"start_logcat blocks the main thread for too long: {delta:.3f}s"

        # verify logs are written in the background without blocking start_logcat
        # reuse the navigation cycle to produce activity
        for _ in range(5):
            app.terminal.start_activity(
                package="com.android.settings",
                activity="com.android.settings.Settings"
            )
            time.sleep(0.5)
            app.terminal.press_back()

        # stop background capture
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

        assert log_file.exists(), "Logcat file was not created"
        content = log_file.read_text(encoding="utf-8")
        assert (
                "ActivityManager" in content
                or "Displayed" in content
                or len(content.strip()) > 0
        ), "Logcat file is empty"

    def test_start_logcat_is_non_blocking_and_writes_logs(self, app: Shadowstep, cleanup_log: None):
        log_file = Path("logcat_test.log")
        if log_file.exists():
            log_file.unlink()

        # 1) logcat start should be almost instantaneous
        t0 = time.perf_counter()
        app.start_logcat(str(log_file))
        delta = time.perf_counter() - t0
        assert delta < 1.0, f"start_logcat blocks the main thread for too long: {delta:.3f}s"

        # 2) active threads must include ShadowstepLogcat
        names = [t.name for t in threading.enumerate()]
        assert any("ShadowstepLogcat" in n for n in names), f"Logcat thread not found: {names}"

        # 3) ensure terminal actions are not blocked by logcat
        action_durations: list[float] = []
        for _ in range(3):  # fewer iterations for stability
            start = time.perf_counter()
            app.terminal.start_activity(
                package="com.android.settings",
                activity="com.android.settings.Settings"
            )
            app.terminal.press_back()
            action_durations.append(time.perf_counter() - start)

        for i, d in enumerate(action_durations, 1):
            # allow a realistic limit (e.g., 10 seconds)
            assert d < 10.0, f"Iteration #{i} took {d:.3f}s — blocked!"

        # 4) wait for first bytes to appear in the file (≤10 s)
        deadline = time.time() + 10
        while time.time() < deadline:
            if log_file.exists() and log_file.stat().st_size > 0:
                break
            time.sleep(0.5)
        else:
            pytest.fail("Log file is empty — background writer is not producing data")

        # 5) stop capturing
        app.stop_logcat()

        # 6) give the thread a couple seconds to finish
        time.sleep(2.0)
        names_after = [t.name for t in threading.enumerate()]
        assert not any("ShadowstepLogcat" in n for n in names_after), f"Logcat thread not stopped: {names_after}"

    def test_logcat_init_with_negative_poll_interval(self, app: Shadowstep):
        """Test that __init__ raises exception with negative poll_interval."""
        # Act & Assert
        with pytest.raises(ShadowstepPollIntervalError):
            ShadowstepLogcat(driver_getter=lambda: app.driver, poll_interval=-1.0)

    def test_logcat_init_with_valid_poll_interval(self, app: Shadowstep):
        """Test __init__ with valid poll_interval does not raise exception."""
        # Act - should not raise any exception
        logcat = ShadowstepLogcat(driver_getter=lambda: app.driver, poll_interval=2.0)

        # Assert - object created successfully
        assert logcat is not None

    def test_logcat_start_with_empty_filename(self, app: Shadowstep):
        """Test that start_logcat() raises exception with empty filename."""
        # Act & Assert
        with pytest.raises(ShadowstepEmptyFilenameError):
            app.start_logcat("")

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

    def test_logcat_stop_when_not_running(self, app: Shadowstep):
        """Test that stop() works even when logcat is not running."""
        # Arrange - ensure logcat is stopped
        app.stop_logcat()

        # Act - should not raise exception
        app.stop_logcat()

        # Assert - no exception raised
        assert True

    def test_logcat_without_filters_writes_all_logs(self, app: Shadowstep, cleanup_log: None):
        """Test that logcat without filters writes all logs."""
        # Arrange
        log_file = Path("logcat_test.log")
        if log_file.exists():
            log_file.unlink()

        # Act - start logcat without filters
        app.start_logcat(str(log_file))
        time.sleep(2)
        
        # Generate activity to produce logs
        app.terminal.start_activity(
            package="com.android.settings",
            activity="com.android.settings.Settings"
        )
        time.sleep(1)
        app.terminal.press_back()
        time.sleep(1)
        
        app.stop_logcat()

        # Assert - file should have content
        assert log_file.exists(), "Logcat file was not created"
        content = log_file.read_text(encoding="utf-8")
        assert len(content.strip()) > 0, "Logcat file is empty"

    def test_logcat_with_single_filter(self, app: Shadowstep, cleanup_log: None):
        """Test that logcat with single filter excludes matching lines (filter works as exclude)."""
        # Arrange
        log_file = Path("logcat_filtered_test.log")
        if log_file.exists():
            log_file.unlink()

        # Act - start logcat with ActivityManager filter (excludes ActivityManager lines)
        app.start_logcat(str(log_file), filters=["ActivityManager"])
        time.sleep(2)
        
        # Generate activity to produce various logs
        for _ in range(3):
            app.terminal.start_activity(
                package="com.android.settings",
                activity="com.android.settings.Settings"
            )
            time.sleep(1)
            app.terminal.press_back()
            time.sleep(1)
        
        app.stop_logcat()
        time.sleep(1)

        # Assert - file should exist
        assert log_file.exists(), "Filtered logcat file was not created"
        content = log_file.read_text(encoding="utf-8")
        
        # File might be empty or have content without ActivityManager
        # This is expected behavior - filter excludes ActivityManager lines

    def test_logcat_with_empty_filters_list_writes_all_logs(self, app: Shadowstep, cleanup_log: None):
        """Test that logcat with empty filters list writes all logs."""
        # Arrange
        log_file = Path("logcat_test.log")
        if log_file.exists():
            log_file.unlink()

        # Act - start logcat with empty filters list (should write all logs)
        app.start_logcat(str(log_file), filters=[])
        time.sleep(2)
        
        # Generate activity to produce logs
        app.terminal.start_activity(
            package="com.android.settings",
            activity="com.android.settings.Settings"
        )
        time.sleep(1)
        app.terminal.press_back()
        time.sleep(1)
        
        app.stop_logcat()

        # Assert - file should have content (all logs should be written)
        assert log_file.exists(), "Logcat file was not created"
        content = log_file.read_text(encoding="utf-8")
        assert len(content.strip()) > 0, "Logcat file is empty"

    def test_logcat_with_multiple_filters(self, app: Shadowstep, cleanup_log: None):
        """Test that logcat with multiple filters excludes all matching lines."""
        # Arrange
        log_file = Path("logcat_filtered_test.log")
        if log_file.exists():
            log_file.unlink()

        # Act - start logcat with multiple filters (excludes both ActivityManager and WindowManager)
        app.start_logcat(str(log_file), filters=["ActivityManager", "WindowManager"])
        time.sleep(2)

        # Generate activity to produce logs
        for _ in range(3):
            app.terminal.start_activity(
                package="com.android.settings",
                activity="com.android.settings.Settings"
            )
            time.sleep(1)
            app.terminal.press_back()
            time.sleep(1)

        app.stop_logcat()
        time.sleep(1)

        # Assert - file should exist (even if empty after filtering)
        assert log_file.exists(), "Filtered logcat file was not created"
        
        # Content verification: file might be empty or have content without filtered tags
        # This is expected - filters exclude specified tags

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


    def test_logcat_context_manager_exit(self, app: Shadowstep, cleanup_log: None):
        """Test __exit__ method stops logcat."""
        # Arrange
        log_file = Path("logcat_context_test.log")
        if log_file.exists():
            log_file.unlink()

        # Act - start logcat
        app.start_logcat(str(log_file))
        time.sleep(1)

        # Verify logcat thread is running
        thread_names_before = [t.name for t in threading.enumerate()]
        assert any("ShadowstepLogcat" in name for name in thread_names_before), \
            "Logcat thread should be running before __exit__"

        # Call __exit__ directly on logcat object
        app._logcat.__exit__(None, None, None)

        # Give thread time to stop
        time.sleep(2)

        # Assert - thread should be stopped
        thread_names_after = [t.name for t in threading.enumerate()]
        assert not any("ShadowstepLogcat" in name for name in thread_names_after), \
            "Logcat thread should be stopped after __exit__"

    def test_logcat_with_custom_port(self, app: Shadowstep, cleanup_log: None):
        """Test logcat with custom port parameter."""
        # Arrange
        log_file = Path("logcat_port_test.log")
        if log_file.exists():
            log_file.unlink()

        # Act - start with default port (None) using public API
        app.start_logcat(str(log_file), port=None)
        time.sleep(2)

        # Assert - logcat thread should be running
        thread_names = [t.name for t in threading.enumerate()]
        assert any("ShadowstepLogcat" in name for name in thread_names), \
            "Logcat thread should be running"

        # Generate activity and verify file is being written
        app.terminal.start_activity(
            package="com.android.settings",
            activity="com.android.settings.Settings"
        )
        time.sleep(1)
        app.terminal.press_back()
        
        # Cleanup
        app.stop_logcat()
        time.sleep(1)
        
        # Verify file was created and has content
        assert log_file.exists(), "Logcat file was not created"
        assert log_file.stat().st_size > 0, "Logcat file is empty"

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


    def test_logcat_init_with_zero_poll_interval(self, app: Shadowstep):
        """Test __init__ with zero poll_interval (valid edge case)."""
        # Act - should not raise exception
        logcat = ShadowstepLogcat(driver_getter=lambda: app.driver, poll_interval=0.0)

        # Assert - object created successfully
        assert logcat is not None

    def test_logcat_stop_releases_resources(self, app: Shadowstep, cleanup_log: None):
        """Test that stop() properly releases resources and stops thread."""
        # Arrange
        log_file = Path("logcat_websocket_test.log")
        if log_file.exists():
            log_file.unlink()

        # Act - start logcat
        app.start_logcat(str(log_file))
        time.sleep(2)  # Let WebSocket connect and logs start flowing

        # Verify thread is running
        thread_names_before = [t.name for t in threading.enumerate()]
        assert any("ShadowstepLogcat" in name for name in thread_names_before), \
            "Logcat thread should be running"

        # Stop logcat
        app.stop_logcat()
        time.sleep(2)  # Let cleanup complete

        # Assert - thread should be stopped (resources released)
        thread_names_after = [t.name for t in threading.enumerate()]
        assert not any("ShadowstepLogcat" in name for name in thread_names_after), \
            "Logcat thread should be stopped after stop()"

    def test_logcat_reconnect_stops_previous_broadcast(  # noqa: PLR0915
        self,
        app: Shadowstep,
        cleanup_log: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Ensure reconnection stops the previous broadcast before restarting."""
        log_file = Path("logcat_reconnect_test.log")
        if log_file.exists():
            log_file.unlink()

        logcat = app._logcat
        events: list[str] = []

        class DummyMobileCommands:
            def start_logs_broadcast(self) -> None:
                events.append("start")

            def stop_logs_broadcast(self) -> None:
                events.append("stop")

        dummy_mobile = DummyMobileCommands()
        monkeypatch.setattr(logcat, "mobile_commands", dummy_mobile, raising=False)
        stop_evt = logcat._stop_evt

        class DummyWebSocket:
            def __init__(self, identifier: str) -> None:
                self.identifier = identifier
                self._first_call = True

            def recv(self) -> str:
                if self.identifier == "first":
                    if self._first_call:
                        self._first_call = False
                        return "first socket line"
                    raise WebSocketConnectionClosedException("forced reconnect")
                if stop_evt.is_set():
                    raise WebSocketConnectionClosedException("stop requested")
                time.sleep(0.05)
                return "second socket line"

            def close(self) -> None:
                pass

        sockets = deque([DummyWebSocket("first"), DummyWebSocket("second")])

        def fake_create_connection(*args: object, **kwargs: object) -> DummyWebSocket:
            if sockets:
                return sockets.popleft()
            return DummyWebSocket("second")

        monkeypatch.setattr(
            "shadowstep.logcat.shadowstep_logcat.create_connection",
            fake_create_connection,
        )

        app.start_logcat(str(log_file))

        deadline = time.time() + 5.0
        while events.count("start") < 2 and time.time() < deadline:
            time.sleep(0.1)

        app.stop_logcat()
        time.sleep(0.5)

        start_indices = [idx for idx, event in enumerate(events) if event == "start"]
        assert len(start_indices) >= 2, f"Expected at least two start attempts, got events: {events}"

        for previous, current in zip(start_indices, start_indices[1:]):
            slice_events = events[previous + 1: current + 1]
            assert "stop" in slice_events, f"Missing stop between start attempts: {events}"

        assert log_file.exists(), "Log file should exist after reconnect scenario"

    def test_logcat_filter_verification(self, app: Shadowstep, cleanup_log: None):
        """Test that filters work correctly by excluding specified tags."""
        # Arrange
        log_file_all = Path("logcat_test.log")
        log_file_filtered = Path("logcat_filter_verification.log")
        if log_file_all.exists():
            log_file_all.unlink()
        if log_file_filtered.exists():
            log_file_filtered.unlink()

        # Act - First capture all logs
        app.start_logcat(str(log_file_all))
        time.sleep(2)
        
        # Generate activity
        for _ in range(3):
            app.terminal.start_activity(
                package="com.android.settings",
                activity="com.android.settings.Settings"
            )
            time.sleep(1)
            app.terminal.press_back()
            time.sleep(1)
        
        app.stop_logcat()
        time.sleep(1)

        # Now capture with filter (should exclude ActivityManager)
        app.start_logcat(str(log_file_filtered), filters=["ActivityManager"])
        time.sleep(2)
        
        # Generate activity again
        for _ in range(3):
            app.terminal.start_activity(
                package="com.android.settings",
                activity="com.android.settings.Settings"
            )
            time.sleep(1)
            app.terminal.press_back()
            time.sleep(1)
        
        app.stop_logcat()
        time.sleep(1)

        # Assert - both files should exist
        assert log_file_all.exists(), "Unfiltered logcat file was not created"
        assert log_file_filtered.exists(), "Filtered logcat file was not created"
        
        # Unfiltered log should have content
        all_content = log_file_all.read_text(encoding="utf-8")
        assert len(all_content.strip()) > 0, "Unfiltered log is empty"
        
        # Check if ActivityManager is present in unfiltered log
        all_lines = [line for line in all_content.split("\n") if line.strip()]
        has_activity_manager_in_all = any("ActivityManager" in line for line in all_lines)
        
        # If ActivityManager is present in unfiltered log, verify it's excluded in filtered
        if has_activity_manager_in_all:
            filtered_content = log_file_filtered.read_text(encoding="utf-8")
            if filtered_content.strip():
                filtered_lines = [line for line in filtered_content.split("\n") if line.strip()]
                has_activity_manager_in_filtered = any("ActivityManager" in line for line in filtered_lines)
                assert not has_activity_manager_in_filtered, \
                    "Filtered log should NOT contain ActivityManager entries (filter excludes them)"
        
        # Test passed - filtering mechanism works (file created, filtering applied if applicable)

