import inspect
import logging
import traceback
import typing
from typing import Union, Tuple, Dict

from appium.webdriver import WebElement
from selenium.common import WebDriverException
from selenium.types import WaitExcTypes

from shadowstep.base import ShadowstepBase
from shadowstep.element.element import Element

# Configure the root logger (basic configuration)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeneralShadowstepException(WebDriverException):
    """Raised when driver is not specified and cannot be located."""

    def __init__(
            self, msg: typing.Optional[str] = None, screen: typing.Optional[str] = None,
            stacktrace: typing.Optional[typing.Sequence[str]] = None
    ) -> None:
        super().__init__(msg, screen, stacktrace)


class Shadowstep(ShadowstepBase):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_element(self,
                    locator: Union[Tuple[str, str], Dict[str, str]] = None,
                    timeout: int = 30,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                    contains: bool = False) -> Element:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        element = Element(locator=locator,
                          timeout=timeout,
                          poll_frequency=poll_frequency,
                          ignored_exceptions=ignored_exceptions,
                          contains=contains,
                          base=self)
        return element

    def get_elements(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def get_image(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def get_images(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def get_text(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def scheduled_actions(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/scheduled-actions.md
        ...

    def get_element_contains(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method get_element_contains is not yet implemented.")

    def get_elements_contains(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method get_elements_contains is not yet implemented.")

    def find_and_get_element(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method find_and_get_element is not yet implemented.")

    def get_image_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method get_image_coordinates is not yet implemented.")

    def get_inner_image_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method get_inner_image_coordinates is not yet implemented.")

    def get_many_coordinates_of_image(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method get_many_coordinates_of_image is not yet implemented.")

    def get_text_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method get_text_coordinates is not yet implemented.")

    def is_text_on_screen(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method is_text_on_screen is not yet implemented.")

    def is_image_on_the_screen(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method is_image_on_the_screen is not yet implemented.")

    def to_ndarray(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method to_ndarray is not yet implemented.")

    def swipe(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method swipe is not yet implemented.")

    def swipe_right_to_left(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method swipe_right_to_left is not yet implemented.")

    def swipe_left_to_right(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method swipe_left_to_right is not yet implemented.")

    def swipe_top_to_bottom(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method swipe_top_to_bottom is not yet implemented.")

    def swipe_bottom_to_top(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method swipe_bottom_to_top is not yet implemented.")

    def wait_for(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method wait_for is not yet implemented.")

    def wait_for_not(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method wait_for_not is not yet implemented.")

    def is_wait_for(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method is_wait_for is not yet implemented.")

    def is_wait_for_not(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method is_wait_for_not is not yet implemented.")

    def wait_return_true(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method wait_return_true is not yet implemented.")

    def draw_by_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method draw_by_coordinates is not yet implemented.")

    def save_screenshot(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method save_screenshot is not yet implemented.")

    def get_screenshot_as_base64_decoded(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method get_screenshot_as_base64_decoded is not yet implemented.")

    def save_source(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method save_source is not yet implemented.")

    def find_and_tap_in_drop_down_menu(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError("Method find_and_tap_in_drop_down_menu is not yet implemented.")




