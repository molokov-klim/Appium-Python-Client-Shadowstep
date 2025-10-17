"""Integration tests for DictConverter class.

This module tests the DictConverter functionality using real Android device
connections through the app fixture.
"""
import pytest

from shadowstep.locator.converter.dict_converter import DictConverter
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def converter():
    """Fixture providing DictConverter instance."""
    return DictConverter()


class TestDictToXPath:
    """Tests for dict_to_xpath method."""

    def test_dict_to_xpath_simple_text(self, app: Shadowstep, converter: DictConverter):
        """Test converting simple text selector to xpath."""
        selector = {"text": "Settings"}
        result = converter.dict_to_xpath(selector)

        assert isinstance(result, str)
        assert "@text='Settings'" in result

        # Verify xpath works with real app
        element = app.get_element(("xpath", result))
        assert element is not None

    def test_dict_to_xpath_clickable(self, app: Shadowstep, converter: DictConverter):
        """Test converting clickable selector to xpath."""
        selector = {"clickable": True}
        result = converter.dict_to_xpath(selector)

        assert isinstance(result, str)
        assert "@clickable='true'" in result

    def test_dict_to_xpath_resource_id(self, app: Shadowstep, converter: DictConverter):
        """Test converting resource-id selector to xpath."""
        selector = {"resource-id": "android:id/title"}
        result = converter.dict_to_xpath(selector)

        assert isinstance(result, str)
        assert "@resource-id='android:id/title'" in result

    def test_dict_to_xpath_multiple_attributes(self, app: Shadowstep, converter: DictConverter):
        """Test converting selector with multiple attributes to xpath."""
        selector = {"text": "Settings", "clickable": True}
        result = converter.dict_to_xpath(selector)

        assert isinstance(result, str)
        assert "@text='Settings'" in result
        assert "@clickable='true'" in result

    def test_dict_to_xpath_text_contains(self, app: Shadowstep, converter: DictConverter):
        """Test converting textContains selector to xpath."""
        selector = {"textContains": "Sett"}
        result = converter.dict_to_xpath(selector)

        assert isinstance(result, str)
        assert "contains(@text,'Sett')" in result

    def test_dict_to_xpath_class_name(self, app: Shadowstep, converter: DictConverter):
        """Test converting className selector to xpath."""
        selector = {"class": "android.widget.TextView"}
        result = converter.dict_to_xpath(selector)

        assert isinstance(result, str)
        assert "@class='android.widget.TextView'" in result

    def test_dict_to_xpath_with_instance(self, app: Shadowstep, converter: DictConverter):
        """Test converting selector with instance to xpath."""
        selector = {"text": "Settings", "instance": 0}
        result = converter.dict_to_xpath(selector)

        assert isinstance(result, str)
        assert "@text='Settings'" in result
        assert "[1]" in result

    def test_dict_to_xpath_hierarchical_child(self, app: Shadowstep, converter: DictConverter):
        """Test converting selector with child to xpath."""
        selector = {
            "class": "android.widget.LinearLayout",
            "childSelector": {"text": "Settings"}
        }
        result = converter.dict_to_xpath(selector)

        assert isinstance(result, str)
        assert "@class='android.widget.LinearLayout'" in result
        assert "@text='Settings'" in result


class TestDictToUiSelector:
    """Tests for dict_to_ui_selector method."""

    def test_dict_to_uiselector_simple_text(self, app: Shadowstep, converter: DictConverter):
        """Test converting simple text selector to UiSelector."""
        selector = {"text": "Settings"}
        result = converter.dict_to_ui_selector(selector)

        assert isinstance(result, str)
        assert result.startswith("new UiSelector()")
        assert '.text("Settings")' in result
        assert result.endswith(";")

        # Verify UiSelector works with real app
        element = app.get_element(result)
        assert element is not None

    def test_dict_to_uiselector_clickable(self, app: Shadowstep, converter: DictConverter):
        """Test converting clickable selector to UiSelector."""
        selector = {"clickable": True}
        result = converter.dict_to_ui_selector(selector)

        assert isinstance(result, str)
        assert ".clickable(true)" in result

    def test_dict_to_uiselector_resource_id(self, app: Shadowstep, converter: DictConverter):
        """Test converting resource-id selector to UiSelector."""
        selector = {"resource-id": "android:id/title"}
        result = converter.dict_to_ui_selector(selector)

        assert isinstance(result, str)
        assert '.resourceId("android:id/title")' in result

    def test_dict_to_uiselector_multiple_attributes(self, app: Shadowstep, converter: DictConverter):
        """Test converting selector with multiple attributes to UiSelector."""
        selector = {"text": "Settings", "clickable": True}
        result = converter.dict_to_ui_selector(selector)

        assert isinstance(result, str)
        assert '.text("Settings")' in result
        assert ".clickable(true)" in result

    def test_dict_to_uiselector_text_contains(self, app: Shadowstep, converter: DictConverter):
        """Test converting textContains selector to UiSelector."""
        selector = {"textContains": "Sett"}
        result = converter.dict_to_ui_selector(selector)

        assert isinstance(result, str)
        assert '.textContains("Sett")' in result

    def test_dict_to_uiselector_class_name(self, app: Shadowstep, converter: DictConverter):
        """Test converting className selector to UiSelector."""
        selector = {"class": "android.widget.TextView"}
        result = converter.dict_to_ui_selector(selector)

        assert isinstance(result, str)
        assert '.className("android.widget.TextView")' in result

    def test_dict_to_uiselector_with_instance(self, app: Shadowstep, converter: DictConverter):
        """Test converting selector with instance to UiSelector."""
        selector = {"text": "Settings", "instance": 0}
        result = converter.dict_to_ui_selector(selector)

        assert isinstance(result, str)
        assert '.text("Settings")' in result
        assert ".instance(0)" in result

    def test_dict_to_uiselector_hierarchical_child(self, app: Shadowstep, converter: DictConverter):
        """Test converting selector with child to UiSelector."""
        selector = {
            "class": "android.widget.LinearLayout",
            "childSelector": {"text": "Settings"}
        }
        result = converter.dict_to_ui_selector(selector)

        assert isinstance(result, str)
        assert '.className("android.widget.LinearLayout")' in result
        assert '.childSelector(new UiSelector()' in result
        assert '.text("Settings")' in result

    def test_dict_to_uiselector_boolean_false(self, app: Shadowstep, converter: DictConverter):
        """Test converting boolean false value to UiSelector."""
        selector = {"enabled": False}
        result = converter.dict_to_ui_selector(selector)

        assert isinstance(result, str)
        assert ".enabled(false)" in result


class TestValidateDictSelector:
    """Tests for validate_dict_selector method."""

    def test_validate_valid_selector(self, app: Shadowstep, converter: DictConverter):
        """Test validating a valid selector."""
        selector = {"text": "Settings"}
        # Should not raise any exception
        converter.validate_dict_selector(selector)

    def test_validate_selector_with_multiple_attrs(self, app: Shadowstep, converter: DictConverter):
        """Test validating selector with multiple attributes."""
        selector = {"text": "Settings", "clickable": True}
        # Should not raise any exception
        converter.validate_dict_selector(selector)

    def test_validate_empty_selector_raises_error(self, app: Shadowstep, converter: DictConverter):
        """Test that empty selector raises error."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepEmptySelectorError

        selector = {}
        with pytest.raises(ShadowstepEmptySelectorError):
            converter.validate_dict_selector(selector)

    def test_validate_not_dict_raises_error(self, app: Shadowstep, converter: DictConverter):
        """Test that non-dict selector raises error."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepSelectorTypeError

        selector = "not a dict"
        with pytest.raises(ShadowstepSelectorTypeError):
            converter.validate_dict_selector(selector)

    def test_validate_conflicting_text_attrs_raises_error(self, app: Shadowstep, converter: DictConverter):
        """Test that conflicting text attributes raise error."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepConflictingTextAttributesError

        selector = {"text": "Settings", "textContains": "Sett"}
        with pytest.raises(ShadowstepConflictingTextAttributesError):
            converter.validate_dict_selector(selector)

    def test_validate_conflicting_description_attrs_raises_error(self, app: Shadowstep, converter: DictConverter):
        """Test that conflicting description attributes raise error."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepConflictingDescriptionAttributesError

        selector = {"content-desc": "Button", "content-descContains": "Butt"}
        with pytest.raises(ShadowstepConflictingDescriptionAttributesError):
            converter.validate_dict_selector(selector)

    def test_validate_hierarchical_with_dict_value(self, app: Shadowstep, converter: DictConverter):
        """Test validating hierarchical selector with dict value."""
        selector = {
            "text": "Parent",
            "childSelector": {"text": "Child"}
        }
        # Should not raise any exception
        converter.validate_dict_selector(selector)

    def test_validate_hierarchical_with_non_dict_raises_error(self, app: Shadowstep, converter: DictConverter):
        """Test that hierarchical selector with non-dict value raises error."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepHierarchicalAttributeError

        selector = {
            "text": "Parent",
            "childSelector": "not a dict"
        }
        with pytest.raises(ShadowstepHierarchicalAttributeError):
            converter.validate_dict_selector(selector)


class TestDictConverterWithRealApp:
    """Integration tests using real app elements."""

    def test_conversion_round_trip_xpath(self, app: Shadowstep, converter: DictConverter):
        """Test converting dict -> xpath and verifying with real app."""
        selector = {"text": "Settings"}

        # Convert to xpath
        xpath_result = converter.dict_to_xpath(selector)

        # Use with real app
        element = app.get_element(("xpath", xpath_result))
        assert element is not None

    def test_conversion_round_trip_uiselector(self, app: Shadowstep, converter: DictConverter):
        """Test converting dict -> uiselector and verifying with real app."""
        selector = {"text": "Settings"}

        # Convert to UiSelector
        uiselector_result = converter.dict_to_ui_selector(selector)

        # Use with real app
        element = app.get_element(uiselector_result)
        assert element is not None

    def test_complex_selector_with_app(self, app: Shadowstep, converter: DictConverter):
        """Test complex selector with multiple attributes."""
        selector = {
            "text": "Settings",
            "clickable": True,
            "class": "android.widget.TextView"
        }

        # Convert to xpath
        xpath_result = converter.dict_to_xpath(selector)
        element1 = app.get_element(("xpath", xpath_result))

        # Convert to UiSelector
        uiselector_result = converter.dict_to_ui_selector(selector)
        element2 = app.get_element(uiselector_result)

        # Both should find the same element
        assert element1 is not None
        assert element2 is not None

    def test_text_contains_with_app(self, app: Shadowstep, converter: DictConverter):
        """Test textContains selector with real app."""
        selector = {"textContains": "Sett"}

        # Convert to xpath
        xpath_result = converter.dict_to_xpath(selector)
        element = app.get_element(("xpath", xpath_result))

        assert element is not None
