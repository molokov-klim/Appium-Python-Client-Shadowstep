# shadowstep/page_base.py
from abc import ABC, abstractmethod
from typing import Any, Dict


class PageBase(ABC):
    _instances = {}

    def __new__(cls):
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance

            # 💡 Lazy import здесь
            from shadowstep.shadowstep import Shadowstep
            instance.app = Shadowstep.get_instance()

        return cls._instances[cls]

    @classmethod
    def get_instance(cls) -> "PageBase":
        """Get or create the singleton instance of the page."""
        return cls()

    @classmethod
    def clear_instance(cls) -> None:
        """Clear the stored instance and its arguments for this page."""
        cls._instances.pop(cls, None)

    @property
    @abstractmethod
    def edges(self) -> Dict[str, Any]:
        """Each page must declare its navigation edges.

        Returns:
            Dict[str, Callable]: Dictionary mapping page class names to navigation methods.
        """
        pass
