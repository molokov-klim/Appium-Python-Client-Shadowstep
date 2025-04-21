# coding: utf-8
from collections import deque
from typing import Any, Optional, List, Union
from loguru import logger

from selenium.common import WebDriverException


class PageNavigator:
    def __init__(self, shadowstep: "ShadowstepBase"):
        self.shadowstep = shadowstep
        self.graph_manager = PageGraph()
        self.logger = logger

    def add_page(self, page, edges):
        self.graph_manager.add_page(page=page, edges=edges)

    def navigate(self, from_page: Any, to_page: Any, timeout: int = 55) -> bool:
        if from_page == to_page:
            return True
        path = self.find_path(from_page, to_page)
        if not path:
            raise ValueError(f"No path found from {from_page} to {to_page}")
        try:
            self.perform_navigation(path, timeout)
            return True
        except WebDriverException as error:
            self.logger.error(error)
            return False

    def find_path(self, start: Union[str, "PageBase"], target: Union[str, "PageBase"]) -> Optional[List["PageBase"]]:
        if isinstance(start, str):
            start = self.shadowstep.resolve_page(start)
        if isinstance(target, str):
            target = self.shadowstep.resolve_page(target)
        visited = set()
        queue = deque([(start, [])])
        while queue:
            current_page, path = queue.popleft()
            visited.add(current_page)
            transitions = self.graph_manager.get_edges(page=current_page)
            for next_page_name in transitions:
                next_page = self.shadowstep.resolve_page(next_page_name)
                if next_page == target:
                    return path + [current_page, next_page]
                if next_page not in visited:
                    queue.append((next_page, path + [current_page]))
        return None

    def perform_navigation(self, path: List["PageBase"], timeout: int = 55) -> None:
        for i in range(len(path) - 1):
            current_page = path[i]
            next_page = path[i + 1]
            transition_method = current_page.edges[next_page.__class__.__name__]
            transition_method()


class PageGraph:
    def __init__(self):
        self.graph = {}

    def add_page(self, page, edges):
        self.graph[page] = edges

    def get_edges(self, page):
        return self.graph.get(page, [])

    def is_valid_edge(self, from_page, to_page):
        transitions = self.get_edges(from_page)
        return to_page in transitions

