# ruff: noqa
# pyright: ignore
import time

from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_gestures_integro_part_4.py
"""


class TestElementGesturesPart4:
    """Special gesture interaction tests.

    This class covers zoom and unzoom gestures for specific elements.
    """

    def test_zoom(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Test zooming in on an element.

        Ensures the zoom operation works on ``Network & internet`` element.

        Args:
            app: Shadowstep instance used for interaction.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_network.zoom()
        time.sleep(3)

    def test_unzoom(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Test zooming out from an element.

        Ensures the unzoom operation works on ``Network & internet`` element.

        Args:
            app: Shadowstep instance used for interaction.
            android_settings_open_close: Fixture that opens and closes Android settings.
        """
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_network.unzoom()
        time.sleep(3)
