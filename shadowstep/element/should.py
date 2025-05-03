# shadowstep/element/should.py

from typing import Any, Optional, Tuple
from .element import Element


class Should:
    """DSL wrapper for element assertions using 'should.have' and 'should.be' syntax."""

    def __init__(self, element: Element) -> None:
        self.element = element
        self.have = _ShouldHave(element)
        self.not_have = _ShouldNotHave(element)
        self.be = _ShouldBe(element)
        self.not_be = _ShouldNotBe(element)

    def __getattr__(self, name: str) -> Any:
        """Delegates unknown attribute access to the underlying Element instance."""
        try:
            return getattr(self.element, name)
        except AttributeError:
            raise AttributeError(
                f"'Should' has no attribute '{name}', and '{self.element.__class__.__name__}' also does not have it.")


class _ShouldBase:
    """Base class for 'have' and 'be' assertion helpers, with optional negation."""

    def __init__(self, element: Element, negate: bool = False) -> None:
        self.element = element
        self.negate = negate

    def _assert(self, condition: bool, message: str) -> None:
        if self.negate:
            assert not condition, "[should.not] " + message
        else:
            assert condition, "[should] " + message


class _ShouldHave(_ShouldBase):
    """Assertions for element attributes: should.have.text(...), should.have.resource_id(...)."""

    def text(self, expected: str) -> Should:
        actual = self.element.text
        self._assert(actual == expected, f"have.text: expected '{expected}', got '{actual}'")
        return Should(self.element)

    def resource_id(self, expected: str) -> Should:
        actual = self.element.get_attribute("resource-id")
        self._assert(actual == expected, f"have.resource_id: expected '{expected}', got '{actual}'")
        return Should(self.element)

    def content_desc(self, expected: str) -> Should:
        actual = self.element.get_attribute("content-desc")
        self._assert(actual == expected, f"have.content_desc: expected '{expected}', got '{actual}'")
        return Should(self.element)

    def class_name(self, expected: str) -> Should:
        actual = self.element.get_attribute("class")
        self._assert(actual == expected, f"have.class_name: expected '{expected}', got '{actual}'")
        return Should(self.element)

    def package(self, expected: str) -> Should:
        actual = self.element.get_attribute("package")
        self._assert(actual == expected, f"have.package: expected '{expected}', got '{actual}'")
        return Should(self.element)

    def bounds(self, expected: Tuple[int, int, int, int]) -> Should:
        actual = self.element.get_attribute("bounds")
        self._assert(actual == expected, f"have.bounds: expected {expected}, got {actual}")
        return Should(self.element)

    def id(self, expected: str) -> Should:
        actual = self.element.get_attribute("id")
        self._assert(actual == expected, f"have.id: expected '{expected}', got '{actual}'")
        return Should(self.element)

    def index(self, expected: str) -> Should:
        actual = self.element.get_attribute("index")
        self._assert(actual == expected, f"have.index: expected '{expected}', got '{actual}'")
        return Should(self.element)

    def attr(self, name: str, expected: Any) -> Should:
        actual = self.element.get_attribute(name)
        self._assert(actual == expected, f"have.attr('{name}'): expected '{expected}', got '{actual}'")
        return Should(self.element)


class _ShouldBe(_ShouldBase):
    """Assertions for element state: should.be.enabled, should.be.selected, etc."""

    def enabled(self) -> Should:
        self._assert(self.element.is_enabled(), "be.enabled: expected element to be enabled")
        return Should(self.element)

    def disabled(self) -> Should:
        self._assert(not self.element.is_enabled(), "be.disabled: expected element to be disabled")
        return Should(self.element)

    def selected(self) -> Should:
        self._assert(self.element.is_selected(), "be.selected: expected element to be selected")
        return Should(self.element)

    def focused(self) -> Should:
        actual = self.element.get_attribute("focused")
        self._assert(actual == "true", "be.focused: expected focused='true'")
        return Should(self.element)

    def focusable(self) -> Should:
        actual = self.element.get_attribute("focusable")
        self._assert(actual == "true", "be.focusable: expected focusable='true'")
        return Should(self.element)

    def long_clickable(self) -> Should:
        actual = self.element.get_attribute("long-clickable")
        self._assert(actual == "true", "be.long_clickable: expected long-clickable='true'")
        return Should(self.element)

    def visible(self) -> Should:
        self._assert(self.element.is_visible(), "be.visible: expected element to be visible")
        return Should(self.element)

    def displayed(self) -> Should:
        return self.visible()

    def checkable(self) -> Should:
        actual = self.element.get_attribute("checkable")
        self._assert(actual == "true", "be.checkable: expected checkable='true'")
        return Should(self.element)

    def checked(self) -> Should:
        actual = self.element.get_attribute("checked")
        self._assert(actual == "true", "be.checked: expected checked='true'")
        return Should(self.element)

    def scrollable(self) -> Should:
        actual = self.element.get_attribute("scrollable")
        self._assert(actual == "true", "be.scrollable: expected scrollable='true'")
        return Should(self.element)

    def password(self) -> Should:
        actual = self.element.get_attribute("password")
        self._assert(actual == "true", "be.password: expected password='true'")
        return Should(self.element)


class _ShouldNotHave(_ShouldHave):
    """Negative assertions for 'have': should.not_have.text(...)"""

    def __init__(self, element: Element) -> None:
        super().__init__(element, negate=True)


class _ShouldNotBe(_ShouldBe):
    """Negative assertions for 'be': should.not_be.visible()"""

    def __init__(self, element: Element) -> None:
        super().__init__(element, negate=True)


"""
have:
    attr
    id
    resource-id
    index
    package
    class
    text
    bounds

be:
    checked
    checkable
    enabled
    focusable
    focused
    long_clickable
    password
    scrollable
    selected
    displayed
"""

"""
######
https://github.com/appium/appium-uiautomator2-driver
Element Attributes

checkable
checked
class or className
clickable
content-desc or contentDescription
enabled
focusable
focused
long-clickable or longClickable
package
password
resource-id or resourceId
scrollable
selection-start
selection-end
selected
text or name
hint
bounds
displayed
contentSize
extras
"""
