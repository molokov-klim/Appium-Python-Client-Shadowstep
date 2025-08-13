# shadowstep/__init__.py
import logging
import sys

class LoguruStyleFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[38;5;81m',      # Светло-голубой (как loguru DEBUG)
        'INFO': '\033[38;5;34m',       # Зелёный (как loguru INFO)
        'WARNING': '\033[38;5;220m',   # Жёлтый
        'ERROR': '\033[38;5;196m',     # Красный
        'CRITICAL': '\033[1;41m',      # Белый на красном фоне
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        # Цвет для уровня логирования
        level_color = self.COLORS.get(record.levelname, '')
        levelname = f"{level_color}{record.levelname:<8}{self.RESET}"

        # Серый таймстемп
        time = f"\033[38;5;240m{self.formatTime(record, self.datefmt)}{self.RESET}"

        # Цвет для имени логгера — фиолетовый
        name = f"\033[38;5;135m{record.name}{self.RESET}"

        # Сообщение
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

    # Применяем и к root
    logging.getLogger().handlers = logger.handlers
    logging.getLogger().setLevel(logger.level)
    logger.propagate = False

configure_logging()
