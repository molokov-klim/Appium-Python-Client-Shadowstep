# shadowstep/utils/utils.py
import inspect
import logging
import math
import os
import re

START_DIR = os.getcwd()
PROJECT_ROOT_DIR = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


def find_coordinates_by_vector(
    width: int,
    height: int,
    direction: int,
    distance: int,
    start_x: int,
    start_y: int
) -> tuple[int, int]:
    angle_radians = direction * (math.pi / 180)
    dy = abs(distance * math.cos(angle_radians))
    dx = abs(distance * math.sin(angle_radians))
    x = start_x + dx if 0 <= direction <= 180 else start_x - dx
    y = start_y - dy if 0 <= direction <= 90 or 270 <= direction <= 360 else start_y + dy
    x2 = int(max(0, min(int(x), width)))
    y2 = int(max(0, min(int(y), height)))
    return x2, y2

def get_current_func_name(depth: int = 1) -> str:
    frame = inspect.currentframe()
    if frame is None:
        return "<unknown>"
    for _ in range(depth):
        if frame.f_back is not None:
            frame = frame.f_back

    return frame.f_code.co_name

def grep_pattern(input_string: str, pattern: str) -> list[str]:
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
