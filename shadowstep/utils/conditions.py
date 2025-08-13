# shadowstep/utils/conditions.py

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from typing import Tuple, Union, Callable

Locator = Tuple[str, str]


def visible(locator: Locator) -> Callable:
    """Wraps EC.visibility_of_element_located."""
    return EC.visibility_of_element_located(locator)


def not_visible(locator: Locator) -> Callable:
    """Wraps EC.invisibility_of_element_located."""
    return EC.invisibility_of_element_located(locator)


def clickable(locator: Union[Locator, WebElement]) -> Callable:
    """Wraps EC.element_to_be_clickable."""
    return EC.element_to_be_clickable(locator)


def not_clickable(locator: Union[Locator, WebElement]) -> Callable:
    """Returns negation of EC.element_to_be_clickable."""
    def _predicate(driver):
        result = EC.element_to_be_clickable(locator)(driver)
        return not bool(result)
    return _predicate


def present(locator: Locator) -> Callable:
    """Wraps EC.presence_of_element_located."""
    return EC.presence_of_element_located(locator)


def not_present(locator: Locator) -> Callable:
    """Returns negation of EC.presence_of_element_located."""
    def _predicate(driver):
        try:
            EC.presence_of_element_located(locator)(driver)
            return False
        except Exception:
            return True
    return _predicate
