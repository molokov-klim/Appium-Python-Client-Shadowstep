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
    start_y: int,
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
    lines = input_string.split("\n")  # Split the input string into lines
    regex = re.compile(pattern)  # Compile the regex pattern
    return [line for line in lines if regex.search(line)]  # Filter lines matching the pattern

def is_camel_case(text: str) -> bool:
    return bool(re.fullmatch(r"[a-z]+(?:[A-Z][a-z0-9]*)*", text))
