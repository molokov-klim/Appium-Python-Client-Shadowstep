# shadowstep/element/actions.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    
class ElementActions:
    def __init__(self, element: "Element"):
        self.element = element



