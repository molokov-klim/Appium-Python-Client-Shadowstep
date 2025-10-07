"""Navigation module for managing page transitions in Shadowstep framework.

This module provides functionality for navigating between pages using graph-based
pathfinding algorithms. It supports both NetworkX-based shortest path finding
and fallback BFS traversal.
"""

from __future__ import annotations

import logging
import time
import traceback
from collections import deque
from typing import TYPE_CHECKING, Any

import networkx as nx
from networkx.exception import NetworkXException
from selenium.common import WebDriverException

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepFromPageCannotBeNoneError,
    ShadowstepNavigationFailedError,
    ShadowstepPageCannotBeNoneError,
    ShadowstepPathCannotBeEmptyError,
    ShadowstepPathMustContainAtLeastTwoPagesError,
    ShadowstepTimeoutMustBeNonNegativeError,
    ShadowstepToPageCannotBeNoneError,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from shadowstep.page_base import PageBaseShadowstep
    from shadowstep.shadowstep import Shadowstep

# Constants
DEFAULT_NAVIGATION_TIMEOUT = 10
MIN_PATH_LENGTH = 2


class PageNavigator:
    """Manages dom between pages using graph-based pathfinding.

    This class provides methods to navigate between different pages in the application
    by finding optimal paths through a graph of page transitions.

    Attributes:
        shadowstep: The main Shadowstep instance for page resolution.
        graph_manager: Manages the page transition graph.
        logger: Logger instance for dom events.

    """

    def __init__(self, shadowstep: Shadowstep) -> None:
        """Initialize the PageNavigator.

        Args:
            shadowstep: The main Shadowstep instance.

        Raises:
            TypeError: If shadowstep is None.

        """
        # shadowstep is already typed as Shadowstep, so it cannot be None

        self.shadowstep = shadowstep
        self.graph_manager = PageGraph()
        self.logger = logger

    def add_page(self, page: Any, edges: dict[str, Any]) -> None:
        """Add a page and its transitions to the dom graph.

        Args:
            page: The page object to add.
            edges: Dictionary mapping target page names to transition methods.

        Raises:
            TypeError: If page is None or edges is not a dictionary.

        """
        if page is None:
            raise ShadowstepPageCannotBeNoneError
        # edges is already typed as dict[str, Any], so isinstance check is unnecessary

        self.graph_manager.add_page(page=page, edges=edges)

    def navigate(self, from_page: Any, to_page: Any, timeout: int = DEFAULT_NAVIGATION_TIMEOUT) -> bool:
        """Navigate from one page to another following the defined graph.

        Args:
            from_page: The current page.
            to_page: The target page to navigate to.
            timeout: Timeout in seconds for dom.

        Returns:
            True if dom succeeded, False otherwise.

        Raises:
            TypeError: If from_page or to_page is None.
            ValueError: If timeout is negative.

        """
        if from_page is None:
            raise ShadowstepFromPageCannotBeNoneError
        if to_page is None:
            raise ShadowstepToPageCannotBeNoneError
        if timeout < 0:
            raise ShadowstepTimeoutMustBeNonNegativeError
        if from_page == to_page:
            self.logger.info("⏭️ Already on target page: %s", to_page)
            return True

        path = self.find_path(from_page, to_page)

        if not path:
            self.logger.error("❌ No dom path found from %s to %s", from_page, to_page)
            return False

        self.logger.info(
            "🚀 Navigating: %s ➡ %s via path: %s", from_page, to_page, [repr(page) for page in path],
        )

        try:
            self.perform_navigation(path, timeout)
            self.logger.info("✅ Successfully navigated to %s", to_page)
        except WebDriverException:
            self.logger.exception("❗ WebDriverException during dom from %s to %s", from_page, to_page)
            self.logger.debug("📌 Full traceback:\n%s", "".join(traceback.format_stack()))
            return False
        else:
            return True

    def find_path(self, start: Any, target: Any) -> list[str] | None:
        """Find a path from start page to target page."""
        start_key = self.graph_manager._page_key(start)
        target_key = self.graph_manager._page_key(target)

        try:
            path = self.graph_manager.find_shortest_path(start_key, target_key)
            if path:
                return path
        except NetworkXException:
            self.logger.exception("NetworkX error in find_shortest_path")

        # Fallback: BFS
        return self._find_path_bfs(start_key, target_key)

    def _find_path_bfs(self, start: str, target: str) -> list[str] | None:
        """Find path using breadth-first search as fallback."""
        visited = set()
        queue = deque([(start, [])])
        while queue:
            current, path = queue.popleft()
            visited.add(current)
            for next_page in self.graph_manager.get_edges(current):
                if next_page == target:
                    return [*path, current, next_page]
                if next_page not in visited:
                    queue.append((next_page, [*path, current]))
        return None

    def perform_navigation(self, path: list[str], timeout: int = DEFAULT_NAVIGATION_TIMEOUT) -> None:
        """Perform navigation through a given path of page names."""
        if not path:
            raise ShadowstepPathCannotBeEmptyError
        if len(path) < MIN_PATH_LENGTH:
            raise ShadowstepPathMustContainAtLeastTwoPagesError

        for i in range(len(path) - 1):
            current_name = path[i]
            next_name = path[i + 1]

            current_page = self.shadowstep.resolve_page(current_name)
            next_page = self.shadowstep.resolve_page(next_name)

            transition_method = current_page.edges[next_name]
            transition_method()

            end_time = time.time() + timeout
            while time.time() < end_time:
                if next_page.is_current_page():
                    break
                time.sleep(0.5)
            else:
                raise ShadowstepNavigationFailedError(current_page, next_page, transition_method)


class PageGraph:
    """Manages the graph of page transitions."""

    def __init__(self) -> None:
        """Initialize the PageGraph with empty graphs."""
        self.graph: dict[str, dict[str, Any]] = {}
        self.nx_graph: nx.DiGraph = nx.DiGraph()

    @staticmethod
    def _page_key(page: str | PageBaseShadowstep) -> str:
        """Normalize page to a consistent string key for graph operations."""
        if isinstance(page, str):
            return page
        return page.__class__.__name__

    def add_page(self, page: Any, edges: dict[str, Any]) -> None:
        """Add a page and its edges to both graph representations."""
        if page is None:
            raise ShadowstepPageCannotBeNoneError

        page_key = self._page_key(page)
        self.graph[page_key] = edges

        self.nx_graph.add_node(page_key)
        for target_name in edges:
            self.nx_graph.add_edge(page_key, self._page_key(target_name))

    def get_edges(self, page: Any) -> list[str]:
        """Get edges for a given page."""
        return list(self.graph.get(self._page_key(page), {}).keys())

    def is_valid_edge(self, from_page: Any, to_page: Any) -> bool:
        """Check if there's a valid edge between two pages."""
        from_key = self._page_key(from_page)
        to_key = self._page_key(to_page)
        return to_key in self.graph.get(from_key, {})

    def has_path(self, from_page: Any, to_page: Any) -> bool:
        """Check if there's a path between two pages."""
        try:
            return nx.has_path(
                self.nx_graph,
                self._page_key(from_page),
                self._page_key(to_page),
            )
        except (nx.NetworkXError, KeyError):
            return False

    def find_shortest_path(self, from_page: Any, to_page: Any) -> list[str] | None:
        """Find the shortest path between two pages."""
        try:
            return nx.shortest_path(
                self.nx_graph,
                source=self._page_key(from_page),
                target=self._page_key(to_page),
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound, nx.NetworkXError):
            logger.exception("Error finding shortest path")
            return None
