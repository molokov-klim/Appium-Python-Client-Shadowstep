# shadowstep/utils/operations.py

import re
import os
import logging
import serial.tools.list_ports
import shutil
import json
from typing import Optional, Union, Tuple, List, Any

START_DIR = os.getcwd()

# Configure the root logger (basic configuration)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_numeric(variable: str) -> Optional[float]:
    """
    Extract a numeric value from a given string.

    Args:
        variable : str
            The input string from which to extract the numeric value.

    Returns:
        Optional[float]
            The extracted numeric value as a float if found; otherwise, None.
    """
    number: Optional[float] = None  # Initialize the number variable as None
    regex = r'-?\d+(?:,\d+)?'  # Regular expression to find a numeric value
    match = re.search(regex, variable)  # Search for a match in the variable using the regex
    if match:
        # If a match is found, extract the numeric value and convert it to a float
        number = float(match.group().replace(',', '.'))
    return number


def find_latest_folder(path: str) -> Optional[str]:
    """
    Find the latest folder in the specified directory that matches a date-time pattern.

    Args:
        path : str
            The path to the directory in which to search for the latest folder.

    Returns:
        Optional[str]
            The name of the latest folder matching the pattern if found; otherwise, None.
    """
    # Folder name pattern
    pattern = re.compile(r"launch_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}")
    # Retrieve a list of folders in the specified path
    dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    # Filter folders by matching the name pattern
    dirs = [d for d in dirs if pattern.match(d)]
    # Sort folders in reverse order
    dirs.sort(reverse=True)
    if dirs:
        # Latest folder in the sorted list
        latest_dir = dirs[0]
        return str(latest_dir)
    else:
        return None


def get_com() -> Optional[str]:
    """
    Retrieve the number of the first available COM port with a number greater than 10.

    Returns:
        Optional[str]
            The number of the COM port (excluding the "COM" prefix) if found; otherwise, None.
    """
    ports = serial.tools.list_ports.comports()  # Retrieve a list of available COM ports
    for port in ports:
        if int(port.device[3:]) > 10:  # Check if the port number is greater than 10
            try:
                ser = serial.Serial(port.device)  # Attempt to open a serial connection to the port
                ser.close()  # Close the connection
                return port.device[3:]  # Return the port number without the "COM" prefix
            except serial.SerialException:
                pass
    return None  # Return None if no suitable port is found


def copy_file(source: str, destination: str) -> None:
    """
    Copy a file from a source path to a destination path.

    Args:
        source : str
            The path to the source file.
        destination : str
            The path to the destination where the file should be copied.

    Returns:
        None
            This function does not return a value.
    """
    # Debug message with source and destination paths
    logging.debug("copy_file() source %s, destination %s", source, destination)
    try:
        # Copy the file from source to destination
        shutil.copy(source, destination)
        # Debug message indicating successful file copy
        logging.debug("File copied successfully!")
    except IOError as e:
        # Error message if file copy fails
        logging.error("Unable to copy file: %s", e)


def count_currency_numbers(number: int) -> Tuple[int, int, int, int]:
    """
    Calculate the number of bills required to make up a given amount in denominations of 5000, 1000, 500, and 100.

    Args:
        number : int
            The total amount to be divided into bills.

    Returns:
        Tuple[int, int, int, int]
            A tuple representing the count of bills in denominations of 5000, 1000, 500, and 100.
    """
    if number < 100:
        number = 100  # If the amount is less than 100, set it to 100 (important for change calculation)
    count_5000 = number // 5000  # Calculate the number of 5000 denomination bills
    remainder = number % 5000  # Calculate the remainder after 5000 bills
    count_1000 = remainder // 1000  # Calculate the number of 1000 denomination bills
    remainder = remainder % 1000  # Calculate the remainder after 1000 bills
    count_500 = remainder // 500  # Calculate the number of 500 denomination bills
    remainder = remainder % 500  # Calculate the remainder after 500 bills
    count_100 = remainder // 100  # Calculate the number of 100 denomination bills
    return count_5000, count_1000, count_500, count_100  # Return a tuple with the count of each bill denomination


def read_json_file(path: str, filename: str) -> Optional[Any]:
    """
    Read and load data from a JSON file.

    Args:
        path : str
            The path to the directory containing the JSON file, relative to START_DIR.
        filename : str
            The name of the JSON file to read.

    Returns:
        Optional[Any]
            The data loaded from the JSON file if successful; otherwise, None if the file is not found.
    """
    filepath = os.path.join(START_DIR, path, filename)  # Construct the full file path to the JSON file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:  # Open the JSON file for reading
            data = json.load(f)  # Load data from the JSON file
    except FileNotFoundError:
        logging.error("Файл не найден")  # Log an error if the file is not found
        return None
    return data  # Return the data from the JSON file


def str_to_float(number: str) -> float:
    """
    Convert a formatted string representing a monetary value to a float.

    Args:
        number : str
            The string containing a monetary value, which may include commas, spaces, or currency symbols.

    Returns:
        float
            The numeric value as a float.
    """
    # Convert argument to string (in case it is already a string)
    number = str(number)
    # Replace commas with dots, remove currency symbols and spaces, then convert to float
    number = float(number.replace(',', '.').replace('₽', '').replace(' ', ''))
    return number  # Return the amount as a float


def grep_pattern(input_string: str, pattern: str) -> List[str]:
    """
    Search for lines matching a specified pattern within an input string.

    Args:
        input_string : str
            The input string containing multiple lines to be searched.
        pattern : str
            The regular expression pattern to match against each line.

    Returns:
        List[str]
            A list of lines that contain matches for the specified pattern.
    """
    lines = input_string.split('\n')  # Split the input string into lines
    regex = re.compile(pattern)  # Compile the regex pattern
    matched_lines = [line for line in lines if regex.search(line)]  # Filter lines matching the pattern
    return matched_lines


def calculate_rectangle_center(coordinates: Tuple[int, int, int, int]) -> Union[Tuple[int, int], None]:
    """
    Calculate the center coordinates of a rectangle given its boundary coordinates.

    Args:
        coordinates : Tuple[int, int, int, int]
            A tuple representing the left, top, right, and bottom boundaries of the rectangle.

    Returns:
        Union[Tuple[int, int], None]
            A tuple containing the x and y coordinates of the rectangle's center.
    """
    left, top, right, bottom = coordinates
    # Calculate the center coordinates of the rectangle
    x = int((left + right) / 2)
    y = int((top + bottom) / 2)
    return x, y


def dict_matches_subset(big: dict, small: dict) -> bool:
    """
    Check if all key-value pairs from `small` are present in `big`.

    Args:
        big: Full dictionary that may contain extra keys.
        small: Subset dictionary with expected key-value pairs.

    Returns:
        True if all key-value pairs from `small` match those in `big`.
    """
    success = True
    for k, v in small.items():
        actual = big.get(k, '__KEY_NOT_FOUND__')
        if actual != v:
            success = False
    return success