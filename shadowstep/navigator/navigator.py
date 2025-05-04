# shadowstep/navigator/navigator.py

import traceback

import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from typing import Any, Optional, List, Union
import logging
logger = logging.getLogger(__name__)
from networkx.exception import NetworkXException

from selenium.common import WebDriverException


class PageNavigator:
    def __init__(self, shadowstep: "ShadowstepBase"):
        self.shadowstep = shadowstep
        self.graph_manager = PageGraph()
        self.logger = logger

    def add_page(self, page, edges):
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

        self.logger.info(f"🚀 Navigating: {from_page} ➡ {to_page} via path: {[page.__repr__ for page in path]}")

        try:
            self.perform_navigation(path, timeout)
            self.logger.info(f"✅ Successfully navigated to {to_page}")
            return True
        except WebDriverException as error:
            self.logger.error(f"❗ WebDriverException during navigation from {from_page} to {to_page}: {error}")
            self.logger.debug("📌 Full traceback:\n" + "".join(traceback.format_stack()))
            return False

    def find_path(self, start, target):
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
        queue = deque([(start, [])])
        while queue:
            current_page, path = queue.popleft()
            visited.add(current_page)
            transitions = self.graph_manager.get_edges(current_page)
            for next_page_name in transitions:
                next_page = self.shadowstep.resolve_page(next_page_name)
                if next_page == target:
                    return path + [current_page, next_page]
                if next_page not in visited:
                    queue.append((next_page, path + [current_page]))
        return None

    def perform_navigation(self, path: List["PageBase"], timeout: int = 55) -> None:
        """Perform navigation through a given path of PageBase instances.

        Args:
            path (List[PageBase]): List of page objects to traverse.
            timeout (int): Timeout for each navigation step.
        """
        for i in range(len(path) - 1):
            current_page = path[i]
            next_page = path[i + 1]
            transition_method = current_page.edges[next_page.__class__.__name__]
            self.logger.info(
                f"Navigating from {current_page.__repr__} to {next_page.__repr__} "
                f"via method {transition_method.__repr__}"
            )
            transition_method()

    def perform_navigation(self, path: List["PageBase"], timeout: int = 55) -> None:
        for i in range(len(path) - 1):
            current_page = path[i]
            next_page = path[i + 1]
            transition_method = current_page.edges[next_page.__class__.__name__]
            transition_method()

    def save_graph(self, path: str = "page_graph.png"):
        self.graph_manager.save_graph_image(path)

    def test_graph(self):
        for from_page in self.graph_manager.nx_graph.nodes:
            for to_page in self.graph_manager.get_edges(from_page):
                from_inst = self.shadowstep.resolve_page(from_page.__repr__)
                to_inst = self.shadowstep.resolve_page(to_page)
                if from_inst and to_inst:
                    try:
                        self.navigate(from_page=from_inst, to_page=to_inst)
                        assert to_inst.is_current_page()
                        logger.info(f"✅ Переход {from_page.__repr__} → {to_page} прошёл успешно.")
                    except Exception as e:
                        logger.warning(f"❌ Ошибка при переходе {from_page.__repr__} → {to_page}: {e}")


class PageGraph:
    def __init__(self):
        self.graph = {}  # старый способ
        self.nx_graph = nx.DiGraph()  # новый способ (networkx)

    def add_page(self, page, edges):
        self.graph[page] = edges

        # добавим вершину и рёбра в networkx-граф
        self.nx_graph.add_node(page)
        for target_name in edges:
            self.nx_graph.add_edge(page, target_name)

    def get_edges(self, page):
        return self.graph.get(page, [])

    def is_valid_edge(self, from_page, to_page):
        transitions = self.get_edges(from_page)
        return to_page in transitions

    def has_path(self, from_page, to_page) -> bool:
        return nx.has_path(self.nx_graph, from_page, to_page)

    def find_shortest_path(self, from_page, to_page) -> Optional[List[Any]]:
        try:
            return nx.shortest_path(self.nx_graph, source=from_page, target=to_page)
        except nx.NetworkXNoPath:
            return None
        except nx.NodeNotFound:
            return None

    def save_graph_image(self, path: str = "page_graph.png"):
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.nx_graph, seed=42)  # позиционирование узлов

        # Отрисовка
        nx.draw(
            self.nx_graph,
            pos,
            with_labels=True,
            arrows=True,
            node_size=2000,
            node_color="lightblue",
            font_size=10,
            font_weight="bold",
            edge_color="gray",
        )

        plt.title("Shadowstep Page Graph")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
