# shadowstep/page_object/page_object_parser.py
"""Page Object Parser for Android UI XML parsing and tree building.

This module provides functionality to parse Android UI XML (uiautomator2 output)
and build a tree structure of UI elements for Page Object generation.
"""

from __future__ import annotations

import logging
from typing import Any, cast

from lxml import etree

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepRootNodeFilteredOutError
from shadowstep.page_object.page_object_element_node import UiElementNode
from shadowstep.utils.utils import get_current_func_name

# Type aliases for better readability
ElementAttributes = dict[str, Any]
ScrollStack = list[str]

# Default configuration constants
DEFAULT_WHITE_LIST_CLASSES: tuple[str, ...] = (
    "android.widget.EditText",
    "android.widget.Switch",
    "android.widget.SeekBar",
    "android.widget.ProgressBar",
    "androidx.recyclerview.widget.RecyclerView",
    "android.widget.ScrollView",
)

DEFAULT_BLACK_LIST_CLASSES: tuple[str, ...] = (
    "hierarchy",
    "android.widget.LinearLayout",
    "android.widget.FrameLayout",
    "android.view.ViewGroup",
    "android.widget.GridLayout",
    "android.widget.TableLayout",
    "android.widget.ImageView",
    "android.widget.RelativeLayout",
)

DEFAULT_WHITE_LIST_RESOURCE_ID: tuple[str, ...] = (
    "button", "btn", "edit", "input",
    "search", "list", "recycler", "nav",
    "menu", "scrollable", "checkbox", "switch", "toggle",
)

DEFAULT_BLACK_LIST_RESOURCE_ID: tuple[str, ...] = (
    "decor", "divider", "wrapper",
)

# Important containers that are allowed even if they contain 'container'
DEFAULT_CONTAINER_WHITELIST: tuple[str, ...] = (
    "main", "dialog", "scrollable",
)


class PageObjectParser:
    """Parser for Android UI XML that builds element trees for Page Object generation.

    This class parses XML output from uiautomator2 and builds a tree structure
    of UI elements, filtering them based on configurable white/black lists.

    Attributes:
        WHITE_LIST_CLASSES: Classes that are always allowed
        BLACK_LIST_CLASSES: Classes that are always filtered out
        WHITE_LIST_RESOURCE_ID: Resource IDs that are always allowed
        BLACK_LIST_RESOURCE_ID: Resource IDs that are always filtered out
        CONTAINER_WHITELIST: Container IDs that are always allowed

    """

    def __init__(
        self,
        white_list_classes: tuple[str, ...] = DEFAULT_WHITE_LIST_CLASSES,
        black_list_classes: tuple[str, ...] = DEFAULT_BLACK_LIST_CLASSES,
        white_list_resource_id: tuple[str, ...] = DEFAULT_WHITE_LIST_RESOURCE_ID,
        black_list_resource_id: tuple[str, ...] = DEFAULT_BLACK_LIST_RESOURCE_ID,
        container_whitelist: tuple[str, ...] = DEFAULT_CONTAINER_WHITELIST,
    ) -> None:
        """Initialize the PageObjectParser with filtering configuration.

        Args:
            white_list_classes: Classes that are always allowed through filtering
            black_list_classes: Classes that are always filtered out
            white_list_resource_id: Resource IDs that are always allowed
            black_list_resource_id: Resource IDs that are always filtered out
            container_whitelist: Container IDs that are always allowed

        """
        self.logger = logging.getLogger(__name__)

        self.WHITE_LIST_CLASSES: tuple[str, ...] = white_list_classes
        self.BLACK_LIST_CLASSES: tuple[str, ...] = black_list_classes
        self.WHITE_LIST_RESOURCE_ID: tuple[str, ...] = white_list_resource_id
        self.BLACK_LIST_RESOURCE_ID: tuple[str, ...] = black_list_resource_id
        self.CONTAINER_WHITELIST: tuple[str, ...] = container_whitelist

        self._tree: etree.Element | None = None
        self.ui_element_tree: UiElementNode | None = None

    def parse(self, xml: str) -> UiElementNode:
        """Parse XML string and build element tree.

        Args:
            xml: XML string to parse (typically from uiautomator2 page_source)

        Returns:
            Root node of the parsed element tree

        Raises:
            etree.XMLSyntaxError: If XML parsing fails
            ValueError: If root node is filtered out and has no valid children

        """
        self.logger.info(f"{get_current_func_name()}")
        try:
            self._tree = etree.fromstring(xml.encode("utf-8"))
            self.ui_element_tree = self._build_tree(self._tree)
        except etree.XMLSyntaxError:
            self.logger.exception("Failed to parse XML")
            raise
        else:
            return self.ui_element_tree

    def _build_tree(self, root_et: etree._Element) -> UiElementNode:  # noqa: C901
        """Build element tree from XML element.

        Args:
            root_et: Root XML element to build tree from

        Returns:
            Root node of the built tree

        Raises:
            ValueError: If root node is filtered out and has no valid children

        """
        id_counter = 0

        def _recurse(
            el: etree._Element,
            parent: UiElementNode | None,
            scroll_stack: ScrollStack,
            depth: int,
        ) -> UiElementNode | None:
            """Recursively build tree nodes from XML elements.

            Args:
                el: Current XML element to process
                parent: Parent node in the tree
                scroll_stack: Stack of scrollable parent IDs
                depth: Current depth in the tree

            Returns:
                Built node or None if filtered out

            """
            nonlocal id_counter
            attrib = dict(cast("Any", el.attrib))
            el_id = f"el_{id_counter}"
            id_counter += 1

            new_scroll_stack = scroll_stack.copy()
            if attrib.get("scrollable") == "true":
                new_scroll_stack.insert(0, el_id)

            children_nodes: list[UiElementNode] = []
            for child_et in el:
                child_node = _recurse(cast("Any", child_et), None, new_scroll_stack, depth + 1)
                if child_node:
                    children_nodes.append(child_node)

            if self._is_element_allowed(attrib):
                node = UiElementNode(
                    id=el_id,
                    tag=cast("Any", el.tag),
                    attrs=attrib,
                    parent=parent,
                    depth=depth,
                    scrollable_parents=new_scroll_stack,
                    children=[],
                )
                for child in children_nodes:
                    child.parent = node
                    node.children.append(child)
                return node
            # If parent is filtered out, create virtual container
            if not children_nodes:
                return None
            virtual = UiElementNode(
                id=el_id,
                tag=cast("Any", el.tag),
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
            root_et = next(iter(cast("Any", root_et)))

        root_node = _recurse(cast("Any", root_et), None, [], 0)
        if not root_node:
            raise ShadowstepRootNodeFilteredOutError
        return root_node

    def _is_element_allowed(self, attrib: ElementAttributes) -> bool:
        """Check if element should be allowed based on its attributes.

        Args:
            attrib: Element attributes dictionary

        Returns:
            True if element should be allowed, False otherwise

        """
        cls = attrib.get("class")
        rid = attrib.get("resource-id")
        text = attrib.get("text")
        desc = attrib.get("content-desc")

        # Absolute ban
        if cls in self.BLACK_LIST_CLASSES:
            return False
        if rid in self.BLACK_LIST_RESOURCE_ID:
            return False

        # Absolute pass
        if cls in self.WHITE_LIST_CLASSES:
            return True
        if rid in self.WHITE_LIST_RESOURCE_ID:
            return True

        return bool(text) or bool(desc)
