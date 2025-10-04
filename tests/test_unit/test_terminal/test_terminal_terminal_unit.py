# ruff: noqa
# pyright: ignore
"""
Tests for shadowstep.terminal.terminal module.
"""

import base64
import subprocess
from unittest.mock import Mock, patch

import pytest
from selenium.common import InvalidSessionIdException, NoSuchDriverException

from shadowstep.terminal.terminal import NotProvideCredentialsError, Terminal, AdbShellError


class TestNotProvideCredentialsError:
    """Test cases for NotProvideCredentialsError exception."""

    @pytest.mark.unit
    def test_default_message(self):
        """Test exception with default message."""
        # Act
        exception = NotProvideCredentialsError()

        # Assert
        expected_message = (
            "Not provided credentials for ssh connection "
            "in connect() method (ssh_username, ssh_password)"
        )
        assert str(exception) == expected_message  # noqa: S101
        assert exception.message == expected_message  # noqa: S101

    @pytest.mark.unit
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
        self.mock_shadowstep = Mock()
        self.mock_driver = Mock()
        self.mock_transport = Mock()
        self.mock_ssh = Mock()
        self.mock_scp = Mock()

        self.mock_shadowstep.driver = self.mock_driver
        self.mock_shadowstep.transport = self.mock_transport
        self.mock_transport.ssh = self.mock_ssh
        self.mock_transport.scp = self.mock_scp

        with patch('shadowstep.shadowstep.Shadowstep.get_instance', return_value=self.mock_shadowstep):
            self.terminal = Terminal()

    @pytest.mark.unit
    def test_init(self):
        """Test Terminal initialization."""
        # Arrange
        mock_shadowstep = Mock()
        mock_driver = Mock()
        mock_transport = Mock()

        mock_shadowstep.driver = mock_driver
        mock_shadowstep.transport = mock_transport

        # Act
        with patch('shadowstep.shadowstep.Shadowstep.get_instance', return_value=mock_shadowstep):
            terminal = Terminal()

        # Assert
        assert terminal.shadowstep == mock_shadowstep  # noqa: S101
        assert terminal.driver == mock_driver  # noqa: S101
        assert terminal.transport == mock_transport  # noqa: S101

    @pytest.mark.unit
    def test_del(self):
        """Test Terminal destructor."""
        # Act
        del self.terminal

        # Assert
        self.mock_ssh.close.assert_called_once()

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_adb_shell_no_such_driver_exception(self):
        """Test adb shell raises AdbShellError on NoSuchDriverException."""
        command = "pm list packages"
        args = ""

        self.mock_driver.execute_script.side_effect = NoSuchDriverException("Driver not found")
        self.mock_shadowstep.reconnect = Mock()

        with pytest.raises(AdbShellError) as exc_info:
            self.terminal.adb_shell(command, args, tries=1)

        assert "adb_shell failed" in str(exc_info.value)  # noqa: S101
        self.mock_shadowstep.reconnect.assert_called_once()

    @pytest.mark.unit
    def test_adb_shell_invalid_session_exception(self):
        """Test adb shell with InvalidSessionIdException."""
        # Arrange
        command = "pm list packages"
        args = ""

        self.mock_driver.execute_script.side_effect = InvalidSessionIdException("Invalid session")
        self.mock_shadowstep.reconnect = Mock()

        with pytest.raises(AdbShellError) as exc_info:
            self.terminal.adb_shell(command, args, tries=1)

        assert "adb_shell failed" in str(exc_info.value)  # noqa: S101
        self.mock_shadowstep.reconnect.assert_called_once()

    @pytest.mark.unit
    def test_adb_shell_key_error(self):
        """Test adb shell with KeyError raises AdbShellError without reconnect."""
        command = "pm list packages"
        args = ""

        self.mock_driver.execute_script.side_effect = KeyError("Key not found")

        with pytest.raises(AdbShellError) as exc_info:
            self.terminal.adb_shell(command, args, tries=1)

        assert "adb_shell failed" in str(exc_info.value)  # noqa: S101
        self.mock_shadowstep.reconnect.assert_not_called()

    @pytest.mark.unit
    def test_adb_shell_multiple_tries(self):
        """Test adb shell with multiple tries."""
        # Arrange
        command = "pm list packages"
        args = ""
        expected_result = "package:com.example.app"

        # First call fails, second succeeds
        self.mock_driver.execute_script.side_effect = [
            NoSuchDriverException("Driver not found"),
            expected_result,
        ]
        self.mock_shadowstep.reconnect = Mock()

        # Act
        result = self.terminal.adb_shell(command, args, tries=2)

        # Assert
        assert result == expected_result  # noqa: S101
        assert self.mock_driver.execute_script.call_count == 2  # noqa: S101
        self.mock_shadowstep.reconnect.assert_called_once()

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

        with (
            patch("pathlib.Path.open", return_value=mock_file),
            patch("pathlib.Path.mkdir") as mock_mkdir,
        ):
            # Act
            result = self.terminal.pull(source, destination)

            # Assert
            assert result is True  # noqa: S101
            self.mock_driver.assert_extension_exists.assert_called_once_with("mobile: pullFile")
            mock_extension.execute_script.assert_called_once_with(
                "mobile: pullFile", {"remotePath": source}
            )

    @pytest.mark.unit
    def test_pull_driver_exception(self):
        """Test file pull with driver exception."""
        # Arrange
        source = "/device/path/file.txt"
        destination = "/local/path/file.txt"

        # Mock the extension assertion to raise exception
        self.mock_shadowstep.reconnect = Mock()
        self.mock_driver.assert_extension_exists = Mock(
            side_effect=NoSuchDriverException("Driver not found")
        )

        # Act
        result = self.terminal.pull(source, destination)

        # Assert
        assert result is False  # noqa: S101
        self.mock_shadowstep.reconnect.assert_called_once()

    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_tap_driver_exception(self):
        """Test tap action with driver exception."""
        # Arrange
        x, y = 100, 200

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.tap(x, y)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
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
            self.terminal.adb_shell.assert_called_once_with(
                command="input", args=f"swipe {x1} {y1} {x2} {y2} {duration}"
            )

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_input_text_driver_exception(self):
        """Test text input with driver exception."""
        # Arrange
        text = "Hello World"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.input_text(text)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_press_home_success(self):
        """Test successful home button press."""
        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.press_home()

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(
                command="input", args="keyevent KEYCODE_HOME"
            )

    @pytest.mark.unit
    def test_press_back_success(self):
        """Test successful back button press."""
        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.press_back()

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(
                command="input", args="keyevent KEYCODE_BACK"
            )

    @pytest.mark.unit
    def test_press_menu_success(self):
        """Test successful menu button press."""
        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.press_menu()

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(
                command="input", args="keyevent KEYCODE_MENU"
            )

    @pytest.mark.unit
    def test_get_prop_success(self):
        """Test successful property retrieval."""
        # Arrange
        expected_value = "[ro.build.version.release]: [11]\n[ro.product.model]: [Nexus 6]"

        with patch.object(
            self.terminal, "adb_shell", return_value=expected_value
        ) as mock_adb_shell:
            # Act
            result = self.terminal.get_prop()

            # Assert
            expected_dict = {"ro.build.version.release": "11", "ro.product.model": "Nexus 6"}
            assert result == expected_dict  # noqa: S101
            mock_adb_shell.assert_called_once_with(command="getprop")

    @pytest.mark.unit
    def test_get_prop_driver_exception(self):
        """Test property retrieval with driver exception."""
        # Arrange
        with (
            patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")),
            pytest.raises(KeyError, match="Driver not found"),
        ):
            # Act & Assert
            self.terminal.get_prop()

    @pytest.mark.unit
    def test_reboot_success(self):
        """Test successful device reboot."""
        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.reboot()

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="reboot")

    @pytest.mark.unit
    def test_reboot_driver_exception(self):
        """Test device reboot with driver exception."""
        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.reboot()

            # Assert
            assert result is True  # noqa: S101

    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_get_packages_driver_exception(self):
        """Test package list retrieval with driver exception."""
        with (
            patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")),
            pytest.raises(KeyError, match="Driver not found"),
        ):
            # Act & Assert
            self.terminal.get_packages()

    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_get_package_path_driver_exception(self):
        """Test package path retrieval with driver exception."""
        # Arrange
        package = "com.nonexistent.app"

        with (
            patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")),
            pytest.raises(KeyError, match="Driver not found"),
        ):
            # Act & Assert
            self.terminal.get_package_path(package)

    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_record_video_driver_exception(self):
        """Test video recording start with driver exception."""
        # Arrange
        filename = "test_video.mp4"
        duration = 30

        with patch.object(
            self.terminal.driver, "start_recording_screen", side_effect=KeyError("Driver not found")
        ):
            # Act
            result = self.terminal.record_video(filename=filename, duration=duration)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_stop_video_success(self):
        """Test successful video recording stop."""
        # Arrange
        mock_base64_data = "base64_encoded_video_data"
        expected_bytes = b"decoded_video_data"

        with (
            patch.object(
                self.terminal.driver, "stop_recording_screen", return_value=mock_base64_data
            ),
            patch("base64.b64decode", return_value=expected_bytes) as mock_b64decode,
        ):
            # Act
            result = self.terminal.stop_video()

            # Assert
            assert result == expected_bytes  # noqa: S101
            self.terminal.driver.stop_recording_screen.assert_called_once_with()
            mock_b64decode.assert_called_once_with(mock_base64_data)

    @pytest.mark.unit
    def test_stop_video_driver_exception(self):
        """Test video recording stop with driver exception."""
        with patch.object(
            self.terminal.driver, "stop_recording_screen", side_effect=KeyError("Driver not found")
        ):
            # Act
            result = self.terminal.stop_video()

            # Assert
            assert result is None  # noqa: S101

    @pytest.mark.unit
    def test_check_vpn_success(self):
        """Test successful VPN check."""
        # Arrange
        ip_address = "192.168.1.100"
        netstat_output = f"tcp 0 0 {ip_address}:443 ESTABLISHED"

        with patch.object(
            self.terminal, "adb_shell", return_value=netstat_output
        ) as mock_adb_shell:
            # Act
            result = self.terminal.check_vpn(ip_address)

            # Assert
            assert result is True  # noqa: S101
            mock_adb_shell.assert_called_once_with(command="netstat", args="")

    @pytest.mark.unit
    def test_check_vpn_no_connection(self):
        """Test VPN check with no VPN connection."""
        # Arrange
        ip_address = "192.168.1.100"

        with patch.object(
            self.terminal, "adb_shell", return_value="netstat output without VPN connection"
        ):
            # Act
            result = self.terminal.check_vpn(ip_address)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_check_vpn_driver_exception(self):
        """Test VPN check with driver exception."""
        # Arrange
        ip_address = "192.168.1.100"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.check_vpn(ip_address)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_start_activity_success(self):
        """Test successful activity start."""
        # Arrange
        package = "com.example.app"
        activity = "com.example.app.MainActivity"

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.start_activity(package, activity)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(
                command="am", args=f"start -n {package}/{activity}"
            )

    @pytest.mark.unit
    def test_start_activity_driver_exception(self):
        """Test activity start with driver exception."""
        # Arrange
        package = "com.example.app"
        activity = "com.example.app.MainActivity"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.start_activity(package, activity)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_get_current_app_package_success(self):
        """Test successful current app package retrieval."""
        # Arrange
        dumpsys_output = "mCurrentFocus=Window{1234567890 u0 com.example.app/com.example.app.MainActivity}"

        with patch.object(self.terminal, "adb_shell", return_value=dumpsys_output):
            # Act
            result = self.terminal.get_current_app_package()

            # Assert
            assert result == "com.example.app"  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="dumpsys", args="window windows")

    @pytest.mark.unit
    def test_get_current_app_package_no_match(self):
        """Test current app package retrieval with no match."""
        # Arrange
        dumpsys_output = "No current focus found"

        with patch.object(self.terminal, "adb_shell", return_value=dumpsys_output):
            # Act
            result = self.terminal.get_current_app_package()

            # Assert
            assert result == ""  # noqa: S101

    @pytest.mark.unit
    def test_get_current_app_package_driver_exception(self):
        """Test current app package retrieval with driver exception."""
        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.get_current_app_package()

            # Assert
            assert result == ""  # noqa: S101

    @pytest.mark.unit
    def test_close_app_success(self):
        """Test successful app close."""
        # Arrange
        package = "com.example.app"

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.close_app(package)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="am", args=f"force-stop {package}")

    @pytest.mark.unit
    def test_close_app_driver_exception(self):
        """Test app close with driver exception."""
        # Arrange
        package = "com.example.app"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.close_app(package)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_reboot_app_success(self):
        """Test successful app reboot."""
        # Arrange
        package = "com.example.app"
        activity = "com.example.app.MainActivity"

        with patch.object(self.terminal, "close_app", return_value=True), \
             patch.object(self.terminal, "start_activity", return_value=True):
            # Act
            result = self.terminal.reboot_app(package, activity)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.close_app.assert_called_once_with(package=package)
            self.terminal.start_activity.assert_called_once_with(package=package, activity=activity)

    @pytest.mark.unit
    def test_reboot_app_close_fails(self):
        """Test app reboot when close fails."""
        # Arrange
        package = "com.example.app"
        activity = "com.example.app.MainActivity"

        with patch.object(self.terminal, "close_app", return_value=False):
            # Act
            result = self.terminal.reboot_app(package, activity)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_is_app_installed_true(self):
        """Test app installation check when app is installed."""
        # Arrange
        package = "com.example.app"
        pm_output = "package:com.example.app\npackage:com.other.app"

        with patch.object(self.terminal, "adb_shell", return_value=pm_output):
            # Act
            result = self.terminal.is_app_installed(package)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="pm", args="list packages")

    @pytest.mark.unit
    def test_is_app_installed_false(self):
        """Test app installation check when app is not installed."""
        # Arrange
        package = "com.nonexistent.app"
        pm_output = "package:com.example.app\npackage:com.other.app"

        with patch.object(self.terminal, "adb_shell", return_value=pm_output):
            # Act
            result = self.terminal.is_app_installed(package)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_is_app_installed_driver_exception(self):
        """Test app installation check with driver exception."""
        # Arrange
        package = "com.example.app"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.is_app_installed(package)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_uninstall_app_success(self):
        """Test successful app uninstall."""
        # Arrange
        package = "com.example.app"

        with patch.object(self.terminal.driver, "remove_app", return_value=True):
            # Act
            result = self.terminal.uninstall_app(package)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.driver.remove_app.assert_called_once_with(app_id=package)

    @pytest.mark.unit
    def test_uninstall_app_driver_exception(self):
        """Test app uninstall with driver exception."""
        # Arrange
        package = "com.example.app"

        with patch.object(self.terminal.driver, "remove_app", side_effect=NoSuchDriverException("Driver not found")):
            self.terminal.shadowstep.reconnect = Mock()
            # Act
            result = self.terminal.uninstall_app(package)

            # Assert
            assert result is False  # noqa: S101
            self.terminal.shadowstep.reconnect.assert_called_once()

    @pytest.mark.unit
    def test_input_keycode_num_success(self):
        """Test successful numeric keycode input."""
        # Arrange
        num = 5

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.input_keycode_num_(num)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="input", args=f"keyevent KEYCODE_NUMPAD_{num}")

    @pytest.mark.unit
    def test_input_keycode_num_driver_exception(self):
        """Test numeric keycode input with driver exception."""
        # Arrange
        num = 5

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.input_keycode_num_(num)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_input_keycode_success(self):
        """Test successful keycode input."""
        # Arrange
        keycode = "KEYCODE_ENTER"

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.input_keycode(keycode)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="input", args=f"keyevent {keycode}")

    @pytest.mark.unit
    def test_input_keycode_driver_exception(self):
        """Test keycode input with driver exception."""
        # Arrange
        keycode = "KEYCODE_ENTER"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.input_keycode(keycode)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_swipe_right_to_left_success(self):
        """Test successful right to left swipe."""
        # Arrange
        duration = 500

        with patch.object(self.terminal, "get_screen_resolution", return_value=(1080, 2400)), \
             patch.object(self.terminal, "swipe", return_value=True) as mock_swipe:
            # Act
            result = self.terminal.swipe_right_to_left(duration)

            # Assert
            assert result is True  # noqa: S101
            mock_swipe.assert_called_once_with(
                start_x=972, start_y=1200, end_x=108, end_y=1200, duration=duration
            )

    @pytest.mark.unit
    def test_swipe_left_to_right_success(self):
        """Test successful left to right swipe."""
        # Arrange
        duration = 500

        with patch.object(self.terminal, "get_screen_resolution", return_value=(1080, 2400)), \
             patch.object(self.terminal, "swipe", return_value=True) as mock_swipe:
            # Act
            result = self.terminal.swipe_left_to_right(duration)

            # Assert
            assert result is True  # noqa: S101
            mock_swipe.assert_called_once_with(
                start_x=108, start_y=1200, end_x=972, end_y=1200, duration=duration
            )

    @pytest.mark.unit
    def test_swipe_top_to_bottom_success(self):
        """Test successful top to bottom swipe."""
        # Arrange
        duration = 500

        with patch.object(self.terminal, "get_screen_resolution", return_value=(1080, 2400)), \
             patch.object(self.terminal, "swipe", return_value=True) as mock_swipe:
            # Act
            result = self.terminal.swipe_top_to_bottom(duration)

            # Assert
            assert result is True  # noqa: S101
            mock_swipe.assert_called_once_with(
                start_x=240, start_y=1200, end_x=2160, end_y=1200, duration=duration
            )

    @pytest.mark.unit
    def test_swipe_bottom_to_top_success(self):
        """Test successful bottom to top swipe."""
        # Arrange
        duration = 500

        with patch.object(self.terminal, "get_screen_resolution", return_value=(1080, 2400)), \
             patch.object(self.terminal, "swipe", return_value=True) as mock_swipe:
            # Act
            result = self.terminal.swipe_bottom_to_top(duration)

            # Assert
            assert result is True  # noqa: S101
            mock_swipe.assert_called_once_with(
                start_x=2160, start_y=1200, end_x=240, end_y=1200, duration=duration
            )

    @pytest.mark.unit
    def test_stop_logcat_success(self):
        """Test successful logcat stop."""
        # Arrange
        ps_output = "USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1234 567 0 0 0 logcat"

        with patch.object(self.terminal, "adb_shell", return_value=ps_output):
            # Act
            result = self.terminal.stop_logcat()

            # Assert
            assert result is True  # noqa: S101
            # stop_logcat calls adb_shell twice: once for ps and once for kill
            assert self.terminal.adb_shell.call_count == 2  # noqa: S101
            self.terminal.adb_shell.assert_any_call(command="ps", args="")
            self.terminal.adb_shell.assert_any_call(command="kill", args="-SIGINT 1234")

    @pytest.mark.unit
    def test_stop_logcat_no_process(self):
        """Test logcat stop when no logcat process found."""
        # Arrange
        ps_output = "USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1234 567 0 0 0 system"

        with patch.object(self.terminal, "adb_shell", return_value=ps_output):
            # Act
            result = self.terminal.stop_logcat()

            # Assert
            assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_stop_logcat_driver_exception(self):
        """Test logcat stop with driver exception."""
        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.stop_logcat()

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_know_pid_success(self):
        """Test successful PID retrieval."""
        # Arrange
        process_name = "logcat"
        ps_output = "USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1234 567 0 0 0 logcat"

        with patch.object(self.terminal, "adb_shell", return_value=ps_output):
            # Act
            result = self.terminal.know_pid(process_name)

            # Assert
            assert result == 1234  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="ps")

    @pytest.mark.unit
    def test_know_pid_not_found(self):
        """Test PID retrieval when process not found."""
        # Arrange
        process_name = "nonexistent"
        ps_output = "USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1234 567 0 0 0 logcat"

        with patch.object(self.terminal, "adb_shell", return_value=ps_output):
            # Act
            result = self.terminal.know_pid(process_name)

            # Assert
            assert result is None  # noqa: S101

    @pytest.mark.unit
    def test_is_process_exist_true(self):
        """Test process existence check when process exists."""
        # Arrange
        process_name = "logcat"
        ps_output = "USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1234 567 0 0 0 logcat"

        with patch.object(self.terminal, "adb_shell", return_value=ps_output):
            # Act
            result = self.terminal.is_process_exist(process_name)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="ps")

    @pytest.mark.unit
    def test_is_process_exist_false(self):
        """Test process existence check when process does not exist."""
        # Arrange
        process_name = "nonexistent"
        ps_output = "USER PID PPID VSIZE RSS WCHAN PC NAME\nroot 1234 1 1234 567 0 0 0 logcat"

        with patch.object(self.terminal, "adb_shell", return_value=ps_output):
            # Act
            result = self.terminal.is_process_exist(process_name)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_run_background_process_success(self):
        """Test successful background process execution."""
        # Arrange
        command = "logcat"
        args = "-v time"
        process = "logcat"

        with patch.object(self.terminal, "adb_shell", return_value="success"), \
             patch.object(self.terminal, "is_process_exist", return_value=True):
            # Act
            result = self.terminal.run_background_process(command, args, process)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(
                command=command, args=f"{args} nohup > /dev/null 2>&1 &"
            )

    @pytest.mark.unit
    def test_run_background_process_no_check(self):
        """Test background process execution without process check."""
        # Arrange
        command = "logcat"
        args = "-v time"
        process = ""

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.run_background_process(command, args, process)

            # Assert
            assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_run_background_process_driver_exception(self):
        """Test background process execution with driver exception."""
        # Arrange
        command = "logcat"
        args = "-v time"
        process = ""

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.run_background_process(command, args, process)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_kill_by_pid_success(self):
        """Test successful process kill by PID."""
        # Arrange
        pid = 1234

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.kill_by_pid(pid)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="kill", args=f"-s SIGINT {pid}")

    @pytest.mark.unit
    def test_kill_by_pid_driver_exception(self):
        """Test process kill by PID with driver exception."""
        # Arrange
        pid = 1234

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.kill_by_pid(pid)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_kill_by_name_success(self):
        """Test successful process kill by name."""
        # Arrange
        name = "logcat"

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.kill_by_name(name)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="pkill", args=f"-l SIGINT {name}")

    @pytest.mark.unit
    def test_kill_by_name_driver_exception(self):
        """Test process kill by name with driver exception."""
        # Arrange
        name = "logcat"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.kill_by_name(name)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_kill_all_success(self):
        """Test successful kill all processes by name."""
        # Arrange
        name = "logcat"

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.kill_all(name)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="pkill", args=f"-f {name}")

    @pytest.mark.unit
    def test_kill_all_driver_exception(self):
        """Test kill all processes with driver exception."""
        # Arrange
        name = "logcat"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.kill_all(name)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_delete_files_from_internal_storage_success(self):
        """Test successful file deletion from internal storage."""
        # Arrange
        path = "/sdcard/test/"

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.delete_files_from_internal_storage(path)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="rm", args=f"-rf {path}*")

    @pytest.mark.unit
    def test_delete_files_from_internal_storage_driver_exception(self):
        """Test file deletion with driver exception."""
        # Arrange
        path = "/sdcard/test/"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.delete_files_from_internal_storage(path)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_delete_file_from_internal_storage_success(self):
        """Test successful single file deletion from internal storage."""
        # Arrange
        path = "/sdcard/test/"
        filename = "test.txt"

        with patch.object(self.terminal, "adb_shell", return_value="success"):
            # Act
            result = self.terminal.delete_file_from_internal_storage(path, filename)

            # Assert
            assert result is True  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="rm", args=f"-rf /sdcard/test/{filename}")

    @pytest.mark.unit
    def test_delete_file_from_internal_storage_driver_exception(self):
        """Test single file deletion with driver exception."""
        # Arrange
        path = "/sdcard/test/"
        filename = "test.txt"

        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act
            result = self.terminal.delete_file_from_internal_storage(path, filename)

            # Assert
            assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_get_screen_resolution_success(self):
        """Test successful screen resolution retrieval."""
        # Arrange
        wm_output = "Physical size: 1080x2400"

        with patch.object(self.terminal, "adb_shell", return_value=wm_output):
            # Act
            result = self.terminal.get_screen_resolution()

            # Assert
            assert result == (1080, 2400)  # noqa: S101
            self.terminal.adb_shell.assert_called_once_with(command="wm", args="size")

    @pytest.mark.unit
    def test_get_screen_resolution_no_physical_size(self):
        """Test screen resolution retrieval when no physical size found."""
        # Arrange
        wm_output = "No physical size information"

        with patch.object(self.terminal, "adb_shell", return_value=wm_output):
            # Act
            result = self.terminal.get_screen_resolution()

            # Assert
            assert result == (0, 0)  # noqa: S101

    @pytest.mark.unit
    def test_get_screen_resolution_driver_exception(self):
        """Test screen resolution retrieval with driver exception."""
        with patch.object(self.terminal, "adb_shell", side_effect=KeyError("Driver not found")):
            # Act & Assert
            with pytest.raises(KeyError):
                self.terminal.get_screen_resolution()

    @pytest.mark.unit
    def test_past_text_success(self):
        """Test successful text pasting."""
        # Arrange
        text = "Hello World"

        with patch.object(self.terminal.driver, "set_clipboard_text"), \
             patch.object(self.terminal, "input_keycode", return_value=True):
            # Act
            self.terminal.past_text(text)

            # Assert
            self.terminal.driver.set_clipboard_text.assert_called_once_with(text=text)
            self.terminal.input_keycode.assert_called_once_with("279")

    @pytest.mark.unit
    def test_past_text_driver_exception(self):
        """Test text pasting with driver exception."""
        # Arrange
        text = "Hello World"

        with patch.object(self.terminal.driver, "set_clipboard_text", side_effect=NoSuchDriverException("Driver not found")):
            self.terminal.shadowstep.reconnect = Mock()
            # Act
            self.terminal.past_text(text, tries=1)

            # Assert
            self.terminal.shadowstep.reconnect.assert_called_once()

    @pytest.mark.unit
    def test_get_prop_hardware_success(self):
        """Test successful hardware property retrieval."""
        # Arrange
        expected_hardware = "qcom"

        with patch.object(self.terminal, "get_prop", return_value={"ro.boot.hardware": expected_hardware}):
            # Act
            result = self.terminal.get_prop_hardware()

            # Assert
            assert result == expected_hardware  # noqa: S101

    @pytest.mark.unit
    def test_get_prop_model_success(self):
        """Test successful model property retrieval."""
        # Arrange
        expected_model = "Nexus 6"

        with patch.object(self.terminal, "get_prop", return_value={"ro.product.model": expected_model}):
            # Act
            result = self.terminal.get_prop_model()

            # Assert
            assert result == expected_model  # noqa: S101

    @pytest.mark.unit
    def test_get_prop_serial_success(self):
        """Test successful serial property retrieval."""
        # Arrange
        expected_serial = "1234567890"

        with patch.object(self.terminal, "get_prop", return_value={"ro.serialno": expected_serial}):
            # Act
            result = self.terminal.get_prop_serial()

            # Assert
            assert result == expected_serial  # noqa: S101

    @pytest.mark.unit
    def test_get_prop_build_success(self):
        """Test successful build property retrieval."""
        # Arrange
        expected_build = "Nexus 6 Build/QQ3A.200805.001"

        with patch.object(self.terminal, "get_prop", return_value={"ro.build.description": expected_build}):
            # Act
            result = self.terminal.get_prop_build()

            # Assert
            assert result == expected_build  # noqa: S101

    @pytest.mark.unit
    def test_get_prop_device_success(self):
        """Test successful device property retrieval."""
        # Arrange
        expected_device = "flame"

        with patch.object(self.terminal, "get_prop", return_value={"ro.product.device": expected_device}):
            # Act
            result = self.terminal.get_prop_device()

            # Assert
            assert result == expected_device  # noqa: S101

    @pytest.mark.unit
    def test_get_prop_uin_success(self):
        """Test successful UIN property retrieval."""
        # Arrange
        expected_uin = "1234567890"

        with patch.object(self.terminal, "get_prop", return_value={"sys.atol.uin": expected_uin}):
            # Act
            result = self.terminal.get_prop_uin()

            # Assert
            assert result == expected_uin  # noqa: S101

    @pytest.mark.unit
    def test_pull_package_success(self):
        """Test successful package pull."""
        # Arrange
        package = "com.example.app"
        path = "/local/path"
        filename = "test_apk"

        with patch.object(self.terminal, "get_package_path", return_value="/data/app/com.example.app/shadowstep._apk"), \
             patch.object(self.terminal, "pull", return_value=True):
            # Act
            self.terminal.pull_package(package, path, filename)

            # Assert
            self.terminal.get_package_path.assert_called_once_with(package=package)
            self.terminal.pull.assert_called_once()

    @pytest.mark.unit
    def test_pull_package_default_filename(self):
        """Test package pull with default filename."""
        # Arrange
        package = "com.example.app"
        path = "/local/path"
        filename = "test_apk"

        with patch.object(self.terminal, "get_package_path", return_value="/data/app/com.example.app/shadowstep._apk"), \
             patch.object(self.terminal, "pull", return_value=True):
            # Act
            self.terminal.pull_package(package, path, filename)

            # Assert
            self.terminal.pull.assert_called_once()

    @pytest.mark.unit
    def test_get_package_manifest_success(self):
        """Test successful package manifest retrieval."""
        # Arrange
        package = "com.example.app"
        aapt_output = "package: name='com.example.app' versionCode='1' versionName='1.0'"

        with patch.object(self.terminal, "pull_package"), \
             patch("subprocess.check_output", return_value=aapt_output.encode()), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.unlink"):
            # Act
            result = self.terminal.get_package_manifest(package)

            # Assert
            assert "package:" in result  # noqa: S101

    @pytest.mark.unit
    def test_get_package_manifest_aapt_error(self):
        """Test package manifest retrieval with aapt error."""
        # Arrange
        package = "com.example.app"

        with patch.object(self.terminal, "pull_package"), \
             patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "aapt")), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.mkdir"):
            # Act
            result = self.terminal.get_package_manifest(package)

            # Assert
            assert result == {}  # noqa: S101
