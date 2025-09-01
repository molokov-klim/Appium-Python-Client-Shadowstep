from shadowstep.element.element import Element
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
        element = app.get_element(locator={"content-desc": "Phone"},
                                  timeout=29,
                                  poll_frequency=0.7,
                                  ignored_exceptions=[TimeoutError],
                                  contains=True)
        assert element.locator == {"content-desc": "Phone"}
        assert isinstance(element, Element)
        assert element.driver is None
        assert element.base is not None
        assert element.timeout == 29
        assert element.poll_frequency == 0.7
        assert element.ignored_exceptions == [TimeoutError]
        assert element.contains is True
        element.tap()
        assert element.driver is not None

    def test_find_and_get_element(self, app: Shadowstep, android_settings_open_close: None):
        el = app.find_and_get_element({"text": "System"})
        assert el.get_attribute("text") == "System"
