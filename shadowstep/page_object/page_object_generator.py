#  shadowstep/page_object/page_object_generator.py
import inspect
import json
import logging
import os
import re
from collections import defaultdict
from typing import (
    List, Dict, Union,
    Set, Tuple, Optional, Any, FrozenSet
)

from matplotlib.pyplot import broken_barh
from unidecode import unidecode
from jinja2 import Environment, FileSystemLoader

from shadowstep.page_object.page_object_element_node import UiElementNode
from shadowstep.page_object.page_object_parser import PageObjectParser


class PageObjectGenerator:
    """
    Генератор PageObject-классов на основе данных из PageObjectExtractor
    и Jinja2-шаблона.
    """

    def __init__(self):
        """
        :param parser: объект, реализующий методы
            - extract_simple_elements(xml: str) -> List[Dict[str,str]]
            - find_summary_siblings(xml: str) -> List[Tuple[Dict, Dict]]
        """
        self.logger = logging.getLogger(__name__)
        self.BLACKLIST_NO_TEXT_CLASSES = {
            'android.widget.SeekBar',
            'android.widget.ProgressBar',
            'android.widget.Switch',
            'android.widget.CheckBox',
            'android.widget.ToggleButton',
            'android.view.View',
            'android.widget.ImageView',
            'android.widget.ImageButton',
            'android.widget.RatingBar',
            'androidx.recyclerview.widget.RecyclerView',
            'androidx.viewpager.widget.ViewPager',
        }
        self._anchor_name_map = None

        # Инициализируем Jinja2
        templates_dir = os.path.join(
            os.path.dirname(__file__),
            'templates'
        )
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),  # откуда загружать шаблоны (директория с .j2-файлами)
            autoescape=False,  # отключаем автоэкранирование HTML/JS (не нужно при генерации Python-кода)
            keep_trailing_newline=True,
            # сохраняем завершающий перевод строки в файле (важно для git-diff, PEP8 и т.д.)
            trim_blocks=True,  # удаляет новую строку сразу после {% block %} или {% endif %} (уменьшает пустые строки)
            lstrip_blocks=True
            # удаляет ведущие пробелы перед {% block %} (избавляет от случайных отступов и пустых строк)
        )
        # добавляем фильтр repr
        self.env.filters['pretty_dict'] = _pretty_dict

    def generate(
            self,
            ui_element_tree: UiElementNode,
            output_dir: str,
            filename_prefix: str = ""
    ) -> Tuple[str, str]:
        """
        Docstring in Google style
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        step = "Формирование title property"
        self.logger.info(step)
        title = self._get_title_property(ui_element_tree)
        assert title is not None, "Can't find title"
        self.logger.info(f"{title.attrs=}")

        step = "Формирование name property"
        self.logger.info(step)
        name = self._get_name_property(title)
        assert name != "", "Name cannot be empty"
        self.logger.info(f"{name=}")

        step = "Формирование имени класса"
        self.logger.info(step)
        page_class_name = self._normilize_to_camel_case(name)
        assert page_class_name != "", "page_class_name cannot be empty"
        self.logger.info(f"{page_class_name=}")

        step = "Формирование recycler property"
        self.logger.info(step)
        recycler = self._get_recycler_property(ui_element_tree)
        assert recycler is not None, "Can't find recycler"
        # self.logger.info(f"{recycler.attrs=}")

        step = "Сбор пар свитчер - якорь"
        self.logger.info(step)
        switcher_anchor_pairs = self._get_anchor_pairs(ui_element_tree, {"class": "android.widget.Switch"})
        # свитчеры могут быть не найдены, это нормально
        # self.logger.info(f"{switcher_anchor_pairs=}")
        self.logger.info(f"{len(switcher_anchor_pairs)=}")

        step = "Сбор summary-свойств"
        self.logger.info(step)
        summary_anchor_pairs = self._get_summary_pairs(ui_element_tree)
        # summary могут быть не найдены, это нормально
        # self.logger.info(f"{summary_anchor_pairs=}")
        self.logger.info(f"{len(summary_anchor_pairs)=}")

        step = "Сбор оставшихся обычных свойств"
        self.logger.info(step)
        used_elements = switcher_anchor_pairs + summary_anchor_pairs + [(title, recycler)]
        regular_properties = self._get_regular_properties(ui_element_tree, used_elements)
        self.logger.info(f"{len(regular_properties)=}")

        step = "Удаление text из локаторов у элементов, которые не ищутся по text в UiAutomator2 (ex. android.widget.SeekBar)"
        self.logger.info(step)
        self._remove_text_from_non_text_elements(regular_properties)

        step = "Рендеринг"
        self.logger.info(step)

        step = "Формирование названия файла"
        self.logger.info(step)

        step = "Добавление префикса к названию файла, если необходимо"
        self.logger.info(step)

        # ) запись в файл
        step = "Запись в файл"
        self.logger.info(step)

        return '', ''

    def _get_title_property(self, ui_element_tree: UiElementNode) -> Optional[UiElementNode]:
        """Returns the most likely title node from the tree.

        Args:
            ui_element_tree (UiElementNode): Root node of the parsed UI tree.

        Returns:
            Optional[UiElementNode]: Node with screen title (from text or content-desc).
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        def is_potential_title(ui_node: UiElementNode) -> bool:
            if ui_node.tag not in {'android.widget.TextView', 'android.widget.FrameLayout'}:
                return False
            if not ui_node.attrs.get('displayed', 'false') == 'true':
                return False
            if ui_node.attrs.get('content-desc'):
                return True
            if ui_node.attrs.get('text'):
                return True
            return False

        # Use BFS to prioritize topmost title
        queue = [ui_element_tree]
        while queue:
            ui_node = queue.pop(0)
            if is_potential_title(ui_node):
                content = ui_node.attrs.get("content-desc") or ui_node.attrs.get("text")
                if content and content.strip():
                    self.logger.debug(f"Found title node: {ui_node.id} → {content}")
                    return ui_node
            queue.extend(ui_node.children)

        self.logger.warning("No title node found.")
        return None

    def _get_name_property(self, title: UiElementNode) -> str:
        """Extracts screen name from title node for use as PageObject class name.

        Args:
            title (UiElementNode): UI node considered the screen title.

        Returns:
            str: Name derived from title node.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        raw_name = title.attrs.get("text") or title.attrs.get("content-desc") or ""
        raw_name = raw_name.strip()
        if not raw_name:
            raise ValueError("Title node does not contain usable name")
        return raw_name

    def _get_recycler_property(self, ui_element_tree: UiElementNode) -> Optional[UiElementNode]:
        """Returns the first scrollable parent found in the tree (used as recycler).

        Args:
            ui_element_tree (UiElementNode): Root of parsed UI tree.

        Returns:
            Optional[UiElementNode]: Node marked as scrollable container (recycler).
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        for node in ui_element_tree.walk():
            scrollable_parents = node.scrollable_parents
            if scrollable_parents:
                # берём самый близкий scrollable (первый в списке)
                scrollable_id = scrollable_parents[0]
                self.logger.debug(f"Recycler determined from node={node.id}, scrollable_id={scrollable_id}")
                return self._find_by_id(ui_element_tree, scrollable_id)

        self.logger.warning("No scrollable parent found in any node")
        return None

    def _get_anchor_pairs(
            self,
            ui_element_tree: UiElementNode,
            target_attrs: dict,
            max_ancestor_distance: int = 3,
            target_anchor: Tuple[str, ...] = ("text", "content-desc")
    ) -> List[Tuple[UiElementNode, UiElementNode]]:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        step = "Init anchor-target pair list"
        self.logger.debug(f"[{step}] started")
        anchor_pairs: List[Tuple[UiElementNode, UiElementNode]] = []

        step = "Find matching targets"
        self.logger.debug(f"[{step}] started")
        targets = ui_element_tree.find(**target_attrs)
        if not targets:
            return []
        # self.logger.info(f"{targets=}")

        step = "Process each target"
        self.logger.debug(f"[{step}] started")
        for target in targets:
            anchor = self._find_anchor_for_target(target, max_ancestor_distance, target_anchor)
            if anchor:
                anchor_pairs.append((anchor, target))
        # self.logger.info(f"{anchor_pairs=}")
        return anchor_pairs

    def _find_anchor_for_target(self, target_element: UiElementNode, max_levels: int, target_anchor: Tuple[str, ...] = ("text", "content-desc")) -> Optional[UiElementNode]:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        for level in range(max_levels + 1):
            parent = self._get_ancestor(target_element, level)
            if not parent:
                break
            candidates = self._get_siblings_or_cousins(parent, target_element)
            for candidate in candidates:
                if self._is_anchor_like(candidate, target_anchor):
                    return candidate
        return None

    def _get_ancestor(self, node: UiElementNode, levels_up: int) -> Optional[UiElementNode]:
        current = node
        for _ in range(levels_up + 1):
            if not current.parent:
                return None
            current = current.parent
        return current

    def _get_siblings_or_cousins(self, ancestor: UiElementNode, target: UiElementNode) -> List[UiElementNode]:
        """
        Returns list of sibling or cousin nodes at same depth as target, excluding target itself.

        Args:
            ancestor (UiElementNode): Common ancestor of nodes.
            target (UiElementNode): Node for which to find siblings or cousins.

        Returns:
            List[UiElementNode]: Filtered nodes at same depth.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        step = "Iterating over ancestor.children"
        self.logger.debug(f"[{step}] started")
        # self.logger.info(f"{ancestor.id=}, {ancestor.attrs=}")
        # self.logger.info(f"{target.id=}, {target.attrs=}")
        # self.logger.info(f"{ancestor.children=}")

        result = []
        # Сначала собираем всех потомков предка
        all_descendants = []
        for child in ancestor.children:
            all_descendants.extend(child.walk())

        # Теперь фильтруем по глубине
        for node in all_descendants:
            # self.logger.info(f"{node.id=}, {node.attrs=}")
            if node is target:
                continue

            if node.depth == target.depth:
                self.logger.debug(
                    f"Sibling/cousin candidate: id={node.id}, class={node.tag}, text={node.attrs.get('text')}, content-desc={node.attrs.get('content-desc')}")
                result.append(node)
            else:
                self.logger.debug(f"Rejected (wrong depth): id={node.id}, depth={node.depth} ≠ {target.depth}")

        self.logger.debug(f"Total candidates found: {len(result)}")
        return result

    def _is_same_depth(self, node1: UiElementNode, node2: UiElementNode) -> bool:
        return node1.depth == node2.depth

    def _is_anchor_like(self, node: UiElementNode, target_anchor: Tuple[str, ...] = ("text", "content-desc")) -> bool:
        """
        Checks if the node has any of the specified attributes used to identify anchor elements.

        Args:
            node (UiElementNode): Node to check.
            target_anchor (Tuple[str, ...]): Attributes that may indicate anchor-like quality.

        Returns:
            bool: True if node has any non-empty anchor attribute.
        """
        # Ensure at least one anchor attribute is present and non-empty
        return any(node.attrs.get(attr) for attr in target_anchor)

    def _get_summary_pairs(self, ui_element_tree: UiElementNode) -> List[Tuple[UiElementNode, UiElementNode]]:
        """
        Находит пары элементов anchor-summary.
        
        Args:
            ui_element_tree (UiElementNode): Дерево элементов UI
            
        Returns:
            List[Tuple[UiElementNode, UiElementNode]]: Список пар (anchor, summary)
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        
        # Находим все элементы, у которых в атрибутах есть "summary"
        summary_elements = []
        for element in ui_element_tree.walk():
            if any(re.search(r'\bsummary\b', str(value).lower()) for value in element.attrs.values()):
                summary_elements.append(element)
                self.logger.debug(f"Found summary element: {element.id}, attrs={element.attrs}")
        
        # Для каждого summary элемента ищем соответствующий anchor
        summary_pairs = []
        for summary in summary_elements:
            # Ищем ближайший anchor для summary элемента
            anchor = self._find_anchor_for_target(summary, max_levels=3, target_anchor=("text", "content-desc"))
            if anchor and not any("summary" in str(value).lower() for value in anchor.attrs.values()):
                self.logger.debug(f"Found anchor for summary {summary.id}: {anchor.id}, attrs={anchor.attrs}")
                summary_pairs.append((anchor, summary))
            else:
                self.logger.warning(f"No anchor found for summary element {summary.id}")
        
        self.logger.info(f"Total summary-anchor pairs found: {len(summary_pairs)}")
        return summary_pairs

    def _get_regular_properties(self, ui_element_tree: UiElementNode, used_elements: List[Tuple[UiElementNode, UiElementNode]]) -> List[UiElementNode]:
        """
        Находит все элементы, которые не входят в used_elements.
        
        Args:
            ui_element_tree (UiElementNode): Дерево элементов UI
            used_elements (List[Tuple[UiElementNode, UiElementNode]]): Список пар элементов, которые уже использованы
            
        Returns:
            List[UiElementNode]: Список неиспользованных элементов
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        
        # Создаем множество id использованных элементов для быстрого поиска
        used_node_ids = set()
        for pair in used_elements:
            used_node_ids.add(id(pair[0]))  # anchor
            used_node_ids.add(id(pair[1]))  # target/summary/recycler
        
        # Находим все элементы, которые не входят в used_nodes
        regular_elements = []
        for element in ui_element_tree.walk():
            if id(element) not in used_node_ids:
                regular_elements.append(element)
                self.logger.debug(f"Found regular element: {element.id}, attrs={element.attrs}")
        
        self.logger.info(f"Total regular elements found: {len(regular_elements)}")
        return regular_elements

    def _normilize_to_camel_case(self, text: str) -> str:
        """
        будет применяться для формирования имени класса из name
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        # sanitize → remove spaces, symbols, make CamelCase
        normalized = self._translate(text)  # переводим на английский
        normalized = re.sub(r"[^\w\s]", "", normalized)  # удаляем спецсимволы
        camel_case = "".join(word.capitalize() for word in normalized.split())

        if not camel_case:
            raise ValueError(f"Failed to normalize screen name from '{text}'")
        return camel_case

    def _translate(self, text: str) -> str:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        # здесь будет код перевода текста через какой-нибудь API (например гугловский, если у них такой есть)
        # метод должен сам понять какой язык (можно через API какой-нибудь, например например гугловский, если у них такой есть)
        """
        if self.is_russian \ source = self.what_language
        https://libretranslate.de/translate
        {
          "q": "Привет, мир",
          "source": "ru",
          "target": "en",
          "format": "text"
        }
        """
        return text

    def _find_by_id(self, root: UiElementNode, target_id: str) -> Optional[UiElementNode]:
        """Поиск узла по id в дереве"""
        for node in root.walk():
            if node.id == target_id:
                return node
        return None

    def _remove_text_from_non_text_elements(self, elements: List[UiElementNode]) -> None:
        """
        Удаляет атрибут text из локаторов элементов, которые не должны искаться по тексту.
        
        Args:
            elements (List[UiElementNode]): Список элементов для обработки
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        
        for element in elements:
            if element.tag in self.BLACKLIST_NO_TEXT_CLASSES and 'text' in element.attrs:
                self.logger.debug(f"Removing text attribute from {element.tag} element: {element.attrs.get('text')}")
                del element.attrs['text']


def _pretty_dict(d: dict, base_indent: int = 8) -> str:
    """Форматирует dict в Python-стиле: каждый ключ с новой строки, выровнано по отступу."""
    lines = ["{"]
    indent = " " * base_indent
    for i, (k, v) in enumerate(d.items()):
        line = f"{indent!s}{repr(k)}: {repr(v)}"
        if i < len(d) - 1:
            line += ","
        lines.append(line)
    lines.append(" " * (base_indent - 4) + "}")
    return "\n".join(lines)
