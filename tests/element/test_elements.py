import time
from typing import Any

import pytest

from shadowstep.element.element import Element
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_elements.py
"""


@pytest.fixture
def sample_elements(app: Shadowstep):
    app.terminal.press_home()
    app.terminal.press_home()
    time.sleep(1)
    app.terminal.start_activity(package="com.android.settings", activity=".Settings")
    time.sleep(1)
    app.get_element({"resource-id": "com.android.settings:id/main_content_scrollable_container"}).scroll_to_top()
    width, height = app.terminal.get_screen_resolution()
    x = width // 2
    y_start = int(height * 0.2)
    y_end = int(height * 0.8)
    for _ in range(9):
        app.swipe(left=100, top=100,
                  width=width, height=height,
                  direction="down", percent=1.0,
                  speed=10000)
        app.terminal.adb_shell(
            command="input",
            args=f"swipe {x} {y_start} {x} {y_end}"
        )
    return app.get_element({"resource-id": "com.android.settings:id/recycler_view"}).get_elements(
        {"resource-id": "android:id/title"})


class TestElements:
    """
    A class to test element interactions within the Shadowstep application.
    """

    def test_elements_unique(self, stability: Any, sample_elements: list[Element]):
        attrs: list[dict[str, Any]] = [
            {
                "class": el.class_name,
                "text": el.text,
                "resource_id": el.resource_id,
            }
            for el in sample_elements
        ]

        # Check uniqueness via conversion to set (needs hashable type → frozenset)
        unique_attrs = {frozenset(attr.items()) for attr in attrs}

        assert len(unique_attrs) == len(attrs), "Duplicate elements found"  # noqa: S101
