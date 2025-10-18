"""Smoke integration tests for UiSelector DSL.

This module contains minimal smoke tests that verify UiSelector DSL works
correctly with real Appium/Android device. Detailed logic testing is in unit tests.
"""
import pytest

from shadowstep.locator.ui_selector import UiSelector
from shadowstep.shadowstep import Shadowstep


@pytest.mark.parametrize(
    "selector_builder,description",
    [
        (lambda: UiSelector().text("Settings"), "simple text"),
        (lambda: UiSelector().text("Settings").clickable(True), "text with clickable"),
        (lambda: UiSelector().textContains("Sett"), "textContains"),
        (lambda: UiSelector().text("Settings").clickable(True).className("android.widget.TextView"), "complex chaining"),
    ],
    ids=["simple", "text_clickable", "contains", "complex"]
)
def test_ui_selector_works_with_real_app(
    app: Shadowstep,
    selector_builder,
    description: str
):
    """Smoke test: verify UiSelector DSL works with real Appium app."""
    selector = selector_builder()
    selector_str = str(selector)
    
    # Verify it produces valid UiSelector string
    assert selector_str.startswith("new UiSelector()")
    assert selector_str.endswith(";")
    
    # Verify it works with real app
    element = app.get_element(selector_str)
    assert element is not None, f"{description} selector failed: {selector_str}"


def test_ui_selector_dict_roundtrip_with_real_app(app: Shadowstep):
    """Smoke test: verify UiSelector dict conversion works with real Appium app."""
    # Create UiSelector
    original_selector = UiSelector().text("Settings").clickable(True)
    
    # Convert to dict
    selector_dict = original_selector.to_dict()
    
    # Create new UiSelector from dict
    new_selector = UiSelector.from_dict(selector_dict)
    
    # Both should work with real app
    element1 = app.get_element(str(original_selector))
    element2 = app.get_element(str(new_selector))
    
    assert element1 is not None, "Original selector failed"
    assert element2 is not None, "Selector from dict failed"
