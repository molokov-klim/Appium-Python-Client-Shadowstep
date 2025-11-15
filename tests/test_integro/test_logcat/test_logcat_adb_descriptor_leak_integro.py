# ruff: noqa
# pyright: ignore
"""Integration test for checking ADB file descriptor leak during logcat operation.

This test verifies that the fix for descriptor leak (stop_logs_broadcast before start_logs_broadcast)
works correctly in real environment by monitoring the number of file descriptors
opened by the adb process during logcat operations.

Test approach:
1. Get PID of adb process
2. Measure initial number of file descriptors
3. Start/stop logcat multiple times
4. Verify that descriptor count doesn't grow unreasonably
5. Verify cleanup after final stop

Requirements:
- Running adb server
- Android device connected
- Shadowstep instance with active connection
"""

import subprocess
import time
from pathlib import Path

import pytest

from shadowstep.shadowstep import Shadowstep


def get_adb_pid() -> int | None:
    """Get PID of the adb process.
    
    Returns:
        PID of adb process or None if not found.
    """
    try:
        result = subprocess.run(
            ["pidof", "adb"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        pid_str = result.stdout.strip()
        if pid_str:
            # pidof can return multiple PIDs, take the first one
            return int(pid_str.split()[0])
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError):
        pass
    return None


def count_file_descriptors(pid: int) -> int | None:
    """Count number of open file descriptors for given process.
    
    Args:
        pid: Process ID to check.
        
    Returns:
        Number of file descriptors or None if unable to count.
    """
    try:
        fd_path = Path(f"/proc/{pid}/fd")
        if not fd_path.exists():
            return None
        # Count entries in /proc/<pid>/fd directory
        return len(list(fd_path.iterdir()))
    except (OSError, PermissionError):
        return None


class TestLogcatAdbDescriptorLeak:
    """Test suite for verifying ADB descriptor leak fix."""

    def test_logcat_no_descriptor_leak_on_multiple_cycles(
        self,
        app: Shadowstep,
        cleanup_log: None,
    ) -> None:
        """Verify that multiple logcat start/stop cycles don't leak file descriptors.
        
        This test:
        1. Gets adb process PID
        2. Measures initial descriptor count
        3. Performs multiple logcat start/stop cycles
        4. Verifies descriptor count doesn't grow significantly
        5. Verifies cleanup after final stop
        
        The test allows for some variance (up to 10 descriptors) to account for
        normal adb operations, but should catch significant leaks.
        """
        # Arrange - get adb PID
        adb_pid = get_adb_pid()
        if adb_pid is None:
            pytest.skip("ADB process not found - cannot test descriptor leak")
        
        # Measure initial descriptor count
        initial_fd_count = count_file_descriptors(adb_pid)
        if initial_fd_count is None:
            pytest.skip(f"Cannot access /proc/{adb_pid}/fd - insufficient permissions")
        
        print(f"\nInitial state: PID={adb_pid}, FD count={initial_fd_count}")
        
        # Prepare log file
        log_file = Path("logcat_descriptor_test.log")
        if log_file.exists():
            log_file.unlink()
        
        # Act - perform multiple logcat cycles
        num_cycles = 5
        fd_counts: list[int] = [initial_fd_count]
        
        for cycle in range(num_cycles):
            # Start logcat
            app.start_logcat(str(log_file))
            time.sleep(2)  # Let it stabilize
            
            # Generate some activity to produce logs
            app.terminal.start_activity(
                package="com.android.settings",
                activity="com.android.settings.Settings"
            )
            time.sleep(1)
            app.terminal.press_back()
            time.sleep(0.5)
            
            # Stop logcat
            app.stop_logcat()
            time.sleep(2)  # Let cleanup complete
            
            # Measure descriptor count after this cycle
            fd_count = count_file_descriptors(adb_pid)
            if fd_count is not None:
                fd_counts.append(fd_count)
                print(f"Cycle {cycle + 1}: FD count={fd_count} (delta={fd_count - initial_fd_count})")
        
        # Assert - verify no significant leak
        final_fd_count = fd_counts[-1]
        fd_growth = final_fd_count - initial_fd_count
        
        # Allow for some variance (up to 10 descriptors) due to normal adb operations
        # but catch significant leaks (the original issue showed growth of 100+ descriptors)
        max_allowed_growth = 10
        
        assert fd_growth <= max_allowed_growth, (
            f"File descriptor leak detected: "
            f"initial={initial_fd_count}, final={final_fd_count}, "
            f"growth={fd_growth} (max allowed: {max_allowed_growth}). "
            f"Full history: {fd_counts}"
        )
        
        print(f"\nTest passed: FD growth={fd_growth} (within limit of {max_allowed_growth})")
        print(f"FD count history: {fd_counts}")
        if log_file.exists():
            log_file.unlink()

    def test_logcat_descriptor_cleanup_after_long_session(
        self,
        app: Shadowstep,
        cleanup_log: None,
    ) -> None:
        """Verify that a long logcat session doesn't accumulate descriptors.
        
        This test runs a single long logcat session and verifies that
        descriptor count remains stable during operation and is properly
        cleaned up after stop.
        """
        # Arrange - get adb PID
        adb_pid = get_adb_pid()
        if adb_pid is None:
            pytest.skip("ADB process not found - cannot test descriptor leak")
        
        initial_fd_count = count_file_descriptors(adb_pid)
        if initial_fd_count is None:
            pytest.skip(f"Cannot access /proc/{adb_pid}/fd - insufficient permissions")
        
        print(f"\nInitial state: PID={adb_pid}, FD count={initial_fd_count}")
        
        # Prepare log file
        log_file = Path("logcat_long_session_test.log")
        if log_file.exists():
            log_file.unlink()
        
        # Act - start logcat for extended period
        app.start_logcat(str(log_file))
        time.sleep(2)
        
        # Measure descriptor count during operation
        fd_counts_during: list[int] = []
        
        for i in range(5):
            # Generate activity
            app.terminal.start_activity(
                package="com.android.settings",
                activity="com.android.settings.Settings"
            )
            time.sleep(1)
            app.terminal.press_back()
            time.sleep(1)
            
            # Measure descriptors
            fd_count = count_file_descriptors(adb_pid)
            if fd_count is not None:
                fd_counts_during.append(fd_count)
                print(f"Iteration {i + 1}: FD count={fd_count} (delta={fd_count - initial_fd_count})")
        
        # Stop logcat
        app.stop_logcat()
        time.sleep(2)
        
        final_fd_count = count_file_descriptors(adb_pid)
        if final_fd_count is not None:
            print(f"After stop: FD count={final_fd_count} (delta={final_fd_count - initial_fd_count})")
        
        # Assert - verify stable descriptor count during operation
        if fd_counts_during:
            max_during = max(fd_counts_during)
            min_during = min(fd_counts_during)
            variance = max_during - min_during
            
            # During stable operation, variance should be minimal
            assert variance <= 5, (
                f"Descriptor count unstable during operation: "
                f"min={min_during}, max={max_during}, variance={variance}"
            )
        
        # Verify cleanup after stop
        if final_fd_count is not None:
            fd_growth = final_fd_count - initial_fd_count
            assert fd_growth <= 10, (
                f"Descriptors not cleaned up properly: "
                f"initial={initial_fd_count}, final={final_fd_count}, "
                f"growth={fd_growth}"
            )
            
            print(f"\nTest passed: FD variance during operation={variance}, final growth={fd_growth}")
        if log_file.exists():
            log_file.unlink()


    def test_logcat_descriptor_count_with_reconnect_simulation(
        self,
        app: Shadowstep,
        cleanup_log: None,
    ) -> None:
        """Verify descriptor cleanup during rapid start/stop cycles (simulating reconnects).
        
        This test simulates the scenario where websocket reconnections happen
        frequently, which was the original cause of the descriptor leak.
        """
        # Arrange - get adb PID
        adb_pid = get_adb_pid()
        if adb_pid is None:
            pytest.skip("ADB process not found - cannot test descriptor leak")
        
        initial_fd_count = count_file_descriptors(adb_pid)
        if initial_fd_count is None:
            pytest.skip(f"Cannot access /proc/{adb_pid}/fd - insufficient permissions")
        
        print(f"\nInitial state: PID={adb_pid}, FD count={initial_fd_count}")
        
        # Prepare log file
        log_file = Path("logcat_reconnect_sim_test.log")
        if log_file.exists():
            log_file.unlink()
        
        # Act - perform rapid start/stop cycles (simulating reconnects)
        num_rapid_cycles = 10
        fd_samples: list[int] = [initial_fd_count]
        
        for cycle in range(num_rapid_cycles):
            # Start logcat
            app.start_logcat(str(log_file))
            time.sleep(0.5)  # Short duration
            
            # Stop immediately (simulating reconnect)
            app.stop_logcat()
            time.sleep(0.5)
            
            # Sample descriptor count
            if cycle % 2 == 0:  # Sample every other cycle to reduce overhead
                fd_count = count_file_descriptors(adb_pid)
                if fd_count is not None:
                    fd_samples.append(fd_count)
                    print(f"Cycle {cycle + 1}: FD count={fd_count} (delta={fd_count - initial_fd_count})")
        
        # Final measurement after all cycles
        time.sleep(2)  # Let final cleanup complete
        final_fd_count = count_file_descriptors(adb_pid)
        if final_fd_count is not None:
            fd_samples.append(final_fd_count)
            print(f"Final: FD count={final_fd_count} (delta={final_fd_count - initial_fd_count})")
        
        # Assert - verify no accumulation
        final_growth = final_fd_count - initial_fd_count if final_fd_count else 0
        
        # With the fix, even rapid cycles shouldn't cause significant growth
        assert final_growth <= 15, (
            f"Descriptor leak during rapid cycles: "
            f"initial={initial_fd_count}, final={final_fd_count}, "
            f"growth={final_growth}. Sample history: {fd_samples}"
        )
        
        print(f"\nTest passed: After {num_rapid_cycles} rapid cycles, FD growth={final_growth}")
        print(f"FD samples: {fd_samples}")
        if log_file.exists():
            log_file.unlink()
