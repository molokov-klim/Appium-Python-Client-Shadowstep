import time
from typing import Any

import pytest

from shadowstep.element.element import Element
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def sample_elements(app: Shadowstep):
    app.terminal.press_home()
    app.terminal.press_home()
    time.sleep(1)
    app.terminal.start_activity(package="com.android.settings", activity=".Settings")
    time.sleep(1)
    app.get_element({"resource-id": "com.android.settings:id/main_content_scrollable_container"}).scroll_to_top(percent=0.7, speed=8000)
    # скроллим вверх до упора
    width, height = app.terminal.get_screen_resolution()
    x = width // 2
    y_start = int(height * 0.2)
    y_end = int(height * 0.8)
    for _ in range(9):
        app.swipe(left=100, top=100,
                        width=width, height=height,
                        direction="down", percent=1.0,
                        speed=10000)  # скроллим вверх
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

    def test_elements_unique(self, stability: Any,  sample_elements: list[Element]):
        attrs: list[dict[str, str]] = [
            {
                "class": el.class_name,
                "text": el.text,
                "resource_id": el.resource_id,
            }
            for el in sample_elements
        ]

        # Проверяем уникальность через преобразование в set (нужен hashable тип → frozenset)
        unique_attrs = {frozenset(attr.items()) for attr in attrs}

        assert len(unique_attrs) == len(attrs), "Найдены дубликаты элементов"
