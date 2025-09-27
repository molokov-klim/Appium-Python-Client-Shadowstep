"""Page object recycler explorer for Shadowstep framework.

This module provides the PageObjectRecyclerExplorer class for
automatically exploring scrollable content in mobile applications
by generating page objects for different scroll positions and
merging them into a comprehensive page object.
"""

# shadowstep/page_object/page_object_recycler_explorer.py
from __future__ import annotations

import importlib.util
import logging
from typing import cast

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepTerminalNotInitializedError
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_merger import PageObjectMerger
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.shadowstep import Shadowstep
from shadowstep.utils.utils import get_current_func_name


class PageObjectRecyclerExplorer:
    """Explorer for scrollable content in mobile applications.

    This class provides functionality to automatically explore scrollable
    content by generating page objects for different scroll positions
    and merging them into a comprehensive page object.
    """

    def __init__(self, base: Shadowstep, translator: YandexTranslate | None) -> None:
        """Initialize the PageObjectRecyclerExplorer.

        Args:
            base: Shadowstep instance for automation operations.
            translator: Translator instance for text translation.

        """
        self.base: Shadowstep = base
        self.logger = logging.getLogger(__name__)
        self.parser = PageObjectParser()
        self.generator = PageObjectGenerator(translator)
        self.merger = PageObjectMerger()

    def explore(self, output_dir: str) -> str:
        """Explore recycler views and generate page objects.

        Args:
            output_dir: Directory to save generated page objects.

        Returns:
            str: Path to the generated file.

        Raises:
            ValueError: If terminal is not initialized.

        """
        self.logger.info("%s", get_current_func_name())
        if self.base.terminal is None:  # type: ignore[comparison-overlap]
            raise ShadowstepTerminalNotInitializedError
        width, height = self.base.terminal.get_screen_resolution()
        x = width // 2
        y_start = int(height * 0.2)
        y_end = int(height * 0.8)
        for _ in range(9):
            self.base.swipe(left=100, top=100,
                            width=width, height=height,
                            direction="down", percent=1.0,
                            speed=10000)  # scroll up
            self.base.terminal.adb_shell(
                command="input",
                args=f"swipe {x} {y_start} {x} {y_end}",
            )

        pages = []
        original_tree = self.parser.parse(self.base.driver.page_source)
        original_page_path, original_page_class_name = self.generator.generate(original_tree, output_dir=output_dir)
        pages.append((original_page_path, original_page_class_name))

        original_cls = self._load_class_from_file(original_page_path, original_page_class_name)
        if not original_cls:
            self.logger.warning("Failed to load class %s from %s", original_page_class_name, original_page_path)
            return ""

        original_page = original_cls()
        if not hasattr(original_page, "recycler"):
            self.logger.info("%s does not contain `recycler` property", original_page_class_name)
            return ""

        recycler_el = original_page.recycler
        if not hasattr(recycler_el, "scroll_down"):
            self.logger.warning("`recycler` does not support scroll_down")
            return ""
        prefix = 0

        while recycler_el.scroll_down(percent=0.5, speed=1000, return_bool=True):
            # tree changed!!! recycler_raw needs to be redefined
            prefix += 1
            tree = self.parser.parse(self.base.driver.page_source)
            page_path, page_class_name = self.generator.generate(tree, output_dir=output_dir,
                                                                 filename_prefix=str(prefix))
            pages.append((page_path, page_class_name))

        width, height = self.base.terminal.get_screen_resolution()
        x = width // 2
        y_start = int(height * 0.8)
        y_end = int(height * 0.2)
        for _ in range(9):
            self.base.swipe(left=100, top=100,
                            width=width, height=height,
                            direction="up", percent=1.0,
                            speed=10000)  # scroll up
            self.base.terminal.adb_shell(
                command="input",
                args=f"swipe {x} {y_start} {x} {y_end}",
            )
        prefix += 1
        tree = self.parser.parse(self.base.driver.page_source)
        page_path, page_class_name = self.generator.generate(tree, output_dir=output_dir, filename_prefix=str(prefix))
        pages.append((page_path, page_class_name))

        output_path = "merged" + original_page_path
        self.merger.merge(original_page_path, cast("str", pages[0][0]), output_path)

        for page_tuple in pages:
            page_path, page_class_name = page_tuple
            self.merger.merge(output_path, cast("str", page_path), output_path)

        for _ in range(5):
            self.base.swipe(left=100, top=100,
                            width=width, height=height,
                            direction="up", percent=1.0,
                            speed=10000)  # scroll down

        return output_path

    def _load_class_from_file(self, path: str, class_name: str) -> type | None:
        spec = importlib.util.spec_from_file_location("loaded_po", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name, None)
