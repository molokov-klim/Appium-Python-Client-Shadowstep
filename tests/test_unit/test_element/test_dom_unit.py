# ruff: noqa
# pyright: ignore
"""Unit tests for ElementDOM class using mocks."""
from unittest.mock import Mock, patch

import pytest

from shadowstep.element.dom import ElementDOM
from shadowstep.element.element import Element
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepElementException,
    ShadowstepResolvingLocatorError,
)
from shadowstep.locator import UiSelector


class TestElementDOMInit:
    """Test ElementDOM initialization."""

    def test_init_creates_instance_with_element(self):
        """Test initialization creates instance with element reference."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.converter = Mock()
        mock_element.utilities = Mock()

        dom = ElementDOM(mock_element)

        assert dom.element == mock_element
        assert dom.shadowstep == mock_shadowstep
        assert dom.converter == mock_element.converter
        assert dom.utilities == mock_element.utilities
        assert dom.logger is not None


class TestGetElement:
    """Test get_element method."""

    def test_get_element_with_tuple_parent_and_tuple_child_creates_combined_xpath(self):
        """Test get_element combines parent and child XPath locators."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//parent")
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//child"))
        mock_element.converter = mock_converter
        
        dom = ElementDOM(mock_element)

        # Call get_element and verify it creates the combined locator
        result = dom.get_element(("xpath", "//child"), timeout=10)

        # Verify converter was called
        mock_converter.to_xpath.assert_called_once_with(("xpath", "//child"))
        # Verify result is an Element (created in the method)
        assert isinstance(result, Element)
        # Verify the combined XPath was created
        assert result.locator[0] == "xpath"
        assert "parent" in result.locator[1]
        assert "child" in result.locator[1]

    def test_get_element_extracts_locator_from_element_instance(self):
        """Test get_element extracts locator when passed Element instance."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//parent")
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//child"))
        mock_element.converter = mock_converter
        
        dom = ElementDOM(mock_element)

        # Create child element to pass as locator
        child_element = Mock(spec=Element)
        child_element.locator = ("id", "child_id")

        result = dom.get_element(child_element)

        # Should extract locator from Element
        assert isinstance(result, Element)

    def test_get_element_raises_error_when_parent_locator_is_none(self):
        """Test get_element raises error when parent locator resolves to None."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//parent")
        
        mock_utilities = Mock()
        # remove_null_value returns None for parent
        mock_utilities.remove_null_value = Mock(side_effect=[None, ("xpath", "//child")])
        mock_element.utilities = mock_utilities
        
        mock_element.converter = Mock()
        
        dom = ElementDOM(mock_element)

        with pytest.raises(ShadowstepResolvingLocatorError) as exc_info:
            dom.get_element(("xpath", "//child"))
        
        assert "Failed to resolve parent locator" in str(exc_info.value)

    def test_get_element_raises_error_when_child_locator_is_none(self):
        """Test get_element raises error when child locator resolves to None."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//parent")
        
        mock_utilities = Mock()
        # remove_null_value returns None for child
        mock_utilities.remove_null_value = Mock(side_effect=[("xpath", "//parent"), None])
        mock_element.utilities = mock_utilities
        
        mock_element.converter = Mock()
        
        dom = ElementDOM(mock_element)

        with pytest.raises(ShadowstepResolvingLocatorError) as exc_info:
            dom.get_element(("xpath", "//child"))
        
        assert "Failed to resolve child locator" in str(exc_info.value)

    def test_get_element_strips_leading_slash_from_child_xpath(self):
        """Test get_element strips leading / from child XPath."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//parent")
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        # Child XPath with leading /
        mock_converter.to_xpath = Mock(return_value=("xpath", "/child"))
        mock_element.converter = mock_converter
        
        dom = ElementDOM(mock_element)

        result = dom.get_element(("xpath", "/child"))

        # Verify result has combined XPath with // added
        assert "//child" in result.locator[1]

    def test_get_element_with_dict_parent_updates_with_child_selector(self):
        """Test get_element with dict parent adds child selector."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = {"text": "Parent"}
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x.copy() if isinstance(x, dict) else x)
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        mock_converter.to_dict = Mock(return_value={"text": "Child"})
        mock_element.converter = mock_converter
        
        dom = ElementDOM(mock_element)

        result = dom.get_element({"text": "Child"})

        # Should call to_dict for dict parent
        mock_converter.to_dict.assert_called_once()
        assert isinstance(result, Element)


class TestGetElements:
    """Test get_elements method."""

    def test_get_elements_raises_error_when_xpath_empty(self):
        """Test get_elements raises error when xpath resolution returns empty string."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        
        mock_utilities = Mock()
        mock_utilities.get_xpath = Mock(return_value="")
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        mock_element.converter = mock_converter
        
        dom = ElementDOM(mock_element)

        with pytest.raises(ShadowstepElementException) as exc_info:
            dom.get_elements(("xpath", "//child"))
        
        assert "Unable to resolve shadowstep xpath" in str(exc_info.value)

    def test_get_elements_extracts_locator_from_element_instance(self):
        """Test get_elements extracts locator from Element instance."""
        mock_shadowstep = Mock()
        mock_driver = Mock()
        mock_driver.page_source = """<?xml version="1.0"?>
        <hierarchy>
            <android.widget.TextView text="Test"/>
        </hierarchy>"""
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.driver = mock_driver
        
        mock_utilities = Mock()
        mock_utilities.get_xpath = Mock(return_value="//parent")
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_utilities.extract_el_attrs_from_source = Mock(return_value=[{"text": "Test"}])
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//child"))
        mock_element.converter = mock_converter
        
        mock_element.get_driver = Mock()
        
        dom = ElementDOM(mock_element)

        # Child locator is Element
        child_element = Mock(spec=Element)
        child_element.locator = ("id", "child_id")

        with patch('selenium.webdriver.support.wait.WebDriverWait') as MockWait:
            mock_wait = Mock()
            MockWait.return_value = mock_wait
            mock_wait.until = Mock()
            
            result = dom.get_elements(child_element)

            assert len(result) == 1


class TestGetParent:
    """Test get_parent method."""

    def test_get_parent_appends_parent_xpath(self):
        """Test get_parent appends /.. to current element XPath."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//child")
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//child"))
        mock_element.converter = mock_converter
        
        dom = ElementDOM(mock_element)

        result = dom.get_parent(timeout=15)

        # Verify result is Element with /.. appended
        assert isinstance(result, Element)
        assert result.locator[1] == "//child/.."
        assert result.timeout == 15

    def test_get_parent_converts_locator_to_xpath(self):
        """Test get_parent converts any locator to XPath."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = {"text": "Child"}
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(return_value=("xpath", "//child"))
        mock_element.converter = mock_converter
        
        dom = ElementDOM(mock_element)

        result = dom.get_parent()

        # Should convert dict to xpath first
        mock_converter.to_xpath.assert_called_once()
        assert isinstance(result, Element)


class TestGetParents:
    """Test get_parents method."""

    def test_get_parents_calls_get_elements_with_ancestor_xpath(self):
        """Test get_parents uses /ancestor::* XPath."""
        mock_shadowstep = Mock()
        mock_driver = Mock()
        mock_driver.page_source = """<?xml version="1.0"?>
        <hierarchy>
            <parent1><parent2><child/></parent2></parent1>
        </hierarchy>"""
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//child")
        mock_element.driver = mock_driver
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_utilities.get_xpath = Mock(return_value="//child")
        mock_utilities.extract_el_attrs_from_source = Mock(return_value=[
            {"class": "parent2"},
            {"class": "parent1"}
        ])
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        # Need 2 calls: 1 in get_parents, 1 in get_elements
        mock_converter.to_xpath = Mock(side_effect=[
            ("xpath", "//child"),
            ("xpath", "//child/ancestor::*")
        ])
        mock_element.converter = mock_converter
        
        mock_element.get_driver = Mock()
        
        dom = ElementDOM(mock_element)

        with patch('selenium.webdriver.support.wait.WebDriverWait') as MockWait:
            mock_wait = Mock()
            MockWait.return_value = mock_wait
            mock_wait.until = Mock()
            
            result = dom.get_parents()

            # Verify it called get_elements with /ancestor::*
            assert mock_converter.to_xpath.call_count >= 1
            assert len(result) == 2

    def test_get_parents_removes_hierarchy_class(self):
        """Test get_parents removes first element if class is 'hierarchy'."""
        mock_shadowstep = Mock()
        mock_driver = Mock()
        mock_driver.page_source = """<?xml version="1.0"?>
        <hierarchy class="hierarchy">
            <parent><child/></parent>
        </hierarchy>"""
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//child")
        mock_element.driver = mock_driver
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_utilities.get_xpath = Mock(return_value="//child")
        mock_utilities.extract_el_attrs_from_source = Mock(return_value=[
            {"class": "hierarchy"},
            {"class": "parent"}
        ])
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        # Need 2 calls: 1 in get_parents, 1 in get_elements
        mock_converter.to_xpath = Mock(side_effect=[
            ("xpath", "//child"),
            ("xpath", "//child/ancestor::*")
        ])
        mock_element.converter = mock_converter
        
        mock_element.get_driver = Mock()
        
        dom = ElementDOM(mock_element)

        with patch('selenium.webdriver.support.wait.WebDriverWait') as MockWait:
            mock_wait = Mock()
            MockWait.return_value = mock_wait
            mock_wait.until = Mock()
            
            result = dom.get_parents()

            # hierarchy should be removed, only parent remains
            assert len(result) == 1
            assert result[0].locator.get("class") == "parent"


class TestGetSibling:
    """Test get_sibling method."""

    def test_get_sibling_creates_following_sibling_xpath(self):
        """Test get_sibling creates XPath with /following-sibling:: axis."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//element")
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(side_effect=[
            ("xpath", "//element"),
            ("xpath", "//sibling")
        ])
        mock_element.converter = mock_converter
        
        dom = ElementDOM(mock_element)

        result = dom.get_sibling(("xpath", "//sibling"), timeout=10)

        assert isinstance(result, Element)
        assert "/following-sibling::" in result.locator[1]
        assert "[1]" in result.locator[1]  # First sibling only

    def test_get_sibling_strips_leading_slashes_from_sibling_path(self):
        """Test get_sibling strips leading slashes from sibling XPath."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//element")
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(side_effect=[
            ("xpath", "//element"),
            ("xpath", "//sibling")
        ])
        mock_element.converter = mock_converter
        
        dom = ElementDOM(mock_element)

        result = dom.get_sibling(("xpath", "//sibling"))

        # Leading slashes should be stripped from sibling part
        assert isinstance(result, Element)
        assert "/following-sibling::sibling[1]" in result.locator[1]


class TestGetSiblings:
    """Test get_siblings method."""

    def test_get_siblings_creates_following_sibling_xpath_without_index(self):
        """Test get_siblings creates XPath without [1] index for multiple siblings."""
        mock_shadowstep = Mock()
        mock_driver = Mock()
        mock_driver.page_source = """<?xml version="1.0"?>
        <hierarchy>
            <element/><sibling1/><sibling2/>
        </hierarchy>"""
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//element")
        mock_element.driver = mock_driver
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_utilities.get_xpath = Mock(return_value="//element")
        mock_utilities.extract_el_attrs_from_source = Mock(return_value=[
            {"class": "sibling1"},
            {"class": "sibling2"}
        ])
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        # Need 3 calls: 1 in get_siblings, 2 in get_elements (remove_null + to_xpath)
        mock_converter.to_xpath = Mock(side_effect=[
            ("xpath", "//element"),
            ("xpath", "//sibling"),
            ("xpath", "//element/following-sibling::sibling")
        ])
        mock_element.converter = mock_converter
        
        mock_element.get_driver = Mock()
        
        dom = ElementDOM(mock_element)

        with patch('selenium.webdriver.support.wait.WebDriverWait') as MockWait:
            mock_wait = Mock()
            MockWait.return_value = mock_wait
            mock_wait.until = Mock()
            
            result = dom.get_siblings(("xpath", "//sibling"))

            assert len(result) == 2
            # Should NOT have [1] for multiple siblings
            assert "[1]" not in str(result)


class TestGetCousin:
    """Test get_cousin method."""

    def test_get_cousin_creates_xpath_with_parent_navigation(self):
        """Test get_cousin creates XPath navigating up to parent then to cousin."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//current")
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(side_effect=[
            ("xpath", "//current"),
            ("xpath", "//cousin")
        ])
        mock_element.converter = mock_converter
        
        dom = ElementDOM(mock_element)

        result = dom.get_cousin(("xpath", "//cousin"), depth_to_parent=1)

        # depth_to_parent=1 becomes 2 levels up (/../..)
        assert isinstance(result, Element)
        assert "/../.." in result.locator[1]
        assert "cousin" in result.locator[1]

    def test_get_cousin_with_depth_0(self):
        """Test get_cousin with depth_to_parent=0."""
        mock_shadowstep = Mock()
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//current")
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        mock_converter.to_xpath = Mock(side_effect=[
            ("xpath", "//current"),
            ("xpath", "//cousin")
        ])
        mock_element.converter = mock_converter
        
        dom = ElementDOM(mock_element)

        result = dom.get_cousin(("xpath", "//cousin"), depth_to_parent=0)

        # depth_to_parent=0 becomes 1 level up (/..)
        assert result.locator[1].count("/..") == 1


class TestGetCousins:
    """Test get_cousins method."""

    def test_get_cousins_creates_xpath_with_parent_navigation(self):
        """Test get_cousins creates XPath navigating up to parent then to cousins."""
        mock_shadowstep = Mock()
        mock_driver = Mock()
        mock_driver.page_source = """<?xml version="1.0"?>
        <hierarchy>
            <grandparent><parent1><current/></parent1><parent2><cousin1/><cousin2/></parent2></grandparent>
        </hierarchy>"""
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//current")
        mock_element.driver = mock_driver
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_utilities.get_xpath = Mock(return_value="//current")
        mock_utilities.extract_el_attrs_from_source = Mock(return_value=[
            {"class": "cousin1"},
            {"class": "cousin2"}
        ])
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        # Need 3 calls: 2 in get_cousins, 1 in get_elements
        mock_converter.to_xpath = Mock(side_effect=[
            ("xpath", "//current"),
            ("xpath", "//cousin"),
            ("xpath", "//current/../..//cousin")
        ])
        mock_element.converter = mock_converter
        
        mock_element.get_driver = Mock()
        
        dom = ElementDOM(mock_element)

        with patch('selenium.webdriver.support.wait.WebDriverWait') as MockWait:
            mock_wait = Mock()
            MockWait.return_value = mock_wait
            mock_wait.until = Mock()
            
            result = dom.get_cousins(("xpath", "//cousin"), depth_to_parent=1)

            assert len(result) == 2

    def test_get_cousins_with_depth_3(self):
        """Test get_cousins with depth_to_parent=3 creates 4 levels up."""
        mock_shadowstep = Mock()
        mock_driver = Mock()
        mock_driver.page_source = """<?xml version="1.0"?>
        <hierarchy><level1><level2><level3><current/></level3></level2></level1></hierarchy>"""
        mock_shadowstep.driver = mock_driver
        
        mock_element = Mock(spec=Element)
        mock_element.shadowstep = mock_shadowstep
        mock_element.locator = ("xpath", "//current")
        mock_element.driver = mock_driver
        
        mock_utilities = Mock()
        mock_utilities.remove_null_value = Mock(side_effect=lambda x: x)
        mock_utilities.get_xpath = Mock(return_value="//current")
        mock_utilities.extract_el_attrs_from_source = Mock(return_value=[])
        mock_element.utilities = mock_utilities
        
        mock_converter = Mock()
        # Need 3 calls: 2 in get_cousins, 1 in get_elements
        mock_converter.to_xpath = Mock(side_effect=[
            ("xpath", "//current"),
            ("xpath", "//cousin"),
            ("xpath", "//current/../../../..//cousin")
        ])
        mock_element.converter = mock_converter
        
        mock_element.get_driver = Mock()
        
        dom = ElementDOM(mock_element)

        with patch('selenium.webdriver.support.wait.WebDriverWait') as MockWait:
            mock_wait = Mock()
            MockWait.return_value = mock_wait
            mock_wait.until = Mock()
            
            result = dom.get_cousins(("xpath", "//cousin"), depth_to_parent=3)

            # depth_to_parent=3 becomes 4 levels up
            assert len(result) == 0  # No cousins found in this test

