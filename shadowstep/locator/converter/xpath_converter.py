"""XPath converter module for Shadowstep framework.

This module provides the XPathConverter class for converting
XPath expressions to UiSelector strings and Shadowstep dictionary
locators with comprehensive validation and error handling.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable

from eulxml.xpath import parse  # type: ignore[import-untyped]
from eulxml.xpath.ast import (  # type: ignore[import-untyped]
    AbbreviatedStep,
    AbsolutePath,
    BinaryExpression,
    FunctionCall,
    NameTest,
    NodeType,
    PredicatedExpression,
    Step,
)

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepAttributePresenceNotSupportedError,
    ShadowstepBooleanLiteralError,
    ShadowstepContainsNotSupportedError,
    ShadowstepConversionError,
    ShadowstepEqualityComparisonError,
    ShadowstepFunctionArgumentCountError,
    ShadowstepInvalidXPathError,
    ShadowstepLogicalOperatorsNotSupportedError,
    ShadowstepMatchesNotSupportedError,
    ShadowstepNumericLiteralError,
    ShadowstepStartsWithNotSupportedError,
    ShadowstepUnbalancedUiSelectorError,
    ShadowstepUnsupportedAbbreviatedStepError,
    ShadowstepUnsupportedASTNodeBuildError,
    ShadowstepUnsupportedASTNodeError,
    ShadowstepUnsupportedAttributeError,
    ShadowstepUnsupportedAttributeExpressionError,
    ShadowstepUnsupportedComparisonOperatorError,
    ShadowstepUnsupportedFunctionError,
    ShadowstepUnsupportedLiteralError,
    ShadowstepUnsupportedPredicateError,
)
from shadowstep.locator.locator_types.shadowstep_dict import ShadowstepDictAttribute
from shadowstep.locator.locator_types.ui_selector import UiAttribute

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
    "content-desc": (
        ShadowstepDictAttribute.DESCRIPTION_CONTAINS,
        UiAttribute.DESCRIPTION_CONTAINS,
    ),
}
_STARTS_ATTRS = {
    "text": (ShadowstepDictAttribute.TEXT_STARTS_WITH, UiAttribute.TEXT_STARTS_WITH),
    "content-desc": (
        ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH,
        UiAttribute.DESCRIPTION_STARTS_WITH,
    ),
}
# where matches() is allowed
_MATCHES_ATTRS = {
    "text": (ShadowstepDictAttribute.TEXT_MATCHES, UiAttribute.TEXT_MATCHES),
    "content-desc": (ShadowstepDictAttribute.DESCRIPTION_MATCHES, UiAttribute.DESCRIPTION_MATCHES),
    "resource-id": (ShadowstepDictAttribute.RESOURCE_ID_MATCHES, UiAttribute.RESOURCE_ID_MATCHES),
    "package": (ShadowstepDictAttribute.PACKAGE_NAME_MATCHES, UiAttribute.PACKAGE_NAME_MATCHES),
    "class": (ShadowstepDictAttribute.CLASS_NAME_MATCHES, UiAttribute.CLASS_NAME_MATCHES),
}


def _to_bool(val: str | float | bool) -> bool:  # noqa: FBT001
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("true", "1"):
            return True
        if v in ("false", "0"):
            return False
    raise ShadowstepBooleanLiteralError(str(val))


def _to_number(val: str | float) -> int:
    if isinstance(val, (int, float)):
        return int(val)
    if val.isdigit():  # type: ignore[union-attr]
        return int(val)
    raise ShadowstepNumericLiteralError(str(val))


# Constants
FUNCTION_ARGUMENT_COUNT = 2


class XPathConverter:
    """Convert xpath expression to UiSelector expression or Shadowstep Dict locator."""

    def __init__(self) -> None:
        """Initialize the XPathConverter."""
        self.logger = logging.getLogger(__name__)

    # ========== validation ==========

    @staticmethod
    def _validate_xpath(xpath_str: str) -> None:
        if re.search(r"\band\b|\bor\b", xpath_str):
            raise ShadowstepLogicalOperatorsNotSupportedError
        try:
            parse(xpath_str)
        except Exception as error:  # noqa: BLE001, RUF100
            raise ShadowstepInvalidXPathError from error

    # ========== public API ==========

    def xpath_to_dict(self, xpath_str: str) -> dict[str, Any]:
        """Convert XPath string to dictionary representation.

        Args:
            xpath_str: XPath expression as string.

        Returns:
            dict[str, Any]: Dictionary representation of the XPath.

        """
        self._validate_xpath(xpath_str)
        node = parse(xpath_str)  # type: ignore[var-annotated]
        node_list = self._ast_to_list(node.relative)  # type: ignore[arg-type,attr-defined]
        return self._ast_to_dict(node_list)

    def xpath_to_ui_selector(self, xpath_str: str) -> str:
        """Convert XPath string to UiSelector string.

        Args:
            xpath_str: XPath expression as string.

        Returns:
            str: UiSelector expression as string.

        """
        self._validate_xpath(xpath_str)
        node = parse(xpath_str)  # type: ignore[var-annotated]
        node_list = self._ast_to_list(node.relative)  # type: ignore[arg-type,attr-defined]
        result = self._balance_parentheses(self._ast_to_ui_selector(node_list))
        return "new UiSelector()" + result + ";"

    # ========== AST traversal ==========

    def _ast_to_ui_selector(self, node_list: list[AbbreviatedStep | Step]) -> str:  # noqa: C901, PLR0912    # type: ignore[return-any]
        if not node_list:
            return ""
        node = node_list[0]
        parts: list[str] = []
        if isinstance(node, Step):
            # add predicates (e.g. @class, @resource-id)
            for predicate in node.predicates:  # type: ignore[attr-defined]
                parts.append(self._predicate_to_ui(predicate))  # type: ignore[arg-type]  # noqa: PERF401

            if len(node_list) > 1:
                next_node = node_list[1]
                child_str = self._ast_to_ui_selector(node_list[1:])  # recurse on next node(s)
                if child_str:
                    if isinstance(next_node, AbbreviatedStep) and next_node.abbr == "..":  # type: ignore[attr-defined]
                        # consecutive ..
                        parent_count = 1
                        i = 2
                        while (
                            i < len(node_list)
                            and isinstance(node_list[i], AbbreviatedStep)
                            and node_list[i].abbr == ".."  # type: ignore[attr-defined]
                        ):
                            parent_count += 1
                            i += 1
                        rest_str = (
                            self._ast_to_ui_selector(node_list[i:]) if i < len(node_list) else ""
                        )
                        for _ in range(parent_count):
                            rest_str = f".fromParent(new UiSelector(){rest_str})"
                        parts.append(rest_str)
                        return "".join(parts)

                    if isinstance(next_node, Step) and next_node.axis in (  # type: ignore[attr-defined]
                        "following-sibling",
                        "preceding-sibling",
                    ):
                        # sibling → fromParent + childSelector
                        parts.append(f".fromParent(new UiSelector(){child_str})")
                    else:
                        parts.append(f".childSelector(new UiSelector(){child_str})")

        elif isinstance(node, AbbreviatedStep):  # type: ignore[arg-type]
            if node.abbr == "..":  # type: ignore[attr-defined]
                if len(node_list) > 1:
                    child_str = self._ast_to_ui_selector(node_list[1:])
                    if child_str:
                        return f".fromParent(new UiSelector(){child_str})"
                return ""
            if node.abbr == ".":  # type: ignore[attr-defined]
                return self._ast_to_ui_selector(node_list[1:])
            raise ShadowstepUnsupportedAbbreviatedStepError(str(node))
        else:
            raise ShadowstepUnsupportedASTNodeError(str(node))
        return "".join(parts)

    def _ast_to_dict(self, node_list: list[Any]) -> dict[str, Any]:
        shadowstep_dict: dict[str, Any] = {}
        return self._build_shadowstep_dict(node_list, shadowstep_dict)

    def _build_shadowstep_dict(
        self,
        node_list: list[AbbreviatedStep | Step],  # type: ignore[arg-type]
        shadowstep_dict: dict[str, Any],
    ) -> dict[str, Any]:
        if not node_list:
            return shadowstep_dict

        node = node_list[0]

        if isinstance(node, Step):
            for predicate in node.predicates:  # type: ignore[attr-defined]
                self._apply_predicate_to_dict(predicate, shadowstep_dict)  # type: ignore[arg-type]

            i = 1
            # ".."
            if (
                i < len(node_list)
                and isinstance(node_list[i], AbbreviatedStep)
                and node_list[i].abbr == ".."  # type: ignore[attr-defined]
            ):
                # create fromParent
                shadowstep_dict[ShadowstepDictAttribute.FROM_PARENT.value] = (
                    self._build_shadowstep_dict(node_list[i + 1 :], {})
                )
                return shadowstep_dict

            # sibling
            if (
                i < len(node_list)
                and isinstance(node_list[i], Step)
                and node_list[i].axis  # type: ignore[attr-defined]
                in (
                    "following-sibling",
                    "preceding-sibling",
                )
            ):
                shadowstep_dict[ShadowstepDictAttribute.SIBLING] = self._build_shadowstep_dict(
                    node_list[i:],
                    {},
                )
                return shadowstep_dict

            # childSelector
            if i < len(node_list):
                shadowstep_dict[ShadowstepDictAttribute.CHILD_SELECTOR.value] = (
                    self._build_shadowstep_dict(node_list[i:], {})
                )
            return shadowstep_dict

        if isinstance(node, AbbreviatedStep) and node.abbr == "..":  # type: ignore[arg-type,attr-defined]
            # count ".."
            depth = 1
            while (
                depth < len(node_list)
                and isinstance(node_list[depth], AbbreviatedStep)
                and node_list[depth].abbr == ".."  # type: ignore[attr-defined]
            ):
                depth += 1

            # ".."
            rest_dict = self._build_shadowstep_dict(node_list[depth:], {})

            # ".."
            for _ in range(depth):
                rest_dict = {ShadowstepDictAttribute.FROM_PARENT.value: rest_dict}

            shadowstep_dict.update(rest_dict)
            return shadowstep_dict

        raise ShadowstepUnsupportedASTNodeBuildError(str(node))

    def _ast_to_list(
        self,
        node: Step | AbbreviatedStep | BinaryExpression,
    ) -> list[AbbreviatedStep | Step]:  # type: ignore[return-any]
        result: list[AbbreviatedStep | Step] = []

        if isinstance(node, (Step, AbbreviatedStep)):  # type: ignore[arg-type]
            result.append(node)  # type: ignore[arg-type]

        elif isinstance(node, BinaryExpression):  # type: ignore[misc]
            result.extend(self._ast_to_list(node.left))  # type: ignore[attr-defined,arg-type]
            result.extend(self._ast_to_list(node.right))  # type: ignore[attr-defined,arg-type]

        else:
            raise ShadowstepUnsupportedASTNodeError(str(node))

        return result

    def _collect_predicates(
        self,
        node: AbsolutePath | PredicatedExpression,
    ) -> Iterable[Step | FunctionCall | BinaryExpression | int | float]:
        if isinstance(node, AbsolutePath):
            if node.relative is not None:  # type: ignore[attr-defined]
                yield from self._collect_predicates(node.relative)  # type: ignore[attr-defined,arg-type]
            return

        if isinstance(node, PredicatedExpression):  # type: ignore[arg-type]
            for p in node.predicates:  # type: ignore[attr-defined]
                yield p
            yield from self._collect_predicates(node.base)  # type: ignore[attr-defined,arg-type]
            return

        if isinstance(node, Step):
            for p in node.predicates:  # type: ignore[attr-defined]
                yield p
            return

        if isinstance(node, BinaryExpression):
            yield from self._collect_predicates(node.left)  # type: ignore[attr-defined,arg-type]
            yield from self._collect_predicates(node.right)  # type: ignore[attr-defined,arg-type]
            return

    # ========== predicate handlers (DICT) ==========

    def _apply_predicate_to_dict(  # noqa: PLR0912, PLR0911, C901
        self,
        pred_expr: Step | FunctionCall | BinaryExpression | float,
        out: dict[str, Any],
    ) -> None:
        if isinstance(pred_expr, Step):
            nested = self._build_shadowstep_dict([pred_expr], {})
            for k, v in nested.items():
                out[k] = v  # noqa: PERF403
            return

        if isinstance(pred_expr, FunctionCall):
            attr, kind, value = self._parse_function_predicate(pred_expr)
            if kind == "contains":
                d_attr = _CONTAINS_ATTRS.get(attr)
                if not d_attr:
                    raise ShadowstepContainsNotSupportedError(attr)
                out[d_attr[0].value] = value  # type: ignore[assignment]
                return
            if kind == "starts-with":
                d_attr = _STARTS_ATTRS.get(attr)
                if not d_attr:
                    raise ShadowstepStartsWithNotSupportedError(attr)
                out[d_attr[0].value] = value  # type: ignore[assignment]
                return
            if kind == "matches":
                d_attr = _MATCHES_ATTRS.get(attr)
                if not d_attr:
                    raise ShadowstepMatchesNotSupportedError(attr)
                out[d_attr[0].value] = value  # type: ignore[assignment]
                return
            raise ShadowstepUnsupportedFunctionError(pred_expr.name)  # type: ignore[attr-defined,arg-type]

        if isinstance(pred_expr, (int, float)):  # type: ignore[arg-type]
            out[ShadowstepDictAttribute.INSTANCE.value] = int(pred_expr) - 1
            return

        if isinstance(pred_expr, BinaryExpression):  # type: ignore[misc]
            if (
                pred_expr.op == "="  # type: ignore[attr-defined]
                and isinstance(pred_expr.left, FunctionCall)  # type: ignore[attr-defined]
                and pred_expr.left.name == "position"  # type: ignore[attr-defined]
                and not pred_expr.left.args  # type: ignore[attr-defined]
                and isinstance(pred_expr.right, (int, float))  # type: ignore[arg-type,attr-defined]
            ):
                out[ShadowstepDictAttribute.INDEX.value] = int(pred_expr.right) - 1  # type: ignore[attr-defined]
                return

            if pred_expr.op not in ("=",):  # type: ignore[attr-defined]
                raise ShadowstepUnsupportedComparisonOperatorError(pred_expr.op)  # type: ignore[attr-defined,arg-type]
            attr, value = self._parse_equality_comparison(pred_expr)
            if attr in _EQ_ATTRS:
                out[_EQ_ATTRS[attr][0].value] = value  # type: ignore[assignment]
                return
            if attr in _BOOL_ATTRS:
                out[_BOOL_ATTRS[attr][0].value] = _to_bool(value)  # type: ignore[assignment]
                return
            if attr in _NUM_ATTRS:
                out[_NUM_ATTRS[attr][0].value] = _to_number(value)  # type: ignore[assignment]
                return
            raise ShadowstepUnsupportedAttributeError(attr)

        # attribute presence: [@enabled]
        if (
            isinstance(pred_expr, Step)
            and pred_expr.axis == "@"
            and isinstance(pred_expr.node_test, NameTest)
        ):
            attr = pred_expr.node_test.name
            if attr in _BOOL_ATTRS:
                out[_BOOL_ATTRS[attr][0].value] = True  # type: ignore[assignment]
                return
            raise ShadowstepAttributePresenceNotSupportedError(attr)

        # positional number [3] or something else
        raise ShadowstepUnsupportedPredicateError(pred_expr)

    # ========== predicate handlers (UI SELECTOR) ==========

    def _predicate_to_ui(self, pred_expr: Step | FunctionCall | BinaryExpression | float) -> str:  # noqa: C901, PLR0912, PLR0911
        if isinstance(pred_expr, FunctionCall):
            attr, kind, value = self._parse_function_predicate(pred_expr)
            if kind == "contains":
                u = _CONTAINS_ATTRS.get(attr)
                if not u:
                    raise ShadowstepContainsNotSupportedError(attr)
                return f'.{u[1].value}("{value}")'
            if kind == "starts-with":
                u = _STARTS_ATTRS.get(attr)
                if not u:
                    raise ShadowstepStartsWithNotSupportedError(attr)
                return f'.{u[1].value}("{value}")'
            if kind == "matches":
                u = _MATCHES_ATTRS.get(attr)
                if not u:
                    raise ShadowstepMatchesNotSupportedError(attr)
                return f'.{u[1].value}("{value}")'
            raise ShadowstepUnsupportedFunctionError(kind)

        if isinstance(pred_expr, (int, float)):
            return f".{UiAttribute.INSTANCE.value}({int(pred_expr) - 1})"

        if isinstance(pred_expr, BinaryExpression):
            if (
                pred_expr.op == "="  # type: ignore[attr-defined]
                and isinstance(pred_expr.left, FunctionCall)  # type: ignore[attr-defined]
                and pred_expr.left.name == "position"  # type: ignore[attr-defined]
                and not pred_expr.left.args  # type: ignore[attr-defined]
                and isinstance(pred_expr.right, (int, float))  # type: ignore[attr-defined]
            ):
                return f".{UiAttribute.INDEX.value}({int(pred_expr.right) - 1})"  # type: ignore[attr-defined]
            attr, value = self._parse_equality_comparison(pred_expr)
            if attr in _EQ_ATTRS:
                return f'.{_EQ_ATTRS[attr][1].value}("{value}")'
            if attr in _BOOL_ATTRS:
                return f".{_BOOL_ATTRS[attr][1].value}({str(_to_bool(value)).lower()})"
            if attr in _NUM_ATTRS:
                return f".{_NUM_ATTRS[attr][1].value}({_to_number(value)})"
            raise ShadowstepUnsupportedAttributeError(attr)
        raise ShadowstepUnsupportedPredicateError(str(pred_expr))

    def _parse_function_predicate(self, func: FunctionCall) -> tuple[str, str, Any]:
        name = func.name  # type: ignore[attr-defined]
        if name not in ("contains", "starts-with", "matches"):
            raise ShadowstepUnsupportedFunctionError(str(name))  # type: ignore[arg-type]
        if len(func.args) != FUNCTION_ARGUMENT_COUNT:  # type: ignore[arg-type,attr-defined]
            raise ShadowstepFunctionArgumentCountError(str(name), str(FUNCTION_ARGUMENT_COUNT))
        lhs, rhs = func.args  # type: ignore[attr-defined]
        attr = self._extract_attr_name(lhs)  # type: ignore[arg-type]
        value = self._extract_literal(rhs)  # type: ignore[arg-type]
        return attr, name, value  # type: ignore[return-value]

    def _parse_equality_comparison(self, bexpr: BinaryExpression) -> tuple[str, Any]:
        left_attr = self._maybe_attr(bexpr.left)  # type: ignore[attr-defined,arg-type]
        right_attr = self._maybe_attr(bexpr.right)  # type: ignore[attr-defined,arg-type]
        if left_attr is not None:
            return left_attr, self._extract_literal(bexpr.right)  # type: ignore[attr-defined,arg-type]
        if right_attr is not None:
            return right_attr, self._extract_literal(bexpr.left)  # type: ignore[attr-defined,arg-type]
        if isinstance(bexpr.left, FunctionCall) and bexpr.left.name == "text":  # type: ignore[attr-defined]
            return "text", self._extract_literal(bexpr.right)  # type: ignore[attr-defined,arg-type]
        if isinstance(bexpr.right, FunctionCall) and bexpr.right.name == "text":  # type: ignore[attr-defined]
            return "text", self._extract_literal(bexpr.left)  # type: ignore[attr-defined,arg-type]
        raise ShadowstepEqualityComparisonError

    def _maybe_attr(self, node: Step | FunctionCall | NodeType) -> str | None:  # type: ignore[return-any]
        try:
            return self._extract_attr_name(node)
        except ShadowstepConversionError:
            return None

    @staticmethod
    def _extract_attr_name(node: Step | FunctionCall | NodeType) -> str:
        if isinstance(node, Step) and node.axis == "@" and isinstance(node.node_test, NameTest):  # type: ignore[attr-defined]
            return node.node_test.name  # type: ignore[attr-defined,return-value]
        if isinstance(node, FunctionCall) and node.name == "text":  # type: ignore[attr-defined]
            return "text"
        if isinstance(node, NodeType) and node.name == "text":  # type: ignore[attr-defined]
            return "text"
        raise ShadowstepUnsupportedAttributeExpressionError(str(node))

    @staticmethod
    def _extract_literal(node: str | float | bool | FunctionCall) -> str | int | float | bool:  # noqa: FBT001
        if isinstance(node, (str, int, float, bool)):
            return node
        if isinstance(node, FunctionCall) and node.name in ("true", "false") and not node.args:  # type: ignore[attr-defined]
            return node.name == "true"  # type: ignore[attr-defined]
        raise ShadowstepUnsupportedLiteralError(str(node))

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
            return selector[:i] + selector[i + 1 :]

        if open_count > close_count:
            raise ShadowstepUnbalancedUiSelectorError(selector)

        return selector
