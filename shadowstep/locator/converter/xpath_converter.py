"""XPath converter module for Shadowstep framework.

This module provides the XPathConverter class for converting
XPath expressions to UiSelector strings and Shadowstep dictionary
locators with comprehensive validation and error handling.
"""
from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from typing import Any

from eulxml.xpath import parse
from eulxml.xpath.ast import (
    AbbreviatedStep,
    AbsolutePath,
    BinaryExpression,
    FunctionCall,
    NameTest,
    NodeType,
    PredicatedExpression,
    Step,
)

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepConversionError
from shadowstep.locator.types.shadowstep_dict import ShadowstepDictAttribute
from shadowstep.locator.types.ui_selector import UiAttribute

_BOOL_ATTRS = {
    "checkable": (ShadowstepDictAttribute.CHECKABLE, UiAttribute.CHECKABLE),
    "checked": (ShadowstepDictAttribute.CHECKED, UiAttribute.CHECKED),
    "clickable": (ShadowstepDictAttribute.CLICKABLE, UiAttribute.CLICKABLE),
    "enabled": (ShadowstepDictAttribute.ENABLED, UiAttribute.ENABLED),
    "focusable": (ShadowstepDictAttribute.FOCUSABLE, UiAttribute.FOCUSABLE),
    "focused": (ShadowstepDictAttribute.FOCUSED, UiAttribute.FOCUSED),
    "long-clickable": (ShadowstepDictAttribute.LONG_CLICKABLE, UiAttribute.LONG_CLICKABLE),
    "scrollable": (ShadowstepDictAttribute.SCROLLABLE, UiAttribute.SCROLLABLE),
    "selected": (ShadowstepDictAttribute.SELECTED, UiAttribute.SELECTED),
    "password": (ShadowstepDictAttribute.PASSWORD, UiAttribute.PASSWORD),
}

_NUM_ATTRS = {
    "index": (ShadowstepDictAttribute.INDEX, UiAttribute.INDEX),
    "instance": (ShadowstepDictAttribute.INSTANCE, UiAttribute.INSTANCE),
}

_EQ_ATTRS = {
    # text / description (content-desc)
    "text": (ShadowstepDictAttribute.TEXT, UiAttribute.TEXT),
    "content-desc": (ShadowstepDictAttribute.DESCRIPTION, UiAttribute.DESCRIPTION),
    # resource id / package / class
    "resource-id": (ShadowstepDictAttribute.RESOURCE_ID, UiAttribute.RESOURCE_ID),
    "package": (ShadowstepDictAttribute.PACKAGE_NAME, UiAttribute.PACKAGE_NAME),
    "class": (ShadowstepDictAttribute.CLASS_NAME, UiAttribute.CLASS_NAME),
}

# where contains / starts-with are allowed
_CONTAINS_ATTRS = {
    "text": (ShadowstepDictAttribute.TEXT_CONTAINS, UiAttribute.TEXT_CONTAINS),
    "content-desc": (ShadowstepDictAttribute.DESCRIPTION_CONTAINS, UiAttribute.DESCRIPTION_CONTAINS),
}
_STARTS_ATTRS = {
    "text": (ShadowstepDictAttribute.TEXT_STARTS_WITH, UiAttribute.TEXT_STARTS_WITH),
    "content-desc": (ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH, UiAttribute.DESCRIPTION_STARTS_WITH),
}
# where matches() is allowed
_MATCHES_ATTRS = {
    "text": (ShadowstepDictAttribute.TEXT_MATCHES, UiAttribute.TEXT_MATCHES),
    "content-desc": (ShadowstepDictAttribute.DESCRIPTION_MATCHES, UiAttribute.DESCRIPTION_MATCHES),
    "resource-id": (ShadowstepDictAttribute.RESOURCE_ID_MATCHES, UiAttribute.RESOURCE_ID_MATCHES),
    "package": (ShadowstepDictAttribute.PACKAGE_NAME_MATCHES, UiAttribute.PACKAGE_NAME_MATCHES),
    "class": (ShadowstepDictAttribute.CLASS_NAME_MATCHES, UiAttribute.CLASS_NAME_MATCHES),
}


def _to_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("true", "1"):
            return True
        if v in ("false", "0"):
            return False
    raise ShadowstepConversionError(f"Expected boolean literal, got: {val!r}")


def _to_number(val: Any) -> int:
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str) and val.isdigit():
        return int(val)
    raise ShadowstepConversionError(f"Expected numeric literal, got: {val!r}")


class XPathConverter:
    """Convert xpath expression to UiSelector expression or Shadowstep Dict locator."""

    def __init__(self):
        """Initialize the XPathConverter."""
        self.logger = logging.getLogger(__name__)

    # ========== validation ==========

    @staticmethod
    def _validate_xpath(xpath_str: str) -> None:
        if re.search(r"\band\b|\bor\b", xpath_str):
            raise ShadowstepConversionError("Logical operators (and/or) are not supported")
        try:
            parse(xpath_str)
        except Exception as e:
            raise ShadowstepConversionError(f"Invalid XPath: {e}")  # noqa: B904

    # ========== public API ==========

    def xpath_to_dict(self, xpath_str: str) -> dict[str, Any]:
        """Convert XPath string to dictionary representation.

        Args:
            xpath_str: XPath expression as string.

        Returns:
            dict[str, Any]: Dictionary representation of the XPath.
        """
        self._validate_xpath(xpath_str)
        node = parse(xpath_str)
        node_list = self._ast_to_list(node.relative)    # type: ignore
        return self._ast_to_dict(node_list)

    def xpath_to_ui_selector(self, xpath_str: str) -> str:
        """Convert XPath string to UiSelector string.

        Args:
            xpath_str: XPath expression as string.

        Returns:
            str: UiSelector expression as string.
        """
        self._validate_xpath(xpath_str)
        node = parse(xpath_str)
        node_list = self._ast_to_list(node.relative)    # type: ignore
        result = self._balance_parentheses(self._ast_to_ui_selector(node_list))
        return "new UiSelector()" + result + ";"

    # ========== AST traversal ==========

    def _ast_to_ui_selector(self, node_list: list[AbbreviatedStep | Step]) -> str:  # noqa: C901    # type: ignore
        if not node_list:
            return ""
        node = node_list[0]
        parts: list[str] = []
        if isinstance(node, Step):
            # add predicates (e.g. @class, @resource-id)
            for predicate in node.predicates:
                parts.append(self._predicate_to_ui(predicate))    # type: ignore

            if len(node_list) > 1:
                next_node = node_list[1]
                child_str = self._ast_to_ui_selector(node_list[1:])  # recurse on next node(s)
                if child_str:
                    if isinstance(next_node, AbbreviatedStep) and next_node.abbr == "..":
                        # consecutive ..
                        parent_count = 1
                        i = 2
                        while i < len(node_list) and isinstance(node_list[i], AbbreviatedStep) and node_list[
                            i].abbr == "..":
                            parent_count += 1
                            i += 1
                        rest_str = self._ast_to_ui_selector(node_list[i:]) if i < len(node_list) else ""
                        for _ in range(parent_count):
                            rest_str = f".fromParent(new UiSelector(){rest_str})"
                        parts.append(rest_str)
                        return "".join(parts)

                    if isinstance(next_node, Step) and next_node.axis in ("following-sibling", "preceding-sibling"):
                        # sibling → fromParent + childSelector
                        parts.append(f".fromParent(new UiSelector(){child_str})")
                    else:
                        # default: child
                        parts.append(f".childSelector(new UiSelector(){child_str})")

        elif isinstance(node, AbbreviatedStep):    # type: ignore
            if node.abbr == "..":
                if len(node_list) > 1:
                    child_str = self._ast_to_ui_selector(node_list[1:])
                    if child_str:
                        return f".fromParent(new UiSelector(){child_str})"
                return ""
            if node.abbr == ".":
                return self._ast_to_ui_selector(node_list[1:])
            raise ShadowstepConversionError(f"Unsupported abbreviated step in UiSelector: {node!r}")
        else:
            raise ShadowstepConversionError(f"Unsupported AST node in UiSelector: {node!r}")
        return "".join(parts)

    def _ast_to_dict(self, node_list: list[Any]) -> dict[str, Any]:
        shadowstep_dict: dict[str, Any] = {}
        return self._build_shadowstep_dict(node_list, shadowstep_dict)

    def _build_shadowstep_dict(
            self,
            node_list: list[AbbreviatedStep | Step],    # type: ignore
            shadowstep_dict: dict[str, Any],
    ) -> dict[str, Any]:
        if not node_list:
            return shadowstep_dict

        node = node_list[0]

        if isinstance(node, Step):
            for predicate in node.predicates:
                self._apply_predicate_to_dict(predicate, shadowstep_dict)    # type: ignore

            i = 1
            # ".."
            if i < len(node_list) and isinstance(node_list[i], AbbreviatedStep) and node_list[i].abbr == "..":
                # create fromParent
                shadowstep_dict[ShadowstepDictAttribute.FROM_PARENT.value] = self._build_shadowstep_dict(node_list[i + 1:], {})
                return shadowstep_dict

            # sibling
            if i < len(node_list) and isinstance(node_list[i], Step) and node_list[i].axis in (
                "following-sibling",
                "preceding-sibling",
            ):
                shadowstep_dict[ShadowstepDictAttribute.SIBLING] = self._build_shadowstep_dict(node_list[i:], {})
                return shadowstep_dict

            # childSelector
            if i < len(node_list):
                shadowstep_dict[ShadowstepDictAttribute.CHILD_SELECTOR.value] = self._build_shadowstep_dict(node_list[i:], {})
            return shadowstep_dict

        if isinstance(node, AbbreviatedStep) and node.abbr == "..":    # type: ignore
            # count ".."
            depth = 1
            while depth < len(node_list) and isinstance(node_list[depth], AbbreviatedStep) and node_list[
                depth].abbr == "..":
                depth += 1

            # ".."
            rest_dict = self._build_shadowstep_dict(node_list[depth:], {})

            # ".."
            for _ in range(depth):
                rest_dict = {ShadowstepDictAttribute.FROM_PARENT.value: rest_dict}

            shadowstep_dict.update(rest_dict)
            return shadowstep_dict

        raise ShadowstepConversionError(f"Unsupported AST node in build: {node!r}")

    def _ast_to_list(self, node: Any) -> list[AbbreviatedStep | Step]:    # type: ignore
        result = []

        if isinstance(node, (Step, AbbreviatedStep)):    # type: ignore
            result.append(node)

        elif isinstance(node, BinaryExpression):
            result.extend(self._ast_to_list(node.left))
            result.extend(self._ast_to_list(node.right))

        else:
            raise ShadowstepConversionError(f"Unsupported AST node: {node!r}")

        return result

    def _collect_predicates(self, node: Any) -> Iterable[Any]:
        if isinstance(node, AbsolutePath):
            if node.relative is not None:
                yield from self._collect_predicates(node.relative)
            return

        if isinstance(node, PredicatedExpression):
            for p in node.predicates:
                yield p
            yield from self._collect_predicates(node.base)
            return

        if isinstance(node, Step):
            for p in node.predicates:
                yield p
            return

        if isinstance(node, BinaryExpression):
            yield from self._collect_predicates(node.left)
            yield from self._collect_predicates(node.right)
            return


    # ========== predicate handlers (DICT) ==========

    def _apply_predicate_to_dict(self, pred_expr: Any, out: dict[str, Any]) -> None:  # noqa: C901
        if isinstance(pred_expr, Step):
            nested = self._build_shadowstep_dict([pred_expr], {})
            for k, v in nested.items():
                out[k] = v
            return

        if isinstance(pred_expr, FunctionCall):
            attr, kind, value = self._parse_function_predicate(pred_expr)
            if kind == "contains":
                d_attr = _CONTAINS_ATTRS.get(attr)
                if not d_attr:
                    raise ShadowstepConversionError(f"contains() is not supported for @{attr}")
                out[d_attr[0].value] = value    # type: ignore
                return
            if kind == "starts-with":
                d_attr = _STARTS_ATTRS.get(attr)
                if not d_attr:
                    raise ShadowstepConversionError(f"starts-with() is not supported for @{attr}")
                out[d_attr[0].value] = value    # type: ignore
                return
            if kind == "matches":
                d_attr = _MATCHES_ATTRS.get(attr)
                if not d_attr:
                    raise ShadowstepConversionError(f"matches() is not supported for @{attr}")
                out[d_attr[0].value] = value    # type: ignore
                return
            raise ShadowstepConversionError(f"Unsupported function: {pred_expr.name}")

        if isinstance(pred_expr, (int, float)):    # type: ignore
            out[ShadowstepDictAttribute.INSTANCE.value] = int(pred_expr) - 1
            return

        if isinstance(pred_expr, BinaryExpression):
            if (
                    pred_expr.op == "="
                    and isinstance(pred_expr.left, FunctionCall)
                    and pred_expr.left.name == "position"
                    and not pred_expr.left.args
                    and isinstance(pred_expr.right, (int, float))    # type: ignore
            ):
                out[ShadowstepDictAttribute.INDEX.value] = int(pred_expr.right) - 1
                return

            if pred_expr.op not in ("=",):
                raise ShadowstepConversionError(f"Unsupported comparison operator: {pred_expr.op}")
            attr, value = self._parse_equality_comparison(pred_expr)
            if attr in _EQ_ATTRS:
                out[_EQ_ATTRS[attr][0].value] = value    # type: ignore
                return
            if attr in _BOOL_ATTRS:
                out[_BOOL_ATTRS[attr][0].value] = _to_bool(value)    # type: ignore
                return
            if attr in _NUM_ATTRS:
                out[_NUM_ATTRS[attr][0].value] = _to_number(value)    # type: ignore
                return
            raise ShadowstepConversionError(f"Unsupported attribute: @{attr}")

        # attribute presence: [@enabled]
        if isinstance(pred_expr, Step) and pred_expr.axis == "@" and isinstance(pred_expr.node_test, NameTest):
            attr = pred_expr.node_test.name
            if attr in _BOOL_ATTRS:
                out[_BOOL_ATTRS[attr][0].value] = True    # type: ignore
                return
            raise ShadowstepConversionError(f"Attribute presence predicate not supported for @{attr}")

        # positional number [3] or something else
        raise ShadowstepConversionError(f"Unsupported predicate: {pred_expr!r}")

    # ========== predicate handlers (UI SELECTOR) ==========

    def _predicate_to_ui(self, pred_expr: Any) -> str:  # noqa: C901
        if isinstance(pred_expr, FunctionCall):
            attr, kind, value = self._parse_function_predicate(pred_expr)
            if kind == "contains":
                u = _CONTAINS_ATTRS.get(attr)
                if not u:
                    raise ShadowstepConversionError(f"contains() is not supported for @{attr}")
                return f'.{u[1].value}("{value}")'
            if kind == "starts-with":
                u = _STARTS_ATTRS.get(attr)
                if not u:
                    raise ShadowstepConversionError(f"starts-with() is not supported for @{attr}")
                return f'.{u[1].value}("{value}")'
            if kind == "matches":
                u = _MATCHES_ATTRS.get(attr)
                if not u:
                    raise ShadowstepConversionError(f"matches() is not supported for @{attr}")
                return f'.{u[1].value}("{value}")'
            raise ShadowstepConversionError(f"Unsupported function: {kind}")

        if isinstance(pred_expr, (int, float)):
            return f".{UiAttribute.INSTANCE.value}({int(pred_expr) - 1})"

        if isinstance(pred_expr, BinaryExpression):
            if (
                    pred_expr.op == "="
                    and isinstance(pred_expr.left, FunctionCall)
                    and pred_expr.left.name == "position"
                    and not pred_expr.left.args
                    and isinstance(pred_expr.right, (int, float))
            ):
                return f".{UiAttribute.INDEX.value}({int(pred_expr.right) - 1})"
            attr, value = self._parse_equality_comparison(pred_expr)
            if attr in _EQ_ATTRS:
                return f'.{_EQ_ATTRS[attr][1].value}("{value}")'
            if attr in _BOOL_ATTRS:
                return f".{_BOOL_ATTRS[attr][1].value}({str(_to_bool(value)).lower()})"
            if attr in _NUM_ATTRS:
                return f".{_NUM_ATTRS[attr][1].value}({_to_number(value)})"
            raise ShadowstepConversionError(f"Unsupported attribute: @{attr}")
        raise ShadowstepConversionError(f"Unsupported predicate: {pred_expr!r}")

    def _parse_function_predicate(self, func: FunctionCall) -> tuple[str, str, Any]:
        name = func.name
        if name not in ("contains", "starts-with", "matches"):
            raise ShadowstepConversionError(f"Unsupported function: {name}")
        if len(func.args) != 2:    # type: ignore
            raise ShadowstepConversionError(f"{name}() must have 2 arguments")
        lhs, rhs = func.args
        attr = self._extract_attr_name(lhs)
        value = self._extract_literal(rhs)
        return attr, name, value

    def _parse_equality_comparison(self, bexpr: BinaryExpression) -> tuple[str, Any]:
        left_attr = self._maybe_attr(bexpr.left)
        right_attr = self._maybe_attr(bexpr.right)
        if left_attr is not None:
            return left_attr, self._extract_literal(bexpr.right)
        if right_attr is not None:
            return right_attr, self._extract_literal(bexpr.left)
        if isinstance(bexpr.left, FunctionCall) and bexpr.left.name == "text":
            return "text", self._extract_literal(bexpr.right)
        if isinstance(bexpr.right, FunctionCall) and bexpr.right.name == "text":
            return "text", self._extract_literal(bexpr.left)
        raise ShadowstepConversionError("Equality must compare @attribute or text() with a literal")

    def _maybe_attr(self, node: Any) -> str | None:    # type: ignore
        try:
            return self._extract_attr_name(node)
        except ShadowstepConversionError:
            return None

    @staticmethod
    def _extract_attr_name(node: Any) -> str:
        if isinstance(node, Step) and node.axis == "@" and isinstance(node.node_test, NameTest):
            return node.node_test.name
        if isinstance(node, FunctionCall) and node.name == "text":
            return "text"
        if isinstance(node, NodeType) and node.name == "text":
            return "text"
        raise ShadowstepConversionError(f"Unsupported attribute expression: {node!r}")

    @staticmethod
    def _extract_literal(node: Any) -> Any:
        if isinstance(node, (str, int, float, bool)):
            return node
        if isinstance(node, FunctionCall) and node.name in ("true", "false") and not node.args:
            return node.name == "true"
        raise ShadowstepConversionError(f"Unsupported literal: {node!r}")

    @staticmethod
    def _balance_parentheses(selector: str) -> str:
        open_count = 0
        close_count = 0

        for ch in selector:
            if ch == "(":
                open_count += 1
            elif ch == ")":
                close_count += 1

        if open_count == close_count:
            return selector

        if close_count > open_count:
            # remove extra ')' on the right
            diff = close_count - open_count
            i = len(selector)
            while diff > 0 and i > 0:
                i -= 1
                if selector[i] == ")":
                    diff -= 1
            return selector[:i] + selector[i+1:]

        if open_count > close_count:
            raise ShadowstepConversionError(
                f"Unbalanced UiSelector string: too many '(' in {selector}",
            )

        return selector
