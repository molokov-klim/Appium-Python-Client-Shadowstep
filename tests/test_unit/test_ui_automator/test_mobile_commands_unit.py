# ruff: noqa
# pyright: ignore
"""Tests for MobileCommands class."""

import pytest
from unittest.mock import Mock, patch
from ui_automator.mobile_commands import MobileCommands
from shadowstep.shadowstep import Shadowstep


class TestMobileCommands:
    """Test cases for MobileCommands class."""
