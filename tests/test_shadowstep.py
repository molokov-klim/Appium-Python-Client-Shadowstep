import os
import subprocess
import time

from shadowstep.shadowstep import Shadowstep


class TestShadowstep:
    """
    A class to test various functionalities of the Shadowstep application.
    """

    def test_get_element(self, app: Shadowstep) -> None:
        """
        Test retrieving an element from the Shadowstep application.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.

        Asserts:
            Asserts that the locator of the retrieved element matches the expected locator.
        """
        element = app.get_element(locator={'content-desc': 'Phone'})
        assert element.locator == {'content-desc': 'Phone'}

