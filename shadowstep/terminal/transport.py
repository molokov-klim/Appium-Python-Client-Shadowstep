# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""SSH transport module for Shadowstep framework.

This module provides the Transport class for establishing SSH connections
and file transfer capabilities using paramiko and SCP libraries.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

import paramiko
from scp import SCPClient  # type: ignore[reportMissingTypeStubs]
from typing_extensions import Self

if TYPE_CHECKING:
    import types

# Configure the root logger (basic configuration)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Transport:
    """Allows you to connect to the server and execute terminal commands via ssh.

    And also copy files to the server and from server.
    Uses the paramiko and scp libraries for this

    This class include to attribute of Shadowstep class and allow use transport, like:
    app.transport.ssh.some_paramiko_method
    app.transport.scp.some_scp_method
    """

    def __init__(self, server: str, port: int, user: str, password: str) -> None:
        """Initialize the Transport.

        Args:
            server: SSH server hostname or IP address.
            port: SSH server port number.
            user: SSH username for authentication.
            password: SSH password for authentication.

        """
        self.ssh = self._create_ssh_client(server=server, port=port, user=user, password=password)
        self.scp = SCPClient(cast("paramiko.Transport", self.ssh.get_transport()))

    def __enter__(self) -> Self:
        """Return the current instance when entering the context manager.

        Returns:
            Self: The current instance.

        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None:
        """Close the connections when exiting the context manager.

        Args:
            exc_type: Exception type, if raised.
            exc_val: Exception value, if raised.
            exc_tb: Exception traceback object.

        Returns:
            bool | None: None to use the default exception handling.

        """
        self.close()
        return None

    def close(self) -> None:
        """Close the SSH and SCP connections.

        Sequentially closes the SCP client and SSH connection, if available.

        """
        if self.scp:
            self.scp.close()
        if self.ssh:
            self.ssh.close()

    @staticmethod
    def _create_ssh_client(server: str, port: int, user: str, password: str) -> paramiko.SSHClient:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # noqa: S507
        client.connect(server, port, user, password)
        return client
