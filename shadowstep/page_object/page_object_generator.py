import logging
from typing import List, Dict
import os
import re
from unidecode import unidecode

from shadowstep.page_object.page_object_extractor import PageObjectExtractor
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep
import logging
from typing import Union, Set, Tuple, List
import os
import re
from unidecode import unidecode

from shadowstep.page_object.page_object_extractor import PageObjectExtractor
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep
import lxml.etree as ET


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

    def generate(self,
                 source_xml: str,
                 output_dir: str,
                 max_name_words: int = 5,
                 attributes: Union[Set[str], Tuple[str], List[str]] = None):
        """
        Generate a PageObject class from the given XML source and write it to a file.

        - max_name_words: maximum number of words to use in each locator name (default 5).
        - attributes: if provided, only these attributes (and 'class' как доп.) будут
          включаться в каждый словарь-локатор; порядок также задаёт приоритет для имени.
        """
        import os
        import re
        from unidecode import unidecode
        import lxml.etree as ET

        # 1) Определяем набор атрибутов для локаторов
        if attributes is None:
            attr_list = ['text', 'content-desc', 'resource-id']
        else:
            attr_list = list(attributes)
        include_class = 'class' in attr_list
        if include_class:
            attr_list.remove('class')

        # 2) Вспомог: разбить строку на слова для имени
        def slug_words(s: str) -> List[str]:
            parts = re.split(r'[^\w]+', unidecode(s))
            return [p.lower() for p in parts if p]

        # 3) build_locator теперь НЕ ОТРЕЗАЕТ префикс у resource-id
        def build_locator(el: Dict[str, str]) -> Dict[str, str]:
            loc: Dict[str, str] = {}
            for key in attr_list:
                val = el.get(key)
                if not val:
                    continue
                # **НЕ тримим** здесь префикс – передаём Appium полный resource-id
                loc[key] = val
            if include_class and el.get('class'):
                loc['class'] = el['class']
            return loc

        # 4) Для имени выбираем ключ по порядку attr_list
        def naming_key(el: Dict[str, str]) -> str:
            for key in attr_list:
                if el.get(key):
                    return key
            return 'resource-id' if el.get('resource-id') else next(iter(el), '')

        # 5) Parse XML и extract_simple_elements
        tree = ET.fromstring(source_xml.encode('utf-8'))
        elems = self.poe.extract_simple_elements(source_xml)

        # 6) Выбираем title_el
        title_el = next((e for e in elems if e.get('text')), None)
        if not title_el:
            title_el = next((e for e in elems if e.get('content-desc')), None)
        if not title_el and elems:
            title_el = elems[0]

        # 7) Формируем class_name и file_name
        raw_title = (
            title_el.get('text')
            or title_el.get('content-desc')
            or title_el.get('resource-id', '').split('/', 1)[-1]
        )
        parts = re.split(r'[^\w]+', unidecode(raw_title))
        class_name = 'Page' + ''.join(p.capitalize() for p in parts if p)
        file_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower() + '.py'

        # 8) Заголовок класса
        lines: List[str] = [
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
            ""
        ]

        # 9) title-свойство
        title_loc = build_locator(title_el)
        lines += [
            "    @property",
            "    def title(self) -> Element:",
            f"        return self.shadowstep.get_element({title_loc!r})",
            ""
        ]

        used_names = {"title"}
        processed_summary: Set[str] = set()

        # 10) Сначала summary-соседи
        for el in elems:
            rid_full = el.get('resource-id', '')
            if rid_full.endswith('/summary'):
                nodes = tree.xpath(f"//*[@resource-id='{rid_full}']")
                if not nodes:
                    continue
                sum_node = nodes[0]
                parent = sum_node.getparent()
                sib = next((
                    s for s in parent
                    if s is not sum_node and
                       (s.attrib.get('resource-id','').endswith('/title') or s.attrib.get('text'))
                ), None)
                if not sib:
                    continue

                raw = sib.attrib.get('text') or sib.attrib.get('content-desc') \
                      or sib.attrib.get('resource-id','').split('/',1)[-1]
                words = slug_words(raw)[:max_name_words]
                base = "_".join(words) or "summary"
                suffix = (sib.attrib.get('class','').split('.')[-1]).lower()
                name = f"{base}_summary_{suffix}"
                i = 1
                while name in used_names:
                    name = f"{base}_summary_{suffix}_{i}"
                    i += 1
                used_names.add(name)

                sib_loc = build_locator(sib)
                lines += [
                    "    @property",
                    f"    def {name}(self):",
                    f"        return (",
                    f"            self.shadowstep.get_element({sib_loc!r})",
                    f"                .get_sibling({{'resource-id': {rid_full!r}}})",
                    f"        )",
                    ""
                ]
                processed_summary.add(rid_full)

        # 11) Регулярные элементы (пропускаем title и summary)
        for el in elems:
            rid_full = el.get('resource-id','')
            if el is title_el or rid_full in processed_summary:
                continue

            loc = build_locator(el)
            if not loc:
                continue

            key = naming_key(el)
            raw = el.get(key) or rid_full.split('/',1)[-1]
            words = slug_words(raw)[:max_name_words]
            base = "_".join(words) or key.replace('-', '_')
            suffix = (el.get('class','').split('.')[-1]).lower()
            name = f"{base}_{suffix}"
            i = 1
            while name in used_names:
                name = f"{base}_{suffix}_{i}"
                i += 1
            used_names.add(name)

            lines += [
                "    @property",
                f"    def {name}(self) -> Element:",
                f"        return self.shadowstep.get_element({loc!r})",
                ""
            ]

        # 12) is_current_page в самом конце
        lines += [
            "    def is_current_page(self) -> bool:",
            "        try:",
            "            return self.title.is_visible()",
            "        except Exception as e:",
            "            self.logger.error(e)",
            "            return False",
            ""
        ]

        # 13) Запись файла
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, file_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.logger.info(f"Generated PageObject → {path}")


