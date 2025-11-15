# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""KeyEvent interface for Shadowstep framework.

This module provides the KeyEvent class for executing ADB commands
through Appium server, see:
https://developer.android.com/reference/android/view/KeyEvent
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shadowstep.terminal import Terminal  # noqa: TC004

# Configure the root logger (basic configuration)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class KeyEvent:
    """Handles all key events from Android KeyEvent API.

    Provides methods for all Android key codes:
    - Navigation keys (DPAD_UP, DPAD_DOWN, etc.)
    - System keys (HOME, BACK, MENU, etc.)
    - Media keys (VOLUME_UP, VOLUME_DOWN, etc.)
    - Text input keys (ENTER, BACKSPACE, DELETE, etc.)
    - And all other keys from KeyEvent constants.
    """

    def __init__(self, terminal: Terminal) -> None:
        """Initialize the TerminalCredentialsError.

        Args:
            terminal: Terminal instance.

        """
        self._terminal = terminal

    def press_home(self) -> bool:
        """Simulate pressing the home button on the device.

        :return: True if the home button press was successfully simulated, False otherwise.
        """
        try:
            self._terminal.input_keycode(keycode="KEYCODE_HOME")
        except KeyError:
            logger.exception("shadowstep_terminal.press_home()")
            return False
        else:
            return True
