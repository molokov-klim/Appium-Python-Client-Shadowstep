# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Terminal and command execution utilities for the Shadowstep framework.

This module provides functionality for executing terminal commands, managing
ADB connections, and handling transport protocols used in mobile automation
testing.

Classes:
    Adb: Android Debug Bridge command execution and device management.
    Terminal: General terminal command execution utilities.
    Transport: Transport protocol handling for device communication.
"""

from shadowstep.terminal.adb import Adb
from shadowstep.terminal.terminal import Terminal
from shadowstep.terminal.transport import Transport

__all__ = [
    "Adb",
    "Terminal",
    "Transport",
]
