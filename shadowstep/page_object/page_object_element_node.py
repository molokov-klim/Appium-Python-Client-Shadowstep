"""Page object element node models and rendering.

This module provides data models and rendering functionality for
page object generation, including UI element tree representation,
property models, and template-based rendering using Jinja2.
"""
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
    """Represents a UI element in the page object tree structure.

    This class represents a single UI element with its attributes,
    parent-child relationships, and metadata for page object generation.
    """
    id: str
    tag: str
    attrs: dict[str, Any]
    parent: UiElementNode | None
    children: list[UiElementNode] = field(default_factory=list)
    depth: int = 0
    scrollable_parents: list[str] = field(default_factory=list)

    # Fields to identify uniqueness (depth REMOVED)
    _signature_fields: tuple[str, ...] = field(default=("resource-id", "text", "class"), repr=False)

    def walk(self) -> Generator[UiElementNode]:
        """DFS traversal of all nodes in the tree"""
        yield self
        for child in self.children:
            yield from child.walk()

    def find(self, **kwargs: Any) -> list[UiElementNode]:
        """Find nodes by matching attrs"""
        return [el for el in self.walk() if all(el.attrs.get(k) == v for k, v in kwargs.items())]

    def get_attr(self, key: str) -> str:
        """Get attribute value by key.

        Args:
            key: Attribute key to retrieve.

        Returns:
            str: Attribute value or empty string if not found.
        """
        return self.attrs.get(key, "") if self.attrs else ""

    def __repr__(self) -> str:
        """Return string representation of the UI element node.
        
        Returns:
            str: Tree-like string representation showing element hierarchy.
        """
        return self._repr_tree()

    def _repr_tree(self, indent: int = 0) -> str:
        pad = "  " * indent
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
        return "\n".join([line] + [child._repr_tree(indent + 1) for child in self.children])


@dataclass
class PropertyModel:
    """Represents a property in the page object model.

    This class contains information about a UI element property
    including its name, locator, and metadata for page object generation.
    """
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
    """Represents a complete page object model.

    This class contains all the information needed to generate a page object
    including the class name, title, locators, and properties.
    """
    class_name: str
    raw_title: str
    title_locator: dict[str, Any]
    recycler_locator: dict[str, Any] | None
    properties: list[PropertyModel] = field(default_factory=list)
    need_recycler: bool = False


class TemplateRenderer(ABC):
    """Abstract base class for template rendering engines.

    This class defines the interface for template rendering engines
    that can render page object models into code using various
    template systems.
    """

    @abstractmethod
    def render(self, model: Any, template_name: str) -> str:
        """Render a model using the specified template."""
        pass

    @abstractmethod
    def save(self, content: str, path: str) -> None:
        """Save rendered content to a file."""
        pass


class Jinja2Renderer(TemplateRenderer):
    """Jinja2-based template renderer for page object generation.

    This class implements the TemplateRenderer interface using Jinja2
    templating engine to render page object models into Python code.
    """

    def __init__(self, templates_dir: str):
        """Initialize the Jinja2TemplateRenderer.

        Args:
            templates_dir: Directory path containing Jinja2 templates.
        """
        self.logger = logging.getLogger(__name__)
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True,  # noqa: S701
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.env.filters["pretty_dict"] = self._pretty_dict

    def render(self, model: PageObjectModel, template_name: str) -> str:
        """Render page object model using template.

        Args:
            model: Page object model to render.
            template_name: Name of the template to use.

        Returns:
            str: Rendered content as string.
        """
        self.logger.debug(f"{get_current_func_name()}")
        template = self.env.get_template(template_name)

        # Convert dataclass to dict for passing to template
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
        """Save content to file.

        Args:
            content: Content to save.
            path: File path to save to.
        """
        self.logger.debug(f"{get_current_func_name()}")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
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
    """Factory class for creating template renderers.

    This class provides a factory method to create appropriate
    template renderers based on the specified renderer type.
    """

    @staticmethod
    def create_renderer(renderer_type: str) -> TemplateRenderer:
        """Create template renderer by type.

        Args:
            renderer_type: Type of renderer to create.

        Returns:
            TemplateRenderer: Configured template renderer instance.

        Raises:
            ValueError: If renderer type is not supported.
        """
        if renderer_type.lower() == "jinja2":
            templates_dir = os.path.join(os.path.dirname(__file__), "templates")
            return Jinja2Renderer(templates_dir)
        raise ValueError(f"Unsupported renderer type: {renderer_type}")


class ModelBuilder:
    """Builder class for creating page object models.

    This class provides static methods to build page object models
    from UI element trees and property definitions.
    """

    @staticmethod
    def build_from_ui_tree(ui_element_tree: UiElementNode,
                           properties: list[dict[str, Any]],
                           title_locator: dict[str, Any],
                           recycler_locator: dict[str, Any] | None) -> PageObjectModel:
        """Build page object model from UI element tree.

        Args:
            ui_element_tree: Root UI element node.
            properties: List of property definitions.
            title_locator: Title locator configuration.
            recycler_locator: Recycler locator configuration.

        Returns:
            PageObjectModel: Built page object model.
        """
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
    """Main renderer class for page object generation.

    This class provides the main interface for rendering page object
    models into Python code files using the configured template renderer.
    """

    def __init__(self, renderer_type: str = "jinja2"):
        """Initialize the PageObjectRenderer.

        Args:
            renderer_type: Type of template renderer to use (default: "jinja2").
        """
        self.logger = logging.getLogger(__name__)
        self.renderer = PageObjectRendererFactory.create_renderer(renderer_type)

    def render_and_save(self, model: PageObjectModel, output_path: str,
                        template_name: str = "page_object.py.j2") -> str:
        """Render model and save to file.

        Args:
            model: Page object model to render.
            output_path: Path to save the rendered file.
            template_name: Name of the template to use.

        Returns:
            str: Path to the saved file.
        """
        self.logger.debug(f"{get_current_func_name()}")
        model.properties.sort(key=lambda p: p.name)
        rendered_content = self.renderer.render(model, template_name)
        self.renderer.save(rendered_content, output_path)
        return output_path
