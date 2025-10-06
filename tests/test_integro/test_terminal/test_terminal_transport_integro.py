# ruff: noqa
# pyright: ignore
"""
Integration tests for shadowstep.terminal.transport module.

These tests verify real SSH and SCP operations with actual servers.
"""

import os
import tempfile
from pathlib import Path

import paramiko
import pytest

from shadowstep.terminal.transport import Transport


class TestTransportIntegration:
    """Integration test cases for Transport class."""
