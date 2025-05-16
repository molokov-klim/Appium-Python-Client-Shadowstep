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
from shadowstep.utils.decorators import neuro_allow_edit, neuro_readonly


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
        # TODO
        """
        TODO
        4. 🪤 _get_regular_properties() — без фильтрации
        Проблема:
        Регулярные элементы добавляются даже если дублируют свитчеры или summary (с другим именем). Потому что ты сравниваешь по id(), а не по locator.
        
        Что нужно:
        Хранить used_locators = set(frozenset(locator.items()) for locator in ...)
        И фильтровать по ним — не пускать дубликаты локаторов с разными именами.
        """
        regular_properties = self._get_regular_properties(ui_element_tree, used_elements)
        self.logger.info(f"{len(regular_properties)=}")

        step = "Удаление text из локаторов у элементов, которые не ищутся по text в UiAutomator2 (ex. android.widget.SeekBar)"
        self.logger.info(step)
        self._remove_text_from_non_text_elements(regular_properties)

        step = "Определение необходимости recycler"
        self.logger.info(step)
        need_recycler = self._is_need_recycler(recycler, regular_properties)
        self.logger.info(f"{need_recycler=}")

        step = "Подготовка свойств для шаблона"
        # TODO _transform_properties просто сваливает в одну кучу и нивелирует switcher_anchor_pairs и summary_anchor_pairs
        # TODO нужно это исправить
        self.logger.info(step)
        properties_for_template = self._transform_properties(
            regular_properties,
            switcher_anchor_pairs,
            summary_anchor_pairs,
            recycler.id if recycler else None
        )

        step = ""
        self.logger.info(step)
        skip_ids = {title.id, recycler.id}
        properties_for_template = [p for p in properties_for_template if p.get("element_id") not in skip_ids]

        # TODO _filter_properties должен ещё фильтровать
        """
        TODO 
        _filter_properties должен ещё фильтровать бесполезные элементы типа (когда recycler уже определен)
        и наверное title тоже не должен дублироваться (вроде не дублируется, но на всякий случай проверь)
         @property
        def recycler_view_recyclerview(self) -> Element:
            return self.recycler.scroll_to_element({
                'resource-id': 'com.android.settings:id/recycler_view',
                'class': 'androidx.recyclerview.widget.RecyclerView'
            })
        """
        step = ""
        self.logger.info(step)
        # properties_for_template = self._filter_properties(properties_for_template, title, recycler)
        # TODO надо properties_for_template = self._filter_properties(properties_for_template, title, recycler, switcher_pairs, sibling_pairs)
        self.logger.info(f"{properties_for_template=}")

        # TODO _prepare_template_data должен принимать switcher_anchor_pairs и summary_anchor_pairs
        step = "Подготовка данных для рендеринга"
        self.logger.info(step)
        template_data = self._prepare_template_data(
            ui_element_tree,
            title,
            recycler,
            properties_for_template,
            need_recycler
        )

        step = "Рендеринг"
        self.logger.info(step)
        template = self.env.get_template('page_object.py.j2')
        rendered = template.render(**template_data)

        step = "Формирование названия файла"
        self.logger.info(step)
        class_name = template_data["class_name"]
        file_name = self._class_name_to_file_name(class_name)

        step = "Добавление префикса к названию файла, если необходимо"
        self.logger.info(step)
        if filename_prefix:
            file_name = f"{filename_prefix}{file_name}"

        step = "Запись в файл"
        self.logger.info(step)
        path = os.path.join(output_dir, file_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(rendered)
            
        self.logger.info(f"Generated PageObject → {path}")
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
        # self.logger.info(f"{targets=}")

        step = "Process each target"
        self.logger.debug(f"[{step}] started")
        for target in targets:
            anchor = self._find_anchor_for_target(target, max_ancestor_distance, target_anchor)
            if anchor:
                anchor_pairs.append((anchor, target))
        # self.logger.info(f"{anchor_pairs=}")
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
        
        self.logger.info(f"Total summary-anchor pairs found: {len(summary_pairs)}")
        return summary_pairs

    @neuro_readonly
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
        return camel_case

    @neuro_readonly
    def _translate(self, text: str) -> str:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        """
        пока не нашёл бесплатный переводчик
        """
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
        class_name = unidecode((self._normilize_to_camel_case(raw_title)))
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
    def _transform_properties(self,
                            regular_properties: List[UiElementNode],
                            switcher_anchor_pairs: List[Tuple[UiElementNode, UiElementNode]],
                            summary_anchor_pairs: List[Tuple[UiElementNode, UiElementNode]],
                            recycler_id: Optional[str]) -> List[Dict]:
        """
        Transforms property nodes into template-compatible property dictionaries.
        
        Args:
            regular_properties (List[UiElementNode]): Regular UI elements
            switcher_anchor_pairs (List[Tuple[UiElementNode, UiElementNode]]): Anchor-switch pairs
            summary_anchor_pairs (List[Tuple[UiElementNode, UiElementNode]]): Anchor-summary pairs
            recycler_id (Optional[str]): ID of recycler element if available
            
        Returns:
            List[Dict]: Template-ready property dictionaries
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        properties = []
        used_names = set()

        # 1. Regular properties
        for node in regular_properties:
            prop = {
                "name": self._generate_property_name(node, used_names),
                "element_id": node.id,
                "locator": self._node_to_locator(node),
                "sibling": False,
                "via_recycler": self._is_scrollable_by(node, recycler_id)
            }
            properties.append(prop)
            used_names.add(prop["name"])

        # 2. Switcher properties
        for anchor, switcher in switcher_anchor_pairs:
            anchor_name = next((p["name"] for p in properties if p.get("element_id") == anchor.id), None)
            if not anchor_name:
                # Если якорь не найден среди обычных свойств, генерируем его
                anchor_name = self._generate_property_name(anchor, used_names, "_anchor")
                used_names.add(anchor_name)
                anchor_prop = {
                    "name": anchor_name,
                    "element_id": anchor.id,
                    "locator": self._node_to_locator(anchor),
                    "sibling": False,
                    "via_recycler": self._is_scrollable_by(anchor, recycler_id)
                }
                properties.append(anchor_prop)

            depth = self._calculate_depth(anchor, switcher)
            name = self._generate_property_name(switcher, used_names, "_switch")

            prop = {
                "name": name,
                "locator": self._node_to_locator(switcher),
                "sibling": False,
                "via_recycler": self._is_scrollable_by(switcher, recycler_id),
                "anchor_name": anchor_name,
                "depth": depth
            }
            properties.append(prop)
            used_names.add(name)

        # 3. Summary properties
        for anchor, summary in summary_anchor_pairs:
            base_name = self._generate_property_name(anchor, used_names)
            if base_name in used_names:
                base_name = f"{base_name}_base"
                used_names.add(base_name)

            name = self._generate_property_name(summary, used_names, "_summary")

            prop = {
                "name": name,
                "locator": self._node_to_locator(anchor),
                "sibling": True,
                "summary_id": self._node_to_locator(summary, only_id=True),
                "base_name": base_name
            }
            properties.append(prop)
            used_names.add(name)

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
    def _generate_property_name(self,
                               node: UiElementNode,
                               used_names: Set[str],
                               suffix: str = "") -> str:
        """
        Generates a unique property name for a node.
        
        Args:
            node (UiElementNode): Node to name
            used_names (Set[str]): Set of already used names
            suffix (str): Optional suffix to add to name
            
        Returns:
            str: Generated unique property name
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        text = node.attrs.get('text') or node.attrs.get('content-desc') or ""
        if not text and node.attrs.get('resource-id'):
            text = self._strip_package_prefix(node.attrs['resource-id'])

        # Slug words and limit to first 5
        words = self._slug_words(text)[:5] if text else []
        base = "_".join(words) if words else "element"
        
        # Add class suffix
        class_suffix = node.tag.split('.')[-1].lower() if node.tag else "element"
        name = self._sanitize_name(f"{base}_{class_suffix}{suffix}")

        # Ensure uniqueness
        i = 1
        orig_name = name
        while name in used_names:
            name = f"{orig_name}_{i}"
            i += 1

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
        return f"page_{file_name}.py"

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

    @neuro_readonly
    def _filter_properties(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Applies a sequence of filtering steps to exclude non-useful properties.

        Args:
            properties (List[Dict[str, Any]]): List of property dictionaries.

        Returns:
            List[Dict[str, Any]]: Filtered property list.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        step = "Filter class-only properties"
        self.logger.debug(f"[{step}] started")
        properties = self._filter_class_only_properties(properties)

        step = "Filter structural container properties"
        self.logger.debug(f"[{step}] started")
        properties = self._filter_structural_containers(properties)

        return properties

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
