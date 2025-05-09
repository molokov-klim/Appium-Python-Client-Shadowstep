# shadowstep/page_object/page_object_recycler_explorer.py

import importlib.util
import inspect
import logging
import os
import re
from typing import Optional, Dict, Type, Any, Set, Tuple, List

from shadowstep.page_object.page_object_extractor import PageObjectExtractor
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.shadowstep import Shadowstep


class PageObjectRecyclerExplorer:
    """Обнаруживает новые элементы в recycler'е уже сгенерированного PageObject и создаёт расширенный PO."""

    def __init__(self, base: Any):
        """
        Args:
            base (Any): Shadowstep с методами scroll, get_source и т.п.
        """
        self.base: Shadowstep = base
        self.logger = logging.getLogger(__name__)
        self.extractor = PageObjectExtractor()
        self.generator = PageObjectGenerator(self.extractor)

    def explore(self, input_path: str, class_name: str, output_path: str) -> Optional[tuple[str, str]]:
        """
        Загружает PageObject, проверяет наличие recycler, скроллит его, извлекает новые элементы
        и генерирует расширенный PageObject с новыми свойствами.

        Args:
            input_path (str): Путь до оригинального PageObject-файла.
            class_name (str): Имя класса PageObject.
            output_path (str): Куда сохранить расширенный PageObject.

        Returns:
            Optional[Dict[str, str]]: {'path': ..., 'class_name': ...} если есть новые элементы, иначе None.
        """
        page_cls = self._load_class_from_file(input_path, class_name)
        if not page_cls:
            self.logger.warning(f"Не удалось загрузить класс {class_name} из {input_path}")
            return None

        page = page_cls()
        if not hasattr(page, "recycler"):
            self.logger.info(f"{class_name} не содержит свойства `recycler`")
            return None

        recycler_el = page.recycler
        if not hasattr(recycler_el, "scroll_down"):
            self.logger.warning("`recycler` не поддерживает scroll_down")
            return None

        # Сбор уже существующих имён свойств
        properties = self._collect_recycler_properties(page)

        xml = self.base.driver.page_source
        elements = self.extractor.parse(xml)

        raw_recycler = None
        for el in elements:
            self.logger.debug(f"{el=}")
            if all(el.get(k) == v for k, v in recycler_el.locator.items()):
                raw_recycler = el

        pack_properties = []
        for name, locator in properties:
            raw_el = self._match_raw_element(locator, elements)
            pack_properties.append((name, locator, raw_el))

        pack_recycler = ("recycler", recycler_el.locator, raw_recycler)

        self.logger.debug(f"============================")
        self.logger.debug(f"{pack_recycler=}")
        self.logger.debug(f"{pack_properties=}")
        self.logger.debug(f"============================")

        #
        # for _ in range(20):
        #     xml = self.base.driver.page_source
        #     elements = self.extractor.parse(xml)
        #
        #     for el in elements:
        #         if not el.get("scrollable_parents"):
        #             continue
        #         if el["scrollable_parents"][0] != recycler_el.locator.get("resource-id"):
        #             continue
        #
        #         key = (el.get("resource-id"), el.get("text"), el.get("content-desc"))
        #         if key in seen_keys:
        #             continue
        #         seen_keys.add(key)
        #
        #         raw = el.get("resource-id") or el.get("text") or el.get("content-desc")
        #         if not raw:
        #             continue
        #         name_base = re.sub(r"[^\w]+", "_", raw).lower()
        #         if name_base in existing_names:
        #             continue
        #
        #         new_elements.append(el)
        #
        #     if not recycler_el.scroll_down():
        #         break

        # if not new_elements:
        #     self.logger.info("Новых элементов в recycler не найдено")
        #     return None
        #
        # # Используем PageObjectGenerator как есть — просто даём XML и output_dir
        # result = self.generator.generate(
        #     source_xml=self.base.driver.page_source,
        #     output_dir=os.path.dirname(output_path),
        # )
        # return result
        return ()

    def _load_class_from_file(self, path: str, class_name: str) -> Optional[Type]:
        """Загружает класс по имени из .py-файла."""
        spec = importlib.util.spec_from_file_location("loaded_po", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name, None)

    def _collect_recycler_properties(self, page: Any) -> List[Tuple[str, Dict[str, Any]]]:
        """Возвращает (имя, локатор) для всех @property, использующих _recycler_get(...)."""
        result = []
        for name in dir(page):
            attr = getattr(type(page), name, None)
            if not isinstance(attr, property):
                continue
            try:
                value = getattr(page, name)
                if hasattr(value, "locator") and isinstance(value.locator, dict):
                    result.append((name, value.locator))
            except Exception:
                self.logger.warning(f"Не удалось извлечь локатор у свойства {name}")
                continue
        return result

    def _match_raw_element(self, locator: Dict[str, Any], elements: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Находит первый элемент из XML, совпадающий с заданным локатором."""
        for el in elements:
            if all(el.get(k) == v for k, v in locator.items()):
                return el
        return None

