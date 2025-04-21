import traceback
import typing
from typing import Optional, Union, Tuple, List, Dict

import numpy as np
from PIL import Image
from appium.webdriver import WebElement
from selenium.types import WaitExcTypes


class ShadowstepError(Exception):
    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class ShadowstepElementError(ShadowstepError):
    def __init__(self, message: str = '', original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class ShadowstepGetElementError(ShadowstepElementError):
    def __init__(self,
                 message='Failed to get element',
                 locator=None,
                 contains=None,
                 timeout: float = None,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: Optional[WaitExcTypes] = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {locator=}, {contains=}" if "Args:" not in message else message
        super().__init__(message, original_exception)
        self.locator = locator
        self.contains = contains
        self.timeout = timeout
        self.poll_frequency = poll_frequency
        self.ignored_exceptions = ignored_exceptions


class ShadowstepImageProcessingError(ShadowstepError):
    def __init__(self, message: str = '',
                 image: Union[bytes, str] = None,
                 full_image: Union[bytes, str] = None,
                 threshold: Optional[float] = None,
                 original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.image = image
        self.full_image = full_image
        self.threshold = threshold
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class ShadowstepTextRecognitionError(ShadowstepError):
    def __init__(self,
                 message: str = 'Failed to recognize text',
                 text: Optional[str] = None,
                 language: Optional[str] = None,
                 image: Union[bytes, str] = None,
                 contains: Optional[bool] = None,
                 ocr: Optional[bool] = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {text=}, {language=}, {ocr=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.text = text
        self.language = language
        self.image = image
        self.ocr = ocr
        self.contains = contains
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class ShadowstepSwipeError(ShadowstepError):
    def __init__(self,
                 message: str = 'Swipe action failed',
                 start_position=None,
                 end_position=None,
                 direction=None,
                 distance=None,
                 duration=None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {start_position=}, {end_position=}, {direction=}, {distance=}, {duration=}" if "Args:" not in message else message
        super().__init__(message)
        self.start_position = start_position
        self.end_position = end_position
        self.direction = direction
        self.distance = distance
        self.duration = duration
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class ShadowstepTimeoutError(ShadowstepError):
    def __init__(self,
                 message: str = 'Timeout exceeded',
                 locator: Optional[Union[str, Dict]] = None,
                 image: Optional[Union[str, bytes, np.ndarray, Image.Image]] = None,
                 timeout: float = 10.0,
                 contains: Optional[bool] = True,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {locator=}, {image=}, {timeout=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.locator = locator
        self.image = image
        self.timeout = timeout
        self.contains = contains
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class ShadowstepTapError(ShadowstepError):
    def __init__(self,
                 message: str = 'Tap action failed',
                 locator: Optional[Union[str, Dict]] = None,
                 x: Optional[int] = None,
                 y: Optional[int] = None,
                 image: Optional[Union[str, bytes]] = None,
                 duration: Optional[int] = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {locator=}, {x=}, {y=}, {duration=}" if "Args:" not in message else message
        super().__init__(message)
        self.locator = locator
        self.x = x
        self.y = y
        self.image = image
        self.duration = duration
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()
