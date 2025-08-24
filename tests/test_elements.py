import time

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
    app.get_element({'resource-id': 'com.android.settings:id/main_content_scrollable_container'}).scroll_to_top(percent=0.7, speed=8000)
    # скроллим вверх до упора
    width, height = app.terminal.get_screen_resolution()
    x = width // 2
    y_start = int(height * 0.2)
    y_end = int(height * 0.8)
    for _ in range(9):
        app.swipe(left=100, top=100,
                        width=width, height=height,
                        direction='down', percent=1.0,
                        speed=10000)  # скроллим вверх
        app.terminal.adb_shell(
            command="input",
            args=f"swipe {x} {y_start} {x} {y_end}"
        )
    return app.get_element({'resource-id': 'com.android.settings:id/main_content_scrollable_container'}).get_elements(
        {'resource-id': 'android:id/title'})


class TestElements:
    """
    A class to test element interactions within the Shadowstep application.
    """

    def test_elements_unique(self, sample_elements: list[Element]):
        attrs: list[dict[str, str]] = []
        expected_attrs = [{'index': '0', 'package': 'com.android.settings', 'class': 'android.widget.TextView', 'text': 'Network & internet', 'resource-id': 'android:id/title', 'checkable': 'false', 'checked': 'false', 'clickable': 'false', 'enabled': 'true', 'focusable': 'false', 'focused': 'false', 'long-clickable': 'false', 'password': 'false', 'scrollable': 'false', 'selected': 'false', 'bounds': '[189,759][625,830]', 'displayed': 'true', 'a11y-important': 'true', 'screen-reader-focusable': 'false', 'drawing-order': '1', 'showing-hint': 'false', 'text-entry-key': 'false', 'dismissable': 'false', 'a11y-focused': 'false', 'heading': 'false', 'live-region': '0', 'context-clickable': 'false', 'content-invalid': 'false'}, {'index': '0', 'package': 'com.android.settings', 'class': 'android.widget.TextView', 'text': 'Connected devices', 'resource-id': 'android:id/title', 'checkable': 'false', 'checked': 'false', 'clickable': 'false', 'enabled': 'true', 'focusable': 'false', 'focused': 'false', 'long-clickable': 'false', 'password': 'false', 'scrollable': 'false', 'selected': 'false', 'bounds': '[189,990][636,1061]', 'displayed': 'true', 'a11y-important': 'true', 'screen-reader-focusable': 'false', 'drawing-order': '1', 'showing-hint': 'false', 'text-entry-key': 'false', 'dismissable': 'false', 'a11y-focused': 'false', 'heading': 'false', 'live-region': '0', 'context-clickable': 'false', 'content-invalid': 'false'}, {'index': '0', 'package': 'com.android.settings', 'class': 'android.widget.TextView', 'text': 'Apps', 'resource-id': 'android:id/title', 'checkable': 'false', 'checked': 'false', 'clickable': 'false', 'enabled': 'true', 'focusable': 'false', 'focused': 'false', 'long-clickable': 'false', 'password': 'false', 'scrollable': 'false', 'selected': 'false', 'bounds': '[189,1221][311,1292]', 'displayed': 'true', 'a11y-important': 'true', 'screen-reader-focusable': 'false', 'drawing-order': '1', 'showing-hint': 'false', 'text-entry-key': 'false', 'dismissable': 'false', 'a11y-focused': 'false', 'heading': 'false', 'live-region': '0', 'context-clickable': 'false', 'content-invalid': 'false'}, {'index': '0', 'package': 'com.android.settings', 'class': 'android.widget.TextView', 'text': 'Notifications', 'resource-id': 'android:id/title', 'checkable': 'false', 'checked': 'false', 'clickable': 'false', 'enabled': 'true', 'focusable': 'false', 'focused': 'false', 'long-clickable': 'false', 'password': 'false', 'scrollable': 'false', 'selected': 'false', 'bounds': '[189,1452][489,1523]', 'displayed': 'true', 'a11y-important': 'true', 'screen-reader-focusable': 'false', 'drawing-order': '1', 'showing-hint': 'false', 'text-entry-key': 'false', 'dismissable': 'false', 'a11y-focused': 'false', 'heading': 'false', 'live-region': '0', 'context-clickable': 'false', 'content-invalid': 'false'}, {'index': '0', 'package': 'com.android.settings', 'class': 'android.widget.TextView', 'text': 'Battery', 'resource-id': 'android:id/title', 'checkable': 'false', 'checked': 'false', 'clickable': 'false', 'enabled': 'true', 'focusable': 'false', 'focused': 'false', 'long-clickable': 'false', 'password': 'false', 'scrollable': 'false', 'selected': 'false', 'bounds': '[189,1683][357,1754]', 'displayed': 'true', 'a11y-important': 'true', 'screen-reader-focusable': 'false', 'drawing-order': '1', 'showing-hint': 'false', 'text-entry-key': 'false', 'dismissable': 'false', 'a11y-focused': 'false', 'heading': 'false', 'live-region': '0', 'context-clickable': 'false', 'content-invalid': 'false'}]
        for el in sample_elements:
            attrs.append(el.get_attributes())
        print(attrs)
        assert attrs == expected_attrs
