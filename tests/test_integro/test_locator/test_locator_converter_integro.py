"""Smoke integration tests for LocatorConverter class.

This module contains minimal smoke tests that verify LocatorConverter works
correctly with real Appium/Android device. Detailed logic testing is in unit tests.
"""
import pytest

from shadowstep.locator.converter.locator_converter import LocatorConverter
from shadowstep.locator.ui_selector import UiSelector
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def converter():
    """Fixture providing LocatorConverter instance."""
    return LocatorConverter()


@pytest.mark.parametrize(
    "selector_format,selector_value",
    [
        ("dict", {"text": "Settings"}),
        ("xpath_tuple", ("xpath", "//*[@text='Settings']")),
        ("xpath_string", "//*[@text='Settings']"),
        ("uiselector_string", 'new UiSelector().text("Settings");'),
    ],
    ids=["dict", "xpath_tuple", "xpath_string", "uiselector_string"]
)
class TestLocatorConverterSmoke:
    """Smoke tests verifying converter output works with real Appium."""

    def test_conversion_works_with_real_app(
        self, 
        app: Shadowstep, 
        converter: LocatorConverter,
        selector_format: str,
        selector_value: any
    ):
        """Smoke test: verify converted selectors work with real Appium app."""
        # Convert to all formats
        dict_result = converter.to_dict(selector_value)
        xpath_result = converter.to_xpath(selector_value)
        uiselector_result = converter.to_uiselector(selector_value)

        # Verify all converted formats can find element with real app
        element_from_dict = app.get_element(dict_result)
        element_from_xpath = app.get_element(xpath_result)
        element_from_uiselector = app.get_element(uiselector_result)

        # All should successfully find the element
        assert element_from_dict is not None, f"Dict selector failed: {dict_result}"
        assert element_from_xpath is not None, f"XPath selector failed: {xpath_result}"
        assert element_from_uiselector is not None, f"UiSelector failed: {uiselector_result}"


def test_complex_selector_roundtrip_with_real_app(app: Shadowstep, converter: LocatorConverter):
    """Smoke test: verify complex selector conversion chain works with real app."""
    # Start with complex selector
    original_selector = {"text": "Settings", "clickable": True}

    # Convert through chain: dict -> xpath -> uiselector -> dict
    xpath_result = converter.to_xpath(original_selector)
    uiselector_result = converter.to_uiselector(xpath_result)
    final_dict = converter.to_dict(uiselector_result)

    # Verify final result works with real app
    element = app.get_element(final_dict)
    assert element is not None, f"Final selector failed: {final_dict}"

    # Verify attributes are preserved
    assert "text" in final_dict
    assert final_dict["text"] == "Settings"
