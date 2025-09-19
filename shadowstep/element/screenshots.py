# shadowstep/element/screenshots.py
import logging
import time
import traceback
from typing import TYPE_CHECKING

from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.decorators.decorators import log_debug
from shadowstep.element.utilities import ElementUtilities
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.locator import LocatorConverter
    from shadowstep.shadowstep import Shadowstep


class ElementScreenshots:
    def __init__(self, element: "Element"):
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities


    @log_debug()
    def screenshot_as_base64(self) -> str:
        """Gets the screenshot of the current element as a base64 encoded string.

        Returns:
            Optional[str]: Base64-encoded screenshot string or None if failed.
        """
        start_time = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()

                current_element = self.element.get_native()

                return current_element.screenshot_as_base64

            except NoSuchDriverException as error:
                self.element.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.handle_driver_error(error)
            except AttributeError as error:
                self.element.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                self.element.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to get screenshot_as_base64 within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def screenshot_as_png(self) -> bytes:
        """Gets the screenshot of the current element as binary data.

        Returns:
            Optional[bytes]: PNG-encoded screenshot bytes or None if failed.
        """
        start_time = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()

                current_element = self.element.get_native()

                return current_element.screenshot_as_png

            except NoSuchDriverException as error:
                self.element.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.handle_driver_error(error)
            except AttributeError as error:
                self.element.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                self.element.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to get screenshot_as_png within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @log_debug()
    def save_screenshot(self, filename: str) -> bool:
        """Saves a screenshot of the current element to a PNG image file.

        Args:
            filename (str): The full path to save the screenshot. Should end with `.png`.

        Returns:
            bool: True if successful, False otherwise.
        """
        start_time = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()

                current_element = self.element.get_native()

                return current_element.screenshot(filename)

            except NoSuchDriverException as error:
                self.element.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.handle_driver_error(error)
            except AttributeError as error:
                self.element.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except OSError as error:
                self.logger.error(f"IOError while saving screenshot to {filename}: {error}")
                return False
            except WebDriverException as error:
                self.element.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to save screenshot to {filename} within {self.element.timeout=}",
            stacktrace=traceback.format_stack()
        )

