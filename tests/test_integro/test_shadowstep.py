# ruff: noqa
# pyright: ignore
import pytest

from shadowstep.page_base import PageBaseShadowstep
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


    def test_list_registered_pages_output(self, app: Shadowstep):
        """Test list_registered_pages() executes without errors.

        Steps:
        1. Call list_registered_pages().
        2. Verify that no exceptions are raised.
        """
        # Call the method - it should execute without exceptions
        app.list_registered_pages()

        # If we reach here, the method executed successfully

    def test_get_page_success(self, app: Shadowstep):
        """Test get_page() returns page instance when page exists.

        Steps:
        1. If pages are registered, test with a registered page.
        2. Verify that a page instance is returned.
        3. Verify that it's a PageBaseShadowstep instance.
        """
        # Skip if no pages are registered
        if not app.pages:
            pytest.skip("No pages registered for testing")

        # Get the first registered page name
        page_name = next(iter(app.pages.keys()))

        # Call get_page()
        page_instance = app.get_page(page_name)

        # Verify instance is returned and is correct type
        assert page_instance is not None  # noqa: S101
        assert isinstance(page_instance, PageBaseShadowstep)  # noqa: S101
        assert page_instance.shadowstep is app  # noqa: S101

    def test_get_page_not_found(self, app: Shadowstep):
        """Test get_page() raises ValueError when page not found.

        Steps:
        1. Call get_page() with a non-existent page name.
        2. Verify that ValueError is raised with appropriate message.
        """
        # Call get_page() with non-existent page name
        with pytest.raises(ValueError) as exc_info:
            app.get_page("NonExistentPageXYZ123")

        # Verify error message contains page name
        error_message = str(exc_info.value)
        assert "NonExistentPageXYZ123" in error_message  # noqa: S101
        assert "not found" in error_message  # noqa: S101

    def test_resolve_page_success(self, app: Shadowstep):
        """Test resolve_page() returns page instance when page exists.

        Steps:
        1. If pages are registered, test with a registered page.
        2. Verify that a page instance is returned.
        3. Verify that it's a PageBaseShadowstep instance.
        """
        # Skip if no pages are registered
        if not app.pages:
            pytest.skip("No pages registered for testing")

        # Get the first registered page name
        page_name = next(iter(app.pages.keys()))

        # Call resolve_page()
        page_instance = app.resolve_page(page_name)

        # Verify instance is returned and is correct type
        assert page_instance is not None  # noqa: S101
        assert isinstance(page_instance, PageBaseShadowstep)  # noqa: S101
        assert page_instance.shadowstep is app  # noqa: S101

    def test_resolve_page_not_found(self, app: Shadowstep):
        """Test resolve_page() raises ValueError when page not found.

        Steps:
        1. Call resolve_page() with a non-existent page name.
        2. Verify that ValueError is raised with appropriate message.
        """
        # Call resolve_page() with non-existent page name
        with pytest.raises(ValueError) as exc_info:
            app.resolve_page("NonExistentResolvePageXYZ123")

        # Verify error message contains page name
        error_message = str(exc_info.value)
        assert "NonExistentResolvePageXYZ123" in error_message  # noqa: S101
        assert "not found" in error_message  # noqa: S101

    def test_get_elements_multiple_elements(self, app: Shadowstep, android_settings_open_close: None):
        """Test get_elements() returns multiple elements matching locator.

        Steps:
        1. Call get_elements() with a locator that matches multiple elements.
        2. Verify that a list of Element instances is returned.
        3. Verify that all elements are properly initialized with shadowstep reference.
        4. Verify that timeout and poll_frequency are set correctly.
        """
        # Step 1: Call get_elements() with a locator that matches multiple elements
        locator = ("xpath", "//android.widget.TextView")
        timeout = 10
        poll_frequency = 0.5

        elements = app.get_elements(
            locator=locator,
            timeout=timeout,
            poll_frequency=poll_frequency
        )

        # Step 2: Verify that a list of Element instances is returned
        assert isinstance(elements, list)  # noqa: S101
        assert len(elements) > 0  # noqa: S101

        # Step 3: Verify that all elements are properly initialized
        for element in elements:
            assert isinstance(element, Element)  # noqa: S101
            assert element.shadowstep is app  # noqa: S101
            assert element.timeout == timeout  # noqa: S101
            assert element.poll_frequency == poll_frequency  # noqa: S101

    def test_is_text_visible_success(self, app: Shadowstep, android_settings_open_close: None):
        """Test is_text_visible() returns True when text element is visible.

        Steps:
        1. Call is_text_visible() with text that exists on Settings screen.
        2. Verify that True is returned.
        """
        # Using "Settings" text which should be visible on Android Settings page
        result = app.is_text_visible("Settings")

        assert result is True  # noqa: S101

    def test_is_text_visible_not_found(self, app: Shadowstep):
        """Test is_text_visible() returns False when text element is not found.

        Steps:
        1. Call is_text_visible() with non-existent text.
        2. Verify that False is returned.
        3. Verify that no exceptions are raised.
        """
        # Call with non-existent text
        result = app.is_text_visible("NonExistentText12345XYZ")

        # Verify False is returned and no exception was raised
        assert result is False  # noqa: S101
