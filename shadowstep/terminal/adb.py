import inspect
import logging
import os
import re
import subprocess
import sys
import time
import traceback
from typing import Dict, Union, Tuple, Optional, Any, List

from shadowstep.utils import operations

logger = logging.getLogger(__name__)


class Adb:

    @staticmethod
    def get_devices() -> Union[List[str], None]:
        logger.debug(f"{inspect.currentframe().f_code.co_name}")

        # Определение команды для выполнения с помощью adb для получения списка устройств
        command = ['adb', 'devices']

        try:
            # Выполнение команды и получение вывода
            response = str(subprocess.check_output(command))

            # Извлечение списка устройств из полученного вывода с использованием регулярных выражений
            devices_list = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+|\d+)', response)

            try:
                # Возвращение первого устройства из списка (UUID подключенного устройства Android)
                logger.debug(f"{inspect.currentframe().f_code.co_name} > {devices_list}")
                return devices_list
            except IndexError:
                logger.error(f"{inspect.currentframe().f_code.co_name} > None")
                logger.error("No connected devices")
                return None
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return None

    @staticmethod
    def get_device_model(udid: str = None) -> Union[str, None]:
        logger.debug(f"{inspect.currentframe().f_code.co_name} < {udid}")
        s_udid = f"-s {udid}" if udid else ""
        command = [f"adb {s_udid}", "shell", "getprop", "ro.product.model"]
        try:
            # Выполнение команды и получение вывода
            model = subprocess.check_output(command)
            # Преобразование байтовой строки в обычную строку и удаление пробельных символов и символов перевода строки
            model = model.decode().strip()
            logger.debug(f"{inspect.currentframe().f_code.co_name} > {model}")
            return model
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return None

    @staticmethod
    def push(source: str, destination: str, udid: str = None) -> bool:
        # USE LINUX STYLE DESTINATION!
        logger.debug(f"{inspect.currentframe().f_code.co_name} < {source=}, {destination=}")

        if not os.path.exists(source):
            logger.error(f"Source path does not exist: {source=}")
            return False
        s_udid = f"-s {udid}" if udid else ""
        command = f"adb {s_udid} push {source} {destination}"
        try:
            subprocess.run(command, check=True)
            logger.debug(f"{inspect.currentframe().f_code.co_name} > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def pull(source: str, destination: str, udid: str = None) -> bool:
        # USE LINUX STYLE SOURCE!
        logger.debug(f"{inspect.currentframe().f_code.co_name} < {source=}, {destination=}")
        s_udid = f"-s {udid}" if udid else ""
        command = f"adb {s_udid} pull {source} {destination}"
        try:
            subprocess.run(command, check=True)
            logger.debug(f"{inspect.currentframe().f_code.co_name} > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def install_app(source: str, udid: str) -> bool:
        logger.debug(f"install() < {source=}")
        s_udid = f"-s {udid}" if udid else ""
        command = f"adb {s_udid} install -r {source}"
        try:
            subprocess.run(command, check=True)
            logger.debug("install() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def is_app_installed(package) -> bool:
        """
        Проверяет, установлен ли пакет.
        """
        logger.debug(f"is_installed() < {package=}")

        command = "adb shell pm list packages"
        try:
            result = subprocess.check_output(command, shell=True).decode().strip()
            # Фильтруем пакеты
            if any([line.strip().endswith(package) for line in result.splitlines()]):
                logger.debug("install() > True")
                return True
            logger.debug("install() > False")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def uninstall_app(package: str) -> bool:
        """
        Удаляет указанный пакет с помощью ADB.

        Аргументы:
            package (str): Название пакета приложения для удаления.

        Возвращает:
            bool: True, если приложение успешно удалено, False в противном случае.
        """
        logger.debug(f"uninstall_app() < {package=}")

        command = ['adb', 'uninstall', package]
        try:
            subprocess.run(command, check=True)
            logger.debug("uninstall_app() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def start_activity(package: str, activity: str) -> bool:
        """
        Запускает активность на подключенном устройстве.

        Аргументы:
            package (str): Название пакета активности.
            activity (str): Название запускаемой активности.

        Возвращает:
            bool: True, если активность была успешно запущена, False в противном случае.
        """
        logger.debug(f"start_activity() < {package=}, {activity=}")

        command = ['adb', 'shell', 'am', 'start', '-n', f'{package}/{activity}']
        try:
            subprocess.check_output(command)
            logger.debug("start_activity() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def get_current_activity() -> Union[str, None]:
        """
        Получает активити текущего запущенного приложения на устройстве с помощью ADB.
        Возвращает имя активити в виде строки или None, если произошла ошибка.

        Возвращает:
            str: Название активити текущего запущенного приложения, либо None, если произошла ошибка.
        """

        # Вывод информации о запуске функции в лог
        logger.debug("get_current_activity()")

        # Команда для ADB для получения информации о текущих окнах
        command = ['adb', 'shell', 'dumpsys', 'window', 'windows']

        try:
            # Выполнение команды и декодирование результата
            result = subprocess.check_output(command, shell=True).decode().strip()

            # Определение паттерна для поиска нужной информации в результатах
            pattern = r'mCurrentFocus|mFocusedApp'

            # Вызов функции grep_pattern для поиска соответствия паттерну
            matched_lines = operations.grep_pattern(input_string=result, pattern=pattern)

            # Если были найдены соответствующие строки
            if matched_lines:
                for line in matched_lines:
                    # Поиск имени активити в строке
                    match = re.search(r'\/([^\/}]*)', line)
                    if match:
                        # Возвращаем найденное значение, исключая '/'
                        activity_name = match.group(1)
                        logger.debug(f"get_current_activity() > {activity_name}")
                        return activity_name

            # Если не удалось найти активити, возвращаем None
            logger.error("get_current_activity() > None")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return None

    @staticmethod
    def get_current_package() -> Union[str, None]:
        """
        Получает пакет текущего запущенного приложения на устройстве с помощью ADB.
        Возвращает имя пакета в виде строки или None, если произошла ошибка.

        Возвращает:
            str: Название пакета текущего запущенного приложения, либо None, если произошла ошибка.
        """
        # Вывод информации о запуске функции в лог
        logger.debug("get_current_app_package()")

        # Команда для ADB для получения информации о текущих окнах
        command = ['adb', 'shell', 'dumpsys', 'window', 'windows']

        try:
            # Выполнение команды и декодирование результата
            result = subprocess.check_output(command, shell=True).decode().strip()

            # Определение паттерна для поиска нужной информации в результатах
            pattern = r'mCurrentFocus|mFocusedApp'

            # Вызов функции grep_pattern для поиска соответствия паттерну
            matched_lines = operations.grep_pattern(input_string=result, pattern=pattern)

            # Если были найдены соответствующие строки
            if matched_lines:
                for line in matched_lines:
                    # Поиск имени пакета в строке
                    match = re.search(r'u0\s(.+?)/', line)
                    if match:
                        # Возвращаем найденное значение
                        package_name = match.group(1)
                        logger.debug(f"get_current_app_package() > {package_name}")
                        return package_name

            # Если не удалось найти имя пакета, возвращаем None
            logger.error("get_current_app_package() > None")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return None

    @staticmethod
    def close_app(package: str) -> bool:
        """
        Принудительно останавливает указанный пакет с помощью ADB.

        Аргументы:
            package (str): Название пакета приложения для закрытия.

        Возвращает:
            bool: True, если приложение успешно закрыто, False в противном случае.
        """
        logger.debug(f"close_app() < {package=}")

        command = ['adb', 'shell', 'am', 'force-stop', package]
        try:
            subprocess.run(command, check=True)
            logger.debug("close_app() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def reboot_app(package: str, activity: str) -> bool:
        """
        Перезапускает приложение, закрывая его и затем запуская указанную активность.

        Аргументы:
            package (str): Название пакета приложения.
            activity (str): Название активности для запуска.

        Возвращает:
            bool: True, если перезапуск приложения выполнен успешно, False в противном случае.
        """
        logger.debug(f"reboot_app() < {package=}, {activity=}")

        # Закрытие приложения
        if not Adb.close_app(package=package):
            logger.error("reboot_app() > False")
            return False

        # Запуск указанной активности
        if not Adb.start_activity(package=package, activity=activity):
            logger.error("reboot_app() > False")
            return False
        logger.debug("reboot_app() > True")
        return True

    @staticmethod
    def press_home() -> bool:
        """
        Отправляет событие нажатия кнопки Home на устройство с помощью ADB.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """
        logger.debug("press_home()")

        command = ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_HOME']
        try:
            subprocess.run(command, check=True)
            logger.debug("press_home() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def press_back() -> bool:
        """
        Отправляет событие нажатия кнопки Back на устройство с помощью ADB.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """

        logger.debug("press_back()")

        command = ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_BACK']
        try:
            subprocess.run(command, check=True)
            logger.debug("press_back() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def press_menu() -> bool:
        """
        Отправляет событие нажатия кнопки Menu на устройство с помощью ADB.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """

        logger.debug("press_menu()")

        command = ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_MENU']
        try:
            subprocess.run(command, check=True)
            logger.debug("press_menu() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def input_keycode_num_(num: int) -> bool:
        """
        Отправляет событие нажатия клавиши с числовым значением на устройство с помощью ADB.
        Допустимые значения: 0-9, ADD, COMMA, DIVIDE, DOT, ENTER, EQUALS

        Аргументы:
            num (int): Числовое значение клавиши для нажатия.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """

        logger.debug(f"input_keycode_num_() < {num=}")

        command = ['adb', 'shell', 'input', 'keyevent', f'KEYCODE_NUMPAD_{num}']
        try:
            subprocess.run(command, check=True)
            logger.debug("input_keycode_num_() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def input_keycode(keycode: str) -> bool:
        """
        Вводит указанный код клавиши на устройстве с помощью ADB.

        Аргументы:
            keycode (str): Код клавиши для ввода.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """

        logger.debug(f"input_keycode() < {keycode=}")

        command = ['adb', 'shell', 'input', 'keyevent', f'{keycode}']
        try:
            subprocess.run(command, check=True)
            logger.debug("input_keycode() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def input_by_virtual_keyboard(text: str, keyboard: Dict[str, tuple]) -> bool:
        """
        Вводит строку символов с помощью виртуальной клавиатуры.

        Аргументы:
            key (str): Строка символов для ввода.
            keyboard (dict): Словарь с маппингом символов на координаты нажатий.

        Возвращает:
            bool: True, если ввод выполнен успешно, False в противном случае.
        """
        logger.debug(f"input_by_virtual_keyboard() < {text=}, {keyboard=}")

        try:
            for char in text:
                # Вызываем функцию tap с координатами, соответствующими символу char
                Adb.tap(*keyboard[char])
            logger.debug("input_by_virtual_keyboard() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def input_text(text: str) -> bool:
        """
        Вводит указанный текст на устройстве с помощью ADB.

        Аргументы:
            text (str): Текст для ввода.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """

        logger.debug(f"input_text() < {text=}")

        # Формируем команду для ввода текста с использованием ADB
        command = ['adb', 'shell', 'input', 'text', text]
        try:
            # Выполняем команду
            subprocess.run(command, check=True)
            logger.debug("input_text() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def tap(x: Union[str, int], y: Union[str, int]) -> bool:
        """
        Выполняет нажатие на указанные координаты на устройстве с помощью ADB.

        Аргументы:
            x: Координата X для нажатия.
            y: Координата Y для нажатия.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """

        logger.debug(f"tap() < {x=}, {y=}")

        # Формируем команду для выполнения нажатия по указанным координатам с использованием ADB
        command = ['adb', 'shell', 'input', 'tap', str(x), str(y)]
        try:
            subprocess.run(command, check=True)
            logger.debug("tap() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def swipe(start_x: Union[str, int], start_y: Union[str, int],
              end_x: Union[str, int], end_y: Union[str, int],
              duration: int = 300) -> bool:
        """
        Выполняет свайп (перетаскивание) с одной точки на экране в другую на устройстве с помощью ADB.

        Аргументы:
            start_x: Координата X начальной точки свайпа.
            start_y: Координата Y начальной точки свайпа.
            end_x: Координата X конечной точки свайпа.
            end_y: Координата Y конечной точки свайпа.
            duration (int): Длительность свайпа в миллисекундах (по умолчанию 300).

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """

        logger.debug(f"swipe() < {start_x=}, {start_y=}, {end_x=}, {end_y=}, {duration=}")

        # Формируем команду для выполнения свайпа с использованием ADB
        command = ['adb', 'shell', 'input', 'swipe', str(start_x), str(start_y), str(end_x), str(end_y), str(duration)]
        try:
            # Выполняем команду
            subprocess.run(command, check=True)
            logger.debug("swipe() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def check_vpn(ip_address: str = '') -> bool:
        """
        Проверяет, активно ли VPN-соединение на устройстве с помощью ADB.

        Аргументы:
            ip_address (str): IP-адрес для проверки VPN-соединения. Если не указан, используется значение из конфигурации.

        Возвращает:
            bool: True, если VPN-соединение активно, False в противном случае.
        """
        logger.debug(f"check_vpn() < {ip_address=}")

        # Определяем команду в виде строки
        command = "adb shell netstat"
        try:
            # Выполняем команду и получаем вывод
            output = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)

            # Поиск строки
            lines = output.stdout.split("\n")
            for line in lines:
                if "ESTABLISHED" in line and ip_address in line:
                    logger.debug("check_vpn() True")
                    return True
            logger.debug("check_vpn() False")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def stop_logcat() -> bool:
        """
        Останавливает выполнение logcat на устройстве с помощью ADB.

        Возвращает:
            bool: True, если выполнение logcat остановлено успешно, False в противном случае.
        """
        logger.debug("stop_logcat()")
        if Adb.is_process_exist(name='logcat'):
            if Adb.kill_all(name='logcat'):
                logger.debug("stop_logcat() > True")
                return True
        logger.error("stop_logcat() > False")
        logger.debug("stop_logcat() [Запущенного процесса logcat не обнаружено]")
        return False

    @staticmethod
    def is_process_exist(name) -> bool:
        """
        Проверяет, запущен ли процесс, используя adb shell ps.

        Параметры:
            name (str): Имя процесса.

        Возвращает:
            bool: True если процесс с указанным именем существует, False в ином случае.
        """
        logger.debug(f"is_process_exist() < {name=}")
        command = ['adb', 'shell', 'ps']
        try:
            processes = subprocess.check_output(command, shell=True).decode().strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        # Разделение вывода на строки и удаление пустых строк
        lines = processes.strip().split('\n')
        # Проход по каждой строке вывода, начиная с 2-й строки, игнорируя заголовки
        for line in lines[1:]:
            # Разделение строки на столбцы по пробелам
            columns = line.split()
            # Проверка, что строка имеет не менее 9 столбцов
            if len(columns) >= 9:
                # Извлечение PID и имени процесса из соответствующих столбцов
                _, process_name = columns[1], columns[8]
                # Сравнение имени процесса с искомым именем
                if name == process_name:
                    logger.debug("is_process_exist() > True")
                    return True
        # Возврат None, если процесс с заданным именем не найден
        logger.debug("is_process_exist() > False")
        return False

    @staticmethod
    def run_background_process(command: str, process: str = "") -> bool:
        """
        Запускает процесс в фоновом режиме на устройстве Android с использованием ADB.

        Аргументы:
            command (str): Команда для выполнения на устройстве.
            process (str): Название процесса, который будет запущен. По умолчанию "".
            Если process == "", то не будет проверяться его запуск в системе.

        Возвращает:
            bool: True, если процесс был успешно запущен, False в противном случае.
        """

        logger.debug(f"run_background_process() < {command=}")

        command = f"{command} nohup > /dev/null 2>&1 &"
        try:
            subprocess.Popen(command, stdout=subprocess.DEVNULL)  # не добавлять with
            if process != "":
                time.sleep(1)
                if not Adb.is_process_exist(name=process):
                    return False
            logger.debug("run_background_process() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def reload_adb() -> bool:
        """
        Перезапускает adb-сервер на устройстве.

        Возвращает:
            bool: True, если adb-сервер успешно перезапущен, False в противном случае.
        """
        logger.debug("reload_adb()")

        try:
            command = ['adb', 'kill-server']
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        # Ожидаем некоторое время перед запуском adb-сервера
        time.sleep(3)
        try:
            command = ['adb', 'start-server']
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.debug("reload_adb() > True")
        return True

    @staticmethod
    def know_pid(name: str) -> Union[int, None]:
        """
        Находит Process ID (PID) процесса по его имени, используя adb shell ps.

        Параметры:
            name (str): Имя процесса, PID которого нужно найти.

        Возвращает:
            Union[int, None]: PID процесса, если он найден, или None, если процесс не найден.
        """

        logger.debug(f"know_pid() < {name=}")
        command = ['adb', 'shell', 'ps']
        try:
            processes = subprocess.check_output(command, shell=True).decode().strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return None
        # Разделение вывода на строки и удаление пустых строк
        lines = processes.strip().split('\n')
        # Проход по каждой строке вывода, начиная с 2-й строки, игнорируя заголовки
        for line in lines[1:]:
            # Разделение строки на столбцы по пробелам
            columns = line.split()
            # Проверка, что строка имеет не менее 9 столбцов
            if len(columns) >= 9:
                # Извлечение PID и имени процесса из соответствующих столбцов
                pid, process_name = columns[1], columns[8]
                # Сравнение имени процесса с искомым именем
                if name == process_name:
                    logger.debug(f"know_pid() > {pid=}")
                    return int(pid)
        # Возврат None, если процесс с заданным именем не найден
        logger.error("know_pid() > None")
        logger.error("know_pid() [Процесс не обнаружен]")
        return None

    @staticmethod
    def kill_by_pid(pid: Union[str, int]) -> bool:
        """
        Отправляет сигнал SIGINT для остановки процесса по указанному идентификатору PID с помощью ADB.

        Аргументы:
            pid (str): Идентификатор PID процесса для остановки.

        Возвращает:
            bool: True, если процесс успешно остановлен, False в противном случае.
        """

        logger.debug(f"kill_by_pid() < {pid=}")

        command = ['adb', 'shell', 'kill', '-s', 'SIGINT', str(pid)]
        try:
            subprocess.call(command)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.debug("kill_by_pid() > True")
        return True

    @staticmethod
    def kill_by_name(name: str) -> bool:
        """
        Останавливает все процессы с указанным именем на устройстве с помощью ADB.

        Аргументы:
            name (str): Имя процесса для остановки.

        Возвращает:
            bool: True, если все процессы успешно остановлены, False в противном случае.
        """

        logger.debug(f"kill_by_name() < {name=}")

        command = ['adb', 'shell', 'pkill', '-l', 'SIGINT', str(name)]
        try:
            subprocess.call(command)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.debug("kill_by_name() > True")
        return True

    @staticmethod
    def kill_all(name: str) -> bool:
        """
        Останавливает все процессы, соответствующие указанному имени, на устройстве с помощью ADB.

        Аргументы:
            name (str): Имя процесса или шаблон имени для остановки.

        Возвращает:
            bool: True, если все процессы успешно остановлены, False в противном случае.
        """

        logger.debug(f"kill_all() < {name=}")

        command = ['adb', 'shell', 'pkill', '-f', str(name)]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.debug("kill_all() > True")
        return True

    @staticmethod
    def delete_files_from_internal_storage(path: str) -> bool:
        """
        Удаляет файлы из внутреннего хранилища устройства с помощью ADB.

        Аргументы:
            path (str): Путь к файлам для удаления.

        Возвращает:
            bool: True, если файлы успешно удалены, False в противном случае.
        """

        logger.debug(f"delete_files_from_internal_storage() < {path=}")

        command = ['adb', 'shell', 'rm', '-rf', f'{path}*']
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.debug("delete_files_from_internal_storage() > True")
        return True

    @staticmethod
    def pull_video(source: str = None, destination: str = ".", delete: bool = True) -> bool:
        """
        Копирует видеофайлы с устройства на компьютер с помощью ADB.

        Аргументы:
            wherefrom (str): Путь к исходным видеофайлам на устройстве.
            destination (str): Путь для сохранения скопированных видеофайлов.
            delete (bool): Удалять исходные видеофайлы с устройства после копирования (по умолчанию True).

        Возвращает:
            bool: True, если видеофайлы успешно скопированы, False в противном случае.
        """

        logger.debug(f"pull_video() < {destination=}")

        if not source:
            source = '/sdcard/Movies/'
        if source.endswith('/'):
            source = source + "/"
        if destination.endswith('/'):
            destination = destination + "/"

        command = ['adb', 'pull', f'{source}', f'{destination}']
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

        if delete:
            command = ['adb', 'shell', 'rm', '-rf', f'{source}*']
            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"{inspect.currentframe().f_code.co_name} > None")
                traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
                logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
                return False

            logger.debug("pull_video() > True")
        return True

    @staticmethod
    def stop_video() -> bool:
        """
        Останавливает запись видео на устройстве с помощью ADB.

        Возвращает:
            bool: True, если запись видео успешно остановлена, False в противном случае.
        """

        logger.debug("stop_video()")

        command = ['adb', 'shell', 'pkill', '-l', 'SIGINT', 'screenrecord']
        try:
            subprocess.call(command)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.debug("stop_video() > True")
        return True

    @staticmethod
    def record_video(path: str = "sdcard/Movies/", filename: str = "screenrecord.mp4") -> \
            Union[subprocess.Popen[bytes], subprocess.Popen[Union[Union[str, bytes], Any]]]:
        """
        Записывает видео на устройстве с помощью ADB.

        Аргументы:
            path (str): Путь куда сохранить файл
            filename (str): Имя файла для сохранения видео.

        Возвращает:
            subprocess.CompletedProcess: Процесс записи видео.
        """

        logger.debug(f"record_video() < {filename}")
        if path.endswith('/'):
            path = path[:-1]
        if filename.endswith('.mp4'):
            filename = filename + ".mp4"

        command = ['adb', 'shell', 'screenrecord', f'{path}/{filename}']
        try:
            # Запускаем команду adb shell screenrecord для начала записи видео
            return subprocess.Popen(command)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return None

    @staticmethod
    def start_record_video(path: str = "sdcard/Movies/", filename: str = "screenrecord.mp4") -> bool:
        """
        Отправляет команду на устройство для начала записи видео.

        Аргументы:
            path (str): Путь куда сохранить файл
            filename (str): Имя файла для сохранения видео.

        Возвращает:
            bool: True, если запись видео успешно начата, False в противном случае.
        """
        if path.endswith('/'):
            path = path[:-1]
        if not filename.endswith('.mp4'):
            filename = filename + ".mp4"

        command = ['adb', 'shell', 'screenrecord', f'{path}/{filename}']
        try:
            # Запускаем команду adb shell screenrecord для начала записи видео
            subprocess.Popen(command)  # не добавлять with
            return True
        except subprocess.CalledProcessError:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def reboot() -> bool:
        """
        Перезагружает устройство с помощью ADB.

        Возвращает:
            bool: True, если перезагрузка успешно запущена, False в противном случае.
        """

        logger.debug("reboot()")

        command = ['adb', 'shell', 'reboot']
        try:
            subprocess.call(command)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.debug("reboot() > True")
        return True

    @staticmethod
    def get_screen_resolution() -> Union[Tuple[int, int], None]:
        """
        Возвращает разрешение экрана устройства с помощью ADB.

        Возвращает:
            tuple[int, int] or None: Кортеж с шириной и высотой экрана в пикселях, или None в случае ошибки.
        """

        logger.debug("get_screen_resolution()")

        command = ['adb', 'shell', 'wm', 'size']
        try:
            output = subprocess.check_output(command).decode()
            if "Physical size" in output:
                resolution_str = output.split(":")[1].strip()
                width, height = resolution_str.split("x")
                logger.debug(f"get_screen_resolution() > {width=}, {height=}")
                return int(width), int(height)
            logger.error(f"Unexpected output from adb: {output}")
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
        return None

    def get_packages_list(self) -> list:
        packages_raw = self.execute(command="shell pm list packages")
        # Используем регулярное выражение для удаления "package:" из каждой строки
        packages_raw = re.sub(r'package:', '', packages_raw)
        # Разбиваем строки на список и удаляем пустые элементы
        packages_list = [package.strip() for package in packages_raw.split('\n') if package.strip()]
        return packages_list

    @staticmethod
    def execute(command: str):
        logger.debug(f"execute() < {command}")
        execute_command = ['adb', *command.split()]
        return subprocess.check_output(execute_command).decode()
