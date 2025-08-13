import os
import subprocess
import time
from datetime import datetime

import pytest

from shadowstep.element.element import Element
from shadowstep.shadowstep import Shadowstep
from tests.decorators import time_it


@pytest.fixture
def sample_elements(app: Shadowstep):
    app.terminal.start_activity(package="com.android.settings", activity=".Settings")
    return app.get_element({'resource-id': 'com.android.settings:id/main_content_scrollable_container'}).get_elements({'resource-id': 'android:id/title'})


class TestElements:
    """
    A class to test element interactions within the Shadowstep application.
    """

    def test_elements_debug(self, sample_elements):
        start = datetime.now()
        attrs = [element.get_attribute('text') for element in sample_elements]
        print("+++")
        for attr in attrs:
            print(attr)
        print("+++")
        print(f"⏱ Duration test_elements_debug: {datetime.now() - start}")

    def test_elements_disconnected(self, app: Shadowstep, sample_elements):
        start = datetime.now()
        attrs = [element.get_attribute('text') for element in sample_elements]
        print("+++")
        for attr in attrs:
            print(attr)
            app.disconnect()
        print("+++")
        print(f"⏱ Duration test_elements_disconnected: {datetime.now() - start}")

    def test_elements_first(self, sample_elements):
        """Verify that the first() method returns a valid Element or None."""
        first = sample_elements.first()
        assert isinstance(first, Element) or first is None

    def test_elements_to_list(self, sample_elements):
        """Ensure to_list() returns all elements as a list."""
        elements_list = sample_elements.to_list()
        assert isinstance(elements_list, list)
        assert all(isinstance(el, Element) for el in elements_list)

    def test_elements_filter(self, sample_elements):
        """Test filtering elements by text presence."""
        filtered = sample_elements.filter(lambda el: "Battery" in (el.text or ""))
        assert isinstance(filtered, type(sample_elements))
        assert any("Battery" in (el.text or "") for el in filtered.to_list())

    def test_elements_should_have_count(self, sample_elements):
        """Assert the number of elements using the should().have.count API."""
        sample_elements.should.have.count(minimum=3)


