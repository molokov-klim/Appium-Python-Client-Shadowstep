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
from unidecode import unidecode
from jinja2 import Environment, FileSystemLoader

from shadowstep.page_object.page_object_parser import PageObjectParser


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
        # 1) выбор атрибутов для локаторов
        attr_list, include_class = self._prepare_attributes(attributes)

        # 2) извлечение и элементов
        elems = self.extractor.parse(source_xml)
        if additional_elements:
            elems += additional_elements
        # self.logger.debug(f"{elems=}")

        # 2.1)
        recycler_id = self._select_main_recycler(elems)
        recycler_el = next((e for e in elems if e['id'] == recycler_id), None)

        # 2.2) формирование пар summary
        summary_pairs = self._find_summary_siblings(elems)
        # self.logger.debug(f"{summary_pairs=}")

        # 3) заголовок страницы
        title_el = self._select_title_element(elems)
        raw_title = self._raw_title(title_el)

        # 4) PageClassName + file_name.py
        class_name, file_name = self._format_names(raw_title)

        # 5) собираем все свойства
        used_names: Set[str] = {'title'}
        title_locator = self._build_locator(
            title_el, attr_list, include_class
        )
        properties: List[Dict] = []

        # 5.1)
        anchor_pairs = self._find_anchor_element_pairs(elems)
        # self.logger.debug(f"{anchor_pairs=}")

        # 5.2) обычные свойства
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

        # 5.2.1) построим мапу id→имя свойства, чтобы потом найти anchor_name
        self._anchor_name_map = {p['element_id']: p['name']
                                 for p in properties
                                 if 'element_id' in p}

        # 5.3) switchers: собираем через общий _build_switch_prop
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

        # 5.4) summary-свойства
        for title_e, summary_e in summary_pairs:
            name, locator, summary_id, base_name = self._build_summary_prop(
                title_e,
                summary_e,
                attr_list,
                include_class,
                max_name_words,
                used_names
            )
            properties.append({
                'name': name,
                'locator': locator,
                'sibling': True,
                'summary_id': summary_id,
                'base_name': base_name,
            })

        # 5.5) удаляем дубликаты элементов
        properties = self._filter_duplicates(properties)

        # 5.6)
        need_recycler = any(p.get("via_recycler") for p in properties)
        recycler_locator = (
            self._build_locator(recycler_el, attr_list, include_class)
            if need_recycler and recycler_el else None
        )

        # 5.7) удаление text из локаторов у элементов, которые не ищутся по text в UiAutomator2
        properties = self._remove_text_from_non_label_elements(properties)

        # 6) рендер и запись
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

        # Формируем путь с постфиксом
        if filename_postfix:
            name, ext = os.path.splitext(file_name)
            final_filename = f"{name}{filename_postfix}{ext}"
        else:
            final_filename = file_name

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
        suffix = title_el.get('class', '').split('.')[-1].lower()
        base_name = self._sanitize_name(f"{base}_{suffix}")
        name = self._sanitize_name(f"{base}_summary_{suffix}")

        i = 1
        while name in used_names:
            name = self._sanitize_name(f"{base}_summary_{suffix}_{i}")
            i += 1
        used_names.add(name)

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
            base = "_".join(words) or key.replace('-', '_')
            suffix = el.get('class', '').split('.')[-1].lower()
            raw_name = f"{base}_{suffix}"

            name = self._sanitize_name(raw_name)
            i = 1
            while name in used_names:
                name = self._sanitize_name(f"{raw_name}_{i}")
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
            target: Tuple[str, str] = ('class', 'android.widget.Switch')
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any], int]]:
        """
        Ищет тройки (anchor, target_element, depth), где:
          - target_element — элемент, у которого атрибут target[0] содержит target[1]
          - anchor         — соседний элемент с text или content-desc (вплоть до одного уровня вложенности)
          - depth          — сколько раз поднялись по дереву до общего родителя
        """
        from collections import defaultdict

        by_attr, attr_val = target

        # 1) группировка: parent_id → прямые дети
        children_by_parent: Dict[Optional[str], List[Dict[str, Any]]] = defaultdict(list)
        for el in elements:
            children_by_parent[el.get('parent_id')].append(el)

        # id → элемент, для подъема вверх
        el_by_id = {el['id']: el for el in elements if 'id' in el}

        # собрать всех потомков по дереву (для проверки уникальности)
        def collect_descendants(parent_id: str) -> List[Dict[str, Any]]:
            stack = [parent_id]
            result = []
            while stack:
                pid = stack.pop()
                for child in children_by_parent.get(pid, []):
                    result.append(child)
                    stack.append(child['id'])
            return result

        pairs: List[Tuple[Dict[str, Any], Dict[str, Any], int]] = []

        # 2) цикл по всем элементам-мишеням
        for target_el in filter(lambda e: attr_val in e.get(by_attr, ''), elements):
            current = target_el
            depth = 0
            anchor = None

            # 2.a) поднимаемся вверх до max_depth
            while depth <= max_depth and current.get('parent_id'):
                parent_id = current['parent_id']
                siblings = children_by_parent.get(parent_id, [])
                siblings.sort(key=lambda x: int(x.get('index', 0)))

                # 2.b) ищем anchor среди siblings и их детей
                for sib in siblings:
                    if sib is target_el:
                        continue

                    if sib.get('text') or sib.get('content-desc'):
                        anchor = sib
                        break

                    for child in children_by_parent.get(sib['id'], []):
                        if child.get('text') or child.get('content-desc'):
                            anchor = child
                            break
                    if anchor:
                        break

                if anchor:
                    # проверяем, что в subtree только один target
                    subtree = collect_descendants(parent_id)
                    count = sum(1 for el in subtree if attr_val in el.get(by_attr, ''))
                    if count == 1:
                        pairs.append((anchor, target_el, depth))
                    else:
                        self.logger.warning(
                            f"Ambiguous targets under parent {parent_id}: {count} found. Skipping."
                        )
                    break

                # идем к следующему родителю
                current = el_by_id.get(parent_id, {})
                depth += 1

            if not anchor:
                self.logger.debug(
                    f"No anchor found for element {target_el.get('id')} up to depth {max_depth}"
                )

        # self.logger.debug(f"Found anchor-element-depth triplets: {pairs}")
        return pairs

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
