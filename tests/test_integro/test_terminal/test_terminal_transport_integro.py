# ruff: noqa
# pyright: ignore
"""
Integration tests for shadowstep.terminal.transport module.

These tests verify real SSH and SCP operations with actual servers.

Coverage notes:
- Tests Transport.__init__() with real SSH connection
- Tests SSH command execution through paramiko
- Tests SCP file upload (put)
- Tests SCP file download (get)
- Tests error handling for invalid credentials
- Tests connection attributes (ssh, scp)

Requirements:
- SSH server accessible at localhost (127.0.0.1)
- Environment variables: SHADOWSTEP_SSH_USER, SHADOWSTEP_SSH_PASSWORD
- SSH service running on standard port (22)
"""

import os
import tempfile
import time
from pathlib import Path

import paramiko
import pytest

from shadowstep.terminal.transport import Transport


@pytest.fixture
def ssh_credentials():
    """Fixture providing SSH credentials from environment variables."""
    user = os.getenv("SHADOWSTEP_SSH_USER")
    password = os.getenv("SHADOWSTEP_SSH_PASSWORD")

    if not user or not password:
        pytest.skip("SSH credentials not set in environment (SHADOWSTEP_SSH_USER, SHADOWSTEP_SSH_PASSWORD)")

    return {
        "server": "127.0.0.1",
        "port": 22,
        "user": user,
        "password": password
    }


@pytest.fixture
def temp_file():
    """Fixture providing temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test content for Transport SCP operations\n")
        f.write("Line 2: Testing file transfer\n")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if Path(temp_path).exists():
        Path(temp_path).unlink()


@pytest.fixture
def temp_dir():
    """Fixture providing temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield temp_path

    # Cleanup
    if Path(temp_path).exists():
        import shutil
        shutil.rmtree(temp_path)


@pytest.fixture
def remote_test_file():
    """Fixture providing remote file path for testing."""
    remote_path = f"/tmp/shadowstep_test_{int(time.time())}.txt"
    yield remote_path

    # Cleanup - try to remove remote file
    try:
        user = os.getenv("SHADOWSTEP_SSH_USER")
        password = os.getenv("SHADOWSTEP_SSH_PASSWORD")
        if user and password:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect("127.0.0.1", 22, user, password)
            stdin, stdout, stderr = client.exec_command(f"rm -f {remote_path}")
            stdout.channel.recv_exit_status()
            client.close()
    except Exception:
        pass


class TestTransportIntegration:
    """Integration test cases for Transport class."""

    def test_transport_initialization(self, ssh_credentials):
        """Test Transport initializes with correct SSH connection."""
        # Act
        transport = Transport(**ssh_credentials)

        # Assert
        assert transport is not None
        assert transport.ssh is not None
        assert isinstance(transport.ssh, paramiko.SSHClient)
        assert transport.scp is not None

        # Verify connection is active
        assert transport.ssh.get_transport() is not None
        assert transport.ssh.get_transport().is_active()

        # Cleanup
        transport.ssh.close()

    def test_transport_ssh_command_execution(self, ssh_credentials):
        """Test executing commands through SSH connection."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Act - execute simple command
        stdin, stdout, stderr = transport.ssh.exec_command("echo 'test message'")
        output = stdout.read().decode().strip()
        exit_status = stdout.channel.recv_exit_status()

        # Assert
        assert exit_status == 0
        assert output == "test message"

        # Cleanup
        transport.ssh.close()

    def test_transport_ssh_command_with_error(self, ssh_credentials):
        """Test SSH command that produces error."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Act - execute command that will fail
        stdin, stdout, stderr = transport.ssh.exec_command("ls /nonexistent_directory_xyz123")
        error_output = stderr.read().decode()
        exit_status = stdout.channel.recv_exit_status()

        # Assert - command should fail
        assert exit_status != 0
        assert len(error_output) > 0

        # Cleanup
        transport.ssh.close()

    def test_transport_scp_put_file(self, ssh_credentials, temp_file, remote_test_file):
        """Test uploading file via SCP."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Act - upload file
        transport.scp.put(temp_file, remote_test_file)

        # Verify file exists on remote
        stdin, stdout, stderr = transport.ssh.exec_command(f"test -f {remote_test_file} && echo 'exists'")
        output = stdout.read().decode().strip()

        # Assert
        assert output == "exists"

        # Verify file content
        stdin, stdout, stderr = transport.ssh.exec_command(f"cat {remote_test_file}")
        content = stdout.read().decode()
        assert "Test content for Transport SCP operations" in content
        assert "Line 2: Testing file transfer" in content

        # Cleanup
        transport.ssh.close()

    def test_transport_scp_get_file(self, ssh_credentials, temp_dir, remote_test_file):
        """Test downloading file via SCP."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Create a file on remote server first
        test_content = "Remote file content for SCP get test\n"
        stdin, stdout, stderr = transport.ssh.exec_command(
            f"echo '{test_content}' > {remote_test_file}"
        )
        stdout.channel.recv_exit_status()

        local_path = Path(temp_dir) / "downloaded_file.txt"

        # Act - download file
        transport.scp.get(remote_test_file, str(local_path))

        # Assert
        assert local_path.exists()
        assert local_path.is_file()

        content = local_path.read_text()
        assert test_content.strip() in content

        # Cleanup
        transport.ssh.close()

    def test_transport_scp_put_multiple_files(self, ssh_credentials, temp_dir):
        """Test uploading multiple files via SCP."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Create multiple temp files
        file1 = Path(temp_dir) / "file1.txt"
        file2 = Path(temp_dir) / "file2.txt"
        file1.write_text("Content of file 1")
        file2.write_text("Content of file 2")

        remote_dir = f"/tmp/shadowstep_multi_{int(time.time())}"

        # Create remote directory
        stdin, stdout, stderr = transport.ssh.exec_command(f"mkdir -p {remote_dir}")
        stdout.channel.recv_exit_status()

        # Act - upload files
        transport.scp.put(str(file1), f"{remote_dir}/file1.txt")
        transport.scp.put(str(file2), f"{remote_dir}/file2.txt")

        # Verify
        stdin, stdout, stderr = transport.ssh.exec_command(f"ls {remote_dir}")
        output = stdout.read().decode()

        # Assert
        assert "file1.txt" in output
        assert "file2.txt" in output

        # Cleanup remote directory
        stdin, stdout, stderr = transport.ssh.exec_command(f"rm -rf {remote_dir}")
        stdout.channel.recv_exit_status()
        transport.ssh.close()

    def test_transport_ssh_multiple_commands(self, ssh_credentials):
        """Test executing multiple SSH commands sequentially."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Act & Assert - multiple commands
        commands = [
            ("echo 'test1'", "test1"),
            ("echo 'test2'", "test2"),
            ("pwd", "/"),  # Should contain at least "/"
        ]

        for command, expected_substr in commands:
            stdin, stdout, stderr = transport.ssh.exec_command(command)
            output = stdout.read().decode().strip()
            stdout.channel.recv_exit_status()
            assert expected_substr in output

        # Cleanup
        transport.ssh.close()

    def test_transport_connection_is_active(self, ssh_credentials):
        """Test that transport connection remains active."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Act
        is_active = transport.ssh.get_transport().is_active()

        # Assert
        assert is_active is True

        # Execute command to verify connection works
        stdin, stdout, stderr = transport.ssh.exec_command("echo 'connection test'")
        output = stdout.read().decode().strip()

        assert output == "connection test"

        # Cleanup
        transport.ssh.close()

    def test_transport_close_connection(self, ssh_credentials):
        """Test closing SSH connection."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Verify connection is active
        assert transport.ssh.get_transport().is_active()

        # Act - close connection
        transport.ssh.close()

        # Assert - connection should be closed
        # Note: get_transport() might return None after close
        if transport.ssh.get_transport():
            assert not transport.ssh.get_transport().is_active()

    def test_transport_invalid_credentials_raises_exception(self):
        """Test that invalid credentials raise authentication exception."""
        # Act & Assert
        with pytest.raises((paramiko.AuthenticationException, paramiko.SSHException)):
            Transport(
                server="127.0.0.1",
                port=22,
                user="invalid_user_xyz123",
                password="invalid_password_xyz123"
            )

    def test_transport_invalid_server_raises_exception(self, ssh_credentials):
        """Test that invalid server raises connection exception."""
        # Act & Assert
        with pytest.raises((paramiko.SSHException, OSError, TimeoutError)):
            Transport(
                server="192.0.2.1",  # Non-routable IP (TEST-NET-1)
                port=22,
                user=ssh_credentials["user"],
                password=ssh_credentials["password"]
            )

    def test_transport_invalid_port_raises_exception(self, ssh_credentials):
        """Test that invalid port raises connection exception."""
        # Act & Assert
        with pytest.raises((paramiko.SSHException, OSError, ConnectionRefusedError)):
            Transport(
                server="127.0.0.1",
                port=9999,  # Likely unused port
                user=ssh_credentials["user"],
                password=ssh_credentials["password"]
            )

    def test_transport_scp_attribute_exists(self, ssh_credentials):
        """Test that SCP client attribute is properly initialized."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Assert
        assert hasattr(transport, 'scp')
        assert transport.scp is not None
        # SCP client should have put/get methods
        assert hasattr(transport.scp, 'put')
        assert hasattr(transport.scp, 'get')

        # Cleanup
        transport.ssh.close()

    def test_transport_ssh_attribute_exists(self, ssh_credentials):
        """Test that SSH client attribute is properly initialized."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Assert
        assert hasattr(transport, 'ssh')
        assert transport.ssh is not None
        assert isinstance(transport.ssh, paramiko.SSHClient)

        # Cleanup
        transport.ssh.close()

    def test_transport_multiple_instances(self, ssh_credentials):
        """Test creating multiple Transport instances."""
        # Act
        transport1 = Transport(**ssh_credentials)
        transport2 = Transport(**ssh_credentials)

        # Assert - both should be independent and active
        assert transport1 is not transport2
        assert transport1.ssh.get_transport().is_active()
        assert transport2.ssh.get_transport().is_active()

        # Cleanup
        transport1.ssh.close()
        transport2.ssh.close()

    def test_transport_ssh_exec_command_with_timeout(self, ssh_credentials):
        """Test SSH command execution with reasonable timeout."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Act - execute command that takes some time
        stdin, stdout, stderr = transport.ssh.exec_command("sleep 1 && echo 'done'")
        output = stdout.read().decode().strip()

        # Assert
        assert output == "done"

        # Cleanup
        transport.ssh.close()

    def test_transport_scp_large_file_transfer(self, ssh_credentials, temp_dir, remote_test_file):
        """Test SCP with larger file (still small for test performance)."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Create a larger file (~1KB)
        large_file = Path(temp_dir) / "large_file.txt"
        content = "x" * 1024  # 1KB of data
        large_file.write_text(content)

        # Act - upload
        transport.scp.put(str(large_file), remote_test_file)

        # Verify size on remote
        stdin, stdout, stderr = transport.ssh.exec_command(f"wc -c < {remote_test_file}")
        size = int(stdout.read().decode().strip())

        # Assert
        assert size == 1024

        # Cleanup
        transport.ssh.close()

    def test_transport_scp_binary_file_transfer(self, ssh_credentials, temp_dir, remote_test_file):
        """Test SCP with binary file."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Create binary file
        binary_file = Path(temp_dir) / "binary_file.bin"
        binary_data = bytes(range(256))  # 0-255 bytes
        binary_file.write_bytes(binary_data)

        # Act - upload
        transport.scp.put(str(binary_file), remote_test_file)

        # Download and verify
        downloaded = Path(temp_dir) / "downloaded.bin"
        transport.scp.get(remote_test_file, str(downloaded))

        # Assert
        assert downloaded.read_bytes() == binary_data

        # Cleanup
        transport.ssh.close()

    def test_transport_reconnect_after_close(self, ssh_credentials):
        """Test creating new transport after closing previous one."""
        # Arrange - create and close first transport
        transport1 = Transport(**ssh_credentials)
        transport1.ssh.close()

        # Act - create new transport
        transport2 = Transport(**ssh_credentials)

        # Assert - new transport should work
        assert transport2.ssh.get_transport().is_active()

        stdin, stdout, stderr = transport2.ssh.exec_command("echo 'reconnect test'")
        output = stdout.read().decode().strip()
        assert output == "reconnect test"

        # Cleanup
        transport2.ssh.close()

    def test_transport_ssh_stderr_capture(self, ssh_credentials):
        """Test capturing stderr from SSH command."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Act - command that writes to stderr
        stdin, stdout, stderr = transport.ssh.exec_command("echo 'error message' >&2")
        error_output = stderr.read().decode().strip()

        # Assert
        assert "error message" in error_output

        # Cleanup
        transport.ssh.close()

    def test_transport_ssh_stdin_interaction(self, ssh_credentials):
        """Test sending input via stdin to SSH command."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Act - use cat to echo stdin
        stdin, stdout, stderr = transport.ssh.exec_command("cat")
        stdin.write("test input\n")
        stdin.channel.shutdown_write()
        output = stdout.read().decode().strip()

        # Assert
        assert output == "test input"

        # Cleanup
        transport.ssh.close()

    def test_transport_working_directory_command(self, ssh_credentials):
        """Test SSH command with working directory verification."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Act - check working directory
        stdin, stdout, stderr = transport.ssh.exec_command("pwd")
        pwd = stdout.read().decode().strip()

        # Assert - should return some valid path
        assert pwd.startswith("/")
        assert len(pwd) > 1

        # Cleanup
        transport.ssh.close()

    def test_transport_environment_variables(self, ssh_credentials):
        """Test SSH command can access environment variables."""
        # Arrange
        transport = Transport(**ssh_credentials)

        # Act - check for common environment variable
        stdin, stdout, stderr = transport.ssh.exec_command("echo $HOME")
        home = stdout.read().decode().strip()

        # Assert - HOME should be set
        assert len(home) > 0
        assert home.startswith("/")

        # Cleanup
        transport.ssh.close()
