# ruff: noqa
# pyright: ignore
"""Unit tests for ElementActions class using mocks."""
from unittest.mock import Mock, patch

import pytest

from shadowstep.element.actions import ElementActions
from shadowstep.element.element import Element


class TestElementActionsInit:
    """Test ElementActions initialization."""

    def test_init_creates_instance_with_element(self):
        """Test initialization creates instance with element reference."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        actions = ElementActions(mock_element)

        assert actions.element == mock_element
        assert actions.shadowstep == mock_shadowstep
        assert actions.converter == mock_element.converter
        assert actions.utilities == mock_element.utilities
        assert actions.logger is not None


class TestSendKeys:
    """Test send_keys method."""

    def test_send_keys_with_single_string(self):
        """Test send_keys with single string argument."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.send_keys = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        result = actions.send_keys("test text")

        mock_element.get_driver.assert_called_once()
        mock_element.get_native.assert_called_once()
        mock_native.send_keys.assert_called_once_with("test text")
        assert result == mock_element

    def test_send_keys_with_multiple_strings(self):
        """Test send_keys with multiple string arguments."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.send_keys = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        result = actions.send_keys("Hello", " ", "World")

        mock_native.send_keys.assert_called_once_with("Hello World")
        assert result == mock_element

    def test_send_keys_with_empty_string(self):
        """Test send_keys with empty string."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.send_keys = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        result = actions.send_keys("")

        mock_native.send_keys.assert_called_once_with("")
        assert result == mock_element

    def test_send_keys_returns_element_for_chaining(self):
        """Test send_keys returns element for method chaining."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.send_keys = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        result = actions.send_keys("text")

        assert result is mock_element


class TestClear:
    """Test clear method."""

    def test_clear_calls_native_clear(self):
        """Test clear calls native element's clear method."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.clear = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        result = actions.clear()

        mock_element.get_driver.assert_called_once()
        mock_element.get_native.assert_called_once()
        mock_native.clear.assert_called_once()
        assert result == mock_element

    def test_clear_returns_element_for_chaining(self):
        """Test clear returns element for method chaining."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.clear = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        result = actions.clear()

        assert result is mock_element


class TestSetValue:
    """Test set_value method."""

    def test_set_value_calls_native_set_value(self):
        """Test set_value calls native element's set_value method."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.set_value = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        result = actions.set_value("new value")

        mock_element.get_driver.assert_called_once()
        mock_element.get_native.assert_called_once()
        mock_native.set_value.assert_called_once_with("new value")
        assert result == mock_element

    def test_set_value_logs_warning_about_uiautomator2(self):
        """Test set_value logs warning that method is not implemented in UiAutomator2."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.set_value = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        with patch.object(actions.logger, 'warning') as mock_warning:
            result = actions.set_value("value")

            # Verify warning was logged
            mock_warning.assert_called_once()
            call_args = mock_warning.call_args[0]
            assert "set_value" in str(call_args)
            assert "not implemented" in str(call_args)

    def test_set_value_returns_element_for_chaining(self):
        """Test set_value returns element for method chaining."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.set_value = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        result = actions.set_value("value")

        assert result is mock_element

    def test_set_value_with_empty_string(self):
        """Test set_value with empty string."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.set_value = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        result = actions.set_value("")

        mock_native.set_value.assert_called_once_with("")
        assert result == mock_element


class TestSubmit:
    """Test submit method."""

    def test_submit_calls_native_submit(self):
        """Test submit calls native element's submit method."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.submit = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        result = actions.submit()

        mock_element.get_driver.assert_called_once()
        mock_element.get_native.assert_called_once()
        mock_native.submit.assert_called_once()
        assert result == mock_element

    def test_submit_logs_warning_about_uiautomator2(self):
        """Test submit logs warning that method is not implemented in UiAutomator2."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.submit = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        with patch.object(actions.logger, 'warning') as mock_warning:
            result = actions.submit()

            # Verify warning was logged
            mock_warning.assert_called_once()
            call_args = mock_warning.call_args[0]
            assert "submit" in str(call_args)
            assert "not implemented" in str(call_args)

    def test_submit_returns_element_for_chaining(self):
        """Test submit returns element for method chaining."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        mock_driver = Mock()
        mock_element.get_driver = Mock(return_value=mock_driver)

        mock_native = Mock()
        mock_native.submit = Mock()
        mock_element.get_native = Mock(return_value=mock_native)

        actions = ElementActions(mock_element)

        result = actions.submit()

        assert result is mock_element

