# shadowstep/elements/elements.py

from typing import Callable, Iterator, List, Optional

class Elements:
    """Lazy wrapper for a sequence of Element objects generated on demand."""

    def __init__(self, factory: Callable[[], Iterator['Element']]):
        """Initialize with generator factory.

        Args:
            factory (Callable[[], Iterator[Element]]): Generator factory.
        """
        self._factory = factory

    def __iter__(self) -> Iterator['Element']:
        """Iterate over elements."""
        return self._factory()

    def first(self) -> Optional['Element']:
        """Return the first element, or None if empty."""
        return next(self._factory(), None)

    def to_list(self) -> List['Element']:
        """Convert all elements to list."""
        return list(self._factory())

    def filter(self, predicate: Callable[['Element'], bool]) -> 'Elements':
        """Filter elements with predicate."""
        return Elements(lambda: (el for el in self._factory() if predicate(el)))

    def next(self):
        raise NotImplementedError

    @property
    def should(self) -> 'ShouldElements':
        from shadowstep.elements.should import ShouldElements
        return ShouldElements(self)
