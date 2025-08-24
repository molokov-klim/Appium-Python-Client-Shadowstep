# shadowstep/page_object/page_object_element_node.py
from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass, field
from typing import Any

from jinja2 import Environment, FileSystemLoader

from shadowstep.utils.utils import get_current_func_name


@dataclass
class UiElementNode:
    id: str
    tag: str
    attrs: dict[str, Any]
    parent: UiElementNode
    children: list[UiElementNode] = field(default_factory=list)
    depth: int = 0
    scrollable_parents: list[str] = field(default_factory=list)

    # Fields to identify uniqueness (depth REMOVED)
    _signature_fields: tuple[str, ...] = field(default=("resource-id", "text", "class"), repr=False)

    def walk(self) -> Generator[UiElementNode, None, None]:
        """DFS traversal of all nodes in the tree"""
        yield self
        for child in self.children:
            yield from child.walk()

    def find(self, **kwargs: Any) -> list[UiElementNode]:
        """Find nodes by matching attrs"""
        return [el for el in self.walk() if all(el.attrs.get(k) == v for k, v in kwargs.items())]

    def get_attr(self, key: str) -> str:
        return self.attrs.get(key, '') if self.attrs else ''

    def __repr__(self) -> str:
        return self._repr_tree()

    def _repr_tree(self, indent: int = 0) -> str:
        pad = '  ' * indent
        parent_id = self.parent.id if self.parent else None
        line = (
            f"{pad}- id={self.id}"
            f" | tag='{self.tag}'"
            f" | text='{self.get_attr('text')}'"
            f" | resource-id='{self.get_attr('resource-id')}'"
            f" | parent_id='{parent_id}'"
            f" | depth='{self.depth}'"
            f" | scrollable_parents='{self.scrollable_parents}'"
            f" | attrs='{self.attrs}'"
        )
        if not self.children:
            return line
        return '\n'.join([line] + [child._repr_tree(indent + 1) for child in self.children])


@dataclass
class PropertyModel:
    name: str
    locator: dict[str, Any]
    anchor_name: str | None
    base_name: str | None
    summary_id: dict[str, Any] | None
    depth: int = 0
    sibling: bool = False
    via_recycler: bool = False


@dataclass
class PageObjectModel:
    class_name: str
    raw_title: str
    title_locator: dict[str, Any]
    recycler_locator: dict[str, Any] | None
    properties: list[PropertyModel] = field(default_factory=list)
    need_recycler: bool = False


class TemplateRenderer(ABC):

    @abstractmethod
    def render(self, model: Any, template_name: str) -> str:
        pass

    @abstractmethod
    def save(self, content: str, path: str) -> None:
        pass


class Jinja2Renderer(TemplateRenderer):

    def __init__(self, templates_dir: str):
        self.logger = logging.getLogger(__name__)
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=False,
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.env.filters['pretty_dict'] = self._pretty_dict

    def render(self, model: PageObjectModel, template_name: str) -> str:
        self.logger.debug(f"{get_current_func_name()}")
        template = self.env.get_template(template_name)

        # Конвертируем dataclass в словарь для передачи в шаблон
        model_dict = {
            "class_name": model.class_name,
            "raw_title": model.raw_title,
            "title_locator": model.title_locator,
            "properties": model.properties,
            "need_recycler": model.need_recycler,
            "recycler_locator": model.recycler_locator,
        }

        return template.render(**model_dict)

    def save(self, content: str, path: str) -> None:
        self.logger.debug(f"{get_current_func_name()}")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def _pretty_dict(d: dict[str, Any], base_indent: int = 8) -> str:
        lines = ["{"]
        indent = " " * base_indent
        for i, (k, v) in enumerate(d.items()):
            line = f"{indent!s}{repr(k)}: {repr(v)}"
            if i < len(d) - 1:
                line += ","
            lines.append(line)
        lines.append(" " * (base_indent - 4) + "}")
        return "\n".join(lines)


class PageObjectRendererFactory:

    @staticmethod
    def create_renderer(renderer_type: str) -> TemplateRenderer:
        if renderer_type.lower() == "jinja2":
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
            return Jinja2Renderer(templates_dir)
        else:
            raise ValueError(f"Unsupported renderer type: {renderer_type}")


class ModelBuilder:

    @staticmethod
    def build_from_ui_tree(ui_element_tree: UiElementNode,
                           properties: list[dict[str, Any]],
                           title_locator: dict[str, Any],
                           recycler_locator: dict[str, Any] | None) -> PageObjectModel:
        property_models: list[PropertyModel] = []
        for prop in properties:
            property_models.append(PropertyModel(
                name=prop["name"],
                locator=prop["locator"],
                anchor_name=prop.get("anchor_name"),
                depth=prop.get("depth", 0),
                base_name=prop.get("base_name"),
                sibling=prop.get("sibling", False),
                via_recycler=prop.get("via_recycler", False),
                summary_id=prop.get("summary_id")
            ))

        raw_title = ui_element_tree.attrs.get("text") or ui_element_tree.attrs.get("content-desc") or ""
        class_name = f"Page{raw_title.replace(' ', '')}"

        return PageObjectModel(
            class_name=class_name,
            raw_title=raw_title,
            title_locator=title_locator,
            properties=property_models,
            need_recycler=recycler_locator is not None,
            recycler_locator=recycler_locator
        )


class PageObjectRenderer:

    def __init__(self, renderer_type: str = "jinja2"):
        self.logger = logging.getLogger(__name__)
        self.renderer = PageObjectRendererFactory.create_renderer(renderer_type)

    def render_and_save(self, model: PageObjectModel, output_path: str,
                        template_name: str = "page_object.py.j2") -> str:
        self.logger.debug(f"{get_current_func_name()}")
        model.properties.sort(key=lambda p: p.name)
        rendered_content = self.renderer.render(model, template_name)
        self.renderer.save(rendered_content, output_path)
        return output_path
