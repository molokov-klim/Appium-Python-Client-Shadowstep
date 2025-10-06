# ruff: noqa
# pyright: ignore
"""
Integration tests for shadowstep.terminal.terminal module.

These tests verify real Terminal operations with actual mobile devices
through Appium server and SSH transport.
"""

import base64
import os
import tempfile
from pathlib import Path

import pytest
from selenium.common import InvalidSessionIdException, NoSuchDriverException

from shadowstep.terminal.terminal import NotProvideCredentialsError, Terminal, AdbShellError


class TestTerminalIntegration:
    """Integration test cases for Terminal class."""
