import inspect
from typing import Union, Tuple, Dict, Optional, cast

from shadowstep.element.base import ElementBase


class Element(ElementBase):
    """
    A class to represent a UI element in the Shadowstep application.
    """
    def __init__(self, locator: Union[Tuple, Dict[str, str], str] = None, contains: bool = True):
        super().__init__()
        self.locator = locator
        self.contains = contains

    def __repr__(self):
        return f"Element(locator={self.locator}, contains={self.contains})"

    def tap(self, duration: Optional[int] = None) -> 'Element':
        """
        Tap on the element.

        Args:
            duration : Optional[int], optional
                The duration for the tap action in milliseconds (default is None).

        Returns:
            Element
                The current Element instance after the tap action.
        """
        self._get_driver()
        element = self._get_element(locator=self.locator)
        # Получение границ элемента
        left, top, right, bottom = map(int, element.get_attribute('bounds').strip("[]").replace("][", ",").split(","))
        # Расчет координат центра элемента
        x = (left + right) / 2
        y = (top + bottom) / 2
        self.driver.tap(positions=[(x, y)], duration=duration)
        return cast('Element', self)
