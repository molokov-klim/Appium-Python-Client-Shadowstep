# shadowstep/navigator/navigator.py
from __future__ import annotations

import logging
import traceback
from collections import deque
from typing import TYPE_CHECKING, Any, cast

import networkx as nx
from networkx.classes import DiGraph
from networkx.exception import NetworkXException
from selenium.common import WebDriverException

from shadowstep.page_base import PageBaseShadowstep

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from shadowstep.shadowstep import Shadowstep



class PageNavigator:
    def __init__(self, shadowstep: Shadowstep):
        self.shadowstep = shadowstep
        self.graph_manager = PageGraph()
        self.logger = logger

    def add_page(self, page: Any, edges: dict[str, Any]):
        self.graph_manager.add_page(page=page, edges=edges)

    def navigate(self, from_page: Any, to_page: Any, timeout: int = 55) -> bool:
        """Navigate from one page to another following the defined graph.

        Args:
            from_page (Any): The current page.
            to_page (Any): The target page to navigate to.
            timeout (int): Timeout in seconds for navigation.

        Returns:
            bool: True if navigation succeeded, False otherwise.
        """
        if from_page == to_page:
            self.logger.info(f"⏭️ Already on target page: {to_page}")
            return True

        path = self.find_path(from_page, to_page)
        if not path:
            self.logger.error(f"❌ No navigation path found from {from_page} to {to_page}")
            return False

        self.logger.info(
            f"🚀 Navigating: {from_page} ➡ {to_page} via path: {[repr(cast(Any, page)) for page in path]}"
        )

        try:
            self.perform_navigation(cast(list['PageBaseShadowstep'], path), timeout)
            self.logger.info(f"✅ Successfully navigated to {to_page}")
            return True
        except WebDriverException as error:
            self.logger.error(f"❗ WebDriverException during navigation from {from_page} to {to_page}: {error}")
            self.logger.debug("📌 Full traceback:\n" + "".join(traceback.format_stack()))
            return False

    def find_path(self, start: Any, target: Any):
        if isinstance(start, str):
            start = self.shadowstep.resolve_page(start)
        if isinstance(target, str):
            target = self.shadowstep.resolve_page(target)

        try:
            path = self.graph_manager.find_shortest_path(start, target)
            if path:
                return path
        except NetworkXException as error:
            self.logger.error(error)
            pass

        # fallback: BFS
        visited = set()
        queue = deque([(start, [])])    # type: ignore
        while queue:
            current_page, path = queue.popleft()
            visited.add(current_page)
            transitions = self.graph_manager.get_edges(current_page)
            for next_page_name in transitions:
                next_page = self.shadowstep.resolve_page(cast(str, next_page_name))
                if next_page == target:
                    return path + [current_page, next_page]
                if next_page not in visited:
                    queue.append((next_page, path + [current_page]))
        return None

    def perform_navigation(self, path: list['PageBaseShadowstep'], timeout: int = 55) -> None:
        """Perform navigation through a given path of PageBase instances.

        Args:
            path (List[PageBase]): List of page objects to traverse.
            timeout (int): Timeout for each navigation step.
        """
        for i in range(len(path) - 1):
            current_page = path[i]
            next_page = path[i + 1]
            transition_method = current_page.edges[next_page.__class__.__name__]
            transition_method()
            if not next_page.is_current_page():
                raise AssertionError(f"navigation error: \n from {current_page} to {next_page} with {transition_method}")


class PageGraph:
    def __init__(self):
        self.graph = {}  # старый способ
        self.nx_graph: DiGraph[Any] = nx.DiGraph()  # новый способ (networkx)

    def add_page(self, page: Any, edges: Any):
        self.graph[page] = edges

        # добавим вершину и рёбра в networkx-граф
        self.nx_graph.add_node(page)
        for target_name in edges:
            self.nx_graph.add_edge(page, target_name)

    def get_edges(self, page: Any):
        return self.graph.get(page, [])

    def is_valid_edge(self, from_page: Any, to_page: Any):
        transitions = self.get_edges(from_page)
        return to_page in transitions

    def has_path(self, from_page: Any, to_page: Any) -> bool:
        return nx.has_path(self.nx_graph, from_page, to_page)

    def find_shortest_path(self, from_page: Any, to_page: Any) -> list[Any] | None:
        try:
            return nx.shortest_path(self.nx_graph, source=from_page, target=to_page)
        except nx.NetworkXNoPath:
            return None
        except nx.NodeNotFound:
            return None
