# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Abstract Syntax Tree (AST) classes for UiSelector parsing.

This module defines the AST node classes used to represent
parsed UiSelector expressions in a structured format for
further processing and conversion.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MethodCall:
    """Represents a method call in the UiSelector AST.

    This class represents a single method call with its name and arguments
    in the parsed UiSelector expression tree.
    """

    name: str
    args: list[str | int | bool | Selector] = field(default_factory=list)  # type: ignore[var-annotated]


@dataclass
class Selector:
    """Represents a complete UiSelector expression in the AST.

    This class represents a UiSelector expression as a collection of
    method calls that can be chained together to form complex selectors.
    """

    methods: list[MethodCall] = field(default_factory=list)  # type: ignore[var-annotated]
