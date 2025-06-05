# shadowstep/shadowstep.py
import base64
import importlib
import inspect
import logging
import os
import sys
import typing
from pathlib import Path
from types import ModuleType
from typing import Union, Tuple, Dict

from PIL import Image
import numpy as np
from appium.webdriver.webdriver import WebDriver
from selenium.common import NoSuchDriverException, InvalidSessionIdException, WebDriverException, \
    StaleElementReferenceException

from selenium.types import WaitExcTypes

from shadowstep.base import ShadowstepBase, WebDriverSingleton
from shadowstep.element.element import Element
from shadowstep.elements.elements import Elements
from shadowstep.image.image import ShadowstepImage
from shadowstep.images.images import ShadowstepImages
from shadowstep.logging.shadowstep_logcat import ShadowstepLogcat
from shadowstep.navigator.navigator import PageNavigator
from shadowstep.page_base import PageBaseShadowstep
from shadowstep.scheduled_actions.action_history import ActionHistory
from shadowstep.scheduled_actions.action_step import ActionStep
from shadowstep.utils.decorators import fail_safe
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

# Configure the root logger (basic configuration)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Shadowstep(ShadowstepBase):
    pages: typing.Dict[str, typing.Type[PageBaseShadowstep]] = {}
    _instance: typing.Optional["Shadowstep"] = None
    _pages_discovered: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # возможная инициализация по kwargs
        return cls._instance

    @classmethod
    def get_instance(cls) -> "Shadowstep":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        super().__init__()

        self._logcat = ShadowstepLogcat(driver_getter=WebDriverSingleton.get_driver)
        self.navigator = PageNavigator(self)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._auto_discover_pages()
        self._initialized = True

    def _auto_discover_pages(self):
        """Automatically import and register all PageBase subclasses from all 'pages' directories in sys.path."""
        self.logger.debug(f"📂 {inspect.currentframe().f_code.co_name}: {list(set(sys.path))}")
        if self._pages_discovered:
            return
        self._pages_discovered = True
        for base_path in map(Path, list(set(sys.path))):
            base_str = str(base_path).lower()
            if any(part in base_str for part in self._ignored_base_path_parts):
                continue
            if not base_path.exists() or not base_path.is_dir():
                continue
            for dirpath, dirs, filenames in os.walk(base_path):
                dir_name = Path(dirpath).name
                # ❌ исключаем вложенные директории
                dirs[:] = [d for d in dirs if d not in self._ignored_auto_discover_dirs]
                if dir_name in self._ignored_auto_discover_dirs:
                    continue
                for file in filenames:
                    if file.startswith("page") and file.endswith(".py"):
                        try:
                            file_path = Path(dirpath) / file
                            rel_path = file_path.relative_to(base_path).with_suffix('')
                            module_name = ".".join(rel_path.parts)
                            module = importlib.import_module(module_name)
                            self._register_pages_from_module(module)
                        except Exception as e:
                            self.logger.warning(f"⚠️ Import error {file}: {e}")

    def _register_pages_from_module(self, module: ModuleType):
        try:
            members = inspect.getmembers(module)
            for name, obj in members:
                if not inspect.isclass(obj):
                    continue
                if not issubclass(obj, PageBaseShadowstep):
                    continue
                if obj is PageBaseShadowstep:
                    continue
                if not name.startswith("Page"):
                    continue
                self.pages[name] = obj
                page_instance = obj()
                edges = list(page_instance.edges.keys())
                self.logger.info(f"✅ register page: {page_instance} with edges {edges}")
                self.navigator.add_page(page_instance, edges)
        except Exception as e:
            self.logger.error(f"❌ Error page register from module {module.__name__}: {e}")

    def list_registered_pages(self) -> None:
        """Log all registered page classes."""
        self.logger.info("=== Registered Pages ===")
        for name, cls in self.pages.items():
            self.logger.info(f"{name}: {cls.__module__}.{cls.__name__}")

    def get_page(self, name: str) -> PageBaseShadowstep:
        cls = self.pages.get(name)
        if not cls:
            raise ValueError(f"Page '{name}' not found in registered pages.")
        return cls()

    def resolve_page(self, name: str) -> PageBaseShadowstep:
        cls = self.pages.get(name)
        if cls:
            return cls()
        raise ValueError(f"Page '{name}' not found.")

    def get_element(self,
                    locator: Union[Tuple[str, str], Dict[str, str]] = None,
                    timeout: int = 30,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                    contains: bool = False) -> Element:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        element = Element(locator=locator,
                          timeout=timeout,
                          poll_frequency=poll_frequency,
                          ignored_exceptions=ignored_exceptions,
                          contains=contains,
                          base=self)
        return element

    def get_elements(
            self,
            locator: Union[Tuple[str, str], Dict[str, str]],
            timeout: int = 30,
            poll_frequency: float = 0.5,
            ignored_exceptions: typing.Optional[WaitExcTypes] = None,
            contains: bool = False
    ) -> Elements:
        """
        Find multiple elements matching the given locator across the whole page.

        Args:
            locator: Locator tuple or dict to search elements.
            timeout: How long to wait for elements.
            poll_frequency: Polling frequency.
            ignored_exceptions: Exceptions to ignore.
            contains: Whether to use contains-style XPath matching.

        Returns:
            Elements: Lazy iterable of Element instances.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        root = Element(
            locator=("xpath", "//*"),
            base=self,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
            contains=False
        )
        return root.get_elements(locator=locator, contains=contains)

    def get_image(
            self,
            image: Union[bytes, np.ndarray, Image.Image, str],
            threshold: float = 0.5,
            timeout: float = 5.0
    ) -> ShadowstepImage:
        """
        Return a lazy ShadowstepImage wrapper for the given template.

        Args:
            image: template (bytes, ndarray, PIL.Image or path)
            threshold: matching threshold [0–1]
            timeout: max seconds to search

        Returns:
            ShadowstepImage: ленивый объект для image-actions.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        return ShadowstepImage(
            image=image,
            base=self,
            threshold=threshold,
            timeout=timeout
        )

    def get_images(
            self,
            image: Union[bytes, np.ndarray, Image.Image, str],
            threshold: float = 0.5,
            timeout: float = 5.0
    ) -> ShadowstepImages:
        return ShadowstepImages(image=image,
                                base=self,
                                threshold=threshold,
                                timeout=timeout)

    def schedule_action(
            self,
            name: str,
            steps: typing.List[ActionStep],
            interval_ms: int = 1000,
            times: int = 1,
            max_pass: typing.Optional[int] = None,
            max_fail: typing.Optional[int] = None,
            max_history_items: int = 20
    ) -> 'Shadowstep':
        """
        Schedule a server-side action sequence.

        Args:
            name: unique action name.
            steps: список шагов (GestureStep, SourceStep, ScreenshotStep и т.п.).
            interval_ms: пауза между запусками в мс.
            times: сколько раз попытаться выполнить.
            max_pass: прекратить после N успешных запусков.
            max_fail: прекратить после N неудач.
            max_history_items: сколько записей хранить в истории.
        Returns:
            self — для удобного чейнинга.
        """
        # shadowstep/scheduled_actions
        raise NotImplementedError

    def get_action_history(self, name: str) -> ActionHistory:
        """
        Fetch the execution history for the named action.

        Args:
            name: то же имя, что и при schedule_action.
        Returns:
            ActionHistory — удобная обёртка над JSON-ответом.
        """
        # shadowstep/scheduled_actions
        raise NotImplementedError

    def unschedule_action(self, name: str) -> ActionHistory:
        """
        Unschedule the action and return its final history.

        Args:
            name: то же имя, что и при schedule_action.
        Returns:
            ActionHistory — история всех выполнений до момента отмены.
        """
        # shadowstep/scheduled_actions
        raise NotImplementedError

    def start_logcat(self, filename: str) -> None:
        self._logcat.start(filename)

    def stop_logcat(self) -> None:
        self._logcat.stop()

    def find_and_get_element(
            self,
            locator: Union[Tuple[str, str], Dict[str, str]],
            timeout: int = 30,
            poll_frequency: float = 0.5,
            ignored_exceptions: typing.Optional[WaitExcTypes] = None,
            contains: bool = False,
            max_swipes: int = 30
    ) -> typing.Optional[Element]:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            scrollables = self.get_elements(
                locator={'scrollable': 'true'},
                timeout=timeout,
                poll_frequency=poll_frequency,
                ignored_exceptions=ignored_exceptions,
                contains=contains
            )
            for scrollable in scrollables:
                try:
                    scrollable: Element
                    result = scrollable.scroll_to_element(locator=locator, max_swipes=max_swipes)
                    if result is not None and result.is_visible():
                        return result
                except Exception as e:  # FIXME use specified exception
                    self.logger.debug(f"Scroll attempt failed on scrollable element: {e}")
                    continue
        except Exception as e:  # FIXME use specified exception
            self.logger.error(f"Failed to find scrollable elements: {e}")
        return None

    def is_text_visible(self, text: str) -> bool:
        """Check if an element with the given text is visible.

        Args:
            text (str): The exact or partial text to search for.

        Returns:
            bool: True if element is found and visible, False otherwise.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            element = Element(locator={'text': text}, base=self, contains=True)
            return element.is_visible()
        except Exception as e:
            self.logger.warning(f"Failed to check visibility for text='{text}': {e}")
            return False

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException)
    )
    def scroll(
            self,
            left: int,
            top: int,
            width: int,
            height: int,
            direction: str,
            percent: float,
            speed: int
    ) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-scrollgesture
        Perform a scroll gesture in the specified area.

        Args:
            left (int): Left coordinate of the scroll area.
            top (int): Top coordinate of the scroll area.
            width (int): Width of the scroll area.
            height (int): Height of the scroll area.
            direction (str): Scroll direction: 'up', 'down', 'left', 'right'.
            percent (float): Scroll size as percentage (0.0 < percent <= 1.0).
            speed (int): Speed in pixels per second.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be scrolled. If the element id is missing then scroll bounding area must be provided. If both the element id and the scroll bounding area are provided then this area is effectively ignored.
        left: The left coordinate of the scroll bounding area
        top: The top coordinate of the scroll bounding area
        width: The width of the scroll bounding area
        height: The height of the scroll bounding area
        direction: Scrolling direction. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
        percent: The size of the scroll as a percentage of the scrolling area size. Valid values must be float numbers greater than zero, where 1.0 is 100%. Mandatory value.
        speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 5000 * displayDensity
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver: WebDriver = WebDriverSingleton.get_driver()

        # Defensive validation (optional, to fail early on bad input)
        if direction.lower() not in {'up', 'down', 'left', 'right'}:
            raise ValueError(f"Invalid direction '{direction}', must be one of: up, down, left, right")

        if not (0.0 < percent <= 1.0):
            raise ValueError(f"Percent must be between 0 and 1, got {percent}")

        if speed < 0:
            raise ValueError(f"Speed must be non-negative, got {speed}")

        self._execute(
            'mobile: scrollGesture',
            {
                'left': left,
                'top': top,
                'width': width,
                'height': height,
                'direction': direction.lower(),
                'percent': percent,
                'speed': speed
            }
        )
        return self

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException)
    )
    def long_click(self, x: int, y: int, duration: int) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-longclickgesture
        Perform a long click gesture at the given coordinates.

        Args:
            x (int): X-coordinate of the click.
            y (int): Y-coordinate of the click.
            duration (int): Duration in milliseconds (default: 500). Must be ≥ 0.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be clicked. If the element is missing then both click offset coordinates must be provided. If both the element id and offset are provided then the coordinates are parsed as relative offsets from the top left corner of the element.
        x: The x-offset coordinate
        y: The y-offset coordinate
        duration: Click duration in milliseconds. 500 by default. The value must not be negative
        locator: The map containing strategy and selector items to make it possible to click dynamic elements.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        if duration < 0:
            raise ValueError(f"Duration must be non-negative, got {duration}")

        self.driver = WebDriverSingleton.get_driver()
        self._execute(
            'mobile: longClickGesture',
            {'x': x, 'y': y, 'duration': duration}
        )
        return self

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def double_click(self, x: int, y: int) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-doubleclickgesture
        Perform a double click gesture at the given coordinates.

        Args:
            x (int): X-coordinate of the click.
            y (int): Y-coordinate of the click.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be clicked. If the element is missing then both click offset coordinates must be provided. If both the element id and offset are provided then the coordinates are parsed as relative offsets from the top left corner of the element.
        x: The x-offset coordinate
        y: The y-offset coordinate
        locator: The map containing strategy and selector items to make it possible to click dynamic elements.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        self.driver = WebDriverSingleton.get_driver()
        self._execute(
            'mobile: doubleClickGesture',
            {'x': x, 'y': y}
        )
        return self

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def click(self, x: int, y: int) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-clickgesture
        Perform a click gesture at the given coordinates.

        Args:
            x (int): X-coordinate of the click.
            y (int): Y-coordinate of the click.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be clicked. If the element is missing then both click offset coordinates must be provided. If both the element id and offset are provided then the coordinates are parsed as relative offsets from the top left corner of the element.
        x: The x-offset coordinate
        y: The y-offset coordinate
        locator: The map containing strategy and selector items to make it possible to click dynamic elements.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        self.driver = WebDriverSingleton.get_driver()
        self._execute(
            'mobile: clickGesture',
            {'x': x, 'y': y}
        )
        return self

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def drag(
            self,
            start_x: int,
            start_y: int,
            end_x: int,
            end_y: int,
            speed: int
    ) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-draggesture
        Perform a drag gesture from one point to another.

        Args:
            start_x (int): Starting X coordinate.
            start_y (int): Starting Y coordinate.
            end_x (int): Target X coordinate.
            end_y (int): Target Y coordinate.
            speed (int): Speed of the gesture in pixels per second.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be dragged. If the element id is missing then both start coordinates must be provided. If both the element id and the start coordinates are provided then these coordinates are considered as offsets from the top left element corner.
        startX: The x-start coordinate
        startY: The y-start coordinate
        endX: The x-end coordinate. Mandatory argument
        endY: The y-end coordinate. Mandatory argument
        speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 2500 * displayDensity
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        if speed < 0:
            raise ValueError(f"Speed must be non-negative, got {speed}")

        self.driver = WebDriverSingleton.get_driver()
        self._execute(
            'mobile: dragGesture',
            {
                'startX': start_x,
                'startY': start_y,
                'endX': end_x,
                'endY': end_y,
                'speed': speed
            }
        )
        return self

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def fling(
            self,
            left: int,
            top: int,
            width: int,
            height: int,
            direction: str,
            speed: int
    ) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-flinggesture
        Perform a fling gesture in the specified area.

        Args:
            left (int): Left coordinate of the fling area.
            top (int): Top coordinate.
            width (int): Width of the area.
            height (int): Height of the area.
            direction (str): One of: 'up', 'down', 'left', 'right'.
            speed (int): Speed in pixels per second (> 50).

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be flinged. If the element id is missing then fling bounding area must be provided. If both the element id and the fling bounding area are provided then this area is effectively ignored.
        left: The left coordinate of the fling bounding area
        top: The top coordinate of the fling bounding area
        width: The width of the fling bounding area
        height: The height of the fling bounding area
        direction: Direction of the fling. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
        speed: The speed at which to perform this gesture in pixels per second. The value must be greater than the minimum fling velocity for the given view (50 by default). The default value is 7500 * displayDensity
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        if direction.lower() not in {"up", "down", "left", "right"}:
            raise ValueError("Invalid direction: {direction}")
        if speed <= 0:
            raise ValueError(f"Speed must be > 0, got {speed}")

        self.driver = WebDriverSingleton.get_driver()
        self._execute(
            'mobile: flingGesture',
            {
                'left': left,
                'top': top,
                'width': width,
                'height': height,
                'direction': direction.lower(),
                'speed': speed
            }
        )
        return self

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def pinch_open(
            self,
            left: int,
            top: int,
            width: int,
            height: int,
            percent: float,
            speed: int
    ) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-pinchopengesture
        Perform a pinch-open gesture in the given bounding area.

        Args:
            left (int): Left coordinate of the bounding box.
            top (int): Top coordinate.
            width (int): Width of the bounding box.
            height (int): Height of the bounding box.
            percent (float): Scale of the pinch (0.0 < percent ≤ 1.0).
            speed (int): Speed in pixels per second.

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be pinched. If the element id is missing then pinch bounding area must be provided. If both the element id and the pinch bounding area are provided then the area is effectively ignored.
        left: The left coordinate of the pinch bounding area
        top: The top coordinate of the pinch bounding area
        width: The width of the pinch bounding area
        height: The height of the pinch bounding area
        percent: The size of the pinch as a percentage of the pinch area size. Valid values must be float numbers in range 0..1, where 1.0 is 100%. Mandatory value.
        speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 2500 * displayDensity
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        if not (0.0 < percent <= 1.0):
            raise ValueError(f"Percent must be between 0 and 1, got {percent}")
        if speed < 0:
            raise ValueError(f"Speed must be non-negative, got {speed}")

        self.driver = WebDriverSingleton.get_driver()
        self._execute(
            'mobile: pinchOpenGesture',
            {
                'left': left,
                'top': top,
                'width': width,
                'height': height,
                'percent': percent,
                'speed': speed
            }
        )
        return self

    @fail_safe(retries=3, delay=0.5,
               raise_exception=ShadowstepException,
               exceptions=(NoSuchDriverException,
                           InvalidSessionIdException,
                           StaleElementReferenceException))
    def pinch_close(
            self,
            left: int,
            top: int,
            width: int,
            height: int,
            percent: float,
            speed: int
    ) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-pinchclosegesture
        Perform a pinch-close gesture in the given bounding area.

        Args:
            left (int): Left coordinate of the bounding box.
            top (int): Top coordinate of the bounding box.
            width (int): Width of the bounding box.
            height (int): Height of the bounding box.
            percent (float): Pinch size as a percentage of area (0.0 < percent ≤ 1.0).
            speed (int): Speed of the gesture in pixels per second (≥ 0).

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be pinched. If the element id is missing then pinch bounding area must be provided. If both the element id and the pinch bounding area are provided then the area is effectively ignored.
        left: The left coordinate of the pinch bounding area
        top: The top coordinate of the pinch bounding area
        width: The width of the pinch bounding area
        height: The height of the pinch bounding area
        percent: The size of the pinch as a percentage of the pinch area size. Valid values must be float numbers in range 0..1, where 1.0 is 100%. Mandatory value.
        speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 2500 * displayDensity
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        if not (0.0 < percent <= 1.0):
            raise ValueError(f"Percent must be between 0 and 1, got {percent}")
        if speed < 0:
            raise ValueError(f"Speed must be non-negative, got {speed}")

        self.driver = WebDriverSingleton.get_driver()
        self._execute(
            'mobile: pinchCloseGesture',
            {
                'left': left,
                'top': top,
                'width': width,
                'height': height,
                'percent': percent,
                'speed': speed
            }
        )
        return self

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def swipe(
            self,
            left: int,
            top: int,
            width: int,
            height: int,
            direction: str,
            percent: float,
            speed: int
    ) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/docs/android-mobile-gestures.md#mobile-swipegesture
        Perform a swipe gesture within the specified bounding box.

        Args:
            left (int): Left coordinate of the swipe area.
            top (int): Top coordinate of the swipe area.
            width (int): Width of the swipe area.
            height (int): Height of the swipe area.
            direction (str): Swipe direction: 'up', 'down', 'left', or 'right'.
            percent (float): Swipe distance as percentage of area size (0.0 < percent ≤ 1.0).
            speed (int): Swipe speed in pixels per second (≥ 0).

        Returns:
            Shadowstep: Self for method chaining.

        origin:
        Supported arguments
        elementId: The id of the element to be swiped. If the element id is missing then swipe bounding area must be provided. If both the element id and the swipe bounding area are provided then the area is effectively ignored.
        left: The left coordinate of the swipe bounding area
        top: The top coordinate of the swipe bounding area
        width: The width of the swipe bounding area
        height: The height of the swipe bounding area
        direction: Swipe direction. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
        percent: The size of the swipe as a percentage of the swipe area size. Valid values must be float numbers in range 0..1, where 1.0 is 100%. Mandatory value.
        speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 5000 * displayDensity
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        if direction.lower() not in {"up", "down", "left", "right"}:
            raise ValueError(f"Invalid direction '{direction}' — must be one of: up, down, left, right")
        if not (0.0 < percent <= 1.0):
            raise ValueError(f"Percent must be between 0 and 1, got {percent}")
        if speed < 0:
            raise ValueError(f"Speed must be non-negative, got {speed}")

        self.driver = WebDriverSingleton.get_driver()
        self._execute(
            'mobile: swipeGesture',
            {
                'left': left,
                'top': top,
                'width': width,
                'height': height,
                'direction': direction.lower(),
                'percent': percent,
                'speed': speed
            }
        )
        return self

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException)
    )
    def swipe_right_to_left(self) -> 'Shadowstep':
        """Perform a full-width horizontal swipe from right to left.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        self.driver = WebDriverSingleton.get_driver()
        size = self.driver.get_window_size()
        width = size["width"]
        height = size["height"]

        return self.swipe(
            left=0,
            top=height // 2,
            width=width,
            height=height // 3,
            direction="left",
            percent=1.0,
            speed=1000
        )

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def swipe_left_to_right(self) -> 'Shadowstep':
        """Perform a full-width horizontal swipe from left to right.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        self.driver = WebDriverSingleton.get_driver()
        size = self.driver.get_window_size()
        width = size["width"]
        height = size["height"]

        return self.swipe(
            left=0,
            top=height // 2,
            width=width,
            height=height // 3,
            direction="right",
            percent=1.0,
            speed=1000
        )

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def swipe_top_to_bottom(self, percent: float=1.0, speed: int=5000) -> 'Shadowstep':
        """Perform a full-height vertical swipe from top to bottom.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        self.driver = WebDriverSingleton.get_driver()
        size = self.driver.get_window_size()
        width = size["width"]
        height = size["height"]

        return self.swipe(
            left=width // 2,
            top=0,
            width=width // 3,
            height=height,
            direction="down",
            percent=percent,
            speed=speed
        )

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def swipe_bottom_to_top(self, percent: float=1.0, speed: int=5000) -> 'Shadowstep':
        """Perform a full-height vertical swipe from bottom to top.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        self.driver = WebDriverSingleton.get_driver()
        size = self.driver.get_window_size()
        width = size["width"]
        height = size["height"]

        return self.swipe(
            left=width // 2,
            top=0,
            width=width // 3,
            height=height,
            direction="up",
            percent=percent,
            speed=speed
        )

    @fail_safe(retries=3, delay=0.5,
               raise_exception=ShadowstepException,
               exceptions=(NoSuchDriverException,
                           InvalidSessionIdException,
                           WebDriverException,
                           StaleElementReferenceException))
    def save_screenshot(self, path: str = '', filename: str = 'screenshot.png') -> bool:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        path_to_file = os.path.join(path, filename)
        with open(path_to_file, "wb") as f:
            f.write(self.get_screenshot())
        return True

    @fail_safe(retries=3, delay=0.5,
               raise_exception=ShadowstepException,
               exceptions=(NoSuchDriverException,
                           InvalidSessionIdException))
    def get_screenshot(self):
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        screenshot = self.driver.get_screenshot_as_base64().encode('utf-8')
        screenshot = base64.b64decode(screenshot)
        return screenshot

    @fail_safe(retries=3, delay=0.5,
               raise_exception=ShadowstepException,
               exceptions=(NoSuchDriverException,
                           InvalidSessionIdException))
    def save_source(self, path: str = '', filename: str = 'screenshot.png') -> bool:
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        path_to_file = os.path.join(path, filename)
        with open(path_to_file, "wb") as f:
            f.write(self.driver.page_source.encode("utf-8"))
        return True

    @fail_safe(retries=3, delay=0.5,
               raise_exception=ShadowstepException,
               exceptions=(NoSuchDriverException,
                           InvalidSessionIdException,
                           StaleElementReferenceException))
    def tap(self, x: int = None, y: int = None, duration: typing.Optional[float] = None) -> 'Shadowstep':
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver.tap([(x, y)], duration or 100)
        return self

    @fail_safe(retries=3, delay=0.5,
               raise_exception=ShadowstepException,
               exceptions=(NoSuchDriverException,
                           InvalidSessionIdException))
    def start_recording_screen(self) -> None:
        """Start screen recording using Appium driver."""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver.start_recording_screen()

    @fail_safe(retries=3, delay=0.5,
               raise_exception=ShadowstepException,
               exceptions=(NoSuchDriverException,
                           InvalidSessionIdException))
    def stop_recording_screen(self) -> bytes:
        """Stop screen recording and return video as bytes.

        Returns:
            bytes: Video recording in base64-decoded format.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        encoded = self.driver.stop_recording_screen()
        return base64.b64decode(encoded)

    def update_settings(self):
        """
        # TODO вынести в отдельный класс с прозрачным выбором settings (enum?)
        self.driver.update_settings(settings={'enableMultiWindows': True})

        https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/README.md?plain=1#L304
        ## Settings API

        UiAutomator2 driver supports Appium [Settings API](https://appium.io/docs/en/latest/guides/settings/).
        Along with the common settings the following driver-specific settings are currently available:

        Name | Type | Description
        --- | --- | ---
        actionAcknowledgmentTimeout | long | Maximum number of milliseconds to wait for an acknowledgment of generic uiautomator actions, such as clicks, text setting, and menu presses. The acknowledgment is an[AccessibilityEvent](http://developer.android.com/reference/android/view/accessibility/AccessibilityEvent.html") corresponding to an action, that lets the framework determine if the action was successful. Generally, this timeout should not be modified. `3000` ms by default
        allowInvisibleElements | boolean | Whether to include elements that are not visible to the user (e. g. whose `displayed` attribute is `false`) to the XML source tree. `false` by default
        ignoreUnimportantViews | boolean | Enables or disables layout hierarchy compression. If compression is enabled, the layout hierarchy derived from the Acessibility framework will only contain nodes that are important for uiautomator testing. Any unnecessary surrounding layout nodes that make viewing and searching the hierarchy inefficient are removed. `false` by default
        elementResponseAttributes | string | Comma-separated list of element attribute names to be included into findElement response. By default only element UUID is present there, but it is also possible to add the following items: `name`, `text`, `rect`, `enabled`, `displayed`, `selected`, `attribute/<element_attribute_name>`. It is required that `shouldUseCompactResponses` setting is set to `false` in order for this one to apply.
        enableMultiWindows | boolean | Whether to include all windows that the user can interact with (for example an on-screen keyboard) while building the XML page source (`true`). By default it is `false` and only the single active application window is included to the page source.
        enableTopmostWindowFromActivePackage | boolean | Whether to limit the window with the highest Z-order from the active package for interactions and page source retrieval. By default it is `false` and the active application window, which may not necessarily have this order, is included to the page source.
        enableNotificationListener | boolean | Whether to enable (`true`) toast notifications listener to listen for new toast notifications. By default this listener is enabled and UiAutomator2 server includes the text of toast messages to the generated XML page source, but not for longer than `3500` ms after the corresponding notification expires.
        keyInjectionDelay | long | Delay in milliseconds between key presses when injecting text input. 0 ms by default
        scrollAcknowledgmentTimeout | long | Timeout for waiting for an acknowledgement of an uiautomator scroll swipe action. The acknowledgment is an [AccessibilityEvent](http://developer.android.com/reference/android/view/accessibility/AccessibilityEvent.html), corresponding to the scroll action, that lets the framework determine if the scroll action was successful. Generally, this timeout should not be modified. `200` ms by default
        shouldUseCompactResponses | boolean | Used in combination with `elementResponseAttributes` setting. If set to `false` then the findElement response is going to include the items enumerated in `elementResponseAttributes` setting. `true` by default
        waitForIdleTimeout | long | Timeout used for waiting for the user interface to go into an idle state. By default, all core uiautomator objects except UiDevice will perform this wait before starting to search for the widget specified by the object's locator. Once the idle state is detected or the timeout elapses (whichever occurs first), the object will start to wait for the selector to find a match. Consider lowering the value of this setting if you experience long delays while interacting with accessibility elements in your test. `10000` ms by default.
        waitForSelectorTimeout | long | Timeout for waiting for a widget to become visible in the user interface so that it can be matched by a selector. Because user interface content is dynamic, sometimes a widget may not be visible immediately and won't be detected by a selector. This timeout allows the uiautomator framework to wait for a match to be found, up until the timeout elapses. This timeout is only applied to `android uiautomator` location strategy. `10000` ms by default
        normalizeTagNames | boolean | Being set to `true` applies unicode-to-ascii normalization of element class names used as tag names in the page source XML document. This is necessary if the application under test has some Unicode class names, which cannot be used as XML tag names by default due to known bugs in Android's XML DOM parser implementation. `false` by default
        shutdownOnPowerDisconnect | boolean | Whether to shutdown the server if the device under test is disconnected from a power source (e. g. stays on battery power). `true` by default.
        simpleBoundsCalculation | boolean | Whether to calculate element bounds as absolute values (`true`) or check if the element is covered by other elements and thus partially hidden (`false`, the default behaviour). Setting this setting to `true` helps to improve the performance of XML page source generation, but decreases bounds preciseness. Use with care.
        trackScrollEvents | boolean | Whether to apply scroll events tracking (`true`, the default value), so the server could calculate the value of `contentSize` attribute. Having this setting enabled may add delays to all scrolling actions.
        wakeLockTimeout | long | The timeout in milliseconds of wake lock that UiAutomator2 server acquires by default to prevent the device under test going to sleep while an automated test is running. By default the server acquires the lock for 24 hours. Setting this value to zero forces the server to release the wake lock.
        serverPort | int | The number of the port on the remote device to start UiAutomator2 server on. Do not mix this with `systemPort`, which is acquired on the host machine. Must be in range 1024..65535. `6790` by default
        mjpegServerPort | int | The number of the port on the remote device to start MJPEG screenshots broadcaster on. Must be in range 1024..65535. `7810` by default
        mjpegServerFramerate | int | The maximum count of screenshots per second taken by the MJPEG screenshots broadcaster. Must be in range 1..60. `10` by default
        mjpegScalingFactor | int | The percentage value used to apply downscaling on the screenshots generated by the MJPEG screenshots broadcaster. Must be in range 1..100. `50` is by default, which means that screenshots are downscaled to the half of their original size keeping their original proportions.
        mjpegServerScreenshotQuality | int | The percentage value used to apply lossy JPEG compression on the screenshots generated by the MJPEG screenshots broadcaster. Must be in range 1..100. `50` is by default, which means that screenshots are compressed to the half of their original quality.
        mjpegBilinearFiltering | boolean | Controls whether (`true`) or not (`false`, the default value) to apply bilinear filtering to MJPEG screenshots broadcaster resize algorithm. Enabling this flag may improve the quality of the resulting scaled bitmap, but may introduce a small performance hit.
        useResourcesForOrientationDetection | boolean | Defines the strategy used by UiAutomator2 server to detect the original device orientation. By default (`false` value) the server uses device rotation value for this purpose. Although, this approach may not work for some devices and a portrait orientation may erroneously be detected as the landscape one (and vice versa). In such case it makes sense to play with this setting.
        enforceXPath1 | boolean | Since UiAutomator2 driver version `4.25.0` XPath2 is set as the default and the recommended interpreter for the corresponding element locators. This interpreter is based on [Psychopath XPath2](https://wiki.eclipse.org/PsychoPathXPathProcessor) implementation, which is now a part of the Eclipse foundation. In most of the cases XPath1 locators are also valid XPath2 locators, so there should be no issues while locating elements. Although, since the XPath2 standard is much more advanced in comparison to the previous version, some [issues](https://github.com/appium/appium/issues/16142) are possible for more sophisticated locators, which cannot be fixed easily, as we depend on the third-party library mentioned above. Then try to workaround such issues by enforcing XPath1 usage (whose implementation is a part of the Android platform itself) and assigning this setting to `true`. Note, this setting is actually applied at the time when the element lookup by XPath is executed, so you could switch it on or off whenever needed throughout your automated testing session.
        limitXPathContextScope | boolean | Due to historical reasons UiAutomator2 driver limits scopes of element context-based searches to the parent element. This means a request like `findElement(By.xpath, "//root").findElement(By.xpath, "./..")` would always fail, because the driver only collects descendants of the `root` element for the destination XML source. The `limitXPathContextScope` setting being set to `false` changes that default behavior, so the collected page source includes the whole page source XML where `root` node is set as the search context. With that setting disabled the search query above should not fail anymore. Although, you must still be careful while building XPath requests for context-based searches with the `limitXPathContextScope` setting set to `false`. A request like `findElement(By.xpath, "//root").findElement(By.xpath, "//element")` would ignore the current context and search for `element` trough the whole page source. Use `.` notation to correct that behavior and only find `element` nodes which are descendants of the `root` node: `findElement(By.xpath, "//root").findElement(By.xpath, ".//element")`.
        disableIdLocatorAutocompletion | boolean | According to internal Android standards it is expected that each resource identifier is prefixed with `<packageName>:id/` string. This should guarantee uniqueness of each identifier. Although some application development frameworks ignore this rule and don't add such prefix automatically or, rather, let it up to the developer to decide how to represent their application identifiers. For example, [testTag modifier attribute in the Jetpack Compose](https://developer.android.com/reference/kotlin/androidx/compose/ui/platform/package-summary#(androidx.compose.ui.Modifier).testTag(kotlin.String)) with [testTagsAsResourceId](https://developer.android.com/reference/kotlin/androidx/compose/ui/semantics/package-summary#(androidx.compose.ui.semantics.SemanticsPropertyReceiver).testTagsAsResourceId()) allows developers to set an arbitrary string without the prefix rule. [Interoperability with UiAutomator](https://developer.android.com/jetpack/compose/testing) also explains how to set it. By default UIA2 driver adds the above prefixes automatically to all resource id locators if they are not prefixed, but in case of such "special" apps this feature might be disabled by assigning the setting to `true`.
        includeExtrasInPageSource | boolean | Whether to include `extras` element attribute in the XML page source result. Then, XPath locator can find the element by the extras. Its value consists of combined [getExtras](https://developer.android.com/reference/android/view/accessibility/AccessibilityNodeInfo#getExtras()) as `keys=value` pair separated by a semicolon (`;`), thus you may need to find the element with partial matching like `contains` e.g. `driver.find_element :xpath, '//*[contains(@extras, "AccessibilityNodeInfo.roleDescription=")]'`. The value could be huge if elements in the XML page source have large `extras`. It could affect the performance of XML page source generation.
        includeA11yActionsInPageSource | boolean | Whether to include `actions` element attribute in the XML page source result. Its value consists of names of available accessibility actions from [getActionList](https://developer.android.com/reference/android/view/accessibility/AccessibilityNodeInfo#getActionList()), separated by a comma. The value could be huge if elements in the XML page source have a lot of actions and could affect the performance of XML page source generation.
        snapshotMaxDepth | int | The number of maximum depth for the source tree snapshot. The default value is `70`. This number should be in range [1, 500]. A part of the elements source tree might be lost if the value is too low. Also, StackOverflowError might be caused if the value is too high (Issues [12545](https://github.com/appium/appium/issues/12545), [12892](https://github.com/appium/appium/issues/12892)). The available driver version is `2.27.0` or higher.
        currentDisplayId | int | The id of the display that should be used when finding elements, taking screenshots, etc. It can be found in the output of `adb shell dumpsys display` (search for `mDisplayId`). The default value is [Display.DEFAULT_DISPLAY](https://developer.android.com/reference/android/view/Display#DEFAULT_DISPLAY). **Please note that it is different from the physical display id, reported by `adb shell dumpsys SurfaceFlinger --display-id`**. **Additionally, please note that `-android uiautomator` (e.g., `UiSelector`) doesn't work predictably with multiple displays, as this is an Android limitation.** **Multi-display support is only available since Android R (30 API level).**
        """

    def _execute(self, name: str, params: Union[dict, list]) -> None:
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
        # I know it looks stupid, but I made a wrapper just in case
        self.driver.execute_script(name, params)
