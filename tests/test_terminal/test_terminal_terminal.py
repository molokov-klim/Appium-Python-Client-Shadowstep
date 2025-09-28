"""
Tests for shadowstep.terminal.terminal module.
"""

import base64
from unittest.mock import Mock, patch

import pytest
from selenium.common import InvalidSessionIdException, NoSuchDriverException

from shadowstep.terminal.terminal import NotProvideCredentialsError, Terminal


class TestNotProvideCredentialsError:
    """Test cases for NotProvideCredentialsError exception."""

    def test_default_message(self):
        """Test exception with default message."""
        # Act
        exception = NotProvideCredentialsError()

        # Assert
        expected_message = ("Not provided credentials for ssh connection "
                          "in connect() method (ssh_username, ssh_password)")
        assert str(exception) == expected_message  # noqa: S101
        assert exception.message == expected_message  # noqa: S101

    def test_custom_message(self):
        """Test exception with custom message."""
        # Arrange
        custom_message = "Custom error message"

        # Act
        exception = NotProvideCredentialsError(custom_message)

        # Assert
        assert str(exception) == custom_message  # noqa: S101
        assert exception.message == custom_message  # noqa: S101


class TestTerminal:
    """Test cases for Terminal class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_base = Mock()
        self.mock_driver = Mock()
        self.mock_transport = Mock()
        self.mock_ssh = Mock()
        self.mock_scp = Mock()

        self.mock_base.driver = self.mock_driver
        self.mock_base.transport = self.mock_transport
        self.mock_transport.ssh = self.mock_ssh
        self.mock_transport.scp = self.mock_scp

        self.terminal = Terminal(self.mock_base)

    def test_init(self):
        """Test Terminal initialization."""
        # Arrange
        mock_base = Mock()
        mock_driver = Mock()
        mock_transport = Mock()

        mock_base.driver = mock_driver
        mock_base.transport = mock_transport

        # Act
        terminal = Terminal(mock_base)

        # Assert
        assert terminal.base == mock_base  # noqa: S101
        assert terminal.driver == mock_driver  # noqa: S101
        assert terminal.transport == mock_transport  # noqa: S101

    def test_del(self):
        """Test Terminal destructor."""
        # Act
        del self.terminal

        # Assert
        self.mock_ssh.close.assert_called_once()

    def test_adb_shell_success(self):
        """Test successful adb shell command execution."""
        # Arrange
        command = "pm list packages"
        args = ""
        expected_result = "package:com.example.app"

        self.mock_driver.execute_script.return_value = expected_result

        # Act
        result = self.terminal.adb_shell(command, args)

        # Assert
        assert result == expected_result  # noqa: S101
        self.mock_driver.execute_script.assert_called_once_with(
            "mobile: shell", {"command": command, "args": [args]}
        )

    def test_adb_shell_with_args(self):
        """Test adb shell command execution with arguments."""
        # Arrange
        command = "pm"
        args = "list packages"
        expected_result = "package:com.example.app"

        self.mock_driver.execute_script.return_value = expected_result

        # Act
        result = self.terminal.adb_shell(command, args)

        # Assert
        assert result == expected_result  # noqa: S101
        self.mock_driver.execute_script.assert_called_once_with(
            "mobile: shell", {"command": command, "args": [args]}
        )

    def test_adb_shell_no_such_driver_exception(self):
        """Test adb shell with NoSuchDriverException."""
        # Arrange
        command = "pm list packages"
        args = ""

        self.mock_driver.execute_script.side_effect = NoSuchDriverException("Driver not found")
        self.mock_base.reconnect = Mock()

        # Act
        result = self.terminal.adb_shell(command, args, tries=1)

        # Assert
        assert result is None  # noqa: S101
        self.mock_base.reconnect.assert_called_once()

    def test_adb_shell_invalid_session_exception(self):
        """Test adb shell with InvalidSessionIdException."""
        # Arrange
        command = "pm list packages"
        args = ""

        self.mock_driver.execute_script.side_effect = InvalidSessionIdException("Invalid session")
        self.mock_base.reconnect = Mock()

        # Act
        result = self.terminal.adb_shell(command, args, tries=1)

        # Assert
        assert result is None  # noqa: S101
        self.mock_base.reconnect.assert_called_once()

    def test_adb_shell_key_error(self):
        """Test adb shell with KeyError."""
        # Arrange
        command = "pm list packages"
        args = ""

        self.mock_driver.execute_script.side_effect = KeyError("Key not found")

        # Act
        result = self.terminal.adb_shell(command, args, tries=1)

        # Assert
        assert result is None  # noqa: S101

    def test_adb_shell_multiple_tries(self):
        """Test adb shell with multiple tries."""
        # Arrange
        command = "pm list packages"
        args = ""
        expected_result = "package:com.example.app"

        # First call fails, second succeeds
        self.mock_driver.execute_script.side_effect = [
            NoSuchDriverException("Driver not found"),
            expected_result
        ]
        self.mock_base.reconnect = Mock()

        # Act
        result = self.terminal.adb_shell(command, args, tries=2)

        # Assert
        assert result == expected_result  # noqa: S101
        assert self.mock_driver.execute_script.call_count == 2  # noqa: S101
        self.mock_base.reconnect.assert_called_once()

    def test_push_success(self):
        """Test successful file push."""
        # Arrange
        source_path = "/local/path"
        remote_server_path = "/remote/path"
        filename = "file.txt"
        destination = "/device/path"
        udid = "emulator-5554"

        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stdout.readlines.return_value = ["success"]

        self.mock_transport.scp.put = Mock()
        self.mock_transport.ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

        # Act
        result = self.terminal.push(source_path, remote_server_path, filename, destination, udid)

        # Assert
        assert result is True  # noqa: S101
        self.mock_transport.scp.put.assert_called_once()
        self.mock_transport.ssh.exec_command.assert_called_once()

    def test_push_without_credentials(self):
        """Test file push without transport credentials."""
        # Arrange
        source_path = "/local/path"
        remote_server_path = "/remote/path"
        filename = "file.txt"
        destination = "/device/path"
        udid = "emulator-5554"

        # Mock transport to raise OSError (simulating missing credentials)
        self.mock_transport.scp.put.side_effect = OSError("Connection failed")

        # Act
        result = self.terminal.push(source_path, remote_server_path, filename, destination, udid)

        # Assert
        assert result is False  # noqa: S101

    def test_install_app_success(self):
        """Test successful app installation."""
        # Arrange
        source = "/local/path"
        remote_server_path = "/remote/path"
        filename = "app._apk"
        udid = "emulator-5554"

        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stdout.readlines.return_value = ["success"]

        self.mock_transport.scp.put = Mock()
        self.mock_transport.ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

        # Act
        result = self.terminal.install_app(source, remote_server_path, filename, udid)

        # Assert
        assert result is True  # noqa: S101
        self.mock_transport.scp.put.assert_called_once()
        self.mock_transport.ssh.exec_command.assert_called_once()

    def test_install_app_without_credentials(self):
        """Test app installation without transport credentials."""
        # Arrange
        source = "/local/path"
        remote_server_path = "/remote/path"
        filename = "app._apk"
        udid = "emulator-5554"

        # Mock transport to raise OSError (simulating missing credentials)
        self.mock_transport.scp.put.side_effect = OSError("Connection failed")

        # Act
        result = self.terminal.install_app(source, remote_server_path, filename, udid)

        # Assert
        assert result is False  # noqa: S101

    def test_pull_success(self):
        """Test successful file pull."""
        # Arrange
        source = "/device/path/file.txt"
        destination = "/local/path/file.txt"

        # Mock the base64 encoded file content
        mock_file_content = b"file content"
        mock_encoded_content = base64.b64encode(mock_file_content).decode()

        # Mock the extension assertion and execute_script chain
        mock_extension = Mock()
        mock_extension.execute_script.return_value = mock_encoded_content
        self.mock_driver.assert_extension_exists = Mock(return_value=mock_extension)

        # Mock the open function
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_file.write = Mock()

        with patch("pathlib.Path.open", return_value=mock_file), \
             patch("pathlib.Path.mkdir") as mock_mkdir:
            # Act
            result = self.terminal.pull(source, destination)

            # Assert
            assert result is True  # noqa: S101
            self.mock_driver.assert_extension_exists.assert_called_once_with("mobile: pullFile")
            mock_extension.execute_script.assert_called_once_with("mobile: pullFile", {"remotePath": source})

    def test_pull_driver_exception(self):
        """Test file pull with driver exception."""
        # Arrange
        source = "/device/path/file.txt"
        destination = "/local/path/file.txt"

        # Mock the extension assertion to raise exception
        self.mock_base.reconnect = Mock()
        self.mock_driver.assert_extension_exists = Mock(side_effect=NoSuchDriverException("Driver not found"))

        # Act
        result = self.terminal.pull(source, destination)

        # Assert
        assert result is False  # noqa: S101
        self.mock_base.reconnect.assert_called_once()

    def test_tap_success(self):
        """Test successful tap action."""
        # Arrange
        x, y = 100, 200

        with patch.object(self.terminal, "adb_shell", return_value=True) as mock_adb_shell:
            # Act
            result = self.terminal.tap(x, y)

            # Assert
            assert result is True  # noqa: S101
            mock_adb_shell.assert_called_once_with(command="input", args=f"tap {x} {y}")

    def test_tap_driver_exception(self):
        """Test tap action with driver exception."""
        # Arrange
        x, y = 100, 200

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.tap(x, y)

            # Assert
            assert result is False  # noqa: S101

    def test_swipe_success(self):
        """Test successful swipe action."""
        # Arrange
        x1, y1, x2, y2 = 100, 200, 300, 400
        duration = 1000

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.swipe(x1, y1, x2, y2, duration)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="input", args=f"swipe {x1} {y1} {x2} {y2} {duration}")

    def test_swipe_driver_exception(self):
        """Test swipe action with driver exception."""
        # Arrange
        x1, y1, x2, y2 = 100, 200, 300, 400
        duration = 1000

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.swipe(x1, y1, x2, y2, duration)

            # Assert
            assert result is False  # noqa: S101

    def test_input_text_success(self):
        """Test successful text input."""
        # Arrange
        text = "Hello World"

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.input_text(text)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="input", args=f"text {text}")

    def test_input_text_driver_exception(self):
        """Test text input with driver exception."""
        # Arrange
        text = "Hello World"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.input_text(text)

            # Assert
            assert result is False  # noqa: S101

    def test_press_home_success(self):
        """Test successful home button press."""
        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.press_home()

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="input", args="keyevent KEYCODE_HOME")

    def test_press_back_success(self):
        """Test successful back button press."""
        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.press_back()

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="input", args="keyevent KEYCODE_BACK")

    def test_press_menu_success(self):
        """Test successful menu button press."""
        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.press_menu()

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="input", args="keyevent KEYCODE_MENU")

    def test_get_prop_success(self):
        """Test successful property retrieval."""
        # Arrange
        expected_value = "[ro.build.version.release]: [11]\n[ro.product.model]: [Nexus 6]"

        with patch.object(self.terminal, "adb_shell", return_value=expected_value) as mock_adb_shell:
            # Act
            result = self.terminal.get_prop()

            # Assert
            expected_dict = {"ro.build.version.release": "11", "ro.product.model": "Nexus 6"}
            assert result == expected_dict  # noqa: S101
            mock_adb_shell.assert_called_once_with(command="getprop")

    def test_get_prop_driver_exception(self):
        """Test property retrieval with driver exception."""
        # Arrange
        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")), \
             pytest.raises(KeyError, match="Driver not found"):
            # Act & Assert
            self.terminal.get_prop()

    def test_reboot_success(self):
        """Test successful device reboot."""
        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.reboot()

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="reboot")

    def test_reboot_driver_exception(self):
        """Test device reboot with driver exception."""
        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.reboot()

            # Assert
            assert result is True  # noqa: S101

    def test_get_packages_success(self):
        """Test successful package list retrieval."""
        # Arrange
        mock_output = "package:com.example.app\npackage:com.other.app"

        with patch.object(self.terminal, "adb_shell", return_value=mock_output):
            # Act
            result = self.terminal.get_packages()

            # Assert
            expected_packages = ["com.example.app", "com.other.app"]
            assert result == expected_packages  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="pm", args="list packages")

    def test_get_packages_driver_exception(self):
        """Test package list retrieval with driver exception."""
        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")), \
             pytest.raises(KeyError, match="Driver not found"):
            # Act & Assert
            self.terminal.get_packages()

    def test_get_package_path_success(self):
        """Test successful package path retrieval."""
        # Arrange
        package = "com.example.app"
        expected_path = "/data/app/com.example.app/shadowstep._apk"

        with patch.object(self.terminal, "adb_shell", return_value=expected_path):
            # Act
            result = self.terminal.get_package_path(package)

            # Assert
            assert result == expected_path  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="pm", args=f"path {package}")

    def test_get_package_path_driver_exception(self):
        """Test package path retrieval with driver exception."""
        # Arrange
        package = "com.nonexistent.app"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")), \
             pytest.raises(KeyError, match="Driver not found"):
            # Act & Assert
            self.terminal.get_package_path(package)

    def test_record_video_success(self):
        """Test successful video recording start."""
        # Arrange
        filename = "test_video.mp4"
        duration = 30

        with patch.object(self.terminal.driver, "start_recording_screen") as mock_start_recording:
            # Act
            result = self.terminal.record_video(filename=filename, duration=duration)

            # Assert
            assert result is True  # noqa: S101
            mock_start_recording.assert_called_once_with(filename=filename, duration=duration)

    def test_record_video_driver_exception(self):
        """Test video recording start with driver exception."""
        # Arrange
        filename = "test_video.mp4"
        duration = 30

        with patch.object(self.terminal.driver, "start_recording_screen", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.record_video(filename=filename, duration=duration)

            # Assert
            assert result is False  # noqa: S101

    def test_stop_video_success(self):
        """Test successful video recording stop."""
        # Arrange
        mock_base64_data = "base64_encoded_video_data"
        expected_bytes = b"decoded_video_data"
        
        with patch.object(self.terminal.driver, "stop_recording_screen", return_value=mock_base64_data), \
             patch("base64.b64decode", return_value=expected_bytes) as mock_b64decode:
            # Act
            result = self.terminal.stop_video()

            # Assert
            assert result == expected_bytes  # noqa: S101
            self.terminal.driver.stop_recording_screen.assert_called_once_with()
            mock_b64decode.assert_called_once_with(mock_base64_data)

    def test_stop_video_driver_exception(self):
        """Test video recording stop with driver exception."""
        with patch.object(self.terminal.driver, "stop_recording_screen", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.stop_video()

            # Assert
            assert result is None  # noqa: S101

    def test_check_vpn_success(self):
        """Test successful VPN check."""
        # Arrange
        ip_address = "192.168.1.100"
        netstat_output = f"tcp 0 0 {ip_address}:443 ESTABLISHED"

        with patch.object(self.terminal, "adb_shell", return_value=netstat_output) as mock_adb_shell:
            # Act
            result = self.terminal.check_vpn(ip_address)

            # Assert
            assert result is True  # noqa: S101
            mock_adb_shell.assert_called_once_with(command="netstat", args="")

    def test_check_vpn_no_connection(self):
        """Test VPN check with no VPN connection."""
        # Arrange
        ip_address = "192.168.1.100"

        with patch.object(self.terminal, "adb_shell", return_value="netstat output without VPN connection"):
            # Act
            result = self.terminal.check_vpn(ip_address)

            # Assert
            assert result is False  # noqa: S101

    def test_check_vpn_driver_exception(self):
        """Test VPN check with driver exception."""
        # Arrange
        ip_address = "192.168.1.100"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.check_vpn(ip_address)

            # Assert
            assert result is False  # noqa: S101



