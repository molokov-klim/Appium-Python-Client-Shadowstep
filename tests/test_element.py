import os
import subprocess
import time

from shadowstep.shadowstep import Shadowstep


class TestElement:
    """
    A class to test element interactions within the Shadowstep application.
    """

    def test_tap(self, app: Shadowstep) -> None:
        """
        Test tapping on an element in the Shadowstep application.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.

        Asserts:
            Asserts that the response from the adb command contains 'com.android.dialer'
            after tapping on the element.
        """
        element = app.get_element(locator={'content-desc': 'Phone'})
        element.tap()
        time.sleep(3)
        response = str(subprocess.check_output('adb shell "dumpsys window windows | grep -E \'mSurface\'"'))
        assert "com.android.dialer" in response

    def test_get_element_valid_locator(self, app: Shadowstep):
        element = app.get_element(locator={'content-desc': 'Phone'})
        assert element is not None

    def test_get_element_repeated_search(self, app: Shadowstep):
        element1 = app.get_element(locator={'content-desc': 'Phone'})
        element2 = app.get_element(locator={'content-desc': 'Phone'})
        assert element1 is not None
        assert element2 is not None
        assert element1.locator == element2.locator

    def test_get_element_disconnected(self, app: Shadowstep):
        app.disconnect()
        element = app.get_element(locator={'content-desc': 'Phone'})
        element.tap()
        assert element is None

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
        assert elements is None







