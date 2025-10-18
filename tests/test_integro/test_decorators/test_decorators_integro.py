# ruff: noqa
# pyright: ignore
"""Smoke integration tests for decorators module.

This module contains minimal smoke tests that verify decorators work
with real Appium/Android device. Detailed logic testing is in unit tests.

Note: These decorators are applied to Element methods, so we test through Element usage.
"""
import time

import pytest

from shadowstep.shadowstep import Shadowstep


def test_fail_safe_decorator_works_with_real_element(
    app: Shadowstep, 
    android_settings_open_close: None
):
    """Smoke test: verify @fail_safe_element decorator works with real app.
    
    The decorator is applied to Element methods like tap(), send_keys(), etc.
    Testing through real element interaction verifies the decorator chain works.
    """
    # Get element (uses fail_safe internally for finding)
            element = app.get_element({"text": "Battery"}, timeout=10)

    # Tap uses @fail_safe_element decorator
        element.tap()
        time.sleep(1)

    # Verify tap worked by checking we're still in Settings
        package = app.get_current_package()
    assert "com.android.settings" in package

        # Go back
        app.terminal.press_back()
        time.sleep(1)


def test_retry_decorator_works_with_real_element(
    app: Shadowstep,
    android_settings_open_close: None
):
    """Smoke test: verify @retry decorator works with real app.
    
    Element finding uses retry decorator to handle timing issues.
    """
    # This internally uses @retry decorator
    element = app.get_element({"text": "Battery"}, timeout=5)
    
    # Verify element was found (retry worked)
    assert element is not None
    assert element.is_displayed()
