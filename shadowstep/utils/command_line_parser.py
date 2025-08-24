# shadowstep/utils/command_line_parser.py
import logging
import os
import sys

from shadowstep.utils.utils import get_current_func_name

logger = logging.getLogger(__name__)


def udid():
    logger.debug(f"{get_current_func_name()}")
    var = ''
    for i in sys.argv[1:]:
        if '--udid' in i:
            var = i.split('=')[1]
            break
    return var


def model():
    logger.debug(f"{get_current_func_name()}")
    var = ''
    for i in sys.argv[1:]:
        if '--model' in i:
            var = i.split('=')[1]
            break
    return var


def detailed():
    logger.debug(f"{get_current_func_name()}")
    var = ''
    for i in sys.argv[1:]:
        if '--detailed' in i:
            var = i.split('=')[1]
            break
    return var


def chat_id():
    logger.debug(f"{get_current_func_name()}")
    var = ''
    for i in sys.argv[1:]:
        if '--chat_id' in i:
            var = i.split('=')[1]
            break
    return var


def env():
    logger.debug(f"{get_current_func_name()}")
    var = ''
    for i in sys.argv[1:]:
        if '--env' in i:
            var = i.split('=')[1]
            break
    return var


def root_dir():
    logger.debug(f"{get_current_func_name()}")
    root_dir_path = ''
    for i in sys.argv[1:]:
        if '--rootdir' in i:
            root_dir_path = i.split('=')[1]
            break
    return os.path.abspath(root_dir_path)
