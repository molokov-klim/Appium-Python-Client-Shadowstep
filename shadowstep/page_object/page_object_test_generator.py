# shadowstep/page_object/page_object_test_generator.py
import re
import ast
from typing import List, Tuple
import inspect
from jinja2 import Environment, FileSystemLoader
import os

import logging


class PageObjectTestGenerator:
    """Генерирует базовый тестовый класс для PageObject.

    Этот класс используется для создания простого теста на основе уже сгенерированного PageObject.
    Он проходит по свойствам страницы и формирует автотест, который проверяет, что элементы отображаются на экране.

    Используется Jinja2-шаблон, тест пишется в файл, например: `tests/pages/test_login_page.py`.

    Стратегия:
        - получает класс или список свойств PageObject;
        - для каждого элемента генерирует проверку `.is_visible()`;
        - сохраняет шаблон в файл (с проверкой на перезапись).

    Пример:
        source = app.driver.page_source
        tree = parser.parse(source)
        path, class_name = POG.generate(ui_element_tree=tree,
                     output_dir="pages")
        test_generator = PageObjectTestGenerator()
        test_path, test_class_name = test_generator.generate_test(input_path=path, class_name=class_name, output_dir="pages")

    Результат генерации:
        imports

        @pytest.fixture()
        def page_object_instance():
            # здесь создаётся объект PageObject
            yield PageObject

        class TestPageExample:
            def test_title(page_object_instance):
                page_object_instance.title.is_visible()


    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=False,
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate_test(self, input_path: str, class_name: str, output_dir: str) -> Tuple[str, str]:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        step = "Извлечение имени модуля"
        self.logger.debug(f"[{step}] started")
        module_path = input_path \
            .replace(os.sep, ".") \
            .removesuffix(".py")

        step = "Извлечение свойств из файла"
        self.logger.debug(f"[{step}] started")
        with open(input_path, "r", encoding="utf-8") as f:
            source = f.read()
        properties = self._extract_properties(source)

        step = "Подготовка данных для шаблона"
        self.logger.debug(f"[{step}] started")
        test_class_name = f"Test{class_name}"
        template = self.env.get_template("page_object_test.py.j2")
        rendered = template.render(
            module_path=module_path,
            class_name=class_name,
            test_class_name=test_class_name,
            properties=properties
        )

        step = "Формирование пути для теста"
        self.logger.debug(f"[{step}] started")
        test_file_name = f"test_{self._camel_to_snake(class_name)}.py"
        test_path = os.path.join(output_dir, test_file_name)

        step = "Запись файла"
        self.logger.debug(f"[{step}] started")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(rendered)

        self.logger.info(f"Generated test → {test_path}")
        return test_path, test_class_name

    def _extract_properties(self, source: str) -> List[str]:
        """Парсит Python AST и вытаскивает список свойств класса."""
        tree = ast.parse(source)
        class_node = next((n for n in tree.body if isinstance(n, ast.ClassDef)), None)
        if not class_node:
            raise ValueError("No class definition found")

        ignore = {"name", "edges", "title", "recycler", "is_current_page"}
        return [
            node.name
            for node in class_node.body
            if isinstance(node, ast.FunctionDef)
               and any(isinstance(d, ast.Name) and d.id == "property" for d in node.decorator_list)
               and node.name not in ignore
        ]

    def _camel_to_snake(self, name: str) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
