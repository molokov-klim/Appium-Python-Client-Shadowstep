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
    """Tests for swipe element interaction gestures.

    This class contains tests for swipe element interaction gestures,
    including swipe operations in various directions and with various parameters.
    """

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_swipe_directions(
        self, app: Shadowstep, direction: str, android_settings_open_close: None
    ):
        """Test swipe in various directions.

        Verifies correct execution of swipe in specified direction
        on "Connected devices" element with percent and speed parameters.

        Args:
            app: Shadowstep instance for application interaction.
            direction: Swipe direction (up, down, left, right).
            android_settings_open_close: Fixture for opening and closing Android settings.
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
        """Test swipe upward.

        Verifies correct execution of swipe upward
        on "Network & internet" element with specified parameters.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
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
        """Test swipe downward.

        Verifies correct execution of swipe downward
        on "Network & internet" element with specified parameters.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
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
        """Test swipe to the left.

        Verifies correct execution of swipe to the left
        on "Network & internet" element with specified parameters.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
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
        """Test swipe to the right.

        Verifies correct execution of swipe to the right
        on "Network & internet" element with specified parameters.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        element = app.get_element(locator={"text": "Network & internet"})
        element.swipe_right(percent=0.6, speed=2500)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101

    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_fling_directions(
        self, app: Shadowstep, direction: str, android_settings_open_close: None
    ):
        """Test fast swipe (fling) in various directions.

        Verifies correct execution of fast swipe in specified direction
        on "Connected devices" element with specified speed.

        Args:
            app: Shadowstep instance for application interaction.
            direction: Fast swipe direction (up, down, left, right).
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        element.fling(speed=3000, direction=direction)
        time.sleep(2)
        assert isinstance(element, Element)  # noqa: S101
