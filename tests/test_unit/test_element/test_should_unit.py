# ruff: noqa
# pyright: ignore
"""Unit tests for Should assertion classes using mocks."""
from unittest.mock import Mock, PropertyMock

import pytest

from shadowstep.element.element import Element
from shadowstep.element.should import Should, _ShouldHave, _ShouldBe, _ShouldNotHave, _ShouldNotBe


class TestShouldInit:
    """Test Should initialization."""

    def test_init_creates_instance_with_element(self):
        """Test initialization creates instance with element reference."""
        mock_element = Mock(spec=Element)

        should = Should(mock_element)

        assert should.element == mock_element
        assert isinstance(should.have, _ShouldHave)
        assert isinstance(should.not_have, _ShouldNotHave)
        assert isinstance(should.be, _ShouldBe)
        assert isinstance(should.not_be, _ShouldNotBe)

    def test_getattr_delegates_to_element(self):
        """Test __getattr__ delegates to underlying element."""
        mock_element = Mock(spec=Element)
        mock_element.some_method = Mock(return_value="test_value")

        should = Should(mock_element)

        result = should.some_method()

        assert result == "test_value"
        mock_element.some_method.assert_called_once()

    def test_getattr_raises_attribute_error_when_not_found(self):
        """Test __getattr__ raises AttributeError when attribute doesn't exist."""
        mock_element = Mock(spec=Element)
        mock_element.__class__.__name__ = "Element"

        should = Should(mock_element)

        with pytest.raises(AttributeError) as exc_info:
            _ = should.nonexistent_attribute

        assert "Should" in str(exc_info.value)
        assert "nonexistent_attribute" in str(exc_info.value)


class TestShouldHaveText:
    """Test should.have.text assertion."""

    def test_have_text_passes_when_text_matches(self):
        """Test have.text passes when text matches expected."""
        mock_element = Mock(spec=Element)
        type(mock_element).text = PropertyMock(return_value="Expected Text")

        should = Should(mock_element)

        result = should.have.text("Expected Text")

        assert isinstance(result, Should)

    def test_have_text_raises_when_text_does_not_match(self):
        """Test have.text raises AssertionError when text doesn't match."""
        mock_element = Mock(spec=Element)
        type(mock_element).text = PropertyMock(return_value="Actual Text")

        should = Should(mock_element)

        with pytest.raises(AssertionError) as exc_info:
            should.have.text("Expected Text")

        assert "[should]" in str(exc_info.value)
        assert "have.text" in str(exc_info.value)
        assert "Expected Text" in str(exc_info.value)
        assert "Actual Text" in str(exc_info.value)


class TestShouldNotHaveText:
    """Test should.not_have.text assertion."""

    def test_not_have_text_passes_when_text_differs(self):
        """Test not_have.text passes when text differs from expected."""
        mock_element = Mock(spec=Element)
        type(mock_element).text = PropertyMock(return_value="Actual Text")

        should = Should(mock_element)

        result = should.not_have.text("Different Text")

        assert isinstance(result, Should)

    def test_not_have_text_raises_when_text_matches(self):
        """Test not_have.text raises AssertionError when text matches."""
        mock_element = Mock(spec=Element)
        type(mock_element).text = PropertyMock(return_value="Same Text")

        should = Should(mock_element)

        with pytest.raises(AssertionError) as exc_info:
            should.not_have.text("Same Text")

        assert "[should.not]" in str(exc_info.value)


class TestShouldHaveResourceId:
    """Test should.have.resource_id assertion."""

    def test_have_resource_id_passes_when_matches(self):
        """Test have.resource_id passes when resource-id matches."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="com.app:id/button")

        should = Should(mock_element)

        result = should.have.resource_id("com.app:id/button")

        mock_element.get_attribute.assert_called_with("resource-id")
        assert isinstance(result, Should)

    def test_have_resource_id_raises_when_does_not_match(self):
        """Test have.resource_id raises when resource-id doesn't match."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="com.app:id/actual")

        should = Should(mock_element)

        with pytest.raises(AssertionError) as exc_info:
            should.have.resource_id("com.app:id/expected")

        assert "have.resource_id" in str(exc_info.value)


class TestShouldHaveAttr:
    """Test should.have.attr assertion."""

    def test_have_attr_passes_when_matches(self):
        """Test have.attr passes when custom attribute matches."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="expected_value")

        should = Should(mock_element)

        result = should.have.attr("custom-attr", "expected_value")

        mock_element.get_attribute.assert_called_with("custom-attr")
        assert isinstance(result, Should)

    def test_have_attr_raises_when_does_not_match(self):
        """Test have.attr raises when custom attribute doesn't match."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="actual_value")

        should = Should(mock_element)

        with pytest.raises(AssertionError) as exc_info:
            should.have.attr("custom-attr", "expected_value")

        assert "have.attr('custom-attr')" in str(exc_info.value)
        assert "expected_value" in str(exc_info.value)
        assert "actual_value" in str(exc_info.value)


class TestShouldHaveOtherAttributes:
    """Test other should.have assertions."""

    def test_have_content_desc(self):
        """Test have.content_desc assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="test description")

        should = Should(mock_element)
        result = should.have.content_desc("test description")

        mock_element.get_attribute.assert_called_with("content-desc")
        assert isinstance(result, Should)

    def test_have_class_name(self):
        """Test have.class_name assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="android.widget.Button")

        should = Should(mock_element)
        result = should.have.class_name("android.widget.Button")

        mock_element.get_attribute.assert_called_with("class")
        assert isinstance(result, Should)

    def test_have_package(self):
        """Test have.package assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="com.example.app")

        should = Should(mock_element)
        result = should.have.package("com.example.app")

        mock_element.get_attribute.assert_called_with("package")
        assert isinstance(result, Should)

    def test_have_bounds(self):
        """Test have.bounds assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="[0,0][100,100]")

        should = Should(mock_element)
        result = should.have.bounds("[0,0][100,100]")

        mock_element.get_attribute.assert_called_with("bounds")
        assert isinstance(result, Should)

    def test_have_id(self):
        """Test have.id assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="test_id")

        should = Should(mock_element)
        result = should.have.id("test_id")

        mock_element.get_attribute.assert_called_with("id")
        assert isinstance(result, Should)

    def test_have_index(self):
        """Test have.index assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="0")

        should = Should(mock_element)
        result = should.have.index("0")

        mock_element.get_attribute.assert_called_with("index")
        assert isinstance(result, Should)


class TestShouldBeEnabled:
    """Test should.be.enabled assertion."""

    def test_be_enabled_passes_when_element_is_enabled(self):
        """Test be.enabled passes when element is enabled."""
        mock_element = Mock(spec=Element)
        mock_element.is_enabled = Mock(return_value=True)

        should = Should(mock_element)

        result = should.be.enabled()

        mock_element.is_enabled.assert_called_once()
        assert isinstance(result, Should)

    def test_be_enabled_raises_when_element_is_disabled(self):
        """Test be.enabled raises when element is disabled."""
        mock_element = Mock(spec=Element)
        mock_element.is_enabled = Mock(return_value=False)

        should = Should(mock_element)

        with pytest.raises(AssertionError) as exc_info:
            should.be.enabled()

        assert "be.enabled" in str(exc_info.value)


class TestShouldBeDisabled:
    """Test should.be.disabled assertion."""

    def test_be_disabled_passes_when_element_is_disabled(self):
        """Test be.disabled passes when element is disabled."""
        mock_element = Mock(spec=Element)
        mock_element.is_enabled = Mock(return_value=False)

        should = Should(mock_element)

        result = should.be.disabled()

        assert isinstance(result, Should)

    def test_be_disabled_raises_when_element_is_enabled(self):
        """Test be.disabled raises when element is enabled."""
        mock_element = Mock(spec=Element)
        mock_element.is_enabled = Mock(return_value=True)

        should = Should(mock_element)

        with pytest.raises(AssertionError) as exc_info:
            should.be.disabled()

        assert "be.disabled" in str(exc_info.value)


class TestShouldBeSelected:
    """Test should.be.selected assertion."""

    def test_be_selected_passes_when_element_is_selected(self):
        """Test be.selected passes when element is selected."""
        mock_element = Mock(spec=Element)
        mock_element.is_selected = Mock(return_value=True)

        should = Should(mock_element)

        result = should.be.selected()

        mock_element.is_selected.assert_called_once()
        assert isinstance(result, Should)

    def test_be_selected_raises_when_element_is_not_selected(self):
        """Test be.selected raises when element is not selected."""
        mock_element = Mock(spec=Element)
        mock_element.is_selected = Mock(return_value=False)

        should = Should(mock_element)

        with pytest.raises(AssertionError) as exc_info:
            should.be.selected()

        assert "be.selected" in str(exc_info.value)


class TestShouldBeVisible:
    """Test should.be.visible assertion."""

    def test_be_visible_passes_when_element_is_visible(self):
        """Test be.visible passes when element is visible."""
        mock_element = Mock(spec=Element)
        mock_element.is_visible = Mock(return_value=True)

        should = Should(mock_element)

        result = should.be.visible()

        mock_element.is_visible.assert_called_once()
        assert isinstance(result, Should)

    def test_be_visible_raises_when_element_is_not_visible(self):
        """Test be.visible raises when element is not visible."""
        mock_element = Mock(spec=Element)
        mock_element.is_visible = Mock(return_value=False)

        should = Should(mock_element)

        with pytest.raises(AssertionError) as exc_info:
            should.be.visible()

        assert "be.visible" in str(exc_info.value)

    def test_be_displayed_calls_visible(self):
        """Test be.displayed is an alias for be.visible."""
        mock_element = Mock(spec=Element)
        mock_element.is_visible = Mock(return_value=True)

        should = Should(mock_element)

        result = should.be.displayed()

        mock_element.is_visible.assert_called_once()
        assert isinstance(result, Should)


class TestShouldBeOtherStates:
    """Test other should.be state assertions."""

    def test_be_focused(self):
        """Test be.focused assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="true")

        should = Should(mock_element)
        result = should.be.focused()

        mock_element.get_attribute.assert_called_with("focused")
        assert isinstance(result, Should)

    def test_be_focusable(self):
        """Test be.focusable assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="true")

        should = Should(mock_element)
        result = should.be.focusable()

        mock_element.get_attribute.assert_called_with("focusable")
        assert isinstance(result, Should)

    def test_be_long_clickable(self):
        """Test be.long_clickable assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="true")

        should = Should(mock_element)
        result = should.be.long_clickable()

        mock_element.get_attribute.assert_called_with("long-clickable")
        assert isinstance(result, Should)

    def test_be_checkable(self):
        """Test be.checkable assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="true")

        should = Should(mock_element)
        result = should.be.checkable()

        mock_element.get_attribute.assert_called_with("checkable")
        assert isinstance(result, Should)

    def test_be_checked(self):
        """Test be.checked assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="true")

        should = Should(mock_element)
        result = should.be.checked()

        mock_element.get_attribute.assert_called_with("checked")
        assert isinstance(result, Should)

    def test_be_scrollable(self):
        """Test be.scrollable assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="true")

        should = Should(mock_element)
        result = should.be.scrollable()

        mock_element.get_attribute.assert_called_with("scrollable")
        assert isinstance(result, Should)

    def test_be_password(self):
        """Test be.password assertion."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(return_value="true")

        should = Should(mock_element)
        result = should.be.password()

        mock_element.get_attribute.assert_called_with("password")
        assert isinstance(result, Should)


class TestShouldNotBe:
    """Test should.not_be assertions."""

    def test_not_be_enabled_passes_when_disabled(self):
        """Test not_be.enabled passes when element is disabled."""
        mock_element = Mock(spec=Element)
        mock_element.is_enabled = Mock(return_value=False)

        should = Should(mock_element)

        result = should.not_be.enabled()

        assert isinstance(result, Should)

    def test_not_be_enabled_raises_when_enabled(self):
        """Test not_be.enabled raises when element is enabled."""
        mock_element = Mock(spec=Element)
        mock_element.is_enabled = Mock(return_value=True)

        should = Should(mock_element)

        with pytest.raises(AssertionError) as exc_info:
            should.not_be.enabled()

        assert "[should.not]" in str(exc_info.value)

    def test_not_be_visible_passes_when_not_visible(self):
        """Test not_be.visible passes when element is not visible."""
        mock_element = Mock(spec=Element)
        mock_element.is_visible = Mock(return_value=False)

        should = Should(mock_element)

        result = should.not_be.visible()

        assert isinstance(result, Should)

    def test_not_be_visible_raises_when_visible(self):
        """Test not_be.visible raises when element is visible."""
        mock_element = Mock(spec=Element)
        mock_element.is_visible = Mock(return_value=True)

        should = Should(mock_element)

        with pytest.raises(AssertionError) as exc_info:
            should.not_be.visible()

        assert "[should.not]" in str(exc_info.value)


class TestMethodChaining:
    """Test method chaining capability."""

    def test_chaining_multiple_have_assertions(self):
        """Test chaining multiple have assertions."""
        mock_element = Mock(spec=Element)
        mock_element.get_attribute = Mock(side_effect=lambda x: {
            "resource-id": "test_id",
            "class": "android.widget.Button"
        }.get(x))

        should = Should(mock_element)

        # Chain multiple assertions
        result = should.have.resource_id("test_id").have.class_name("android.widget.Button")

        assert isinstance(result, Should)

    def test_chaining_have_and_be_assertions(self):
        """Test chaining have and be assertions."""
        mock_element = Mock(spec=Element)
        type(mock_element).text = PropertyMock(return_value="Button")
        mock_element.is_enabled = Mock(return_value=True)

        should = Should(mock_element)

        # Chain have and be assertions
        result = should.have.text("Button").be.enabled()

        assert isinstance(result, Should)

