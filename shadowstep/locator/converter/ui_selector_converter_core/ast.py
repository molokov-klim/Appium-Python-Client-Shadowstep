from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MethodCall:
    name: str
    args: list[str | int | bool | Selector] = field(default_factory=list)

@dataclass
class Selector:
    methods: list[MethodCall] = field(default_factory=list)
