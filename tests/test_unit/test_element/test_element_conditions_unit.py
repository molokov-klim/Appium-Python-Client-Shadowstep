"""Unit tests for shadowstep/element/conditions.py module."""
from unittest.mock import Mock, MagicMock, patch
import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from appium.webdriver.webelement import WebElement

from shadowstep.element.conditions import (
    visible,
    not_visible,
    clickable,
    not_clickable,
    present,
    not_present,
)


class TestConditions:
    """Test suite for conditions module."""

    @pytest.mark.unit
    def test_visible_returns_callable(self):
        """Test visible returns a callable condition."""
        locator = ("xpath", "//test")
        condition = visible(locator)
        assert callable(condition)

    @pytest.mark.unit
    def test_not_visible_returns_callable(self):
        """Test not_visible returns a callable condition."""
        locator = ("xpath", "//test")
        condition = not_visible(locator)
        assert callable(condition)

    @pytest.mark.unit
    def test_clickable_with_tuple_locator(self):
        """Test clickable with tuple locator."""
        locator = ("xpath", "//button")
        condition = clickable(locator)
        assert callable(condition)

    @pytest.mark.unit
    def test_clickable_with_web_element(self):
        """Test clickable with WebElement."""
        mock_element = Mock(spec=WebElement)
        condition = clickable(mock_element)
        assert callable(condition)

    @pytest.mark.unit
    def test_not_clickable_returns_callable(self):
        """Test not_clickable returns a callable condition."""
        locator = ("xpath", "//button")
        condition = not_clickable(locator)
        assert callable(condition)
        assert condition.__name__ == "_predicate"

    @pytest.mark.unit
    def test_not_clickable_returns_true_when_not_clickable(self):
        """Test not_clickable condition returns True when element is not clickable."""
        locator = ("xpath", "//button")
        mock_driver = Mock()
        
        # Mock the element_to_be_clickable to return False
        with patch(
            "shadowstep.element.conditions.expected_conditions.element_to_be_clickable"
        ) as mock_ec:
            mock_condition = Mock()
            mock_condition.return_value = False  # Element is not clickable
            mock_ec.return_value = mock_condition
            
            condition = not_clickable(locator)
            result = condition(mock_driver)
            
            assert result is True

    @pytest.mark.unit
    def test_not_clickable_returns_false_when_clickable(self):
        """Test not_clickable condition returns False when element is clickable."""
        locator = ("xpath", "//button")
        mock_driver = Mock()
        mock_element = Mock(spec=WebElement)
        
        # Mock the element_to_be_clickable to return element (truthy)
        with patch(
            "shadowstep.element.conditions.expected_conditions.element_to_be_clickable"
        ) as mock_ec:
            mock_condition = Mock()
            mock_condition.return_value = mock_element  # Element is clickable
            mock_ec.return_value = mock_condition
            
            condition = not_clickable(locator)
            result = condition(mock_driver)
            
            assert result is False

    @pytest.mark.unit
    def test_present_returns_callable(self):
        """Test present returns a callable condition."""
        locator = ("xpath", "//test")
        condition = present(locator)
        assert callable(condition)

    @pytest.mark.unit
    def test_not_present_returns_callable(self):
        """Test not_present returns a callable condition."""
        locator = ("xpath", "//test")
        condition = not_present(locator)
        assert callable(condition)
        assert condition.__name__ == "_predicate"

    @pytest.mark.unit
    def test_not_present_returns_true_on_no_such_element_exception(self):
        """Test not_present condition returns True when NoSuchElementException is raised."""
        locator = ("xpath", "//test")
        mock_driver = Mock()
        
        # Mock the presence_of_element_located to raise NoSuchElementException
        with patch(
            "shadowstep.element.conditions.expected_conditions.presence_of_element_located"
        ) as mock_ec:
            mock_condition = Mock()
            mock_condition.side_effect = NoSuchElementException("Element not found")
            mock_ec.return_value = mock_condition
            
            condition = not_present(locator)
            result = condition(mock_driver)
            
            assert result is True

    @pytest.mark.unit
    def test_not_present_returns_true_on_timeout_exception(self):
        """Test not_present condition returns True when TimeoutException is raised."""
        locator = ("xpath", "//test")
        mock_driver = Mock()
        
        # Mock the presence_of_element_located to raise TimeoutException
        with patch(
            "shadowstep.element.conditions.expected_conditions.presence_of_element_located"
        ) as mock_ec:
            mock_condition = Mock()
            mock_condition.side_effect = TimeoutException("Timeout")
            mock_ec.return_value = mock_condition
            
            condition = not_present(locator)
            result = condition(mock_driver)
            
            assert result is True

    @pytest.mark.unit
    def test_not_present_returns_false_when_element_is_present(self):
        """Test not_present condition returns False when element is present."""
        locator = ("xpath", "//test")
        mock_driver = Mock()
        mock_element = Mock(spec=WebElement)
        
        # Mock the presence_of_element_located to return element
        with patch(
            "shadowstep.element.conditions.expected_conditions.presence_of_element_located"
        ) as mock_ec:
            mock_condition = Mock()
            mock_condition.return_value = mock_element  # Element is present
            mock_ec.return_value = mock_condition
            
            condition = not_present(locator)
            result = condition(mock_driver)
            
            assert result is False

