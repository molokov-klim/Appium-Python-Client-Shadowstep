# shadowstep/page_object/page_object_recycler_explorer.py

import importlib.util
import inspect
import logging
import os
import re
from typing import Optional, Dict, Type, Any, Set, Tuple, List

from shadowstep.page_object.page_object_element_node import UiElementNode
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.shadowstep import Shadowstep


class PageObjectRecyclerExplorer:
    """Обнаруживает новые элементы в recycler'е уже сгенерированного PageObject и создаёт расширенный PO."""

    def __init__(self, base: Any, translator):
        """
        Args:
            base (Any): Shadowstep с методами scroll, get_source и т.п.
        """
        self.base: Shadowstep = base
        self.logger = logging.getLogger(__name__)
        self.parser = PageObjectParser()
        self.generator = PageObjectGenerator(translator)

    def explore(self, output_dir: str) -> Optional[tuple[str, str]]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        # скроллим вверх до упора
        width, height = self.base.terminal.get_screen_resolution()
        for _ in range(5):
            self.base.swipe(left=100, top=100,
                            width=width, height=height,
                            direction='down', percent=1.0,
                            speed=10000)  # скроллим вверх

        original_tree = self.parser.parse(self.base.driver.page_source)
        self.logger.info(f"{original_tree=}")
        original_page_path, original_page_class_name = self.generator.generate(original_tree, output_dir=output_dir)

        page_cls = self._load_class_from_file(original_page_path, original_page_class_name)
        if not page_cls:
            self.logger.warning(f"Не удалось загрузить класс {original_page_class_name} из {original_page_path}")
            return None

        page = page_cls()
        if not hasattr(page, "recycler"):
            self.logger.info(f"{original_page_class_name} не содержит свойства `recycler`")
            return None

        recycler_el = page.recycler
        if not hasattr(recycler_el, "scroll_down"):
            self.logger.warning("`recycler` не поддерживает scroll_down")
            return None

        while recycler_el.scroll_down(percent=0.5, speed=100, return_bool=True):
            # дерево изменилось!!! recycler_raw нужно переопределить
            new_tree = self.parser.parse(self.base.driver.page_source)
            new_tree = original_tree + new_tree
            self.logger.info(f"{new_tree=}")
        for _ in range(5):
            self.base.swipe(left=100, top=100,
                            width=width, height=height,
                            direction='up', percent=1.0,
                            speed=10000)  # скроллим вниз
        new_tree = self.parser.parse(self.base.driver.page_source)
        new_tree = original_tree + new_tree
        page_path, page_class_name = self.generator.generate(new_tree, output_dir=output_dir)
        return page_path, page_class_name

    def _load_class_from_file(self, path: str, class_name: str) -> Optional[Type]:
        """Загружает класс по имени из .py-файла."""
        spec = importlib.util.spec_from_file_location("loaded_po", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name, None)
