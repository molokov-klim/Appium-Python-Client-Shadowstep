import logging
import sys

# Создание корневого логгера
logger = logging.getLogger("shadowstep")
logger.setLevel(logging.DEBUG)

# Проверка наличия обработчиков, чтобы избежать дублирования
if not logger.handlers:
    # Обработчик для вывода в stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    # Форматтер для логов
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    # Добавление обработчика к логгеру
    logger.addHandler(handler)

# Установка логгера как корневого для всех модулей
logging.getLogger().handlers = logger.handlers
logging.getLogger().setLevel(logger.level)
