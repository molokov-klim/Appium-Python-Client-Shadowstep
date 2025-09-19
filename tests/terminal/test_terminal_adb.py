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

    def test_get_devices_no_devices(self):
        """Test device list retrieval with no devices."""
        # Arrange
        mock_output = b"List of devices attached\n"

        with patch("subprocess.check_output", return_value=mock_output):
            # Act
            result = Adb.get_devices()

            # Assert
            assert result == []  # noqa: S101

    def test_get_devices_subprocess_error(self):
        """Test device list retrieval with subprocess error."""
        # Arrange
        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = Adb.get_devices()

            # Assert
            assert result == []  # noqa: S101

    def test_get_device_model_success(self):
        """Test successful device model retrieval."""
        # Arrange
        udid = "emulator-5554"
        expected_model = "ro.product.model=Pixel 4"
        mock_output = expected_model.encode()

        with patch("subprocess.check_output", return_value=mock_output) as mock_subprocess:
            # Act
            result = self.adb.get_device_model(udid)

            # Assert
            assert result == expected_model  # noqa: S101
            mock_subprocess.assert_called_once_with(["adb", "-s", udid, "shell", "getprop", "ro.product.model"])

    def test_get_device_model_no_udid(self):
        """Test device model retrieval without UDID."""
        # Arrange
        expected_model = "ro.product.model=Pixel 4"
        mock_output = expected_model.encode()

        with patch("subprocess.check_output", return_value=mock_output) as mock_subprocess:
            # Act
            result = self.adb.get_device_model("")

            # Assert
            assert result == expected_model  # noqa: S101
            mock_subprocess.assert_called_once_with(["adb", "shell", "getprop", "ro.product.model"])

    def test_get_device_model_subprocess_error(self):
        """Test device model retrieval with subprocess error."""
        # Arrange
        udid = "invalid-device"

        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.get_device_model(udid)

            # Assert
            assert result == ""  # noqa: S101

    def test_push_success(self):
        """Test successful file push."""
        # Arrange
        source = "/local/file.txt"
        destination = "/remote/file.txt"
        udid = "emulator-5554"

        with patch("os.path.exists", return_value=True), patch("subprocess.run") as mock_subprocess:
            # Act
            result = Adb.push(source, destination, udid)

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "-s", udid, "push", source, destination], check=True
            )

    def test_push_no_udid(self):
        """Test file push without UDID."""
        # Arrange
        source = "/local/file.txt"
        destination = "/remote/file.txt"

        with patch("os.path.exists", return_value=True), patch("subprocess.run") as mock_subprocess:
            # Act
            result = Adb.push(source, destination, "")

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(
                ["adb", "push", source, destination], check=True
            )

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

    def test_is_app_installed_subprocess_error(self):
        """Test app installation check with subprocess error."""
        # Arrange
        package = "com.example.app"

        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.is_app_installed(package)

            # Assert
            assert result is False  # noqa: S101

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

    def test_uninstall_app_subprocess_error(self):
        """Test app uninstallation with subprocess error."""
        # Arrange
        package = "com.nonexistent.app"

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.uninstall_app(package)

            # Assert
            assert result is False  # noqa: S101

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

    def test_close_app_subprocess_error(self):
        """Test app closure with subprocess error."""
        # Arrange
        package = "com.nonexistent.app"

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.close_app(package)

            # Assert
            assert result is False  # noqa: S101

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

    def test_tap_subprocess_error(self):
        """Test tap action with subprocess error."""
        # Arrange
        x, y = 100, 200

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.tap(x, y)

            # Assert
            assert result is False  # noqa: S101

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

    def test_input_text_subprocess_error(self):
        """Test text input with subprocess error."""
        # Arrange
        text = "Hello World"

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.input_text(text)

            # Assert
            assert result is False  # noqa: S101

    def test_reboot_success(self):
        """Test successful device reboot."""
        with patch("subprocess.call") as mock_subprocess:
            # Act
            result = self.adb.reboot()

            # Assert
            assert result is True  # noqa: S101
            mock_subprocess.assert_called_once_with(["adb", "shell", "reboot"])

    def test_reboot_subprocess_error(self):
        """Test device reboot with subprocess error."""
        with patch("subprocess.call", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.reboot()

            # Assert
            assert result is False  # noqa: S101

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

    def test_get_screen_resolution_subprocess_error(self):
        """Test screen resolution retrieval with subprocess error."""
        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")):
            # Act
            result = self.adb.get_screen_resolution()

            # Assert
            assert result is None  # noqa: S101

    def test_get_screen_resolution_invalid_output(self):
        """Test screen resolution retrieval with invalid output."""
        # Arrange
        mock_output = "Invalid output format"

        with patch("subprocess.check_output", return_value=mock_output.encode()):
            # Act
            result = self.adb.get_screen_resolution()

            # Assert
            assert result is None  # noqa: S101

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

    def test_get_packages_empty_output(self):
        """Test package list retrieval with empty output."""
        # Arrange
        mock_output = ""

        with patch.object(self.adb, "execute", return_value=mock_output):
            # Act
            result = self.adb.get_packages_list()

            # Assert
            assert result == []  # noqa: S101

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

    def test_execute_subprocess_error(self):
        """Test command execution with subprocess error."""
        # Arrange
        command = "invalid command"

        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "adb")), \
             pytest.raises(subprocess.CalledProcessError):
            # Act & Assert
            Adb.execute(command)
