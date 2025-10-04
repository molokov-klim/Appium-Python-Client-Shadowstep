# ruff: noqa
# pyright: ignore
"""
Tests for shadowstep.terminal.transport module.
"""

from unittest.mock import Mock, patch

import paramiko
import pytest

from shadowstep.terminal.transport import Transport


class TestTransport:
    """Test cases for Transport class."""

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_transport_with_none_ssh_client(self):
        """Test Transport initialization when SSH client creation fails."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        with patch.object(Transport, "_create_ssh_client", side_effect=Exception("SSH connection failed")), \
             pytest.raises(Exception, match="SSH connection failed"):
            # Act
            Transport(server, port, user, password)

    @pytest.mark.unit
    def test_transport_with_none_transport(self):
        """Test Transport initialization when get_transport returns None."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_ssh_client = Mock()
        mock_ssh_client.get_transport.return_value = None

        with patch.object(Transport, "_create_ssh_client", return_value=mock_ssh_client), \
             patch("shadowstep.terminal.transport.SCPClient") as mock_scp_client:
            # Act
            transport = Transport(server, port, user, password)

            # Assert
            assert transport.ssh == mock_ssh_client  # noqa: S101
            mock_scp_client.assert_called_once_with(None)

    @pytest.mark.unit
    def test_create_ssh_client_with_unicode_credentials(self):
        """Test SSH client creation with unicode characters in credentials."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "тест_пользователь"
        password = "пароль123"  # noqa: S105

        mock_client = Mock()

        with patch("paramiko.SSHClient", return_value=mock_client):
            # Act
            result = Transport._create_ssh_client(server, port, user, password)

            # Assert
            assert result == mock_client  # noqa: S101
            mock_client.connect.assert_called_once_with(server, port, user, password)

    @pytest.mark.unit
    def test_create_ssh_client_with_very_long_credentials(self):
        """Test SSH client creation with very long credentials."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "a" * 1000
        password = "b" * 1000  # noqa: S105

        mock_client = Mock()

        with patch("paramiko.SSHClient", return_value=mock_client):
            # Act
            result = Transport._create_ssh_client(server, port, user, password)

            # Assert
            assert result == mock_client  # noqa: S101
            mock_client.connect.assert_called_once_with(server, port, user, password)

    @pytest.mark.unit
    def test_create_ssh_client_with_numeric_credentials(self):
        """Test SSH client creation with numeric credentials."""
        # Arrange
        server = "192.168.1.1"
        port = 22
        user = "12345"
        password = "67890"  # noqa: S105

        mock_client = Mock()

        with patch("paramiko.SSHClient", return_value=mock_client):
            # Act
            result = Transport._create_ssh_client(server, port, user, password)

            # Assert
            assert result == mock_client  # noqa: S101
            mock_client.connect.assert_called_once_with(server, port, user, password)

    @pytest.mark.unit
    def test_create_ssh_client_with_whitespace_credentials(self):
        """Test SSH client creation with whitespace in credentials."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = " test user "
        password = " test pass "  # noqa: S105

        mock_client = Mock()

        with patch("paramiko.SSHClient", return_value=mock_client):
            # Act
            result = Transport._create_ssh_client(server, port, user, password)

            # Assert
            assert result == mock_client  # noqa: S101
            mock_client.connect.assert_called_once_with(server, port, user, password)

    @pytest.mark.unit
    def test_transport_attributes_after_init(self):
        """Test that Transport attributes are properly set after initialization."""
        # Arrange
        server = "test.server.com"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_ssh_client = Mock()
        mock_transport = Mock()
        mock_ssh_client.get_transport.return_value = mock_transport
        mock_scp_client_instance = Mock()

        with patch.object(Transport, "_create_ssh_client", return_value=mock_ssh_client), \
             patch("shadowstep.terminal.transport.SCPClient", return_value=mock_scp_client_instance):
            # Act
            transport = Transport(server, port, user, password)

            # Assert
            assert hasattr(transport, 'ssh')  # noqa: S101
            assert hasattr(transport, 'scp')  # noqa: S101
            assert transport.ssh is not None  # noqa: S101
            assert transport.scp is not None  # noqa: S101

    @pytest.mark.unit
    def test_create_ssh_client_method_calls_order(self):
        """Test that SSH client methods are called in the correct order."""
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
            # Verify the order of method calls
            calls = mock_client.method_calls
            assert len(calls) == 3  # noqa: S101
            assert calls[0][0] == 'load_system_host_keys'
            assert calls[1][0] == 'set_missing_host_key_policy'
            assert calls[2][0] == 'connect'

    @pytest.mark.unit
    def test_create_ssh_client_with_ipv6_server(self):
        """Test SSH client creation with IPv6 server address."""
        # Arrange
        server = "2001:db8::1"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_client = Mock()

        with patch("paramiko.SSHClient", return_value=mock_client):
            # Act
            result = Transport._create_ssh_client(server, port, user, password)

            # Assert
            assert result == mock_client  # noqa: S101
            mock_client.connect.assert_called_once_with(server, port, user, password)

    @pytest.mark.unit
    def test_create_ssh_client_with_localhost(self):
        """Test SSH client creation with localhost server."""
        # Arrange
        server = "localhost"
        port = 22
        user = "testuser"
        password = "testpass"  # noqa: S105

        mock_client = Mock()

        with patch("paramiko.SSHClient", return_value=mock_client):
            # Act
            result = Transport._create_ssh_client(server, port, user, password)

            # Assert
            assert result == mock_client  # noqa: S101
            mock_client.connect.assert_called_once_with(server, port, user, password)
