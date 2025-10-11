# ruff: noqa
# pyright: ignore
"""Unit tests for shadowstep/element/dom.py module."""
from typing import Any
from unittest.mock import Mock, patch, MagicMock
import pytest

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.element.dom import ElementDOM
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepElementException,
    ShadowstepResolvingLocatorError,
)
from shadowstep.shadowstep import Shadowstep


class TestElementDOM:
    """Test suite for ElementDOM class."""

    def _create_test_element(self, mock_driver: Mock, timeout: float = 1.0) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        el.timeout = timeout
        return app, el

    # Tests for __init__ method
    @pytest.mark.unit
    def test_element_dom_initialization(self):
        """Test ElementDOM initialization."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        dom = ElementDOM(el)
        
        assert dom.element is el
        assert dom.shadowstep is el.shadowstep
        assert dom.converter is el.converter
        assert dom.utilities is el.utilities
        assert dom.logger is not None

    # Tests for get_element method
    @pytest.mark.unit
    def test_get_element_with_xpath_locator(self):
        """Test get_element with xpath parent and child locators."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//parent")
        
        child_locator = ("xpath", "//child")
        
        result = el.dom.get_element(child_locator)
        
        assert result is not None
        assert isinstance(result.locator, tuple)
        assert result.locator[0] == "xpath"
        assert "//parent" in result.locator[1]
        assert "//child" in result.locator[1]

    @pytest.mark.unit
    def test_get_element_with_dict_locator(self):
        """Test get_element with dict parent and child locators."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = {"class": "parent-class"}
        
        child_locator = {"class": "child-class"}
        
        result = el.dom.get_element(child_locator)
        
        assert result is not None
        assert isinstance(result.locator, dict)

    @pytest.mark.unit
    def test_get_element_with_element_locator(self):
        """Test get_element when locator is an Element instance."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//parent")
        
        child_element = app.get_element(("xpath", "//child"))
        
        result = el.dom.get_element(child_element)
        
        assert result is not None

    @pytest.mark.unit
    def test_get_element_raises_error_on_empty_parent_locator(self):
        """Test get_element raises error when parent locator is empty."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.utilities, 'remove_null_value', side_effect=[{}, {"class": "child"}]):
            with pytest.raises(ShadowstepResolvingLocatorError) as exc_info:
                el.dom.get_element({"class": "child"})
        
        assert "Failed to resolve parent locator" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_element_raises_error_on_empty_child_locator(self):
        """Test get_element raises error when child locator is empty."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//parent")
        
        with patch.object(el.utilities, 'remove_null_value', side_effect=[("xpath", "//parent"), {}]):
            with pytest.raises(ShadowstepResolvingLocatorError) as exc_info:
                el.dom.get_element({"text": "null"})
        
        assert "Failed to resolve child locator" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_element_xpath_removes_leading_slash(self):
        """Test get_element correctly handles xpath with leading slash."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//parent")
        
        child_locator = ("xpath", "/child")
        
        result = el.dom.get_element(child_locator)
        
        assert result is not None
        # Should add // before child if it doesn't start with //
        assert "//child" in result.locator[1]

    # Tests for get_elements method
    @pytest.mark.unit
    @patch("shadowstep.element.dom.WebDriverWait")
    def test_get_elements_success(self, mock_wait):
        """Test successful get_elements operation."""
        mock_driver = Mock()
        mock_driver.page_source = '<root><child id="1"/><child id="2"/></root>'
        
        app, el = self._create_test_element(mock_driver)
        
        # Mock utilities.get_xpath
        with patch.object(el.utilities, 'get_xpath', return_value="//parent"):
            # Mock extract_el_attrs_from_source
            with patch.object(el.utilities, 'extract_el_attrs_from_source', 
                            return_value=[{"id": "1"}, {"id": "2"}]):
                # Mock WebDriverWait
                mock_wait_instance = Mock()
                mock_wait_instance.until.return_value = Mock()
                mock_wait.return_value = mock_wait_instance
                
                with patch.object(el, 'get_driver', return_value=mock_driver):
                    result = el.dom.get_elements(("xpath", "//child"))
        
        assert len(result) == 2
        assert all(hasattr(elem, 'locator') for elem in result)

    @pytest.mark.unit
    def test_get_elements_raises_error_when_xpath_fails(self):
        """Test get_elements raises error when xpath resolution fails."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.utilities, 'get_xpath', return_value=None):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.dom.get_elements(("xpath", "//child"))
        
        assert "Unable to resolve shadowstep xpath" in str(exc_info.value)

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    @patch("shadowstep.element.dom.WebDriverWait")
    def test_get_elements_handles_no_such_driver_exception(self, mock_wait, mock_handle_error):
        """Test get_elements handles NoSuchDriverException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el.utilities, 'get_xpath', return_value="//parent"):
            with patch.object(el, 'get_driver', side_effect=NoSuchDriverException("No driver")):
                result = el.dom.get_elements(("xpath", "//child"))
        
        assert result == []
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    @patch("shadowstep.element.dom.WebDriverWait")
    def test_get_elements_handles_invalid_session_id_exception(self, mock_wait, mock_handle_error):
        """Test get_elements handles InvalidSessionIdException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el.utilities, 'get_xpath', return_value="//parent"):
            with patch.object(el, 'get_driver', side_effect=InvalidSessionIdException("Invalid session")):
                result = el.dom.get_elements(("xpath", "//child"))
        
        assert result == []
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.dom.WebDriverWait")
    def test_get_elements_handles_stale_element_reference_exception(self, mock_wait):
        """Test get_elements handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_driver.page_source = '<root><child/></root>'
        
        app, el = self._create_test_element(mock_driver)
        
        # First call raises exception, second succeeds
        call_count = [0]
        def mock_get_driver():
            call_count[0] += 1
            if call_count[0] == 1:
                raise StaleElementReferenceException("Stale")
            return mock_driver
        
        with patch.object(el.utilities, 'get_xpath', return_value="//parent"):
            with patch.object(el.utilities, 'extract_el_attrs_from_source', return_value=[{"id": "1"}]):
                mock_wait_instance = Mock()
                mock_wait_instance.until.return_value = Mock()
                mock_wait.return_value = mock_wait_instance
                
                with patch.object(el, 'get_driver', side_effect=mock_get_driver):
                    with patch.object(el, 'get_native', return_value=Mock()):
                        result = el.dom.get_elements(("xpath", "//child"))
        
        assert len(result) == 1

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    @patch("shadowstep.element.dom.WebDriverWait")
    def test_get_elements_handles_webdriver_exception_instrumentation(self, mock_wait, mock_handle_error):
        """Test get_elements handles WebDriverException with instrumentation error."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Instrumentation process is not running")
        
        with patch.object(el.utilities, 'get_xpath', return_value="//parent"):
            with patch.object(el, 'get_driver', return_value=mock_driver):
                mock_wait_instance = Mock()
                mock_wait_instance.until.side_effect = error
                mock_wait.return_value = mock_wait_instance
                
                result = el.dom.get_elements(("xpath", "//child"))
        
        assert result == []
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.dom.WebDriverWait")
    def test_get_elements_raises_other_webdriver_exceptions(self, mock_wait):
        """Test get_elements raises other WebDriverException."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        error = WebDriverException("Some other error")
        
        with patch.object(el.utilities, 'get_xpath', return_value="//parent"):
            with patch.object(el, 'get_driver', return_value=mock_driver):
                mock_wait_instance = Mock()
                mock_wait_instance.until.side_effect = error
                mock_wait.return_value = mock_wait_instance
                
                with pytest.raises(WebDriverException):
                    el.dom.get_elements(("xpath", "//child"))

    # Tests for get_parent method
    @pytest.mark.unit
    def test_get_parent_success(self):
        """Test successful get_parent operation."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//child")
        
        result = el.dom.get_parent()
        
        assert result is not None
        assert isinstance(result.locator, tuple)
        assert result.locator[0] == "xpath"
        assert result.locator[1] == "//child/.."

    @pytest.mark.unit
    def test_get_parent_with_dict_locator(self):
        """Test get_parent with dict locator."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = {"class": "child-class"}
        
        result = el.dom.get_parent()
        
        assert result is not None
        # Should be converted to xpath with /..
        assert result.locator[0] == "xpath"
        assert "/.." in result.locator[1]

    # Tests for get_parents method
    @pytest.mark.unit
    @patch("shadowstep.element.dom.ElementDOM.get_elements")
    def test_get_parents_success(self, mock_get_elements):
        """Test successful get_parents operation."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//child")
        
        # Mock get_elements to return a list of elements
        mock_parent1 = Mock()
        mock_parent1.locator = {"class": "parent1"}
        mock_parent2 = Mock()
        mock_parent2.locator = {"class": "parent2"}
        mock_get_elements.return_value = [mock_parent1, mock_parent2]
        
        result = el.dom.get_parents()
        
        assert len(result) == 2
        # Check that xpath was constructed correctly
        mock_get_elements.assert_called_once()
        xpath_arg = mock_get_elements.call_args[0][0]
        assert "/ancestor::*" in xpath_arg[1]

    @pytest.mark.unit
    @patch("shadowstep.element.dom.ElementDOM.get_elements")
    def test_get_parents_removes_hierarchy_root(self, mock_get_elements):
        """Test get_parents removes hierarchy root element."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//child")
        
        # Mock get_elements to return hierarchy as first element
        mock_hierarchy = Mock()
        mock_hierarchy.locator = {"class": "hierarchy"}
        mock_parent = Mock()
        mock_parent.locator = {"class": "parent"}
        mock_get_elements.return_value = [mock_hierarchy, mock_parent]
        
        result = el.dom.get_parents()
        
        # hierarchy should be removed
        assert len(result) == 1
        assert result[0].locator == {"class": "parent"}

    # Tests for get_sibling method
    @pytest.mark.unit
    def test_get_sibling_success(self):
        """Test successful get_sibling operation."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//div[1]")
        
        sibling_locator = ("xpath", "//div")
        
        result = el.dom.get_sibling(sibling_locator)
        
        assert result is not None
        assert isinstance(result.locator, tuple)
        assert result.locator[0] == "xpath"
        assert "/following-sibling::" in result.locator[1]
        assert "[1]" in result.locator[1]

    @pytest.mark.unit
    def test_get_sibling_with_dict_locator(self):
        """Test get_sibling with dict locator."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = {"class": "first-div"}
        
        sibling_locator = {"class": "second-div"}
        
        result = el.dom.get_sibling(sibling_locator)
        
        assert result is not None
        assert result.locator[0] == "xpath"
        assert "/following-sibling::" in result.locator[1]

    # Tests for get_siblings method
    @pytest.mark.unit
    @patch("shadowstep.element.dom.ElementDOM.get_elements")
    def test_get_siblings_success(self, mock_get_elements):
        """Test successful get_siblings operation."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//div[1]")
        
        mock_sibling1 = Mock()
        mock_sibling2 = Mock()
        mock_get_elements.return_value = [mock_sibling1, mock_sibling2]
        
        sibling_locator = ("xpath", "//div")
        
        result = el.dom.get_siblings(sibling_locator)
        
        assert len(result) == 2
        # Check that xpath was constructed correctly
        mock_get_elements.assert_called_once()
        xpath_arg = mock_get_elements.call_args[0][0]
        assert "/following-sibling::" in xpath_arg[1]
        # Should NOT have [1] for get_siblings (unlike get_sibling)
        assert xpath_arg[1].count("[1]") == 0 or not xpath_arg[1].endswith("[1]")

    # Tests for get_cousin method
    @pytest.mark.unit
    def test_get_cousin_success(self):
        """Test successful get_cousin operation."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//parent/child")
        
        cousin_locator = ("xpath", "//cousin")
        
        result = el.dom.get_cousin(cousin_locator, depth_to_parent=1)
        
        assert result is not None
        assert isinstance(result.locator, tuple)
        assert result.locator[0] == "xpath"
        # Should have ../ for going up
        assert "/.." in result.locator[1]

    @pytest.mark.unit
    def test_get_cousin_with_depth_2(self):
        """Test get_cousin with depth_to_parent=2."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//grandparent/parent/child")
        
        cousin_locator = ("xpath", "//cousin")
        
        result = el.dom.get_cousin(cousin_locator, depth_to_parent=2)
        
        assert result is not None
        # Should have multiple ../ for going up multiple levels
        assert result.locator[1].count("/..") >= 2

    @pytest.mark.unit
    def test_get_cousin_with_dict_locator(self):
        """Test get_cousin with dict locator."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = {"class": "child-class"}
        
        cousin_locator = {"class": "cousin-class"}
        
        result = el.dom.get_cousin(cousin_locator, depth_to_parent=1)
        
        assert result is not None
        assert result.locator[0] == "xpath"

    # Tests for get_cousins method
    @pytest.mark.unit
    @patch("shadowstep.element.dom.ElementDOM.get_elements")
    def test_get_cousins_success(self, mock_get_elements):
        """Test successful get_cousins operation."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//parent/child")
        
        mock_cousin1 = Mock()
        mock_cousin2 = Mock()
        mock_get_elements.return_value = [mock_cousin1, mock_cousin2]
        
        cousin_locator = ("xpath", "//cousin")
        
        result = el.dom.get_cousins(cousin_locator, depth_to_parent=1)
        
        assert len(result) == 2
        # Check that xpath was constructed correctly
        mock_get_elements.assert_called_once()
        xpath_arg = mock_get_elements.call_args[0][0]
        assert "/.." in xpath_arg[1]

    @pytest.mark.unit
    @patch("shadowstep.element.dom.ElementDOM.get_elements")
    def test_get_cousins_with_depth_3(self, mock_get_elements):
        """Test get_cousins with depth_to_parent=3."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//great/grand/parent/child")
        
        mock_cousin = Mock()
        mock_get_elements.return_value = [mock_cousin]
        
        cousin_locator = ("xpath", "//cousin")
        
        result = el.dom.get_cousins(cousin_locator, depth_to_parent=3)
        
        assert len(result) == 1
        # Check that xpath has multiple ../ for depth
        xpath_arg = mock_get_elements.call_args[0][0]
        assert xpath_arg[1].count("/..") >= 3

    # Additional edge case tests
    @pytest.mark.unit
    def test_get_element_with_custom_timeout(self):
        """Test get_element with custom timeout parameter."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//parent")
        
        child_locator = ("xpath", "//child")
        
        result = el.dom.get_element(child_locator, timeout=60)
        
        assert result is not None
        assert result.timeout == 60

    @pytest.mark.unit
    def test_get_elements_with_element_locator(self):
        """Test get_elements when locator is an Element instance."""
        mock_driver = Mock()
        mock_driver.page_source = '<root><child/></root>'
        
        app, el = self._create_test_element(mock_driver)
        
        child_element = app.get_element(("xpath", "//child"))
        
        with patch.object(el.utilities, 'get_xpath', return_value="//parent"):
            with patch.object(el.utilities, 'extract_el_attrs_from_source', return_value=[{"id": "1"}]):
                with patch("shadowstep.element.dom.WebDriverWait") as mock_wait:
                    mock_wait_instance = Mock()
                    mock_wait_instance.until.return_value = Mock()
                    mock_wait.return_value = mock_wait_instance
                    
                    with patch.object(el, 'get_driver', return_value=mock_driver):
                        result = el.dom.get_elements(child_element)
        
        assert len(result) == 1

    @pytest.mark.unit
    def test_get_parent_with_custom_parameters(self):
        """Test get_parent with custom timeout and poll_frequency."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//child")
        
        result = el.dom.get_parent(timeout=60, poll_frequency=1.0)
        
        assert result is not None
        assert result.timeout == 60
        assert result.poll_frequency == 1.0

