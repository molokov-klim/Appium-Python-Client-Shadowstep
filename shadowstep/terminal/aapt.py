import logging
import os
import subprocess

logger = logging.getLogger(__name__)


class Aapt:

    @staticmethod
    def get_package_name(path_to_apk: str) -> str:
        """
        Получает название пакета APK-файла с помощью команды aapt.
        Возвращает название пакета.
        """
        logger.info(f"get_package_name() < {path_to_apk}")

        command = ["aapt", "dump", "badging", os.path.join(path_to_apk)]

        try:
            # Выполнение команды и получение вывода
            output: str = str(subprocess.check_output(command)).strip()

            # Извлечение строки, содержащей информацию о пакете
            start_index = output.index("package: name='") + len("package: name='")
            end_index = output.index("'", start_index)

            # Извлекаем название пакета
            package_name = output[start_index:end_index]

        except subprocess.CalledProcessError as e:
            logger.error(f"Could not extract package name. Error: {str(e)}")
            raise  # Выбрасываем исключение дальше

        except ValueError:
            logger.error(f"Could not find package name in the output.")
            raise  # Выбрасываем исключение дальше

        logger.info(f"get_package_name() > {package_name}")
        # Возвращение названия пакета в виде строки
        return package_name

    @staticmethod
    def get_launchable_activity(path_to_apk: str) -> str:
        """
        Получает название запускаемой активности из APK-файла с помощью команды aapt.
        Возвращает название активности в виде строки.
        """
        logger.info(f"get_launchable_activity_from_apk() < {path_to_apk}")

        command = ["aapt", "dump", "badging", path_to_apk]

        try:
            # Выполнение команды и получение вывода
            output = subprocess.check_output(command, universal_newlines=True).strip()

            # Извлечение строки, содержащей информацию о запускаемой активности
            package_line = next(line for line in output.splitlines() if line.startswith("launchable-activity"))

            # Извлечение названия активности из строки
            launchable_activity = package_line.split("'")[1]

            # Возвращение названия активности в виде строки
            logger.info(f"get_launchable_activity_from_apk() > {launchable_activity}")
            return launchable_activity
        except subprocess.CalledProcessError as e:
            logger.error(f"Could not extract launchable activity. Error: {str(e)}")
        except StopIteration:
            logger.error("Could not find 'launchable-activity' line in aapt output.")

        return ""
