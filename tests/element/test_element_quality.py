# tests/element/test_element_quality.py
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
from shadowstep.element.element import Element
from shadowstep.element.should import Should, _ShouldBe, _ShouldHave, _ShouldNotBe, _ShouldNotHave
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_element_quality.py
"""

class TestElementQuality:

    def test_element_base_initialization(self):
        mock_base = Mock()
        locator = ("xpath", "//test")
        element_base = ElementBase(locator=locator, shadowstep=mock_base, timeout=30.0)
        assert element_base.locator == locator  # noqa: S101
        assert element_base.shadowstep == mock_base  # noqa: S101, S101
        assert element_base.timeout == 30.0  # noqa: S101
        assert element_base.poll_frequency == 0.5  # noqa: S101

    def test_element_initialization(self):
        mock_base = Mock()
        locator = {"class": "test", "text": "test"}
        element = Element(locator=locator, shadowstep=mock_base, timeout=30.0)
        assert element.locator == locator  # noqa: S101
        assert element.shadowstep == mock_base  # noqa: S101
        assert element.timeout == 30.0  # noqa: S101
        assert element.poll_frequency == 0.5  # noqa: S101

    def test_conditions_visible(self):
        locator = ("xpath", "//test")
        condition = visible(locator)
        assert callable(condition)  # noqa: S101  # noqa: S101  # pyright: ignore [reportUnknownArgumentType]

    def test_conditions_not_visible(self):
        locator = ("xpath", "//test")
        condition = not_visible(locator)
        assert callable(condition)  # noqa: S101

    def test_conditions_clickable(self):
        locator = ("xpath", "//test")
        condition = clickable(locator)
        assert callable(condition)  # noqa: S101

    def test_conditions_not_clickable(self):
        locator = ("xpath", "//test")
        condition = not_clickable(locator)
        assert callable(condition)  # noqa: S101
        assert condition.__name__ == "_predicate"  # noqa: S101

    def test_conditions_present(self):
        locator = ("xpath", "//test")
        condition = present(locator)
        assert callable(condition)  # noqa: S101

    def test_conditions_not_present(self):
        locator = ("xpath", "//test")
        condition = not_present(locator)
        assert callable(condition)  # noqa: S101
        assert condition.__name__ == "_predicate"  # noqa: S101

    def test_should_initialization(self):
        mock_element = Mock()
        should = Should(mock_element)

        assert should.element == mock_element  # noqa: S101
        assert isinstance(should.have, _ShouldHave)  # noqa: S101
        assert isinstance(should.not_have, _ShouldNotHave)  # noqa: S101
        assert isinstance(should.be, _ShouldBe)  # noqa: S101
        assert isinstance(should.not_be, _ShouldNotBe)  # noqa: S101

    def test_should_have_text(self):
        mock_element = Mock()
        mock_element.text = "test text"
        should = Should(mock_element)
        result = should.have.text("test text")
        assert isinstance(result, Should)  # noqa: S101

    def test_should_have_text_failure(self):
        mock_element = Mock()
        mock_element.text = "different text"
        should = Should(mock_element)
        with pytest.raises(AssertionError, match="have.text: expected 'test text', got 'different text'"):
            should.have.text("test text")

    def test_should_not_have_text(self):
        mock_element = Mock()
        mock_element.text = "different text"
        should = Should(mock_element)
        result = should.not_have.text("test text")
        assert isinstance(result, Should)  # noqa: S101

    def test_should_not_have_text_failure(self):
        mock_element = Mock()
        mock_element.text = "test text"
        should = Should(mock_element)
        with pytest.raises(AssertionError, match="\\[should.not\\] have.text: expected 'test text', got 'test text'"):
            should.not_have.text("test text")

    def test_should_be_enabled(self):
        mock_element = Mock()
        mock_element.is_enabled.return_value = True
        should = Should(mock_element)
        result = should.be.enabled()
        assert isinstance(result, Should)  # noqa: S101

    def test_should_be_enabled_failure(self):
        mock_element = Mock()
        mock_element.is_enabled.return_value = False
        should = Should(mock_element)
        with pytest.raises(AssertionError, match="be.enabled: expected element to be enabled"):
            should.be.enabled()

    def test_should_not_be_enabled(self):
        mock_element = Mock()
        mock_element.is_enabled.return_value = False
        should = Should(mock_element)
        result = should.not_be.enabled()
        assert isinstance(result, Should)  # noqa: S101

    def test_should_not_be_enabled_failure(self):
        mock_element = Mock()
        mock_element.is_enabled.return_value = True
        should = Should(mock_element)
        with pytest.raises(AssertionError, match="\\[should.not\\] be.enabled: expected element to be enabled"):
            should.not_be.enabled()

    def test_should_have_attr(self):
        mock_element = Mock()
        mock_element.get_attribute.return_value = "test value"
        should = Should(mock_element)
        result = should.have.attr("test_attr", "test value")
        assert isinstance(result, Should)  # noqa: S101

    def test_should_have_attr_failure(self):
        mock_element = Mock()
        mock_element.get_attribute.return_value = "different value"
        should = Should(mock_element)
        with pytest.raises(AssertionError,
                           match="have.attr\\('test_attr'\\): expected 'test value', got 'different value'"):
            should.have.attr("test_attr", "test value")

    def test_element_repr(self):
        mock_base = Mock()
        locator = ("xpath", "//test")
        element = Element(
            locator=locator,
            shadowstep=mock_base
        )
        repr_str = repr(element)
        assert "Element(locator=('xpath', '//test')" in repr_str  # noqa: S101

    def test_general_element_exception(self):
        exception = ShadowstepElementException(
            msg="Test error",
            screen="screenshot.png",
            stacktrace=["trace1", "trace2"]
        )

        assert exception.msg == "Test error"  # noqa: S101
        assert exception.screen == "screenshot.png"  # noqa: S101
        assert exception.stacktrace == ["trace1", "trace2"]  # noqa: S101

    def test_element_getattr_delegation(self):
        mock_element = Mock()
        mock_element.test_method.return_value = "test result"
        should = Should(mock_element)
        result = should.test_method()
        assert result == "test result"  # noqa: S101

    def test_element_getattr_error(self):
        mock_element = Mock()
        del mock_element.nonexistent
        should = Should(mock_element)
        with pytest.raises(AttributeError, match="'Should' has no attribute 'nonexistent'"):
            _ = should.nonexistent  # noqa: B018


class TestElementTypeAnnotations:

    def test_element_type_annotations(self):
        annotations = Element.__init__.__annotations__

        assert "locator" in annotations  # noqa: S101
        assert "shadowstep" in annotations  # noqa: S101
        assert "timeout" in annotations  # noqa: S101
        assert "poll_frequency" in annotations  # noqa: S101
        assert "ignored_exceptions" in annotations  # noqa: S101
        assert "native" in annotations  # noqa: S101

    def test_element_base_type_annotations(self):
        annotations = ElementBase.__init__.__annotations__

        assert "locator" in annotations  # noqa: S101
        assert "shadowstep" in annotations  # noqa: S101
        assert "timeout" in annotations  # noqa: S101
        assert "poll_frequency" in annotations  # noqa: S101
        assert "ignored_exceptions" in annotations  # noqa: S101
        assert "native" in annotations  # noqa: S101

    def test_conditions_type_annotations(self):
        assert hasattr(visible, "__annotations__")  # noqa: S101
        assert hasattr(not_visible, "__annotations__")  # noqa: S101
        assert hasattr(clickable, "__annotations__")  # noqa: S101
        assert hasattr(not_clickable, "__annotations__")  # noqa: S101
        assert hasattr(present, "__annotations__")  # noqa: S101
        assert hasattr(not_present, "__annotations__")  # noqa: S101

    def test_should_type_annotations(self):
        annotations = Should.__init__.__annotations__
        assert "element" in annotations  # noqa: S101
