import json
import logging
import os
import re
from typing import (
    List, Dict, Union,
    Set, Tuple, Optional
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

        # 2) «сырые» данные от экстрактора
        elems = self.extractor.extract_simple_elements(source_xml)
        summary_pairs = self.extractor.find_summary_siblings(source_xml)

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

        # 5.1) обычные свойства
        for prop in self._build_regular_props(
            elems,
            title_el,
            summary_pairs,
            attr_list,
            include_class,
            max_name_words,
            used_names
        ):
            properties.append(prop)

        # 5.2) summary-свойства
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

        # 5.3) удаляем дубликаты элементов
        properties = self._filter_duplicates(properties)

        # 6) рендер и запись
        template = self.env.get_template('page_object.py.j2')
        properties.sort(key=lambda p: p["name"])  # сортировка по алфавиту
        rendered = template.render(
            class_name    = class_name,
            raw_title     = raw_title,
            title_locator = title_locator,
            properties    = properties,
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
        for key in ('text', 'content-desc'):
            found = next((e for e in elems if e.get(key)), None)
            if found:
                return found
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
        used_names: Set[str]
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
                'name':    name,
                'locator': locator,
                'sibling': False,
            })

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

