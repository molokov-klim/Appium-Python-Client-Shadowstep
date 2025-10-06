# ruff: noqa
# pyright: ignore
"""
Integration tests for shadowstep.terminal.adb module.

These tests verify real ADB operations with actual Android devices
through Android Debug Bridge.
"""

import os
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

from shadowstep.shadowstep import Shadowstep


class TestAdbIntegration:
    """Integration test cases for Adb class."""
