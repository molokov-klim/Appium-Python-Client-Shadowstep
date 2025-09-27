# shadowstep/utils/command_line_parser.py
"""Command line argument parser for Shadowstep framework.

This module provides utility functions for parsing command line arguments
including device UDID, model, environment settings, and other configuration
parameters used by the Shadowstep automation framework.
"""

import logging
import os
import sys
from pathlib import Path

from shadowstep.utils.utils import get_current_func_name

logger = logging.getLogger(__name__)


def udid():
    """Extract UDID from command line arguments.

    Returns:
        str: The UDID value from --udid argument, empty string if not found.

    """
    logger.debug(f"{get_current_func_name()}")
    var = ""
    for i in sys.argv[1:]:
        if "--udid" in i:
            var = i.split("=")[1]
            break
    return var


def model():
    """Extract device model from command line arguments.

    Returns:
        str: The model value from --model argument, empty string if not found.

    """
    logger.debug(f"{get_current_func_name()}")
    var = ""
    for i in sys.argv[1:]:
        if "--model" in i:
            var = i.split("=")[1]
            break
    return var


def detailed():
    """Extract detailed flag from command line arguments.

    Returns:
        str: The detailed value from --detailed argument, empty string if not found.

    """
    logger.debug(f"{get_current_func_name()}")
    var = ""
    for i in sys.argv[1:]:
        if "--detailed" in i:
            var = i.split("=")[1]
            break
    return var


def chat_id():
    """Extract chat ID from command line arguments.

    Returns:
        str: The chat ID value from --chat_id argument, empty string if not found.

    """
    logger.debug(f"{get_current_func_name()}")
    var = ""
    for i in sys.argv[1:]:
        if "--chat_id" in i:
            var = i.split("=")[1]
            break
    return var


def env():
    """Extract environment setting from command line arguments.

    Returns:
        str: The environment value from --env argument, empty string if not found.

    """
    logger.debug(f"{get_current_func_name()}")
    var = ""
    for i in sys.argv[1:]:
        if "--env" in i:
            var = i.split("=")[1]
            break
    return var


def root_dir():
    """Extract root directory path from command line arguments.

    Returns:
        str: The absolute path from --rootdir argument, empty string if not found.

    """
    logger.debug(f"{get_current_func_name()}")
    root_dir_path = ""
    for i in sys.argv[1:]:
        if "--rootdir" in i:
            root_dir_path = i.split("=")[1]
            break
    return str(Path(root_dir_path).resolve())
