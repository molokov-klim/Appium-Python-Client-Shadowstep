import logging
from typing import Union, Tuple, Dict

from shadowstep.base import ShadowstepBase
from shadowstep.element.element import Element

# Configure the root logger (basic configuration)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Shadowstep(ShadowstepBase):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @staticmethod
    def get_element(locator: Union[Tuple, Dict[str, str]] = None) -> Element:
        """
        Retrieve an element based on the specified locator.

        Args:
            locator : Union[Tuple, Dict[str, str]], optional
                The locator used to find the element (default is None).

        Returns:
            Element
                An instance of the Element class corresponding to the locator.
        """
        element = Element(locator=locator)
        return element

    def get_elements(self):
        ...

    def get_image(self):
        ...

    def get_images(self):
        ...

    def get_text(self):
        ...
