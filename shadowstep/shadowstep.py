import inspect
import logging
import traceback
import typing
from typing import Union, Tuple, Dict

import numpy as np
from PIL import Image
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
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_image(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_images(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_text(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def scheduled_actions(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/scheduled-actions.md

    def find_and_get_element(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_image_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_inner_image_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_many_coordinates_of_image(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_text_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def is_text_on_screen(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def is_image_on_the_screen(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def to_ndarray(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def swipe(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def swipe_right_to_left(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def swipe_left_to_right(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def swipe_top_to_bottom(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def swipe_bottom_to_top(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def wait_for(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def wait_for_not(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def is_wait_for(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def is_wait_for_not(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def wait_return_true(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def draw_by_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def save_screenshot(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_screenshot_as_base64_decoded(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def save_source(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def find_and_tap_in_drop_down_menu(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def _get_screenshot_as_base64_decoded(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def tap(
            self,
            locator: Union[Tuple[str, str], Dict[str, str], Element, WebElement] = None,
            x: int = None,
            y: int = None,
            image: Union[bytes, np.ndarray, Image.Image, str] = None,
            duration: typing.Optional[int] = None,
            timeout: float = 5.0,
            threshold: float = 0.9
    ) -> 'Shadowstep':
        """Perform tap action via locator, coordinates, image or element.

        Args:
            locator (Union[Tuple[str, str], Dict[str, str], Element, WebElement], optional): Element locator or object.
            x (int, optional): X coordinate to tap.
            y (int, optional): Y coordinate to tap.
            image (Union[bytes, np.ndarray, Image.Image, str], optional): Image to find and tap.
            duration (int, optional): Tap duration in milliseconds.
            timeout (float): Timeout for waiting elements or image match.
            threshold (float): Matching threshold for image recognition.

        Returns:
            Shadowstep: self instance for chaining.

        Raises:
            GeneralShadowstepException: if none of the strategies succeed.
        """
        self.logger.info(
            f"{inspect.currentframe().f_code.co_name} with args locator={locator}, x={x}, y={y}, image={bool(image)}")

        try:
            if locator:
                # If locator is already an Element or WebElement
                if isinstance(locator, Element):
                    locator.tap(duration=duration)
                elif isinstance(locator, WebElement):
                    # Wrap into our lazy Element and tap
                    elem = Element(locator=(), base=self)
                    elem._element = locator
                    elem.tap(duration=duration)
                else:
                    # Create lazy element from locator
                    self.get_element(locator=locator, timeout=int(timeout)).tap(duration=duration)
                return self

            elif x is not None and y is not None:
                # Use driver touch_action for coordinate tap
                self.logger.debug(f"Tapping at coordinates: ({x}, {y})")
                self.driver.tap([(x, y)], duration or 100)
                return self

            elif image:
                raise NotImplementedError(f"image {inspect.currentframe().f_code.co_name} is not yet implemented.")
                # # Handle different image input types
                # if isinstance(image, str):
                #     img_data = Image.open(image).convert("RGB")
                # elif isinstance(image, bytes):
                #     from io import BytesIO
                #     img_data = Image.open(BytesIO(image)).convert("RGB")
                # elif isinstance(image, np.ndarray):
                #     img_data = Image.fromarray(image)
                # elif isinstance(image, Image.Image):
                #     img_data = image.convert("RGB")
                # else:
                #     raise ValueError("Unsupported image format for tap.")
                #
                # from shadowstep.vision.image_matcher import find_image_on_screen  # предположим, что такой модуль есть
                #
                # coords = find_image_on_screen(
                #     driver=self.driver,
                #     template=img_data,
                #     threshold=threshold,
                #     timeout=timeout
                # )
                #
                # if coords:
                #     self.driver.tap([coords], duration or 100)
                #     return self
                #
                # raise GeneralShadowstepException("Image not found on screen.")

            else:
                raise GeneralShadowstepException("Tap requires locator, coordinates or image.")
        except Exception as e:
            self.logger.exception(f"Tap failed: {e}")
            raise GeneralShadowstepException(str(e)) from e

