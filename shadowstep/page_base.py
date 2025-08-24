# shadowstep/page_base.py
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T", bound="PageBase")      # type: ignore  # noqa: F821

class PageBaseShadowstep(ABC):
    """Abstract base class for all pages in the Shadowstep framework.

    Implements singleton behavior and lazy initialization of the shadowstep context.
    """

    _instances: dict[type, "PageBaseShadowstep"] = {}

    def __new__(cls, *args: Any, **kwargs: Any) -> "PageBaseShadowstep":
        if cls not in cls._instances:
            instance = super().__new__(cls)

            # 💡 Lazy import to avoid circular dependencies
            from shadowstep.shadowstep import Shadowstep
            instance.shadowstep = Shadowstep.get_instance()
            cls._instances[cls] = instance
        return cls._instances[cls]

    @classmethod
    def get_instance(cls: type[T]) -> T:
        """Get or create the singleton instance of the page.
        Returns:
            PageBaseShadowstep: The singleton instance of the page class.
        """
        return cls()

    @classmethod
    def clear_instance(cls) -> None:
        """Clear the stored instance and its arguments for this page."""
        cls._instances.pop(cls, None)

    @property
    @abstractmethod
    def edges(self) -> dict[str, Callable[[], "PageBaseShadowstep"]]:
        """Each page must declare its navigation edges.

        Returns:
            Dict[str, Callable]: Dictionary mapping page class names to navigation methods.
        """
        pass
