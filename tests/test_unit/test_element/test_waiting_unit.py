# ruff: noqa
# pyright: ignore
"""Unit tests for ElementWaiting class using mocks."""
from unittest.mock import Mock, patch

import pytest
from selenium.common import TimeoutException

from shadowstep.element.element import Element
from shadowstep.element.waiting import ElementWaiting


class TestElementWaitingInit:
    """Test ElementWaiting initialization."""

    def test_init_creates_instance_with_element(self):
        """Test initialization creates instance with element reference."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        assert waiting.element == mock_element
        assert waiting.shadowstep == mock_shadowstep
        assert waiting.converter == mock_element.converter
        assert waiting.utilities == mock_element.utilities
        assert waiting.logger is not None


class TestWait:
    """Test wait method."""

    def test_wait_returns_element_when_present(self):
        """Test wait returns element when element is present."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch('shadowstep.element.waiting.WebDriverWait') as MockWait, \
             patch('shadowstep.element.waiting.conditions') as mock_conditions:
            mock_wait_instance = Mock()
            MockWait.return_value = mock_wait_instance
            mock_wait_instance.until = Mock()  # Element found
            mock_conditions.present = Mock(return_value=Mock())
            
            result = waiting.wait(timeout=10, poll_frequency=0.5, return_bool=False)
            
            assert result == mock_element
            MockWait.assert_called_once_with(mock_driver, 10, 0.5)

    def test_wait_returns_true_when_present_and_return_bool_true(self):
        """Test wait returns True when element is present and return_bool=True."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch('shadowstep.element.waiting.WebDriverWait') as MockWait, \
             patch('shadowstep.element.waiting.conditions') as mock_conditions:
            mock_wait_instance = Mock()
            MockWait.return_value = mock_wait_instance
            mock_wait_instance.until = Mock()
            mock_conditions.present = Mock(return_value=Mock())
            
            result = waiting.wait(timeout=5, return_bool=True)
            
            assert result is True

    def test_wait_returns_element_on_timeout(self):
        """Test wait returns element on timeout when return_bool=False."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch('shadowstep.element.waiting.WebDriverWait') as MockWait, \
             patch('shadowstep.element.waiting.conditions') as mock_conditions:
            mock_wait_instance = Mock()
            MockWait.return_value = mock_wait_instance
            mock_wait_instance.until = Mock(side_effect=TimeoutException("Timeout"))
            mock_conditions.present = Mock(return_value=Mock())
            
            result = waiting.wait(timeout=1, return_bool=False)
            
            assert result == mock_element

    def test_wait_returns_false_on_timeout_when_return_bool_true(self):
        """Test wait returns False on timeout when return_bool=True."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch('shadowstep.element.waiting.WebDriverWait') as MockWait, \
             patch('shadowstep.element.waiting.conditions') as mock_conditions:
            mock_wait_instance = Mock()
            MockWait.return_value = mock_wait_instance
            mock_wait_instance.until = Mock(side_effect=TimeoutException("Timeout"))
            mock_conditions.present = Mock(return_value=Mock())
            
            result = waiting.wait(timeout=1, return_bool=True)
            
            assert result is False


class TestWaitVisible:
    """Test wait_visible method."""

    def test_wait_visible_returns_element_when_visible(self):
        """Test wait_visible returns element when element is visible."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_visibility_with_locator', return_value=True):
            result = waiting.wait_visible(timeout=10, return_bool=False)
            
            assert result == mock_element

    def test_wait_visible_returns_true_when_visible_and_return_bool_true(self):
        """Test wait_visible returns True when visible and return_bool=True."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_visibility_with_locator', return_value=True):
            result = waiting.wait_visible(return_bool=True)
            
            assert result is True

    def test_wait_visible_returns_false_when_not_visible_and_return_bool_true(self):
        """Test wait_visible returns False when not visible and return_bool=True."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_visibility_with_locator', return_value=False):
            result = waiting.wait_visible(return_bool=True)
            
            assert result is False


class TestWaitClickable:
    """Test wait_clickable method."""

    def test_wait_clickable_returns_element_when_clickable(self):
        """Test wait_clickable returns element when element is clickable."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_clickability_with_locator', return_value=True):
            result = waiting.wait_clickable(timeout=10, return_bool=False)
            
            assert result == mock_element

    def test_wait_clickable_returns_true_when_clickable_and_return_bool_true(self):
        """Test wait_clickable returns True when clickable and return_bool=True."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_clickability_with_locator', return_value=True):
            result = waiting.wait_clickable(return_bool=True)
            
            assert result is True

    def test_wait_clickable_returns_false_when_not_clickable_and_return_bool_true(self):
        """Test wait_clickable returns False when not clickable and return_bool=True."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_clickability_with_locator', return_value=False):
            result = waiting.wait_clickable(return_bool=True)
            
            assert result is False


class TestWaitForNot:
    """Test wait_for_not method."""

    def test_wait_for_not_returns_element_when_not_present(self):
        """Test wait_for_not returns element when element is not present."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_not_present_with_locator', return_value=True):
            result = waiting.wait_for_not(return_bool=False)
            
            assert result == mock_element

    def test_wait_for_not_returns_true_when_not_present_and_return_bool_true(self):
        """Test wait_for_not returns True when not present and return_bool=True."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_not_present_with_locator', return_value=True):
            result = waiting.wait_for_not(return_bool=True)
            
            assert result is True


class TestWaitForNotVisible:
    """Test wait_for_not_visible method."""

    def test_wait_for_not_visible_returns_element_when_not_visible(self):
        """Test wait_for_not_visible returns element when not visible."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_not_visible_with_locator', return_value=True):
            result = waiting.wait_for_not_visible(return_bool=False)
            
            assert result == mock_element

    def test_wait_for_not_visible_returns_true_when_not_visible_and_return_bool_true(self):
        """Test wait_for_not_visible returns True when not visible and return_bool=True."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_not_visible_with_locator', return_value=True):
            result = waiting.wait_for_not_visible(return_bool=True)
            
            assert result is True


class TestWaitForNotClickable:
    """Test wait_for_not_clickable method."""

    def test_wait_for_not_clickable_returns_element_when_not_clickable(self):
        """Test wait_for_not_clickable returns element when not clickable."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_not_clickable_with_locator', return_value=True):
            result = waiting.wait_for_not_clickable(return_bool=False)
            
            assert result == mock_element

    def test_wait_for_not_clickable_returns_true_when_not_clickable_and_return_bool_true(self):
        """Test wait_for_not_clickable returns True when not clickable and return_bool=True."""
        mock_driver = Mock()
        mock_shadowstep = Mock()
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//test")
        mock_element.remove_null_value = Mock(side_effect=lambda x: x)
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//test"))
        mock_element.converter = mock_converter
        mock_element.utilities = Mock()

        waiting = ElementWaiting(mock_element)

        with patch.object(waiting, '_wait_for_not_clickable_with_locator', return_value=True):
            result = waiting.wait_for_not_clickable(return_bool=True)
            
            assert result is True
