# ruff: noqa
# pyright: ignore
"""Unit tests for shadowstep/element/should.py module."""
from typing import Any
from unittest.mock import Mock, patch
import pytest

from shadowstep.element.should import Should, _ShouldHave, _ShouldBe, _ShouldNotHave, _ShouldNotBe
from shadowstep.shadowstep import Shadowstep


class TestShould:
    """Test suite for Should class."""

    def _create_test_element(self, mock_driver: Mock) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        return app, el

    # Tests for Should __init__ method
    @pytest.mark.unit
    def test_should_initialization(self):
        """Test Should initialization."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        should = Should(el)
        
        assert should.element is el
        assert isinstance(should.have, _ShouldHave)
        assert isinstance(should.not_have, _ShouldNotHave)
        assert isinstance(should.be, _ShouldBe)
        assert isinstance(should.not_be, _ShouldNotBe)

    # Tests for Should __getattr__ method
    @pytest.mark.unit
    def test_should_getattr_delegates_to_element(self):
        """Test Should delegates attribute access to element."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//test")
        
        should = Should(el)
        
        # Should delegate to element.locator
        assert should.locator == el.locator

    @pytest.mark.unit
    def test_should_getattr_raises_error_for_unknown_attribute(self):
        """Test Should raises AttributeError for unknown attribute."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        should = Should(el)
        
        with pytest.raises(AttributeError) as exc_info:
            _ = should.nonexistent_attribute
        
        assert "'Should' has no attribute 'nonexistent_attribute'" in str(exc_info.value)


class TestShouldHave:
    """Test suite for _ShouldHave class."""

    def _create_test_element(self, mock_driver: Mock) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        return app, el

    # Tests for text method
    @pytest.mark.unit
    def test_have_text_success(self):
        """Test have.text assertion passes when text matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.properties, 'text', return_value="Expected Text"):
            result = el.should.have.text("Expected Text")
        
        assert isinstance(result, Should)
        assert result.element is el

    @pytest.mark.unit
    def test_have_text_fails_when_text_does_not_match(self):
        """Test have.text assertion fails when text does not match."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.properties, 'text', return_value="Actual Text"):
            with pytest.raises(AssertionError) as exc_info:
                el.should.have.text("Expected Text")
        
        assert "[should] have.text: expected 'Expected Text', got 'Actual Text'" in str(exc_info.value)

    # Tests for resource_id method
    @pytest.mark.unit
    def test_have_resource_id_success(self):
        """Test have.resource_id assertion passes when resource-id matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="com.example:id/button"):
            result = el.should.have.resource_id("com.example:id/button")
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_have_resource_id_fails_when_does_not_match(self):
        """Test have.resource_id assertion fails when resource-id does not match."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="com.example:id/other"):
            with pytest.raises(AssertionError) as exc_info:
                el.should.have.resource_id("com.example:id/button")
        
        assert "[should] have.resource_id" in str(exc_info.value)

    # Tests for content_desc method
    @pytest.mark.unit
    def test_have_content_desc_success(self):
        """Test have.content_desc assertion passes when content-desc matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="Submit button"):
            result = el.should.have.content_desc("Submit button")
        
        assert isinstance(result, Should)

    # Tests for class_name method
    @pytest.mark.unit
    def test_have_class_name_success(self):
        """Test have.class_name assertion passes when class matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="android.widget.Button"):
            result = el.should.have.class_name("android.widget.Button")
        
        assert isinstance(result, Should)

    # Tests for package method
    @pytest.mark.unit
    def test_have_package_success(self):
        """Test have.package assertion passes when package matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="com.example.app"):
            result = el.should.have.package("com.example.app")
        
        assert isinstance(result, Should)

    # Tests for bounds method
    @pytest.mark.unit
    def test_have_bounds_success(self):
        """Test have.bounds assertion passes when bounds matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="[0,0][100,100]"):
            result = el.should.have.bounds("[0,0][100,100]")
        
        assert isinstance(result, Should)

    # Tests for id method
    @pytest.mark.unit
    def test_have_id_success(self):
        """Test have.id assertion passes when id matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="button1"):
            result = el.should.have.id("button1")
        
        assert isinstance(result, Should)

    # Tests for index method
    @pytest.mark.unit
    def test_have_index_success(self):
        """Test have.index assertion passes when index matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="5"):
            result = el.should.have.index("5")
        
        assert isinstance(result, Should)

    # Tests for attr method
    @pytest.mark.unit
    def test_have_attr_success(self):
        """Test have.attr assertion passes when attribute matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="test-value"):
            result = el.should.have.attr("custom-attr", "test-value")
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_have_attr_fails_when_does_not_match(self):
        """Test have.attr assertion fails when attribute does not match."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="actual-value"):
            with pytest.raises(AssertionError) as exc_info:
                el.should.have.attr("custom-attr", "expected-value")
        
        assert "[should] have.attr('custom-attr')" in str(exc_info.value)


class TestShouldBe:
    """Test suite for _ShouldBe class."""

    def _create_test_element(self, mock_driver: Mock) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        return app, el

    # Tests for enabled method
    @pytest.mark.unit
    def test_be_enabled_success(self):
        """Test be.enabled assertion passes when element is enabled."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_enabled', return_value=True):
            result = el.should.be.enabled()
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_be_enabled_fails_when_disabled(self):
        """Test be.enabled assertion fails when element is disabled."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_enabled', return_value=False):
            with pytest.raises(AssertionError) as exc_info:
                el.should.be.enabled()
        
        assert "[should] be.enabled" in str(exc_info.value)

    # Tests for disabled method
    @pytest.mark.unit
    def test_be_disabled_success(self):
        """Test be.disabled assertion passes when element is disabled."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_enabled', return_value=False):
            result = el.should.be.disabled()
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_be_disabled_fails_when_enabled(self):
        """Test be.disabled assertion fails when element is enabled."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_enabled', return_value=True):
            with pytest.raises(AssertionError) as exc_info:
                el.should.be.disabled()
        
        assert "[should] be.disabled" in str(exc_info.value)

    # Tests for selected method
    @pytest.mark.unit
    def test_be_selected_success(self):
        """Test be.selected assertion passes when element is selected."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_selected', return_value=True):
            result = el.should.be.selected()
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_be_selected_fails_when_not_selected(self):
        """Test be.selected assertion fails when element is not selected."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_selected', return_value=False):
            with pytest.raises(AssertionError) as exc_info:
                el.should.be.selected()
        
        assert "[should] be.selected" in str(exc_info.value)

    # Tests for focused method
    @pytest.mark.unit
    def test_be_focused_success(self):
        """Test be.focused assertion passes when element is focused."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="true"):
            result = el.should.be.focused()
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_be_focused_fails_when_not_focused(self):
        """Test be.focused assertion fails when element is not focused."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="false"):
            with pytest.raises(AssertionError) as exc_info:
                el.should.be.focused()
        
        assert "[should] be.focused" in str(exc_info.value)

    # Tests for focusable method
    @pytest.mark.unit
    def test_be_focusable_success(self):
        """Test be.focusable assertion passes when element is focusable."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="true"):
            result = el.should.be.focusable()
        
        assert isinstance(result, Should)

    # Tests for long_clickable method
    @pytest.mark.unit
    def test_be_long_clickable_success(self):
        """Test be.long_clickable assertion passes when element is long-clickable."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="true"):
            result = el.should.be.long_clickable()
        
        assert isinstance(result, Should)

    # Tests for visible method
    @pytest.mark.unit
    def test_be_visible_success(self):
        """Test be.visible assertion passes when element is visible."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_visible', return_value=True):
            result = el.should.be.visible()
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_be_visible_fails_when_not_visible(self):
        """Test be.visible assertion fails when element is not visible."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_visible', return_value=False):
            with pytest.raises(AssertionError) as exc_info:
                el.should.be.visible()
        
        assert "[should] be.visible" in str(exc_info.value)

    # Tests for displayed method
    @pytest.mark.unit
    def test_be_displayed_calls_visible(self):
        """Test be.displayed calls visible method."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_visible', return_value=True):
            result = el.should.be.displayed()
        
        assert isinstance(result, Should)

    # Tests for checkable method
    @pytest.mark.unit
    def test_be_checkable_success(self):
        """Test be.checkable assertion passes when element is checkable."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="true"):
            result = el.should.be.checkable()
        
        assert isinstance(result, Should)

    # Tests for checked method
    @pytest.mark.unit
    def test_be_checked_success(self):
        """Test be.checked assertion passes when element is checked."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="true"):
            result = el.should.be.checked()
        
        assert isinstance(result, Should)

    # Tests for scrollable method
    @pytest.mark.unit
    def test_be_scrollable_success(self):
        """Test be.scrollable assertion passes when element is scrollable."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="true"):
            result = el.should.be.scrollable()
        
        assert isinstance(result, Should)

    # Tests for password method
    @pytest.mark.unit
    def test_be_password_success(self):
        """Test be.password assertion passes when element is password field."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="true"):
            result = el.should.be.password()
        
        assert isinstance(result, Should)


class TestShouldNotHave:
    """Test suite for _ShouldNotHave class."""

    def _create_test_element(self, mock_driver: Mock) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        return app, el

    # Tests for negative text assertion
    @pytest.mark.unit
    def test_not_have_text_success(self):
        """Test not_have.text assertion passes when text does not match."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.properties, 'text', return_value="Actual Text"):
            result = el.should.not_have.text("Different Text")
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_not_have_text_fails_when_text_matches(self):
        """Test not_have.text assertion fails when text matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.properties, 'text', return_value="Same Text"):
            with pytest.raises(AssertionError) as exc_info:
                el.should.not_have.text("Same Text")
        
        assert "[should.not] have.text" in str(exc_info.value)

    # Tests for negative resource_id assertion
    @pytest.mark.unit
    def test_not_have_resource_id_success(self):
        """Test not_have.resource_id assertion passes when resource-id does not match."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="com.example:id/button"):
            result = el.should.not_have.resource_id("com.example:id/other")
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_not_have_resource_id_fails_when_matches(self):
        """Test not_have.resource_id assertion fails when resource-id matches."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="com.example:id/button"):
            with pytest.raises(AssertionError) as exc_info:
                el.should.not_have.resource_id("com.example:id/button")
        
        assert "[should.not] have.resource_id" in str(exc_info.value)

    # Tests for negative attr assertion
    @pytest.mark.unit
    def test_not_have_attr_success(self):
        """Test not_have.attr assertion passes when attribute does not match."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="actual"):
            result = el.should.not_have.attr("custom", "expected")
        
        assert isinstance(result, Should)


class TestShouldNotBe:
    """Test suite for _ShouldNotBe class."""

    def _create_test_element(self, mock_driver: Mock) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        return app, el

    # Tests for negative enabled assertion
    @pytest.mark.unit
    def test_not_be_enabled_success(self):
        """Test not_be.enabled assertion passes when element is disabled."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_enabled', return_value=False):
            result = el.should.not_be.enabled()
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_not_be_enabled_fails_when_enabled(self):
        """Test not_be.enabled assertion fails when element is enabled."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_enabled', return_value=True):
            with pytest.raises(AssertionError) as exc_info:
                el.should.not_be.enabled()
        
        assert "[should.not] be.enabled" in str(exc_info.value)

    # Tests for negative disabled assertion
    @pytest.mark.unit
    def test_not_be_disabled_success(self):
        """Test not_be.disabled assertion passes when element is enabled."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_enabled', return_value=True):
            result = el.should.not_be.disabled()
        
        assert isinstance(result, Should)

    # Tests for negative selected assertion
    @pytest.mark.unit
    def test_not_be_selected_success(self):
        """Test not_be.selected assertion passes when element is not selected."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_selected', return_value=False):
            result = el.should.not_be.selected()
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_not_be_selected_fails_when_selected(self):
        """Test not_be.selected assertion fails when element is selected."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_selected', return_value=True):
            with pytest.raises(AssertionError) as exc_info:
                el.should.not_be.selected()
        
        assert "[should.not] be.selected" in str(exc_info.value)

    # Tests for negative visible assertion
    @pytest.mark.unit
    def test_not_be_visible_success(self):
        """Test not_be.visible assertion passes when element is not visible."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_visible', return_value=False):
            result = el.should.not_be.visible()
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_not_be_visible_fails_when_visible(self):
        """Test not_be.visible assertion fails when element is visible."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'is_visible', return_value=True):
            with pytest.raises(AssertionError) as exc_info:
                el.should.not_be.visible()
        
        assert "[should.not] be.visible" in str(exc_info.value)

    # Tests for negative focused assertion
    @pytest.mark.unit
    def test_not_be_focused_success(self):
        """Test not_be.focused assertion passes when element is not focused."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="false"):
            result = el.should.not_be.focused()
        
        assert isinstance(result, Should)

    # Tests for negative checked assertion
    @pytest.mark.unit
    def test_not_be_checked_success(self):
        """Test not_be.checked assertion passes when element is not checked."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="false"):
            result = el.should.not_be.checked()
        
        assert isinstance(result, Should)


class TestShouldChaining:
    """Test suite for method chaining in Should assertions."""

    def _create_test_element(self, mock_driver: Mock) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        return app, el

    @pytest.mark.unit
    def test_chaining_multiple_have_assertions(self):
        """Test chaining multiple have assertions."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        def mock_get_attribute(name):
            attrs = {
                "resource-id": "com.example:id/button",
                "class": "android.widget.Button",
                "text": "Submit"
            }
            return attrs.get(name, "")
        
        with patch.object(el, 'get_attribute', side_effect=mock_get_attribute):
            with patch.object(el.properties, 'text', return_value="Submit"):
                result = (el.should
                         .have.text("Submit")
                         .have.resource_id("com.example:id/button")
                         .have.class_name("android.widget.Button"))
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_chaining_have_and_be_assertions(self):
        """Test chaining have and be assertions."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.properties, 'text', return_value="Test"):
            with patch.object(el, 'is_enabled', return_value=True):
                with patch.object(el, 'is_visible', return_value=True):
                    result = (el.should
                             .have.text("Test")
                             .be.enabled()
                             .be.visible())
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_chaining_not_have_and_not_be_assertions(self):
        """Test chaining negative assertions."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.properties, 'text', return_value="Actual"):
            with patch.object(el, 'is_selected', return_value=False):
                result = (el.should
                         .not_have.text("Different")
                         .not_be.selected())
        
        assert isinstance(result, Should)


class TestShouldBaseAssert:
    """Test suite for _ShouldBase._assert method."""

    def _create_test_element(self, mock_driver: Mock) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        return app, el

    @pytest.mark.unit
    def test_assert_passes_when_condition_true_and_not_negated(self):
        """Test _assert passes when condition is True and not negated."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        should_have = _ShouldHave(el, negate=False)
        
        # Should not raise
        should_have._assert(True, "test message")

    @pytest.mark.unit
    def test_assert_raises_when_condition_false_and_not_negated(self):
        """Test _assert raises when condition is False and not negated."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        should_have = _ShouldHave(el, negate=False)
        
        with pytest.raises(AssertionError) as exc_info:
            should_have._assert(False, "test message")
        
        assert "[should] test message" in str(exc_info.value)

    @pytest.mark.unit
    def test_assert_passes_when_condition_false_and_negated(self):
        """Test _assert passes when condition is False and negated."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        should_not_have = _ShouldNotHave(el)
        
        # Should not raise (negated, condition False)
        should_not_have._assert(False, "test message")

    @pytest.mark.unit
    def test_assert_raises_when_condition_true_and_negated(self):
        """Test _assert raises when condition is True and negated."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        should_not_have = _ShouldNotHave(el)
        
        with pytest.raises(AssertionError) as exc_info:
            should_not_have._assert(True, "test message")
        
        assert "[should.not] test message" in str(exc_info.value)


class TestShouldEdgeCases:
    """Test suite for edge cases in Should assertions."""

    def _create_test_element(self, mock_driver: Mock) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        return app, el

    @pytest.mark.unit
    def test_have_text_with_empty_string(self):
        """Test have.text with empty string."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.properties, 'text', return_value=""):
            result = el.should.have.text("")
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_have_attr_with_none_value(self):
        """Test have.attr with None value."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value=None):
            result = el.should.have.attr("nullable-attr", None)
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_have_attr_with_numeric_value(self):
        """Test have.attr with numeric value."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_attribute', return_value="123"):
            result = el.should.have.attr("count", "123")
        
        assert isinstance(result, Should)

    @pytest.mark.unit
    def test_should_not_have_initialization(self):
        """Test _ShouldNotHave initializes with negate=True."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        should_not_have = _ShouldNotHave(el)
        
        assert should_not_have.negate is True
        assert should_not_have.element is el

    @pytest.mark.unit
    def test_should_not_be_initialization(self):
        """Test _ShouldNotBe initializes with negate=True."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        should_not_be = _ShouldNotBe(el)
        
        assert should_not_be.negate is True
        assert should_not_be.element is el

