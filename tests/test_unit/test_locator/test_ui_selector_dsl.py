"""
Tests for UiSelector DSL functionality.

This module tests the fluent DSL for building UiSelector locators in a more
readable and maintainable way.
"""
# ruff: noqa: S101

import logging

import pytest

from shadowstep.locator.ui_selector import UiSelector

logger = logging.getLogger(__name__)


class TestUiSelectorDSL:
    """Test cases for UiSelector DSL functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.selector = UiSelector()

    @pytest.mark.unit
    def test_basic_text_method(self):
        """Test basic text method."""
        selector = UiSelector().text("OK")
        result = str(selector)
        expected = 'new UiSelector().text("OK");'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_basic_class_method(self):
        """Test basic className method."""
        selector = UiSelector().className("android.widget.Button")
        result = str(selector)
        expected = 'new UiSelector().className("android.widget.Button");'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_basic_boolean_method(self):
        """Test basic boolean method."""
        selector = UiSelector().clickable(True)
        result = str(selector)
        expected = "new UiSelector().clickable(true);"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_boolean_method_default_true(self):
        """Test boolean method with default True value."""
        selector = UiSelector().clickable()
        result = str(selector)
        expected = "new UiSelector().clickable(true);"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_boolean_method_false(self):
        """Test boolean method with False value."""
        selector = UiSelector().enabled(False)
        result = str(selector)
        expected = "new UiSelector().enabled(false);"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_numeric_methods(self):
        """Test numeric methods."""
        selector = UiSelector().index(2).instance(1)
        result = str(selector)
        expected = "new UiSelector().index(2).instance(1);"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_text_functions(self):
        """Test text function methods."""
        selector = (UiSelector()
                   .textContains("Hello")
                   .textStartsWith("Start")
                   .textMatches(".*test.*"))
        result = str(selector)
        expected = 'new UiSelector().textContains("Hello").textStartsWith("Start").textMatches(".*test.*");'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_description_functions(self):
        """Test description function methods."""
        selector = (UiSelector()
                   .description("Submit")
                   .descriptionContains("icon")
                   .descriptionStartsWith("prefix")
                   .descriptionMatches(".*icon.*"))
        result = str(selector)
        expected = 'new UiSelector().description("Submit").descriptionContains("icon").descriptionStartsWith("prefix").descriptionMatches(".*icon.*");'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_resource_id_methods(self):
        """Test resource ID methods."""
        selector = (UiSelector()
                   .resourceId("com.example:id/button")
                   .resourceIdMatches(".*button.*"))
        result = str(selector)
        expected = 'new UiSelector().resourceId("com.example:id/button").resourceIdMatches(".*button.*");'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_package_methods(self):
        """Test package name methods."""
        selector = (UiSelector()
                   .packageName("com.example.app")
                   .packageNameMatches("com.example.*"))
        result = str(selector)
        expected = 'new UiSelector().packageName("com.example.app").packageNameMatches("com.example.*");'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_class_methods(self):
        """Test class name methods."""
        selector = (UiSelector()
                   .className("android.widget.Button")
                   .classNameMatches(".*Button.*"))
        result = str(selector)
        expected = 'new UiSelector().className("android.widget.Button").classNameMatches(".*Button.*");'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_all_boolean_properties(self):
        """Test all boolean property methods."""
        selector = (UiSelector()
                   .checkable(True)
                   .checked(False)
                   .clickable(True)
                   .enabled(False)
                   .focusable(True)
                   .focused(False)
                   .longClickable(True)
                   .scrollable(False)
                   .selected(True)
                   .password(False))
        result = str(selector)
        expected = ("new UiSelector().checkable(true).checked(false).clickable(true).enabled(false)"
                   ".focusable(true).focused(false).longClickable(true).scrollable(false)"
                   ".selected(true).password(false);")
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_fluent_chaining(self):
        """Test fluent method chaining."""
        selector = (UiSelector()
                   .text("Submit")
                   .className("android.widget.Button")
                   .clickable(True)
                   .enabled(True)
                   .index(1))
        result = str(selector)
        expected = 'new UiSelector().text("Submit").className("android.widget.Button").clickable(true).enabled(true).index(1);'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_hierarchical_child_selector(self):
        """Test hierarchical childSelector method."""
        child = UiSelector().text("Item")
        selector = UiSelector().className("android.widget.LinearLayout").childSelector(child)
        result = str(selector)
        expected = 'new UiSelector().className("android.widget.LinearLayout").childSelector(new UiSelector().text("Item"));'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_hierarchical_from_parent(self):
        """Test hierarchical fromParent method."""
        parent = UiSelector().className("android.widget.FrameLayout")
        selector = UiSelector().text("Child").fromParent(parent)
        result = str(selector)
        expected = 'new UiSelector().text("Child").fromParent(new UiSelector().className("android.widget.FrameLayout"));'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_hierarchical_sibling(self):
        """Test hierarchical sibling method."""
        sibling = UiSelector().text("Second")
        selector = UiSelector().text("First").sibling(sibling)
        result = str(selector)
        expected = 'new UiSelector().text("First").sibling(new UiSelector().text("Second"));'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_deep_hierarchical_nesting(self):
        """Test deep hierarchical nesting."""
        deep_child = UiSelector().text("Deep Text")
        child = UiSelector().className("android.widget.Button").childSelector(deep_child)
        selector = UiSelector().className("android.widget.LinearLayout").childSelector(child)
        result = str(selector)
        expected = ('new UiSelector().className("android.widget.LinearLayout")'
                   '.childSelector(new UiSelector().className("android.widget.Button")'
                   '.childSelector(new UiSelector().text("Deep Text")));')
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_mixed_hierarchical_relationships(self):
        """Test mixed hierarchical relationships."""
        child = UiSelector().text("Menu")
        parent = UiSelector().className("android.widget.LinearLayout").childSelector(child)
        selector = (UiSelector()
                   .text("Settings")
                   .clickable(True)
                   .fromParent(parent))
        result = str(selector)
        expected = ('new UiSelector().text("Settings").clickable(true)'
                   '.fromParent(new UiSelector().className("android.widget.LinearLayout")'
                   '.childSelector(new UiSelector().text("Menu")));')
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_string_escaping(self):
        """Test string value escaping."""
        selector = UiSelector().text('Text with "quotes" and \'apostrophes\'')
        result = str(selector)
        expected = 'new UiSelector().text("Text with \\"quotes\\" and \'apostrophes\'");'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_to_dict_conversion(self):
        """Test conversion to dictionary format."""
        child = UiSelector().text("Item")
        selector = (UiSelector()
                   .text("OK")
                   .clickable(True)
                   .childSelector(child))
        result = selector.to_dict()
        expected = {
            "text": "OK",
            "clickable": True,
            "childSelector": {
                "text": "Item"
            }
        }
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_from_dict_conversion(self):
        """Test conversion from dictionary format."""
        selector_dict = {
            "text": "OK",
            "clickable": True,
            "childSelector": {
                "text": "Item"
            }
        }
        selector = UiSelector.from_dict(selector_dict)
        result = str(selector)
        expected = 'new UiSelector().text("OK").clickable(true).childSelector(new UiSelector().text("Item"));'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_equality(self):
        """Test equality comparison."""
        selector1 = UiSelector().text("OK").clickable(True)
        selector2 = UiSelector().text("OK").clickable(True)
        selector3 = UiSelector().text("Cancel").clickable(True)
        
        assert selector1 == selector2  # noqa: S101
        assert selector1 != selector3  # noqa: S101
        assert selector1 != "not a selector"  # noqa: S101

    @pytest.mark.unit
    def test_copy(self):
        """Test copying UiSelector."""
        original = UiSelector().text("OK").clickable(True)
        copy_selector = original.copy()
        
        assert original == copy_selector  # noqa: S101
        assert original is not copy_selector  # noqa: S101
        
        # Modify copy and ensure original is unchanged
        copy_selector.text("Modified")
        assert original != copy_selector  # noqa: S101

    @pytest.mark.unit
    def test_hash(self):
        """Test hashing UiSelector."""
        selector1 = UiSelector().text("OK").clickable(True)
        selector2 = UiSelector().text("OK").clickable(True)
        selector3 = UiSelector().text("Cancel").clickable(True)
        
        assert hash(selector1) == hash(selector2)  # noqa: S101
        assert hash(selector1) != hash(selector3)  # noqa: S101

    @pytest.mark.unit
    def test_repr(self):
        """Test string representation for debugging."""
        selector = UiSelector().text("OK")
        result = repr(selector)
        expected = 'UiSelector(new UiSelector().text("OK");)'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_empty_selector(self):
        """Test empty selector."""
        selector = UiSelector()
        result = str(selector)
        expected = "new UiSelector();"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_from_string_validation(self):
        """Test from_string method validation."""
        # Valid string
        selector = UiSelector.from_string("new UiSelector().text('OK');")
        assert isinstance(selector, UiSelector)  # noqa: S101
        
        # Invalid string
        with pytest.raises(ValueError, match="Invalid UiSelector string format"):
            UiSelector.from_string("invalid string")

    @pytest.mark.unit
    def test_complex_real_world_example(self):
        """Test complex real-world example."""
        # Build a complex selector similar to the user's example
        image_view = UiSelector().className("android.widget.ImageView")
        selector = (UiSelector()
                   .description("Confirm")
                   .clickable(True)
                   .childSelector(image_view))
        
        result = str(selector)
        expected = ('new UiSelector().description("Confirm").clickable(true)'
                   '.childSelector(new UiSelector().className("android.widget.ImageView"));')
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_unicode_and_special_characters(self):
        """Test unicode and special characters."""
        selector = UiSelector().text("Hello world! 🌍").description("Special chars: @#$%^&*()")
        result = str(selector)
        expected = 'new UiSelector().text("Hello world! 🌍").description("Special chars: @#$%^&*()");'
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_regex_patterns(self):
        """Test regex patterns."""
        selector = (UiSelector()
                   .textMatches("^[A-Z][a-z]+\\s+\\d{2,4}$")
                   .resourceIdMatches("com\\.example\\..*\\.id\\..*")
                   .classNameMatches(".*Button.*|.*TextView.*"))
        result = str(selector)
        expected = ('new UiSelector().textMatches("^[A-Z][a-z]+\\\\s+\\\\d{2,4}$")'
                   '.resourceIdMatches("com\\\\.example\\\\..*\\\\.id\\\\..*")'
                   '.classNameMatches(".*Button.*|.*TextView.*");')
        assert result == expected  # noqa: S101

