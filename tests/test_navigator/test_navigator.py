"""Tests for the navigator module.

This module contains comprehensive tests for the PageNavigator and PageGraph classes,
covering dom functionality, pathfinding algorithms, and error handling.
"""

from collections.abc import Callable
from unittest.mock import Mock, patch

import networkx as nx
import pytest
from selenium.common import WebDriverException

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepPageCannotBeNoneError,
    ShadowstepFromPageCannotBeNoneError,
    ShadowstepToPageCannotBeNoneError,
    ShadowstepTimeoutMustBeNonNegativeError,
    ShadowstepPathCannotBeEmptyError,
    ShadowstepPathMustContainAtLeastTwoPagesError,
    ShadowstepNavigationFailedError,
)
from shadowstep.navigator.navigator import DEFAULT_NAVIGATION_TIMEOUT, PageGraph, PageNavigator


class MockPage:
    """Mock page class for testing purposes."""
    
    def __init__(self, name: str) -> None:
        """Initialize mock page.
        
        Args:
            name: Name of the page.
        """
        self.name = name
        self.edges: dict[str, Callable[[], None]] = {}
    
    def __repr__(self) -> str:
        """String representation of the page."""
        return f"MockPage({self.name})"
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another page."""
        if not isinstance(other, MockPage):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.name)


class MockPageBase:
    """Mock PageBaseShadowstep for testing."""
    
    def __init__(self, name: str) -> None:
        """Initialize mock page shadowstep.
        
        Args:
            name: Name of the page.
        """
        self.name = name
        self.edges: dict[str, Callable[[], None]] = {}
    
    def is_current_page(self) -> bool:
        """Mock implementation of is_current_page."""
        return True
    
    def __repr__(self) -> str:
        """String representation of the page."""
        return f"MockPageBase({self.name})"
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another page."""
        if not isinstance(other, MockPageBase):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.name)


class TestPageGraph:
    """Test cases for PageGraph class."""
    
    def test_init(self) -> None:
        """Test PageGraph initialization."""
        graph = PageGraph()
        assert isinstance(graph.graph, dict)  # noqa: S101
        assert isinstance(graph.nx_graph, nx.DiGraph)  # noqa: S101
        assert len(graph.graph) == 0  # noqa: S101
        assert graph.nx_graph.number_of_nodes() == 0  # noqa: S101
    
    def test_add_page_with_dict_edges(self) -> None:
        """Test adding a page with dictionary edges."""
        graph = PageGraph()
        page = MockPage("page1")
        edges = {"page2": lambda: None, "page3": lambda: None}
        
        graph.add_page(page, edges)
        
        assert page in graph.graph  # noqa: S101
        assert graph.graph[page] == edges  # noqa: S101
        assert graph.nx_graph.has_node(page)  # noqa: S101
        assert graph.nx_graph.has_edge(page, "page2")  # noqa: S101
        assert graph.nx_graph.has_edge(page, "page3")  # noqa: S101
    
    def test_add_page_with_list_edges(self) -> None:
        """Test adding a page with list edges."""
        graph = PageGraph()
        page = MockPage("page1")
        edges = ["page2", "page3"]
        
        graph.add_page(page, edges)
        
        assert page in graph.graph  # noqa: S101
        assert graph.graph[page] == edges  # noqa: S101
        assert graph.nx_graph.has_node(page)  # noqa: S101
        assert graph.nx_graph.has_edge(page, "page2")  # noqa: S101
        assert graph.nx_graph.has_edge(page, "page3")  # noqa: S101
    
    def test_add_page_with_tuple_edges(self) -> None:
        """Test adding a page with tuple edges."""
        graph = PageGraph()
        page = MockPage("page1")
        edges = ("page2", "page3")
        
        graph.add_page(page, edges)
        
        assert page in graph.graph  # noqa: S101
        assert graph.graph[page] == edges  # noqa: S101
        assert graph.nx_graph.has_node(page)  # noqa: S101
        assert graph.nx_graph.has_edge(page, "page2")  # noqa: S101
        assert graph.nx_graph.has_edge(page, "page3")  # noqa: S101
    
    def test_add_page_none_page_raises_error(self) -> None:
        """Test that adding None page raises TypeError."""
        graph = PageGraph()
        edges = {"page2": lambda: None}
        
        with pytest.raises(ShadowstepPageCannotBeNoneError, match="page cannot be None"):
            graph.add_page(None, edges)
    
    def test_get_edges_existing_page(self) -> None:
        """Test getting edges for existing page."""
        graph = PageGraph()
        page = MockPage("page1")
        edges = {"page2": lambda: None}
        
        graph.add_page(page, edges)
        result = graph.get_edges(page)
        
        assert result == edges  # noqa: S101
    
    def test_get_edges_nonexistent_page(self) -> None:
        """Test getting edges for non-existent page."""
        graph = PageGraph()
        page = MockPage("nonexistent")
        
        result = graph.get_edges(page)
        
        assert result == []  # noqa: S101
    
    def test_is_valid_edge_existing(self) -> None:
        """Test checking valid edge that exists."""
        graph = PageGraph()
        page1 = MockPage("page1")
        edges = {"page2": lambda: None}
        
        graph.add_page(page1, edges)
        result = graph.is_valid_edge(page1, "page2")
        
        assert result is True  # noqa: S101
    
    def test_is_valid_edge_nonexistent(self) -> None:
        """Test checking valid edge that doesn't exist."""
        graph = PageGraph()
        page1 = MockPage("page1")
        edges = {"page3": lambda: None}
        
        graph.add_page(page1, edges)
        result = graph.is_valid_edge(page1, "page2")
        
        assert result is False  # noqa: S101
    
    def test_has_path_existing_path(self) -> None:
        """Test checking path that exists."""
        graph = PageGraph()
        page1 = MockPage("page1")
        page2 = MockPage("page2")
        page3 = MockPage("page3")
        
        graph.add_page(page1, [page2])
        graph.add_page(page2, [page3])
        graph.add_page(page3, [])
        
        result = graph.has_path(page1, page3)
        
        assert result is True  # noqa: S101
    
    def test_has_path_nonexistent_path(self) -> None:
        """Test checking path that doesn't exist."""
        graph = PageGraph()
        page1 = MockPage("page1")
        page3 = MockPage("page3")
        
        graph.add_page(page1, [])
        graph.add_page(page3, [])
        
        result = graph.has_path(page1, page3)
        
        assert result is False  # noqa: S101
    
    def test_find_shortest_path_existing(self) -> None:
        """Test finding shortest path that exists."""
        graph = PageGraph()
        page1 = MockPage("page1")
        page2 = MockPage("page2")
        page3 = MockPage("page3")
        
        graph.add_page(page1, [page2])
        graph.add_page(page2, [page3])
        graph.add_page(page3, [])
        
        result = graph.find_shortest_path(page1, page3)
        
        assert result == [page1, page2, page3]  # noqa: S101
    
    def test_find_shortest_path_nonexistent(self) -> None:
        """Test finding shortest path that doesn't exist."""
        graph = PageGraph()
        page1 = MockPage("page1")
        page2 = MockPage("page2")
        
        graph.add_page(page1, [])
        graph.add_page(page2, [])
        
        result = graph.find_shortest_path(page1, "page2")
        
        assert result is None  # noqa: S101


class TestPageNavigator:
    """Test cases for PageNavigator class."""
    
    @pytest.fixture
    def mock_shadowstep(self) -> Mock:
        """Create a mock Shadowstep instance."""
        shadowstep = Mock()
        def resolve_page_mock(page_name: str) -> MockPage:
            return MockPage(page_name)
        shadowstep.resolve_page = Mock(side_effect=resolve_page_mock)
        return shadowstep
    
    @pytest.fixture
    def navigator(self, mock_shadowstep: Mock) -> PageNavigator:
        """Create a PageNavigator instance with mock Shadowstep."""
        return PageNavigator(mock_shadowstep)
    
    def test_init(self, mock_shadowstep: Mock) -> None:
        """Test PageNavigator initialization."""
        navigator = PageNavigator(mock_shadowstep)
        
        assert navigator.shadowstep == mock_shadowstep  # noqa: S101
        assert isinstance(navigator.graph_manager, PageGraph)  # noqa: S101
        assert navigator.logger is not None  # noqa: S101
    
    def test_add_page(self, navigator: PageNavigator) -> None:
        """Test adding a page to the navigator."""
        page = MockPage("page1")
        edges = {"page2": lambda: None}
        
        navigator.add_page(page, edges)
        
        assert page in navigator.graph_manager.graph  # noqa: S101
        assert navigator.graph_manager.graph[page] == edges  # noqa: S101
    
    def test_add_page_none_page_raises_error(self, navigator: PageNavigator) -> None:
        """Test that adding None page raises TypeError."""
        edges = {"page2": lambda: None}
        
        with pytest.raises(ShadowstepPageCannotBeNoneError, match="page cannot be None"):
            navigator.add_page(None, edges)
    
    def test_navigate_same_page(self, navigator: PageNavigator) -> None:
        """Test navigating to the same page."""
        page = MockPage("page1")
        
        result = navigator.navigate(page, page)
        
        assert result is True  # noqa: S101
    
    def test_navigate_none_from_page_raises_error(self, navigator: PageNavigator) -> None:
        """Test that navigating with None from_page raises TypeError."""
        to_page = MockPage("page2")
        
        with pytest.raises(ShadowstepFromPageCannotBeNoneError, match="from_page cannot be None"):
            navigator.navigate(None, to_page)
    
    def test_navigate_none_to_page_raises_error(self, navigator: PageNavigator) -> None:
        """Test that navigating with None to_page raises TypeError."""
        from_page = MockPage("page1")
        
        with pytest.raises(ShadowstepToPageCannotBeNoneError, match="to_page cannot be None"):
            navigator.navigate(from_page, None)
    
    def test_navigate_negative_timeout_raises_error(self, navigator: PageNavigator) -> None:
        """Test that navigating with negative timeout raises ValueError."""
        from_page = MockPage("page1")
        to_page = MockPage("page2")
        
        with pytest.raises(ShadowstepTimeoutMustBeNonNegativeError, match="timeout must be non-negative"):
            navigator.navigate(from_page, to_page, timeout=-1)
    
    def test_find_path_with_strings(self, navigator: PageNavigator) -> None:
        """Test finding path with string page names."""
        page1 = MockPage("page1")
        page2 = MockPage("page2")
        
        navigator.graph_manager.add_page(page1, ["page2"])
        navigator.graph_manager.add_page(page2, [])
        
        result = navigator.find_path("page1", "page2")
        
        assert result == [page1, page2]  # noqa: S101
    
    def test_find_path_with_objects(self, navigator: PageNavigator) -> None:
        """Test finding path with page objects."""
        page1 = MockPage("page1")
        page2 = MockPage("page2")
        
        navigator.graph_manager.add_page(page1, ["page2"])
        navigator.graph_manager.add_page(page2, [])
        
        result = navigator.find_path(page1, "page2")
        
        assert result == [page1, page2]  # noqa: S101
    
    def test_find_path_nonexistent(self, navigator: PageNavigator) -> None:
        """Test finding path that doesn't exist."""
        page1 = MockPage("page1")
        
        navigator.graph_manager.add_page(page1, [])
        
        result = navigator.find_path(page1, "page2")
        
        assert result is None  # noqa: S101
    
    def test_find_path_bfs_fallback(self, navigator: PageNavigator) -> None:
        """Test BFS fallback when NetworkX fails."""
        page1 = MockPage("page1")
        page2 = MockPage("page2")
        page3 = MockPage("page3")
        
        navigator.graph_manager.add_page(page1, ["page2"])
        navigator.graph_manager.add_page(page2, ["page3"])
        navigator.graph_manager.add_page(page3, [])
        
        # Mock NetworkX to raise exception
        with patch.object(navigator.graph_manager, "find_shortest_path", side_effect=nx.NetworkXException("Test error")):
            result = navigator.find_path(page1, "page3")
        
        assert result == [page1, page2, page3]  # noqa: S101
    
    def test_perform_navigation_success(self, navigator: PageNavigator) -> None:
        """Test successful dom through a path."""
        page1 = MockPageBase("page1")
        page2 = MockPageBase("page2")
        page3 = MockPageBase("page3")
        
        transition_method = Mock()
        page1.edges = {"MockPageBase": transition_method}
        page2.edges = {"MockPageBase": transition_method}
        
        path = [page1, page2, page3]
        
        navigator.perform_navigation(path)
        
        assert transition_method.call_count == 2  # noqa: S101
    
    def test_perform_navigation_empty_path_raises_error(self, navigator: PageNavigator) -> None:
        """Test that performing dom with empty path raises ValueError."""
        with pytest.raises(ShadowstepPathCannotBeEmptyError, match="path cannot be empty"):
            navigator.perform_navigation([])
    
    def test_perform_navigation_single_page_raises_error(self, navigator: PageNavigator) -> None:
        """Test that performing dom with single page raises ValueError."""
        page = MockPageBase("page1")
        
        with pytest.raises(ShadowstepPathMustContainAtLeastTwoPagesError, match="path must contain at least 2 pages"):
            navigator.perform_navigation([page])
    
    def test_perform_navigation_failure_raises_assertion_error(self, navigator: PageNavigator) -> None:
        """Test that dom failure raises AssertionError."""
        page1 = MockPageBase("page1")
        page2 = MockPageBase("page2")
        
        # Mock is_current_page to return False
        page2.is_current_page = Mock(return_value=False)
        
        transition_method = Mock()
        page1.edges = {"MockPageBase": transition_method}
        
        path = [page1, page2]
        
        with pytest.raises(ShadowstepNavigationFailedError, match="Navigation error"):
            navigator.perform_navigation(path)
    
    def test_navigate_successful_path(self, navigator: PageNavigator) -> None:
        """Test successful dom through a complete path."""
        page1 = MockPage("page1")
        page2 = MockPage("page2")
        
        navigator.graph_manager.add_page(page1, ["page2"])
        navigator.graph_manager.add_page(page2, [])
        
        with patch.object(navigator, "perform_navigation") as mock_perform:
            result = navigator.navigate(page1, "page2")
        
        assert result is True  # noqa: S101
        mock_perform.assert_called_once()
    
    def test_navigate_no_path_found(self, navigator: PageNavigator) -> None:
        """Test dom when no path is found."""
        page1 = MockPage("page1")
        
        navigator.graph_manager.add_page(page1, [])
        
        result = navigator.navigate(page1, "page2")
        
        assert result is False  # noqa: S101
    
    def test_navigate_webdriver_exception(self, navigator: PageNavigator) -> None:
        """Test dom when WebDriverException occurs."""
        page1 = MockPage("page1")
        page2 = MockPage("page2")
        
        navigator.graph_manager.add_page(page1, ["page2"])
        navigator.graph_manager.add_page(page2, [])
        
        with patch.object(navigator, "perform_navigation", side_effect=WebDriverException("Test error")):
            result = navigator.navigate(page1, "page2")
        
        assert result is False  # noqa: S101
    
    def test_default_timeout_constant(self) -> None:
        """Test that DEFAULT_NAVIGATION_TIMEOUT has expected value."""
        assert DEFAULT_NAVIGATION_TIMEOUT == 55  # noqa: S101
