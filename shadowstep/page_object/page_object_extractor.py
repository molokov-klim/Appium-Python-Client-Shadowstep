import inspect
import logging
from typing import Dict, List, Set, Optional, Tuple
from collections import Counter
from lxml import etree as ET

DEFAULT_WHITE_LIST_CLASSES: Set[str] = {
    'android.widget.EditText',
    'android.widget.Switch',
    'android.widget.SeekBar',
    'android.widget.ProgressBar',
}
DEFAULT_BLACK_LIST_CLASSES: Set[str] = {
    'android.widget.LinearLayout',
    'android.widget.FrameLayout',
    'android.view.ViewGroup',
    'android.widget.GridLayout',
    'android.widget.TableLayout'
}
DEFAULT_WHITE_LIST_RESOURCE_ID: Set[str] = {
    'button', 'btn', 'edit', 'input',
    'search', 'list', 'recycler', 'nav',
    'menu', 'scrollable', 'checkbox', 'switch', 'toggle'
}
DEFAULT_BLACK_LIST_RESOURCE_ID: Set[str] = {
    'decor', 'divider', 'wrapper'
}
# «важные» контейнеры, которые отдаем даже при наличии 'container'
DEFAULT_CONTAINER_WHITELIST: Set[str] = {
    'main', 'dialog', 'scrollable'
}


class PageObjectExtractor:
    def __init__(self,
                 white_list_classes: Set[str] = None,
                 black_list_classes: Set[str] = None,
                 white_list_resource_id: Set[str] = None,
                 black_list_resource_id: Set[str] = None,
                 package: str = None,
                 filter_system: bool = True,
                 smart_filter: bool = True,
                 filter_by_class: bool = True):
        self.logger = logging.getLogger(__name__)
        # фильтрация по resource-id (whitelist/blacklist/container)
        self.smart_filter: bool = smart_filter
        # фильтрация по black-list классам
        self.filter_by_class: bool = filter_by_class
        # дропать ли системные android:id/…
        self.filter_system: bool = filter_system
        # пакет приложения (если None, определяется автоматически)
        self.package: Optional[str] = package

        self.WHITE_LIST_CLASSES: Set[str] = (
            DEFAULT_WHITE_LIST_CLASSES if white_list_classes is None else white_list_classes
        )
        self.BLACK_LIST_CLASSES: Set[str] = (
            DEFAULT_BLACK_LIST_CLASSES if black_list_classes is None else black_list_classes
        )
        self.WHITE_LIST_RESOURCE_ID: Set[str] = (
            DEFAULT_WHITE_LIST_RESOURCE_ID if white_list_resource_id is None else white_list_resource_id
        )
        self.BLACK_LIST_RESOURCE_ID: Set[str] = (
            DEFAULT_BLACK_LIST_RESOURCE_ID if black_list_resource_id is None else black_list_resource_id
        )
        self.CONTAINER_WHITELIST: Set[str] = DEFAULT_CONTAINER_WHITELIST

    def extract_simple_elements(self, xml: str) -> List[Dict[str, str]]:
        """Aggregate elements by text, resource-id, content-desc and class, remove duplicates."""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        all_elements = (
            self.extract_by_text(xml)
            + self.extract_by_resource_id(xml)
            + self.extract_by_content_desc(xml)
            + self.extract_by_class(xml)
        )

        seen: Set[frozenset] = set()
        unique: List[Dict[str, str]] = []

        for el in all_elements:
            key = frozenset(el.items())
            if key not in seen:
                seen.add(key)
                unique.append(el)

        return unique

    def find_summary_siblings(self, xml: str) -> List[Tuple[Dict[str, str], Dict[str, str]]]:
        """
        Найти пары (заголовок, summary), где:
        - summary имеет resource-id, заканчивающийся на '/summary'
        - заголовок — соседний элемент по родителю с text или resource-id, заканчивающимся на '/title'
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            tree = ET.fromstring(xml.encode('utf-8'))
            result = []
            for parent in tree.iter():
                children = list(parent)
                for i, el in enumerate(children):
                    rid = el.attrib.get('resource-id', '')
                    if not rid.endswith('/summary'):
                        continue
                    # ищем title-соседа слева или справа
                    sibling = None
                    for j in (i - 1, i + 1):
                        if 0 <= j < len(children):
                            sib = children[j].attrib
                            sib_rid = sib.get('resource-id', '')
                            if sib_rid.endswith('/title') or sib.get('text'):
                                sibling = sib
                                break
                    if sibling:
                        result.append((dict(sibling), dict(el.attrib)))
            return result
        except ET.XMLSyntaxError:
            self.logger.exception("XML parse error in find_summary_siblings()")
            return []

    def extract_by_text(self, xml: str) -> List[Dict[str, str]]:
        """Extract elements that have non-empty 'text' attribute."""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        return self._extract_by_attribute(xml, 'text')

    def extract_by_resource_id(self, xml: str) -> List[Dict[str, str]]:
        """Extract elements that have non-empty 'resource-id' attribute, with optional filtering."""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        list_res = self._extract_by_attribute(xml, 'resource-id')
        # всегда прогоняем через единый метод, который сам смотрит флаги
        return self.filter_resource_id(list_res)

    def extract_by_content_desc(self, xml: str) -> List[Dict[str, str]]:
        """Extract elements that have non-empty 'content-desc' attribute."""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        return self._extract_by_attribute(xml, 'content-desc')

    def extract_by_class(self, xml: str) -> List[Dict[str, str]]:
        """Extract only elements whose class в white-list."""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        return self._extract_by_class_list(xml, self.WHITE_LIST_CLASSES)



    def filter_resource_id(self, elements: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Многоуровневая фильтрация по resource-id и классам.
        Если указан self.APP_PACKAGE, сразу оставит только элементы этого пакета.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        result: List[Dict[str, str]] = []

        # Определяем автоматический пакет, но он больше нужен для smart_filter-веток
        pkg = self.package
        if self.smart_filter and not pkg:
            prefixes = [
                rid.split(':', 1)[0]
                for el in elements
                if (rid := el.get('resource-id', '')).count(':') == 1
            ]
            valid = [p for p in prefixes if p and p != 'android' and len(p) > 2]
            if valid:
                pkg = Counter(valid).most_common(1)[0][0]
                self.logger.debug(f"Auto-detected app package: {pkg}")

        for el in elements:
            rid = el.get('resource-id', '')
            cls = el.get('class', '')

            # 1) Всегда: пропускаем пустые ID
            if not rid:
                self.logger.debug(f"Skipping element {el} — empty resource-id")
                continue

            # 2) Всегда: если явно задан APP_PACKAGE — оставляем только его ID
            if self.package and not rid.startswith(f"{self.package}:id/"):
                self.logger.debug(f"Skipping {rid} — outside of specified app_package {self.package}")
                continue

            # 3) Системные ID (опционально)
            if self.filter_system and rid.startswith("android:id/"):
                self.logger.debug(f"Skipping {rid} — system id")
                continue

            # --- теперь уже ветки smart_filter и filter_by_class ---

            # Готовим токены «чистого» имени
            raw_id = rid.split('/', 1)[-1]
            tokens = set(raw_id.split('_'))

            # 4) whitelist по ID
            if self.smart_filter and tokens & self.WHITE_LIST_RESOURCE_ID:
                self.logger.debug(f"Keeping {rid} — whitelist-id match {tokens & self.WHITE_LIST_RESOURCE_ID}")
                result.append(el)
                continue

            # 5) контейнерный whitelist
            if self.smart_filter and 'container' in tokens and tokens & self.CONTAINER_WHITELIST:
                self.logger.debug(f"Keeping {rid} — container-whitelist match {tokens & self.CONTAINER_WHITELIST}")
                result.append(el)
                continue

            # 6) blacklist по ID
            if self.smart_filter and tokens & self.BLACK_LIST_RESOURCE_ID:
                self.logger.debug(f"Skipping {rid} — blacklist-id match {tokens & self.BLACK_LIST_RESOURCE_ID}")
                continue

            # 7) blacklist по классам
            if self.filter_by_class and cls in self.BLACK_LIST_CLASSES:
                self.logger.debug(f"Skipping {rid} — blacklist-class match {cls}")
                continue

            # 8) всё остальное
            self.logger.debug(f"Keeping {rid} — no filter matched")
            result.append(el)

        return result

    def _extract_by_class_list(self, xml: str, class_set: Set[str]) -> List[Dict[str, str]]:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            tree = ET.fromstring(xml.encode('utf-8'))
            return [
                dict(el.attrib)
                for el in tree.iter()
                if el.attrib.get('class') in class_set
            ]
        except ET.XMLSyntaxError:
            return []

    def _extract_by_attribute(self, xml: str, attr_name: str) -> List[Dict[str, str]]:
        """Внутренний метод: вернуть все элементы с непустым атрибутом."""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            tree = ET.fromstring(xml.encode('utf-8'))
            return [
                dict(element.attrib)
                for element in tree.iter()
                if element.attrib.get(attr_name)
            ]
        except ET.XMLSyntaxError:
            return []


