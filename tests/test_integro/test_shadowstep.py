from shadowstep.element.element import Element
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/base/test_shadowstep.py
"""


class TestShadowstep:
    """
    A class to test various functionalities of the Shadowstep application.
    """

    def test_get_element(self, app: Shadowstep, stability: None) -> None:
        """
        Test retrieving an element from the Shadowstep application.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.

        Asserts:
            Asserts that the locator of the retrieved element matches the expected locator.
        """
        element = app.get_element(
            locator={"class": "android.widget.FrameLayout"},
            timeout=29,
            poll_frequency=0.7,
            ignored_exceptions=[TimeoutError],
        )
        assert element.locator == {"class": "android.widget.FrameLayout"}  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101
        assert element.driver is None  # noqa: S101
        assert element.shadowstep is not None  # noqa: S101
        assert element.timeout == 29  # noqa: S101
        assert element.poll_frequency == 0.7  # noqa: S101
        assert element.ignored_exceptions == [TimeoutError]  # noqa: S101
        element.tap()
        assert element.driver is not None  # noqa: S101

    def test_find_and_get_element(self, app: Shadowstep, android_settings_open_close: None):
        el = app.find_and_get_element({"class": "android.widget.TextView"})
        assert el.get_attribute("class") == "android.widget.TextView"  # noqa: S101

    def test_auto_discover_pages_already_discovered(self, app: Shadowstep):
        """Test _auto_discover_pages when pages already discovered."""
        app._pages_discovered = True
        original_pages = app.pages.copy()

        app._auto_discover_pages()

        # Pages should remain unchanged
        assert app.pages == original_pages
