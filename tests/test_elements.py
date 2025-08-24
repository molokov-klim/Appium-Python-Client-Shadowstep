import pytest

from shadowstep.element.element import Element
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def sample_elements(app: Shadowstep):
    app.terminal.start_activity(package="com.android.settings", activity=".Settings")
    return app.get_element({'resource-id': 'com.android.settings:id/main_content_scrollable_container'}).get_elements(
        {'resource-id': 'android:id/title'})


class TestElements:
    """
    A class to test element interactions within the Shadowstep application.
    """

    def test_elements_unique(self, sample_elements: list[Element]):
        attrs: list[dict[str, str]] = []
        expected_attrs = [{'index': '0', 'package': 'com.android.settings', 'class': 'android.widget.TextView',
                           'text': 'Network & internet', 'resource-id': 'android:id/title', 'checkable': 'false',
                           'checked': 'false', 'clickable': 'false', 'enabled': 'true', 'focusable': 'false',
                           'focused': 'false', 'long-clickable': 'false', 'password': 'false', 'scrollable': 'false',
                           'selected': 'false', 'bounds': '[189,608][625,679]', 'displayed': 'true',
                           'a11y-important': 'true', 'screen-reader-focusable': 'false', 'drawing-order': '1',
                           'showing-hint': 'false', 'text-entry-key': 'false', 'dismissable': 'false',
                           'a11y-focused': 'false', 'heading': 'false', 'live-region': '0',
                           'context-clickable': 'false', 'content-invalid': 'false'},
                          {'index': '0', 'package': 'com.android.settings', 'class': 'android.widget.TextView',
                           'text': 'Connected devices', 'resource-id': 'android:id/title', 'checkable': 'false',
                           'checked': 'false', 'clickable': 'false', 'enabled': 'true', 'focusable': 'false',
                           'focused': 'false', 'long-clickable': 'false', 'password': 'false', 'scrollable': 'false',
                           'selected': 'false', 'bounds': '[189,839][636,910]', 'displayed': 'true',
                           'a11y-important': 'true', 'screen-reader-focusable': 'false', 'drawing-order': '1',
                           'showing-hint': 'false', 'text-entry-key': 'false', 'dismissable': 'false',
                           'a11y-focused': 'false', 'heading': 'false', 'live-region': '0',
                           'context-clickable': 'false', 'content-invalid': 'false'},
                          {'index': '0', 'package': 'com.android.settings', 'class': 'android.widget.TextView',
                           'text': 'Apps', 'resource-id': 'android:id/title', 'checkable': 'false', 'checked': 'false',
                           'clickable': 'false', 'enabled': 'true', 'focusable': 'false', 'focused': 'false',
                           'long-clickable': 'false', 'password': 'false', 'scrollable': 'false', 'selected': 'false',
                           'bounds': '[189,1070][311,1141]', 'displayed': 'true', 'a11y-important': 'true',
                           'screen-reader-focusable': 'false', 'drawing-order': '1', 'showing-hint': 'false',
                           'text-entry-key': 'false', 'dismissable': 'false', 'a11y-focused': 'false',
                           'heading': 'false', 'live-region': '0', 'context-clickable': 'false',
                           'content-invalid': 'false'},
                          {'index': '0', 'package': 'com.android.settings', 'class': 'android.widget.TextView',
                           'text': 'Notifications', 'resource-id': 'android:id/title', 'checkable': 'false',
                           'checked': 'false', 'clickable': 'false', 'enabled': 'true', 'focusable': 'false',
                           'focused': 'false', 'long-clickable': 'false', 'password': 'false', 'scrollable': 'false',
                           'selected': 'false', 'bounds': '[189,1301][489,1372]', 'displayed': 'true',
                           'a11y-important': 'true', 'screen-reader-focusable': 'false', 'drawing-order': '1',
                           'showing-hint': 'false', 'text-entry-key': 'false', 'dismissable': 'false',
                           'a11y-focused': 'false', 'heading': 'false', 'live-region': '0',
                           'context-clickable': 'false', 'content-invalid': 'false'},
                          {'index': '0', 'package': 'com.android.settings', 'class': 'android.widget.TextView',
                           'text': 'Battery', 'resource-id': 'android:id/title', 'checkable': 'false',
                           'checked': 'false', 'clickable': 'false', 'enabled': 'true', 'focusable': 'false',
                           'focused': 'false', 'long-clickable': 'false', 'password': 'false', 'scrollable': 'false',
                           'selected': 'false', 'bounds': '[189,1532][357,1603]', 'displayed': 'true',
                           'a11y-important': 'true', 'screen-reader-focusable': 'false', 'drawing-order': '1',
                           'showing-hint': 'false', 'text-entry-key': 'false', 'dismissable': 'false',
                           'a11y-focused': 'false', 'heading': 'false', 'live-region': '0',
                           'context-clickable': 'false', 'content-invalid': 'false'},
                          {'index': '0', 'package': 'com.android.settings', 'class': 'android.widget.TextView',
                           'text': 'Storage', 'resource-id': 'android:id/title', 'checkable': 'false',
                           'checked': 'false', 'clickable': 'false', 'enabled': 'true', 'focusable': 'false',
                           'focused': 'false', 'long-clickable': 'false', 'password': 'false', 'scrollable': 'false',
                           'selected': 'false', 'bounds': '[189,1763][371,1794]', 'displayed': 'true',
                           'a11y-important': 'true', 'screen-reader-focusable': 'false', 'drawing-order': '1',
                           'showing-hint': 'false', 'text-entry-key': 'false', 'dismissable': 'false',
                           'a11y-focused': 'false', 'heading': 'false', 'live-region': '0',
                           'context-clickable': 'false', 'content-invalid': 'false'}]
        for el in sample_elements:
            attrs.append(el.get_attributes())
        assert attrs == expected_attrs
