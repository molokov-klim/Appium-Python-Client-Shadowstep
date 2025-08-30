from enum import Enum


class XPathMethod(str, Enum):
    CHILD = "child"
    DESCENDANT = "descendant"
    PARENT = "parent"
    ANCESTOR = "ancestor"
    FOLLOWING_SIBLING = "following-sibling"
    PRECEDING_SIBLING = "preceding-sibling"
    ATTRIBUTE = "attribute"
    SELF = "self"
    DESCENDANT_OR_SELF = "descendant-or-self"
    ANCESTOR_OR_SELF = "ancestor-or-self"

    NODE_NAME = "nodeName"

    ATTRIBUTE_EQUALS = "attributeEquals"
    ATTRIBUTE_CONTAINS = "attributeContains"
    ATTRIBUTE_STARTS_WITH = "attributeStartsWith"

    TEXT_EQUALS = "textEquals"
    TEXT_CONTAINS = "textContains"
    TEXT_STARTS_WITH = "textStartsWith"

    POSITION = "position"
    LAST = "last"

    ABSOLUTE_PATH = "absolutePath"
    RELATIVE_PATH = "relativePath"
