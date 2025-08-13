# shadowstep/utils/device_info_parser.py

from pathlib import Path
from typing import List, Dict, Any, Callable, Optional, Set, Tuple, Final

import logging
logger = logging.getLogger(__name__)
import inspect
import os
import re
import time
import matplotlib.pyplot as plt
from datetime import datetime

from matplotlib import cm
from pytest_adaptavist import MetaBlock

from shadowstep.utils.zephyr_uploader import ZephyrUploader


class DeviceInfoAnalyzer:
    def __init__(self, app):
        self.logger = logger
        self.app = app
        self.zephyr = ZephyrUploader()
        self.device_info_filepath = set()
        self.include_packages_in_search = ["ru", "org", "skytech"]
        self.exclude_packages_in_search = ["simalliance"]
        self.battery_pattern = re.compile(r"battery_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.txt")
        self.cpu_pattern = re.compile(r"cpu_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.txt")
        self.mem_pattern = re.compile(r"meminfo_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.txt")
        self.battery_pattern_map = {
            "level": [
                r"\blevel\s*[:：]?\s*(\d+)",
                r"\bbattery\s+level\s*[:：]?\s*(\d+)",
                r"\bbat(?:tery)?[_\-]?level\s*[:：]?\s*(\d+)",
                r"\blevel\s*=\s*(\d+)",
                r"\bbat_lvl\s*[:：=]?\s*(\d+)"
            ],
            "voltage": [
                r"\bvoltage\s*[:：]?\s*(\d+)",
                r"\bbattery\s+voltage\s*[:：]?\s*(\d+)",
                r"\bbat[_\-]?volt(?:age)?\s*[:：=]?\s*(\d+)",
                r"\bvolt\s*[:：=]?\s*(\d+)",
                r"\bvoltage\s*=\s*(\d+)"
            ],
            "temperature": [
                r"\btemperature\s*[:：]?\s*(\d+)",
                r"\bbattery\s+temperature\s*[:：]?\s*(\d+)",
                r"\bbat[_\-]?temp\s*[:：=]?\s*(\d+)",
                r"\btemp\s*[:：=]?\s*(\d+)",
                r"\btemperature\s*=\s*(\d+)"
            ]
        }
        self.cpu_pattern_map = {
            "cpu_usage": [r"(\d+(?:\.\d+)?)%cpu"],
            "user_usage": [r"(\d+(?:\.\d+)?)%user", r"User\s+(\d+)"],
            "nice": [r"(\d+(?:\.\d+)?)%nice", r"Nice\s+(\d+)"],
            "sys": [r"(\d+(?:\.\d+)?)%sys", r"Sys\s+(\d+)"],
            "idle": [r"(\d+(?:\.\d+)?)%idle", r"Idle\s+(\d+)"],
            "iow": [r"(\d+(?:\.\d+)?)%iow", r"IOW\s+(\d+)"],
            "irq": [r"(\d+(?:\.\d+)?)%irq", r"IRQ\s+(\d+)"],
            "sirq": [r"(\d+(?:\.\d+)?)%sirq", r"SIRQ\s+(\d+)"],
            "host": [r"(\d+(?:\.\d+)?)%host"],
        }
        self.mem_pattern_map = {
            "total_ram": [
                r"^\s*total\s+ram\s*[:：]?\s*([\d,]+)K",
                r"^\s*ram\s+total\s*[:：]?\s*([\d,]+)K",
                r"^\s*total\-ram\s*[:：]?\s*([\d,]+)K",
                r"^\s*ram_total\s*[:：]?\s*([\d,]+)K",
                r"^\s*mem_total\s*[:：]?\s*([\d,]+)K",
            ],
            "free_ram": [
                r"^\s*free\s+ram\s*[:：]?\s*([\d,]+)K",
                r"^\s*ram\s+free\s*[:：]?\s*([\d,]+)K",
                r"^\s*free\-ram\s*[:：]?\s*([\d,]+)K",
                r"^\s*ram_free\s*[:：]?\s*([\d,]+)K",
                r"^\s*mem_free\s*[:：]?\s*([\d,]+)K",
            ],
            "used_ram": [
                r"^\s*used\s+ram\s*[:：]?\s*([\d,]+)K",
                r"^\s*ram\s+used\s*[:：]?\s*([\d,]+)K",
                r"^\s*used\-ram\s*[:：]?\s*([\d,]+)K",
                r"^\s*ram_used\s*[:：]?\s*([\d,]+)K",
                r"^\s*mem_used\s*[:：]?\s*([\d,]+)K",
            ],
            "lost_ram": [
                r"^\s*lost\s+ram\s*[:：]?\s*([\d,]+)K",
                r"^\s*ram\s+lost\s*[:：]?\s*([\d,]+)K",
                r"^\s*lost\-ram\s*[:：]?\s*([\d,]+)K",
                r"^\s*ram_lost\s*[:：]?\s*([\d,]+)K",
                r"^\s*mem_lost\s*[:：]?\s*([\d,]+)K",
            ],
            "zram": [
                r"^\s*zram\s*[:：]?\s*([\d,]+)K",
                r"^\s*z\-ram\s*[:：]?\s*([\d,]+)K",
                r"^\s*ram\s+z\s*[:：]?\s*([\d,]+)K",
                r"^\s*zram_used\s*[:：]?\s*([\d,]+)K",
                r"^\s*zram\s+used\s*[:：]?\s*([\d,]+)K",
            ],
        }
        self.battery_plot_keys: Final[List[str]] = ["level", "voltage", "temperature"]
        self.battery_plot_labels: Final[List[str]] = ["Battery Level (%)", "Voltage (mV)", "Temperature (0.1°C)"]
        self.memory_plot_keys: Final[List[str]] = ["total_ram", "free_ram", "used_ram", "lost_ram", "zram"]
        self.memory_plot_labels: Final[List[str]] = ["Total RAM", "Free RAM", "Used RAM", "Lost RAM", "ZRAM"]
        self.cpu_plot_keys: Final[List[str]] = [
            "cpu_usage", "user_usage", "nice", "sys",
            "idle", "iow", "irq", "sirq", "host"
        ]
        self.cpu_plot_labels: Final[List[str]] = [
            "CPU Usage", "User", "Nice", "System",
            "Idle", "IO Wait", "IRQ", "Soft IRQ", "Host"
        ]

    def battery_info(self, input_dir: str, output_dir: str) -> Optional[str]:
        """
        Парсит battery_*.txt и строит график заряда, напряжения и температуры.

        Args:
            input_dir (str): Путь к логам.
            output_dir (str): Куда сохранить график.

        Returns:
            Optional[str]: Путь к изображению или None.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        try:

            def parse_battery(content: str) -> Dict[str, int]:
                return self._parse_by_patterns(self.battery_pattern_map, content)

            data = self._parse_files(input_dir, self.battery_pattern, parse_battery)

            if not data:
                self.logger.info("data is empty")
                return None

            return self._plot_data(
                output_dir,
                data,
                self._battery_plot_fields(),
                title="Battery Statistics Over Time",
                ylabel="Value"
            )

        except Exception as error:
            self.logger.error("Ошибка парсинга battery_info")
            self.logger.exception(error)
            raise

    def cpu_info(self, input_dir: str, output_dir: str) -> Optional[str]:
        """
        Парсит логи CPU и строит график загрузки.

        Args:
            input_dir (str): Директория с логами.
            output_dir (str): Куда сохранить график.

        Returns:
            Optional[str]: Путь к графику или None.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        try:

            def parse_cpu(content: str) -> Dict[str, int]:
                return self._parse_by_patterns(self.cpu_pattern_map, content)

            data = self._parse_files(input_dir, self.cpu_pattern, parse_cpu)

            if not data:
                self.logger.info("data is empty")
                return None

            return self._plot_data(
                output_dir,
                data,
                self._cpu_plot_fields(),
                title="CPU Usage Over Time",
                ylabel="CPU Usage (%)",
                use_subplots=False
            )

        except Exception as error:
            self.logger.error("Ошибка парсинга cpu_info")
            self.logger.exception(error)
            raise

    def mem_info(self, input_dir: str, output_dir: str) -> Optional[str]:
        """
        Парсит логи памяти и строит график использования RAM.

        Args:
            input_dir (str): Директория с логами.
            output_dir (str): Куда сохранить график.

        Returns:
            Optional[str]: Путь к графику или None.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        try:

            def parse_mem(content: str) -> Dict[str, int]:
                return self._parse_by_patterns(self.mem_pattern_map, content)

            data = self._parse_files(input_dir, self.mem_pattern, parse_mem)

            if not data:
                self.logger.info("data is empty")
                return None

            return self._plot_data(
                output_dir,
                data,
                self._memory_plot_fields(),
                title="RAM Over Time",
                ylabel="Memory (KB)",
                use_subplots=False
            )

        except Exception as error:
            self.logger.error(f"Ошибка парсинга mem_info")
            self.logger.exception(error)
            raise

    def generate_and_attach_all_graphs(self, mb: Optional[MetaBlock], output_dir: str) -> None:
        """
        Генерирует графики battery/cpu/mem по всем накопленным логам
        и прикрепляет их к текущему шагу Zephyr.

        Args:
            mb (MetaBlock): Zephyr метаобъект.
            output_dir (str): Куда сохранять графики.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        unique_dirs = self._get_unique_directories(self.device_info_filepath)

        if mb is not None:
            for input_dir in unique_dirs:
                self.logger.info(f"Генерация графиков для директории: {input_dir}")
                self._attach_device_graphs(mb=mb, input_dir=input_dir, output_dir=output_dir)

    def _add_attachment_zephyr(self, mb: Optional[MetaBlock], directory: str, filename: str) -> bool:
        """
        Прикрепляет лог-файл к Zephyr и сохраняет путь в накопитель.

        Args:
            mb (MetaBlock): Zephyr метаблок.
            directory (str): Папка, где лежит лог-файл.
            filename (str): Имя лог-файла.

        Returns:
            bool: True — успех, False — ошибка.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            filepath = os.path.join(directory, filename)
            if mb is not None:
                # Прикрепляем файл
                self.zephyr.attach_to_step(mb=mb, filepath=filepath, filename=filename)
            # Добавляем в накопитель
            self.device_info_filepath.add(filepath)
            return True
        except Exception as error:
            self.logger.error(f"Ошибка {inspect.currentframe().f_code.co_name}")
            self.logger.exception(error)
            return False

    def _battery_plot_fields(self) -> List[Tuple[str, str, str]]:
        return self._assign_colors(self.battery_plot_keys, self.battery_plot_labels)

    def _memory_plot_fields(self) -> List[Tuple[str, str, str]]:
        return self._assign_colors(self.memory_plot_keys, self.memory_plot_labels)

    def _cpu_plot_fields(self) -> List[Tuple[str, str, str]]:
        return self._assign_colors(self.cpu_plot_keys, self.cpu_plot_labels)

    def _parse_files(
            self,
            input_dir: str,
            pattern: re.Pattern,
            parse_function: Callable[[str], Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Парсит файлы в указанной директории, имена которых соответствуют заданному шаблону,
        и возвращает отсортированный по времени список словарей, полученных из содержимого файлов.

        Args:
            input_dir (str): Путь к директории с файлами.
            pattern (re.Pattern): Регулярное выражение для фильтрации и извлечения временной метки из имени файла.
            parse_function (Callable[[str], Dict[str, Any]]): Функция для парсинга содержимого файла.

        Returns:
            List[Dict[str, Any]]: Список словарей, содержащих данные из файлов и ключ 'timestamp'.

        Raises:
            FileNotFoundError: Если указанная директория не существует.
            ValueError: Если парс-функция возвращает не словарь.
            Exception: Любая другая ошибка при чтении файлов или парсинге.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}\n{input_dir=}\n{pattern=}\n{parse_function=}")
        data: List[Dict[str, Any]] = []

        if not os.path.exists(input_dir):
            self.logger.error(f"❌ Директория не существует: {input_dir}")
            raise FileNotFoundError(f"Directory '{input_dir}' does not exist")

        try:
            contents = os.listdir(input_dir)
            if contents:
                self.logger.info("📁 Содержимое директории:")
                for item in contents:
                    self.logger.info(f"  - {item}")
            else:
                self.logger.info("📁 Директория пуста.")
                return None
        except Exception as e:
            self.logger.error(f"⚠️ Ошибка при получении содержимого директории: {e}")
            return None

        for filename in sorted(contents):
            filepath = os.path.join(input_dir, filename)
            self.logger.info(f"Обработка файла: {filename}")
            self.logger.info(f"Путь: {filepath}")

            match = pattern.match(filename)
            self.logger.info(f"Результат pattern.match: {match}")

            if not match:
                self.logger.info(f"Файл не подошел по шаблону: {filename}")
                continue

            try:
                timestamp_str = match.group(1)
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
                self.logger.info(f"timestamp: {timestamp}")

                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.logger.info(f"Прочитано содержимое: {len(content)} символов")

                    parsed_data = parse_function(content)
                    if not isinstance(parsed_data, dict):
                        raise ValueError(f"parse_function must return a dictionary, got {type(parsed_data)}")

                    parsed_data["timestamp"] = timestamp
                    data.append(parsed_data)
                    self.logger.info(f"Добавлены данные: {parsed_data}")

            except Exception as e:
                self.logger.error(f"⚠️ Ошибка при обработке файла '{filename}': {e}")
                continue

        data.sort(key=lambda x: x["timestamp"])
        self.logger.info("Отсортированные данные", data)
        return data

    def _plot_data(
            self,
            output_dir: str,
            data: List[Dict[str, Any]],
            fields: List[Tuple[str, str, str]],
            title: str,
            ylabel: str,
            xlabel: str = "Timestamp",
            use_subplots: bool = True
    ) -> str:
        """
        Строит и сохраняет график на основе предоставленных данных и метрик.

        Args:
            output_dir (str): Папка, в которую будет сохранено изображение.
            data (List[Dict[str, Any]]): Список данных, содержащих ключ 'timestamp' и значения для каждого поля.
            fields (List[Tuple[str, str, str]]): Список кортежей вида (ключ, подпись, цвет), определяющих, что отображать.
            title (str): Заголовок графика.
            ylabel (str): Подпись оси Y.
            xlabel (str, optional): Подпись оси X. По умолчанию "Timestamp".
            use_subplots (bool, optional): Если True — разбивает по подграфикам. Если False — один общий график.

        Returns:
            str: Полный путь к сохранённому изображению.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}\n{output_dir=}\n{data=}\n{fields=}\n{title=}\n"
                         f"{ylabel=}\n{xlabel=}\n")

        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                self.logger.info(f"Created directory: {output_dir}")

            if not data:
                raise ValueError("Data is empty")

            for field, _, _ in fields:
                if field not in data[0]:
                    raise ValueError(f"Field '{field}' not found in data")

            timestamps = [entry["timestamp"] for entry in data]

            if use_subplots:
                fig, axs = plt.subplots(len(fields), 1, figsize=(10, 5 * len(fields)), sharex=True)
                if len(fields) == 1:
                    axs = [axs]

                for ax, (field, label, color) in zip(axs, fields):
                    values = [entry[field] for entry in data]
                    marker = "o" if fields.index((field, label, color)) % 2 == 0 else "x"
                    ax.plot(timestamps, values, label=label, marker=marker, color=color)
                    ax.set_ylabel(label)
                    ax.grid()
                    plt.legend(
                        loc="upper center",
                        bbox_to_anchor=(0.5, -0.15),  # X=по центру, Y=под графиком
                        ncol=3,  # Количество колонок — подбирается под длину
                        frameon=False,  # Убрать рамку (по желанию)
                    )
                    plt.tight_layout(rect=(0, 0.1, 1, 1))  # ↑ увеличиваем нижний отступ

                axs[-1].set_xlabel(xlabel)
                plt.xticks(rotation=45)
                plt.suptitle(title)

            else:
                plt.figure(figsize=(10, 5))
                for field, label, color in fields:
                    values = [entry[field] for entry in data]
                    marker = "o" if fields.index((field, label, color)) % 2 == 0 else "x"
                    plt.plot(timestamps, values, label=label, marker=marker, color=color)

                plt.ylabel(ylabel)
                plt.xlabel(xlabel)
                plt.grid()
                plt.legend(
                    loc="upper center",
                    bbox_to_anchor=(0.5, -0.15),  # X=по центру, Y=под графиком
                    ncol=3,  # Количество колонок — подбирается под длину
                    frameon=False,  # Убрать рамку (по желанию)
                )
                plt.tight_layout(rect=(0, 0.1, 1, 1))  # ↑ увеличиваем нижний отступ
                plt.xticks(rotation=45)
                plt.title(title)

            plt.tight_layout()

            filename = os.path.join(output_dir, f"{title.lower().replace(' ', '_')}_{int(time.time())}.png")
            plt.savefig(filename)
            plt.close()

            self.logger.info(f"Plot saved to {filename}")
            return filename

        except Exception as e:
            self.logger.error(f"Error in _plot_data: {e}")
            plt.close()
            raise

    def _search_float(self, patterns: List[str], content: str) -> float:
        """
        Пытается найти первое совпадение с шаблоном из списка и извлечь из него float-значение.

        Args:
            patterns (List[str]): Список регулярных выражений для поиска числового значения.
            content (str): Текст, в котором выполняется поиск.

        Returns:
            float: Найденное значение, приведённое к float. Если ничего не найдено — возвращает 0.0.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        for pattern in patterns:
            try:
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    # Удаляем запятые (на случай формата 1,234.56) и преобразуем в float
                    return float(match.group(1).replace(',', ''))
            except (AttributeError, ValueError):
                # Пропускаем, если нет совпадения или не удалось преобразовать
                continue

        # Если ничего не найдено — возвращаем 0.0
        return 0.0

    def _assign_colors(self, keys: List[str], labels: List[str]) -> List[Tuple[str, str, str]]:
        """
        Присваивает читаемые цвета из палитры `tab10` для каждого поля.

        Args:
            keys (List[str]): Ключи для данных.
            labels (List[str]): Подписи для легенды.

        Returns:
            List[Tuple[str, str, str]]: (ключ, подпись, цвет).
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        cmap = cm.get_cmap("tab10")
        colors = cmap.colors
        return [(k, l, colors[i % len(colors)]) for i, (k, l) in enumerate(zip(keys, labels))]

    def _parse_by_patterns(self, pattern_map: Dict[str, List[str]], content: str) -> Dict[str, int]:
        """
        Универсальный парсер по карте паттернов. Возвращает значения по каждому ключу.

        Args:
            pattern_map (Dict[str, List[str]]): {ключ: список регулярных выражений}.
            content (str): Содержимое лог-файла.

        Returns:
            Dict[str, int]: Результат для каждого ключа (0, если не найдено).
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        result: Dict[str, int] = {}

        for key, patterns in pattern_map.items():
            raw = self._search_float(patterns, content)
            result[key] = int(raw) if raw else 0

        return result

    def _attach_device_graphs(self, mb: Optional[MetaBlock], input_dir: str, output_dir: str) -> None:
        """
        Генерирует графики (battery, cpu, mem) из логов и прикрепляет их к шагу Zephyr.

        Args:
            mb (MetaBlock): Zephyr метаблок.
            input_dir (str): Папка, где лежат логи.
            output_dir (str): Папка для сохранения графиков.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        generators = [
            ("Battery", self.battery_info),
            ("CPU", self.cpu_info),
            ("Memory", self.mem_info),
        ]

        for label, generator in generators:
            try:
                path = generator(input_dir=input_dir, output_dir=output_dir)
                if path:
                    self.logger.info(f"{label} график сгенерирован: {path}")
                    with open(file=path, mode='rb') as file:
                        self.app.telegram.send_message_document(
                            document=file,
                            caption=f'{label} график сгенерирован: {path}'
                        )
                    if mb is not None:
                        self.zephyr.attach_to_step(mb=mb, filepath=path, filename=os.path.basename(path))
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка при генерации/прикреплении графика {label}: {e}")

    def _get_unique_directories(self, filepaths: Set[str]) -> Set[str]:
        """
        Возвращает уникальные директории из списка путей к файлам и/или директориям.

        Args:
            filepaths (List[str]): Список строковых путей. Каждый путь может быть как файлом, так и директорией.

        Returns:
            Set[str]: Множество абсолютных путей к директориям без дубликатов.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        unique_dirs: Set[str] = set()

        for path_str in filepaths:
            path = Path(path_str)

            # Если путь — директория, добавляем как есть
            if path.is_dir():
                unique_dirs.add(str(path.resolve()))
            else:
                # Если путь — файл, берём его родительскую директорию
                unique_dirs.add(str(path.parent.resolve()))

        return unique_dirs

    def _generate_timestamp(self) -> str:
        """
        Генерирует текущую временную метку в формате, пригодном для использования в имени файла.

        Returns:
            str: Строка формата 'YYYY-MM-DD_HH-MM-SS', представляющая текущую дату и время.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        # Используется для создания уникальных и читаемых имён файлов
        return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    def _build_filename(self, prefix: str, timestamp: str) -> str:
        """
        Формирует имя файла, объединяя префикс и временную метку.

        Args:
            prefix (str): Префикс имени файла, например: 'meminfo', 'battery', 'cpu'.
            timestamp (str): Временная метка, например: '2025-03-31_22-45-00'.

        Returns:
            str: Полное имя файла с расширением .txt.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        return f"{prefix}_{timestamp}.txt"

    def _write_file(self, directory: str, filename: str, content: str) -> str:
        """
        Записывает переданный текст в файл с заданным именем в указанной директории.

        Args:
            directory (str): Целевая директория для записи файла.
            filename (str): Имя создаваемого файла.
            content (str): Строка с текстом, который нужно записать в файл.

        Returns:
            str: Абсолютный путь к созданному файлу.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        filepath = os.path.join(directory, filename)

        # Запись содержимого в файл
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)

        return filepath

    def _save_output(
            self,
            filename_prefix: str,
            adb_command: str,
            adb_args: str,
            directory: str,
            mb: Optional[MetaBlock]
    ) -> None:
        """
        Выполняет ADB-команду, сохраняет результат в файл с временной меткой,
        логирует путь и при наличии Zephyr-модуля прикрепляет файл как вложение.

        Args:
            filename_prefix (str): Префикс для имени файла (например, 'meminfo', 'cpu', 'battery').
            adb_command (str): ADB-команда (например, 'dumpsys', 'getprop').
            adb_args (str): Аргументы команды (например, 'meminfo', 'ro.serialno').
            directory (str): Папка, в которую сохранить результат.
            mb (Optional[MetaBlock]): Метаблок Zephyr для добавления вложения, если есть.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        # Генерируем имя файла по временной метке
        timestamp = self._generate_timestamp()
        filename = self._build_filename(filename_prefix, timestamp)

        # Выполняем команду ADB
        output = self.app.terminal.adb_shell(command=adb_command, args=adb_args)

        # Сохраняем результат в файл
        filepath = self._write_file(directory, filename, output)

        self.logger.info(f"Файл сохранён: {filepath} (команда: {adb_command} {adb_args})")

        # При наличии Zephyr — прикрепляем
        if mb is not None:
            self._add_attachment_zephyr(mb, directory, filename)

    def _save_device_details(self, directory: str, mb: Optional[MetaBlock]) -> None:
        """
        Сохраняет информацию об устройстве и установленных пакетах в текстовый файл.
        При наличии Zephyr MetaBlock прикрепляет файл к шагу Zephyr.

        Args:
            directory (str): Путь к директории для сохранения.
            mb (Optional[MetaBlock]): Объект Zephyr (если прикрепление требуется).
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        timestamp = self._generate_timestamp()
        filename = f"device_info_{timestamp}.txt"

        device_info = self._get_device_properties()
        packages = self._get_filtered_packages()
        processes = self._get_process_list()
        versions = self._get_package_versions(packages)

        self.logger.info(f"Найдено {len(packages)} интересующих пакетов.")

        package_descriptions = [
            self._describe_package(pkg, processes, versions) for pkg in packages
        ]

        filepath = self._write_device_info_file(directory, filename, device_info, package_descriptions)
        self.logger.info(f"Device info written to: {filepath}")

        if mb is not None:
            self.zephyr.attach_to_step(mb=mb, filepath=filepath, filename=filename)

    def _get_device_properties(self) -> Dict[str, str]:
        """
        Получает системные свойства устройства через ADB.

        Returns:
            Dict[str, str]: Словарь с основными свойствами устройства.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        properties = [
            "ro.boot.hardware",
            "ro.product.model",
            "ro.serialno",
            "sys.atol.uin",
            "ro.build.description"
        ]
        return {
            prop: self.app.terminal.adb_shell("getprop", prop).strip()
            for prop in properties
        }

    def _get_process_list(self) -> List[str]:
        """
        Получает список всех процессов на устройстве через один вызов ADB.

        Returns:
            List[str]: Список строк из вывода `adb shell ps`.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        return self.app.terminal.adb_shell("ps").splitlines()

    def _get_package_versions(self, packages: List[str]) -> Dict[str, str]:
        """
        Получает версии пакетов из общего вывода `dumpsys package`.

        Args:
            packages (List[str]): Названия интересующих пакетов.

        Returns:
            Dict[str, str]: {название пакета: версия или 'unknown'}
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        output = self.app.terminal.adb_shell("dumpsys", "package")
        result: Dict[str, str] = {pkg: "unknown" for pkg in packages}
        current_package: Optional[str] = None

        for line in output.splitlines():
            line = line.strip()
            if line.startswith("Package ["):
                match = re.match(r"Package \[(.+?)]", line)
                current_package = match.group(1) if match else None
            elif current_package and current_package in result and "versionName=" in line:
                version = line.split("=", 1)[-1].strip()
                result[current_package] = version
                current_package = None

        return result

    def _describe_package(self, package: str, processes: List[str], versions: Dict[str, str]) -> str:
        """
        Формирует текстовое описание пакета: имя, версия, процессы.

        Args:
            package (str): Название пакета.
            processes (List[str]): Список всех процессов.
            versions (Dict[str, str]): Словарь с версиями пакетов.

        Returns:
            str: Форматированный блок описания.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        version = versions.get(package, "unknown")
        matched = [p for p in processes if package in p]
        proc_info = "\n".join(matched) if matched else "Not running"

        return f"{package}\nVersion: {version}\nProcess info:\n{proc_info}\n"

    def _write_device_info_file(
            self,
            directory: str,
            filename: str,
            device_info: Dict[str, str],
            package_descriptions: List[str]
    ) -> str:
        """
        Записывает собранную информацию в текстовый файл.

        Args:
            directory (str): Папка назначения.
            filename (str): Имя создаваемого файла.
            device_info (Dict[str, str]): Системная информация об устройстве.
            package_descriptions (List[str]): Текстовые блоки с информацией о пакетах.

        Returns:
            str: Полный путь к созданному файлу.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        filepath = os.path.join(directory, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            file.write("Device info:\n")
            for key, value in device_info.items():
                file.write(f"{key}: {value}\n")

            file.write("\nPackages installed on the device:\n")
            file.write("=======================================================\n\n")

            for desc in package_descriptions:
                file.write(desc)
                file.write("=======================================================\n\n")

        return filepath

    def _get_filtered_packages(self) -> List[str]:
        """
        Возвращает список установленных на устройстве пакетов, отфильтрованных по ключевым подстрокам.

        Фильтруются пакеты, содержащие: 'ru', 'org', 'skytech'.
        Исключаются пакеты, содержащие: 'simalliance'.

        Returns:
            List[str]: Отфильтрованные имена пакетов без префикса 'package:'.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        raw = self.app.terminal.adb_shell("pm", "list packages")
        packages = raw.replace("package:", "").splitlines()

        filtered = [
            p for p in packages
            if any(kw in p for kw in self.include_packages_in_search)
               and not any(ex_kw in p for ex_kw in self.exclude_packages_in_search)
        ]

        self.logger.info(f"Отфильтровано {len(filtered)} из {len(packages)} пакетов")
        return filtered

    def _prepare_device_info_directory(self, path: str) -> str:
        """
        Создаёт поддиректорию 'device_info' в указанном пути, если она не существует.
        Возвращает абсолютный путь к ней.

        Args:
            path (str): Базовый путь.

        Returns:
            str: Абсолютный путь к поддиректории device_info.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        directory = os.path.join(path, "device_info")
        os.makedirs(directory, exist_ok=True)
        abs_path = os.path.abspath(directory)
        self.logger.info(f"Device info directory prepared at: {abs_path}")
        return abs_path
