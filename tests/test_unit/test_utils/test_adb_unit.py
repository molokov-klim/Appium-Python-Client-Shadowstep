"""Tests for shadowstep.utils.adb module.

This module contains tests for the legacy Adb class and its ADB functionality.
Note: This is a legacy module marked as deprecated.
"""

import subprocess
from unittest.mock import Mock, patch

import pytest

from shadowstep.utils.adb import Adb


class TestAdbGetDevices:
    """Test cases for Adb.get_devices method."""

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_devices_success(self, mock_check_output: Mock) -> None:
        """Test successful device list retrieval."""
        mock_check_output.return_value = b"List of devices attached\n1234567890\tdevice\n"
        result = Adb.get_devices()
        assert result == ["1234567890"]  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_devices_multiple_devices(self, mock_check_output: Mock) -> None:
        """Test device list retrieval with multiple devices."""
        mock_check_output.return_value = b"List of devices attached\n1234567890\tdevice\n192.168.1.100:5555\tdevice\n"
        result = Adb.get_devices()
        assert result == ["1234567890", "192.168.1.100:5555"]  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_devices_no_devices(self, mock_check_output: Mock) -> None:
        """Test device list retrieval with no devices."""
        mock_check_output.return_value = b"List of devices attached\n"
        result = Adb.get_devices()
        assert result == []  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_devices_called_process_error(self, mock_check_output: Mock) -> None:
        """Test device list retrieval with subprocess error."""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "adb")
        # The method doesn't handle the exception properly, so it should raise it
        with pytest.raises(subprocess.CalledProcessError):
            Adb.get_devices()

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_devices_index_error(self, mock_check_output: Mock) -> None:
        """Test device list retrieval with index error."""
        mock_check_output.return_value = b"Invalid output format"
        result = Adb.get_devices()
        assert result == []  # noqa: S101


class TestAdbGetDeviceModel:
    """Test cases for Adb.get_device_model method."""

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_device_model_success(self, mock_check_output: Mock) -> None:
        """Test successful device model retrieval."""
        mock_check_output.return_value = b"Nexus 6\n"
        result = Adb.get_device_model("1234567890")
        assert result == "Nexus 6"  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_device_model_no_udid(self, mock_check_output: Mock) -> None:
        """Test device model retrieval without UDID."""
        mock_check_output.return_value = b"Nexus 6\n"
        result = Adb.get_device_model("")
        assert result == "Nexus 6"  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_device_model_called_process_error(self, mock_check_output: Mock) -> None:
        """Test device model retrieval with subprocess error."""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.get_device_model("1234567890")
        assert result == ""  # noqa: S101


class TestAdbPush:
    """Test cases for Adb.push method."""

    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    @pytest.mark.unit
    def test_push_success(self, mock_run: Mock, mock_exists: Mock) -> None:
        """Test successful file push."""
        mock_exists.return_value = True
        mock_run.return_value = None
        result = Adb.push("/local/file.txt", "/remote/file.txt", "1234567890")
        assert result is True  # noqa: S101

    @patch("pathlib.Path.exists")
    @pytest.mark.unit
    def test_push_file_not_exists(self, mock_exists: Mock) -> None:
        """Test push with non-existent source file."""
        mock_exists.return_value = False
        result = Adb.push("/nonexistent/file.txt", "/remote/file.txt", "1234567890")
        assert result is False  # noqa: S101

    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    @pytest.mark.unit
    def test_push_called_process_error(self, mock_run: Mock, mock_exists: Mock) -> None:
        """Test push with subprocess error."""
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.push("/local/file.txt", "/remote/file.txt", "1234567890")
        assert result is False  # noqa: S101


class TestAdbPull:
    """Test cases for Adb.pull method."""

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_pull_success(self, mock_run: Mock) -> None:
        """Test successful file pull."""
        mock_run.return_value = None
        result = Adb.pull("/remote/file.txt", "/local/file.txt", "1234567890")
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_pull_called_process_error(self, mock_run: Mock) -> None:
        """Test pull with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.pull("/remote/file.txt", "/local/file.txt", "1234567890")
        assert result is False  # noqa: S101


class TestAdbInstallApp:
    """Test cases for Adb.install_app method."""

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_install_app_success(self, mock_run: Mock) -> None:
        """Test successful app installation."""
        mock_run.return_value = None
        result = Adb.install_app("/path/to/app.apk", "1234567890")
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_install_app_called_process_error(self, mock_run: Mock) -> None:
        """Test app installation with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.install_app("/path/to/app.apk", "1234567890")
        assert result is False  # noqa: S101


class TestAdbIsAppInstalled:
    """Test cases for Adb.is_app_installed method."""

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_is_app_installed_true(self, mock_check_output: Mock) -> None:
        """Test app installation check when app is installed."""
        mock_check_output.return_value = b"package:com.example.app\npackage:com.other.app\n"
        result = Adb.is_app_installed("com.example.app")
        assert result is True  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_is_app_installed_false(self, mock_check_output: Mock) -> None:
        """Test app installation check when app is not installed."""
        mock_check_output.return_value = b"package:com.other.app\n"
        result = Adb.is_app_installed("com.example.app")
        assert result is False  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_is_app_installed_called_process_error(self, mock_check_output: Mock) -> None:
        """Test app installation check with subprocess error."""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.is_app_installed("com.example.app")
        assert result is False  # noqa: S101


class TestAdbUninstallApp:
    """Test cases for Adb.uninstall_app method."""

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_uninstall_app_success(self, mock_run: Mock) -> None:
        """Test successful app uninstallation."""
        mock_run.return_value = None
        result = Adb.uninstall_app("com.example.app")
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_uninstall_app_called_process_error(self, mock_run: Mock) -> None:
        """Test app uninstallation with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.uninstall_app("com.example.app")
        assert result is False  # noqa: S101


class TestAdbStartActivity:
    """Test cases for Adb.start_activity method."""

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_start_activity_success(self, mock_check_output: Mock) -> None:
        """Test successful activity start."""
        mock_check_output.return_value = b""
        result = Adb.start_activity("com.example.app", "MainActivity")
        assert result is True  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_start_activity_called_process_error(self, mock_check_output: Mock) -> None:
        """Test activity start with subprocess error."""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.start_activity("com.example.app", "MainActivity")
        assert result is False  # noqa: S101


class TestAdbGetCurrentActivity:
    """Test cases for Adb.get_current_activity method."""

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_current_activity_success(self, mock_check_output: Mock) -> None:
        """Test successful current activity retrieval."""
        mock_check_output.return_value = b"mCurrentFocus=Window{12345 u0 com.example.app/.MainActivity}\n"
        result = Adb.get_current_activity()
        assert result == ".MainActivity"  # noqa: S101 - the regex extracts the part after the last /

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_current_activity_no_match(self, mock_check_output: Mock) -> None:
        """Test current activity retrieval with no matching activity."""
        mock_check_output.return_value = b"No activity information\n"
        result = Adb.get_current_activity()
        assert result == ""  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_current_activity_called_process_error(self, mock_check_output: Mock) -> None:
        """Test current activity retrieval with subprocess error."""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.get_current_activity()
        assert result == ""  # noqa: S101


class TestAdbGetCurrentPackage:
    """Test cases for Adb.get_current_package method."""

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_current_package_success(self, mock_check_output: Mock) -> None:
        """Test successful current package retrieval."""
        mock_check_output.return_value = b"mCurrentFocus=Window{12345 u0 com.example.app/.MainActivity}\n"
        result = Adb.get_current_package()
        assert result == "com.example.app"  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_current_package_no_match(self, mock_check_output: Mock) -> None:
        """Test current package retrieval with no matching package."""
        mock_check_output.return_value = b"No package information\n"
        result = Adb.get_current_package()
        assert result == ""  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_current_package_called_process_error(self, mock_check_output: Mock) -> None:
        """Test current package retrieval with subprocess error."""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.get_current_package()
        assert result == ""  # noqa: S101


class TestAdbCloseApp:
    """Test cases for Adb.close_app method."""

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_close_app_success(self, mock_run: Mock) -> None:
        """Test successful app close."""
        mock_run.return_value = None
        result = Adb.close_app("com.example.app")
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_close_app_called_process_error(self, mock_run: Mock) -> None:
        """Test app close with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.close_app("com.example.app")
        assert result is False  # noqa: S101


class TestAdbRebootApp:
    """Test cases for Adb.reboot_app method."""

    @patch.object(Adb, "close_app")
    @patch.object(Adb, "start_activity")
    @pytest.mark.unit
    def test_reboot_app_success(self, mock_start_activity: Mock, mock_close_app: Mock) -> None:
        """Test successful app reboot."""
        mock_close_app.return_value = True
        mock_start_activity.return_value = True
        result = Adb.reboot_app("com.example.app", "MainActivity")
        assert result is True  # noqa: S101

    @patch.object(Adb, "close_app")
    @pytest.mark.unit
    def test_reboot_app_close_fails(self, mock_close_app: Mock) -> None:
        """Test app reboot when close fails."""
        mock_close_app.return_value = False
        result = Adb.reboot_app("com.example.app", "MainActivity")
        assert result is False  # noqa: S101

    @patch.object(Adb, "close_app")
    @patch.object(Adb, "start_activity")
    @pytest.mark.unit
    def test_reboot_app_start_fails(self, mock_start_activity: Mock, mock_close_app: Mock) -> None:
        """Test app reboot when start activity fails."""
        mock_close_app.return_value = True
        mock_start_activity.return_value = False
        result = Adb.reboot_app("com.example.app", "MainActivity")
        assert result is False  # noqa: S101


class TestAdbInputMethods:
    """Test cases for ADB input methods."""

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_press_home_success(self, mock_run: Mock) -> None:
        """Test successful home button press."""
        mock_run.return_value = None
        result = Adb.press_home()
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_press_back_success(self, mock_run: Mock) -> None:
        """Test successful back button press."""
        mock_run.return_value = None
        result = Adb.press_back()
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_press_menu_success(self, mock_run: Mock) -> None:
        """Test successful menu button press."""
        mock_run.return_value = None
        result = Adb.press_menu()
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_input_keycode_num_success(self, mock_run: Mock) -> None:
        """Test successful number key input."""
        mock_run.return_value = None
        result = Adb.input_keycode_num_(5)
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_input_keycode_success(self, mock_run: Mock) -> None:
        """Test successful keycode input."""
        mock_run.return_value = None
        result = Adb.input_keycode("KEYCODE_ENTER")
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_input_text_success(self, mock_run: Mock) -> None:
        """Test successful text input."""
        mock_run.return_value = None
        result = Adb.input_text("Hello World")
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_tap_success(self, mock_run: Mock) -> None:
        """Test successful tap."""
        mock_run.return_value = None
        result = Adb.tap(100, 200)
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_swipe_success(self, mock_run: Mock) -> None:
        """Test successful swipe."""
        mock_run.return_value = None
        result = Adb.swipe(100, 200, 300, 400, 500)
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_press_home_error(self, mock_run: Mock) -> None:
        """Test home button press with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.press_home()
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_press_back_error(self, mock_run: Mock) -> None:
        """Test back button press with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.press_back()
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_press_menu_error(self, mock_run: Mock) -> None:
        """Test menu button press with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.press_menu()
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_input_keycode_num_error(self, mock_run: Mock) -> None:
        """Test number key input with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.input_keycode_num_(5)
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_input_keycode_error(self, mock_run: Mock) -> None:
        """Test keycode input with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.input_keycode("KEYCODE_ENTER")
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_input_text_error(self, mock_run: Mock) -> None:
        """Test text input with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.input_text("Hello World")
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_tap_error(self, mock_run: Mock) -> None:
        """Test tap with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.tap(100, 200)
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_swipe_error(self, mock_run: Mock) -> None:
        """Test swipe with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.swipe(100, 200, 300, 400, 500)
        assert result is False  # noqa: S101


class TestAdbProcessMethods:
    """Test cases for ADB process management methods."""

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_is_process_exist_true(self, mock_check_output: Mock) -> None:
        """Test process existence check when process exists."""
        # Mock the return value as bytes since the method calls .decode().strip()
        # The process name should be in column 8 (index 8) after splitting by spaces
        # Need at least 9 columns (MIN_PS_COLUMNS_COUNT = 9)
        mock_check_output.return_value = b"USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1000 500 0x0 0x0 0x0 test_process\n"
        result = Adb.is_process_exist("test_process")
        assert result is True  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_is_process_exist_false(self, mock_check_output: Mock) -> None:
        """Test process existence check when process doesn't exist."""
        mock_check_output.return_value = b"USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1000 500 0x0 0x0 0x0 other_process\n"
        result = Adb.is_process_exist("test_process")
        assert result is False  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_is_process_exist_error(self, mock_check_output: Mock) -> None:
        """Test process existence check with subprocess error."""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.is_process_exist("test_process")
        assert result is False  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_know_pid_success(self, mock_check_output: Mock) -> None:
        """Test successful PID retrieval."""
        mock_check_output.return_value = b"USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1000 500 0x0 0x0 0x0 test_process\n"
        result = Adb.know_pid("test_process")
        assert result == 1234  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_know_pid_not_found(self, mock_check_output: Mock) -> None:
        """Test PID retrieval when process not found."""
        mock_check_output.return_value = b"USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1000 500 0x0 0x0 0x0 other_process\n"
        result = Adb.know_pid("test_process")
        assert result is None  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_know_pid_error(self, mock_check_output: Mock) -> None:
        """Test PID retrieval with subprocess error."""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.know_pid("test_process")
        assert result is None  # noqa: S101

    @patch("subprocess.call")
    @pytest.mark.unit
    def test_kill_by_pid_success(self, mock_call: Mock) -> None:
        """Test successful process kill by PID."""
        mock_call.return_value = 0
        result = Adb.kill_by_pid(1234)
        assert result is True  # noqa: S101

    @patch("subprocess.call")
    @pytest.mark.unit
    def test_kill_by_pid_error(self, mock_call: Mock) -> None:
        """Test process kill by PID with subprocess error."""
        mock_call.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.kill_by_pid(1234)
        assert result is False  # noqa: S101

    @patch("subprocess.call")
    @pytest.mark.unit
    def test_kill_by_name_success(self, mock_call: Mock) -> None:
        """Test successful process kill by name."""
        mock_call.return_value = 0
        result = Adb.kill_by_name("test_process")
        assert result is True  # noqa: S101

    @patch("subprocess.call")
    @pytest.mark.unit
    def test_kill_by_name_error(self, mock_call: Mock) -> None:
        """Test process kill by name with subprocess error."""
        mock_call.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.kill_by_name("test_process")
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_kill_all_success(self, mock_run: Mock) -> None:
        """Test successful kill all processes."""
        mock_run.return_value = None
        result = Adb.kill_all("test_process")
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_kill_all_error(self, mock_run: Mock) -> None:
        """Test kill all processes with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.kill_all("test_process")
        assert result is False  # noqa: S101


class TestAdbUtilityMethods:
    """Test cases for ADB utility methods."""

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_reload_adb_success(self, mock_run: Mock) -> None:
        """Test successful ADB reload."""
        mock_run.return_value = None
        with patch("time.sleep"):
            result = Adb.reload_adb()
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_reload_adb_kill_server_error(self, mock_run: Mock) -> None:
        """Test ADB reload with kill-server error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        with patch("time.sleep"):
            result = Adb.reload_adb()
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_reload_adb_start_server_error(self, mock_run: Mock) -> None:
        """Test ADB reload with start-server error."""
        # First call (kill-server) succeeds, second call (start-server) fails
        mock_run.side_effect = [None, subprocess.CalledProcessError(1, "adb")]
        with patch("time.sleep"):
            result = Adb.reload_adb()
        assert result is False  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_screen_resolution_success(self, mock_check_output: Mock) -> None:
        """Test successful screen resolution retrieval."""
        mock_check_output.return_value = b"Physical size: 1080x1920\n"
        result = Adb.get_screen_resolution()
        assert result == (1080, 1920)  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_screen_resolution_invalid_output(self, mock_check_output: Mock) -> None:
        """Test screen resolution retrieval with invalid output."""
        mock_check_output.return_value = b"Invalid output\n"
        result = Adb.get_screen_resolution()
        assert result is None  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_screen_resolution_value_error(self, mock_check_output: Mock) -> None:
        """Test screen resolution retrieval with value that cannot be converted to int."""
        mock_check_output.return_value = b"Physical size: abcxdef\n"
        result = Adb.get_screen_resolution()
        assert result is None  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_get_screen_resolution_called_process_error(self, mock_check_output: Mock) -> None:
        """Test screen resolution retrieval with subprocess error."""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.get_screen_resolution()
        assert result is None  # noqa: S101

    @patch("subprocess.check_output")
    @pytest.mark.unit
    def test_execute_success(self, mock_check_output: Mock) -> None:
        """Test successful command execution."""
        mock_check_output.return_value = b"Command output\n"
        result = Adb.execute("shell ls")
        assert result == "Command output\n"  # noqa: S101


class TestAdbVideoMethods:
    """Test cases for ADB video recording methods."""

    @patch("subprocess.Popen")
    @pytest.mark.unit
    def test_record_video_success(self, mock_popen: Mock) -> None:
        """Test successful video recording start."""
        mock_process = Mock()
        mock_popen.return_value = mock_process
        result = Adb.record_video("sdcard/Movies/", "test.mp4")
        assert result == mock_process  # noqa: S101

    @patch("subprocess.Popen")
    @pytest.mark.unit
    def test_record_video_error(self, mock_popen: Mock) -> None:
        """Test video recording start with subprocess error."""
        mock_popen.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.record_video("sdcard/Movies/", "test.mp4")
        assert result is None  # noqa: S101

    @patch("subprocess.Popen")
    @pytest.mark.unit
    def test_start_record_video_success(self, mock_popen: Mock) -> None:
        """Test successful video recording start (boolean version)."""
        mock_popen.return_value = Mock()
        result = Adb.start_record_video("sdcard/Movies/", "test.mp4")
        assert result is True  # noqa: S101

    @patch("subprocess.Popen")
    @pytest.mark.unit
    def test_start_record_video_error(self, mock_popen: Mock) -> None:
        """Test video recording start with subprocess error (boolean version)."""
        mock_popen.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.start_record_video("sdcard/Movies/", "test.mp4")
        assert result is False  # noqa: S101

    @patch("subprocess.Popen")
    @pytest.mark.unit
    def test_start_record_video_without_mp4_extension(self, mock_popen: Mock) -> None:
        """Test video recording start with filename without .mp4 extension."""
        mock_popen.return_value = Mock()
        result = Adb.start_record_video("sdcard/Movies/", "test")
        assert result is True  # noqa: S101
        # Verify that .mp4 was added to the filename
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert call_args[-1] == "sdcard/Movies/test.mp4"  # noqa: S101

    @patch("subprocess.call")
    @pytest.mark.unit
    def test_stop_video_success(self, mock_call: Mock) -> None:
        """Test successful video recording stop."""
        mock_call.return_value = 0
        result = Adb.stop_video()
        assert result is True  # noqa: S101

    @patch("subprocess.call")
    @pytest.mark.unit
    def test_stop_video_error(self, mock_call: Mock) -> None:
        """Test video recording stop with subprocess error."""
        mock_call.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.stop_video()
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_pull_video_success(self, mock_run: Mock) -> None:
        """Test successful video pull."""
        mock_run.return_value = None
        result = Adb.pull_video("sdcard/Movies/", "/local/path/", True)
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_pull_video_pull_error(self, mock_run: Mock) -> None:
        """Test video pull with pull command error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.pull_video("sdcard/Movies/", "/local/path/", True)
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_pull_video_delete_error(self, mock_run: Mock) -> None:
        """Test video pull with delete command error."""
        # First call (pull) succeeds, second call (delete) fails
        mock_run.side_effect = [None, subprocess.CalledProcessError(1, "adb")]
        result = Adb.pull_video("sdcard/Movies/", "/local/path/", True)
        assert result is False  # noqa: S101


class TestAdbFileMethods:
    """Test cases for ADB file management methods."""

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_delete_files_from_internal_storage_success(self, mock_run: Mock) -> None:
        """Test successful file deletion from internal storage."""
        mock_run.return_value = None
        result = Adb.delete_files_from_internal_storage("/sdcard/test/")
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_delete_files_from_internal_storage_error(self, mock_run: Mock) -> None:
        """Test file deletion from internal storage with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.delete_files_from_internal_storage("/sdcard/test/")
        assert result is False  # noqa: S101

    @patch("subprocess.call")
    @pytest.mark.unit
    def test_reboot_success(self, mock_call: Mock) -> None:
        """Test successful device reboot."""
        mock_call.return_value = 0
        result = Adb.reboot()
        assert result is True  # noqa: S101

    @patch("subprocess.call")
    @pytest.mark.unit
    def test_reboot_error(self, mock_call: Mock) -> None:
        """Test device reboot with subprocess error."""
        mock_call.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.reboot()
        assert result is False  # noqa: S101


class TestAdbNetworkMethods:
    """Test cases for ADB network methods."""

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_check_vpn_true(self, mock_run: Mock) -> None:
        """Test VPN check when VPN is connected."""
        mock_output = Mock()
        mock_output.stdout = "tcp 0 0 192.168.1.100:443 ESTABLISHED\n"
        mock_run.return_value = mock_output
        result = Adb.check_vpn("192.168.1.100")
        assert result is True  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_check_vpn_false(self, mock_run: Mock) -> None:
        """Test VPN check when VPN is not connected."""
        mock_output = Mock()
        mock_output.stdout = "tcp 0 0 10.0.0.1:443 ESTABLISHED\n"
        mock_run.return_value = mock_output
        result = Adb.check_vpn("192.168.1.100")
        assert result is False  # noqa: S101

    @patch("subprocess.run")
    @pytest.mark.unit
    def test_check_vpn_error(self, mock_run: Mock) -> None:
        """Test VPN check with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.check_vpn("192.168.1.100")
        assert result is False  # noqa: S101


class TestAdbLogcatMethods:
    """Test cases for ADB logcat methods."""

    @patch.object(Adb, "is_process_exist")
    @patch.object(Adb, "kill_all")
    @pytest.mark.unit
    def test_stop_logcat_success(self, mock_kill_all: Mock, mock_is_process_exist: Mock) -> None:
        """Test successful logcat stop."""
        mock_is_process_exist.return_value = True
        mock_kill_all.return_value = True
        result = Adb.stop_logcat()
        assert result is True  # noqa: S101

    @patch.object(Adb, "is_process_exist")
    @pytest.mark.unit
    def test_stop_logcat_no_process(self, mock_is_process_exist: Mock) -> None:
        """Test logcat stop when no process exists."""
        mock_is_process_exist.return_value = False
        result = Adb.stop_logcat()
        assert result is False  # noqa: S101


class TestAdbBackgroundProcess:
    """Test cases for ADB background process methods."""

    @patch("subprocess.Popen")
    @patch.object(Adb, "is_process_exist")
    @patch("time.sleep")
    @pytest.mark.unit
    def test_run_background_process_success(self, mock_sleep: Mock, mock_is_process_exist: Mock, mock_popen: Mock) -> None:
        """Test successful background process execution."""
        mock_popen.return_value = Mock()
        mock_is_process_exist.return_value = True
        result = Adb.run_background_process("test_command", "test_process")
        assert result is True  # noqa: S101

    @patch("subprocess.Popen")
    @patch.object(Adb, "is_process_exist")
    @patch("time.sleep")
    @pytest.mark.unit
    def test_run_background_process_not_exist(self, mock_sleep: Mock, mock_is_process_exist: Mock, mock_popen: Mock) -> None:
        """Test background process execution when process doesn't exist."""
        mock_popen.return_value = Mock()
        mock_is_process_exist.return_value = False
        result = Adb.run_background_process("test_command", "test_process")
        assert result is False  # noqa: S101

    @patch("subprocess.Popen")
    @pytest.mark.unit
    def test_run_background_process_error(self, mock_popen: Mock) -> None:
        """Test background process execution with subprocess error."""
        mock_popen.side_effect = subprocess.CalledProcessError(1, "adb")
        result = Adb.run_background_process("test_command", "test_process")
        assert result is False  # noqa: S101


class TestAdbPackagesList:
    """Test cases for ADB packages list method."""

    @pytest.mark.unit
    def test_get_packages_list_success(self) -> None:
        """Test successful packages list retrieval."""
        adb_instance = Adb()
        with patch.object(adb_instance, "execute", return_value="package:com.example.app\npackage:com.other.app\n"):
            result = adb_instance.get_packages_list()
            assert result == ["com.example.app", "com.other.app"]  # noqa: S101

    @pytest.mark.unit
    def test_get_packages_list_empty(self) -> None:
        """Test packages list retrieval with empty result."""
        adb_instance = Adb()
        with patch.object(adb_instance, "execute", return_value=""):
            result = adb_instance.get_packages_list()
            assert result == []  # noqa: S101
