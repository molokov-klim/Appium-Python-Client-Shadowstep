from typing import Union, Tuple, Dict

from shadowstep.base import ShadowstepBase
from shadowstep.element.element import Element


class Shadowstep(ShadowstepBase):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_element(locator: Union[Tuple, Dict[str, str]] = None,
                    contains: bool = True) -> Element:
        """
        Retrieve an element based on the specified locator.

        Args:
            locator : Union[Tuple, Dict[str, str]], optional
                The locator used to find the element (default is None).
            contains : bool, optional
                Indicates whether to match the locator partially (default is True).

        Returns:
            Element
                An instance of the Element class corresponding to the locator.
        """
        element = Element(locator=locator,
                          contains=contains)
        return element

    def get_elements(self):
        ...

    def get_image(self):
        ...

    def get_images(self):
        ...

    def get_text(self):
        ...
