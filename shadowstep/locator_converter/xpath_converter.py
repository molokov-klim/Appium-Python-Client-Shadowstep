# shadowstep/locator_converter/xpath_converter.py
from __future__ import annotations

import logging
import re
from typing import Any, Iterable, List

from eulxml.xpath import parse
from eulxml.xpath.ast import (
    AbsolutePath,
    BinaryExpression,
    FunctionCall,
    NameTest,
    NodeType,
    PredicatedExpression,
    Step, AbbreviatedStep,
)
from icecream import ic

from shadowstep.exceptions.shadowstep_exceptions import ConversionError
from shadowstep.locator_converter.types.shadowstep_dict import DictAttribute
from shadowstep.locator_converter.types.ui_selector import UiAttribute
from utils.utils import get_current_func_name

_BOOL_ATTRS = {
    "checkable": (DictAttribute.CHECKABLE, UiAttribute.CHECKABLE),
    "checked": (DictAttribute.CHECKED, UiAttribute.CHECKED),
    "clickable": (DictAttribute.CLICKABLE, UiAttribute.CLICKABLE),
    "enabled": (DictAttribute.ENABLED, UiAttribute.ENABLED),
    "focusable": (DictAttribute.FOCUSABLE, UiAttribute.FOCUSABLE),
    "focused": (DictAttribute.FOCUSED, UiAttribute.FOCUSED),
    "long-clickable": (DictAttribute.LONG_CLICKABLE, UiAttribute.LONG_CLICKABLE),
    "scrollable": (DictAttribute.SCROLLABLE, UiAttribute.SCROLLABLE),
    "selected": (DictAttribute.SELECTED, UiAttribute.SELECTED),
    "password": (DictAttribute.PASSWORD, UiAttribute.PASSWORD),
}

_NUM_ATTRS = {
    "index": (DictAttribute.INDEX, UiAttribute.INDEX),
    "instance": (DictAttribute.INSTANCE, UiAttribute.INSTANCE),
}

_EQ_ATTRS = {
    # text / description (content-desc)
    "text": (DictAttribute.TEXT, UiAttribute.TEXT),
    "content-desc": (DictAttribute.DESCRIPTION, UiAttribute.DESCRIPTION),
    # resource id / package / class
    "resource-id": (DictAttribute.RESOURCE_ID, UiAttribute.RESOURCE_ID),
    "package": (DictAttribute.PACKAGE_NAME, UiAttribute.PACKAGE_NAME),
    "class": (DictAttribute.CLASS_NAME, UiAttribute.CLASS_NAME),
}

# where contains / starts-with are allowed
_CONTAINS_ATTRS = {
    "text": (DictAttribute.TEXT_CONTAINS, UiAttribute.TEXT_CONTAINS),
    "content-desc": (DictAttribute.DESCRIPTION_CONTAINS, UiAttribute.DESCRIPTION_CONTAINS),
}
_STARTS_ATTRS = {
    "text": (DictAttribute.TEXT_STARTS_WITH, UiAttribute.TEXT_STARTS_WITH),
    "content-desc": (DictAttribute.DESCRIPTION_STARTS_WITH, UiAttribute.DESCRIPTION_STARTS_WITH),
}
# where matches() is allowed
_MATCHES_ATTRS = {
    "text": (DictAttribute.TEXT_MATCHES, UiAttribute.TEXT_MATCHES),
    "content-desc": (DictAttribute.DESCRIPTION_MATCHES, UiAttribute.DESCRIPTION_MATCHES),
    "resource-id": (DictAttribute.RESOURCE_ID_MATCHES, UiAttribute.RESOURCE_ID_MATCHES),
    "package": (DictAttribute.PACKAGE_NAME_MATCHES, UiAttribute.PACKAGE_NAME_MATCHES),
    "class": (DictAttribute.CLASS_NAME_MATCHES, UiAttribute.CLASS_NAME_MATCHES),
}


def _escape_java_string(s: str) -> str:
    # достаточно экранировать обратный слеш и двойную кавычку
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _to_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("true", "1"):
            return True
        if v in ("false", "0"):
            return False
    raise ConversionError(f"Expected boolean literal, got: {val!r}")


def _to_number(val: Any) -> int:
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str) and val.isdigit():
        return int(val)
    raise ConversionError(f"Expected numeric literal, got: {val!r}")


class XPathConverter:
    """
    Convert xpath expression to UiSelector expression or Shadowstep Dict locator
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # ========== validation ==========

    def _validate_xpath(self, xpath_str: str) -> None:
        # запрет логических операторов
        # простая текстовая проверка, затем — парсинг
        if re.search(r"\band\b|\bor\b", xpath_str):
            raise ConversionError("Logical operators (and/or) are not supported")
        try:
            parse(xpath_str)
        except Exception as e:
            raise ConversionError(f"Invalid XPath: {e}")

    # ========== public API ==========

    def xpath_to_dict(self, xpath_str: str) -> dict[str, Any]:
        self._validate_xpath(xpath_str)
        node = parse(xpath_str)
        node_list = self._ast_to_list(node.relative)
        result = self._ast_to_dict(node_list)
        return result

    def xpath_to_ui_selector(self, xpath_str: str) -> str:
        self._validate_xpath(xpath_str)
        node = parse(xpath_str)
        node_list = self._ast_to_list(node.relative)
        result = self._ast_to_ui_selector(node_list)
        return "new UiSelector()" + "".join(result)

    # ========== AST traversal ==========
    
    def _ast_to_list(self, node: Any) -> str:
        ...

    def _ast_to_dict(self, node_list) -> dict[str, Any]:
        shadowstep_dict: dict[str, Any] = {}
        shadowstep_dict = self._build_shadowstep_dict(node_list, shadowstep_dict)
        return shadowstep_dict

    def _build_shadowstep_dict(
            self,
            node_list: list[AbbreviatedStep | Step],
            shadowstep_dict: dict[str, Any],
    ) -> dict[str, Any]:
        if not node_list:
            return shadowstep_dict

        node = node_list[0]

        if isinstance(node, Step):
            # применяем предикаты на текущем шаге
            ic(node)
            for predicate in node.predicates:
                ic(predicate)
                self._apply_predicate_to_dict(predicate, shadowstep_dict)

            i = 1
            # если следующий шаг — ".."
            if i < len(node_list) and isinstance(node_list[i], AbbreviatedStep) and node_list[i].abbr == "..":
                # создаём fromParent
                shadowstep_dict[DictAttribute.FROM_PARENT.value] = self._build_shadowstep_dict(node_list[i + 1:], {})
                return shadowstep_dict

            # иначе это просто childSelector
            if i < len(node_list):
                shadowstep_dict[DictAttribute.CHILD_SELECTOR.value] = self._build_shadowstep_dict(node_list[i:], {})
            return shadowstep_dict

        if isinstance(node, AbbreviatedStep) and node.abbr == "..":
            # считаем подряд идущие ".."
            depth = 1
            while depth < len(node_list) and isinstance(node_list[depth], AbbreviatedStep) and node_list[
                depth].abbr == "..":
                depth += 1

            # разбираем остаток после всех ".."
            rest_dict = self._build_shadowstep_dict(node_list[depth:], {})

            # оборачиваем в fromParent столько раз, сколько ".."
            for _ in range(depth):
                rest_dict = {DictAttribute.FROM_PARENT.value: rest_dict}

            shadowstep_dict.update(rest_dict)
            return shadowstep_dict

        raise ConversionError(f"Unsupported AST node in build: {node!r}")

    def _ast_to_list(self, node) -> list[AbbreviatedStep | Step]:
        result = []

        if isinstance(node, (Step, AbbreviatedStep)):
            result.append(node)

        elif isinstance(node, BinaryExpression):
            # собираем рекурсивно из левой и правой части
            result.extend(self._ast_to_list(node.left))
            result.extend(self._ast_to_list(node.right))

        else:
            raise ConversionError(f"Unsupported AST node: {node!r}")

        return result

    def _collect_predicates(self, node) -> Iterable[Any]:
        """Собрать все выражения-предикаты из дерева.
        Поддерживаем:
          - Step(..., predicates=[...])
          - PredicatedExpression(base, predicates=[...])
          - Рекурсивно обходим бинарные выражения (/, //, |, и т.п.).
        """
        if isinstance(node, AbsolutePath):
            if node.relative is not None:
                yield from self._collect_predicates(node.relative)
            return

        if isinstance(node, PredicatedExpression):
            for p in node.predicates:
                yield p
            # и базу тоже обходим
            yield from self._collect_predicates(node.base)
            return

        if isinstance(node, Step):
            for p in node.predicates:
                yield p
            # node_test предикаты не содержит, но могут быть вложенности справа/слева — нет
            return

        if isinstance(node, BinaryExpression):
            # обходим обе стороны (для / и пр. операторов пути/объединения)
            yield from self._collect_predicates(node.left)
            yield from self._collect_predicates(node.right)
            return

        # прочие узлы (FunctionCall, NameTest, NodeType, ...) предикатов не имеют

    # ========== predicate handlers (DICT) ==========

    def _apply_predicate_to_dict(self, pred_expr, out: dict[str, Any]) -> None:
        if isinstance(pred_expr, Step):
            # конвертируем его так же, как обычный шаг
            nested = self._build_shadowstep_dict([pred_expr], {})
            # приклеиваем результат к target_dict
            for k, v in nested.items():
                # если ключ уже есть, надо вложить через childSelector
                if k in out:
                    target_dict = {"childSelector": out}
                out[k] = v
            return
        
        # функция contains/starts-with/matches(...)
        if isinstance(pred_expr, FunctionCall):
            attr, kind, value = self._parse_function_predicate(pred_expr)
            if kind == "contains":
                d_attr = _CONTAINS_ATTRS.get(attr)
                if not d_attr:
                    raise ConversionError(f"contains() is not supported for @{attr}")
                out[d_attr[0].value] = value
                return
            if kind == "starts-with":
                d_attr = _STARTS_ATTRS.get(attr)
                if not d_attr:
                    raise ConversionError(f"starts-with() is not supported for @{attr}")
                out[d_attr[0].value] = value
                return
            if kind == "matches":
                d_attr = _MATCHES_ATTRS.get(attr)
                if not d_attr:
                    raise ConversionError(f"matches() is not supported for @{attr}")
                out[d_attr[0].value] = value
                return
            raise ConversionError(f"Unsupported function: {pred_expr.name}")

        # позиционный номер напрямую: [3], [6] и т.п.
        if isinstance(pred_expr, (int, float)):
            out[DictAttribute.INSTANCE.value] = int(pred_expr) - 1
            return

        # сравнение (например, @text = 'Hi')
        if isinstance(pred_expr, BinaryExpression):
            if (
                    pred_expr.op == "="
                    and isinstance(pred_expr.left, FunctionCall)
                    and pred_expr.left.name == "position"
                    and not pred_expr.left.args
                    and isinstance(pred_expr.right, (int, float))
            ):
                out[DictAttribute.INDEX.value] = int(pred_expr.right) - 1
                return

            if pred_expr.op not in ("=",):
                raise ConversionError(f"Unsupported comparison operator: {pred_expr.op}")
            attr, value = self._parse_equality_comparison(pred_expr)
            if attr in _EQ_ATTRS:
                out[_EQ_ATTRS[attr][0].value] = value
                return
            if attr in _BOOL_ATTRS:
                out[_BOOL_ATTRS[attr][0].value] = _to_bool(value)
                return
            if attr in _NUM_ATTRS:
                out[_NUM_ATTRS[attr][0].value] = _to_number(value)
                return
            raise ConversionError(f"Unsupported attribute: @{attr}")

        # наличие атрибута: [@enabled]
        if isinstance(pred_expr, Step) and pred_expr.axis == "@" and isinstance(pred_expr.node_test, NameTest):
            attr = pred_expr.node_test.name
            if attr in _BOOL_ATTRS:
                out[_BOOL_ATTRS[attr][0].value] = True
                return
            raise ConversionError(f"Attribute presence predicate not supported for @{attr}")

        # позиционный номер [3] или что-то ещё
        raise ConversionError(f"Unsupported predicate: {pred_expr!r}")

    # ========== predicate handlers (UI SELECTOR) ==========

    def _predicate_to_ui(self, pred_expr) -> str:
        # функции
        if isinstance(pred_expr, FunctionCall):
            attr, kind, value = self._parse_function_predicate(pred_expr)
            if kind == "contains":
                u = _CONTAINS_ATTRS.get(attr)
                if not u:
                    raise ConversionError(f"contains() is not supported for @{attr}")
                return f'.{u[1].value}("{_escape_java_string(str(value))}")'
            if kind == "starts-with":
                u = _STARTS_ATTRS.get(attr)
                if not u:
                    raise ConversionError(f"starts-with() is not supported for @{attr}")
                return f'.{u[1].value}("{_escape_java_string(str(value))}")'
            if kind == "matches":
                u = _MATCHES_ATTRS.get(attr)
                if not u:
                    raise ConversionError(f"matches() is not supported for @{attr}")
                return f'.{u[1].value}("{_escape_java_string(str(value))}")'
            raise ConversionError(f"Unsupported function: {kind}")

        # позиционный номер напрямую: [3], [6]
        if isinstance(pred_expr, (int, float)):
            return f".{UiAttribute.INSTANCE.value}({int(pred_expr) - 1})"

        # сравнение (например, position() = 3)
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
                return f'.{_EQ_ATTRS[attr][1].value}("{_escape_java_string(str(value))}")'
            if attr in _BOOL_ATTRS:
                return f".{_BOOL_ATTRS[attr][1].value}({_to_bool(value)})"
            if attr in _NUM_ATTRS:
                return f".{_NUM_ATTRS[attr][1].value}({_to_number(value)})"
            raise ConversionError(f"Unsupported attribute: @{attr}")

        # наличие атрибута [@enabled]
        if isinstance(pred_expr, Step) and pred_expr.axis == "@" and isinstance(pred_expr.node_test, NameTest):
            attr = pred_expr.node_test.name
            if attr in _BOOL_ATTRS:
                return f".{_BOOL_ATTRS[attr][1].value}(true)"
            raise ConversionError(f"Attribute presence predicate not supported for @{attr}")

        raise ConversionError(f"Unsupported predicate: {pred_expr!r}")

    def _parse_function_predicate(self, func: FunctionCall) -> tuple[str, str, Any]:
        name = func.name
        if name not in ("contains", "starts-with", "matches"):
            raise ConversionError(f"Unsupported function: {name}")
        if len(func.args) != 2:
            raise ConversionError(f"{name}() must have 2 arguments")
        lhs, rhs = func.args
        attr = self._extract_attr_name(lhs)
        value = self._extract_literal(rhs)
        return (attr, name, value)

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
        raise ConversionError("Equality must compare @attribute or text() with a literal")

    def _maybe_attr(self, node) -> str | None:
        try:
            return self._extract_attr_name(node)
        except ConversionError:
            return None

    def _extract_attr_name(self, node) -> str:
        if isinstance(node, Step) and node.axis == "@" and isinstance(node.node_test, NameTest):
            return node.node_test.name
        if isinstance(node, FunctionCall) and node.name == "text":
            return "text"
        if isinstance(node, NodeType) and node.name == "text":
            return "text"
        raise ConversionError(f"Unsupported attribute expression: {node!r}")

    def _extract_literal(self, node) -> Any:
        if isinstance(node, (str, int, float, bool)):
            return node
        if isinstance(node, FunctionCall) and node.name in ("true", "false") and not node.args:
            return node.name == "true"
        raise ConversionError(f"Unsupported literal: {node!r}")
