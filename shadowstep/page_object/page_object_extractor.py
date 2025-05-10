# shadowstep/page_object/#page_object_extractor.py

import inspect
import logging
from typing import Dict, List, Set, Optional, Tuple, Any, Union
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


class PageObjectParser:
    def __init__(self,
                 white_list_classes: Set[str] = None,
                 black_list_classes: Set[str] = None,
                 white_list_resource_id: Set[str] = None,
                 black_list_resource_id: Set[str] = None,
                 filter_system: bool = True,):
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
        self._elements: List[Dict[str, Any]] = []

    def parse(self, xml: str) -> Union[list[dict[str, Any]], list[Any]]:
        """Parses and walks the XML, populating elements and tree."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            self._tree = ET.fromstring(xml.encode('utf-8'))
            self._elements = self._walk_tree(self._tree)
        except ET.XMLSyntaxError:
            self.logger.exception("Failed to parse XML")
            self._tree = None
            self._elements = []
        return self._elements

    def _walk_tree(self, root: ET.Element) -> List[Dict[str, Any]]:
        result = []
        id_counter = 0

        def _recurse(el: ET.Element, parent_id: Optional[str], scroll_stack: List[str], depth: int) -> None:
            nonlocal id_counter
            attrib = dict(el.attrib)
            el_id = f"el_{id_counter}"
            id_counter += 1

            new_scroll_stack = scroll_stack.copy()
            if attrib.get("scrollable") == "true":
                new_scroll_stack.insert(0, el_id)

            add_element = False
            if attrib.get("text"):
                add_element = True
            if attrib.get("content-desc"):
                add_element = True

            resource_id = attrib.get("resource-id")
            if resource_id in self.WHITE_LIST_RESOURCE_ID:
                add_element = True
            elif resource_id and resource_id not in self.BLACK_LIST_RESOURCE_ID:
                add_element = True

            class_name = attrib.get("class")
            if class_name in self.WHITE_LIST_CLASSES:
                add_element = True
            elif class_name not in self.BLACK_LIST_CLASSES:
                add_element = True

            attrib.update({
                "id": el_id,
                "parent_id": parent_id,
                "scrollable_parents": new_scroll_stack,
                "depth": depth,
            })
            # self.logger.debug(
            #     f"[{el_id}] parent={parent_id} depth={depth} scrollable={attrib.get('scrollable')} "
            #     f"scroll_stack={new_scroll_stack} attrib={attrib}"
            # )
            if add_element:
                result.append(attrib)

            for child in el:
                _recurse(child, el_id, new_scroll_stack, depth + 1)

        _recurse(root, None, [], 0)
        # self.logger.debug("====================================================")
        # for res in result:
        #     self.logger.debug(f"res:\n{res}")
        # self.logger.debug("====================================================")
        return result
