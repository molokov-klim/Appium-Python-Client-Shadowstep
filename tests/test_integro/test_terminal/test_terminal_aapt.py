# ruff: noqa
# pyright: ignore
"""
Integration tests for shadowstep.terminal.aapt module.

These tests verify real AAPT operations with actual APK files
using the Android Asset Packaging Tool.
"""

import os
import tempfile
from pathlib import Path

import pytest

from shadowstep.terminal.aapt import Aapt


class TestAaptIntegration:
    """Integration test cases for Aapt class."""
