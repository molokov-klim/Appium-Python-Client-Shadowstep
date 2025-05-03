# shadowstep/elements/should.py

from typing import Optional, List
from shadowstep.elements.elements import Elements


class ShouldElements:
    """DSL wrapper for assertions on Elements collection using should.have / should.be syntax."""

    def __init__(self, elements: Elements):
        self.elements = elements
        self.have = _ShouldElementsHave(elements)
        self.not_have = _ShouldElementsHave(elements, negate=True)
        self.be = _ShouldElementsBe(elements)
        self.not_be = _ShouldElementsBe(elements, negate=True)


class _ShouldElementsBase:
    def __init__(self, elements: Elements, negate: bool = False):
        self.elements = elements
        self.negate = negate

    def _assert(self, condition: bool, message: str) -> None:
        if self.negate:
            assert not condition, f"[should.not] {message}"
        else:
            assert condition, f"[should] {message}"


class _ShouldElementsHave(_ShouldElementsBase):

    def count(self, expected: Optional[int] = None, minimum: Optional[int] = None, maximum: Optional[int] = None) -> 'ShouldElements':
        items = self.elements.to_list()
        actual = len(items)
        if expected is not None:
            self._assert(actual == expected, f"have.count: expected {expected}, got {actual}")
        if minimum is not None:
            self._assert(actual >= minimum, f"have.count: expected >= {minimum}, got {actual}")
        if maximum is not None:
            self._assert(actual <= maximum, f"have.count: expected <= {maximum}, got {actual}")
        return ShouldElements(self.elements)

    def texts(self, expected_texts: List[str]) -> 'ShouldElements':
        actual_texts = [el.text or "" for el in self.elements.to_list()]
        self._assert(actual_texts == expected_texts, f"have.texts: expected {expected_texts}, got {actual_texts}")
        return ShouldElements(self.elements)

    def text(self, text: str) -> 'ShouldElements':
        match = any((el.text or "") == text for el in self.elements.to_list())
        self._assert(match, f"have.text: no element has text '{text}'")
        return ShouldElements(self.elements)


class _ShouldElementsBe(_ShouldElementsBase):

    def all_visible(self) -> 'ShouldElements':
        items = self.elements.to_list()
        result = all(el.is_visible() for el in items)
        self._assert(result, "be.all_visible: not all elements are visible")
        return ShouldElements(self.elements)

    def any_visible(self) -> 'ShouldElements':
        items = self.elements.to_list()
        result = any(el.is_visible() for el in items)
        self._assert(result, "be.any_visible: no visible elements found")
        return ShouldElements(self.elements)

    def none_visible(self) -> 'ShouldElements':
        items = self.elements.to_list()
        result = all(not el.is_visible() for el in items)
        self._assert(result, "be.none_visible: some elements are visible")
        return ShouldElements(self.elements)
