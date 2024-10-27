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
