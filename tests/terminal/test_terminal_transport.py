"""
Tests for shadowstep.terminal.transport module.
"""

from unittest.mock import Mock, patch

import paramiko
import pytest

from shadowstep.terminal.transport import Transport


class TestTransport:
    """Test cases for Transport class."""

    def test_init_success(self):
        """Test successful Transport initialization."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_ssh_client = Mock()
        mock_transport = Mock()
        mock_ssh_client.get_transport.return_value = mock_transport
        mock_scp_client_instance = Mock()

        with patch.object(Transport, "_create_ssh_client", return_value=mock_ssh_client) as mock_create_ssh, \
             patch("shadowstep.terminal.transport.SCPClient", return_value=mock_scp_client_instance) as mock_scp_client:
            # Act
            transport = Transport(server, port, user, password)

            # Assert
            assert transport.ssh == mock_ssh_client  # noqa: S101
            assert transport.scp == mock_scp_client_instance  # noqa: S101
            mock_create_ssh.assert_called_once_with(server=server, port=port, user=user, password=password)
            mock_ssh_client.get_transport.assert_called_once()
            mock_scp_client.assert_called_once_with(mock_transport)

    def test_create_ssh_client_success(self):
        """Test successful SSH client creation."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_client = Mock()

        with patch("paramiko.SSHClient", return_value=mock_client):
            # Act
            result = Transport._create_ssh_client(server, port, user, password)

            # Assert
            assert result == mock_client  # noqa: S101
            mock_client.load_system_host_keys.assert_called_once()
            mock_client.set_missing_host_key_policy.assert_called_once()
            mock_client.connect.assert_called_once_with(server, port, user, password)

    def test_create_ssh_client_connection_error(self):
        """Test SSH client creation with connection error."""
        # Arrange
        server = "invalid.server.com"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_client = Mock()
        mock_client.connect.side_effect = paramiko.AuthenticationException("Authentication failed")

        with patch("paramiko.SSHClient", return_value=mock_client), \
             pytest.raises(paramiko.AuthenticationException):
            Transport._create_ssh_client(server, port, user, password)

    def test_create_ssh_client_ssh_exception(self):
        """Test SSH client creation with SSH exception."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_client = Mock()
        mock_client.connect.side_effect = paramiko.SSHException("SSH connection failed")

        with patch("paramiko.SSHClient", return_value=mock_client), \
             pytest.raises(paramiko.SSHException):
            Transport._create_ssh_client(server, port, user, password)

    def test_create_ssh_client_socket_error(self):
        """Test SSH client creation with socket error."""
        # Arrange
        server = "unreachable.server.com"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_client = Mock()
        mock_client.connect.side_effect = OSError("Connection refused")

        with patch("paramiko.SSHClient", return_value=mock_client), \
             pytest.raises(OSError, match=".*"):  # noqa: PT011
            Transport._create_ssh_client(server, port, user, password)

    def test_init_with_different_ports(self):
        """Test Transport initialization with different ports."""
        # Arrange
        server = "test.server.com"
        user = "testuser"
        password = "testpass"  # noqa: S105
        ports = [22, 2222, 8022]

        for port in ports:
            mock_ssh_client = Mock()
            mock_transport = Mock()
            mock_ssh_client.get_transport.return_value = mock_transport

            with patch.object(Transport, "_create_ssh_client", return_value=mock_ssh_client) as mock_create_ssh, \
                 patch("scp.SCPClient"):
                # Act
                Transport(server, port, user, password)

                # Assert
                mock_create_ssh.assert_called_with(server=server, port=port, user=user, password=password)

    def test_init_with_empty_credentials(self):
        """Test Transport initialization with empty credentials."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = ""
        password = ""

        mock_ssh_client = Mock()
        mock_transport = Mock()
        mock_ssh_client.get_transport.return_value = mock_transport

        with patch.object(Transport, "_create_ssh_client", return_value=mock_ssh_client), \
             patch("scp.SCPClient"):
            # Act
            transport = Transport(server, port, user, password)

            # Assert
            assert transport.ssh == mock_ssh_client  # noqa: S101
            assert transport.scp is not None  # noqa: S101

    def test_create_ssh_client_with_special_characters(self):
        """Test SSH client creation with special characters in credentials."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "user@domain.com"
        password = "pass@word#123"  # noqa: S105

        mock_client = Mock()

        with patch("paramiko.SSHClient", return_value=mock_client):
            # Act
            result = Transport._create_ssh_client(server, port, user, password)

            # Assert
            assert result == mock_client  # noqa: S101
            mock_client.connect.assert_called_once_with(server, port, user, password)

    def test_scp_client_initialization(self):
        """Test that SCPClient is properly initialized with transport."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_ssh_client = Mock()
        mock_transport = Mock()
        mock_ssh_client.get_transport.return_value = mock_transport

        with patch.object(Transport, "_create_ssh_client", return_value=mock_ssh_client), \
             patch("shadowstep.terminal.transport.SCPClient") as mock_scp_client:
            # Act
            Transport(server, port, user, password)

            # Assert
            mock_scp_client.assert_called_once_with(mock_transport)

    def test_ssh_client_methods_called(self):
        """Test that all required SSH client methods are called during initialization."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_client = Mock()

        with patch("paramiko.SSHClient", return_value=mock_client):
            # Act
            Transport._create_ssh_client(server, port, user, password)

            # Assert
            mock_client.load_system_host_keys.assert_called_once()
            mock_client.set_missing_host_key_policy.assert_called_once()
            mock_client.connect.assert_called_once()

    def test_auto_add_policy_used(self):
        """Test that AutoAddPolicy is used for host key policy."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_client = Mock()

        with patch("paramiko.SSHClient", return_value=mock_client), \
             patch("paramiko.AutoAddPolicy") as mock_auto_add_policy:
            # Act
            Transport._create_ssh_client(server, port, user, password)

            # Assert
            mock_client.set_missing_host_key_policy.assert_called_once_with(mock_auto_add_policy.return_value)
