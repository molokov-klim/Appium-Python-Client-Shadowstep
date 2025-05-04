# shadowstep/terminal/adb.py

import inspect

from appium.webdriver.webdriver import WebDriver
import logging
logger = logging.getLogger(__name__)
import os
import re
import subprocess
import sys
import time
import traceback
from typing import Dict, Union, Tuple, Optional, Any, List

from shadowstep.utils import operations


class Adb:
    """
    A class to interact with Android Debug Bridge (ADB) for device management.
    Use only if Appium server is running locally where the test is being performed
    """

    base = None
    driver = None

    def __init__(self, base: "Shadowstep"):
        self.base: "Shadowstep" = base
        self.driver: WebDriver = base.driver

        
    @staticmethod
    def get_devices() -> Union[List[str], None]:
        """
        Retrieve a list of connected devices via ADB.

        Returns:
            Union[List[str], None]
                A list of connected device identifiers (UUIDs) or None if no devices are found or an error occurs.
        """
        logger.info(f"{inspect.currentframe().f_code.co_name}")

        # Определение команды для выполнения с помощью adb для получения списка устройств
        command = ['adb', 'devices']

        try:
            # Выполнение команды и получение вывода
            response = str(subprocess.check_output(command))

            # Извлечение списка устройств из полученного вывода с использованием регулярных выражений
            devices_list = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+|\d+)', response)

            try:
                # Возвращение первого устройства из списка (UUID подключенного устройства Android)
                logger.info(f"{inspect.currentframe().f_code.co_name} > {devices_list}")
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
        """
        Retrieve the model of the connected device using ADB.

        Args:
            udid : str, optional
                The unique device identifier for the connected device (default is None).
                Not required if only one device is connected.

        Returns:
            Union[str, None]
                The model of the device as a string, or None if an error occurs or the model cannot be retrieved.
        """
        logger.info(f"{inspect.currentframe().f_code.co_name} < {udid}")
        s_udid = f"-s {udid}" if udid else ""
        command = [f"adb {s_udid}", "shell", "getprop", "ro.product.model"]
        try:
            # Выполнение команды и получение вывода
            model = subprocess.check_output(command)
            # Преобразование байтовой строки в обычную строку и удаление пробельных символов и символов перевода строки
            model = model.decode().strip()
            logger.info(f"{inspect.currentframe().f_code.co_name} > {model}")
            return model
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return None

    @staticmethod
    def push(source: str, destination: str, udid: str = None) -> bool:
        """
        Push a file from the local machine to the connected device using ADB.

        Args:
            source : str
                The path to the source file on the local machine.
            destination : str
                The destination path on the connected device (use Linux-style paths).
            udid : str, optional
                The unique device identifier for the connected device (default is None).

        Returns:
            bool
                True if the file was successfully pushed, False otherwise.
        """
        logger.info(f"{inspect.currentframe().f_code.co_name} < {source=}, {destination=}")

        if not os.path.exists(source):
            logger.error(f"Source path does not exist: {source=}")
            return False
        s_udid = f"-s {udid}" if udid else ""
        command = f"adb {s_udid} push {source} {destination}"
        try:
            subprocess.run(command, check=True)
            logger.info(f"{inspect.currentframe().f_code.co_name} > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def pull(source: str, destination: str, udid: str = None) -> bool:
        """
        Pull a file from the connected device to the local machine using ADB.

        Args:
            source : str
                The path to the source file on the connected device (use Linux-style paths).
            destination : str
                The destination path on the local machine.
            udid : str, optional
                The unique device identifier for the connected device (default is None).

        Returns:
            bool
                True if the file was successfully pulled, False otherwise.
        """
        logger.info(f"{inspect.currentframe().f_code.co_name} < {source=}, {destination=}")
        s_udid = f"-s {udid}" if udid else ""
        command = f"adb {s_udid} pull {source} {destination}"
        try:
            subprocess.run(command, check=True)
            logger.info(f"{inspect.currentframe().f_code.co_name} > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def install_app(source: str, udid: str) -> bool:
        """
        Install an application on the connected device using ADB.

        Args:
            source : str
                The path to the APK file on the local machine.
            udid : str
                The unique device identifier for the connected device.

        Returns:
            bool
                True if the application was successfully installed, False otherwise.
        """
        logger.info(f"install() < {source=}")
        s_udid = f"-s {udid}" if udid else ""
        command = f"adb {s_udid} install -r {source}"
        try:
            subprocess.run(command, check=True)
            logger.info("install() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def is_app_installed(package) -> bool:
        """
        Check if the specified package is installed on the connected device.

        Args:
            package : str
                The package name of the application to check.

        Returns:
            bool
                True if the application is installed, False otherwise.
        """
        logger.info(f"is_installed() < {package=}")

        command = "adb shell pm list packages"
        try:
            result = subprocess.check_output(command, shell=True).decode().strip()
            # Фильтруем пакеты
            if any([line.strip().endswith(package) for line in result.splitlines()]):
                logger.info("install() > True")
                return True
            logger.info("install() > False")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def uninstall_app(package: str) -> bool:
        """
        Removes the specified package using ADB.

        Args:
            package : str
                The package name of the application to remove.

        Returns:
            bool
                True, if the application was successfully removed, False otherwise.
        """
        logger.info(f"uninstall_app() < {package=}")

        command = ['adb', 'uninstall', package]
        try:
            subprocess.run(command, check=True)
            logger.info("uninstall_app() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def start_activity(package: str, activity: str) -> bool:
        """
        Starts the specified activity of the application on the device using ADB.

        Args:
            package : str
                The package name of the application containing the activity.
            activity : str
                The name of the activity to be launched.

        Returns:
            bool
                True if the activity was successfully started, False otherwise.
        """
        logger.info(f"start_activity() < {package=}, {activity=}")

        command = ['adb', 'shell', 'am', 'start', '-n', f'{package}/{activity}']
        try:
            subprocess.check_output(command)
            logger.info("start_activity() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def get_current_activity() -> Union[str, None]:
        """
        Retrieve the name of the current activity running on the device.

        Returns:
            Union[str, None]
                The name of the current activity if found, None otherwise.
        """
        # Вывод информации о запуске функции в лог
        logger.info("get_current_activity()")

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
                        logger.info(f"get_current_activity() > {activity_name}")
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
        Retrieve the name of the current application package running on the device.

        Returns:
            Union[str, None]
                The name of the current application package if found, None otherwise.
        """
        # Вывод информации о запуске функции в лог
        logger.info("get_current_app_package()")

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
                        logger.info(f"get_current_app_package() > {package_name}")
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
        Close the specified application on the device using ADB.

        Args:
            package : str
                The package name of the application to be closed.

        Returns:
            bool
                True if the application was successfully closed, False otherwise.
        """
        logger.info(f"close_app() < {package=}")

        command = ['adb', 'shell', 'am', 'force-stop', package]
        try:
            subprocess.run(command, check=True)
            logger.info("close_app() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def reboot_app(package: str, activity: str) -> bool:
        """
        Reboot the specified application by closing and then starting its activity.

        Args:
            package : str
                The package name of the application to be rebooted.
            activity : str
                The name of the activity to be launched after the application is closed.

        Returns:
            bool
                True if the application was successfully rebooted, False otherwise.
        """
        logger.info(f"reboot_app() < {package=}, {activity=}")

        # Закрытие приложения
        if not Adb.close_app(package=package):
            logger.error("reboot_app() > False")
            return False

        # Запуск указанной активности
        if not Adb.start_activity(package=package, activity=activity):
            logger.error("reboot_app() > False")
            return False
        logger.info("reboot_app() > True")
        return True

    @staticmethod
    def press_home() -> bool:
        """
        Simulate pressing the home button on the device using ADB.

        Returns:
            bool
                True if the home button press was successfully executed, False otherwise.
        """
        logger.info("press_home()")

        command = ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_HOME']
        try:
            subprocess.run(command, check=True)
            logger.info("press_home() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def press_back() -> bool:
        """
        Simulate pressing the back button on the device using ADB.

        Returns:
            bool
                True if the back button press was successfully executed, False otherwise.
        """
        logger.info("press_back()")

        command = ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_BACK']
        try:
            subprocess.run(command, check=True)
            logger.info("press_back() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def press_menu() -> bool:
        """
        Simulate pressing the menu button on the device using ADB.

        Returns:
            bool
                True if the menu button press was successfully executed, False otherwise.
        """
        logger.info("press_menu()")

        command = ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_MENU']
        try:
            subprocess.run(command, check=True)
            logger.info("press_menu() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def input_keycode_num_(num: int) -> bool:
        """
        Simulate pressing a number key on the device's numpad using ADB.

        Args:
            num : int
                The number corresponding to the KEYCODE_NUMPAD to press (0-9).

        Returns:
            bool
                True if the key press was successfully executed, False otherwise.
        """
        logger.info(f"input_keycode_num_() < {num=}")

        command = ['adb', 'shell', 'input', 'keyevent', f'KEYCODE_NUMPAD_{num}']
        try:
            subprocess.run(command, check=True)
            logger.info("input_keycode_num_() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def input_keycode(keycode: str) -> bool:
        """
        Simulate pressing a specified key on the device using ADB.

        Args:
            keycode : str
                The keycode corresponding to the key to be pressed.

        Returns:
            bool
                True if the key press was successfully executed, False otherwise.
        """
        logger.info(f"input_keycode() < {keycode=}")

        command = ['adb', 'shell', 'input', 'keyevent', f'{keycode}']
        try:
            subprocess.run(command, check=True)
            logger.info("input_keycode() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def input_by_virtual_keyboard(text: str, keyboard: Dict[str, tuple]) -> bool:
        """
        Input text using a virtual keyboard by tapping on the corresponding coordinates for each character.

        Args:
            text : str
                The text to be inputted.
            keyboard : Dict[str, tuple]
                A dictionary mapping each character to its corresponding coordinates on the virtual keyboard.

        Returns:
            bool
                True if the input was successfully executed, False otherwise.
        """
        logger.info(f"input_by_virtual_keyboard() < {text=}, {keyboard=}")
        try:
            for char in text:
                # Вызываем функцию tap с координатами, соответствующими символу char
                Adb.tap(*keyboard[char])
            logger.info("input_by_virtual_keyboard() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def input_text(text: str) -> bool:
        """
        Input the specified text on the device using ADB.

        Args:
            text : str
                The text to be inputted.

        Returns:
            bool
                True if the text was successfully inputted, False otherwise.
        """
        logger.info(f"input_text() < {text=}")

        # Формируем команду для ввода текста с использованием ADB
        command = ['adb', 'shell', 'input', 'text', text]
        try:
            # Выполняем команду
            subprocess.run(command, check=True)
            logger.info("input_text() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def tap(x: Union[str, int], y: Union[str, int]) -> bool:
        """
        Simulate a tap at the specified screen coordinates on the device using ADB.

        Args:
            x : Union[str, int]
                The x-coordinate of the tap location.
            y : Union[str, int]
                The y-coordinate of the tap location.

        Returns:
            bool
                True if the tap was successfully executed, False otherwise.
        """
        logger.info(f"tap() < {x=}, {y=}")

        # Формируем команду для выполнения нажатия по указанным координатам с использованием ADB
        command = ['adb', 'shell', 'input', 'tap', str(x), str(y)]
        try:
            subprocess.run(command, check=True)
            logger.info("tap() > True")
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
        Simulate a swipe gesture from the starting coordinates to the ending coordinates on the device using ADB.

        Args:
            start_x : Union[str, int]
                The starting x-coordinate of the swipe.
            start_y : Union[str, int]
                The starting y-coordinate of the swipe.
            end_x : Union[str, int]
                The ending x-coordinate of the swipe.
            end_y : Union[str, int]
                The ending y-coordinate of the swipe.
            duration : int, optional
                The duration of the swipe in milliseconds (default is 300).

        Returns:
            bool
                True if the swipe was successfully executed, False otherwise.
        """
        logger.info(f"swipe() < {start_x=}, {start_y=}, {end_x=}, {end_y=}, {duration=}")

        # Формируем команду для выполнения свайпа с использованием ADB
        command = ['adb', 'shell', 'input', 'swipe', str(start_x), str(start_y), str(end_x), str(end_y), str(duration)]
        try:
            # Выполняем команду
            subprocess.run(command, check=True)
            logger.info("swipe() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def check_vpn(ip_address: str = '') -> bool:
        """
        Check if a VPN connection is established with the specified IP address.

        Args:
            ip_address : str, optional
                The IP address to check for an established VPN connection (default is an empty string).

        Returns:
            bool
                True if the VPN connection is established with the specified IP address, False otherwise.
        """
        logger.info(f"check_vpn() < {ip_address=}")

        # Определяем команду в виде строки
        command = "adb shell netstat"
        try:
            # Выполняем команду и получаем вывод
            output = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)

            # Поиск строки
            lines = output.stdout.split("\n")
            for line in lines:
                if "ESTABLISHED" in line and ip_address in line:
                    logger.info("check_vpn() True")
                    return True
            logger.info("check_vpn() False")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def stop_logcat() -> bool:
        """
        Stop the logcat process if it is currently running.

        Returns:
            bool
                True if the logcat process was successfully stopped, False otherwise.
        """
        logger.info("stop_logcat()")
        if Adb.is_process_exist(name='logcat'):
            if Adb.kill_all(name='logcat'):
                logger.info("stop_logcat() > True")
                return True
        logger.error("stop_logcat() > False")
        logger.info("stop_logcat() [Запущенного процесса logcat не обнаружено]")
        return False

    @staticmethod
    def is_process_exist(name) -> bool:
        """
        Check if a process with the specified name is currently running on the device.

        Args:
            name : str
                The name of the process to check for existence.

        Returns:
            bool
                True if the process is running, False otherwise.
        """
        logger.info(f"is_process_exist() < {name=}")
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
                    logger.info("is_process_exist() > True")
                    return True
        # Возврат None, если процесс с заданным именем не найден
        logger.info("is_process_exist() > False")
        return False

    @staticmethod
    def run_background_process(command: str, process: str = "") -> bool:
        """
        Run a specified command as a background process.

        Args:
            command : str
                The command to be executed in the background.
            process : str, optional
                The name of the process to check for existence after starting (default is an empty string).

        Returns:
            bool
                True if the process was successfully started and exists, False otherwise.
        """
        logger.info(f"run_background_process() < {command=}")

        command = f"{command} nohup > /dev/null 2>&1 &"
        try:
            subprocess.Popen(command, stdout=subprocess.DEVNULL)  # не добавлять with
            if process != "":
                time.sleep(1)
                if not Adb.is_process_exist(name=process):
                    return False
            logger.info("run_background_process() > True")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False

    @staticmethod
    def reload_adb() -> bool:
        """
        Reload the ADB server by killing and then starting it again.

        Returns:
            bool
                True if the ADB server was successfully reloaded, False otherwise.
        """
        logger.info("reload_adb()")

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
        logger.info("reload_adb() > True")
        return True

    @staticmethod
    def know_pid(name: str) -> Union[int, None]:
        """
        Retrieve the process ID (PID) of a running process with the specified name.

        Args:
            name : str
                The name of the process to find.

        Returns:
            Union[int, None]
                The PID of the process if found, None otherwise.
        """
        logger.info(f"know_pid() < {name=}")
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
                    logger.info(f"know_pid() > {pid=}")
                    return int(pid)
        # Возврат None, если процесс с заданным именем не найден
        logger.error("know_pid() > None")
        logger.error("know_pid() [Процесс не обнаружен]")
        return None

    @staticmethod
    def kill_by_pid(pid: Union[str, int]) -> bool:
        """
        Terminate a process with the specified PID using ADB.

        Args:
            pid : Union[str, int]
                The process ID of the process to terminate.

        Returns:
            bool
                True if the process was successfully terminated, False otherwise.
        """
        logger.info(f"kill_by_pid() < {pid=}")

        command = ['adb', 'shell', 'kill', '-s', 'SIGINT', str(pid)]
        try:
            subprocess.call(command)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.info("kill_by_pid() > True")
        return True

    @staticmethod
    def kill_by_name(name: str) -> bool:
        """
        Terminate processes with the specified name using ADB.

        Args:
            name : str
                The name of the process to terminate.

        Returns:
            bool
                True if the process was successfully terminated, False otherwise.
        """
        logger.info(f"kill_by_name() < {name=}")

        command = ['adb', 'shell', 'pkill', '-l', 'SIGINT', str(name)]
        try:
            subprocess.call(command)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.info("kill_by_name() > True")
        return True

    @staticmethod
    def kill_all(name: str) -> bool:
        """
        Terminate all processes with the specified name using ADB.

        Args:
            name : str
                The name of the processes to terminate.

        Returns:
            bool
                True if the processes were successfully terminated, False otherwise.
        """
        logger.info(f"kill_all() < {name=}")

        command = ['adb', 'shell', 'pkill', '-f', str(name)]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.info("kill_all() > True")
        return True

    @staticmethod
    def delete_files_from_internal_storage(path: str) -> bool:
        """
        Delete all files from the specified internal storage path on the device using ADB.

        Args:
            path : str
                The path from which to delete files. The path should end with a directory name.

        Returns:
            bool
                True if the files were successfully deleted, False otherwise.
        """
        logger.info(f"delete_files_from_internal_storage() < {path=}")

        command = ['adb', 'shell', 'rm', '-rf', f'{path}*']
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.info("delete_files_from_internal_storage() > True")
        return True

    @staticmethod
    def pull_video(source: str = None, destination: str = ".", delete: bool = True) -> bool:
        """
        Pull videos from the specified source directory on the device to the destination directory on the local machine.

        Args:
            source : str, optional
                The source directory on the device from which to pull videos.
                Defaults to '/sdcard/Movies/' if not provided.
            destination : str, optional
                The destination directory on the local machine where videos will be saved (default is the current directory).
            delete : bool, optional
                Whether to delete the pulled videos from the source directory after pulling (default is True).

        Returns:
            bool
                True if the videos were successfully pulled and deleted (if specified), False otherwise.
        """
        logger.info(f"pull_video() < {destination=}")

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

            logger.info("pull_video() > True")
        return True

    @staticmethod
    def stop_video() -> bool:
        """
        Stop the video recording on the device by terminating the screenrecord process using ADB.

        Returns:
            bool
                True if the video recording was successfully stopped, False otherwise.
        """
        logger.info("stop_video()")

        command = ['adb', 'shell', 'pkill', '-l', 'SIGINT', 'screenrecord']
        try:
            subprocess.call(command)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.info("stop_video() > True")
        return True

    @staticmethod
    def record_video(path: str = "sdcard/Movies/", filename: str = "screenrecord.mp4") -> \
            Union[subprocess.Popen[bytes], subprocess.Popen[Union[Union[str, bytes], Any]]]:
        """
        Start recording a video on the device using ADB.

        Args:
            path : str, optional
                The path where the recorded video will be saved (default is 'sdcard/Movies/').
            filename : str, optional
                The name of the recorded video file (default is 'screenrecord.mp4').

        Returns:
            Union[subprocess.Popen[bytes], subprocess.Popen[Union[Union[str, bytes], Any]]]
                The Popen object representing the running video recording process if successful, None otherwise.
        """
        logger.info(f"record_video() < {filename}")
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
        Start recording a video on the device using ADB.

        Args:
            path : str, optional
                The path where the recorded video will be saved (default is 'sdcard/Movies/').
            filename : str, optional
                The name of the recorded video file (default is 'screenrecord.mp4').

        Returns:
            bool
                True if the video recording was successfully started, False otherwise.
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
        Reboot the device using ADB.

        Returns:
            bool
                True if the reboot command was successfully executed, False otherwise.
        """
        logger.info("reboot()")

        command = ['adb', 'shell', 'reboot']
        try:
            subprocess.call(command)
        except subprocess.CalledProcessError as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
            return False
        logger.info("reboot() > True")
        return True

    @staticmethod
    def get_screen_resolution() -> Union[Tuple[int, int], None]:
        """
        Retrieve the screen resolution of the connected device.

        Returns:
            Union[Tuple[int, int], None]
                A tuple containing the width and height of the screen in pixels if successful, None otherwise.
        """
        logger.info("get_screen_resolution()")

        command = ['adb', 'shell', 'wm', 'size']
        try:
            output = subprocess.check_output(command).decode()
            if "Physical size" in output:
                resolution_str = output.split(":")[1].strip()
                width, height = resolution_str.split("x")
                logger.info(f"get_screen_resolution() > {width=}, {height=}")
                return int(width), int(height)
            logger.error(f"Unexpected output from adb: {output}")
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.error(f"{inspect.currentframe().f_code.co_name} > None")
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(f"{sys.exc_info()[0]}\n{traceback_info}{sys.exc_info()[1]}")
        return None

    def get_packages_list(self) -> list:
        """
        Retrieve a list of all installed packages on the device.

        Returns:
            list
                A list of package names installed on the device.
        """
        packages_raw = self.execute(command="shell pm list packages")
        # Используем регулярное выражение для удаления "package:" из каждой строки
        packages_raw = re.sub(r'package:', '', packages_raw)
        # Разбиваем строки на список и удаляем пустые элементы
        packages_list = [package.strip() for package in packages_raw.split('\n') if package.strip()]
        return packages_list

    @staticmethod
    def execute(command: str):
        """
        Execute a specified ADB command and return the output.

        Args:
            command : str
                The ADB command to execute, excluding the 'adb' prefix.

        Returns:
            str
                The output of the executed command as a string.
        """
        logger.info(f"execute() < {command}")
        execute_command = ['adb', *command.split()]
        return subprocess.check_output(execute_command).decode()
