# shadowstep/page_base.py
from abc import ABC, abstractmethod
from typing import Callable

class PageBase(ABC):
    def __init__(self, app: "Shadowstep"):
        self.app = app

    @property
    @abstractmethod
    def edges(self) -> dict[str, Callable[[], None]]:
        """
        Returns a dictionary of page name to navigation method.

        example:
        @property
        def edges(self) -> dict[str, Callable[[], None]]:
            return {"PageExample": self.link_to_transition_method}
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
