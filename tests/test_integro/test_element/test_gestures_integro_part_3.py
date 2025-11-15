# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
import logging
import time

import pytest

from shadowstep.element.element import Element
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_gestures_integro_part_3.py
"""
LOCATOR_CONNECTED_DEVICES = {"text": "Connected devices"}

logger = logging.getLogger(__name__)


class TestElementGesturesPart3:
    """Swipe gesture interaction tests.

    This class exercises swipe gestures in various directions and with
    different configurations.
    """

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_swipe_directions(
        self, app: Shadowstep, direction: str, android_settings_open_close: None
    ):
        """Test swiping in various directions.

        Ensures the swipe runs correctly on ``Connected devices`` with the
        desired percent and speed settings.

        Args:
            app: Shadowstep instance used for interaction.
            direction: Swipe direction (``up``, ``down``, ``left``, ``right``).
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.swipe(direction=direction, percent=0.5, speed=3000)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_up(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Test swiping upward.

        Verifies the upward swipe on ``Network & internet`` with given
        parameters behaves correctly.

        Args:
            app: Shadowstep instance used for interaction.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_up(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_down(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Test swiping downward.

        Verifies the downward swipe on ``Network & internet`` with specified
        parameters behaves correctly.

        Args:
            app: Shadowstep instance used for interaction.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_down(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_left(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Test swiping left.

        Verifies the leftward swipe on ``Network & internet`` with specified
        parameters behaves correctly.

        Args:
            app: Shadowstep instance used for interaction.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_left(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    def test_swipe_right(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Test swiping right.

        Verifies the rightward swipe on ``Network & internet`` with specified
        parameters behaves correctly.

        Args:
            app: Shadowstep instance used for interaction.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_right(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_fling_directions(
        self, app: Shadowstep, direction: str, android_settings_open_close: None
    ):
        """Test fling gestures in multiple directions.

        Ensures the fling executes correctly on ``Connected devices`` with the
        requested direction and speed.

        Args:
            app: Shadowstep instance used for interaction.
            direction: Fling direction (``up``, ``down``, ``left``, ``right``).
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.fling(speed=3000, direction=direction)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101
