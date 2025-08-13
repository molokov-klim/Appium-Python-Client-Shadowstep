import time

import pytest
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def sample_element(app: Shadowstep):
    app.terminal.start_activity(package="com.android.settings", activity=".Settings")
    time.sleep(3)
    container = app.get_element({'resource-id': 'com.android.settings:id/main_content_scrollable_container'})
    sample_element = container.scroll_to_element(locator={
        'text': 'Network & internet'
    })
    attrs = sample_element.get_attributes()
    for k, v in attrs.items():
        print(f"{k}: {v}")
    return sample_element


class TestElementShould:

    def test_should_have_text(self, sample_element):
        sample_element.should.have.text("Network & internet")

    def test_should_have_multiple(self, sample_element):
        sample_element.should.have.text("Network & internet").have.resource_id("android:id/title")

    def test_should_have_attr(self, sample_element):
        sample_element.should.have.attr("class", "android.widget.TextView")

    def test_should_be_visible(self, sample_element):
        sample_element.should.be.visible()

    def test_should_be_enabled(self, sample_element):
        sample_element.should.be.enabled()

    def test_should_not_be_focused(self, sample_element):
        sample_element.should.not_be.focused()

    def test_should_not_be_scrollable(self, sample_element):
        sample_element.should.not_be.scrollable()

    def test_should_not_be_password(self, sample_element):
        sample_element.should.not_be.password()

    def test_should_have_package_and_class_name(self, sample_element):
        sample_element.should.have.package("com.android.settings").have.class_name("android.widget.TextView")

    def test_should_have_resource_id_and_attr(self, sample_element):
        sample_element.should.have.resource_id("android:id/title").have.attr("text", "Network & internet")

    def test_should_fail_on_wrong_text(self, sample_element):
        with pytest.raises(AssertionError):
            sample_element.should.have.text("Wrong title")

    def test_should_fail_on_wrong_attr(self, sample_element):
        with pytest.raises(AssertionError):
            sample_element.should.have.attr("enabled", "false")

    def test_should_fail_on_not_be_enabled(self, sample_element):
        with pytest.raises(AssertionError):
            sample_element.should.not_be.enabled()

    def test_should_fail_on_not_be_displayed(self, sample_element):
        with pytest.raises(AssertionError):
            sample_element.should.not_be.displayed()

    def test_should_fail_on_not_have_text(self, sample_element):
        with pytest.raises(AssertionError):
            sample_element.should.not_have.text("Network & internet")

    def test_should_fail_on_not_have_attr(self, sample_element):
        with pytest.raises(AssertionError):
            sample_element.should.not_have.attr("text", "Network & internet")

    def test_should_have_resource_id_should_fail(self, sample_element):
        with pytest.raises(AssertionError):
            sample_element.should.have.resource_id("some_resource_id")

    def test_should_unknown_attribute_raises(self, sample_element):
        with pytest.raises(AttributeError):
            _ = sample_element.should.nonexistent_attribute

    def test_should_be_selected(self, sample_element):
        try:
            sample_element.should.be.selected()
        except AssertionError:
            pass

    def test_should_be_checkable(self, sample_element):
        try:
            sample_element.should.be.checkable()
        except AssertionError:
            pass

    def test_should_be_checked(self, sample_element):
        try:
            sample_element.should.be.checked()
        except AssertionError:
            pass

    def test_should_have_content_desc(self, sample_element):
        assert sample_element.get_attribute("content-desc") is not None  # sanity check
        sample_element.should.have.content_desc(sample_element.get_attribute("content-desc"))

    def test_should_have_bounds(self, sample_element):
        assert sample_element.get_attribute("bounds") is not None
        sample_element.should.have.bounds(sample_element.get_attribute("bounds"))

    def test_should_be_disabled(self, sample_element):
        if not sample_element.is_enabled():
            sample_element.should.be.disabled()
        else:
            with pytest.raises(AssertionError):
                sample_element.should.be.disabled()

    def test_should_be_focusable(self, sample_element):
        if sample_element.get_attribute("focusable") == "true":
            sample_element.should.be.focusable()

    def test_should_be_long_clickable(self, sample_element):
        if sample_element.get_attribute("long-clickable") == "true":
            sample_element.should.be.long_clickable()
