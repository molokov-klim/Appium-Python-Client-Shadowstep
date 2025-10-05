# ruff: noqa
# pyright: ignore
"""
Integration tests for mobile_commands.py module.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_mobile_commands.py
"""
import pytest
from unittest.mock import Mock, patch

from shadowstep.mobile_commands import MobileCommands
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException


class TestMobileCommands:
    """Integration tests for MobileCommands class."""
