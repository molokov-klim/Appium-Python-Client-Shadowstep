# ruff: noqa
# pyright: ignore
import logging
import time

import pytest

from shadowstep.element.element import Element
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_gestures_integro_part_2.py
"""
LOCATOR_CONNECTED_DEVICES = {"text": "Connected devices"}
LOCATOR_RECYCLER = {"resource-id": "com.android.settings:id/main_content_scrollable_container"}
LOCATOR_BOTTOM_ELEMENT = {"textContains": "About"}

logger = logging.getLogger(__name__)


class TestElementGesturesPart2:
    """Tests for advanced element interaction gestures.

    This class contains tests for advanced element interaction gestures,
    including drag, fling and scroll operations with various parameters.
    """

    def test_drag(self, app: Shadowstep, android_settings_open_close: None):
        """Test element dragging.

        Verifies correct execution of drag operation for
        "Connected devices" element to new coordinates.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        gallery = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        center_x1, center_y1 = gallery.get_center()
        gallery.drag(end_x=center_x1 - 500, end_y=center_y1 - 500)
        assert gallery.get_center() != center_x1, center_y1

    def test_fling(self, app: Shadowstep, android_settings_open_close: None):
        """Test fast swipe (fling) downward.

        Verifies correct execution of fast swipe downward
        on "Connected devices" element with element bounds changing.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        element = app.get_element(locator=LOCATOR_CONNECTED_DEVICES)
        bounds_1 = element.bounds
        element.fling_down(speed=3000)
        bounds_2 = element.bounds
        assert bounds_1 != bounds_2

    def test_scroll(self, app: Shadowstep, android_settings_open_close: None):
        """Test scrolling container downward.

        Verifies correct execution of scrolling settings container
        downward until "About" element appears.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        logger.info(app.driver.page_source)
        logger.info("+++++++++++++++++++")
        logger.info("+++++++++++++++++++")
        logger.info("+++++++++++++++++++")
        logger.info("+++++++++++++++++++")

        while settings_recycler.scroll_down(percent=10, speed=2000, return_bool=True):
            time.sleep(1)
        logger.info(app.driver.page_source)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    def test_scroll_to_element_not_found(self, app: Shadowstep, android_settings_open_close: None):
        """Test scrolling to non-existent element.

        Verifies correct exception handling when attempting
        to scroll to non-existent element.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        container = app.get_element({"text": "not existing element"})
        with pytest.raises(ShadowstepElementException):
            container.scroll_to_element(locator={"text": "Element That Does Not Exist"})

    def test_scroll_to_bottom(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Test scrolling to bottom of container.

        Verifies correct execution of scrolling to bottom of
        settings container and appearance of "About" element.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_bottom()
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101

    def test_scroll_to_top(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Test scrolling to top of container.

        Verifies correct execution of scrolling to top of
        settings container after scrolling down.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        settings_recycler = app.get_element(locator=LOCATOR_RECYCLER)
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_bottom()
        time.sleep(3)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101
        settings_recycler.scroll_to_top()
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101

    def test_scroll_to_element(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ):
        """Test scrolling to specific element.

        Verifies correct execution of scrolling to specific element
        in settings container.

        Args:
            app: Shadowstep instance for application interaction.
            android_settings_open_close: Fixture for opening and closing Android settings.
        """
        settings_recycler = app.get_element(
            locator={"resource-id": "com.android.settings:id/settings_homepage_container"}
        )
        settings_network = app.get_element(
            locator={"text": "Network & internet", "resource-id": "android:id/title"}
        )
        settings_about_phone = app.get_element(locator=LOCATOR_BOTTOM_ELEMENT)
        settings_recycler.scroll_to_element(locator=settings_about_phone.locator)  # type: ignore
        time.sleep(3)
        assert "About" in settings_about_phone.get_attribute("text")  # noqa: S101
        settings_recycler.scroll_to_element(locator=settings_network)
        time.sleep(3)
        assert "Network & internet" in settings_network.get_attribute("text")  # noqa: S101
