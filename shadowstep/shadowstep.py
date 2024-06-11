from typing import Union, Tuple, Dict, List

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.by import By

from shadowstep.base import SBase
from shadowstep.element.element import Element


class Shadowstep(SBase):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_element(locator: Union[Tuple, Dict[str, str]] = None,
                    contains: bool = True):
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
