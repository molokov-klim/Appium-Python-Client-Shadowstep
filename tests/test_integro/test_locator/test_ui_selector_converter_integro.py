# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Smoke integration tests for UiSelectorConverter class.

This module contains minimal smoke tests that verify UiSelectorConverter works
correctly with real Appium/Android device. Detailed logic testing is in unit tests.
"""
import pytest

from shadowstep.locator.converter.ui_selector_converter import UiSelectorConverter
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def converter():
    """Fixture providing UiSelectorConverter instance."""
    return UiSelectorConverter()


@pytest.mark.parametrize(
    "uiselector,conversion_type",
    [
        ('new UiSelector().text("Settings");', "xpath"),
        ('new UiSelector().text("Settings").clickable(true);', "xpath"),
        ('new UiSelector().textContains("Sett");', "xpath"),
        ('new UiSelector().text("Settings");', "dict"),
        ('new UiSelector().text("Settings").clickable(true);', "dict"),
        ('new UiSelector().textContains("Sett");', "dict"),
    ],
    ids=[
        "simple_xpath", "complex_xpath", "contains_xpath",
        "simple_dict", "complex_dict", "contains_dict"
    ]
)
def test_uiselector_conversion_works_with_real_app(
    app: Shadowstep,
    converter: UiSelectorConverter,
    uiselector: str,
    conversion_type: str
):
    """Smoke test: verify UiSelector conversions work with real Appium app."""
    if conversion_type == "xpath":
        result = converter.selector_to_xpath(uiselector)
        element = app.get_element(("xpath", result))
    else:
        result = converter.selector_to_dict(uiselector)
        element = app.get_element(result)
    
    assert element is not None, f"Conversion failed: {result}"
