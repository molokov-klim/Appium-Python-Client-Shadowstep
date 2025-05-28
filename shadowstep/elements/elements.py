# shadowstep/elements/elements.py
from typing import Iterator, List, Optional, TYPE_CHECKING, Any
from shadowstep.base import ShadowstepBase

if TYPE_CHECKING:
    from shadowstep.element.element import Element  # только для type hints
    from selenium.webdriver.remote.webelement import WebElement


class Elements:
    """
    Lazy iterable wrapper over a list of native WebElement instances.
    Converts each to an Element on access.
    """

    def __init__(
        self,
        native_elements: List['WebElement'],
        base: ShadowstepBase,
        locator: Any,
        timeout: float,
        poll_frequency: float,
        ignored_exceptions: Optional[Any] = None,
        contains: bool = False
    ):
        self._native_elements = native_elements
        self._base = base
        self._locator = locator
        self._timeout = timeout
        self._poll_frequency = poll_frequency
        self._ignored_exceptions = ignored_exceptions
        self._contains = contains

    def __iter__(self) -> Iterator['Element']:
        from shadowstep.element.element import Element  # ← отложенный импорт, избегает рекурсии
        for native in self._native_elements:
            yield Element(
                locator=self._locator,
                base=self._base,
                timeout=self._timeout,
                poll_frequency=self._poll_frequency,
                ignored_exceptions=self._ignored_exceptions,
                contains=self._contains,
                native=native
            )

    def __len__(self) -> int:
        return len(self._native_elements)

    def __getitem__(self, index: int) -> 'Element':
        from shadowstep.element.element import Element
        native = self._native_elements[index]
        return Element(
            locator=self._locator,
            base=self._base,
            timeout=self._timeout,
            poll_frequency=self._poll_frequency,
            ignored_exceptions=self._ignored_exceptions,
            contains=self._contains,
            native=native
        )

    def to_list(self) -> List['Element']:
        return list(iter(self))
