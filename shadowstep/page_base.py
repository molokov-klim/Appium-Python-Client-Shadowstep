# shadowstep/page_base.py
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

T = TypeVar("T", bound="PageBase")      # type: ignore  # noqa: F821

if TYPE_CHECKING:
    from shadowstep.shadowstep import Shadowstep

class PageBaseShadowstep(ABC):
    """Abstract shadowstep class for all pages in the Shadowstep framework.

    Implements singleton behavior and lazy initialization of the shadowstep context.
    """
    shadowstep: "Shadowstep"
    _instances: dict[type, "PageBaseShadowstep"] = {}
    

    def __new__(cls, *args: Any, **kwargs: Any) -> "PageBaseShadowstep":
        if cls not in cls._instances:
            from shadowstep.shadowstep import Shadowstep
            instance = super().__new__(cls)
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
        """Each page must declare its dom edges.

        Returns:
            Dict[str, Callable]: Dictionary mapping page class names to dom methods.
        """
        pass
