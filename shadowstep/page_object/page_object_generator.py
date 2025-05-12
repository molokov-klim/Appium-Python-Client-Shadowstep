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

from shadowstep.page_object.page_object_extractor import PageObjectParser


class PageObjectGenerator:
    """
    Генератор PageObject-классов на основе данных из PageObjectExtractor
    и Jinja2-шаблона.
    """

    def __init__(self, extractor: PageObjectParser):
        """
        :param extractor: объект, реализующий методы
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
        self.extractor = extractor

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
            source_xml: str,
            output_dir: str,
            filename_postfix: str = "",
            max_name_words: int = 5,
            attributes: Optional[
                Union[Set[str], Tuple[str], List[str]]
            ] = None,
            additional_elements: list = None
    ) -> Tuple[str, str]:
        # 1) Выбор атрибутов для локаторов
        self.logger.info(f"1) Выбор атрибутов для локаторов")
        attr_list, include_class = self._prepare_attributes(attributes)

        # 2) извлечение и элементов
        self.logger.info(f"2) извлечение и элементов")
        elems = self.extractor.parse(source_xml)
        if additional_elements:
            elems += additional_elements
        # self.logger.debug(f"{elems=}")

        # 2.1) выбор основного скроллера
        self.logger.info(f"2.1) выбор основного скроллера")
        recycler_id = self._select_main_recycler(elems)
        recycler_el = next((e for e in elems if e['id'] == recycler_id), None)

        # 2.2) формирование пар summary
        self.logger.info(f"2.2) формирование пар summary")
        summary_pairs = self._find_summary_siblings(elems)
        self.logger.info(f"{summary_pairs=}")

        # 3) заголовок страницы
        self.logger.info(f"3) заголовок страницы")
        title_el = self._select_title_element(elems)
        raw_title = self._raw_title(title_el)

        # 4) PageClassName + file_name.py
        self.logger.info(f"4) PageClassName + file_name.py")
        class_name, file_name = self._format_names(raw_title)

        # 5) собираем все свойства
        self.logger.info(f"5) собираем все свойства")
        used_names: Set[str] = {'title'}
        title_locator = self._build_locator(
            title_el, attr_list, include_class
        )
        properties: List[Dict] = []

        # 5.1) собираем пары якорь - элемент (свитчер)
        self.logger.info(f"5.1) собираем пары якорь - элемент (свитчер)")
        anchor_pairs = self._find_anchor_element_pairs(elems)
        self.logger.info(f"{anchor_pairs=}")

        # 5.2) обычные свойства
        self.logger.info(f"5.2) обычные свойства")
        for prop in self._build_regular_props(
                elems,
                title_el,
                summary_pairs,
                attr_list,
                include_class,
                max_name_words,
                used_names,
                recycler_id
        ):
            properties.append(prop)
        self.logger.info(f"{properties=}")

        # 5.2.1) построим мапу id→имя свойства, чтобы потом найти anchor_name
        self.logger.info(f"5.2.1) построим мапу id→имя свойства, чтобы потом найти anchor_name")
        self._anchor_name_map = {p['element_id']: p['name']
                                 for p in properties
                                 if 'element_id' in p}
        self.logger.info(f"{self._anchor_name_map=}")


        # 5.3) switchers: собираем через общий _build_switch_prop
        self.logger.info(f"5.3) switchers: собираем через общий _build_switch_prop")
        for anchor, switch, depth in anchor_pairs:
            name, anchor_name, locator, depth = self._build_switch_prop(
                anchor, switch, depth,
                attr_list, include_class,
                max_name_words, used_names
            )
            properties.append({
                "name": name,
                "locator": locator,
                "sibling": False,
                "via_recycler": switch.get("scrollable_parents", [None])[0] == recycler_id if switch.get(
                    "scrollable_parents") else False,
                "anchor_name": anchor_name,
                "depth": depth,
            })
        self.logger.info(f"{properties}")

        # 5.4) summary-свойства
        self.logger.info("5.4) summary-свойства")
        for title_e, summary_e in summary_pairs:
            name, locator, summary_id, base_name = self._build_summary_prop(
                title_el=title_e,
                summary_el=summary_e,
                attr_list=attr_list,
                include_class=False,
                max_name_words=max_name_words,
                used_names=used_names
            )
            properties.append({
                'name': name,
                'locator': locator,
                'sibling': True,
                'summary_id': summary_id,
                'base_name': base_name,
            })

        # 5.5) удаляем дубликаты элементов
        self.logger.info(f"5.5) удаляем дубликаты элементов")
        properties = self._filter_duplicates(properties)
        self.logger.info(f"{properties=}")

        # 5.6) определение локатора для скроллера
        self.logger.info(f"5.6) определение локатора для скроллера")
        need_recycler = any(p.get("via_recycler") for p in properties)
        recycler_locator = (
            self._build_locator(recycler_el, attr_list, include_class)
            if need_recycler and recycler_el else None
        )

        # 5.7) удаление text из локаторов у элементов, которые не ищутся по text в UiAutomator2
        self.logger.info(f"5.7) удаление text из локаторов у элементов, которые не ищутся по text в UiAutomator2")
        properties = self._remove_text_from_non_label_elements(properties)

        # 6) рендер и запись
        self.logger.info(f"6) рендер и запись")
        template = self.env.get_template('page_object.py.j2')
        properties.sort(key=lambda p: p["name"])  # сортировка по алфавиту
        rendered = template.render(
            class_name=class_name,
            raw_title=raw_title,
            title_locator=title_locator,
            properties=properties,
            need_recycler=need_recycler,
            recycler_locator=recycler_locator,
        )

        # self.logger.info(f"Props:\n{json.dumps(properties, indent=2)}")

        # 7) Формируем путь с постфиксом
        self.logger.info(f"7) Формируем путь с постфиксом")
        if filename_postfix:
            name, ext = os.path.splitext(file_name)
            final_filename = f"{name}{filename_postfix}{ext}"
        else:
            final_filename = file_name

        # 8) Запись в файл
        self.logger.info(f"8) Запись в файл")
        path = os.path.join(output_dir, final_filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)  # ← вот так
        with open(path, 'w', encoding='utf-8') as f:
            f.write(rendered)

        self.logger.info(f"Generated PageObject → {path}")

        return path, class_name

    # —————————————————————————————————————————————————————————————————————————
    #                           приватные «стройблоки»
    # —————————————————————————————————————————————————————————————————————————

    def _prepare_attributes(
            self,
            attributes: Optional[
                Union[Set[str], Tuple[str], List[str]]
            ]
    ) -> Tuple[List[str], bool]:
        default = ['text', 'content-desc', 'resource-id']
        attr_list = list(attributes) if attributes else default.copy()
        include_class = 'class' in attr_list
        if include_class:
            attr_list.remove('class')
        return attr_list, include_class

    def _slug_words(self, s: str) -> List[str]:
        parts = re.split(r'[^\w]+', unidecode(s))
        return [p.lower() for p in parts if p]

    def _build_locator(
            self,
            el: Dict[str, str],
            attr_list: List[str],
            include_class: bool
    ) -> Dict[str, str]:
        # loc: Dict[str, str] = {
        #     k: el[k] for k in attr_list if el.get(k)
        # }
        loc: Dict[str, str] = {}
        for k in attr_list:
            val = el.get(k)
            if not val:
                continue
            if k == 'scrollable' and val == 'false':
                continue  # пропускаем бесполезный scrollable=false
            loc[k] = val

        if include_class and el.get('class'):
            loc['class'] = el['class']
        return loc

    def _select_title_element(
            self,
            elems: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """Выбирает первый элемент, у которого есть text или content-desc (в этом порядке)."""
        for el in elems:
            if el.get('text') or el.get('content-desc'):
                return el
        return elems[0] if elems else {}

    def _raw_title(self, title_el: Dict[str, str]) -> str:
        return (
                title_el.get('text')
                or title_el.get('content-desc')
                or title_el.get('resource-id', '').split('/', 1)[-1]
        )

    def _format_names(self, raw_title: str) -> Tuple[str, str]:
        parts = re.split(r'[^\w]+', unidecode(raw_title))
        class_name = 'Page' + ''.join(p.capitalize() for p in parts if p)
        file_name = re.sub(
            r'(?<!^)(?=[A-Z])', '_', class_name
        ).lower() + '.py'
        return class_name, file_name

    def _build_summary_prop(
            self,
            title_el: Dict[str, str],
            summary_el: Dict[str, str],
            attr_list: List[str],
            include_class: bool,
            max_name_words: int,
            used_names: Set[str]
    ) -> Tuple[str, Dict[str, str], Dict[str, str], Optional[str]]:
        """
        Строит:
          name       — имя summary-свойства,
          locator    — словарь локатора title-элемента,
          summary_id — словарь для get_sibling(),
          base_name  — имя базового title-свойства (если оно будет сгенерировано)
        """
        rid = summary_el.get('resource-id', '')
        raw = title_el.get('text') or title_el.get('content-desc')
        if not raw and title_el.get('resource-id'):
            raw = self._strip_package_prefix(title_el['resource-id'])
        words = self._slug_words(raw)[:max_name_words]
        base = "_".join(words) or "summary"
        base_name = self._sanitize_name(f"{base}")
        name = self._sanitize_name(f"{base}_summary")

        locator = self._build_locator(title_el, attr_list, include_class)
        summary_id = {'resource-id': rid}
        return name, locator, summary_id, base_name

    def _build_regular_props(
            self,
            elems: List[Dict[str, str]],
            title_el: Dict[str, str],
            summary_pairs: List[Tuple[Dict[str, str], Dict[str, str]]],
            attr_list: List[str], # ['text', 'content-desc', 'resource-id']
            include_class: bool,
            max_name_words: int,
            used_names: Set[str],
            recycler_id
    ) -> List[Dict]:
        props: List[Dict] = []
        processed_ids = {
            s.get('resource-id', '')
            for _, s in summary_pairs
        }
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

        for el in elems:
            self.logger.info(f"{el=}")
            rid = el.get('resource-id', '')
            if el is title_el or rid in processed_ids:
                continue

            locator = self._build_locator(el, attr_list, include_class)
            if not locator:
                continue

            cls = el.get("class", "")
            is_blacklisted = cls in self.BLACKLIST_NO_TEXT_CLASSES

            if is_blacklisted:
                raw = el.get("content-desc") or self._strip_package_prefix(el.get("resource-id", ""))
                key = "content-desc" if el.get("content-desc") else "resource-id"
            else:
                key = next((k for k in attr_list if el.get(k)), 'resource-id')
                raw = el.get(key) or self._strip_package_prefix(el.get('resource-id', ''))

            words = self._slug_words(raw)[:max_name_words]
            base_name = "_".join(words) or key.replace('-', '_')

            name = self._sanitize_name(base_name)
            i = 1
            while name in used_names:
                name = self._sanitize_name(f"{name}_{i}")
                i += 1
            used_names.add(name)

            props.append({
                'name': name,
                'element_id': el['id'],
                'locator': locator,
                'sibling': False,
                'via_recycler': el.get("scrollable_parents", [None])[0] == recycler_id if el.get(
                    "scrollable_parents") else False,
            })
        #     self.logger.debug("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        #     self.logger.debug(f"{el.items()}")
        #     self.logger.debug(f'{el.get("scrollable_parents", [None])[0] == recycler_id if el.get("scrollable_parents") else False}')
        #
        # self.logger.debug(f"\n{props=}\n")
        return props

    def _sanitize_name(self, raw_name: str) -> str:
        """
        Валидное имя метода:
         - не-буквенно-цифровые → '_'
         - если начинается с цифры → 'num_' + …
        """
        name = re.sub(r'[^\w]', '_', raw_name)
        if name and name[0].isdigit():
            name = 'num_' + name
        return name

    def _strip_package_prefix(self, resource_id: str) -> str:
        """Обрезает package-префикс из resource-id, если он есть (например: com.android.settings:id/foo -> foo)."""
        return resource_id.split('/', 1)[-1] if '/' in resource_id else resource_id

    def _filter_duplicates(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Removes duplicate properties based on locator.
        Keeps:
          - Summary elements (sibling=True)
          - Switches (identified by presence of 'anchor_name')

        Args:
            properties (List[Dict]): List of property dicts with 'locator' and optional 'sibling' / 'anchor_name'

        Returns:
            List[Dict]: Filtered properties
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}()")

        seen: Set[FrozenSet[Tuple[str, str]]] = set()
        filtered: List[Dict] = []

        for prop in properties:
            locator = prop.get("locator", {})
            loc_key = frozenset(locator.items())  # делаем hashable для set

            is_summary = prop.get("sibling", False)
            is_switch = "anchor_name" in prop

            if loc_key in seen and not is_summary and not is_switch:
                self.logger.debug(f"Duplicate locator skipped: {prop['name']} → {locator}")
                continue

            seen.add(loc_key)
            filtered.append(prop)

        return filtered

    def _find_summary_siblings(self, elements: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """Find (title, summary) element pairs based on parent and sibling relation."""

        # Группируем по родителю
        grouped: Dict[Optional[str], List[Dict[str, Any]]] = defaultdict(list)
        for el in elements:
            grouped[el.get("parent_id")].append(el)

        result: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []

        for siblings in grouped.values():
            # Восстанавливаем порядок — можно по `index`, или по порядку в списке (если гарантировано)
            siblings.sort(key=lambda x: int(x.get("index", 0)))
            for i, el in enumerate(siblings):
                rid = el.get("resource-id", "")
                if not rid.endswith("/summary"):
                    continue

                # ищем соседа title
                for j in (i - 1, i + 1):
                    if 0 <= j < len(siblings):
                        sib = siblings[j]
                        sib_rid = sib.get("resource-id", "")
                        if sib_rid.endswith("/title") or sib.get("text"):
                            result.append((sib, el))
                            break
        return result

    def _select_main_recycler(self, elems: List[Dict[str, Any]]) -> Optional[str]:
        """Возвращает id самого вложенного scrollable-контейнера (по максимальной глубине scrollable_parents)."""
        candidates = [
            el.get("scrollable_parents", [])
            for el in elems
            if el.get("scrollable_parents")
        ]
        if not candidates:
            return None
        # Выбираем scrollable_parents с максимальной длиной и берём [0]
        deepest = max(candidates, key=len)
        return deepest[0] if deepest else None

    def _find_anchor_element_pairs(
            self,
            elements: List[Dict[str, Any]],
            max_depth: int = 5,
            target: Tuple[str, str] = ('class', 'android.widget.Switch'),
            looking_for_an_anchor: Tuple[str, str] = ("class", "android.widget.TextView"),
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any], int]]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        pairs = []
        target_by, target_value = target
        targets = self._find_targets_for_anchor(elements, target_by, target_value)
        self.logger.info(f"{targets=}")
        for target in targets:
            if "depth" not in target or "parent_id" not in target:
                self.logger.warning(f"Target {target.get('id')} missing depth or parent_id. Skipping.")
                continue

            anchor = self._find_anchor_in_siblings(elements, target, looking_for_an_anchor)
            if anchor is None:
                for current_depth in range(max_depth):
                    anchor = self._find_anchor_in_cousins(elements, target, current_depth, looking_for_an_anchor)
                    if anchor:
                        pairs.append((target, anchor, current_depth))
                        break
                if anchor is None:
                    self.logger.debug(f"No anchor found for target {target.get('id')} after {max_depth} levels.")
            else:
                pairs.append((target, anchor, 0))
        return pairs

    def _find_anchor_in_cousins(
            self,
            elements: List[Dict[str, Any]],
            target: Dict[str, Any],
            depth: int,
            looking_for_an_anchor: Tuple[str, str] = ("class", "android.widget.TextView"),
    ) -> Optional[Dict[str, Any]]:
        """Finds anchor among 'cousin' elements by climbing up the tree and scanning subtree at same depth as target.

        Args:
            elements (List[Dict[str, Any]]): All parsed elements.
            target (Dict[str, Any]): The target element.
            depth (int): Number of levels to climb to reach common ancestor.
            looking_for_an_anchor (Tuple[str, str]): Key and value pair to identify valid anchor.

        Returns:
            Optional[Dict[str, Any]]: Anchor element if found, else None.
        """
        from_id = target.get("parent_id")
        if not from_id:
            self.logger.debug(f"Skip cousin search: target {target.get('id')} has no parent_id")
            return None

        # 1. climb up N levels to get the ancestor
        ancestor_id = from_id
        for _ in range(depth):
            ancestor = next((el for el in elements if el["id"] == ancestor_id), None)
            if not ancestor:
                self.logger.debug(f"Ancestor not found at depth {depth} for element {target.get('id')}")
                return None
            ancestor_id = ancestor.get("parent_id")
            if not ancestor_id:
                self.logger.debug(f"Reached top of tree before expected depth for element {target.get('id')}")
                return None

        # 2. find elements that are direct/indirect children of ancestor_id and have same depth as target
        target_depth = target["depth"]
        cousins = [
            el for el in elements
            if el.get("parent_id") != target.get("parent_id")  # exclude direct siblings
               and el.get("depth") == target_depth
        ]

        if not cousins:
            self.logger.debug(f"No cousins found at depth={target_depth} under ancestor={ancestor_id}")
            return None

        key, value = looking_for_an_anchor
        for el in cousins:
            if el.get(key) == value and el.get("text"):
                return el

        self.logger.debug(
            f"No matching anchor found among cousins at depth={target_depth} under ancestor={ancestor_id}")
        return None

    def _find_anchor_in_siblings(
            self,
            elements: List[Dict[str, Any]],
            target: Dict[str, Any],
            looking_for_an_anchor: Tuple[str, str]
    ) -> Optional[Dict[str, Any]]:
        parent_id = target.get("parent_id")
        looking_for_an_anchor_by = looking_for_an_anchor[0]
        looking_for_an_anchor_value = looking_for_an_anchor[1]
        if not parent_id:
            self.logger.debug("Anchor search aborted: target has no parent_id.")
            return None

        siblings = [
            el for el in elements
            if el.get("parent_id") == parent_id and el.get("id") != target.get("id")
        ]

        if not siblings:
            self.logger.debug(f"No siblings found for target id={target.get('id')} with parent_id={parent_id} in elements={elements}")
            return None

        for sibling in siblings:
            if sibling.get(looking_for_an_anchor_by) == looking_for_an_anchor_value:
                return sibling

        self.logger.debug(
            f"No suitable anchor found among siblings of target id={target.get('id')} with parent_id={parent_id} in elements={elements}")
        return None

    def _find_targets_for_anchor(self, elements,  by: str, value: str) -> List[Dict[str, Any]]:
        """Find all elements matching the given attribute and value.

        Args:
            by (str): Attribute name to filter by (e.g., "class", "resource-id").
            value (str): Attribute value to match.

        Returns:
            List[Dict[str, Any]]: Filtered list of matching elements.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}: by={by}, value={value}")
        return [el for el in elements if el.get(by) == value]

    def _build_switch_prop(
            self,
            anchor_el: Dict[str, Any],
            switch_el: Dict[str, Any],
            depth: int,
            attr_list: List[str],
            include_class: bool,
            max_name_words: int,
            used_names: Set[str]
    ) -> Tuple[str, str, Dict[str, str], int]:
        """
        Возвращает кортеж:
         - name         — имя свойства-свитчера
         - anchor_name  — имя свойства-якоря (уже сгенерированного)
         - locator      — словарь для get_element(switch_el)
         - depth        — глубина подъёма (сколько раз get_parent())
        """
        # 1) имя якоря найдём в списке regular_props по id
        anchor_name = self._anchor_name_map[anchor_el['id']]

        # 2) генерим имя для switch
        raw = anchor_el.get('text') or anchor_el.get('content-desc') or ""
        words = self._slug_words(raw)[:max_name_words]
        base = "_".join(words) or "switch"
        name = self._sanitize_name(f"{base}_switch")
        i = 1
        while name in used_names:
            name = self._sanitize_name(f"{base}_switch_{i}")
            i += 1
        used_names.add(name)

        # 3) локатор для самого switch
        locator = self._build_locator(switch_el, attr_list, include_class)

        return name, anchor_name, locator, depth

    def _remove_text_from_non_label_elements(self, props: List[Dict]) -> List[Dict]:
        """
        Удаляет ключ 'text' из локаторов у элементов, которые не ищутся по text в UiAutomator2.
        """
        for prop in props:
            locator = prop.get("locator", {})
            cls = locator.get("class")
            if cls in self.BLACKLIST_NO_TEXT_CLASSES and "text" in locator:
                self.logger.debug(f"Удаляем 'text' из локатора {cls} → {locator}")
                locator.pop("text", None)

        return props



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
