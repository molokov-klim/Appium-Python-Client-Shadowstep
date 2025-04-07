import os
import subprocess
import time

from icecream import ic

from shadowstep.element.element import Element
from shadowstep.shadowstep import Shadowstep


class TestElements:
    """
    A class to test element interactions within the Shadowstep application.
    """

    def test_get_elements_valid_locator(self, app: Shadowstep):
        elements = app.get_elements(locator={'class': 'android.widget.TextView'})
        assert elements is not None
        assert len(elements) > 0

    def test_get_elements_repeated_search(self, app: Shadowstep):
        elements1 = app.get_elements(locator={'class': 'android.widget.TextView'})
        elements2 = app.get_elements(locator={'class': 'android.widget.TextView'})
        assert elements1 == elements2

    def test_get_elements_invalid_locator(self, app: Shadowstep):
        elements = app.get_elements(locator={'class': 'InvalidClass'})
        assert elements is None

    def test_get_elements_disconnected(self, app: Shadowstep):
        app.disconnect()
        elements = app.get_elements(locator={'class': 'android.widget.TextView'})
        app.connect()
        assert elements is None
