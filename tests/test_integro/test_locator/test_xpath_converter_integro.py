# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Smoke integration tests for XPathConverter class.

This module contains minimal smoke tests that verify XPathConverter works
correctly with real Appium/Android device. Detailed logic testing is in unit tests.
"""
import pytest

from shadowstep.locator.converter.xpath_converter import XPathConverter
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def converter():
    """Fixture providing XPathConverter instance."""
    return XPathConverter()


@pytest.mark.parametrize(
    "xpath,conversion_type",
    [
        ("//*[@text='Settings']", "dict"),
        ("//*[@text='Settings'][@clickable='true']", "dict"),
        ("//*[contains(@text,'Sett')]", "dict"),
        ("//*[@text='Settings']", "uiselector"),
        ("//*[@text='Settings'][@clickable='true']", "uiselector"),
        ("//*[contains(@text,'Sett')]", "uiselector"),
    ],
    ids=[
        "simple_dict", "complex_dict", "contains_dict",
        "simple_uiselector", "complex_uiselector", "contains_uiselector"
    ]
)
def test_xpath_conversion_works_with_real_app(
    app: Shadowstep,
    converter: XPathConverter,
    xpath: str,
    conversion_type: str
):
    """Smoke test: verify XPath conversions work with real Appium app."""
    if conversion_type == "dict":
        result = converter.xpath_to_dict(xpath)
        element = app.get_element(result)
    else:
        result = converter.xpath_to_ui_selector(xpath)
        element = app.get_element(result)
    
    assert element is not None, f"Conversion failed: {result}"
