# shadowstep/page_object/#page_object_parser.py

import inspect
import logging
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from collections import Counter
from lxml import etree as ET

from shadowstep.page_object.page_object_element_node import UiElementNode

DEFAULT_WHITE_LIST_CLASSES: Set[str] = {
    'android.widget.EditText',
    'android.widget.Switch',
    'android.widget.SeekBar',
    'android.widget.ProgressBar',
    'androidx.recyclerview.widget.RecyclerView',
    'android.widget.ScrollView'
}
DEFAULT_BLACK_LIST_CLASSES: Set[str] = {
    'hierarchy',
    'android.widget.LinearLayout',
    'android.widget.FrameLayout',
    'android.view.ViewGroup',
    'android.widget.GridLayout',
    'android.widget.TableLayout',
    'android.widget.ImageView',
    'android.widget.RelativeLayout'
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


class PageObjectParser:
    def __init__(self,
                 white_list_classes: Set[str] = None,
                 black_list_classes: Set[str] = None,
                 white_list_resource_id: Set[str] = None,
                 black_list_resource_id: Set[str] = None,
                 filter_system: bool = True, ):
        self.logger = logging.getLogger(__name__)

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

        self._tree: Optional[ET.Element] = None
        self.ui_element_tree = None

    def parse(self, xml: str) -> UiElementNode:
        """Parses and walks the XML, populating elements and tree."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            self._tree = ET.fromstring(xml.encode('utf-8'))
            self.ui_element_tree = self._build_tree(self._tree)
            return self.ui_element_tree
        except ET.XMLSyntaxError:
            self.logger.exception("Failed to parse XML")
            raise

    def _build_tree(self, root_et: ET.Element) -> UiElementNode:
        id_counter = 0

        def _recurse(el: ET.Element, parent: Optional[UiElementNode], scroll_stack: List[str], depth: int) -> Optional[
            UiElementNode]:
            nonlocal id_counter
            attrib = dict(el.attrib)
            el_id = f'el_{id_counter}'
            id_counter += 1

            new_scroll_stack = scroll_stack.copy()
            if attrib.get("scrollable") == "true":
                new_scroll_stack.insert(0, el_id)

            children_nodes: List[UiElementNode] = []
            for child_et in el:
                child_node = _recurse(child_et, None, new_scroll_stack, depth + 1)
                if child_node:
                    children_nodes.append(child_node)

            if self._is_element_allowed(attrib):
                node = UiElementNode(
                    id=el_id,
                    tag=el.tag,
                    attrs=attrib,
                    parent=parent,
                    depth=depth,
                    scrollable_parents=new_scroll_stack,
                    children=[]
                )
                for child in children_nodes:
                    child.parent = node
                    node.children.append(child)
                return node
            else:
                # Если родитель отфильтрован — создаём виртуального контейнера
                if not children_nodes:
                    return None
                virtual = UiElementNode(
                    id=el_id,
                    tag=el.tag,
                    attrs=attrib,
                    parent=parent,
                    depth=depth,
                    scrollable_parents=new_scroll_stack,
                    children=[],
                )
                for child in children_nodes:
                    child.parent = virtual
                    virtual.children.append(child)
                return virtual

        if root_et.tag == "hierarchy":
            root_et = next(iter(root_et))

        root_node = _recurse(root_et, None, [], 0)
        if not root_node:
            raise ValueError("Root node was filtered out and has no valid children.")
        return root_node

    def _is_element_allowed(self, attrib: Dict[str, str]) -> bool:
        cls = attrib.get("class")
        rid = attrib.get("resource-id")
        text = attrib.get("text")
        desc = attrib.get("content-desc")

        # ❌ Абсолютный бан
        if cls in self.BLACK_LIST_CLASSES:
            return False
        if rid in self.BLACK_LIST_RESOURCE_ID:
            return False

        # ✅ Абсолютный проход
        if cls in self.WHITE_LIST_CLASSES:
            return True
        if rid in self.WHITE_LIST_RESOURCE_ID:
            return True

        # 🟡 Условный проход — текстовая интерактивность
        if text or desc:
            return True

        # ❌ Всё остальное — в мусор
        return False
