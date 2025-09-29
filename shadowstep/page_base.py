"""Base page class for Shadowstep framework.

This module provides the abstract base class for all page objects in the
Shadowstep framework, implementing singleton pattern and page navigation.
"""
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, ClassVar, TypeVar, Any

from typing_extensions import Self

T = TypeVar("T", bound="PageBase")      # type: ignore[valid-type]  # noqa: F821

if TYPE_CHECKING:
    from shadowstep.shadowstep import Shadowstep

class PageBaseShadowstep(ABC):
    """Abstract shadowstep class for all pages in the Shadowstep framework.

    Implements singleton behavior and lazy initialization of the shadowstep context.
    """

    shadowstep: "Shadowstep"
    _instances: ClassVar[dict[type, "PageBaseShadowstep"]] = {}


    def __new__(cls) -> Any:  # noqa: ARG004
        """Create a new instance or return existing singleton instance.

        Returns:
            PageBaseShadowstep: The singleton instance of the page class.

        """
        if cls not in cls._instances:
            from shadowstep.shadowstep import Shadowstep  # noqa: PLC0415
            instance = super().__new__(cls)
            instance.shadowstep = Shadowstep.get_instance()
            cls._instances[cls] = instance
        return cls._instances[cls]

    @classmethod
    def get_instance(cls) -> Self:
        """Get or create the singleton instance of the page.

        Returns:
            PageBaseShadowstep: The singleton instance of the page class.

        """
        return cls()  # type: ignore[return-value]

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
