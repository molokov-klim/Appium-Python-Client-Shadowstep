# shadowstep/utils/zephyr_uploader.py

import dataclasses
import os
import inspect
from datetime import datetime
from typing import Optional
import logging
logger = logging.getLogger(__name__)
from pytest_adaptavist import MetaBlock



class ZephyrUploader:
    """
    Обёртка для взаимодействия с Zephyr через MetaBlock.
    Позволяет прикреплять файлы и управлять комментариями к шагам тестов.
    """
    def __init__(self):
        self.logger = logger

    def attach_to_step(self, mb: MetaBlock, filepath: str, filename: Optional[str] = None) -> None:
        """
        Прикрепляет файл к конкретному шагу теста в Zephyr.

        Args:
            mb (MetaBlock): MetaBlock с данными Zephyr и текущим шагом.
            filepath (str): Путь к файлу.
            filename (Optional[str]): Имя файла. Если не указано — берётся из пути.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self._attach(
            mb=mb,
            filepath=filepath,
            filename=filename,
            method="add_test_script_attachment",
            step=mb.step
        )

    def attach_to_test_case(self, mb: MetaBlock, filepath: str, filename: Optional[str] = None) -> None:
        """
        Прикрепляет файл к тест-кейсу (вне шага).

        Args:
            mb (MetaBlock): MetaBlock с данными Zephyr.
            filepath (str): Путь к файлу.
            filename (Optional[str]): Имя файла. Если не указано — берётся из пути.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self._attach(
            mb=mb,
            filepath=filepath,
            filename=filename,
            method="add_test_result_attachment"
        )

    def attach_to_test_run(self, mb: MetaBlock, filepath: str, filename: Optional[str] = None) -> None:
        """
        Прикрепляет файл к тест-рану (всему прогону).

        Args:
            mb (MetaBlock): MetaBlock с данными Zephyr.
            filepath (str): Путь к файлу.
            filename (Optional[str]): Имя файла. Если не указано — берётся из пути.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self._attach(
            mb=mb,
            filepath=filepath,
            filename=filename,
            method="add_test_run_attachment"
        )

    def append_script_comment(self, mb, prefix: str, text: str) -> None:
        """
        Добавляет текст в комментарий к шагу test_script, не стирая предыдущий.

        Args:
            mb (MetaBlock): MetaBlock с доступом к Adaptavist и текущим шагом.
            prefix (str): Префикс комментария (например, метка или описание).
            text (str): Текст, который нужно добавить.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        status = mb.data.get("status", "Pass")  # fallback — на всякий случай
        block = f"{'-' * 40} {timestamp} {'-' * 40}\n{prefix}\n\n{status}{text}\n"

        adaptavist = mb.adaptavist.adaptavist

        # Получаем текущий комментарий
        test_result = adaptavist.get_test_result(
            test_run_key=mb.adaptavist.test_run_key,
            test_case_key=mb.adaptavist.test_case_keys[0]
        )

        current_comment = ""
        for step in test_result.get("scriptResults", []):
            if step["index"] == mb.step - 1:
                current_comment = step.get("comment", "")
                break

        new_comment = f"{block}\n{current_comment.strip()}"

        adaptavist.edit_test_script_status(
            test_run_key=mb.adaptavist.test_run_key,
            test_case_key=mb.adaptavist.test_case_keys[0],
            step=mb.step,
            status=status,
            comment=new_comment
        )

    def __attach_image_to_comment(self, mb, filepath: str, filename: Optional[str] = None, label: Optional[str] = None) -> None:
        """
        Прикрепляет изображение к шагу и добавляет его как ссылку в комментарий.

        Args:
            mb (MetaBlock): MetaBlock с данными Zephyr.
            filepath (str): Путь к изображению.
            filename (Optional[str]): Имя файла. Если не указано — берётся из пути.
            label (Optional[str]): Текстовая метка изображения (alt-текст).
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError
        # не работает, надо копать апи жиры
        # filename = filename or os.path.basename(filepath)
        # label = label or "Graph"
        #
        # # Прикрепляем изображение
        # self.logger.info(f"Прикрепляется изображение: {filename}")
        # self.attach_to_test_case(mb=mb, filepath=filepath, filename=filename)
        #
        # # Формируем ссылку на изображение (можно доработать, если знаешь базовый URL JIRA)
        # image_link = f"![{label}]({filename})"
        # self.append_script_comment(mb=mb, prefix=label, text=f"\n{image_link}")


    def _attach(
        self,
        mb: MetaBlock,
        filepath: str,
        filename: Optional[str],
        method: str,
        step: Optional[int] = None
    ) -> None:
        """
        Универсальный метод прикрепления файла через адаптер Adaptavist.

        Args:
            mb (MetaBlock): MetaBlock Zephyr.
            filepath (str): Полный путь к файлу.
            filename (Optional[str]): Имя файла (по умолчанию — из пути).
            method (str): Название метода Adaptavist API (строкой).
            step (Optional[int]): Индекс шага, если применяется (для script_step).

        Raises:
            ValueError: Если указан неизвестный метод прикрепления.
            Exception: При ошибке во время прикрепления файла.
        """
        filename = filename or os.path.basename(filepath)
        log_prefix = inspect.currentframe().f_code.co_name
        self.logger.info(f"{log_prefix}: прикрепляется файл '{filename}' через метод '{method}'")

        try:
            with open(filepath, "rb") as file:
                mb.data["attachment"] = file.read()

            mb.data["filename"] = filename

            adaptavist = mb.adaptavist.adaptavist
            test_run_key = mb.adaptavist.test_run_key
            test_case_key = mb.adaptavist.test_case_keys[0]

            if method == "add_test_script_attachment" and step is not None:
                getattr(adaptavist, method)(
                    test_run_key=test_run_key,
                    test_case_key=test_case_key,
                    step=step,
                    attachment=filepath,
                    filename=filename
                )
            elif method == "add_test_result_attachment":
                adaptavist.add_test_result_attachment(
                    test_run_key=test_run_key,
                    test_case_key=test_case_key,
                    attachment=filepath,
                    filename=filename
                )
            elif method == "add_test_run_attachment":
                adaptavist.add_test_run_attachment(
                    test_run_key=test_run_key,
                    attachment=filepath,
                    filename=filename
                )
            else:
                raise ValueError(f"Неизвестный метод прикрепления: {method}")

            self.logger.info(f"{log_prefix}: успешно прикреплён файл '{filename}'")

        except Exception as e:
            self.logger.error(f"{log_prefix}: ошибка при прикреплении файла '{filename}'")
            self.logger.exception(e)
            raise

