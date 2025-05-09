import inspect
import logging
import time
import traceback
import typing
from typing import Union, Tuple, Dict, Optional, cast

from lxml import etree as ET

from appium.webdriver import WebElement
from icecream import ic
from selenium.common import NoSuchDriverException, InvalidSessionIdException, WebDriverException, \
    StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.types import WaitExcTypes
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from shadowstep.element.base import ElementBase
from shadowstep.utils import conditions
from shadowstep.utils.operations import dict_matches_subset
from shadowstep.utils.utils import find_coordinates_by_vector

# Configure the root logger (basic configuration)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeneralElementException(WebDriverException):
    """Raised when driver is not specified and cannot be located."""

    def __init__(
            self, msg: Optional[str] = None, screen: Optional[str] = None,
            stacktrace: Optional[typing.Sequence[str]] = None
    ) -> None:
        super().__init__(msg, screen, stacktrace)


class Element(ElementBase):
    """
    A class to represent a UI element in the Shadowstep application.
    !WARNING! USE XPATH STRATEGY ONLY !WARNING!
    """

    def __init__(self,
                 locator: Union[Tuple, Dict[str, str], 'Element'] = None,
                 base=None,
                 timeout: int = 30,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                 contains: bool = False):
        super().__init__(locator, base, timeout, poll_frequency, ignored_exceptions, contains)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"Initialized Element with locator: {self.locator}")

    def __repr__(self):
        return f"Element(locator={self.locator}"

    def get_element(self,
                    locator: Union[Tuple, Dict[str, str]],
                    timeout: int = 30,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: Optional[WaitExcTypes] = None,
                    contains: bool = False) -> Union['Element', None]:
        """
        Recursively search for an element inside the current one.

        Args:
            locator: Dict or Tuple describing target locator.
            timeout: How long to wait for the element.
            poll_frequency: Poll interval in seconds.
            ignored_exceptions: Exceptions to ignore while waiting.
            contains: Whether to use contains-based XPath instead of strict equality.

        Returns:
            Found Element or None.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        if isinstance(locator, Element):
            locator = locator.locator

        # XPath for parent
        parent_locator = self.handle_locator(self.locator, self.contains)

        # XPath for child (relative)
        pre_inner_locator = self.handle_locator(locator, contains)
        inner_path = pre_inner_locator[1].lstrip('/')  # Remove accidental `/` in front

        # ⛑ Гарантированная вложенность: parent//child
        if not inner_path.startswith("//"):
            inner_path = f"//{inner_path}"

        inner_locator = ('xpath', f"{parent_locator[1]}{inner_path}")

        return Element(locator=inner_locator,
                       base=self.base,
                       timeout=timeout,
                       poll_frequency=poll_frequency,
                       ignored_exceptions=ignored_exceptions,
                       contains=contains)

    def get_elements(
            self,
            locator: Union[Tuple, Dict[str, str], 'Element'],
            contains: bool = False,
            max_count: int = 10
    ) -> typing.Generator['Element', None, None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        if isinstance(locator, Element):
            locator = locator.locator
        resolved_locator = self.handle_locator(locator, contains)
        base_xpath = self._get_xpath()

        if not base_xpath:
            raise GeneralElementException("Unable to resolve base xpath")

        # Убираем финальные / у base_xpath и начальные у локатора
        base_xpath = base_xpath.rstrip('/')
        child_xpath = resolved_locator[1].lstrip('/')

        for index in range(1, max_count + 1):
            try:
                element = Element(
                    locator=('xpath', f"{base_xpath}//{child_xpath}[{index}]"),
                    base=self.base,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=contains
                )
                # Пробуем получить базовый атрибут
                if element.get_attribute("class") is None:
                    break
                yield element
            except NoSuchElementException:
                break
            except WebDriverException:
                break

    def get_elements_greedy(
            self,
            locator: Union[Tuple, Dict[str, str], 'Element'],
            contains: bool = False,
            timeout: int = 30,
    ) -> typing.List['Element']:
        """
        Returns a list of elements found using find_elements.
        This is a greedy method and fetches all matching elements immediately.

        Args:
            locator: Locator to search for child elements.
            contains: If True, performs partial match.
            timeout: Timeout to wait for elements.

        Returns:
            List of Element instances matching the locator.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            self._get_driver()
            if isinstance(locator, Element):
                locator = locator.locator
            resolved_locator = self.handle_locator(locator, contains)
            base_xpath = self._get_xpath()

            if not base_xpath:
                raise GeneralElementException("Unable to resolve base xpath")

            base_xpath = base_xpath.rstrip('/')
            child_xpath = resolved_locator[1].lstrip('/')

            # Совмещённый XPath для поиска потомков
            full_xpath = f"{base_xpath}//{child_xpath}"

            base_element = self._get_element(locator=self.locator)

            found_elements = base_element.find_elements('xpath', full_xpath)

            result = []
            for i in range(len(found_elements)):
                xpath = f"{full_xpath}[{i + 1}]"
                result.append(Element(
                    locator=('xpath', xpath),
                    base=self.base,
                    timeout=timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=contains
                ))

            return result
        except NoSuchDriverException as error:
            self._handle_driver_error(error)
            return []
        except InvalidSessionIdException as error:
            self._handle_driver_error(error)
            return []

    def get_attributes(self) -> Optional[Dict[str, str]]:
        """Fetch all XML attributes of the element by matching locator against page source.

        Returns:
            Optional[Dict[str, str]]: Dictionary of all attributes, or None if not found.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        # Convert locator to XPath expression (supports dict, tuple, UiSelector string)
        try:
            xpath_expr = self.locator_converter.to_xpath(self.locator)[1]
            if not xpath_expr:
                self.logger.error(f"Failed to resolve XPath from locator: {self.locator}")
                return None
            self.logger.debug(f"Resolved XPath: {xpath_expr}")
        except Exception as e:
            self.logger.error(f"Exception in to_xpath: {e}")
            return None


        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                page_source = self.driver.page_source
                parser = ET.XMLParser(recover=True)
                root = ET.fromstring(page_source.encode("utf-8"), parser=parser)

                matches = root.xpath(xpath_expr)
                if matches:
                    element = matches[0]
                    attrib = {k: str(v) for k, v in element.attrib.items()}
                    self.logger.debug(f"Matched attributes: {attrib}")
                    return attrib
                else:
                    self.logger.warning("No matches found for given XPath.")
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException:
                continue
            except ET.XPathEvalError as e:
                self.logger.error(f"XPathEvalError: {e}")
                self.logger.error(f"XPath: {xpath_expr}")
                return None
            except ET.XMLSyntaxError as e:
                self.logger.error(f"XMLSyntaxError: {e}")
                self.logger.debug(f"Raw page_source (first 500 chars):\n{page_source[:500]}")
                return None
            except UnicodeEncodeError as e:
                self.logger.error(f"UnicodeEncodeError in page_source: {e}")
                return None
            except Exception as e:
                self.logger.error(f"Unexpected error in get_attributes: {e}")
                self.logger.debug(f"page_source[:500]: {page_source[:500]}")
                continue
        self.logger.warning(f"Timeout exceeded ({self.timeout}s) without matching element.")
        return None

    def get_parent(self) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            xpath = self._get_xpath()
            if xpath is None:
                raise GeneralElementException("Unable to retrieve XPath of the element")
            xpath = xpath + "/.."
            return Element(locator=('xpath', xpath), base=self.base)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} NoSuchDriverException")
            self.base.reconnect()
            return None
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} InvalidSessionIdException")
            self.base.reconnect()
            return None

    def get_parents(self) -> typing.Generator['Element', None, None]:
        """Yields all parent elements lazily using XPath `ancestor::*`.

        Yields:
            Generator of Element instances representing each parent in the hierarchy.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        current_xpath = self._get_xpath()

        if not current_xpath:
            raise GeneralElementException("Cannot resolve current XPath")

        # Формируем базовый XPath, который захватывает всех родителей
        base_ancestor_xpath = f"{current_xpath}/ancestor::*"

        # Вместо вызова `find_elements`, просто итерируем индексы и строим XPath
        for index in range(1, 100):  # ограничим разумным пределом
            ancestor_xpath = f"{base_ancestor_xpath}[{index}]"
            element = Element(
                locator=('xpath', ancestor_xpath),
                base=self.base,
                timeout=self.timeout,
                poll_frequency=self.poll_frequency,
                ignored_exceptions=self.ignored_exceptions,
                contains=self.contains
            )
            # Проверяем существование элемента по какому-нибудь безопасному признаку
            try:
                if element.get_attribute("class") is None:
                    break
                yield element
            except NoSuchElementException:
                break
            except WebDriverException:
                break

    def get_sibling(self, locator: Union[Tuple, Dict[str, str], 'Element']) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        if isinstance(locator, Element):
            locator = locator.locator

        base_xpath = self._get_xpath()
        if not base_xpath:
            raise GeneralElementException("Unable to resolve current XPath")

        sibling_locator = self.handle_locator(locator, contains=self.contains)
        sibling_path = sibling_locator[1].lstrip('/')

        # Пытаемся найти первого совпадающего "соседа" справа
        xpath = f"{base_xpath}/following-sibling::{sibling_path}[1]"

        return Element(
            locator=('xpath', xpath),
            base=self.base,
            timeout=self.timeout,
            poll_frequency=self.poll_frequency,
            ignored_exceptions=self.ignored_exceptions,
            contains=self.contains
        )

    def get_siblings(self) -> typing.Generator['Element', None, None]:
        """Yields all sibling elements of the current element.

        Yields:
            Generator of Element instances that are siblings of the current element.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")

        base_xpath = self._get_xpath()
        if not base_xpath:
            raise GeneralElementException("Unable to resolve current XPath")

        # Сначала preceding-sibling (в обратном порядке)
        for index in range(1, 50):
            xpath = f"{base_xpath}/preceding-sibling::*[{index}]"
            sibling = Element(
                locator=('xpath', xpath),
                base=self.base,
                timeout=self.timeout,
                poll_frequency=self.poll_frequency,
                ignored_exceptions=self.ignored_exceptions,
                contains=self.contains
            )
            try:
                if sibling.get_attribute("class") is None:
                    break
                yield sibling
            except NoSuchElementException:
                break
            except WebDriverException:
                break

        # Затем following-sibling (в прямом порядке)
        for index in range(1, 50):
            xpath = f"{base_xpath}/following-sibling::*[{index}]"
            sibling = Element(
                locator=('xpath', xpath),
                base=self.base,
                timeout=self.timeout,
                poll_frequency=self.poll_frequency,
                ignored_exceptions=self.ignored_exceptions,
                contains=self.contains
            )
            try:
                if sibling.get_attribute("class") is None:
                    break
                yield sibling
            except NoSuchElementException:
                break
            except WebDriverException:
                break

    def get_cousin(
            self,
            ancestor_locator: Union[Tuple, Dict[str, str], 'Element'],
            cousin_locator: Union[Tuple, Dict[str, str], 'Element']
    ) -> Union['Element', None]:
        """Finds a cousin element (same depth relative to a shared ancestor).

        Args:
            ancestor_locator (Union[Tuple, Dict[str, str], 'Element']): The common ancestor to search from.
            cousin_locator (Union[Tuple, Dict[str, str], 'Element']): The target cousin element locator.

        Returns:
            Union['Element', None]: The cousin element found at the same depth.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            if isinstance(ancestor_locator, Element):
                ancestor_locator = ancestor_locator.locator
            if isinstance(cousin_locator, Element):
                cousin_locator = cousin_locator.locator

            # XPath текущего элемента
            current_xpath = self._get_xpath()
            if not current_xpath:
                raise GeneralElementException("Unable to resolve current XPath")

            # Количество узлов от текущего до корня
            depth = current_xpath.count('/')

            # XPath предка
            ancestor_xpath = self.handle_locator(ancestor_locator, contains=self.contains)[1]
            ancestor_xpath = ancestor_xpath.rstrip('/')

            # XPath кузена: тот же уровень вложенности
            cousin_relative = self.handle_locator(cousin_locator, contains=self.contains)[1].lstrip('/')
            cousin_xpath = f"{ancestor_xpath}//{cousin_relative}[{depth}]"

            return Element(
                locator=('xpath', cousin_xpath),
                base=self.base,
                timeout=self.timeout,
                poll_frequency=self.poll_frequency,
                ignored_exceptions=self.ignored_exceptions,
                contains=self.contains
            )
        except NoSuchDriverException as error:
            self._handle_driver_error(error)
        except InvalidSessionIdException as error:
            self._handle_driver_error(error)
        return None

    def from_parent(
            self,
            parent: Union[Tuple, Dict[str, str], 'Element'],
            locator: Union[Tuple, Dict[str, str], 'Element']
    ) -> Union['Element', None]:
        return self.get_cousin(parent,locator)

    def get_center(self, element: Optional[WebElement] = None) -> Optional[Tuple[int, int]]:
        """Get the center coordinates of the element.

        Args:
            element (Optional[WebElement]): Optional direct WebElement. If not provided, uses current locator.

        Returns:
            Optional[Tuple[int, int]]: (x, y) center point or None if element not found.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                if element is None:
                    element = self._get_element(
                        locator=self.locator,
                        timeout=self.timeout,
                        poll_frequency=self.poll_frequency,
                        ignored_exceptions=self.ignored_exceptions,
                        contains=self.contains
                    )
                coords = self.get_coordinates(element)
                if coords is None:
                    continue
                left, top, right, bottom = coords
                x = int((left + right) / 2)
                y = int((top + bottom) / 2)
                return x, y
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def get_coordinates(self, element: Optional[WebElement] = None) -> Optional[Tuple[int, int, int, int]]:
        """Get the bounding box coordinates of the element.

        Args:
            element (Optional[WebElement]): Element to get bounds from. If None, uses internal locator.

        Returns:
            Optional[Tuple[int, int, int, int]]: (left, top, right, bottom) or None.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                if element is None:
                    element = self._get_element(
                        locator=self.locator,
                        timeout=self.timeout,
                        poll_frequency=self.poll_frequency,
                        ignored_exceptions=self.ignored_exceptions,
                        contains=self.contains
                    )
                bounds = element.get_attribute('bounds')
                if not bounds:
                    continue
                left, top, right, bottom = map(int, bounds.strip("[]").replace("][", ",").split(","))
                return left, top, right, bottom
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    def get_attribute(self, name: str) -> Optional[Union[str, Dict]]:
        """Gets the specified attribute of the element.

        Args:
            name (str): Name of the attribute to retrieve.

        Returns:
            Optional[Union[str, Dict]]: Value of the attribute or None.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )
                return current_element.get_attribute(name)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name}('{name}') within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def get_property(self, name: str) -> Union[str, bool, dict, None]:
        """NOT IMPLEMENTED!
        Gets the given property of the element.

        Args:
            name (str): Name of the property to retrieve.

        Returns:
            Union[str, bool, dict, None]: Property value.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        self.logger.warning(f"Method {inspect.currentframe().f_code.co_name} is not implemented in UiAutomator2")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )
                return current_element.get_property(name)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def get_dom_attribute(self, name: str) -> str:
        """Gets the given attribute of the element. Unlike
        :func:`~selenium.webdriver.remote.BaseWebElement.get_attribute`, this
        method only returns attributes declared in the element's HTML markup.

        :Args:
            - name - Name of the attribute to retrieve.

        :Usage:
            ::

                text_length = target_element.get_dom_attribute("class")
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )
                return current_element.get_dom_attribute(name)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    def is_displayed(self) -> bool:
        """Whether the element is visible to a user.

        Returns:
            bool: True if the element is displayed on screen and visible to the user.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )
                return element.is_displayed()
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def is_visible(self) -> bool:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                screen_size = self.base.terminal.get_screen_resolution()  # Получаем размеры экрана
                screen_width = screen_size[0]  # Ширина экрана
                screen_height = screen_size[1]  # Высота экрана
                current_element = self._get_element(locator=self.locator,
                                                    timeout=self.timeout,
                                                    poll_frequency=self.poll_frequency,
                                                    ignored_exceptions=self.ignored_exceptions,
                                                    contains=self.contains)
                if current_element is None:
                    return False
                if not current_element.get_attribute('displayed') == 'true':
                    # Если элемент не отображается на экране
                    return False
                element_location = current_element.location  # Получаем координаты элемента
                element_size = current_element.size  # Получаем размеры элемента
                if (
                        element_location['y'] + element_size['height'] > screen_height or
                        element_location['x'] + element_size['width'] > screen_width or
                        element_location['y'] < 0 or
                        element_location['x'] < 0
                ):
                    # Если элемент находится за пределами экрана
                    return False
                # Если элемент находится на экране
                return True
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def is_not_within_screen(self) -> bool:
        """Checks whether the element is not within the visible screen bounds.

        Returns:
            bool: True if element is not displayed or outside screen bounds.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            return not self.is_visible()
        except GeneralElementException as error:
            self.logger.warning(f"is_not_within_screen fallback due to: {error}")
            return True
        except Exception as error:
            self.logger.warning(f"is_not_within_screen unexpected error: {error}")
            return True

    def is_selected(self) -> bool:
        """Returns whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.

        Returns:
            bool: True if the element is selected.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )
                return element.is_selected()
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def is_enabled(self) -> bool:
        """Returns whether the element is enabled.

        Returns:
            bool: True if the element is enabled.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )
                return element.is_enabled()
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def is_contains(self,
                    locator: Union[Tuple, Dict[str, str], 'Element'] = None,
                    contains: bool = False
                    ) -> bool:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                if isinstance(locator, Element):
                    locator = locator.locator
                child_element = self._get_element(locator=locator, contains=contains)
                if child_element is not None:
                    return True
                # Если элемент находится на экране
                return False
            except NoSuchElementException:
                return False
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def tap(self, duration: Optional[int] = None) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                x, y = self.get_center()
                if x is None or y is None:
                    continue
                self.driver.tap(positions=[(x, y)], duration=duration)
                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}\n{duration}",
            stacktrace=traceback.format_stack()
        )

    def tap_and_move(
            self,
            locator: Union[Tuple, WebElement, 'Element', Dict[str, str], str] = None,
            x: int = None,
            y: int = None,
            direction: int = None,
            distance: int = None,
    ) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                if isinstance(locator, Element):
                    locator = locator.locator
                # Получение координат центра исходного элемента
                x1, y1 = self.get_center()

                # Настройка жеста
                actions = ActionChains(self.driver)
                actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
                actions.w3c_actions.pointer_action.move_to_location(x1, y1)
                actions.w3c_actions.pointer_action.pointer_down()

                # === Прямое указание координат ===
                if x is not None and y is not None:
                    actions.w3c_actions.pointer_action.move_to_location(x, y)
                    actions.w3c_actions.pointer_action.pointer_up()
                    actions.perform()
                    return cast('Element', self)

                # === Перемещение к другому элементу ===
                if locator is not None:
                    target_element = self._get_element(locator=locator)
                    x, y = self.get_center(target_element)
                    actions.w3c_actions.pointer_action.move_to_location(x, y)
                    actions.w3c_actions.pointer_action.pointer_up()
                    actions.perform()
                    return cast('Element', self)
                # === Перемещение по вектору направления ===
                if direction is not None and distance is not None:
                    width, height = self.base.terminal.get_screen_resolution()
                    x2, y2 = find_coordinates_by_vector(width=width, height=height,
                                                        direction=direction, distance=distance,
                                                        start_x=x1, start_y=y1)
                    actions.w3c_actions.pointer_action.move_to_location(x2, y2)
                    actions.w3c_actions.pointer_action.pointer_up()
                    actions.perform()
                    return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
        # === Недостаточно данных для действия ===
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}\n{locator=}\n{x=}\n{y=}\n{direction}\n{distance}\n",
            stacktrace=traceback.format_stack()
        )

    def click(self, duration: int = None) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                self._get_element(locator=self.locator)
                if duration is None:
                    self._mobile_gesture('mobile: clickGesture',
                                         {'elementId': self.id})
                else:
                    self._mobile_gesture('mobile: longClickGesture',
                                         {'elementId': self.id, 'duration': duration})
                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}\n{duration}",
            stacktrace=traceback.format_stack()
        )

    def click_double(self) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                self._get_element(locator=self.locator)
                self._mobile_gesture('mobile: doubleClickGesture',
                                     {'elementId': self.id})
                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def drag(self, end_x: int, end_y: int, speed: int = 2500) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                self._get_element(locator=self.locator)
                self._mobile_gesture('mobile: dragGesture',
                                     {'elementId': self.id,
                                      'endX': end_x,
                                      'endY': end_y,
                                      'speed': speed})
                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def fling_up(self, speed: int = 2500) -> Union['Element', None]:
        return self._fling(speed=speed, direction='up')

    def fling_down(self, speed: int = 2500) -> Union['Element', None]:
        return self._fling(speed=speed, direction='down')

    def fling_left(self, speed: int = 2500) -> Union['Element', None]:
        return self._fling(speed=speed, direction='left')

    def fling_right(self, speed: int = 2500) -> Union['Element', None]:
        return self._fling(speed=speed, direction='right')

    def _fling(self, speed: int, direction: str) -> Union['Element', None]:
        """
        direction: Direction of the fling. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
        speed: The speed at which to perform this gesture in pixels per second. The value must be greater than the minimum fling velocity for the given view (50 by default). The default value is 7500 * displayDensity
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-flinggesture
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                self._get_element(locator=self.locator)
                self._mobile_gesture('mobile: flingGesture',
                                     {'elementId': self.id,
                                      'direction': direction,
                                      'speed': speed})
                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def scroll_down(self, percent: int = 10, speed: int = 2000) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        return self._scroll(direction='down', percent=percent, speed=speed)

    def scroll_up(self, percent: int = 10, speed: int = 2000) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        return self._scroll(direction='up', percent=percent, speed=speed)

    def scroll_left(self, percent: int = 10, speed: int = 2000) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        return self._scroll(direction='left', percent=percent, speed=speed)

    def scroll_right(self, percent: int = 10, speed: int = 2000) -> Union['Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        return self._scroll(direction='right', percent=percent, speed=speed)

    def _scroll(self, direction: str, percent: int, speed: int) -> Union['Element', None]:
        """
        direction: Scrolling direction. Mandatory value. Acceptable values are: up, down, left and right (case insensitive)
        percent: The size of the scroll as a percentage of the scrolling area size. Valid values must be float numbers greater than zero, where 1.0 is 100%. Mandatory value.
        speed: The speed at which to perform this gesture in pixels per second. The value must not be negative. The default value is 5000 * displayDensity
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollgesture
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                self._get_element(locator=self.locator)
                self._mobile_gesture('mobile: scrollGesture',
                                     {'elementId': self.id,
                                      'percent': percent,
                                      'direction': direction,
                                      'speed': speed})
                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def scroll_to_bottom(self, locator: Union[Tuple, Dict[str, str], str, WebElement, 'Element'] = None) -> Union[
        'Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        last_child = None
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                if isinstance(locator, Element):
                    locator = locator.locator
                if not locator:
                    class_name = self._get_first_child_class()
                    if not class_name:
                        raise GeneralElementException("Unable to determine first child class")
                    locator = {'class': class_name}
                child = self._get_element(locator=locator)
                if last_child is not None and child.get_attribute('bounds') == last_child.get_attribute('bounds'):
                    self.scroll_down()
                    return cast('Element', self)
                last_child = child
                self.scroll_down()
            except StaleElementReferenceException:
                continue
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def scroll_to_top(self, locator: Union[Tuple, Dict[str, str], str, WebElement, 'Element'] = None) -> Union[
        'Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        last_child = None
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                if isinstance(locator, Element):
                    locator = locator.locator
                if not locator:
                    class_name = self._get_first_child_class()
                    if not class_name:
                        raise GeneralElementException("Unable to determine first child class")
                    locator = {'class': class_name}
                child = self._get_element(locator=locator)
                if last_child is not None and child.get_attribute('bounds') == last_child.get_attribute('bounds'):
                    self.scroll_up()
                    return cast('Element', self)
                last_child = child
                self.scroll_up()
            except StaleElementReferenceException:
                continue
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def scroll_to_element(self, locator: Union['Element', Dict[str, str], Tuple[str, str]], max_swipes: int = 30) -> \
    Union[
        'Element', None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()
        if isinstance(locator, Element):
            locator = locator.locator
        if isinstance(locator, dict):
            selector = self.locator_converter.to_uiselector(locator)
        elif isinstance(locator, tuple):
            selector = self.locator_converter.to_uiselector(locator)
        else:
            raise GeneralElementException("Only dictionary locators are supported")

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                self.driver.execute_script("mobile: scroll", {
                    "elementId": self.id,
                    "strategy": "-android uiautomator",
                    "selector": selector,
                    "maxSwipes": max_swipes
                })
                found = self.base.get_element(locator)
                if found.is_visible():
                    return cast('Element', found)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
            except Exception as error:
                # Some instability detected, information gathering required
                self.logger.error(error)
                self.logger.error(type(error))
                self.logger.error(traceback.format_stack())
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to scroll to element with locator: {locator}",
            stacktrace=traceback.format_stack()
        )

    def zoom(self, percent: float = 0.75, speed: int = 2500) -> Union['Element', None]:
        """
        Performs a pinch-open (zoom) gesture on the element.

        Args:
            percent (float): Size of the pinch as a percentage of the pinch area size (0.0 to 1.0).
            speed (int): Speed in pixels per second.

        Returns:
            Element: Self instance on success.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                self._get_element(locator=self.locator)

                self._mobile_gesture('mobile: pinchOpenGesture', {
                    'elementId': self.id,
                    'percent': percent,
                    'speed': speed
                })

                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def unzoom(self, percent: float = 0.75, speed: int = 2500) -> Union['Element', None]:
        """
        Performs a pinch-close (unzoom) gesture on the element.

        Args:
            percent (float): Size of the pinch as a percentage of the pinch area size (0.0 to 1.0).
            speed (int): Speed in pixels per second.

        Returns:
            Element: Self instance on success.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                self._get_element(locator=self.locator)

                self._mobile_gesture('mobile: pinchCloseGesture', {
                    'elementId': self.id,
                    'percent': percent,
                    'speed': speed
                })

                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def swipe_up(self, percent: float = 0.75, speed: int = 5000) -> Union['Element', None]:
        """Performs a swipe up gesture on the current element."""
        return self.swipe(direction='up', percent=percent, speed=speed)

    def swipe_down(self, percent: float = 0.75, speed: int = 5000) -> Union['Element', None]:
        """Performs a swipe down gesture on the current element."""
        return self.swipe(direction='down', percent=percent, speed=speed)

    def swipe_left(self, percent: float = 0.75, speed: int = 5000) -> Union['Element', None]:
        """Performs a swipe left gesture on the current element."""
        return self.swipe(direction='left', percent=percent, speed=speed)

    def swipe_right(self, percent: float = 0.75, speed: int = 5000) -> Union['Element', None]:
        """Performs a swipe right gesture on the current element."""
        return self.swipe(direction='right', percent=percent, speed=speed)

    def swipe(self, direction: str, percent: float = 0.75, speed: int = 5000) -> Union['Element', None]:
        """
        Performs a swipe gesture on the current element.

        Args:
            direction (str): Swipe direction. Acceptable values: 'up', 'down', 'left', 'right'.
            percent (float): The size of the swipe as a percentage of the swipe area size (0.0 - 1.0).
            speed (int): Speed in pixels per second (default: 5000).

        Returns:
            Element: Self instance on success.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                self._mobile_gesture("mobile: swipeGesture", {
                    'elementId': self.id,
                    "direction": direction.lower(),
                    "percent": percent,
                    "speed": speed
                })

                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to {inspect.currentframe().f_code.co_name} within {self.timeout=} {direction=} {percent=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    def clear(self) -> Union['Element', None]:
        """Clears text content of the element (e.g. input or textarea).

        Returns:
            Element: Self instance if successful.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                current_element.clear()
                return cast('Element', self)
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to clear element within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    @property
    def location_in_view(self) -> Optional[dict]:
        """Gets the location of an element relative to the view.

        Returns:
            dict: Dictionary with keys 'x' and 'y', or None on failure.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return current_element.location_in_view  # Appium WebElement property
            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to get location_in_view within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    def set_value(self, value: str) -> Union['Element', None]:
        """NOT IMPLEMENTED!
        Set the value on this element in the application.

        Args:
            value: The value to be set.

        Returns:
            Element: Self instance on success.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        self.logger.warning(f"Method {inspect.currentframe().f_code.co_name} is not implemented in UiAutomator2")

        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                element.set_value(value)
                return cast('Element', self)

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to set_value({value}) within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    # Override
    def send_keys(self, *value: str) -> Union['Element', None]:
        """Simulates typing into the element.

        Args:
            value: One or more strings to type.

        Returns:
            Element: Self instance on success.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        text = "".join(value)

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                element.send_keys(text)
                return cast('Element', self)

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to send_keys({text}) within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def tag_name(self) -> Optional[str]:
        """This element's ``tagName`` property.

        Returns:
            Optional[str]: The tag name of the element, or None if not retrievable.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return element.tag_name

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to retrieve tag_name within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def text(self) -> str:
        """The text of the element.

        Returns:
            str: Text content of the element.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return element.text

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to retrieve text within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def submit(self) -> Union['Element', None]:
        """NOT IMPLEMENTED!
        Submits a form element.

        Returns:
            Element: Self instance on success.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        self.logger.warning(f"Method {inspect.currentframe().f_code.co_name} is not implemented in UiAutomator2")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )
                element.submit()
                return cast('Element', self)

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to submit element within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def shadow_root(self) -> ShadowRoot:
        """NOT IMPLEMENTED!
        Returns the shadow root of the current element if available.

        Returns:
            ShadowRoot: Shadow DOM root attached to the element.

        Raises:
            GeneralElementException: If shadow root is not available or an error occurs.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        self.logger.warning(f"Method {inspect.currentframe().f_code.co_name} is not implemented in UiAutomator2")

        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()
                element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )
                return element.shadow_root

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except WebDriverException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to retrieve shadow_root within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def location_once_scrolled_into_view(self) -> dict:
        """NOT IMPLEMENTED
        Gets the top-left corner location of the element after scrolling it into view.

        Returns:
            dict: Dictionary with keys 'x' and 'y' indicating location on screen.

        Raises:
            GeneralElementException: If element could not be scrolled into view or location determined.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        self.logger.warning(f"Method {inspect.currentframe().f_code.co_name} is not implemented in UiAutomator2")

        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return current_element.location_once_scrolled_into_view

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except WebDriverException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to get location_once_scrolled_into_view within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def size(self) -> dict:
        """Returns the size of the element.

        Returns:
            dict: Dictionary with keys 'width' and 'height'.

        Raises:
            GeneralElementException: If size cannot be determined.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return current_element.size

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
            except WebDriverException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to retrieve size within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def value_of_css_property(self, property_name: str) -> str:
        """NOT IMPLEMENTED!
        Returns the value of a CSS property.

        Args:
            property_name (str): The name of the CSS property.

        Returns:
            str: The value of the CSS property.

        Raises:
            GeneralElementException: If value could not be retrieved within timeout.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        self.logger.warning(f"Method {inspect.currentframe().f_code.co_name} is not implemented in UiAutomator2")

        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return current_element.value_of_css_property(property_name)

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
            except WebDriverException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to retrieve CSS property '{property_name}' within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def location(self) -> dict:
        """NOT IMPLEMENTED
        The location of the element in the renderable canvas.

        Returns:
            dict: Dictionary with 'x' and 'y' coordinates of the element.

        Raises:
            GeneralElementException: If location could not be retrieved within timeout.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        self.logger.warning(f"Method {inspect.currentframe().f_code.co_name} is not implemented in UiAutomator2")

        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return current_element.location

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
            except WebDriverException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to retrieve location within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def rect(self) -> dict:
        """A dictionary with the size and location of the element.

        Returns:
            dict: Dictionary with keys 'x', 'y', 'width', 'height'.

        Raises:
            GeneralElementException: If rect could not be retrieved within timeout.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return current_element.rect

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
            except WebDriverException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to retrieve rect within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def aria_role(self) -> Optional[str]:
        """Returns the ARIA role of the current web element.

        Returns:
            str: The ARIA role of the element, or None if not found.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return current_element.aria_role

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
            except WebDriverException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to retrieve aria_role within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def accessible_name(self) -> Optional[str]:
        """Returns the ARIA Level (accessible name) of the current web element.

        Returns:
            Optional[str]: Accessible name or None if not found.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return current_element.accessible_name

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
            except WebDriverException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to retrieve accessible_name within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def screenshot_as_base64(self) -> Optional[str]:
        """Gets the screenshot of the current element as a base64 encoded string.

        Returns:
            Optional[str]: Base64-encoded screenshot string or None if failed.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return current_element.screenshot_as_base64

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
            except WebDriverException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to get screenshot_as_base64 within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    @property
    def screenshot_as_png(self) -> Optional[bytes]:
        """Gets the screenshot of the current element as binary data.

        Returns:
            Optional[bytes]: PNG-encoded screenshot bytes or None if failed.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return current_element.screenshot_as_png

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
            except WebDriverException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to get screenshot_as_png within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def save_screenshot(self, filename: str) -> bool:
        """Saves a screenshot of the current element to a PNG image file.

        Args:
            filename (str): The full path to save the screenshot. Should end with `.png`.

        Returns:
            bool: True if successful, False otherwise.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self._get_driver()

                current_element = self._get_element(
                    locator=self.locator,
                    timeout=self.timeout,
                    poll_frequency=self.poll_frequency,
                    ignored_exceptions=self.ignored_exceptions,
                    contains=self.contains
                )

                return current_element.screenshot(filename)

            except NoSuchDriverException as error:
                self._handle_driver_error(error)
            except InvalidSessionIdException as error:
                self._handle_driver_error(error)
            except AttributeError as error:
                self._handle_driver_error(error)
            except StaleElementReferenceException as error:
                self._handle_driver_error(error)
            except IOError as error:
                self.logger.error(f"IOError while saving screenshot to {filename}: {error}")
                return False
            except WebDriverException as error:
                self._handle_driver_error(error)

        raise GeneralElementException(
            msg=f"Failed to save screenshot to {filename} within {self.timeout=}",
            stacktrace=traceback.format_stack()
        )

    def _handle_driver_error(self, error: Exception) -> None:
        self.logger.error(f"{inspect.currentframe().f_code.co_name} {error}")
        self.base.reconnect()
        time.sleep(0.3)

    def _mobile_gesture(self, name: str, params: Union[dict, list]) -> None:
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
        self.driver.execute_script(name, params)

    def _ensure_session_alive(self) -> None:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            self._get_driver()
        except NoSuchDriverException:
            self.logger.warning("Reconnecting driver due to session issue")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.warning("Reconnecting driver due to session issue")
            self.base.reconnect()

    def _get_first_child_class(self, tries: int = 3) -> str:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        for _ in range(tries):
            try:
                parent_element = self
                parent_class = parent_element.get_attribute('class')
                child_elements = parent_element.get_elements(("xpath", "//*[1]"))
                for i, child_element in enumerate(child_elements):
                    child_class = child_element.get_attribute('class')
                    if parent_class != child_class:
                        return str(child_class)
            except StaleElementReferenceException:
                continue

    def _get_xpath(self) -> Union[str, None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        locator = self.handle_locator(self.locator, self.contains)
        if locator[0] == 'xpath':
            return locator[1]
        return self._get_xpath_by_driver()

    def _get_xpath_by_driver(self) -> Union[str, None]:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            xpath = "//"
            attrs = self.get_attributes()
            if not attrs:
                raise GeneralElementException("Failed to retrieve attributes for XPath construction.")

            element_type = attrs.get('class')
            except_attrs = ['hint', 'selection-start', 'selection-end', 'extras']

            # Start XPath with element class or wildcard
            if element_type:
                xpath += element_type
            else:
                xpath += "*"
            for key, value in attrs.items():
                if key in except_attrs:
                    continue
                if value is None:
                    xpath += f"[@{key}]"
                elif "'" in value and '"' not in value:
                    xpath += f'[@{key}="{value}"]'
                elif '"' in value and "'" not in value:
                    xpath += f"[@{key}='{value}']"
                elif "'" in value and '"' in value:
                    parts = value.split('"')
                    escaped = 'concat(' + ', '.join(
                        f'"{part}"' if i % 2 == 0 else "'\"'" for i, part in enumerate(parts)) + ')'
                    xpath += f"[@{key}={escaped}]"
                else:
                    xpath += f"[@{key}='{value}']"
            return xpath
        except AttributeError as e:
            self.logger.error("Ошибка при формировании XPath: {}".format(str(e)))
        except KeyError as e:
            self.logger.error("Ошибка при формировании XPath: {}".format(str(e)))
        except WebDriverException as e:
            self.logger.error("Неизвестная ошибка при формировании XPath: {}".format(str(e)))
        return None

    def _build_element_xpath(self, base_element: WebElement, index: int) -> str:
        """
        Constructs XPath for a child element at a specific index.
        Used for greedy element wrapping.

        Args:
            base_element: Parent WebElement.
            index: Index of the child element (1-based).

        Returns:
            XPath string to access the element.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        parent_xpath = self._get_xpath()
        return f"{parent_xpath}/*[{index}]"

    def wait(self, timeout: int = 10, poll_frequency: float = 0.5) -> bool:
        """Waits for the element to appear (present in DOM).

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Frequency of polling.

        Returns:
            bool: True if the element is found, False otherwise.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            resolved_locator = self.handle_locator(self.locator, self.contains)
            if not resolved_locator:
                self.logger.error("Resolved locator is None or invalid")
                return False
            WebDriverWait(self.base.driver, timeout, poll_frequency).until(
                conditions.present(resolved_locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_visible(self, timeout: int = 10, poll_frequency: float = 0.5) -> bool:
        """Waits until the element is visible.

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Frequency of polling.

        Returns:
            bool: True if the element becomes visible, False otherwise.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            resolved_locator = self.handle_locator(self.locator, self.contains)
            if not resolved_locator:
                self.logger.error("Resolved locator is None or invalid")
                return False

            WebDriverWait(self.base.driver, timeout, poll_frequency).until(
                conditions.visible(resolved_locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_clickable(self, timeout: int = 10, poll_frequency: float = 0.5) -> bool:
        """Waits until the element is clickable.

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Frequency of polling.

        Returns:
            bool: True if the element becomes clickable, False otherwise.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            resolved_locator = self.handle_locator(self.locator, self.contains)
            if not resolved_locator:
                self.logger.error("Resolved locator is None or invalid")
                return False

            WebDriverWait(self.base.driver, timeout, poll_frequency).until(
                conditions.clickable(resolved_locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_not(self, timeout: int = 10, poll_frequency: float = 0.5) -> bool:
        """Waits until the element is no longer present in the DOM.

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Frequency of polling.

        Returns:
            bool: True if the element disappears, False otherwise.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            resolved_locator = self.handle_locator(self.locator, self.contains)
            if not resolved_locator:
                self.logger.error("Resolved locator is None or invalid")
                return True
            WebDriverWait(self.base.driver, timeout, poll_frequency).until(
                conditions.not_present(resolved_locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_not_visible(self, timeout: int = 10, poll_frequency: float = 0.5) -> bool:
        """Waits until the element becomes invisible.

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Polling frequency.

        Returns:
            bool: True if the element becomes invisible, False otherwise.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            resolved_locator = self.handle_locator(self.locator, self.contains)
            if not resolved_locator:
                self.logger.error("Resolved locator is None or invalid")
                return True
            WebDriverWait(self.base.driver, timeout, poll_frequency).until(
                conditions.not_visible(resolved_locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_not_clickable(self, timeout: int = 10, poll_frequency: float = 0.5) -> bool:
        """Waits until the element becomes not clickable.

        Args:
            timeout (int): Timeout in seconds.
            poll_frequency (float): Polling frequency.

        Returns:
            bool: True if the element becomes not clickable, False otherwise.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            resolved_locator = self.handle_locator(self.locator, self.contains)
            if not resolved_locator:
                self.logger.error("Resolved locator is None or invalid")
                return True
            WebDriverWait(self.base.driver, timeout, poll_frequency).until(
                conditions.not_clickable(resolved_locator)
            )
            return True
        except TimeoutException:
            return False
