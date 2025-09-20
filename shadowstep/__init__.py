# shadowstep/__init__.py
import logging
import sys


class LoguruStyleFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[38;5;81m",      # Light blue (like loguru DEBUG)
        "INFO": "\033[38;5;34m",       # Green (like loguru INFO)
        "WARNING": "\033[38;5;220m",   # Yellow
        "ERROR": "\033[38;5;196m",     # Red
        "CRITICAL": "\033[1;41m",      # White on red background
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        # Color for log level
        level_color = self.COLORS.get(record.levelname, "")
        levelname = f"{level_color}{record.levelname:<8}{self.RESET}"

        # Gray timestamp
        time = f"\033[38;5;240m{self.formatTime(record, self.datefmt)}{self.RESET}"

        # Color for logger name - purple
        name = f"\033[38;5;135m{record.name}{self.RESET}"

        # Message
        message = record.getMessage()

        return f"{time} | {levelname} | {name} | {message}"

def configure_logging():
    logger = logging.getLogger("shadowstep")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(LoguruStyleFormatter(datefmt="%Y-%m-%d %H:%M:%S"))

    if not logger.handlers:
        logger.addHandler(handler)

    # Apply to root logger as well
    logging.getLogger().handlers = logger.handlers
    logging.getLogger().setLevel(logger.level)
    logger.propagate = False

configure_logging()
