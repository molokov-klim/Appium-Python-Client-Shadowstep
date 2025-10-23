"""Smoke integration tests for PageObjectParser class.

This module contains minimal smoke tests that verify PageObjectParser works
with real Appium/Android device. Detailed logic testing is in unit tests.
"""
import pytest

from shadowstep.page_object.page_object_element_node import UiElementNode
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.shadowstep import Shadowstep


def test_parser_works_with_real_page_source(
    app: Shadowstep,
    android_settings_open_close: None
):
    """Smoke test: verify parser works with real device page source."""
    # Arrange
    parser = PageObjectParser()
    
    # Act - Get real page source from device
    page_source = app.driver.page_source
    tree = parser.parse(page_source)
    
    # Assert - Tree is valid UiElementNode with structure
    assert isinstance(tree, UiElementNode)
    assert tree.id is not None
    assert tree.tag is not None
    assert isinstance(tree.attrs, dict)
    assert isinstance(tree.children, list)
    assert isinstance(tree.scrollable_parents, list)
