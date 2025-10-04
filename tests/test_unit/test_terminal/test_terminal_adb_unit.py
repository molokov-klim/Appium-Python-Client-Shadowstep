# ruff: noqa
# pyright: ignore
"""
Tests for shadowstep.terminal.adb module.
"""

import subprocess
from unittest.mock import Mock, patch

import pytest

from shadowstep.terminal.adb import Adb


class TestAdb:
    """Test cases for Adb class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_base = Mock()
        self.mock_driver = Mock()
        self.mock_base.driver = self.mock_driver
        self.adb = Adb(self.mock_base)

    @pytest.mark.unit
    def test_init(self):
        """Test Adb initialization."""
        # Arrange
        mock_base = Mock()
        mock_driver = Mock()
        mock_base.driver = mock_driver

        # Act
        adb = Adb(mock_base)

        # Assert
        assert adb.base == mock_base  # noqa: S101
        assert adb.driver == mock_driver  # noqa: S101

    @pytest.mark.unit
    def test_get_devices_success(self):
        """Test successful device list retrieval."""
        # Arrange
        mock_output = b"List of devices attached\n192.168.1.100:5555\tdevice\nemulator-5554\tdevice\n"
        expected_devices = ["192.168.1.100:5555", "5554"]

        with patch("subprocess.check_output", return_value=mock_output) as mock_subprocess:
            # Act
            result = Adb.get_devices()

            # Assert
            assert result == expected_devices  # noqa: S101
            mock_subprocess.assert_called_once_with(["adb", "devices"])

    @pytest.mark.unit
    def test_get_devices_no_devices(self):
        """Test device list retrieval with no devices."""
        # Arrange
        mock_output = b"List of devices attached\n"

        with patch("subprocess.check_output", return_value=mock_output):
            # Act
            result = Adb.get_devices()

            # Assert
            assert result == []  # noqa: S101

    @pytest.mark.unit
    def test_get_devices_subprocess_error(self):
        """Test device list retrieval with subprocess error."""
        # Arrange
        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.get_devices()

            # Assert
            assert result == []  # noqa: S101

    @pytest.mark.unit
    def test_get_device_model_success(self):
        """Test successful device model retrieval."""
        # Arrange
        udid = "emulator-5554"
        expected_model = "ro.product.model=Nexus 6"
        mock_output = expected_model.encode()

        with patch("subprocess.check_output", return_value=mock_output) as mock_subprocess:
            # Act
            result = self.adb.get_device_model(udid)

            # Assert
            assert result == expected_model  # noqa: S101
            mock_subprocess.assert_called_once_with(["adb", "-s", udid, "shell", "getprop", "ro.product.model"])

    @pytest.mark.unit
    def test_get_device_model_no_udid(self):
        """Test device model retrieval without UDID."""
        # Arrange
        expected_model = "ro.product.model=Nexus 6"
        mock_output = expected_model.encode()

        with patch("subprocess.check_output", return_value=mock_output) as mock_subprocess:
            # Act
            result = self.adb.get_device_model("")

            # Assert
            assert result == expected_model  # noqa: S101
            mock_subprocess.assert_called_once_with(["adb", "shell", "getprop", "ro.product.model"])

    @pytest.mark.unit
    def test_get_device_model_subprocess_error(self):
        """Test device model retrieval with subprocess error."""
        # Arrange
        udid = "invalid-device"

        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.get_device_model(udid)

            # Assert
            assert result == ""  # noqa: S101

    @pytest.mark.unit
    def test_push_success(self):
        """Test successful file push."""
        # Arrange
        source = "/local/file.txt"
        destination = "/remote/file.txt"
        udid = "emulator-5554"

        with patch("pathlib.Path.exists", return_value=True), patch("subprocess.run") as mock_subprocess:
            # Act
            result = Adb.push(source, destination, udid)

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "-s", udid, "push", source, destination], check=True
            )

    @pytest.mark.unit
    def test_push_no_udid(self):
        """Test file push without UDID."""
        # Arrange
        source = "/local/file.txt"
        destination = "/remote/file.txt"

        with patch("pathlib.Path.exists", return_value=True), patch("subprocess.run") as mock_subprocess:
            # Act
            result = Adb.push(source, destination, "")

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "push", source, destination], check=True
            )

    @pytest.mark.unit
    def test_push_subprocess_error(self):
        """Test file push with subprocess error."""
        # Arrange
        source = "/local/file.txt"
        destination = "/remote/file.txt"
        udid = "emulator-5554"

        with patch("os.path.exists", return_value=True), patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.push(source, destination, udid)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_pull_success(self):
        """Test successful file pull."""
        # Arrange
        source = "/remote/file.txt"
        destination = "/local/file.txt"
        udid = "emulator-5554"

        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = self.adb.pull(source, destination, udid)

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "-s", udid, "pull", source, destination], check=True
            )

    @pytest.mark.unit
    def test_pull_no_udid(self):
        """Test file pull without UDID."""
        # Arrange
        source = "/remote/file.txt"
        destination = "/local/file.txt"

        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = self.adb.pull(source, destination, "")

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "pull", source, destination], check=True
            )

    @pytest.mark.unit
    def test_pull_subprocess_error(self):
        """Test file pull with subprocess error."""
        # Arrange
        source = "/remote/file.txt"
        destination = "/local/file.txt"
        udid = "emulator-5554"

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.pull(source, destination, udid)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_install_app_success(self):
        """Test successful app installation."""
        # Arrange
        source = "/path/to/app._apk"
        udid = "emulator-5554"

        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = Adb.install_app(source, udid)

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "-s", udid, "install", "-r", source], check=True
            )

    @pytest.mark.unit
    def test_install_app_no_udid(self):
        """Test app installation without UDID."""
        # Arrange
        source = "/path/to/app._apk"

        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = Adb.install_app(source, "")

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "install", source], check=True
            )

    @pytest.mark.unit
    def test_install_app_subprocess_error(self):
        """Test app installation with subprocess error."""
        # Arrange
        source = "/path/to/invalid._apk"
        udid = "emulator-5554"

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.install_app(source, udid)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_is_app_installed_true(self):
        """Test app installation check - app is installed."""
        # Arrange
        package = "com.example.app"
        mock_output = "package:com.example.app\npackage:com.other.app"

        with patch("subprocess.check_output", return_value=mock_output.encode()) as mock_subprocess:
            # Act
            result = self.adb.is_app_installed(package)

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with("adb shell pm list packages", shell=True)  # noqa: S604

    @pytest.mark.unit
    def test_is_app_installed_false(self):
        """Test app installation check - app is not installed."""
        # Arrange
        package = "com.nonexistent.app"
        mock_output = "package:com.example.app\npackage:com.other.app"

        with patch("subprocess.check_output", return_value=mock_output.encode()):
            # Act
            result = self.adb.is_app_installed(package)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_is_app_installed_subprocess_error(self):
        """Test app installation check with subprocess error."""
        # Arrange
        package = "com.example.app"

        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.is_app_installed(package)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_uninstall_app_success(self):
        """Test successful app uninstallation."""
        # Arrange
        package = "com.example.app"

        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = self.adb.uninstall_app(package)

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "uninstall", package], check=True
            )

    @pytest.mark.unit
    def test_uninstall_app_subprocess_error(self):
        """Test app uninstallation with subprocess error."""
        # Arrange
        package = "com.nonexistent.app"

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.uninstall_app(package)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_start_activity_success(self):
        """Test successful activity start."""
        # Arrange
        package = "com.example.app"
        activity = "com.example.app.MainActivity"

        with patch("subprocess.check_output") as mock_subprocess:
            # Act
            result = self.adb.start_activity(package, activity)

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "shell", "am", "start", "-n", f"{package}/{activity}"]
            )

    @pytest.mark.unit
    def test_start_activity_subprocess_error(self):
        """Test activity start with subprocess error."""
        # Arrange
        package = "com.nonexistent.app"
        activity = "com.nonexistent.app.MainActivity"

        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.start_activity(package, activity)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_close_app_success(self):
        """Test successful app closure."""
        # Arrange
        package = "com.example.app"

        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = self.adb.close_app(package)

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "shell", "am", "force-stop", package], check=True
            )

    @pytest.mark.unit
    def test_close_app_subprocess_error(self):
        """Test app closure with subprocess error."""
        # Arrange
        package = "com.nonexistent.app"

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.close_app(package)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_press_home_success(self):
        """Test successful home button press."""
        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = self.adb.press_home()

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "shell", "input", "keyevent", "KEYCODE_HOME"], check=True
            )

    @pytest.mark.unit
    def test_press_back_success(self):
        """Test successful back button press."""
        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = self.adb.press_back()

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "shell", "input", "keyevent", "KEYCODE_BACK"], check=True
            )

    @pytest.mark.unit
    def test_press_menu_success(self):
        """Test successful menu button press."""
        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = self.adb.press_menu()

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "shell", "input", "keyevent", "KEYCODE_MENU"], check=True
            )

    @pytest.mark.unit
    def test_tap_success(self):
        """Test successful tap action."""
        # Arrange
        x, y = 100, 200

        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = self.adb.tap(x, y)

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "shell", "input", "tap", "100", "200"], check=True
            )

    @pytest.mark.unit
    def test_tap_subprocess_error(self):
        """Test tap action with subprocess error."""
        # Arrange
        x, y = 100, 200

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.tap(x, y)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_swipe_success(self):
        """Test successful swipe action."""
        # Arrange
        x1, y1, x2, y2 = 100, 200, 300, 400
        duration = 1000

        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = self.adb.swipe(x1, y1, x2, y2, duration)

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "shell", "input", "swipe", "100", "200", "300", "400", "1000"], check=True
            )

    @pytest.mark.unit
    def test_swipe_subprocess_error(self):
        """Test swipe action with subprocess error."""
        # Arrange
        x1, y1, x2, y2 = 100, 200, 300, 400
        duration = 1000

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.swipe(x1, y1, x2, y2, duration)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_input_text_success(self):
        """Test successful text input."""
        # Arrange
        text = "Hello World"

        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = self.adb.input_text(text)

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "shell", "input", "text", "Hello World"], check=True
            )

    @pytest.mark.unit
    def test_input_text_subprocess_error(self):
        """Test text input with subprocess error."""
        # Arrange
        text = "Hello World"

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.input_text(text)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_reboot_success(self):
        """Test successful device reboot."""
        with patch("subprocess.call") as mock_subprocess:
            # Act
            result = self.adb.reboot()

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(["adb", "shell", "reboot"])

    @pytest.mark.unit
    def test_reboot_subprocess_error(self):
        """Test device reboot with subprocess error."""
        with patch("subprocess.call", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.reboot()

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_get_screen_resolution_success(self):
        """Test successful screen resolution retrieval."""
        # Arrange
        mock_output = "Physical size: 1080x1920"

        with patch("subprocess.check_output", return_value=mock_output.encode()) as mock_subprocess:
            # Act
            result = self.adb.get_screen_resolution()

            # Assert
            assert result == (1080, 1920)  # noqa: S101
            mock_subprocess.assert_called_once_with(["adb", "shell", "wm", "size"])

    @pytest.mark.unit
    def test_get_screen_resolution_subprocess_error(self):
        """Test screen resolution retrieval with subprocess error."""
        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.get_screen_resolution()

            # Assert
            assert result is None  # noqa: S101

    @pytest.mark.unit
    def test_get_screen_resolution_invalid_output(self):
        """Test screen resolution retrieval with invalid output."""
        # Arrange
        mock_output = "Invalid output format"

        with patch("subprocess.check_output", return_value=mock_output.encode()):
            # Act
            result = self.adb.get_screen_resolution()

            # Assert
            assert result is None  # noqa: S101

    @pytest.mark.unit
    def test_get_packages_success(self):
        """Test successful package list retrieval."""
        # Arrange
        mock_output = "package:com.example.app\npackage:com.other.app\npackage:com.third.app"

        with patch.object(self.adb, "execute", return_value=mock_output):
            # Act
            result = self.adb.get_packages_list()

            # Assert
            expected_packages = ["com.example.app", "com.other.app", "com.third.app"]
            assert result == expected_packages  # noqa: S101

    @pytest.mark.unit
    def test_get_packages_empty_output(self):
        """Test package list retrieval with empty output."""
        # Arrange
        mock_output = ""

        with patch.object(self.adb, "execute", return_value=mock_output):
            # Act
            result = self.adb.get_packages_list()

            # Assert
            assert result == []  # noqa: S101

    @pytest.mark.unit
    def test_execute_success(self):
        """Test successful command execution."""
        # Arrange
        command = "shell pm list packages"
        expected_output = "package:com.example.app"

        with patch("subprocess.check_output", return_value=expected_output.encode()) as mock_subprocess:
            # Act
            result = Adb.execute(command)

            # Assert
            assert result == expected_output  # noqa: S101
            mock_subprocess.assert_called_once_with(["adb", "shell", "pm", "list", "packages"])

    @pytest.mark.unit
    def test_execute_subprocess_error(self):
        """Test command execution with subprocess error."""
        # Arrange
        command = "invalid command"

        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")), \
             pytest.raises(subprocess.CalledProcessError):
            # Act & Assert
            Adb.execute(command)

    @pytest.mark.unit
    def test_get_devices_index_error(self):
        """Test get_devices with IndexError when no devices found."""
        # Arrange
        mock_output = b"List of devices attached\n"
        
        with patch("subprocess.check_output", return_value=mock_output):
            # Act
            result = Adb.get_devices()
            
            # Assert
            assert result == []  # noqa: S101

    @pytest.mark.unit
    def test_get_devices_empty_output(self):
        """Test get_devices with empty output."""
        # Arrange
        mock_output = b""
        
        with patch("subprocess.check_output", return_value=mock_output):
            # Act
            result = Adb.get_devices()
            
            # Assert
            assert result == []  # noqa: S101

    @pytest.mark.unit
    def test_push_file_not_exists(self):
        """Test push when source file does not exist."""
        # Arrange
        source = "/nonexistent/file.txt"
        destination = "/remote/path"
        udid = "test_device"
        
        with patch("os.path.exists", return_value=False):
            # Act
            result = Adb.push(source, destination, udid)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_push_subprocess_error(self):
        """Test push with subprocess error."""
        # Arrange
        source = "/local/file.txt"
        destination = "/remote/path"
        udid = "test_device"
        
        with patch("os.path.exists", return_value=True), \
             patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.push(source, destination, udid)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_pull_subprocess_error(self):
        """Test pull with subprocess error."""
        # Arrange
        source = "/remote/file.txt"
        destination = "/local/file.txt"
        udid = "test_device"
        
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.pull(source, destination, udid)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_get_current_activity_success(self):
        """Test get_current_activity with successful result."""
        # Arrange
        mock_output = "mCurrentFocus=Window{12345 u0 com.example.app/.MainActivity}"
        
        with patch("subprocess.check_output", return_value=mock_output.encode()), \
             patch("shadowstep.terminal.adb.grep_pattern", return_value=[mock_output]):
            # Act
            result = Adb.get_current_activity()
            
            # Assert
            assert result == ".MainActivity"  # noqa: S101

    @pytest.mark.unit
    def test_get_current_activity_no_match(self):
        """Test get_current_activity with no matching pattern."""
        # Arrange
        mock_output = "No matching lines found"
        
        with patch("subprocess.check_output", return_value=mock_output.encode()), \
             patch("shadowstep.terminal.adb.grep_pattern", return_value=[]):
            # Act
            result = Adb.get_current_activity()
            
            # Assert
            assert result == ""  # noqa: S101

    @pytest.mark.unit
    def test_get_current_activity_subprocess_error(self):
        """Test get_current_activity with subprocess error."""
        # Arrange
        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.get_current_activity()
            
            # Assert
            assert result == ""  # noqa: S101

    @pytest.mark.unit
    def test_get_current_package_success(self):
        """Test get_current_package with successful result."""
        # Arrange
        mock_output = "mCurrentFocus=Window{12345 u0 com.example.app/.MainActivity}"
        
        with patch("subprocess.check_output", return_value=mock_output.encode()), \
             patch("shadowstep.terminal.adb.grep_pattern", return_value=[mock_output]):
            # Act
            result = Adb.get_current_package()
            
            # Assert
            assert result == "com.example.app"  # noqa: S101

    @pytest.mark.unit
    def test_get_current_package_no_match(self):
        """Test get_current_package with no matching pattern."""
        # Arrange
        mock_output = "No matching lines found"
        
        with patch("subprocess.check_output", return_value=mock_output.encode()), \
             patch("shadowstep.terminal.adb.grep_pattern", return_value=[]):
            # Act
            result = Adb.get_current_package()
            
            # Assert
            assert result == ""  # noqa: S101

    @pytest.mark.unit
    def test_get_current_package_subprocess_error(self):
        """Test get_current_package with subprocess error."""
        # Arrange
        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.get_current_package()
            
            # Assert
            assert result == ""  # noqa: S101

    @pytest.mark.unit
    def test_install_app_success(self):
        """Test install_app with successful installation."""
        # Arrange
        source = "/path/to/app.apk"
        udid = "test_device"
        
        with patch("subprocess.run") as mock_run:
            # Act
            result = Adb.install_app(source, udid)
            
            # Assert
            assert result is True  # noqa: S101
            mock_run.assert_called_once_with(["adb", "-s", "test_device", "install", "-r", "/path/to/app.apk"], check=True)

    @pytest.mark.unit
    def test_install_app_subprocess_error(self):
        """Test install_app with subprocess error."""
        # Arrange
        source = "/path/to/app.apk"
        udid = "test_device"
        
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.install_app(source, udid)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_install_app_no_udid(self):
        """Test install_app without udid."""
        # Arrange
        source = "/path/to/app.apk"
        udid = None
        
        with patch("subprocess.run") as mock_run:
            # Act
            result = Adb.install_app(source, udid)
            
            # Assert
            assert result is True  # noqa: S101
            mock_run.assert_called_once_with(["adb", "install", "/path/to/app.apk"], check=True)

    @pytest.mark.unit
    def test_uninstall_app_success(self):
        """Test uninstall_app with successful uninstallation."""
        # Arrange
        package = "com.example.app"
        
        with patch("subprocess.run") as mock_run:
            # Act
            result = Adb.uninstall_app(package)
            
            # Assert
            assert result is True  # noqa: S101
            mock_run.assert_called_once_with(["adb", "uninstall", "com.example.app"], check=True)

    @pytest.mark.unit
    def test_uninstall_app_subprocess_error(self):
        """Test uninstall_app with subprocess error."""
        # Arrange
        package = "com.example.app"
        
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.uninstall_app(package)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_uninstall_app_no_udid(self):
        """Test uninstall_app without udid."""
        # Arrange
        package = "com.example.app"
        
        with patch("subprocess.run") as mock_run:
            # Act
            result = Adb.uninstall_app(package)
            
            # Assert
            assert result is True  # noqa: S101
            mock_run.assert_called_once_with(["adb", "uninstall", "com.example.app"], check=True)

    @pytest.mark.unit
    def test_input_keycode_num_success(self):
        """Test successful numpad key input."""
        # Arrange
        num = 5
        
        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = Adb.input_keycode_num_(num)
            
            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "shell", "input", "keyevent", "KEYCODE_NUMPAD_5"], check=True
            )

    @pytest.mark.unit
    def test_input_keycode_num_subprocess_error(self):
        """Test numpad key input with subprocess error."""
        # Arrange
        num = 5
        
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.input_keycode_num_(num)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_input_keycode_success(self):
        """Test successful keycode input."""
        # Arrange
        keycode = "KEYCODE_ENTER"
        
        with patch("subprocess.run") as mock_subprocess:
            # Act
            result = Adb.input_keycode(keycode)
            
            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "shell", "input", "keyevent", "KEYCODE_ENTER"], check=True
            )

    @pytest.mark.unit
    def test_input_keycode_subprocess_error(self):
        """Test keycode input with subprocess error."""
        # Arrange
        keycode = "KEYCODE_ENTER"
        
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.input_keycode(keycode)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_check_vpn_success(self):
        """Test successful VPN check."""
        # Arrange
        ip_address = "192.168.1.1"
        mock_output = subprocess.CompletedProcess(
            args=["adb", "shell", "netstat"],
            returncode=0,
            stdout="tcp 0 0 192.168.1.1:443 ESTABLISHED",
            stderr=""
        )
        
        with patch("subprocess.run", return_value=mock_output):
            # Act
            result = Adb.check_vpn(ip_address)
            
            # Assert
            assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_check_vpn_not_found(self):
        """Test VPN check when connection not found."""
        # Arrange
        ip_address = "192.168.1.1"
        mock_output = subprocess.CompletedProcess(
            args=["adb", "shell", "netstat"],
            returncode=0,
            stdout="tcp 0 0 10.0.0.1:443 ESTABLISHED",
            stderr=""
        )
        
        with patch("subprocess.run", return_value=mock_output):
            # Act
            result = Adb.check_vpn(ip_address)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_check_vpn_subprocess_error(self):
        """Test VPN check with subprocess error."""
        # Arrange
        ip_address = "192.168.1.1"
        
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.check_vpn(ip_address)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_stop_logcat_success(self):
        """Test successful logcat stop."""
        # Arrange
        with patch.object(Adb, "is_process_exist", return_value=True), \
             patch.object(Adb, "kill_all", return_value=True):
            # Act
            result = Adb.stop_logcat()
            
            # Assert
            assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_stop_logcat_no_process(self):
        """Test logcat stop when no process exists."""
        # Arrange
        with patch.object(Adb, "is_process_exist", return_value=False):
            # Act
            result = Adb.stop_logcat()
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_stop_logcat_kill_failed(self):
        """Test logcat stop when kill fails."""
        # Arrange
        with patch.object(Adb, "is_process_exist", return_value=True), \
             patch.object(Adb, "kill_all", return_value=False):
            # Act
            result = Adb.stop_logcat()
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_is_process_exist_success(self):
        """Test successful process existence check."""
        # Arrange
        process_name = "logcat"
        mock_output = "USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1234 567 0 0 0 logcat"
        
        with patch("subprocess.check_output", return_value=mock_output.encode()) as mock_check_output:
            # Act
            result = Adb.is_process_exist(process_name)
            
            # Assert
            assert result is True  # noqa: S101
            mock_check_output.assert_called_once_with(["adb", "shell", "ps"], shell=True)

    @pytest.mark.unit
    def test_is_process_exist_not_found(self):
        """Test process existence check when process not found."""
        # Arrange
        process_name = "nonexistent"
        mock_output = "USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1234 567 0 0 0 logcat"
        
        with patch("subprocess.check_output", return_value=mock_output.encode()):
            # Act
            result = Adb.is_process_exist(process_name)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_is_process_exist_subprocess_error(self):
        """Test process existence check with subprocess error."""
        # Arrange
        process_name = "logcat"
        
        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.is_process_exist(process_name)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_run_background_process_success(self):
        """Test successful background process execution."""
        # Arrange
        command = "test_command"
        process_name = "test_process"
        
        with patch("subprocess.Popen"), \
             patch("time.sleep"), \
             patch.object(Adb, "is_process_exist", return_value=True):
            # Act
            result = Adb.run_background_process(command, process_name)
            
            # Assert
            assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_run_background_process_no_check(self):
        """Test background process execution without process check."""
        # Arrange
        command = "test_command"
        
        with patch("subprocess.Popen"):
            # Act
            result = Adb.run_background_process(command)
            
            # Assert
            assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_run_background_process_check_failed(self):
        """Test background process execution when process check fails."""
        # Arrange
        command = "test_command"
        process_name = "test_process"
        
        with patch("subprocess.Popen"), \
             patch("time.sleep"), \
             patch.object(Adb, "is_process_exist", return_value=False):
            # Act
            result = Adb.run_background_process(command, process_name)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_run_background_process_subprocess_error(self):
        """Test background process execution with subprocess error."""
        # Arrange
        command = "test_command"
        
        with patch("subprocess.Popen", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.run_background_process(command)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_reload_adb_success(self):
        """Test successful ADB reload."""
        # Arrange
        with patch("subprocess.run") as mock_run, \
             patch("time.sleep"):
            # Act
            result = Adb.reload_adb()
            
            # Assert
            assert result is True  # noqa: S101
            assert mock_run.call_count == 2  # noqa: S101

    @pytest.mark.unit
    def test_reload_adb_kill_server_error(self):
        """Test ADB reload when kill-server fails."""
        # Arrange
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.reload_adb()
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_reload_adb_start_server_error(self):
        """Test ADB reload when start-server fails."""
        # Arrange
        with patch("subprocess.run") as mock_run, \
             patch("time.sleep"):
            # First call succeeds (kill-server), second call fails (start-server)
            mock_run.side_effect = [None, subprocess.CalledProcessError(1, "adb")]
            
            # Act
            result = Adb.reload_adb()
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_know_pid_success(self):
        """Test successful PID retrieval."""
        # Arrange
        process_name = "logcat"
        mock_output = "USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1234 567 0 0 0 logcat"
        
        with patch("subprocess.check_output", return_value=mock_output.encode()) as mock_check_output:
            # Act
            result = Adb.know_pid(process_name)
            
            # Assert
            assert result == 1234  # noqa: S101
            mock_check_output.assert_called_once_with(["adb", "shell", "ps"], shell=True)

    @pytest.mark.unit
    def test_know_pid_not_found(self):
        """Test PID retrieval when process not found."""
        # Arrange
        process_name = "nonexistent"
        mock_output = "USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1234 567 0 0 0 logcat"
        
        with patch("subprocess.check_output", return_value=mock_output.encode()):
            # Act
            result = Adb.know_pid(process_name)
            
            # Assert
            assert result is None  # noqa: S101

    @pytest.mark.unit
    def test_know_pid_subprocess_error(self):
        """Test PID retrieval with subprocess error."""
        # Arrange
        process_name = "logcat"
        
        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.know_pid(process_name)
            
            # Assert
            assert result is None  # noqa: S101

    @pytest.mark.unit
    def test_kill_by_pid_success(self):
        """Test successful process kill by PID."""
        # Arrange
        pid = 1234
        
        with patch("subprocess.call") as mock_call:
            # Act
            result = Adb.kill_by_pid(pid)
            
            # Assert
            assert result is True  # noqa: S101
            mock_call.assert_called_once_with(
                ["adb", "shell", "kill", "-s", "SIGINT", "1234"]
            )

    @pytest.mark.unit
    def test_kill_by_pid_subprocess_error(self):
        """Test process kill by PID with subprocess error."""
        # Arrange
        pid = 1234
        
        with patch("subprocess.call", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.kill_by_pid(pid)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_kill_by_name_success(self):
        """Test successful process kill by name."""
        # Arrange
        name = "logcat"
        
        with patch("subprocess.call") as mock_call:
            # Act
            result = Adb.kill_by_name(name)
            
            # Assert
            assert result is True  # noqa: S101
            mock_call.assert_called_once_with(
                ["adb", "shell", "pkill", "-l", "SIGINT", "logcat"]
            )

    @pytest.mark.unit
    def test_kill_by_name_subprocess_error(self):
        """Test process kill by name with subprocess error."""
        # Arrange
        name = "logcat"
        
        with patch("subprocess.call", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.kill_by_name(name)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_kill_all_success(self):
        """Test successful kill all processes."""
        # Arrange
        name = "logcat"
        
        with patch("subprocess.run") as mock_run:
            # Act
            result = Adb.kill_all(name)
            
            # Assert
            assert result is True  # noqa: S101
            mock_run.assert_called_once_with(
                ["adb", "shell", "pkill", "-f", "logcat"], check=True
            )

    @pytest.mark.unit
    def test_kill_all_subprocess_error(self):
        """Test kill all processes with subprocess error."""
        # Arrange
        name = "logcat"
        
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.kill_all(name)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_delete_files_from_internal_storage_success(self):
        """Test successful file deletion from internal storage."""
        # Arrange
        path = "/sdcard/test/"
        
        with patch("subprocess.run") as mock_run:
            # Act
            result = Adb.delete_files_from_internal_storage(path)
            
            # Assert
            assert result is True  # noqa: S101
            mock_run.assert_called_once_with(
                ["adb", "shell", "rm", "-rf", "/sdcard/test/*"], check=True
            )

    @pytest.mark.unit
    def test_delete_files_from_internal_storage_subprocess_error(self):
        """Test file deletion with subprocess error."""
        # Arrange
        path = "/sdcard/test/"
        
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.delete_files_from_internal_storage(path)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_pull_video_success(self):
        """Test successful video pull."""
        # Arrange
        source = "/sdcard/Movies/"
        destination = "/local/videos/"
        delete = True
        
        with patch("subprocess.run") as mock_run:
            # Act
            result = Adb.pull_video(source, destination, delete)
            
            # Assert
            assert result is True  # noqa: S101
            assert mock_run.call_count == 2  # noqa: S101

    @pytest.mark.unit
    def test_pull_video_empty_source(self):
        """Test video pull with empty source."""
        # Arrange
        source = ""
        destination = "/local/videos/"
        delete = True
        
        with patch("subprocess.run") as mock_run:
            # Act
            result = Adb.pull_video(source, destination, delete)
            
            # Assert
            assert result is True  # noqa: S101
            assert mock_run.call_count == 2  # noqa: S101

    @pytest.mark.unit
    def test_pull_video_no_delete(self):
        """Test video pull without deletion."""
        # Arrange
        source = "/sdcard/Movies/"
        destination = "/local/videos/"
        delete = False
        
        with patch("subprocess.run") as mock_run:
            # Act
            result = Adb.pull_video(source, destination, delete)
            
            # Assert
            assert result is True  # noqa: S101
            mock_run.assert_called_once_with(
                ["adb", "pull", "/sdcard/Movies//", "/local/videos//"], check=True
            )

    @pytest.mark.unit
    def test_pull_video_subprocess_error(self):
        """Test video pull with subprocess error."""
        # Arrange
        source = "/sdcard/Movies/"
        destination = "/local/videos/"
        
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.pull_video(source, destination)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_stop_video_success(self):
        """Test successful video stop."""
        # Arrange
        with patch("subprocess.call") as mock_call:
            # Act
            result = Adb.stop_video()
            
            # Assert
            assert result is True  # noqa: S101
            mock_call.assert_called_once_with(
                ["adb", "shell", "pkill", "-l", "SIGINT", "screenrecord"]
            )

    @pytest.mark.unit
    def test_stop_video_subprocess_error(self):
        """Test video stop with subprocess error."""
        # Arrange
        with patch("subprocess.call", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.stop_video()
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_record_video_success(self):
        """Test successful video recording start."""
        # Arrange
        path = "sdcard/Movies/"
        filename = "test_video.mp4"
        
        with patch("subprocess.Popen") as mock_popen:
            # Act
            result = Adb.record_video(path, filename)
            
            # Assert
            assert result is not None  # noqa: S101
            mock_popen.assert_called_once_with(
                ["adb", "shell", "screenrecord", "sdcard/Movies/test_video.mp4.mp4"]
            )

    @pytest.mark.unit
    def test_record_video_filename_already_mp4(self):
        """Test video recording with filename already ending in .mp4."""
        # Arrange
        path = "sdcard/Movies/"
        filename = "test_video.mp4"
        
        with patch("subprocess.Popen") as mock_popen:
            # Act
            result = Adb.record_video(path, filename)
            
            # Assert
            assert result is not None  # noqa: S101
            mock_popen.assert_called_once_with(
                ["adb", "shell", "screenrecord", "sdcard/Movies/test_video.mp4.mp4"]
            )

    @pytest.mark.unit
    def test_record_video_subprocess_error(self):
        """Test video recording with subprocess error."""
        # Arrange
        path = "sdcard/Movies/"
        filename = "test_video.mp4"
        
        with patch("subprocess.Popen", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.record_video(path, filename)
            
            # Assert
            assert result is None  # noqa: S101

    @pytest.mark.unit
    def test_start_record_video_success(self):
        """Test successful video recording start."""
        # Arrange
        path = "sdcard/Movies/"
        filename = "test_video.mp4"
        
        with patch("subprocess.Popen"):
            # Act
            result = Adb.start_record_video(path, filename)
            
            # Assert
            assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_start_record_video_filename_no_mp4(self):
        """Test video recording start with filename not ending in .mp4."""
        # Arrange
        path = "sdcard/Movies/"
        filename = "test_video"
        
        with patch("subprocess.Popen"):
            # Act
            result = Adb.start_record_video(path, filename)
            
            # Assert
            assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_start_record_video_subprocess_error(self):
        """Test video recording start with subprocess error."""
        # Arrange
        path = "sdcard/Movies/"
        filename = "test_video.mp4"
        
        with patch("subprocess.Popen", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.start_record_video(path, filename)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_reboot_app_success(self):
        """Test successful app reboot."""
        # Arrange
        package = "com.example.app"
        activity = "com.example.app.MainActivity"
        
        with patch.object(Adb, "close_app", return_value=True), \
             patch.object(Adb, "start_activity", return_value=True):
            # Act
            result = Adb.reboot_app(package, activity)
            
            # Assert
            assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_reboot_app_close_fails(self):
        """Test app reboot when close fails."""
        # Arrange
        package = "com.example.app"
        activity = "com.example.app.MainActivity"
        
        with patch.object(Adb, "close_app", return_value=False):
            # Act
            result = Adb.reboot_app(package, activity)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_reboot_app_start_fails(self):
        """Test app reboot when start fails."""
        # Arrange
        package = "com.example.app"
        activity = "com.example.app.MainActivity"
        
        with patch.object(Adb, "close_app", return_value=True), \
             patch.object(Adb, "start_activity", return_value=False):
            # Act
            result = Adb.reboot_app(package, activity)
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_push_success_return_true(self):
        """Test push method returns True on success."""
        # Arrange
        source = "/path/to/file.txt"
        destination = "/sdcard/file.txt"
        udid = "emulator-5554"
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = None
                
                # Act
                result = Adb.push(source, destination, udid)
                
                # Assert
                assert result is True  # noqa: S101
                mock_run.assert_called_once()

    @pytest.mark.unit
    def test_press_home_subprocess_error(self):
        """Test press_home with subprocess error."""
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.press_home()
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_press_back_subprocess_error(self):
        """Test press_back with subprocess error."""
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.press_back()
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_press_menu_subprocess_error(self):
        """Test press_menu with subprocess error."""
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.press_menu()
            
            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_pull_video_delete_source_subprocess_error(self):
        """Test pull_video with delete source subprocess error."""
        # Arrange
        source = "sdcard/Movies/test.mp4"
        destination = "./test.mp4"
        delete_source = True
        
        with patch("subprocess.run") as mock_run:
            # First call succeeds (pull), second call fails (delete)
            mock_run.side_effect = [None, subprocess.CalledProcessError(1, "adb")]
            
            # Act
            result = Adb.pull_video(source, destination, delete_source)
            
            # Assert
            assert result is False  # noqa: S101
