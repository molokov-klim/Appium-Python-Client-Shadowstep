from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Generator


@dataclass
class UiElementNode:
    id: Optional[str] = None
    tag: Optional[str] = None
    attrs: Optional[Dict[str, Any]] = None
    parent: Optional['UiElementNode'] = None
    children: List['UiElementNode'] = field(default_factory=list)

    depth: int = 0
    scrollable_parents: List[str] = field(default_factory=list)

    def walk(self) -> Generator['UiElementNode', None, None]:
        yield self
        for child in self.children:
            yield from child.walk()

    def find(self, **kwargs) -> List['UiElementNode']:
        return [el for el in self.walk() if all(el.attrs.get(k) == v for k, v in kwargs.items())]

    def __repr__(self) -> str:
        return self._repr_tree()

    def _repr_tree(self, indent: int = 0) -> str:
        pad = '  ' * indent
        parent_id = self.parent.id if self.parent else None
        line = (
            f"{pad}- id={self.id}"
            f" | tag='{self.tag}'"
            f" | text='{self.attrs.get('text', '')}'"
            f" | resource-id='{self.attrs.get('resource-id', '')}'"
            f" | parent_id='{parent_id}'"
            f" | depth='{self.depth}'"
            f" | scrollable_parents='{self.scrollable_parents}'"
            f" | attrs='{self.attrs}'"
        )
        if not self.children:
            return line
        return '\n'.join([line] + [child._repr_tree(indent + 1) for child in self.children])

