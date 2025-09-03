from __future__ import annotations

import logging
import textwrap
from pathlib import Path

from shadowstep.utils.utils import get_current_func_name


class PageObjectMerger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def merge(self, file1: str, file2: str, output_path: str) -> str:
        """
        merge pages
        """
        self.logger.info(f"{get_current_func_name()}")
        page1 = self.parse(file1)
        page2 = self.parse(file2)
        imports = self.get_imports(page1)
        class_name = self.get_class_name(page1)
        methods1 = self.get_methods(page1)
        methods2 = self.get_methods(page2)
        unique_methods = self.remove_duplicates(methods1, methods2)
        self.write_to_file(filepath=output_path,
                           imports=imports,
                           class_name=class_name,
                           unique_methods=unique_methods)
        return output_path

    def parse(self, file: str | Path) -> str:
        """
        Reads and returns the full content of a Python file as a UTF-8 string.

        Args:
            file (str or Path): Path to the Python file.

        Returns:
            str: Raw content of the file.
        """
        self.logger.debug(f"{get_current_func_name()}")
        try:
            with open(file, encoding="utf-8") as f:
                # self.logger.info(f"{content=}")
                return f.read()
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
        self.logger.debug(f"{get_current_func_name()}")
        lines = page.splitlines()
        import_lines: list[str] = []
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
        self.logger.info(f"{get_current_func_name()}")
        for line in page.splitlines():
            stripped = line.strip()
            self.logger.info(f"{stripped=}")
            if stripped.startswith("class "):
                self.logger.info(f"finded class {stripped=}")
                return line.rstrip()
        raise ValueError("No class definition found in the given source.")

    def get_methods(self, page: str) -> dict[str, str]:
        """
        Извлекает методы и property-блоки через \n\n-разделение, с нормализацией отступов.

        Args:
            page (str): Исходник PageObject-а.

        Returns:
            dict: имя_метода -> текст_метода
        """
        self.logger.debug(f"{get_current_func_name()}")

        methods = {}
        blocks = page.split("\n\n")

        for block in blocks:
            block = textwrap.dedent(block)  # <<< ВАЖНО: УБИРАЕМ ЛИШНИЕ ВЛОЖЕННОСТИ
            stripped = block.strip()

            if not stripped.startswith("def ") and not stripped.startswith("@property") and not stripped.startswith(
                    "@current_page"):
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

    def remove_duplicates(self, methods1: dict[str, str], methods2: dict[str, str]) -> dict[str, str]:
        self.logger.debug(f"{get_current_func_name()}")

        unique_methods = {}

        for name, body in methods1.items():
            unique_methods[name] = body

        for name, body in methods2.items():
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
            unique_methods: dict[str, str],
            encoding: str = "utf-8"
    ) -> None:
        self.logger.debug(f"{get_current_func_name()}")
        lines: list[str] = [imports.strip(), "", "", class_name.strip(), ""]

        for name, body in unique_methods.items():
            if name == "recycler" or name == "is_current_page":
                continue
            clean_body = textwrap.dedent(body)  # убрать вложенные отступы
            method_lines = textwrap.indent(clean_body, "    ")  # вложить внутрь класса
            lines.append(method_lines)
            lines.append("")  # Пустая строка между методами

        if "recycler" in unique_methods:
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
