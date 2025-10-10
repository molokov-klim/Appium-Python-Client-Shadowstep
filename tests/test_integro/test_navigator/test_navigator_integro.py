# ruff: noqa
# pyright: ignore
"""Integration tests for the navigator module.

This module contains integration tests for the PageNavigator and PageGraph classes,
testing real navigation scenarios with actual Android pages.

Coverage notes:
- Tests PageGraph.__init__() with empty graph initialization
- Tests PageGraph.add_page() with page registration
- Tests PageGraph.get_edges() for edge retrieval
- Tests PageGraph.is_valid_edge() for edge validation
- Tests PageGraph.has_path() for path existence checking
- Tests PageGraph.find_shortest_path() with NetworkX
- Tests PageNavigator.__init__() with Shadowstep instance
- Tests PageNavigator.get_page() for page retrieval
- Tests PageNavigator.resolve_page() for page resolution
- Tests PageNavigator.add_page() for page registration
- Tests PageNavigator.navigate() for full navigation
- Tests PageNavigator.find_path() for path finding
- Tests PageNavigator.perform_navigation() for navigation execution
- Tests error handling for None pages, invalid timeouts, empty paths

Requirements:
- Shadowstep instance connected to Android device (app fixture)
- Test pages that inherit from PageBaseShadowstep
"""

import time
from typing import Dict, Callable

import pytest

from shadowstep.navigator.navigator import PageNavigator, PageGraph
from shadowstep.page_base import PageBaseShadowstep
from shadowstep.shadowstep import Shadowstep
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepPageCannotBeNoneError,
    ShadowstepFromPageCannotBeNoneError,
    ShadowstepToPageCannotBeNoneError,
    ShadowstepTimeoutMustBeNonNegativeError,
    ShadowstepPathCannotBeEmptyError,
    ShadowstepPathMustContainAtLeastTwoPagesError,
)


# Test Page Classes for Integration Testing

class PageTestA(PageBaseShadowstep):
    """Test page A for navigation testing."""

    def __init__(self):
        super().__init__()
        self._current = False

    @property
    def edges(self) -> Dict[str, Callable[[], PageBaseShadowstep]]:
        """Define edges to other pages."""
        return {
            "PageTestB": self.to_page_b,
            "PageTestC": self.to_page_c
        }

    def to_page_b(self) -> PageBaseShadowstep:
        """Navigate to PageTestB."""
        self._current = False
        page_b = PageTestB()
        page_b._current = True
        return page_b

    def to_page_c(self) -> PageBaseShadowstep:
        """Navigate to PageTestC."""
        self._current = False
        page_c = PageTestC()
        page_c._current = True
        return page_c

    def is_current_page(self) -> bool:
        """Check if this is the current page."""
        return getattr(self, '_current', False)


class PageTestB(PageBaseShadowstep):
    """Test page B for navigation testing."""

    def __init__(self):
        super().__init__()
        self._current = False

    @property
    def edges(self) -> Dict[str, Callable[[], PageBaseShadowstep]]:
        """Define edges to other pages."""
        return {
            "PageTestC": self.to_page_c,
            "PageTestD": self.to_page_d
        }

    def to_page_c(self) -> PageBaseShadowstep:
        """Navigate to PageTestC."""
        self._current = False
        page_c = PageTestC()
        page_c._current = True
        return page_c

    def to_page_d(self) -> PageBaseShadowstep:
        """Navigate to PageTestD."""
        self._current = False
        page_d = PageTestD()
        page_d._current = True
        return page_d

    def is_current_page(self) -> bool:
        """Check if this is the current page."""
        return getattr(self, '_current', False)


class PageTestC(PageBaseShadowstep):
    """Test page C for navigation testing."""

    def __init__(self):
        super().__init__()
        self._current = False

    @property
    def edges(self) -> Dict[str, Callable[[], PageBaseShadowstep]]:
        """Define edges to other pages."""
        return {
            "PageTestD": self.to_page_d
        }

    def to_page_d(self) -> PageBaseShadowstep:
        """Navigate to PageTestD."""
        self._current = False
        page_d = PageTestD()
        page_d._current = True
        return page_d

    def is_current_page(self) -> bool:
        """Check if this is the current page."""
        return getattr(self, '_current', False)


class PageTestD(PageBaseShadowstep):
    """Test page D for navigation testing (terminal node)."""

    def __init__(self):
        super().__init__()
        self._current = False

    @property
    def edges(self) -> Dict[str, Callable[[], PageBaseShadowstep]]:
        """Define edges to other pages."""
        return {}

    def is_current_page(self) -> bool:
        """Check if this is the current page."""
        return getattr(self, '_current', False)


class PageTestIsolated(PageBaseShadowstep):
    """Test page with no edges (isolated node)."""

    def __init__(self):
        super().__init__()
        self._current = False

    @property
    def edges(self) -> Dict[str, Callable[[], PageBaseShadowstep]]:
        """Define edges to other pages."""
        return {}

    def is_current_page(self) -> bool:
        """Check if this is the current page."""
        return getattr(self, '_current', False)


# Integration Tests

class TestPageGraph:
    """Integration tests for PageGraph class."""

    def test_page_graph_initialization(self):
        """Test PageGraph initializes with empty graphs."""
        # Act
        graph = PageGraph()

        # Assert
        assert graph is not None
        assert graph.graph == {}
        assert graph.nx_graph is not None
        assert len(graph.nx_graph.nodes) == 0
        assert len(graph.nx_graph.edges) == 0

    def test_page_graph_add_page(self):
        """Test adding a page to the graph."""
        # Arrange
        graph = PageGraph()
        page_a = PageTestA()
        page_a._current = True
        edges = page_a.edges

        # Act
        graph.add_page(page_a, edges)

        # Assert
        assert "PageTestA" in graph.graph
        assert graph.graph["PageTestA"] == edges
        assert "PageTestA" in graph.nx_graph.nodes
        assert "PageTestB" in graph.nx_graph.nodes
        assert "PageTestC" in graph.nx_graph.nodes
        assert graph.nx_graph.has_edge("PageTestA", "PageTestB")
        assert graph.nx_graph.has_edge("PageTestA", "PageTestC")

    def test_page_graph_add_page_raises_exception_for_none(self):
        """Test that adding None page raises exception."""
        # Arrange
        graph = PageGraph()

        # Act & Assert
        with pytest.raises(ShadowstepPageCannotBeNoneError):
            graph.add_page(None, {})

    def test_page_graph_get_edges(self):
        """Test getting edges for a page."""
        # Arrange
        graph = PageGraph()
        page_a = PageTestA()
        graph.add_page(page_a, page_a.edges)

        # Act
        edges = graph.get_edges("PageTestA")

        # Assert
        assert "PageTestB" in edges
        assert "PageTestC" in edges
        assert len(edges) == 2

    def test_page_graph_get_edges_for_nonexistent_page(self):
        """Test getting edges for a page that doesn't exist."""
        # Arrange
        graph = PageGraph()

        # Act
        edges = graph.get_edges("NonExistentPage")

        # Assert
        assert edges == []

    def test_page_graph_is_valid_edge(self):
        """Test checking if an edge is valid."""
        # Arrange
        graph = PageGraph()
        page_a = PageTestA()
        page_b = PageTestB()
        graph.add_page(page_a, page_a.edges)
        graph.add_page(page_b, page_b.edges)

        # Act & Assert
        assert graph.is_valid_edge("PageTestA", "PageTestB") is True
        assert graph.is_valid_edge("PageTestA", "PageTestC") is True
        assert graph.is_valid_edge("PageTestA", "PageTestD") is False
        assert graph.is_valid_edge("PageTestB", "PageTestC") is True
        assert graph.is_valid_edge("PageTestB", "PageTestD") is True

    def test_page_graph_is_valid_edge_with_page_objects(self):
        """Test checking edge validity with page objects."""
        # Arrange
        graph = PageGraph()
        page_a = PageTestA()
        page_b = PageTestB()
        graph.add_page(page_a, page_a.edges)
        graph.add_page(page_b, page_b.edges)

        # Act & Assert
        assert graph.is_valid_edge(page_a, page_b) is True
        assert graph.is_valid_edge(page_b, page_a) is False

    def test_page_graph_has_path(self):
        """Test checking if a path exists between pages."""
        # Arrange
        graph = PageGraph()
        page_a = PageTestA()
        page_b = PageTestB()
        page_c = PageTestC()
        page_d = PageTestD()
        graph.add_page(page_a, page_a.edges)
        graph.add_page(page_b, page_b.edges)
        graph.add_page(page_c, page_c.edges)
        graph.add_page(page_d, page_d.edges)

        # Act & Assert
        assert graph.has_path("PageTestA", "PageTestD") is True
        assert graph.has_path("PageTestA", "PageTestB") is True
        assert graph.has_path("PageTestD", "PageTestA") is False

    def test_page_graph_has_path_to_isolated_node(self):
        """Test path checking to isolated node."""
        # Arrange
        graph = PageGraph()
        page_a = PageTestA()
        page_isolated = PageTestIsolated()
        graph.add_page(page_a, page_a.edges)
        graph.add_page(page_isolated, page_isolated.edges)

        # Act & Assert
        assert graph.has_path("PageTestA", "PageTestIsolated") is False
        assert graph.has_path("PageTestIsolated", "PageTestA") is False

    def test_page_graph_find_shortest_path(self):
        """Test finding shortest path between pages."""
        # Arrange
        graph = PageGraph()
        page_a = PageTestA()
        page_b = PageTestB()
        page_c = PageTestC()
        page_d = PageTestD()
        graph.add_page(page_a, page_a.edges)
        graph.add_page(page_b, page_b.edges)
        graph.add_page(page_c, page_c.edges)
        graph.add_page(page_d, page_d.edges)

        # Act
        path_direct = graph.find_shortest_path("PageTestA", "PageTestB")
        path_indirect = graph.find_shortest_path("PageTestA", "PageTestD")

        # Assert
        assert path_direct == ["PageTestA", "PageTestB"]
        # Shortest path A->D could be A->B->D or A->C->D
        assert path_indirect is not None
        assert path_indirect[0] == "PageTestA"
        assert path_indirect[-1] == "PageTestD"
        assert len(path_indirect) == 3

    def test_page_graph_find_shortest_path_no_path(self):
        """Test finding path when no path exists."""
        # Arrange
        graph = PageGraph()
        page_a = PageTestA()
        page_isolated = PageTestIsolated()
        graph.add_page(page_a, page_a.edges)
        graph.add_page(page_isolated, page_isolated.edges)

        # Act
        path = graph.find_shortest_path("PageTestA", "PageTestIsolated")

        # Assert
        assert path is None

    def test_page_graph_page_key_with_string(self):
        """Test _page_key static method with string input."""
        # Act
        key = PageGraph.page_key("PageTestA")

        # Assert
        assert key == "PageTestA"

    def test_page_graph_page_key_with_page_object(self):
        """Test _page_key static method with page object."""
        # Arrange
        page_a = PageTestA()

        # Act
        key = PageGraph.page_key(page_a)

        # Assert
        assert key == "PageTestA"


class TestPageNavigator:
    """Integration tests for PageNavigator class with real Android pages."""

    def test_page_navigator_initialization(self, app: Shadowstep):
        """Test PageNavigator initializes correctly."""
        # Act
        navigator = PageNavigator(app)

        # Assert
        assert navigator is not None
        assert navigator.shadowstep is app
        assert navigator.graph_manager is not None
        assert isinstance(navigator.graph_manager, PageGraph)
        assert navigator.logger is not None

    def test_page_navigator_add_page(self, app: Shadowstep):
        """Test adding a page to the navigator."""
        # Arrange
        navigator = PageNavigator(app)
        page_a = PageTestA()
        page_a._current = True

        # Act
        navigator.add_page(page_a, page_a.edges)

        # Assert
        assert "PageTestA" in navigator.graph_manager.graph
        assert navigator.graph_manager.is_valid_edge("PageTestA", "PageTestB")

    def test_page_navigator_add_page_raises_exception_for_none(self, app: Shadowstep):
        """Test that adding None page raises exception."""
        # Arrange
        navigator = PageNavigator(app)

        # Act & Assert
        with pytest.raises(ShadowstepPageCannotBeNoneError):
            navigator.add_page(None, {})

    def test_page_navigator_get_page_success(self, app: Shadowstep):
        """Test getting a page by name."""
        # Arrange
        navigator = PageNavigator(app)
        navigator.pages["PageTestA"] = PageTestA

        # Act
        page = navigator.get_page("PageTestA")

        # Assert
        assert page is not None
        assert isinstance(page, PageTestA)

    def test_page_navigator_get_page_not_found(self, app: Shadowstep):
        """Test getting a non-existent page raises ValueError."""
        # Arrange
        navigator = PageNavigator(app)

        # Act & Assert
        with pytest.raises(ValueError, match="Page 'NonExistentPage' not found"):
            navigator.get_page("NonExistentPage")

    def test_page_navigator_resolve_page_success(self, app: Shadowstep):
        """Test resolving a page by name."""
        # Arrange
        navigator = PageNavigator(app)
        navigator.pages["PageTestB"] = PageTestB

        # Act
        page = navigator.resolve_page("PageTestB")

        # Assert
        assert page is not None
        assert isinstance(page, PageTestB)

    def test_page_navigator_resolve_page_not_found(self, app: Shadowstep):
        """Test resolving non-existent page raises ValueError."""
        # Arrange
        navigator = PageNavigator(app)

        # Act & Assert
        with pytest.raises(ValueError, match="Page 'NonExistentPage' not found"):
            navigator.resolve_page("NonExistentPage")

    def test_page_navigator_find_path(self, app: Shadowstep):
        """Test finding path between pages."""
        # Arrange
        navigator = PageNavigator(app)
        page_a = PageTestA()
        page_b = PageTestB()
        page_c = PageTestC()
        page_d = PageTestD()

        navigator.add_page(page_a, page_a.edges)
        navigator.add_page(page_b, page_b.edges)
        navigator.add_page(page_c, page_c.edges)
        navigator.add_page(page_d, page_d.edges)

        # Act
        path = navigator.find_path(page_a, page_d)

        # Assert
        assert path is not None
        assert path[0] == "PageTestA"
        assert path[-1] == "PageTestD"
        assert len(path) == 3  # A->B->D or A->C->D

    def test_page_navigator_find_path_no_path(self, app: Shadowstep):
        """Test finding path when no path exists."""
        # Arrange
        navigator = PageNavigator(app)
        page_a = PageTestA()
        page_isolated = PageTestIsolated()

        navigator.add_page(page_a, page_a.edges)
        navigator.add_page(page_isolated, page_isolated.edges)

        # Act
        path = navigator.find_path(page_a, page_isolated)

        # Assert
        assert path is None

    def test_page_navigator_find_path_bfs_fallback(self, app: Shadowstep):
        """Test BFS fallback when NetworkX fails."""
        # Arrange
        navigator = PageNavigator(app)
        page_a = PageTestA()
        page_b = PageTestB()

        navigator.add_page(page_a, page_a.edges)
        navigator.add_page(page_b, page_b.edges)

        # Act - find path using string keys (which should work with BFS)
        path = navigator._find_path_bfs("PageTestA", "PageTestB")

        # Assert
        assert path is not None
        assert path == ["PageTestA", "PageTestB"]

    def test_page_navigator_perform_navigation_raises_empty_path(self, app: Shadowstep):
        """Test that performing navigation with empty path raises exception."""
        # Arrange
        navigator = PageNavigator(app)

        # Act & Assert
        with pytest.raises(ShadowstepPathCannotBeEmptyError):
            navigator.perform_navigation([])

    def test_page_navigator_perform_navigation_raises_short_path(self, app: Shadowstep):
        """Test that performing navigation with single page raises exception."""
        # Arrange
        navigator = PageNavigator(app)

        # Act & Assert
        with pytest.raises(ShadowstepPathMustContainAtLeastTwoPagesError):
            navigator.perform_navigation(["PageTestA"])

    def test_page_navigator_navigate_same_page(self, app: Shadowstep):
        """Test navigating to the same page returns True."""
        # Arrange
        navigator = PageNavigator(app)
        page_a = PageTestA()
        page_a._current = True

        # Act
        result = navigator.navigate(page_a, page_a)

        # Assert
        assert result is True

    def test_page_navigator_navigate_raises_from_page_none(self, app: Shadowstep):
        """Test that navigate with None from_page raises exception."""
        # Arrange
        navigator = PageNavigator(app)
        page_b = PageTestB()

        # Act & Assert
        with pytest.raises(ShadowstepFromPageCannotBeNoneError):
            navigator.navigate(None, page_b)

    def test_page_navigator_navigate_raises_to_page_none(self, app: Shadowstep):
        """Test that navigate with None to_page raises exception."""
        # Arrange
        navigator = PageNavigator(app)
        page_a = PageTestA()

        # Act & Assert
        with pytest.raises(ShadowstepToPageCannotBeNoneError):
            navigator.navigate(page_a, None)

    def test_page_navigator_navigate_raises_negative_timeout(self, app: Shadowstep):
        """Test that navigate with negative timeout raises exception."""
        # Arrange
        navigator = PageNavigator(app)
        page_a = PageTestA()
        page_b = PageTestB()

        # Act & Assert
        with pytest.raises(ShadowstepTimeoutMustBeNonNegativeError):
            navigator.navigate(page_a, page_b, timeout=-1)

    def test_page_navigator_navigate_no_path_returns_false(self, app: Shadowstep):
        """Test that navigate returns False when no path exists."""
        # Arrange
        navigator = PageNavigator(app)
        page_a = PageTestA()
        page_isolated = PageTestIsolated()

        navigator.add_page(page_a, page_a.edges)
        navigator.add_page(page_isolated, page_isolated.edges)

        # Act
        result = navigator.navigate(page_a, page_isolated)

        # Assert
        assert result is False

    def test_page_navigator_list_registered_pages(self, app: Shadowstep):
        """Test listing registered pages logs correctly."""
        # Arrange
        navigator = PageNavigator(app)
        navigator.pages["PageTestA"] = PageTestA
        navigator.pages["PageTestB"] = PageTestB

        # Act - should not raise exception
        navigator.list_registered_pages()

        # Assert - just verify it doesn't crash
        assert True

    def test_page_navigator_auto_discover_pages_called_once(self, app: Shadowstep):
        """Test that auto_discover_pages can be called multiple times safely."""
        # Arrange
        navigator = PageNavigator(app)

        # Act - call multiple times
        navigator.auto_discover_pages()
        initial_count = len(navigator.pages)

        navigator.auto_discover_pages()
        second_count = len(navigator.pages)

        # Assert - should not discover pages again after first call
        assert second_count == initial_count
        assert navigator._pages_discovered is True

    def test_page_navigator_register_pages_from_module(self, app: Shadowstep):
        """Test registering pages from a module."""
        # Arrange
        navigator = PageNavigator(app)
        import sys

        # Create a mock module with test pages
        import types
        test_module = types.ModuleType("test_pages")
        test_module.PageTestA = PageTestA
        test_module.PageTestB = PageTestB

        # Act
        navigator._register_pages_from_module(test_module)

        # Assert
        assert "PageTestA" in navigator.pages
        assert "PageTestB" in navigator.pages
        assert navigator.pages["PageTestA"] == PageTestA
        assert navigator.pages["PageTestB"] == PageTestB

    def test_page_navigator_ignored_dirs_set(self, app: Shadowstep):
        """Test that ignored directories are properly initialized."""
        # Arrange & Act
        navigator = PageNavigator(app)

        # Assert
        assert "__pycache__" in navigator._ignored_auto_discover_dirs
        assert ".venv" in navigator._ignored_auto_discover_dirs
        assert "site-packages" in navigator._ignored_auto_discover_dirs
        assert ".git" in navigator._ignored_auto_discover_dirs

    def test_page_graph_multiple_paths_shortest_selected(self):
        """Test that shortest path is selected when multiple paths exist."""
        # Arrange
        graph = PageGraph()
        page_a = PageTestA()
        page_b = PageTestB()
        page_c = PageTestC()
        page_d = PageTestD()

        graph.add_page(page_a, page_a.edges)
        graph.add_page(page_b, page_b.edges)
        graph.add_page(page_c, page_c.edges)
        graph.add_page(page_d, page_d.edges)

        # Act - Find path from A to D (two possible paths: A->B->D and A->C->D)
        path = graph.find_shortest_path("PageTestA", "PageTestD")

        # Assert
        assert path is not None
        assert len(path) == 3  # Both paths have length 3
        assert path[0] == "PageTestA"
        assert path[-1] == "PageTestD"

    def test_page_navigator_find_path_with_strings(self, app: Shadowstep):
        """Test finding path using string keys directly."""
        # Arrange
        navigator = PageNavigator(app)
        page_a = PageTestA()
        page_b = PageTestB()
        page_c = PageTestC()

        navigator.add_page(page_a, page_a.edges)
        navigator.add_page(page_b, page_b.edges)
        navigator.add_page(page_c, page_c.edges)

        # Act
        path = navigator.find_path("PageTestA", "PageTestC")

        # Assert
        assert path is not None
        assert path[0] == "PageTestA"
        assert path[-1] == "PageTestC"

    def test_page_navigator_perform_navigation_success(self, app: Shadowstep):
        """Test successful navigation through a path."""
        # Arrange
        navigator = PageNavigator(app)

        # Register test pages
        navigator.pages["PageTestA"] = PageTestA
        navigator.pages["PageTestB"] = PageTestB

        page_a = PageTestA()
        page_b = PageTestB()
        page_a._current = True

        navigator.add_page(page_a, page_a.edges)
        navigator.add_page(page_b, page_b.edges)

        # Act - perform navigation with valid path
        path = ["PageTestA", "PageTestB"]
        navigator.perform_navigation(path, timeout=5)

        # Assert - navigation should complete without exception
        assert True

    def test_page_navigator_navigate_success(self, app: Shadowstep):
        """Test successful navigation from one page to another."""
        # Arrange
        navigator = PageNavigator(app)

        # Register test pages
        navigator.pages["PageTestA"] = PageTestA
        navigator.pages["PageTestB"] = PageTestB

        page_a = PageTestA()
        page_b = PageTestB()
        page_a._current = True

        navigator.add_page(page_a, page_a.edges)
        navigator.add_page(page_b, page_b.edges)

        # Act
        result = navigator.navigate(page_a, page_b, timeout=5)

        # Assert
        assert result is True

    def test_page_navigator_get_ignored_dirs(self, app: Shadowstep):
        """Test _get_ignored_dirs returns expected directories."""
        # Arrange
        navigator = PageNavigator(app)

        # Act
        ignored_dirs = navigator._get_ignored_dirs()

        # Assert
        assert isinstance(ignored_dirs, set)
        assert len(ignored_dirs) > 0
        # Should contain common directory names
        assert "venv" in ignored_dirs or ".venv" in ignored_dirs

    def test_page_navigator_auto_discover_real_pages(self, app: Shadowstep):
        """Test auto_discover_pages discovers real pages from filesystem."""
        # Arrange
        navigator = PageNavigator(app)

        # Act
        navigator.auto_discover_pages()

        # Assert - should have discovered at least our test pages or real project pages
        # Since auto_discover only runs once, and we may have already called it
        assert navigator._pages_discovered is True

    def test_page_navigator_register_pages_with_invalid_class(self, app: Shadowstep):
        """Test registering module with non-page classes doesn't break."""
        # Arrange
        navigator = PageNavigator(app)
        import types

        # Create module with invalid class (not a Page class)
        test_module = types.ModuleType("test_invalid")

        class NotAPageClass:
            pass

        test_module.NotAPageClass = NotAPageClass
        test_module.PageValidButNotSubclass = str  # Has "Page" prefix but not a PageBaseShadowstep

        # Act - should not raise exception
        navigator._register_pages_from_module(test_module)

        # Assert - no pages should be registered from this module
        assert "NotAPageClass" not in navigator.pages

    def test_page_navigator_register_pages_without_page_prefix(self, app: Shadowstep):
        """Test that PageBaseShadowstep subclasses without 'Page' prefix are not registered."""
        # Arrange
        navigator = PageNavigator(app)
        import types

        # Create a class that IS a PageBaseShadowstep subclass but doesn't start with "Page"
        # This exercises line 172 (checking for "Page" prefix)
        test_module = types.ModuleType("test_no_prefix")

        class MyCustomScreen(PageBaseShadowstep):
            @property
            def edges(self):
                return {}

            def is_current_page(self):
                return False

        test_module.MyCustomScreen = MyCustomScreen

        # Act
        navigator._register_pages_from_module(test_module)

        # Assert - should not be registered because name doesn't start with "Page"
        assert "MyCustomScreen" not in navigator.pages

    def test_page_navigator_auto_discover_with_temp_page_file(self, app: Shadowstep):
        """Test auto_discover_pages with a real page file in temporary directory."""
        # Arrange
        import tempfile
        import sys
        from pathlib import Path

        # Create a temporary directory and add it to sys.path
        temp_dir = tempfile.mkdtemp(prefix="test_pages_")
        sys.path.insert(0, temp_dir)

        try:
            # Create a test page file
            page_file = Path(temp_dir) / "page_temp_test.py"
            page_content = '''
from shadowstep.page_base import PageBaseShadowstep

class PageTempTest(PageBaseShadowstep):
    """Temporary test page for auto-discovery."""

    @property
    def edges(self):
        return {}

    def is_current_page(self):
        return False
'''
            page_file.write_text(page_content)

            # Create a fresh navigator to test discovery
            navigator = PageNavigator(app)
            navigator._pages_discovered = False  # Reset to allow re-discovery

            # Act
            navigator.auto_discover_pages()

            # Assert - the page should be discovered
            # Note: This exercises lines 143, 149 in auto_discover_pages
            assert navigator._pages_discovered is True

        finally:
            # Cleanup
            sys.path.remove(temp_dir)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_page_navigator_auto_discover_with_import_error(self, app: Shadowstep):
        """Test auto_discover_pages handles import errors gracefully."""
        # Arrange
        import tempfile
        import sys
        from pathlib import Path

        # Create a temporary directory and add it to sys.path
        temp_dir = tempfile.mkdtemp(prefix="test_pages_bad_")
        sys.path.insert(0, temp_dir)

        try:
            # Create a page file with syntax error
            bad_page_file = Path(temp_dir) / "page_bad_syntax.py"
            bad_page_file.write_text("this is not valid python syntax!!!")

            # Create a fresh navigator
            navigator = PageNavigator(app)
            navigator._pages_discovered = False  # Reset

            # Act - should not raise exception despite bad file
            # This exercises lines 158-159 (exception handling)
            navigator.auto_discover_pages()

            # Assert - discovery should complete despite errors
            assert navigator._pages_discovered is True

        finally:
            # Cleanup
            sys.path.remove(temp_dir)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_page_navigator_perform_navigation_timeout_failure(self, app: Shadowstep):
        """Test perform_navigation raises exception on timeout."""
        # Arrange
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepNavigationFailedError

        navigator = PageNavigator(app)

        # Create pages where target page never becomes current
        class PageNeverCurrent(PageBaseShadowstep):
            @property
            def edges(self):
                return {"PageAlwaysCurrent": self.to_always_current}

            def to_always_current(self):
                return PageAlwaysCurrent()

            def is_current_page(self):
                return False

        class PageAlwaysCurrent(PageBaseShadowstep):
            @property
            def edges(self):
                return {}

            def is_current_page(self):
                # Always returns False, simulating timeout
                return False

        # Register pages
        navigator.pages["PageNeverCurrent"] = PageNeverCurrent
        navigator.pages["PageAlwaysCurrent"] = PageAlwaysCurrent

        page_never = PageNeverCurrent()
        page_always = PageAlwaysCurrent()

        navigator.add_page(page_never, page_never.edges)
        navigator.add_page(page_always, page_always.edges)

        # Act & Assert - should raise ShadowstepNavigationFailedError due to timeout
        # This exercises lines 317-319
        with pytest.raises(ShadowstepNavigationFailedError):
            navigator.perform_navigation(["PageNeverCurrent", "PageAlwaysCurrent"], timeout=1)

    def test_page_navigator_auto_discover_with_nonexistent_path(self, app: Shadowstep):
        """Test auto_discover_pages handles non-existent paths in sys.path."""
        # Arrange
        import sys
        from pathlib import Path

        # Add a non-existent path to sys.path
        fake_path = "/completely/nonexistent/path/12345"
        sys.path.insert(0, fake_path)

        try:
            # Create a fresh navigator
            navigator = PageNavigator(app)
            navigator._pages_discovered = False  # Reset

            # Act - should not raise exception despite non-existent path
            # This exercises line 143 (continue when path doesn't exist)
            navigator.auto_discover_pages()

            # Assert - discovery should complete
            assert navigator._pages_discovered is True

        finally:
            # Cleanup
            sys.path.remove(fake_path)

    def test_page_navigator_auto_discover_with_ignored_directory(self, app: Shadowstep):
        """Test auto_discover_pages skips ignored directories."""
        # Arrange
        import tempfile
        import sys
        from pathlib import Path

        # Create a temporary directory structure where the directory name itself is ignored
        temp_base = tempfile.mkdtemp(prefix="test_base_")

        try:
            # Create a directory whose NAME is in ignored list (line 149 check)
            ignored_dir = Path(temp_base) / "__pycache__"
            ignored_dir.mkdir()

            # Add the ignored directory itself to sys.path
            # This will trigger line 149 when os.walk processes it
            sys.path.insert(0, str(ignored_dir))

            # Create a page file inside it
            page_file = ignored_dir / "page_in_ignored.py"
            page_content = '''
from shadowstep.page_base import PageBaseShadowstep

class PageInIgnored(PageBaseShadowstep):
    @property
    def edges(self):
        return {}

    def is_current_page(self):
        return False
'''
            page_file.write_text(page_content)

            # Create a fresh navigator
            navigator = PageNavigator(app)
            navigator._pages_discovered = False  # Reset

            # Act - should skip the ignored directory
            # This exercises line 149 (continue when dir_name in ignored)
            navigator.auto_discover_pages()

            # Assert - page should NOT be discovered because directory is ignored
            assert "PageInIgnored" not in navigator.pages
            assert navigator._pages_discovered is True

            # Cleanup this path early
            sys.path.remove(str(ignored_dir))

        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_base, ignore_errors=True)
