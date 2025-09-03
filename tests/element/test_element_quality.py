"""
Tests for element module quality improvements.

This module tests the quality improvements made to the element module,
including proper error handling, type annotations, and code standards.
"""

from unittest.mock import Mock

import pytest

from shadowstep.element.base import ElementBase
from shadowstep.element.conditions import (
    clickable,
    not_clickable,
    not_present,
    not_visible,
    present,
    visible,
)
from shadowstep.element.element import Element, GeneralElementException
from shadowstep.element.should import Should, _ShouldBe, _ShouldHave, _ShouldNotBe, _ShouldNotHave


class TestElementQuality:
    """Test class for element module quality improvements."""

    def test_element_base_initialization(self):
        """Test ElementBase initialization with proper types."""
        mock_base = Mock()
        locator = ("xpath", "//test")
        
        element_base = ElementBase(
            locator=locator,
            base=mock_base,
            timeout=30.0,
            poll_frequency=0.5,
            contains=False
        )
        
        assert element_base.locator == locator  # noqa: S101
        assert element_base.base == mock_base  # noqa: S101, S101
        assert element_base.timeout == 30.0  # noqa: S101
        assert element_base.poll_frequency == 0.5  # noqa: S101
        assert element_base.contains is False  # noqa: S101

    def test_element_initialization(self):
        """Test Element initialization with proper types."""
        mock_base = Mock()
        locator = {"class": "test", "text": "test"}
        
        element = Element(
            locator=locator,
            base=mock_base,
            timeout=30.0,
            poll_frequency=0.5,
            contains=False
        )
        
        assert element.locator == locator  # noqa: S101
        assert element.base == mock_base  # noqa: S101
        assert element.timeout == 30.0  # noqa: S101
        assert element.poll_frequency == 0.5  # noqa: S101
        assert element.contains is False  # noqa: S101

    def test_handle_dict_locator_with_class(self):
        """Test handle_dict_locator with class attribute."""
        mock_base = Mock()
        element_base = ElementBase(
            locator=("xpath", "//test"),
            base=mock_base
        )
        
        locator = {"class": "Button", "text": "Click me"}
        result = element_base.handle_dict_locator(locator)
        
        assert result == ("xpath", "//Button[@class='Button'][@text='Click me']")  # noqa: S101

    def test_handle_dict_locator_without_class(self):
        """Test handle_dict_locator without class attribute."""
        mock_base = Mock()
        element_base = ElementBase(
            locator=("xpath", "//test"),
            base=mock_base
        )
        
        locator = {"text": "Click me", "resource-id": "button1"}
        result = element_base.handle_dict_locator(locator)
        
        assert result == ("xpath", "//*[@text='Click me'][@resource-id='button1']")  # noqa: S101

    def test_handle_dict_locator_with_contains(self):
        """Test handle_dict_locator with contains=True."""
        mock_base = Mock()
        element_base = ElementBase(
            locator=("xpath", "//test"),
            base=mock_base
        )
        
        locator = {"class": "Button", "text": "Click me"}
        result = element_base.handle_dict_locator(locator, contains=True)
        
        assert result == ("xpath", "//Button[contains(@class, 'Button')][contains(@text, 'Click me')]")  # noqa: S101

    def test_handle_dict_locator_error_handling(self):
        """Test handle_dict_locator error handling."""
        mock_base = Mock()
        element_base = ElementBase(
            locator=("xpath", "//test"),
            base=mock_base
        )
        
        # Test with invalid locator that should raise KeyError
        locator = {}
        result = element_base.handle_dict_locator(locator)
        
        # Should return xpath with wildcard on empty locator
        assert result == ("xpath", "//*")  # noqa: S101

    def test_conditions_visible(self):
        """Test visible condition function."""
        locator = ("xpath", "//test")
        condition = visible(locator)
        
        assert callable(condition)  # noqa: S101  # noqa: S101  # pyright: ignore [reportUnknownArgumentType]

    def test_conditions_not_visible(self):
        """Test not_visible condition function."""
        locator = ("xpath", "//test")
        condition = not_visible(locator)
        
        assert callable(condition)  # noqa: S101

    def test_conditions_clickable(self):
        """Test clickable condition function."""
        locator = ("xpath", "//test")
        condition = clickable(locator)
        
        assert callable(condition)  # noqa: S101

    def test_conditions_not_clickable(self):
        """Test not_clickable condition function."""
        locator = ("xpath", "//test")
        condition = not_clickable(locator)
        
        assert callable(condition)  # noqa: S101
        assert condition.__name__ == "_predicate"  # noqa: S101

    def test_conditions_present(self):
        """Test present condition function."""
        locator = ("xpath", "//test")
        condition = present(locator)
        
        assert callable(condition)  # noqa: S101

    def test_conditions_not_present(self):
        """Test not_present condition function."""
        locator = ("xpath", "//test")
        condition = not_present(locator)
        
        assert callable(condition)  # noqa: S101
        assert condition.__name__ == "_predicate"  # noqa: S101

    def test_should_initialization(self):
        """Test Should class initialization."""
        mock_element = Mock()
        should = Should(mock_element)
        
        assert should.element == mock_element  # noqa: S101
        assert isinstance(should.have, _ShouldHave)  # noqa: S101
        assert isinstance(should.not_have, _ShouldNotHave)  # noqa: S101
        assert isinstance(should.be, _ShouldBe)  # noqa: S101
        assert isinstance(should.not_be, _ShouldNotBe)  # noqa: S101

    def test_should_have_text(self):
        """Test should.have.text assertion."""
        mock_element = Mock()
        mock_element.text = "test text"
        
        should = Should(mock_element)
        
        # Should not raise exception for matching text
        result = should.have.text("test text")
        assert isinstance(result, Should)  # noqa: S101

    def test_should_have_text_failure(self):
        """Test should.have.text assertion failure."""
        mock_element = Mock()
        mock_element.text = "different text"
        
        should = Should(mock_element)
        
        # Should raise AssertionError for non-matching text
        with pytest.raises(AssertionError, match="have.text: expected 'test text', got 'different text'"):
            should.have.text("test text")

    def test_should_not_have_text(self):
        """Test should.not_have.text assertion."""
        mock_element = Mock()
        mock_element.text = "different text"
        
        should = Should(mock_element)
        
        # Should not raise exception for non-matching text
        result = should.not_have.text("test text")
        assert isinstance(result, Should)  # noqa: S101

    def test_should_not_have_text_failure(self):
        """Test should.not_have.text assertion failure."""
        mock_element = Mock()
        mock_element.text = "test text"
        
        should = Should(mock_element)
        
        # Should raise AssertionError for matching text
        with pytest.raises(AssertionError, match="\\[should.not\\] have.text: expected 'test text', got 'test text'"):
            should.not_have.text("test text")

    def test_should_be_enabled(self):
        """Test should.be.enabled assertion."""
        mock_element = Mock()
        mock_element.is_enabled.return_value = True
        
        should = Should(mock_element)
        
        # Should not raise exception for enabled element
        result = should.be.enabled()
        assert isinstance(result, Should)  # noqa: S101

    def test_should_be_enabled_failure(self):
        """Test should.be.enabled assertion failure."""
        mock_element = Mock()
        mock_element.is_enabled.return_value = False
        
        should = Should(mock_element)
        
        # Should raise AssertionError for disabled element
        with pytest.raises(AssertionError, match="be.enabled: expected element to be enabled"):
            should.be.enabled()

    def test_should_not_be_enabled(self):
        """Test should.not_be.enabled assertion."""
        mock_element = Mock()
        mock_element.is_enabled.return_value = False
        
        should = Should(mock_element)
        
        # Should not raise exception for disabled element
        result = should.not_be.enabled()
        assert isinstance(result, Should)  # noqa: S101

    def test_should_not_be_enabled_failure(self):
        """Test should.not_be.enabled assertion failure."""
        mock_element = Mock()
        mock_element.is_enabled.return_value = True
        
        should = Should(mock_element)
        
        # Should raise AssertionError for enabled element
        with pytest.raises(AssertionError, match="\\[should.not\\] be.enabled: expected element to be enabled"):
            should.not_be.enabled()

    def test_should_have_attr(self):
        """Test should.have.attr assertion."""
        mock_element = Mock()
        mock_element.get_attribute.return_value = "test value"
        
        should = Should(mock_element)
        
        # Should not raise exception for matching attribute
        result = should.have.attr("test_attr", "test value")
        assert isinstance(result, Should)  # noqa: S101

    def test_should_have_attr_failure(self):
        """Test should.have.attr assertion failure."""
        mock_element = Mock()
        mock_element.get_attribute.return_value = "different value"
        
        should = Should(mock_element)
        
        # Should raise AssertionError for non-matching attribute
        with pytest.raises(AssertionError, match="have.attr\\('test_attr'\\): expected 'test value', got 'different value'"):
            should.have.attr("test_attr", "test value")

    def test_element_repr(self):
        """Test Element __repr__ method."""
        mock_base = Mock()
        locator = ("xpath", "//test")
        
        element = Element(
            locator=locator,
            base=mock_base
        )
        
        repr_str = repr(element)
        assert "Element(locator=('xpath', '//test')" in repr_str  # noqa: S101

    def test_general_element_exception(self):
        """Test GeneralElementException initialization."""
        exception = GeneralElementException(
            msg="Test error",
            screen="screenshot.png",
            stacktrace=["trace1", "trace2"]
        )
        
        assert exception.msg == "Test error"  # noqa: S101
        assert exception.screen == "screenshot.png"  # noqa: S101
        assert exception.stacktrace == ["trace1", "trace2"]  # noqa: S101

    def test_element_getattr_delegation(self):
        """Test Should __getattr__ delegation to underlying element."""
        mock_element = Mock()
        mock_element.test_method.return_value = "test result"
        
        should = Should(mock_element)
        
        # Should delegate to underlying element
        result = should.test_method()
        assert result == "test result"  # noqa: S101

    def test_element_getattr_error(self):
        """Test Should __getattr__ error handling."""
        mock_element = Mock()
        # Mock element that doesn't have the attribute
        del mock_element.nonexistent
        
        should = Should(mock_element)
        
        # Should raise AttributeError with proper message
        with pytest.raises(AttributeError, match="'Should' has no attribute 'nonexistent'"):
            _ = should.nonexistent  # noqa: B018


class TestElementTypeAnnotations:
    """Test class for type annotation improvements."""

    def test_element_type_annotations(self):
        """Test that Element class has proper type annotations."""
        # Check that Element class has proper type hints
        annotations = Element.__init__.__annotations__
        
        assert "locator" in annotations  # noqa: S101
        assert "base" in annotations  # noqa: S101
        assert "timeout" in annotations  # noqa: S101
        assert "poll_frequency" in annotations  # noqa: S101
        assert "ignored_exceptions" in annotations  # noqa: S101
        assert "contains" in annotations  # noqa: S101
        assert "native" in annotations  # noqa: S101

    def test_element_base_type_annotations(self):
        """Test that ElementBase class has proper type annotations."""
        # Check that ElementBase class has proper type hints
        annotations = ElementBase.__init__.__annotations__
        
        assert "locator" in annotations  # noqa: S101
        assert "base" in annotations  # noqa: S101
        assert "timeout" in annotations  # noqa: S101
        assert "poll_frequency" in annotations  # noqa: S101
        assert "ignored_exceptions" in annotations  # noqa: S101
        assert "contains" in annotations  # noqa: S101
        assert "native" in annotations  # noqa: S101

    def test_conditions_type_annotations(self):
        """Test that conditions functions have proper type annotations."""
        # Check that condition functions have proper type hints
        assert hasattr(visible, "__annotations__")  # noqa: S101
        assert hasattr(not_visible, "__annotations__")  # noqa: S101
        assert hasattr(clickable, "__annotations__")  # noqa: S101
        assert hasattr(not_clickable, "__annotations__")  # noqa: S101
        assert hasattr(present, "__annotations__")  # noqa: S101
        assert hasattr(not_present, "__annotations__")  # noqa: S101

    def test_should_type_annotations(self):
        """Test that Should class has proper type annotations."""
        # Check that Should class has proper type hints
        annotations = Should.__init__.__annotations__
        
        assert "element" in annotations  # noqa: S101
