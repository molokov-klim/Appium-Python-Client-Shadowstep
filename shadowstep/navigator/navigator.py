# shadowstep/navigator/navigator.py
"""Navigation module for managing page transitions in Shadowstep framework.

This module provides functionality for navigating between pages using graph-based
pathfinding algorithms. It supports both NetworkX-based shortest path finding
and fallback BFS traversal.
"""


from __future__ import annotations

import logging
import traceback
from collections import deque
from typing import TYPE_CHECKING, Any, cast

import networkx as nx
from networkx.classes import DiGraph
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
from shadowstep.page_base import PageBaseShadowstep

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from shadowstep.shadowstep import Shadowstep

# Constants
DEFAULT_NAVIGATION_TIMEOUT = 55
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
            self.logger.info(f"⏭️ Already on target page: {to_page}")
            return True

        path = self.find_path(from_page, to_page)
        if not path:
            self.logger.error(f"❌ No dom path found from {from_page} to {to_page}")
            return False

        self.logger.info(
            f"🚀 Navigating: {from_page} ➡ {to_page} via path: {[repr(page) for page in path]}",
        )

        try:
            self.perform_navigation(cast("list[PageBaseShadowstep]", path), timeout)
            self.logger.info(f"✅ Successfully navigated to {to_page}")
        except WebDriverException:
            self.logger.exception(f"❗ WebDriverException during dom from {from_page} to {to_page}")
            self.logger.debug("📌 Full traceback:\n" + "".join(traceback.format_stack()))
            return False
        else:
            return True

    def find_path(self, start: Any, target: Any) -> list[Any] | None:
        """Find a path from start page to target page.

        Args:
            start: Starting page (can be string or page object).
            target: Target page (can be string or page object).

        Returns:
            List of pages representing the path, or None if no path exists.

        """
        if isinstance(start, str):
            start = self.shadowstep.resolve_page(start)
        if isinstance(target, str):
            target = self.shadowstep.resolve_page(target)

        try:
            path = self.graph_manager.find_shortest_path(start, target)
            if path:
                return path
        except NetworkXException:
            self.logger.exception("NetworkX error in find_shortest_path")

        # Fallback: BFS traversal
        return self._find_path_bfs(start, target)

    def _find_path_bfs(self, start: Any, target: Any) -> list[Any] | None:
        """Find path using breadth-first search as fallback.

        Args:
            start: Starting page.
            target: Target page.

        Returns:
            List of pages representing the path, or None if no path exists.

        """
        visited = set()
        queue = deque([(start, [])])  # type: ignore[arg-type]
        while queue:
            current_page, path = queue.popleft()
            visited.add(current_page)
            transitions = self.graph_manager.get_edges(current_page)
            for next_page_name in transitions:
                next_page = self.shadowstep.resolve_page(cast("str", next_page_name))
                if next_page == target:
                    return path + [current_page, next_page]
                if next_page not in visited:
                    queue.append((next_page, path + [current_page]))
        return None

    def perform_navigation(self, path: list[Any], timeout: int = DEFAULT_NAVIGATION_TIMEOUT) -> None:
        """Perform dom through a given path of PageBase instances.

        Args:
            path: List of page objects to traverse.
            timeout: Timeout for each dom step.

        Raises:
            ValueError: If path is empty or has only one element.
            AssertionError: If dom to next page fails.

        """
        if not path:
            raise ShadowstepPathCannotBeEmptyError
        if len(path) < MIN_PATH_LENGTH:
            raise ShadowstepPathMustContainAtLeastTwoPagesError

        for i in range(len(path) - 1):
            current_page = path[i]
            next_page = path[i + 1]
            transition_method = current_page.edges[next_page.__class__.__name__]
            transition_method()
            if not next_page.is_current_page():
                raise ShadowstepNavigationFailedError(current_page, next_page, transition_method)


class PageGraph:
    """Manages the graph of page transitions.

    This class maintains both a simple dictionary-based graph and a NetworkX
    directed graph for efficient pathfinding operations.

    Attributes:
        graph: Dictionary-based graph for backward compatibility.
        nx_graph: NetworkX directed graph for advanced operations.

    """

    def __init__(self) -> None:
        """Initialize the PageGraph with empty graphs."""
        self.graph: dict[Any, Any] = {}  # Legacy dictionary-based graph
        self.nx_graph: DiGraph[Any] = nx.DiGraph()  # NetworkX directed graph

    def add_page(self, page: Any, edges: Any) -> None:
        """Add a page and its edges to both graph representations.

        Args:
            page: The page object to add.
            edges: Dictionary or list of target pages/names.

        Raises:
            TypeError: If page is None.

        """
        if page is None:
            raise ShadowstepPageCannotBeNoneError

        self.graph[page] = edges

        # Add vertex and edges to NetworkX graph
        self.nx_graph.add_node(page)
        if isinstance(edges, (dict, list, tuple)):
            for target_name in edges:
                self.nx_graph.add_edge(page, target_name)

    def get_edges(self, page: Any) -> list[Any]:
        """Get edges for a given page.

        Args:
            page: The page to get edges for.

        Returns:
            List of target pages/names, empty list if page not found.

        """
        return self.graph.get(page, [])

    def is_valid_edge(self, from_page: Any, to_page: Any) -> bool:
        """Check if there's a valid edge between two pages.

        Args:
            from_page: Source page.
            to_page: Target page.

        Returns:
            True if edge exists, False otherwise.

        """
        transitions = self.get_edges(from_page)
        return to_page in transitions

    def has_path(self, from_page: Any, to_page: Any) -> bool:
        """Check if there's a path between two pages.

        Args:
            from_page: Source page.
            to_page: Target page.

        Returns:
            True if path exists, False otherwise.

        """
        try:
            return nx.has_path(self.nx_graph, from_page, to_page)
        except (nx.NetworkXError, KeyError):
            return False

    def find_shortest_path(self, from_page: Any, to_page: Any) -> list[Any] | None:
        """Find the shortest path between two pages.

        Args:
            from_page: Source page.
            to_page: Target page.

        Returns:
            List of pages representing the shortest path, or None if no path exists.

        """
        try:
            return nx.shortest_path(self.nx_graph, source=from_page, target=to_page)
        except nx.NetworkXNoPath:
            return None
        except nx.NodeNotFound:
            return None
        except nx.NetworkXError:
            return None
