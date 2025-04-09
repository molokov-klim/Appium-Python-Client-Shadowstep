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
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/scheduled-actions.md
        ...
