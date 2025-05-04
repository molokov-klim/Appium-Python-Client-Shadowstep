# shadowstep/utils/utils.py

import json
import logging
import math
import os
from collections import Counter
from typing import Tuple


START_DIR = os.getcwd()
PROJECT_ROOT_DIR = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


def write_to_json(path, filename, data):
    try:
        filepath = os.path.join(START_DIR, path, filename)
        with open(filepath, 'x', encoding='utf-8') as f:
            json.dump(data, f)
        return True
    except:
        return False


def remove_keys_from_json_files_recursively(keys: list, path: str):
    """
    Метод рекурсивно проходит по всем вложенным папкам в поисках .json файлов.
    В каждом файле удаляет ключи и значения заданные в параметрах.
    Например:
    keys_to_remove = ["1038",
                      "1040",
                      "1042",
                      "qr",
                      "1021",
                      "1012",
                      "1042",
                      "1077",
                      ]
    path = os.path.join('test_data', 'FFD_1_05', 'cash')
    operations.change_values_in_json_files_recursively(keys=keys_to_remove, path=path)
    """
    # Define the directory to traverse
    root_dir = os.path.join(START_DIR, path)

    # Traverse the directory tree and modify JSON files
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            # Check if the file is a JSON file
            if file.endswith('.json'):
                # Load the JSON data from the file
                file_path = os.path.join(subdir, file)
                logger.debug(f"file_path: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Delete the text-value pair from the JSON data
                for key in keys:
                    if key in data:
                        del data[key]

                # Write the modified JSON data back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f)


def change_values_in_json_files_recursively(keys: dict, path: str):
    """
    Метод рекурсивно проходит по всем вложенным папкам в поисках .json файлов.
    В каждом файле меняет значения у ключей заданных в параметрах.
    Например:
    keys = {
    "1031": 0,
    "1081": 1,
    }
    path = os.path.join('test_data', 'FFD_1_05', 'card')
    operations.change_values_in_json_files_recursively(keys=keys, path=path)
    """
    # Define the directory to traverse
    root_dir = os.path.join(START_DIR, path)

    # Traverse the directory tree and modify JSON files
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            # Check if the file is a JSON file
            if file.endswith('.json'):
                # Load the JSON data from the file
                file_path = os.path.join(subdir, file)
                logger.debug(f"file_path: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Delete the text-value pair from the JSON data
                for key in keys:
                    if key in data:
                        logger.debug(f"data[text]: {data[key]}")
                        logger.debug(f"keys[text]: {keys[key]}")
                        data[key] = keys[key]

                # Write the modified JSON data back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f)


def change_values_in_dict(dict_needs_to_change: dict, changes: dict) -> dict:
    """
    Метод изменяет поданный словарь, согласно поданным параметрам (поиск с заменой).
    Если значение None, то удаляет ключ.
    Возвращает измененный словарь.
    """
    logger.debug("change_values_in_dict()")
    # Delete the text-value pair from the JSON data
    count = 0
    for key in changes:
        if key in dict_needs_to_change:
            if changes[key] is None:
                dict_needs_to_change.pop(key)
            else:
                dict_needs_to_change[key] = changes[key]
            count += 1
    if count > 0:
        logger.debug("change_values_in_dict(): Словарь подготовлен")
        return dict_needs_to_change
    else:
        logger.debug("change_values_in_dict(): В словаре нечего менять")


def find_coordinates_by_vector(width, height, direction: int, distance: int, start_x: int, start_y: int) -> Tuple[int, int]:
    """
    fill me
    """

    # Расчет конечной точки на основе направления и расстояния
    angle_radians = direction * (math.pi / 180)  # Преобразование направления в радианы
    dy = abs(distance * math.cos(angle_radians))
    dx = abs(distance * math.sin(angle_radians))

    if 0 <= direction <= 180:
        x = start_x + dx
    else:
        x = start_x - dx

    if 0 <= direction <= 90 or 270 <= direction <= 360:
        y = start_y - dy
    else:
        y = start_y + dy

    # Обрезка конечной точки до границ экрана
    x2 = (max(0, min(x, width)))
    y2 = (max(0, min(y, height)))

    return x2, y2


def calculate_center_of_coordinates(coordinates: Tuple[int, int, int, int]) -> Tuple[int, int]:
    """
    Вычисляет центр координат для четырех точек.

    Аргументы:
    coordinates (Tuple[int, int, int, int]): Кортеж из четырех целочисленных значений координат: x1, y1, x2, y2.

    Возвращает:
    Tuple[int, int]: Кортеж из двух целочисленных значений, представляющих координаты центра.

    """
    # Распаковываем координаты из кортежа
    x1, y1, x2, y2 = coordinates

    # Вычисляем центр по оси x путем сложения x1 и x2, деленного на 2
    center_x = (x1 + x2) // 2

    # Вычисляем центр по оси y путем сложения y1 и y2, деленного на 2
    center_y = (y1 + y2) // 2

    # Возвращаем кортеж с центральными координатами (center_x, center_y)
    return center_x, center_y


def is_list_in_list(small_list: list, big_list: list) -> bool:
    """
    Метод проверки вхождения одного списка в другой
    """

    big_list_counter = Counter(big_list)
    small_list_counter = Counter(small_list)

    if all(big_list_counter[element] >= small_list_counter[element] for element in small_list):
        return True
    else:
        return False


def get_keys_contains(dictionary: dict, key_fragment: str) -> dict:
    """
    Извлекает все ключи и значения из словаря, ключи которых содержат заданный фрагмент.
    Args:
        dictionary (dict): словарь, для поиска
        key_fragment (str): фрагмент ключа
    Returns:
        dict: словарь содержащий совпадения
    """
    return {key: value for key, value in dictionary.items() if key_fragment in key}



