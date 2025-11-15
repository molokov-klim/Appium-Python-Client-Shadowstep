# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Integration tests for the navigator module.

This module contains integration tests for the PageNavigator and PageGraph classes,
testing real navigation scenarios with actual Android pages.

Coverage notes:
- Tests PageGraph public API with real page instances
- Tests PageNavigator public API with real Android pages
- Tests navigation between actual Settings pages
- Tests path finding and edge validation
- Tests error handling for invalid inputs

Requirements:
- Shadowstep instance connected to Android device (app fixture)
- Real Android Settings app pages
"""

import pytest

from shadowstep.navigator.navigator import PageNavigator
from shadowstep.navigator.page_graph import PageGraph
from shadowstep.page_base import PageBaseShadowstep
from shadowstep.shadowstep import Shadowstep
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepPageCannotBeNoneError,
    ShadowstepFromPageCannotBeNoneError,
    ShadowstepToPageCannotBeNoneError,
    ShadowstepTimeoutMustBeNonNegativeError,
    ShadowstepPathCannotBeEmptyError,
    ShadowstepPathMustContainAtLeastTwoPagesError,
    ShadowstepNavigationFailedError,
)


class TestPageGraph:
    """Integration tests for PageGraph class with real page objects."""

    def test_page_graph_initialization(self):
        """Test PageGraph initializes correctly."""
        # Act
        graph = PageGraph()

        # Assert
        assert graph is not None

    def test_page_graph_add_page_with_real_page(self, app: Shadowstep):
        """Test adding a real page to the graph."""
        # Arrange
        graph = PageGraph()
        page = app.get_page("PageSettings")

        # Act
        graph.add_page(page, page.edges)

        # Assert - verify edges were added by checking if valid edges exist
        edges = graph.get_edges(page)
        assert len(edges) > 0, "PageSettings should have edges"

    def test_page_graph_add_page_raises_exception_for_none(self):
        """Test that adding None page raises exception."""
        # Arrange
        graph = PageGraph()

        # Act & Assert
        with pytest.raises(ShadowstepPageCannotBeNoneError):
            graph.add_page(None, {})

    def test_page_graph_get_edges_for_real_page(self, app: Shadowstep):
        """Test getting edges for a real page."""
        # Arrange
        graph = PageGraph()
        page = app.get_page("PageSettings")
        graph.add_page(page, page.edges)

        # Act
        edges = graph.get_edges(page)

        # Assert
        assert isinstance(edges, list)
        assert len(edges) > 0

    def test_page_graph_get_edges_for_nonexistent_page(self):
        """Test getting edges for a page that doesn't exist returns empty list."""
        # Arrange
        graph = PageGraph()

        # Act
        edges = graph.get_edges("NonExistentPage")

        # Assert
        assert edges == []

    def test_page_graph_is_valid_edge_with_real_pages(self, app: Shadowstep):
        """Test checking if an edge is valid with real pages."""
        # Arrange
        graph = PageGraph()
        settings_page = app.get_page("PageSettings")
        graph.add_page(settings_page, settings_page.edges)

        # Act - check valid edge from settings
        edges = settings_page.edges
        if edges:
            first_edge_name = list(edges.keys())[0]
            is_valid = graph.is_valid_edge(settings_page, first_edge_name)

            # Assert
            assert is_valid is True

    def test_page_graph_is_valid_edge_invalid(self, app: Shadowstep):
        """Test checking invalid edge returns False."""
        # Arrange
        graph = PageGraph()
        settings_page = app.get_page("PageSettings")
        graph.add_page(settings_page, settings_page.edges)

        # Act
        is_valid = graph.is_valid_edge(settings_page, "NonExistentPage")

        # Assert
        assert is_valid is False

    def test_page_graph_page_key_with_string(self):
        """Test page_key static method with string input."""
        # Act
        key = PageGraph.page_key("PageSettings")

        # Assert
        assert key == "PageSettings"

    def test_page_graph_page_key_with_page_object(self, app: Shadowstep):
        """Test page_key static method with real page object."""
        # Arrange
        page = app.get_page("PageSettings")

        # Act
        key = PageGraph.page_key(page)

        # Assert
        assert key == "PageSettings"

    def test_page_graph_has_path_with_connected_pages(self, app: Shadowstep):
        """Test has_path returns True for connected pages."""
        # Arrange
        graph = PageGraph()
        settings_page = app.get_page("PageSettings")
        network_page = app.get_page("PageNetworkInternet")
        
        graph.add_page(settings_page, settings_page.edges)
        graph.add_page(network_page, network_page.edges)

        # Act
        has_path = graph.has_path("PageSettings", "PageNetworkInternet")

        # Assert
        assert has_path is True

    def test_page_graph_find_shortest_path_with_real_pages(self, app: Shadowstep):
        """Test finding shortest path between real pages."""
        # Arrange
        graph = PageGraph()
        settings_page = app.get_page("PageSettings")
        network_page = app.get_page("PageNetworkInternet")
        
        graph.add_page(settings_page, settings_page.edges)
        graph.add_page(network_page, network_page.edges)

        # Act
        path = graph.find_shortest_path("PageSettings", "PageNetworkInternet")

        # Assert
        assert path is not None
        assert path[0] == "PageSettings"
        assert path[-1] == "PageNetworkInternet"


class TestPageNavigator:
    """Integration tests for PageNavigator class with real Android pages."""

    def test_page_navigator_initialization(self, app: Shadowstep):
        """Test PageNavigator initializes correctly with Shadowstep instance."""
        # Act
        navigator = PageNavigator(app)

        # Assert
        assert navigator is not None
        assert navigator.shadowstep is app
        assert navigator.graph_manager is not None
        assert isinstance(navigator.graph_manager, PageGraph)

    def test_page_navigator_add_page_with_real_page(self, app: Shadowstep):
        """Test adding a real page to the navigator."""
        # Arrange
        navigator = PageNavigator(app)
        page = app.get_page("PageSettings")

        # Act
        navigator.add_page(page, page.edges)

        # Assert - verify page was added by checking edges
        edges = navigator.graph_manager.get_edges(page)
        assert len(edges) > 0

    def test_page_navigator_add_page_raises_exception_for_none(self, app: Shadowstep):
        """Test that adding None page raises exception."""
        # Arrange
        navigator = PageNavigator(app)

        # Act & Assert
        with pytest.raises(ShadowstepPageCannotBeNoneError):
            navigator.add_page(None, {})

    def test_page_navigator_auto_discover_pages(self, app: Shadowstep):
        """Test auto_discover_pages discovers real pages from filesystem."""
        # Arrange
        navigator = PageNavigator(app)

        # Act
        navigator.auto_discover_pages()

        # Assert - should have discovered some pages
        assert len(navigator.pages) > 0, "Should discover at least some pages"

    def test_page_navigator_auto_discover_pages_idempotent(self, app: Shadowstep):
        """Test that auto_discover_pages can be called multiple times safely."""
        # Arrange
        navigator = PageNavigator(app)

        # Act
        navigator.auto_discover_pages()
        first_count = len(navigator.pages)
        
        navigator.auto_discover_pages()
        second_count = len(navigator.pages)

        # Assert
        assert second_count == first_count, "Second call should not discover new pages"

    def test_page_navigator_get_page_success(self, app: Shadowstep):
        """Test getting a page by name after discovery."""
        # Arrange
        navigator = PageNavigator(app)
        navigator.auto_discover_pages()

        # Act
        page = navigator.get_page("PageSettings")

        # Assert
        assert page is not None
        assert isinstance(page, PageBaseShadowstep)

    def test_page_navigator_get_page_not_found(self, app: Shadowstep):
        """Test getting a non-existent page raises ValueError."""
        # Arrange
        navigator = PageNavigator(app)

        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            navigator.get_page("CompletelyNonExistentPage")

    def test_page_navigator_resolve_page_success(self, app: Shadowstep):
        """Test resolving a page by name after discovery."""
        # Arrange
        navigator = PageNavigator(app)
        navigator.auto_discover_pages()

        # Act
        page = navigator.resolve_page("PageSettings")

        # Assert
        assert page is not None
        assert isinstance(page, PageBaseShadowstep)

    def test_page_navigator_resolve_page_not_found(self, app: Shadowstep):
        """Test resolving non-existent page raises ValueError."""
        # Arrange
        navigator = PageNavigator(app)

        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            navigator.resolve_page("CompletelyNonExistentPage")

    def test_page_navigator_find_path_between_real_pages(self, app: Shadowstep):
        """Test finding path between real Android pages."""
        # Arrange
        navigator = PageNavigator(app)
        settings_page = app.get_page("PageSettings")
        network_page = app.get_page("PageNetworkInternet")
        
        navigator.add_page(settings_page, settings_page.edges)
        navigator.add_page(network_page, network_page.edges)

        # Act
        path = navigator.find_path(settings_page, network_page)

        # Assert
        assert path is not None
        assert "PageSettings" in path
        assert "PageNetworkInternet" in path

    def test_page_navigator_list_registered_pages(self, app: Shadowstep):
        """Test listing registered pages doesn't raise exception."""
        # Arrange
        navigator = PageNavigator(app)
        navigator.auto_discover_pages()

        # Act - should not raise exception
        navigator.list_registered_pages()

        # Assert
        assert True

    def test_page_navigator_navigate_same_page_returns_true(self, app: Shadowstep):
        """Test navigating to the same page returns True immediately."""
        # Arrange
        navigator = PageNavigator(app)
        page = app.get_page("PageSettings")

        # Act
        result = navigator.navigate(page, page)

        # Assert
        assert result is True

    def test_page_navigator_navigate_raises_from_page_none(self, app: Shadowstep):
        """Test that navigate with None from_page raises exception."""
        # Arrange
        navigator = PageNavigator(app)
        page = app.get_page("PageSettings")

        # Act & Assert
        with pytest.raises(ShadowstepFromPageCannotBeNoneError):
            navigator.navigate(None, page)

    def test_page_navigator_navigate_raises_to_page_none(self, app: Shadowstep):
        """Test that navigate with None to_page raises exception."""
        # Arrange
        navigator = PageNavigator(app)
        page = app.get_page("PageSettings")

        # Act & Assert
        with pytest.raises(ShadowstepToPageCannotBeNoneError):
            navigator.navigate(page, None)

    def test_page_navigator_navigate_raises_negative_timeout(self, app: Shadowstep):
        """Test that navigate with negative timeout raises exception."""
        # Arrange
        navigator = PageNavigator(app)
        page1 = app.get_page("PageSettings")
        page2 = app.get_page("PageNetworkInternet")

        # Act & Assert
        with pytest.raises(ShadowstepTimeoutMustBeNonNegativeError):
            navigator.navigate(page1, page2, timeout=-1)

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
            navigator.perform_navigation(["PageSettings"])

    def test_page_navigator_prepare_navigation_structures(self, app: Shadowstep):
        """Test preparing navigation structures with real pages (no actual navigation)."""
        # Arrange
        navigator = PageNavigator(app)
        settings_page = app.get_page("PageSettings")
        network_page = app.get_page("PageNetworkInternet")
        
        navigator.add_page(settings_page, settings_page.edges)
        navigator.add_page(network_page, network_page.edges)

        # Register pages in navigator.pages
        navigator.pages["PageSettings"] = type(settings_page)
        navigator.pages["PageNetworkInternet"] = type(network_page)

        # Act - find path (without executing it)
        path = navigator.find_path(settings_page, network_page)

        # Assert
        assert path is not None
        assert len(path) >= 2
        assert "PageSettings" in path
        assert "PageNetworkInternet" in path

    def test_page_navigator_find_path_with_string_keys(self, app: Shadowstep):
        """Test finding path using string keys instead of page objects."""
        # Arrange
        navigator = PageNavigator(app)
        settings_page = app.get_page("PageSettings")
        network_page = app.get_page("PageNetworkInternet")
        
        navigator.add_page(settings_page, settings_page.edges)
        navigator.add_page(network_page, network_page.edges)

        # Act
        path = navigator.find_path("PageSettings", "PageNetworkInternet")

        # Assert
        assert path is not None
        assert "PageSettings" in path
        assert "PageNetworkInternet" in path

    def test_page_navigator_build_navigation_graph(self, app: Shadowstep):
        """Test building complete navigation graph with real pages."""
        # Arrange
        navigator = PageNavigator(app)
        settings_page = app.get_page("PageSettings")
        network_page = app.get_page("PageNetworkInternet")
        
        navigator.add_page(settings_page, settings_page.edges)
        navigator.add_page(network_page, network_page.edges)

        navigator.pages["PageSettings"] = type(settings_page)
        navigator.pages["PageNetworkInternet"] = type(network_page)

        # Act - verify graph structure
        has_path = navigator.graph_manager.has_path("PageSettings", "PageNetworkInternet")
        is_valid_edge = navigator.graph_manager.is_valid_edge("PageSettings", "PageNetworkInternet")

        # Assert
        assert has_path is True
        assert is_valid_edge is True
