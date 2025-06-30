#  shadowstep/page_object/page_object_generator.py
import inspect
import json
import keyword
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
from shadowstep.utils.decorators import neuro_allow_edit, neuro_readonly


class PageObjectGenerator:
    """
    Генератор PageObject-классов на основе данных из PageObjectExtractor
    и Jinja2-шаблона.
    """

    def __init__(self, translator=None):
        self.logger = logging.getLogger(__name__)
        self.translator = translator
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
        self.STRUCTURAL_CLASSES = {
            "android.widget.FrameLayout",
            "android.widget.LinearLayout",
            "android.widget.RelativeLayout",
            "android.view.ViewGroup"
        }
        self.CONTAINER_IDS = {
            "android:id/content",
            "com.android.settings:id/app_bar",
            "com.android.settings:id/action_bar",
            "com.android.settings:id/content_frame",
            "com.android.settings:id/main_content",
            "com.android.settings:id/container_material",
            "android:id/widget_frame",
            "android:id/list_container"
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

    @neuro_allow_edit
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
        self.logger.debug(step)
        title = self._get_title_property(ui_element_tree)
        assert title is not None, "Can't find title"
        self.logger.debug(f"{title.attrs=}")

        step = "Формирование name property"
        self.logger.debug(step)
        name = self._get_name_property(title)
        assert name != "", "Name cannot be empty"
        self.logger.debug(f"{name=}")

        step = "Формирование имени класса"
        self.logger.debug(step)
        page_class_name = self._normilize_to_camel_case(name)
        assert page_class_name != "", "page_class_name cannot be empty"
        self.logger.debug(f"{page_class_name=}")

        step = "Формирование recycler property"
        self.logger.debug(step)
        recycler = self._get_recycler_property(ui_element_tree)
        # assert recycler is not None, "Can't find recycler"
        if recycler is None:
            recycler = title
        self.logger.debug(f"{recycler.attrs=}")

        step = "Сбор пар свитчер - якорь"
        self.logger.debug(step)
        switcher_anchor_pairs = self._get_anchor_pairs(ui_element_tree, {"class": "android.widget.Switch"})
        # свитчеры могут быть не найдены, это нормально
        # self.logger.debug(f"{switcher_anchor_pairs=}")
        self.logger.debug(f"{len(switcher_anchor_pairs)=}")

        step = "Сбор summary-свойств"
        self.logger.debug(step)
        summary_anchor_pairs = self._get_summary_pairs(ui_element_tree)
        # summary могут быть не найдены, это нормально
        # self.logger.debug(f"{summary_anchor_pairs=}")
        self.logger.debug(f"{len(summary_anchor_pairs)=}")

        step = "Сбор оставшихся обычных свойств"
        self.logger.debug(step)
        used_elements = switcher_anchor_pairs + summary_anchor_pairs + [(title, recycler)]
        regular_properties = self._get_regular_properties(ui_element_tree, used_elements, recycler)

        step = "Удаление text из локаторов у элементов, которые не ищутся по text в UiAutomator2 (ex. android.widget.SeekBar)"
        self.logger.debug(step)
        self._remove_text_from_non_text_elements(regular_properties)

        step = "Определение необходимости recycler"
        self.logger.debug(step)
        need_recycler = self._is_need_recycler(recycler, regular_properties)
        self.logger.debug(f"{need_recycler=}")

        step = "Подготовка свойств для шаблона"
        self.logger.debug(step)
        properties_for_template = self._transform_properties(
            regular_properties,
            switcher_anchor_pairs,
            summary_anchor_pairs,
            recycler.id if recycler else None
        )

        step = ""
        self.logger.debug(step)
        skip_ids = {title.id, recycler.id}
        properties_for_template = [p for p in properties_for_template if p.get("element_id") not in skip_ids]

        step = "Фильтрация итоговых свойств"
        self.logger.debug(step)

        properties_for_template = self._filter_properties(properties_for_template,
                                                          title.id,
                                                          recycler.id if recycler else None)

        step = "Подготовка данных для рендеринга"
        self.logger.debug(step)
        template_data = self._prepare_template_data(
            ui_element_tree,
            title,
            recycler,
            properties_for_template,
            need_recycler
        )

        step = "Рендеринг"
        self.logger.debug(step)
        template = self.env.get_template('page_object.py.j2')
        rendered = template.render(**template_data)

        step = "Формирование названия файла"
        self.logger.debug(step)
        class_name = template_data["class_name"]
        file_name = self._class_name_to_file_name(class_name)

        step = "Добавление префикса к названию файла, если необходимо"
        self.logger.debug(step)
        if filename_prefix:
            file_name = f"{filename_prefix}{file_name}"

        step = "Запись в файл"
        self.logger.debug(step)
        path = os.path.join(output_dir, file_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(rendered)

        self.logger.debug(f"Generated PageObject → {path}")
        return path, class_name

    @neuro_readonly
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

    @neuro_readonly
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
        if raw_name in keyword.kwlist:
            raw_name = raw_name + '_'
        return raw_name

    @neuro_readonly
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

    @neuro_readonly
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
        # self.logger.debug(f"{targets=}")

        step = "Process each target"
        self.logger.debug(f"[{step}] started")
        for target in targets:
            anchor = self._find_anchor_for_target(target, max_ancestor_distance, target_anchor)
            if anchor:
                anchor_pairs.append((anchor, target))
        # self.logger.debug(f"{anchor_pairs=}")
        return anchor_pairs

    @neuro_readonly
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

    @neuro_readonly
    def _get_ancestor(self, node: UiElementNode, levels_up: int) -> Optional[UiElementNode]:
        current = node
        for _ in range(levels_up + 1):
            if not current.parent:
                return None
            current = current.parent
        return current

    @neuro_readonly
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
        # self.logger.debug(f"{ancestor.id=}, {ancestor.attrs=}")
        # self.logger.debug(f"{target.id=}, {target.attrs=}")
        # self.logger.debug(f"{ancestor.children=}")

        result = []
        # Сначала собираем всех потомков предка
        all_descendants = []
        for child in ancestor.children:
            all_descendants.extend(child.walk())

        # Теперь фильтруем по глубине
        for node in all_descendants:
            # self.logger.debug(f"{node.id=}, {node.attrs=}")
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

    @neuro_readonly
    def _is_same_depth(self, node1: UiElementNode, node2: UiElementNode) -> bool:
        return node1.depth == node2.depth

    @neuro_readonly
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

    @neuro_readonly
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

        self.logger.debug(f"Total summary-anchor pairs found: {len(summary_pairs)}")
        return summary_pairs

    @neuro_readonly
    def _get_regular_properties(
            self,
            ui_element_tree: UiElementNode,
            used_elements: List[Tuple[UiElementNode, UiElementNode]],
            recycler: Optional[UiElementNode] = None
    ) -> List[UiElementNode]:
        """
        Returns all elements that are not part of used_elements, filtering by locator to avoid duplicates.

        Args:
            ui_element_tree (UiElementNode): UI tree root
            used_elements (List[Tuple[UiElementNode, UiElementNode]]): Already used pairs (anchor, target)

        Returns:
            List[UiElementNode]: List of unused, unique-locator elements
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        # 🔁 Сконвертировать used_elements в set of locator hashes
        used_locators: Set[FrozenSet[Tuple[str, str]]] = set()
        for pair in used_elements:
            for node in pair:
                locator = self._node_to_locator(node)
                locator_frozen = frozenset(locator.items())
                used_locators.add(locator_frozen)

        regular_elements = []
        for element in ui_element_tree.walk():
            locator = self._node_to_locator(element)
            if not locator:
                continue

            locator_frozen = frozenset(locator.items())
            if locator_frozen in used_locators:
                continue

            if element.tag == 'androidx.recyclerview.widget.RecyclerView' and recycler.id and element.id != recycler.id:
                self.logger.debug(f"Skipping redundant recycler view: id={recycler.id}")
                continue

            self.logger.debug(f"Regular element accepted: {element.id}, locator={locator}")
            regular_elements.append(element)
            used_locators.add(locator_frozen)

        self.logger.debug(f"Total regular elements found (filtered): {len(regular_elements)}")
        return regular_elements

    @neuro_readonly
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
        if not camel_case.startswith('Page'):
            camel_case = 'Page' + camel_case
        return camel_case

    @neuro_readonly
    def _translate(self, text: str) -> str:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        if self.translator is not None:
            text = self.translator.translate(text)
        return text

    @neuro_readonly
    def _find_by_id(self, root: UiElementNode, target_id: str) -> Optional[UiElementNode]:
        """Поиск узла по id в дереве"""
        for node in root.walk():
            if node.id == target_id:
                return node
        return None

    @neuro_readonly
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

    @neuro_allow_edit
    def _prepare_template_data(self,
                             ui_element_tree: UiElementNode,
                             title: UiElementNode,
                             recycler: Optional[UiElementNode],
                             properties: List[Dict],
                             need_recycler: bool) -> Dict[str, Any]:
        """
        Transforms structured UiElementNode data into a format compatible with the template.

        Args:
            ui_element_tree (UiElementNode): Root UI element tree
            title (UiElementNode): Title node
            recycler (Optional[UiElementNode]): Recycler node if found
            properties (List[Dict]): Prepared properties for template
            need_recycler (bool): Whether recycler is needed

        Returns:
            Dict[str, Any]: Data structure ready for template rendering
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        raw_title = self._get_name_property(title)
        translated = self._translate(raw_title)
        class_name = self._normilize_to_camel_case(translated)

        title_locator = self._node_to_locator(title)
        recycler_locator = self._node_to_locator(recycler) if recycler else None

        return {
            "class_name": class_name,
            "raw_title": raw_title,
            "title_locator": title_locator,
            "properties": properties,
            "need_recycler": need_recycler,
            "recycler_locator": recycler_locator
        }

    @neuro_allow_edit
    def _node_to_locator(self, node: UiElementNode, only_id: bool = False) -> Dict[str, str]:
        """
        Converts UiElementNode to a locator dictionary for template.

        Args:
            node (UiElementNode): Node to convert
            only_id (bool): Whether to return only resource-id

        Returns:
            Dict[str, str]: Locator dictionary
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        if only_id and node.attrs.get('resource-id'):
            return {'resource-id': node.attrs['resource-id']}

        locator = {}
        for attr in ['text', 'content-desc', 'resource-id']:
            if value := node.attrs.get(attr):
                locator[attr] = value

        if node.tag and 'class' not in locator:
            locator['class'] = node.tag

        return locator

    @neuro_allow_edit
    def _transform_properties(
            self,
            regular_properties: List[UiElementNode],
            switcher_anchor_pairs: List[Tuple[UiElementNode, UiElementNode]],
            summary_anchor_pairs: List[Tuple[UiElementNode, UiElementNode]],
            recycler_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Transforms property nodes into template-compatible property dictionaries.

        Args:
            regular_properties (List[UiElementNode]): Regular UI elements
            switcher_anchor_pairs (List[Tuple[UiElementNode, UiElementNode]]): Anchor-switch pairs
            summary_anchor_pairs (List[Tuple[UiElementNode, UiElementNode]]): Anchor-summary pairs
            recycler_id (Optional[str]): ID of recycler element if available

        Returns:
            List[Dict[str, Any]]: Template-ready property dictionaries
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        properties: List[Dict[str, Any]] = []
        used_names: Set[str] = set()
        used_ids: Set[str] = set()

        # 💣 Фильтрация: remove элемент, если он совпадает с recycler
        regular_properties = [
            node for node in regular_properties
            if node.id != recycler_id
        ]

        # Regular properties
        for node in regular_properties:
            if node.id in used_ids:
                continue
            name = self._generate_property_name(node, used_names)
            prop = {
                "type": "regular",
                "name": name,
                "element_id": node.id,
                "locator": self._node_to_locator(node),
                "sibling": False,
                "via_recycler": self._is_scrollable_by(node, recycler_id)
            }
            properties.append(prop)
            used_names.add(name)
            used_ids.add(node.id)
            self.logger.debug(f"Added regular: {name} → {prop['locator']}")

        # Switcher properties
        for anchor, switcher in switcher_anchor_pairs:
            if anchor.id not in used_ids:
                anchor_name = self._generate_property_name(anchor, used_names)
                anchor_prop = {
                    "type": "anchor",
                    "name": anchor_name,
                    "element_id": anchor.id,
                    "locator": self._node_to_locator(anchor),
                    "sibling": False,
                    "via_recycler": self._is_scrollable_by(anchor, recycler_id),
                    "anchor_locator": self._node_to_locator(anchor)
                }
                properties.append(anchor_prop)
                used_names.add(anchor_name)
                used_ids.add(anchor.id)
                self.logger.debug(f"Added anchor: {anchor_name} → {anchor_prop['locator']}")
            else:
                anchor_name = None
                for p in properties:
                    if p.get("element_id") == anchor.id:
                        anchor_name = p.get("name")
                        break
                if anchor_name is None:
                    anchor_name = self._generate_property_name(anchor, used_names)

            if switcher.id in used_ids:
                continue
            name = self._generate_property_name(switcher, used_names, "_switch", anchor_base=anchor_name)
            prop = {
                "type": "switcher",
                "name": name,
                "locator": self._node_to_locator(switcher),
                "sibling": False,
                "via_recycler": self._is_scrollable_by(switcher, recycler_id),
                "anchor_name": anchor_name,
                "depth": self._calculate_depth(anchor, switcher),
                "anchor_locator": self._node_to_locator(anchor)
            }
            properties.append(prop)
            used_names.add(name)
            used_ids.add(switcher.id)
            self.logger.debug(f"Added switcher: {name} (anchor: {anchor_name}) → {prop['locator']}")

        # Summary properties
        for anchor, summary in summary_anchor_pairs:
            if anchor.id not in used_ids:
                base_name = self._generate_property_name(anchor, used_names)
                anchor_prop = {
                    "type": "anchor",
                    "name": base_name,
                    "element_id": anchor.id,
                    "locator": self._node_to_locator(anchor),
                    "sibling": False,
                    "via_recycler": self._is_scrollable_by(anchor, recycler_id),
                    "anchor_locator": self._node_to_locator(anchor)
                }
                properties.append(anchor_prop)
                used_names.add(base_name)
                used_ids.add(anchor.id)
                self.logger.debug(f"Added summary anchor: {base_name} → {anchor_prop['locator']}")
            else:
                base_name = None
                for p in properties:
                    if p.get("element_id") == anchor.id:
                        base_name = p["name"]
                        self.logger.debug(f"[Find base_name] matched property: name={base_name}, id={anchor.id}")
                        break
                if base_name is None:
                    self.logger.debug(f"[Find base_name] no match found, generating new name")
                    base_name = self._generate_property_name(anchor, used_names)
                    self.logger.debug(f"[Find base_name] generated name: {base_name}")

            if summary.id in used_ids:
                continue
            name = self._generate_property_name(summary, used_names, "_summary", anchor_base=base_name)
            prop = {
                "type": "summary",
                "name": name,
                "element_id": anchor.id,
                "locator": self._node_to_locator(anchor),
                "sibling": True,
                "summary_id": self._node_to_locator(summary, only_id=True),
                "base_name": base_name,
                "anchor_locator": self._node_to_locator(anchor)
            }
            properties.append(prop)
            used_names.add(name)
            used_ids.add(summary.id)
            self.logger.debug(f"Added summary: {name} (anchor: {base_name}) → {prop['summary_id']}")

        return properties

    @neuro_allow_edit
    def _is_scrollable_by(self, node: UiElementNode, recycler_id: Optional[str]) -> bool:
        """
        Checks if the node is scrollable by the given recycler.

        Args:
            node (UiElementNode): Node to check
            recycler_id (Optional[str]): ID of potential recycler

        Returns:
            bool: True if node is scrollable by the recycler
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        if not recycler_id or not node.scrollable_parents:
            return False
        return recycler_id in node.scrollable_parents

    @neuro_allow_edit
    def _calculate_depth(self, anchor: UiElementNode, target: UiElementNode) -> int:
        """
        Calculates parent traversal depth between anchor and target.

        Args:
            anchor (UiElementNode): Anchor node
            target (UiElementNode): Target node

        Returns:
            int: Number of parent traversals needed
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        # Find common ancestor
        anchor_ancestors = [anchor]
        current = anchor
        while current.parent:
            anchor_ancestors.append(current.parent)
            current = current.parent

        # Find path from target to first common ancestor
        depth = 0
        current = target
        while current and current not in anchor_ancestors:
            depth += 1
            current = current.parent

        if not current:
            # No common ancestor found, default to 0
            return 0

        # Add distance from anchor to common ancestor
        depth += anchor_ancestors.index(current)

        return depth

    @neuro_allow_edit
    def _generate_property_name(
            self,
            node: UiElementNode,
            used_names: Set[str],
            suffix: str = "",
            anchor_base: Optional[str] = None
    ) -> str:
        """
        Generates a clean, unique property name for a node.

        Args:
            node (UiElementNode): UI node.
            used_names (Set[str]): Already used property names.
            suffix (str): Optional suffix, like '_switch' or '_summary'.
            anchor_base (Optional[str]): Use anchor name as prefix if provided.

        Returns:
            str: Property name.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        base = ""
        # Use anchor name if explicitly passed (e.g., switcher/summary tied to anchor)
        if anchor_base:
            base = anchor_base
        else:
            # Prefer text → content-desc → stripped resource-id
            text = node.attrs.get("text") or node.attrs.get("content-desc") or ""
            if not text and node.attrs.get("resource-id"):
                text = self._strip_package_prefix(node.attrs['resource-id'])
            if self.translator is not None:
                text = self._translate(text)
            words = self._slug_words(text)[:5]
            base = "_".join(words) if words else "element"

        name = self._sanitize_name(f"{base}{suffix}")
        i = 1
        original = name
        while name in used_names:
            name = f"{original}_{i}"
            i += 1
        if name in keyword.kwlist:
            name = name + '_'
        return name

    @neuro_allow_edit
    def _slug_words(self, s: str) -> List[str]:
        """
        Breaks a string into lowercase slug words.

        Args:
            s (str): Input string

        Returns:
            List[str]: List of slug words
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        parts = re.split(r'[^\w]+', unidecode(s))
        return [p.lower() for p in parts if p]

    @neuro_allow_edit
    def _strip_package_prefix(self, resource_id: str) -> str:
        """
        Strips package prefix from resource ID.

        Args:
            resource_id (str): Full resource ID

        Returns:
            str: Resource ID without package prefix
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        return resource_id.split('/', 1)[-1] if '/' in resource_id else resource_id

    @neuro_allow_edit
    def _sanitize_name(self, raw_name: str) -> str:
        """
        Creates a valid Python property name.

        Args:
            raw_name (str): Raw property name

        Returns:
            str: Sanitized property name
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        name = re.sub(r'[^\w]', '_', raw_name)
        if name and name[0].isdigit():
            name = 'num_' + name
        return name

    @neuro_allow_edit
    def _class_name_to_file_name(self, class_name: str) -> str:
        """
        Converts CamelCase class name to snake_case file name.

        Args:
            class_name (str): Class name in CamelCase

        Returns:
            str: File name in snake_case with .py extension
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        step = "Convert CamelCase to snake_case"
        self.logger.debug(f"[{step}] started")
        file_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
        return f"{file_name}.py"

    @neuro_allow_edit
    def _is_need_recycler(self, recycler: Optional[UiElementNode], regular_properties: List[UiElementNode]) -> bool:
        """
        Determines if recycler is needed by checking if any regular properties use it.

        Args:
            recycler (Optional[UiElementNode]): Recycler node if found
            regular_properties (List[UiElementNode]): Regular properties

        Returns:
            bool: Whether recycler is needed
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        if not recycler:
            return False

        recycler_id = recycler.id
        return any(
            node.scrollable_parents and recycler_id in node.scrollable_parents
            for node in regular_properties if node.scrollable_parents
        )

    @neuro_allow_edit
    def _filter_properties(
            self,
            properties: List[Dict[str, Any]],
            title_id: Optional[str],
            recycler_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Filters out redundant properties, but preserves title and recycler.

        Args:
            properties (List[Dict[str, Any]]): Raw property list.
            title_id (Optional[str]): ID of the title node.
            recycler_id (Optional[str]): ID of the recycler node.

        Returns:
            List[Dict[str, Any]]: Cleaned list of properties.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        step = "Filter class-only properties"
        self.logger.debug(f"[{step}] started")
        properties = self._filter_class_only_properties(properties)

        step = "Filter structural containers"
        self.logger.debug(f"[{step}] started")
        properties = self._filter_structural_containers(properties)

        # ⛔ Защита от удаления title и recycler
        step = "Protect title and recycler"
        self.logger.debug(f"[{step}] started")

        def is_important(prop: Dict[str, Any]) -> bool:
            return prop.get("element_id") in {title_id, recycler_id}

        final = []
        for prop in properties:
            if is_important(prop):
                final.append(prop)
                continue
            # Остальная фильтрация (если добавишь еще шаги - вставь сюда)
            final.append(prop)

        self.logger.debug(f"{inspect.currentframe().f_code.co_name} > {final=}")
        return final

    @neuro_readonly
    def _filter_class_only_properties(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Removes properties where the locator contains only 'class' and no other meaningful attributes.

        Args:
            properties (List[Dict[str, Any]]): List of property dictionaries.

        Returns:
            List[Dict[str, Any]]: Filtered property list.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        filtered = []
        for prop in properties:
            locator = prop.get("locator", {})
            if list(locator.keys()) == ["class"]:
                self.logger.debug(f"Removing class-only locator: {prop['name']} ({locator['class']})")
                continue
            filtered.append(prop)

        return filtered

    @neuro_readonly
    def _filter_structural_containers(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Removes non-interactive structural container elements like FrameLayout, LinearLayout, etc.

        Args:
            properties (List[Dict[str, Any]]): List of property dictionaries.

        Returns:
            List[Dict[str, Any]]: Filtered property list.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        filtered = []
        for prop in properties:
            locator = prop.get("locator", {})
            cls = locator.get("class")
            res_id = locator.get("resource-id", "")

            # Class is a known container, and either no id, or id is known to be layout-only
            if cls in self.STRUCTURAL_CLASSES and (not res_id or res_id in self.CONTAINER_IDS):
                self.logger.debug(f"Removing structural container: {prop['name']} ({cls}, {res_id})")
                continue

            filtered.append(prop)

        return filtered


@neuro_readonly
def _pretty_dict(d: dict, base_indent: int = 8) -> str:
    """Форматирует dict в Python-стиле: каждый ключ с новой строки, выровнено по отступу."""
    lines = ["{"]
    indent = " " * base_indent
    for i, (k, v) in enumerate(d.items()):
        line = f"{indent!s}{repr(k)}: {repr(v)}"
        if i < len(d) - 1:
            line += ","
        lines.append(line)
    lines.append(" " * (base_indent - 4) + "}")
    return "\n".join(lines)
