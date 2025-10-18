"""Graph management for page navigation and transitions."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import networkx as nx

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepPageCannotBeNoneError

if TYPE_CHECKING:
    from shadowstep.page_base import PageBaseShadowstep

logger = logging.getLogger(__name__)

class PageGraph:
    """Manages the graph of page transitions."""

    def __init__(self) -> None:
        """Initialize the PageGraph with empty graphs."""
        self.graph: dict[str, dict[str, Any]] = {}
        self.nx_graph: nx.DiGraph[str] = nx.DiGraph()

    @staticmethod
    def page_key(page: str | PageBaseShadowstep) -> str:
        """Normalize page to a consistent string key for graph operations."""
        if isinstance(page, str):
            return page
        return page.__class__.__name__

    def add_page(self, page: Any, edges: dict[str, Any]) -> None:
        """Add a page and its edges to both graph representations."""
        if page is None:
            raise ShadowstepPageCannotBeNoneError

        page_key = self.page_key(page)
        self.graph[page_key] = edges

        self.nx_graph.add_node(page_key)
        for target_name in edges:
            self.nx_graph.add_edge(page_key, self.page_key(target_name))

    def get_edges(self, page: Any) -> list[str]:
        """Get edges for a given page."""
        return list(self.graph.get(self.page_key(page), {}).keys())

    def is_valid_edge(self, from_page: Any, to_page: Any) -> bool:
        """Check if there's a valid edge between two pages."""
        from_key = self.page_key(from_page)
        to_key = self.page_key(to_page)
        return to_key in self.graph.get(from_key, {})

    def has_path(self, from_page: Any, to_page: Any) -> bool:
        """Check if there's a path between two pages."""
        try:
            return nx.has_path(
                self.nx_graph,
                self.page_key(from_page),
                self.page_key(to_page),
            )
        except (nx.NetworkXError, KeyError):
            return False

    def find_shortest_path(self, from_page: Any, to_page: Any) -> list[str] | None:
        """Find the shortest path between two pages."""
        try:
            return nx.shortest_path(  # type: ignore[misc]
                self.nx_graph,
                source=self.page_key(from_page),
                target=self.page_key(to_page),
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound, nx.NetworkXError):
            logger.exception("Error finding shortest path")
            return None
