"""Navigation module for managing page transitions in Shadowstep framework.

This module provides functionality for navigating between pages using graph-based
pathfinding algorithms. It supports both NetworkX-based shortest path finding
and fallback BFS traversal.
"""

from __future__ import annotations

import importlib
import inspect
import logging
import os
import site
import sys
import time
import traceback
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from networkx.exception import NetworkXException
from page_graph import PageGraph
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
from shadowstep.utils.utils import get_current_func_name

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
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

    pages: ClassVar[dict[str, type[PageBaseShadowstep]]] = {}
    _pages_discovered: bool = False

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
        self._ignored_auto_discover_dirs: set[str] = {
            "__pycache__",
            ".venv",
            "venv",
            "site-packages",
            "dist-packages",
            ".git",
            "build",
            "dist",
            ".idea",
            ".pytest_cache",
            "results",
        }
        self._ignored_base_path_parts: set[str] = self._get_ignored_dirs()

    def get_page(self, name: str) -> PageBaseShadowstep:
        """Get a page instance by name.

        Args:
            name: The name of the page to retrieve.

        Returns:
            PageBaseShadowstep: An instance of the requested page.

        Raises:
            ValueError: If the page is not found in registered pages.

        """
        cls = self.pages.get(name)
        if not cls:
            msg = f"Page '{name}' not found in registered pages."
            raise ValueError(msg)
        return cls()

    def resolve_page(self, name: str) -> PageBaseShadowstep:
        """Resolve a page instance by name.

        Args:
            name: The name of the page to resolve.

        Returns:
            PageBaseShadowstep: An instance of the requested page.

        Raises:
            ValueError: If the page is not found.

        """
        cls = self.pages.get(name)
        if cls:
            return cls()
        msg = f"Page '{name}' not found."
        raise ValueError(msg)

    def auto_discover_pages(self) -> None:
        """Automatically import and register all PageBase subclasses from all 'pages' directories in sys.path."""
        self.logger.debug("📂 %s: %s", get_current_func_name(), list(set(sys.path)))
        if self._pages_discovered:
            return
        self._pages_discovered = True
        for base_path in map(Path, list(set(sys.path))):
            base_str = base_path.name.lower()
            if base_str in self._ignored_base_path_parts:
                continue
            if not base_path.exists() or not base_path.is_dir():
                continue
            for dirpath, dirs, filenames in os.walk(base_path):
                dir_name = Path(dirpath).name
                # ❌ remove inner folders
                dirs[:] = [d for d in dirs if d not in self._ignored_auto_discover_dirs]
                if dir_name in self._ignored_auto_discover_dirs:
                    continue
                for file in filenames:
                    if file.startswith("page") and file.endswith(".py"):
                        try:
                            file_path = Path(dirpath) / file
                            rel_path = file_path.relative_to(base_path).with_suffix("")
                            module_name = ".".join(rel_path.parts)
                            module = importlib.import_module(module_name)
                            self._register_pages_from_module(module)
                        except Exception as e:  # noqa: BLE001
                            self.logger.warning("⚠️ Import error %s: %s", file, e)

    def _register_pages_from_module(self, module: Any) -> None:
        try:
            members = inspect.getmembers(module)
            for name, obj in members:
                if not inspect.isclass(obj):
                    continue
                if not issubclass(obj, PageBaseShadowstep):
                    continue
                if obj is PageBaseShadowstep:
                    continue
                if not name.startswith("Page"):
                    continue
                self.pages[name] = obj
                page_instance = obj()
                edges = page_instance.edges
                edge_names = list(edges.keys())
                self.logger.info("✅ register page: %s with edges %s", page_instance, edge_names)
                self.add_page(page_instance, edges)
        except Exception:
            self.logger.exception("❌ Error page register from module %s", module.__name__)

    def list_registered_pages(self) -> None:
        """Log all registered page classes."""
        self.logger.info("=== Registered Pages ===")
        for name, cls in self.pages.items():
            self.logger.info("%s: %s.%s", name, cls.__module__, cls.__name__)

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

    def navigate(
            self,
            from_page: Any,
            to_page: Any,
            timeout: int = DEFAULT_NAVIGATION_TIMEOUT,
    ) -> bool:
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
            "🚀 Navigating: %s ➡ %s via path: %s",
            from_page,
            to_page,
            [repr(page) for page in path],
        )

        try:
            self.perform_navigation(path, timeout)
            self.logger.info("✅ Successfully navigated to %s", to_page)
        except WebDriverException:
            self.logger.exception(
                "❗ WebDriverException during dom from %s to %s",
                from_page,
                to_page,
            )
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

    def perform_navigation(
            self,
            path: list[str],
            timeout: int = DEFAULT_NAVIGATION_TIMEOUT,
    ) -> None:
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

    def _get_ignored_dirs(self) -> set[str]:
        logger.debug(get_current_func_name())

        # Base paths that we consider "system"
        system_base = Path(sys.base_prefix).resolve()
        site_packages = {Path(p).resolve() for p in site.getsitepackages() if Path(p).exists()}
        stdlib = system_base / "lib"

        def is_system_path(path: Path) -> bool:
            try:
                path = path.resolve()
            except Exception:  # noqa: BLE001
                return False
            return (
                    str(path).startswith(str(system_base))  # inside python installation / venv
                    or any(str(path).startswith(str(s)) for s in site_packages)  # site-packages
                    or str(path).startswith(str(stdlib))  # stdlib
            )

        system_paths = {Path(p).resolve().name for p in sys.path if p and is_system_path(Path(p))}
        ignored_names = {
            "venv",
            ".venv",
            "env",
            ".env",
            "Scripts",
            "bin",
            "lib",
            "include",
            "__pycache__",
            ".idea",
            ".vscode",
            "build",
            "dist",
            "dlls",
        }
        return system_paths.union(ignored_names)
