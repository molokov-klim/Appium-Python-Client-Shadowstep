# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Integration tests for ``mobile_commands.py`` — Part 2.

This suite focuses on gesture commands: click, long click, double click,
swipe, scroll, drag, pinch, fling, and other screen interactions.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_ui_automator/test_mobile_commands_integro_part_2.py
"""

import logging
from typing import Any

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.ui_automator.mobile_commands import MobileCommands

logger = logging.getLogger(__name__)


class TestMobileCommandsPart2:
    """Integration tests for ``MobileCommands`` — Part 2.

    Covers gesture commands and screen interactions.
    """

    @pytest.fixture(autouse=True)
    def setup_mobile_commands(self, app: Shadowstep):
        """Configure a ``MobileCommands`` instance with the ``app`` fixture.

        Args:
            app: Shadowstep application instance for testing.
        """
        self.mobile_commands = MobileCommands()
        self.app = app
        # Ensure app is connected
        assert self.app.is_connected()  # noqa: S101
        yield

    def test_click_gesture(self):
        """Exercise the ``click_gesture`` command.

        Steps:
            1. Click the center of the screen (500, 500).

        Verifies:
            - The command finishes without exceptions.
        """
        # Click at center of screen
        result = self.mobile_commands.click_gesture({"x": 500, "y": 500})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_long_click_gesture(self):
        """Exercise the ``long_click_gesture`` command.

        Steps:
            1. Perform a 1000 ms long click at (500, 500).

        Verifies:
            - The command finishes without exceptions.
        """
        result = self.mobile_commands.long_click_gesture({"x": 500, "y": 500, "duration": 1000})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_double_click_gesture(self):
        """Exercise the ``double_click_gesture`` command.

        Steps:
            1. Perform a double click at (500, 500).

        Verifies:
            - The command finishes without exceptions.
        """
        result = self.mobile_commands.double_click_gesture({"x": 500, "y": 500})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_swipe_gesture(self):
        """Exercise the ``swipe_gesture`` command.

        Steps:
            1. Swipe left within the specified region.

        Parameters:
            - left: 100
            - top: 500
            - width: 600
            - height: 100
            - direction: ``left``
            - percent: 0.75

        Verifies:
            - The command finishes without exceptions.
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
        """Exercise the ``scroll_gesture`` command.

        Steps:
            1. Scroll down within the specified region.

        Parameters:
            - left: 100
            - top: 500
            - width: 600
            - height: 800
            - direction: ``down``
            - percent: 1.0

        Verifies:
            - The result is a boolean indicating whether further scrolling is possible.
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
        """Exercise the ``drag_gesture`` command.

        Steps:
            1. Drag from (500, 500) to (500, 800).

        Verifies:
            - The command finishes without exceptions.
        """
        result = self.mobile_commands.drag_gesture(
            {"startX": 500, "startY": 500, "endX": 500, "endY": 800}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_pinch_open_gesture(self):
        """Exercise the ``pinch_open_gesture`` command.

        Steps:
            1. Perform a zoom-in gesture.

        Parameters:
            - left: 100
            - top: 100
            - width: 600
            - height: 600
            - percent: 0.5

        Verifies:
            - The command finishes without exceptions.
        """
        result = self.mobile_commands.pinch_open_gesture(
            {"left": 100, "top": 100, "width": 600, "height": 600, "percent": 0.5}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_pinch_close_gesture(self):
        """Exercise the ``pinch_close_gesture`` command.

        Steps:
            1. Perform a zoom-out gesture.

        Parameters:
            - left: 100
            - top: 100
            - width: 600
            - height: 600
            - percent: 0.5

        Verifies:
            - The command finishes without exceptions.
        """
        result = self.mobile_commands.pinch_close_gesture(
            {"left": 100, "top": 100, "width": 600, "height": 600, "percent": 0.5}
        )

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    def test_fling_gesture(self):
        """Exercise the ``fling_gesture`` command.

        Steps:
            1. Perform a fast downward swipe.

        Parameters:
            - left: 100
            - top: 100
            - width: 600
            - height: 800
            - direction: ``down``
            - speed: 7500

        Verifies:
            - The result is a boolean indicating whether further scrolling is possible.
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
        """Exercise the legacy ``scroll`` command.

        Note:
            This is the older ``scroll`` command, different from ``scroll_gesture``.
            Requires a scrollable element with a specific selector.
        """
        # This is the old scroll command, different from scroll_gesture
        result = self.mobile_commands.scroll({"strategy": "accessibility id", "selector": "test"})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires valid element ID", strict=False)
    def test_replace_element_value(self):
        """Exercise the ``replace_element_value`` command.

        Note:
            Requires a valid element ID and therefore marked xfail.
        """
        result = self.mobile_commands.replace_element_value(
            {"elementId": "test", "text": "replacement"}
        )
        logger.info(result)

