# shadowstep/page_base.py

import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict, TYPE_CHECKING, TypeVar, Type, Callable

if TYPE_CHECKING:
    from shadowstep.shadowstep import Shadowstep

T = TypeVar("T", bound="PageBase")

class PageBase(ABC):
    """Abstract base class for all pages in the Shadowstep framework.

    Implements singleton behavior and lazy initialization of the app context.
    """

    _instances: Dict[type, "PageBase"] = {}

    def __new__(cls, *args: Any, **kwargs: Any) -> "PageBase":
        if cls not in cls._instances:
            instance = super().__new__(cls)

            # 💡 Lazy import to avoid circular dependencies
            from shadowstep.shadowstep import Shadowstep
            instance.app: "Shadowstep" = Shadowstep.get_instance()
            cls._instances[cls] = instance
        return cls._instances[cls]

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        """Get or create the singleton instance of the page.
        Returns:
            PageBase: The singleton instance of the page class.
        """
        return cls()

    @classmethod
    def clear_instance(cls) -> None:
        """Clear the stored instance and its arguments for this page."""
        cls._instances.pop(cls, None)

    @property
    @abstractmethod
    def edges(self) -> Dict[str, Callable[[], "PageBase"]]:
        """Each page must declare its navigation edges.

        Returns:
            Dict[str, Callable]: Dictionary mapping page class names to navigation methods.
        """
        pass
