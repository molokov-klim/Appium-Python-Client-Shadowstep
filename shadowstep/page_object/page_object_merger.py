import inspect
import logging
import textwrap
from pathlib import Path

from icecream import ic


class PageObjectMerger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def merge(self, file1: str, file2: str, output_path: str) -> str:
        """
        Производит слияние
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        page1 = self.parse(file1)
        page2 = self.parse(file2)
        imports = self.get_imports(page1)
        class_name = self.get_class_name(page1)
        methods1 = self.get_methods(page1)
        methods2 = self.get_methods(page2)
        # self.logger.info(f"{page1=}")
        # self.logger.info(f"{imports=}")
        # self.logger.info(f"{class_name=}")
        # self.logger.info(f"{methods1=}")
        unique_methods = self.remove_duplicates(methods1, methods2)
        # self.logger.info(f"{unique_methods=}")
        self.write_to_file(filepath=output_path,
                           imports=imports,
                           class_name=class_name,
                           unique_methods=unique_methods)
        return output_path

    def parse(self, file) -> str:
        """
        Reads and returns the full content of a Python file as a UTF-8 string.

        Args:
            file (str or Path): Path to the Python file.

        Returns:
            str: Raw content of the file.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                # self.logger.info(f"{content=}")
                return content
        except Exception as e:
            self.logger.error(f"Failed to read {file}: {e}")
            raise

    def get_imports(self, page: str) -> str:
        """
        Extracts all import statements from the given source code.

        Args:
            page (str): Raw text of a Python file.

        Returns:
            str: All import lines joined by newline.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        lines = page.splitlines()
        import_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                import_lines.append(line)
            elif stripped == "" or stripped.startswith("#"):
                continue
            else:
                # Stop at first non-import, non-comment, non-empty line
                break
        return "\n".join(import_lines)

    def get_class_name(self, page: str) -> str:
        """
        Возвращает строку с первым объявлением класса.

        Args:
            page (str): Исходный код Python-файла.

        Returns:
            str: Полная строка class-определения, включая наследование.

        Raises:
            ValueError: Если не найдено определение класса.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        for line in page.splitlines():
            stripped = line.strip()
            self.logger.info(f"{stripped=}")
            if stripped.startswith("class "):
                self.logger.info(f"finded class {stripped=}")
                return line.rstrip()
        raise ValueError("No class definition found in the given source.")

    def get_methods(self, page: str) -> dict:
        """
        Извлекает методы и property-блоки через \n\n-разделение, с нормализацией отступов.

        Args:
            page (str): Исходник PageObject-а.

        Returns:
            dict: имя_метода -> текст_метода
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        methods = {}
        blocks = page.split("\n\n")

        for block in blocks:
            block = textwrap.dedent(block)  # <<< ВАЖНО: УБИРАЕМ ЛИШНИЕ ВЛОЖЕННОСТИ
            stripped = block.strip()

            if not stripped.startswith("def ") and not stripped.startswith("@property"):
                continue

            lines = block.splitlines()
            name = None

            for i, line in enumerate(lines):
                line_stripped = line.strip()
                if line_stripped.startswith("def "):
                    name = line_stripped.split("def ")[1].split("(")[0].strip()
                    break
                if line_stripped.startswith("@property") and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith("def "):
                        name = next_line.split("def ")[1].split("(")[0].strip()
                        break

            if name:
                methods[name] = block

        return methods

    def remove_duplicates(self, methods1: dict, methods2: dict) -> dict:
        """
        Удаляет дубликаты методов (по имени и тексту), объединяя оба словаря.
        При конфликте (одинаковое имя, разный код) оставляет версию из methods1.

        Args:
            methods1 (dict): Метод-словарь из первого файла.
            methods2 (dict): Метод-словарь из второго файла.

        Returns:
            dict: Объединённый словарь уникальных методов.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        unique_methods = {}

        # Сначала добавим всё из первого файла
        for name, body in methods1.items():
            unique_methods[name] = body

        # Теперь добавляем из второго файла, если:
        # - имя не встречалось
        # - либо тело полностью совпадает (дубликат, но безопасный)
        for name, body in methods2.items():
            # self.logger.info("===================================")
            # self.logger.info(f"{name=}")
            # self.logger.info(f"{body=}")
            # self.logger.info(f"{unique_methods[name].strip()=}")
            # self.logger.info(f"{body.strip()=}")
            # self.logger.info(f"{unique_methods[name].strip() == body.strip()}")
            # self.logger.info("===================================")
            if name not in unique_methods:
                unique_methods[name] = body
            elif unique_methods[name].strip() == body.strip():
                continue  # дубликат — игнорируем
            else:
                self.logger.warning(f"Method conflict on '{name}', skipping version from second file.")

        return unique_methods

    def write_to_file(
            self,
            filepath: str,
            imports: str,
            class_name: str,
            unique_methods: dict,
            encoding: str = "utf-8"
    ) -> None:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        lines = []

        # Импорты
        lines.append(imports.strip())
        lines.append("")  # Пустая строка
        lines.append("")  # Пустая строка

        # Заголовок класса
        lines.append(class_name.strip())
        lines.append("")  # Пустая строка

        # Методы
        for name, body in unique_methods.items():
            if name == "recycler" or name == "is_current_page":
                continue
            clean_body = textwrap.dedent(body)  # убрать вложенные отступы
            method_lines = textwrap.indent(clean_body, "    ")  # вложить внутрь класса
            lines.append(method_lines)
            lines.append("")  # Пустая строка между методами

        if "recycler" in unique_methods.keys():
            body = unique_methods["recycler"]
            clean_body = textwrap.dedent(body)  # убрать вложенные отступы
            method_lines = textwrap.indent(clean_body, "    ")  # вложить внутрь класса
            lines.append(method_lines)
            lines.append("")  # Пустая строка между методами
            body = unique_methods["is_current_page"]
            clean_body = textwrap.dedent(body)  # убрать вложенные отступы
            method_lines = textwrap.indent(clean_body, "    ")  # вложить внутрь класса
            lines.append(method_lines)
            lines.append("")  # Пустая строка между методами

        content = "\n".join(lines).rstrip() + "\n"

        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding=encoding)

