# shadowstep/page_base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Type
from loguru import logger

from shadowstep.shadowstep import Shadowstep


class PageBase(ABC):
    _instances = {}
    _init_args = {}
    _init_kwargs = {}

    def __new__(cls):
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance

            # Получаем Shadowstep и цепляем его как .app
            shadowstep = Shadowstep.get_instance()
            instance.app = shadowstep

        return cls._instances[cls]

    def __init__(self) -> None:
        # !!! Важно: app и другие зависимости должны быть здесь
        self.app = Shadowstep.get_instance()
        logger.info(f"{self.app=}")

    @classmethod
    def get_instance(cls) -> "PageBase":
        """Get or create the singleton instance of the page."""
        return cls()

    @classmethod
    def clear_instance(cls) -> None:
        """Clear the stored instance and its arguments for this page."""
        cls._instances.pop(cls, None)
        cls._init_args.pop(cls, None)
        cls._init_kwargs.pop(cls, None)

    @property
    @abstractmethod
    def edges(self) -> Dict[str, Any]:
        """Each page must declare its navigation edges.

        Returns:
            Dict[str, Callable]: Dictionary mapping page class names to navigation methods.
        """
        pass
