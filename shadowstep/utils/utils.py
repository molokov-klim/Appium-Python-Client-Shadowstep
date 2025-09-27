# shadowstep/utils/utils.py
"""General utility functions for Shadowstep framework.

This module provides various utility functions including coordinate calculations,
function name introspection, text pattern matching, and string validation
used throughout the Shadowstep automation framework.
"""

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
    """Calculate end coordinates based on vector from start point.
    
    Args:
        width: Screen width in pixels.
        height: Screen height in pixels.
        direction: Direction angle in degrees (0-360).
        distance: Distance to move in pixels.
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        
    Returns:
        tuple[int, int]: End coordinates (x, y) clamped to screen bounds.
    """
    angle_radians = direction * (math.pi / 180)
    dy = abs(distance * math.cos(angle_radians))
    dx = abs(distance * math.sin(angle_radians))
    x = start_x + dx if 0 <= direction <= 180 else start_x - dx
    y = start_y - dy if 0 <= direction <= 90 or 270 <= direction <= 360 else start_y + dy
    x2 = int(max(0, min(int(x), width)))
    y2 = int(max(0, min(int(y), height)))
    return x2, y2

def get_current_func_name(depth: int = 1) -> str:
    """Get the name of the calling function.
    
    Args:
        depth: Stack depth to look up (1 = caller, 2 = caller's caller, etc.).
        
    Returns:
        str: Name of the function at the specified depth, or "<unknown>" if not found.
    """
    frame = inspect.currentframe()
    if frame is None:
        return "<unknown>"
    for _ in range(depth):
        if frame.f_back is not None:
            frame = frame.f_back

    return frame.f_code.co_name

def grep_pattern(input_string: str, pattern: str) -> list[str]:
    """Filter lines from input string that match the given regex pattern.
    
    Args:
        input_string: Multi-line string to search in.
        pattern: Regular expression pattern to match.
        
    Returns:
        list[str]: List of lines that match the pattern.
    """
    lines = input_string.split("\n")  # Split the input string into lines
    regex = re.compile(pattern)  # Compile the regex pattern
    return [line for line in lines if regex.search(line)]  # Filter lines matching the pattern

def is_camel_case(text: str) -> bool:
    """Check if the given text is in camelCase format.
    
    Args:
        text: String to validate.
        
    Returns:
        bool: True if text is in camelCase format, False otherwise.
    """
    return bool(re.fullmatch(r"[a-z]+(?:[A-Z][a-z0-9]*)*", text))
