# shadowstep/element/waiting.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shadowstep.element.element import Element


class ElementWaiting:
    def __init__(self, element: "Element"):
        self.element: Element = element
