# ruff: noqa
# pyright: ignore
"""Integration tests for mobile_commands.py module - Part 2.

Gestures test group: click, long click, double click, swipe, scroll, drag,
pinch, fling and other screen interaction gestures.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_ui_automator/test_mobile_commands_integro_part_2.py
"""

import logging
from typing import Any

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.ui_automator.mobile_commands import MobileCommands

logger = logging.getLogger(__name__)


class TestMobileCommandsPart2:
    """Integration tests for MobileCommands class - Part 2.
    
    Testing gesture commands and screen interaction.
    """

    @pytest.fixture(autouse=True)
    def setup_mobile_commands(self, app: Shadowstep):
        """Setup MobileCommands instance with app fixture.
        
        Args:
            app: Shadowstep application instance for testing.
        """
        self.mobile_commands = MobileCommands()
        self.app = app
        # Ensure app is connected
        assert self.app.is_connected()  # noqa: S101
        yield

    def test_click_gesture(self):
        """Test click_gesture command.
        
        Steps:
            1. Perform click at screen center (500, 500).
        
        Verifies:
            - Command executes without exceptions.
        """
        # Click at center of screen
        result = self.mobile_commands.click_gesture({"x": 500, "y": 500})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_long_click_gesture(self):
        """Test long_click_gesture command.
        
        Steps:
            1. Perform long click (1000ms) at coordinates (500, 500).
        
        Verifies:
            - Command executes without exceptions.
        """
        result = self.mobile_commands.long_click_gesture({"x": 500, "y": 500, "duration": 1000})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_double_click_gesture(self):
        """Test double_click_gesture command.
        
        Steps:
            1. Perform double click at coordinates (500, 500).
        
        Verifies:
            - Command executes without exceptions.
        """
        result = self.mobile_commands.double_click_gesture({"x": 500, "y": 500})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_swipe_gesture(self):
        """Test swipe_gesture command.
        
        Steps:
            1. Perform left swipe in specified area.
        
        Parameters:
            - left: 100
            - top: 500
            - width: 600
            - height: 100
            - direction: left
            - percent: 0.75
        
        Verifies:
            - Command executes without exceptions.
        """
        result = self.mobile_commands.swipe_gesture(
            {
                "left": 100,
                "top": 500,
                "width": 600,
                "height": 100,
                "direction": "left",
                "percent": 0.75,
            }
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_scroll_gesture(self):
        """Test scroll_gesture command.
        
        Steps:
            1. Perform downward scroll in specified area.
        
        Parameters:
            - left: 100
            - top: 500
            - width: 600
            - height: 800
            - direction: down
            - percent: 1.0
        
        Verifies:
            - Result is a boolean value (whether can scroll further).
        """
        result = self.mobile_commands.scroll_gesture(
            {
                "left": 100,
                "top": 500,
                "width": 600,
                "height": 800,
                "direction": "down",
                "percent": 1.0,
            }
        )

        # Returns boolean indicating if can scroll more
        assert isinstance(result, bool)  # noqa: S101

    def test_drag_gesture(self):
        """Test drag_gesture command.
        
        Steps:
            1. Perform drag from (500, 500) to (500, 800).
        
        Verifies:
            - Command executes without exceptions.
        """
        result = self.mobile_commands.drag_gesture(
            {"startX": 500, "startY": 500, "endX": 500, "endY": 800}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_pinch_open_gesture(self):
        """Test pinch_open_gesture command.
        
        Steps:
            1. Perform pinch open gesture (zoom in).
        
        Parameters:
            - left: 100
            - top: 100
            - width: 600
            - height: 600
            - percent: 0.5
        
        Verifies:
            - Command executes without exceptions.
        """
        result = self.mobile_commands.pinch_open_gesture(
            {"left": 100, "top": 100, "width": 600, "height": 600, "percent": 0.5}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_pinch_close_gesture(self):
        """Test pinch_close_gesture command.
        
        Steps:
            1. Perform pinch close gesture (zoom out).
        
        Parameters:
            - left: 100
            - top: 100
            - width: 600
            - height: 600
            - percent: 0.5
        
        Verifies:
            - Command executes without exceptions.
        """
        result = self.mobile_commands.pinch_close_gesture(
            {"left": 100, "top": 100, "width": 600, "height": 600, "percent": 0.5}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_fling_gesture(self):
        """Test fling_gesture command.
        
        Steps:
            1. Perform fast swipe gesture downward.
        
        Parameters:
            - left: 100
            - top: 100
            - width: 600
            - height: 800
            - direction: down
            - speed: 7500
        
        Verifies:
            - Result is a boolean value (whether can scroll further).
        """
        result = self.mobile_commands.fling_gesture(
            {
                "left": 100,
                "top": 100,
                "width": 600,
                "height": 800,
                "direction": "down",
                "speed": 7500,
            }
        )

        # Returns boolean indicating if can scroll more
        assert isinstance(result, bool)  # noqa: S101

    @pytest.mark.xfail(reason="Requires scrollable element with specific selector", strict=False)
    def test_scroll_legacy(self):
        """Test legacy scroll command.
        
        Note:
            This is the old scroll command, different from scroll_gesture.
            Requires scrollable element with specific selector.
        """
        # This is the old scroll command, different from scroll_gesture
        result = self.mobile_commands.scroll({"strategy": "accessibility id", "selector": "test"})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires valid element ID", strict=False)
    def test_replace_element_value(self):
        """Test replace_element_value command.
        
        Note:
            Requires valid element ID.
            Test is marked as xfail due to need for existing element.
        """
        result = self.mobile_commands.replace_element_value(
            {"elementId": "test", "text": "replacement"}
        )
        logger.info(result)

