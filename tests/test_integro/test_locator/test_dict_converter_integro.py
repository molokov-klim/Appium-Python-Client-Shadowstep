"""Smoke integration tests for DictConverter class.

This module contains minimal smoke tests that verify DictConverter works
correctly with real Appium/Android device. Detailed logic testing is in unit tests.
"""
import pytest

from shadowstep.locator.converter.dict_converter import DictConverter
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def converter():
    """Fixture providing DictConverter instance."""
    return DictConverter()


@pytest.mark.parametrize(
    "selector,expected_format",
    [
        ({"text": "Settings"}, "xpath"),
        ({"text": "Settings", "clickable": True}, "xpath"),
        ({"textContains": "Sett"}, "xpath"),
        ({"text": "Settings"}, "uiselector"),
        ({"text": "Settings", "clickable": True}, "uiselector"),
        ({"textContains": "Sett"}, "uiselector"),
    ],
    ids=[
        "simple_xpath", "complex_xpath", "contains_xpath",
        "simple_uiselector", "complex_uiselector", "contains_uiselector"
    ]
)
def test_dict_conversion_works_with_real_app(
    app: Shadowstep, 
    converter: DictConverter,
    selector: dict,
    expected_format: str
):
    """Smoke test: verify dict conversions work with real Appium app."""
    if expected_format == "xpath":
        result = converter.dict_to_xpath(selector)
        element = app.get_element(("xpath", result))
    else:
        result = converter.dict_to_ui_selector(selector)
        element = app.get_element(result)
    
    assert element is not None, f"Selector failed to find element: {result}"
