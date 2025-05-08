#  shadowstep/page_object/page_object_generator.py
import inspect
import json
import logging
import os
import re
from typing import (
    List, Dict, Union,
    Set, Tuple, Optional, Any
)
from unidecode import unidecode
from jinja2 import Environment, FileSystemLoader

from shadowstep.page_object.page_object_extractor import PageObjectExtractor


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


class PageObjectGenerator:
    """
    Генератор PageObject-классов на основе данных из PageObjectExtractor
    и Jinja2-шаблона.
    """

    def __init__(self, extractor: PageObjectExtractor):
        """
        :param extractor: объект, реализующий методы
            - extract_simple_elements(xml: str) -> List[Dict[str,str]]
            - find_summary_siblings(xml: str) -> List[Tuple[Dict, Dict]]
        """
        self.extractor = extractor
        self.logger = logging.getLogger(__name__)

        # Инициализируем Jinja2
        templates_dir = os.path.join(
            os.path.dirname(__file__),
            'templates'
        )
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),  # откуда загружать шаблоны (директория с .j2-файлами)
            autoescape=False,  # отключаем автоэкранирование HTML/JS (не нужно при генерации Python-кода)
            keep_trailing_newline=True, # сохраняем завершающий перевод строки в файле (важно для git-diff, PEP8 и т.д.)
            trim_blocks=True,  # удаляет новую строку сразу после {% block %} или {% endif %} (уменьшает пустые строки)
            lstrip_blocks=True # удаляет ведущие пробелы перед {% block %} (избавляет от случайных отступов и пустых строк)
        )
        # добавляем фильтр repr
        self.env.filters['pretty_dict'] = _pretty_dict

    def generate(
        self,
        source_xml: str,
        output_dir: str,
        max_name_words: int = 5,
        attributes: Optional[
            Union[Set[str], Tuple[str], List[str]]
        ] = None
    ):
        """
        Оркестратор:
          1) получаем приоритет атрибутов
          2) извлекаем все элементы и пары title/summary
          3) выбираем заголовок страницы
          4) формируем имена класса и файла
          5) собираем список свойств
          6) рендерим через Jinja2 и пишем файл
        """
        # 1) выбор атрибутов для локаторов
        attr_list, include_class = self._prepare_attributes(attributes)

        # 2) извлечение и элементов
        elems = self.extractor.parse(source_xml)
        self.logger.debug(f"{elems=}")

        # 2.1)
        recycler_id = self._select_main_recycler(elems)
        recycler_el = next((e for e in elems if e['id'] == recycler_id), None)

        # 2.2) формирование пар summary
        summary_pairs = self._find_summary_siblings(elems)
        self.logger.debug(f"{summary_pairs=}")

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
        anchor_pairs = self._find_switch_anchor_pairs(elems)
        self.logger.debug(f"{anchor_pairs=}")

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

        # 5.3) switchers
        for anchor, switch in anchor_pairs:
            raw = anchor.get('text') or anchor.get('content-desc')
            words = self._slug_words(raw)[:max_name_words]
            base = "_".join(words) or "switch"
            suffix = "switch"
            name = self._sanitize_name(f"{base}_{suffix}")
            i = 1
            while name in used_names:
                name = self._sanitize_name(f"{base}_{suffix}_{i}")
                i += 1
            used_names.add(name)

            locator = self._build_locator(switch, attr_list, include_class)
            anchor_locator = self._build_locator(anchor, attr_list, include_class)

            properties.append({
                "name": name,
                "locator": locator,
                "sibling": False,
                "via_recycler": switch.get("scrollable_parents", [None])[0] == recycler_id if switch.get(
                    "scrollable_parents") else False,
                "anchor_locator": anchor_locator,  # спец-флаг для jinja2
                "anchor_get_via": True,  # укажем что будет get_parent().get_element(...)
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

        self.logger.info(f"Props:\n{json.dumps(properties, indent=2)}")

        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, file_name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(rendered)

        self.logger.info(f"Generated PageObject → {path}")

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
        file_name  = re.sub(
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
        attr_list: List[str],
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

        for el in elems:
            rid = el.get('resource-id', '')
            if el is title_el or rid in processed_ids:
                continue

            locator = self._build_locator(el, attr_list, include_class)
            if not locator:
                continue

            key = next((k for k in attr_list if el.get(k)), 'resource-id')
            if key == 'resource-id':
                raw = self._strip_package_prefix(el.get(key, ''))
            else:
                raw = el.get(key) or self._strip_package_prefix(rid)
            words = self._slug_words(raw)[:max_name_words]
            base   = "_".join(words) or key.replace('-', '_')
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
                'locator': locator,
                'sibling': False,
                'via_recycler': el.get("scrollable_parents", [None])[0] == recycler_id if el.get("scrollable_parents") else False,
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

    def _filter_duplicates(self, properties: List[Dict]) -> List[Dict]:
        """
        Удаляет свойства, у которых одинаковое «базовое имя» (до _1, _2 и т.д.), если таких свойств ≥ 3.
        """
        from collections import defaultdict

        base_name_map: Dict[str, List[Dict]] = defaultdict(list)
        for prop in properties:
            base = re.sub(r'(_\d+)?$', '', prop['name'])
            base_name_map[base].append(prop)

        filtered: List[Dict] = []
        for group in base_name_map.values():
            if len(group) < 3:
                filtered.extend(group)
        return filtered

    def _find_summary_siblings(self, elements: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """Find (title, summary) element pairs based on parent and sibling relation."""
        from collections import defaultdict

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

    def _find_switch_anchor_pairs(
            self,
            elements: List[Dict[str, Any]],
            max_depth: int = 5
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any], int]]:
        """
        Ищет пары (anchor, switch), где:
          - switch  — элемент с классом, содержащим 'Switch'
          - anchor  — соседний элемент с текстом или content-desc,
                      даже если он вложен на один уровень внутрь
        Алгоритм:
          1. Сгруппировать элементы по parent_id.
          2. Для каждого switch:
             a) Подняться вверх по дереву до max_depth.
             b) В каждом родителе перебрать его прямых детей (siblings), отсортированных по index:
                - если у sibling есть text или content-desc, взять его как anchor;
                - иначе заглянуть на один уровень внутрь его прямых детей.
             c) Если найден anchor, проверить, что в subtree этого parent_id ровно один Switch.
                Если да — добавить пару в результат, иначе — пропустить с предупреждением.
        """
        from collections import defaultdict

        # 1) группировка: parent_id → список прямых детей
        children_by_parent: Dict[Optional[str], List[Dict[str, Any]]] = defaultdict(list)
        for el in elements:
            children_by_parent[el.get('parent_id')].append(el)

        # быстрый доступ по id для подъема вверх
        el_by_id = {el['id']: el for el in elements if 'id' in el}

        def collect_descendants(parent_id: str) -> List[Dict[str, Any]]:
            """Собрать всех потомков (любая глубина) заданного родителя."""
            stack = [parent_id]
            result = []
            while stack:
                pid = stack.pop()
                for child in children_by_parent.get(pid, []):
                    result.append(child)
                    stack.append(child['id'])
            return result

        result: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []

        # 2) основной цикл по всем Switch
        for switch in filter(lambda e: 'Switch' in e.get('class', ''), elements):
            current = switch
            depth = 0
            found_anchor = None

            while depth <= max_depth and current.get('parent_id'):
                parent_id = current['parent_id']
                siblings = children_by_parent.get(parent_id, [])
                # сортируем по index (если есть)
                siblings.sort(key=lambda x: int(x.get('index', 0)))

                # 2.b) ищем anchor среди siblings и их прямых детей
                for sib in siblings:
                    if sib is switch:
                        continue

                    # 1) прямо у sibling
                    if sib.get('text') or sib.get('content-desc'):
                        found_anchor = sib
                        break

                    # 2) на уровень глубже
                    for child in children_by_parent.get(sib['id'], []):
                        if child.get('text') or child.get('content-desc'):
                            found_anchor = child
                            break
                    if found_anchor:
                        break

                if found_anchor:
                    # 2.c) проверяем, что под этим родителем ровно один Switch в subtree
                    subtree = collect_descendants(parent_id)
                    switch_count = sum(1 for el in subtree if 'Switch' in el.get('class', ''))
                    if switch_count == 1:
                        result.append((found_anchor, switch))
                    else:
                        self.logger.warning(
                            f"Ambiguous switches under parent {parent_id}: {switch_count} found. Skipping."
                        )
                    break

                # поднимаемся на уровень выше
                current = el_by_id.get(parent_id, {})
                depth += 1

            if not found_anchor:
                self.logger.debug(
                    f"No anchor found for switch {switch.get('id')} up to depth {max_depth}"
                )

        self.logger.debug(f"Switch-anchor pairs: {result}")
        return result


