from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Generator, Tuple
import inspect
import os
import logging
from jinja2 import Environment, FileSystemLoader, Template
from abc import ABC, abstractmethod


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


@dataclass
class PropertyModel:
    """Модель для свойства элемента в Page Object"""
    name: str
    locator: Dict[str, str]
    anchor_name: Optional[str] = None
    depth: int = 0
    base_name: Optional[str] = None
    sibling: bool = False
    via_recycler: bool = False
    summary_id: Optional[Dict[str, str]] = None


@dataclass
class PageObjectModel:
    """Полная модель для генерации Page Object класса"""
    class_name: str
    raw_title: str
    title_locator: Dict[str, str]
    properties: List[PropertyModel] = field(default_factory=list)
    need_recycler: bool = False
    recycler_locator: Optional[Dict[str, str]] = None


class TemplateRenderer(ABC):
    """Абстрактный класс для рендеринга шаблонов"""
    
    @abstractmethod
    def render(self, model: Any, template_name: str) -> str:
        """Рендерит шаблон на основе модели"""
        pass
    
    @abstractmethod
    def save(self, content: str, path: str) -> None:
        """Сохраняет отрендеренный контент в файл"""
        pass


class Jinja2Renderer(TemplateRenderer):
    """Реализация рендеринга на Jinja2"""
    
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
        """Рендерит шаблон на основе модели PageObject"""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
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
        """Сохраняет контент в файл"""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def _pretty_dict(d: dict, base_indent: int = 8) -> str:
        """Форматирует dict в Python-стиле: каждый ключ с новой строки, выровнено по отступу."""
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
    """Фабрика для создания рендереров разных типов"""
    
    @staticmethod
    def create_renderer(renderer_type: str, templates_dir: Optional[str] = None) -> TemplateRenderer:
        """Создает рендерер указанного типа"""
        if renderer_type.lower() == "jinja2":
            if templates_dir is None:
                templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
            return Jinja2Renderer(templates_dir)
        else:
            raise ValueError(f"Unsupported renderer type: {renderer_type}")


class ModelBuilder:
    """Строитель моделей PageObject из данных UI"""
    
    @staticmethod
    def build_from_ui_tree(ui_element_tree, properties: List[Dict], title_locator: Dict[str, str], 
                           recycler_locator: Optional[Dict[str, str]] = None) -> PageObjectModel:
        """Создает модель PageObject из дерева UI элементов"""
        # Конвертация в PropertyModel
        property_models = []
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
        
        # Получение имени и класса
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
    """Высокоуровневый класс для процесса рендеринга Page Objects"""
    
    def __init__(self, renderer_type: str = "jinja2", templates_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.renderer = PageObjectRendererFactory.create_renderer(renderer_type, templates_dir)
    
    def render_and_save(self, model: PageObjectModel, output_path: str, template_name: str = "page_object.py.j2") -> str:
        """Рендерит и сохраняет Page Object класс"""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        
        # Сортировка свойств по имени для красоты
        model.properties.sort(key=lambda p: p.name)
        
        # Рендеринг
        rendered_content = self.renderer.render(model, template_name)
        
        # Сохранение
        self.renderer.save(rendered_content, output_path)
        
        return output_path


def generate(self, ui_element_tree: UiElementNode, output_dir: str, filename_prefix: str = "") -> Tuple[str, str]:
    """
    Генерирует Page Object класс на основе UI-дерева
    """
    self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
    
    # 1. Получаем данные для модели (как в текущей реализации)
    title = self._get_title_property(ui_element_tree)
    name = self._get_name_property(title)
    page_class_name = self._normilize_to_camel_case(name)
    recycler = self._get_recycler_property(ui_element_tree)
    
    # ...дальше собираем свойства как в текущей реализации...
    
    # 2. Строим модель для рендеринга
    model_builder = ModelBuilder()
    model = model_builder.build_from_ui_tree(
        ui_element_tree=title,
        properties=properties,
        title_locator=title_locator,
        recycler_locator=recycler_locator
    )
    
    # 3. Создаем имя файла
    file_name = f"{filename_prefix}{page_class_name.replace('Page', '').lower()}_page.py"
    output_path = os.path.join(output_dir, file_name)
    
    # 4. Рендерим и сохраняем
    renderer = PageObjectRenderer()
    output_path = renderer.render_and_save(model, output_path)
    
    return output_path, page_class_name

