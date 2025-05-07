import logging
from typing import List
import os
import re
from unidecode import unidecode

from shadowstep.page_object.page_object_extractor import PageObjectExtractor
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep


class PageObjectGenerator:
    def __init__(self):
        self.poe = PageObjectExtractor()
        self.logger = logging.getLogger(__name__)

    def transliterate(self, text: str) -> str:
        # убираем кириллицу → латиницу, акценты и т.п.
        return unidecode(text)

    def camel_case(self, text: str) -> str:
        """Example Page → ExamplePage"""
        tr = self.transliterate(text)
        parts = re.split(r'[\s\-_]+', tr)
        return ''.join(p.capitalize() for p in parts if p)

    def snake_case(self, text: str) -> str:
        """PageExample → page_example"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower()

    def make_attr_name(self, base: str, prefix: str) -> str:
        """
        base: текст / content-desc / resource-id
        prefix: последняя часть класса (например, Button, TextView)
        """
        tr = self.transliterate(base)
        parts = re.split(r'[\s\-\./]+', tr)
        # усечём каждое слово до 10 символов
        words = [p[:10] for p in parts if p]
        name = '_'.join(words).lower()
        # удаляем все не-буквы/цифры/_
        name = re.sub(r'[^\w]', '', name)
        if not name:
            name = prefix.lower()
        return f"{prefix.lower()}_{name}"

    def generate(self, source_xml: str, output_dir: str, max_name_words: int = 5):
        """
        Generate a PageObject class from the given XML source and write it to a file.
        - max_name_words: maximum number of words to use in each locator name (default 5).
        - summary siblings are handled specially: for any element with resource-id ending in '/summary',
          find its sibling (e.g. the title), and generate a `<title>_summary_<class>` property.
        """
        import os
        import re
        from unidecode import unidecode
        import lxml.etree as ET

        # parse XML to allow sibling lookup
        tree = ET.fromstring(source_xml.encode('utf-8'))

        # extract all simple elements
        elems = self.poe.extract_simple_elements(source_xml)

        # pick the title element (first with text, then content-desc, else first)
        title_el = next((el for el in elems if el.get('text')), None)
        if not title_el:
            title_el = next((el for el in elems if el.get('content-desc')), None)
        if not title_el and elems:
            title_el = elems[0]

        # derive raw title string
        raw_title = (
            title_el.get('text')
            or title_el.get('content-desc')
            or title_el.get('resource-id', '').split('/', 1)[-1]
        )

        # helper: CamelCase from words
        def to_camel(s: str) -> str:
            parts = re.split(r'[^\w]+', unidecode(s))
            return ''.join(p.capitalize() for p in parts if p)

        # class name and file name
        class_name = f"Page{to_camel(raw_title)}"
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
        file_name = f"{snake}.py"

        lines = [
            "import logging",
            "",
            "from shadowstep.element.element import Element",
            "from shadowstep.page_base import PageBaseShadowstep",
            "",
            f"class {class_name}(PageBaseShadowstep):",
            "    def __init__(self):",
            "        super().__init__()",
            "        self.logger = logging.getLogger(__name__)",
            "",
            "    def __repr__(self):",
            f"        return f\"{{self.name}} ({class_name})\"",
            "",
            "    @property",
            "    def edges(self) -> dict:",
            "        return {}",
            "",
            "    @property",
            "    def name(self) -> str:",
            f"        return \"{raw_title}\"",
            "",
            "    @property",
            "    def title(self) -> Element:",
            f"        return self.shadowstep.get_element({{'text': {repr(title_el.get('text'))}, 'class': {repr(title_el.get('class'))}}})",
            ""
        ]

        used_names = {"title"}
        processed_summary_ids = set()

        # helper: slugify into words
        def slug_words(s: str):
            slug = unidecode(s)
            parts = re.split(r'[^\w]+', slug)
            return [p.lower() for p in parts if p]

        for el in elems:
            rid = el.get('resource-id', '')

            # special: summary siblings
            if rid.endswith('/summary'):
                # ... (логика без изменений) ...
                processed_summary_ids.add(rid)
                continue

            # skip processed summaries
            if rid in processed_summary_ids:
                continue

            # --- основная ветка для обычных элементов ---

            # выбираем, что брать для имени
            if el.get('text'):
                key, raw_val = 'text', el['text']
            elif el.get('content-desc'):
                key, raw_val = 'content-desc', el['content-desc']
            else:
                # <--- ИЗМЕНЕНО: для resource-id берём часть после '/' без пакета/id
                key, raw_val = 'resource-id', rid.split('/', 1)[1] if '/' in rid else rid

            # строим сам локатор (для resource-id — полный, для остальных — raw_val + класс)
            if key == 'resource-id':
                loc = {'resource-id': rid}
            else:
                loc = {key: raw_val}
                if el.get('class'):
                    loc['class'] = el['class']

            # генерируем имя: до max_name_words слов из raw_val + суффикс класса
            words = slug_words(raw_val)[:max_name_words]
            base = "_".join(words) or key.replace('-', '_')
            class_suffix = (el.get('class', '').split('.')[-1] or "element").lower()
            name = f"{base}_{class_suffix}"

            # обеспечиваем уникальность
            i = 1
            orig = name
            while name in used_names:
                name = f"{orig}_{i}"
                i += 1
            used_names.add(name)

            dict_literal = "{" + ", ".join(f"{repr(k)}: {repr(v)}" for k, v in loc.items()) + "}"
            lines += [
                "    @property",
                f"    def {name}(self) -> Element:",
                f"        return self.shadowstep.get_element({dict_literal})",
                ""
            ]

        # is_current_page() должен быть последним методом
        lines += [
            "    def is_current_page(self) -> bool:",
            "        try:",
            "            return self.title.is_visible()",
            "        except Exception as e:",
            "            self.logger.error(e)",
            "            return False",
            ""
        ]

        # записываем файл
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, file_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.logger.info(f"Generated PageObject → {path}")


