from enum import Enum


class XPathMethod(str, Enum):
    # --- Tree navigation operators ---
    CHILD = "child"  # direct child node (e.g., /child::div)
    DESCENDANT = "descendant"  # any descendant at any level (//div)
    PARENT = "parent"  # parent node
    ANCESTOR = "ancestor"  # any ancestor at any level
    FOLLOWING_SIBLING = "following-sibling"  # next sibling node at the same level
    PRECEDING_SIBLING = "preceding-sibling"  # previous sibling node at the same level
    SELF = "self"  # current node
    DESCENDANT_OR_SELF = "descendant-or-self"  # current node + all descendants
    ANCESTOR_OR_SELF = "ancestor-or-self"  # current node + all ancestors

    # --- Node/element selection ---
    NODE_NAME = "nodeName"  # filter by node/tag name

    # --- Attribute handling ---
    ATTRIBUTE = "attribute"  # access a node's attribute
    ATTRIBUTE_EQUALS = "attributeEquals"  # attribute equals a given value
    ATTRIBUTE_CONTAINS = "attributeContains"  # attribute contains a substring
    ATTRIBUTE_STARTS_WITH = "attributeStartsWith"  # attribute starts with a substring

    # --- Text handling ---
    TEXT_EQUALS = "textEquals"  # node text exactly matches
    TEXT_CONTAINS = "textContains"  # node text contains a substring
    TEXT_STARTS_WITH = "textStartsWith"  # node text starts with a substring

    # --- Positional filters ---
    POSITION = "position"  # position of the node among siblings
    LAST = "last"  # last node among siblings

    # --- XPath path types ---
    ABSOLUTE_PATH = "absolutePath"  # absolute path from the document root
    RELATIVE_PATH = "relativePath"  # relative path from the current node
