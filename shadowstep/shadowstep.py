from typing import Union, Tuple, Dict, List

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.by import By

from shadowstep.base import SBase
from shadowstep.element.element import Element


class Shadowstep(SBase):

    def __init__(self):
        super().__init__()

    def get_element(self,
                    locator: Union[Tuple, Dict[str, str], str] = None,
                    contains: bool = True):
        return Element(locator=locator,
                       contains=contains)

    def get_elements(self):
        ...

    def get_image(self):
        ...

    def get_images(self):
        ...

    def get_text(self):
        ...





















