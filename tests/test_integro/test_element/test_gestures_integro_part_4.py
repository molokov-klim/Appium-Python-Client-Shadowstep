# ruff: noqa
# pyright: ignore
import time

from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_gestures_integro_part_4.py
"""


class TestElementGesturesPart4:
    """Tests for special element interaction gestures.

    This class contains tests for special element interaction gestures,
    including zoom and unzoom operations.
    """

    def test_zoom(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Test element zoom in.

        Verifies correct execution of zoom in operation
        on "Network & internet" element.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
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
        """Test element zoom out.

        Verifies correct execution of zoom out operation
        on "Network & internet" element.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_network.unzoom()
        time.sleep(3)
