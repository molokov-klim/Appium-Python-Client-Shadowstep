"""Integration tests for UiSelector class.

This module tests the UiSelector DSL functionality using real Android device
connections through the app fixture.
"""
import pytest

from shadowstep.locator.ui_selector import UiSelector
from shadowstep.shadowstep import Shadowstep


class TestUiSelectorTextMethods:
    """Tests for text-related methods."""

    def test_text_method(self, app: Shadowstep):
        """Test UiSelector text method."""
        selector = UiSelector().text("Settings")
        selector_str = str(selector)

        assert selector_str.startswith("new UiSelector()")
        assert '.text("Settings")' in selector_str
        assert selector_str.endswith(";")

        # Verify with real app
        element = app.get_element(selector_str)
        assert element is not None

    def test_text_contains_method(self, app: Shadowstep):
        """Test UiSelector textContains method."""
        selector = UiSelector().textContains("Sett")
        selector_str = str(selector)

        assert '.textContains("Sett")' in selector_str

        # Verify with real app
        element = app.get_element(selector_str)
        assert element is not None

    def test_text_starts_with_method(self, app: Shadowstep):
        """Test UiSelector textStartsWith method."""
        selector = UiSelector().textStartsWith("Sett")
        selector_str = str(selector)

        assert '.textStartsWith("Sett")' in selector_str

    def test_text_matches_method(self, app: Shadowstep):
        """Test UiSelector textMatches method."""
        selector = UiSelector().textMatches(".*Settings.*")
        selector_str = str(selector)

        assert '.textMatches(".*Settings.*")' in selector_str


class TestUiSelectorDescriptionMethods:
    """Tests for description-related methods."""

    def test_description_method(self, app: Shadowstep):
        """Test UiSelector description method."""
        selector = UiSelector().description("Test description")
        selector_str = str(selector)

        assert '.description("Test description")' in selector_str

    def test_description_contains_method(self, app: Shadowstep):
        """Test UiSelector descriptionContains method."""
        selector = UiSelector().descriptionContains("Test")
        selector_str = str(selector)

        assert '.descriptionContains("Test")' in selector_str

    def test_description_starts_with_method(self, app: Shadowstep):
        """Test UiSelector descriptionStartsWith method."""
        selector = UiSelector().descriptionStartsWith("Test")
        selector_str = str(selector)

        assert '.descriptionStartsWith("Test")' in selector_str

    def test_description_matches_method(self, app: Shadowstep):
        """Test UiSelector descriptionMatches method."""
        selector = UiSelector().descriptionMatches(".*Test.*")
        selector_str = str(selector)

        assert '.descriptionMatches(".*Test.*")' in selector_str


class TestUiSelectorResourceIdAndPackageMethods:
    """Tests for resource ID and package methods."""

    def test_resource_id_method(self, app: Shadowstep):
        """Test UiSelector resourceId method."""
        selector = UiSelector().resourceId("android:id/title")
        selector_str = str(selector)

        assert '.resourceId("android:id/title")' in selector_str

    def test_resource_id_matches_method(self, app: Shadowstep):
        """Test UiSelector resourceIdMatches method."""
        selector = UiSelector().resourceIdMatches(".*title.*")
        selector_str = str(selector)

        assert '.resourceIdMatches(".*title.*")' in selector_str

    def test_package_name_method(self, app: Shadowstep):
        """Test UiSelector packageName method."""
        selector = UiSelector().packageName("com.android.settings")
        selector_str = str(selector)

        assert '.packageName("com.android.settings")' in selector_str

    def test_package_name_matches_method(self, app: Shadowstep):
        """Test UiSelector packageNameMatches method."""
        selector = UiSelector().packageNameMatches(".*android.*")
        selector_str = str(selector)

        assert '.packageNameMatches(".*android.*")' in selector_str


class TestUiSelectorClassMethods:
    """Tests for class-related methods."""

    def test_class_name_method(self, app: Shadowstep):
        """Test UiSelector className method."""
        selector = UiSelector().className("android.widget.TextView")
        selector_str = str(selector)

        assert '.className("android.widget.TextView")' in selector_str

    def test_class_name_matches_method(self, app: Shadowstep):
        """Test UiSelector classNameMatches method."""
        selector = UiSelector().classNameMatches(".*TextView.*")
        selector_str = str(selector)

        assert '.classNameMatches(".*TextView.*")' in selector_str


class TestUiSelectorBooleanMethods:
    """Tests for boolean property methods."""

    def test_checkable_method_true(self, app: Shadowstep):
        """Test UiSelector checkable method with true."""
        selector = UiSelector().checkable(True)
        selector_str = str(selector)

        assert ".checkable(true)" in selector_str

    def test_checkable_method_false(self, app: Shadowstep):
        """Test UiSelector checkable method with false."""
        selector = UiSelector().checkable(False)
        selector_str = str(selector)

        assert ".checkable(false)" in selector_str

    def test_checked_method(self, app: Shadowstep):
        """Test UiSelector checked method."""
        selector = UiSelector().checked(True)
        selector_str = str(selector)

        assert ".checked(true)" in selector_str

    def test_clickable_method(self, app: Shadowstep):
        """Test UiSelector clickable method."""
        selector = UiSelector().clickable(True)
        selector_str = str(selector)

        assert ".clickable(true)" in selector_str

    def test_enabled_method(self, app: Shadowstep):
        """Test UiSelector enabled method."""
        selector = UiSelector().enabled(True)
        selector_str = str(selector)

        assert ".enabled(true)" in selector_str

    def test_focusable_method(self, app: Shadowstep):
        """Test UiSelector focusable method."""
        selector = UiSelector().focusable(True)
        selector_str = str(selector)

        assert ".focusable(true)" in selector_str

    def test_focused_method(self, app: Shadowstep):
        """Test UiSelector focused method."""
        selector = UiSelector().focused(True)
        selector_str = str(selector)

        assert ".focused(true)" in selector_str

    def test_long_clickable_method(self, app: Shadowstep):
        """Test UiSelector longClickable method."""
        selector = UiSelector().longClickable(True)
        selector_str = str(selector)

        assert ".longClickable(true)" in selector_str

    def test_scrollable_method(self, app: Shadowstep):
        """Test UiSelector scrollable method."""
        selector = UiSelector().scrollable(True)
        selector_str = str(selector)

        assert ".scrollable(true)" in selector_str

    def test_selected_method(self, app: Shadowstep):
        """Test UiSelector selected method."""
        selector = UiSelector().selected(True)
        selector_str = str(selector)

        assert ".selected(true)" in selector_str

    def test_password_method(self, app: Shadowstep):
        """Test UiSelector password method."""
        selector = UiSelector().password(True)
        selector_str = str(selector)

        assert ".password(true)" in selector_str


class TestUiSelectorNumericMethods:
    """Tests for numeric methods."""

    def test_index_method(self, app: Shadowstep):
        """Test UiSelector index method."""
        selector = UiSelector().index(0)
        selector_str = str(selector)

        assert ".index(0)" in selector_str

    def test_instance_method(self, app: Shadowstep):
        """Test UiSelector instance method."""
        selector = UiSelector().instance(0)
        selector_str = str(selector)

        assert ".instance(0)" in selector_str


class TestUiSelectorHierarchicalMethods:
    """Tests for hierarchical methods."""

    def test_child_selector_method(self, app: Shadowstep):
        """Test UiSelector childSelector method."""
        child = UiSelector().text("Child")
        selector = UiSelector().text("Parent").childSelector(child)
        selector_str = str(selector)

        assert '.text("Parent")' in selector_str
        assert ".childSelector(new UiSelector()" in selector_str
        assert '.text("Child")' in selector_str

    def test_from_parent_method(self, app: Shadowstep):
        """Test UiSelector fromParent method."""
        parent = UiSelector().text("Parent")
        selector = UiSelector().text("Child").fromParent(parent)
        selector_str = str(selector)

        assert '.text("Child")' in selector_str
        assert ".fromParent(new UiSelector()" in selector_str
        assert '.text("Parent")' in selector_str

    def test_sibling_method(self, app: Shadowstep):
        """Test UiSelector sibling method."""
        sibling = UiSelector().text("Sibling")
        selector = UiSelector().text("Element").sibling(sibling)
        selector_str = str(selector)

        assert '.text("Element")' in selector_str
        assert ".sibling(new UiSelector()" in selector_str
        assert '.text("Sibling")' in selector_str


class TestUiSelectorToDict:
    """Tests for to_dict method."""

    def test_to_dict_simple(self, app: Shadowstep):
        """Test converting UiSelector to dictionary."""
        selector = UiSelector().text("Settings")
        result = selector.to_dict()

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"

    def test_to_dict_multiple_attributes(self, app: Shadowstep):
        """Test converting UiSelector with multiple attributes to dictionary."""
        selector = UiSelector().text("Settings").clickable(True)
        result = selector.to_dict()

        assert isinstance(result, dict)
        assert "text" in result
        assert result["text"] == "Settings"
        assert "clickable" in result
        assert result["clickable"] is True

    def test_to_dict_with_hierarchy(self, app: Shadowstep):
        """Test converting UiSelector with hierarchy to dictionary."""
        child = UiSelector().text("Child")
        selector = UiSelector().text("Parent").childSelector(child)
        result = selector.to_dict()

        assert isinstance(result, dict)
        assert "text" in result
        assert "childSelector" in result
        assert isinstance(result["childSelector"], dict)
        assert result["childSelector"]["text"] == "Child"


class TestUiSelectorFluentInterface:
    """Tests for fluent interface chaining."""

    def test_method_chaining(self, app: Shadowstep):
        """Test method chaining returns self."""
        selector = UiSelector().text("Settings").clickable(True).className("android.widget.TextView")
        selector_str = str(selector)

        assert '.text("Settings")' in selector_str
        assert ".clickable(true)" in selector_str
        assert '.className("android.widget.TextView")' in selector_str

        # Verify with real app
        element = app.get_element(selector_str)
        assert element is not None


class TestUiSelectorCopy:
    """Tests for copy method."""

    def test_copy_creates_independent_instance(self, app: Shadowstep):
        """Test that copy creates an independent instance."""
        original = UiSelector().text("Original")
        copied = original.copy()

        # Modify copied
        copied.clickable(True)

        # Original should not be affected
        original_str = str(original)
        copied_str = str(copied)

        assert '.text("Original")' in original_str
        assert ".clickable(true)" not in original_str
        assert '.text("Original")' in copied_str
        assert ".clickable(true)" in copied_str


class TestUiSelectorFromDict:
    """Tests for from_dict method."""

    def test_from_dict_simple(self, app: Shadowstep):
        """Test creating UiSelector from simple dictionary."""
        selector_dict = {"text": "Settings"}
        selector = UiSelector.from_dict(selector_dict)
        selector_str = str(selector)

        assert '.text("Settings")' in selector_str

        # Verify with real app
        element = app.get_element(selector_str)
        assert element is not None

    def test_from_dict_multiple_attributes(self, app: Shadowstep):
        """Test creating UiSelector from dictionary with multiple attributes."""
        selector_dict = {"text": "Settings", "clickable": True}
        selector = UiSelector.from_dict(selector_dict)
        selector_str = str(selector)

        assert '.text("Settings")' in selector_str
        assert ".clickable(true)" in selector_str

    def test_from_dict_with_hierarchy(self, app: Shadowstep):
        """Test creating UiSelector from dictionary with hierarchy."""
        selector_dict = {
            "text": "Parent",
            "childSelector": {"text": "Child"}
        }
        selector = UiSelector.from_dict(selector_dict)
        selector_str = str(selector)

        assert '.text("Parent")' in selector_str
        assert ".childSelector(new UiSelector()" in selector_str
        assert '.text("Child")' in selector_str


class TestUiSelectorWithRealApp:
    """Integration tests using real app elements."""

    def test_find_element_with_text(self, app: Shadowstep):
        """Test finding element using UiSelector with text."""
        selector = UiSelector().text("Settings")
        selector_str = str(selector)

        element = app.get_element(selector_str)
        assert element is not None

    def test_find_element_with_multiple_attributes(self, app: Shadowstep):
        """Test finding element using UiSelector with multiple attributes."""
        selector = UiSelector().text("Settings").clickable(True).className("android.widget.TextView")
        selector_str = str(selector)

        element = app.get_element(selector_str)
        assert element is not None

    def test_conversion_to_dict_and_back(self, app: Shadowstep):
        """Test converting UiSelector to dict and back."""
        # Create UiSelector
        original_selector = UiSelector().text("Settings").clickable(True)

        # Convert to dict
        selector_dict = original_selector.to_dict()

        # Create new UiSelector from dict
        new_selector = UiSelector.from_dict(selector_dict)

        # Both should work with real app
        element1 = app.get_element(str(original_selector))
        element2 = app.get_element(str(new_selector))

        assert element1 is not None
        assert element2 is not None

    def test_equality(self, app: Shadowstep):
        """Test UiSelector equality comparison."""
        selector1 = UiSelector().text("Settings")
        selector2 = UiSelector().text("Settings")
        selector3 = UiSelector().text("Different")

        assert selector1 == selector2
        assert selector1 != selector3

    def test_string_with_special_characters(self, app: Shadowstep):
        """Test UiSelector with special characters in text."""
        selector = UiSelector().text('Settings "quoted"')
        selector_str = str(selector)

        # Check that quotes are properly escaped
        assert 'Settings \\"quoted\\"' in selector_str
