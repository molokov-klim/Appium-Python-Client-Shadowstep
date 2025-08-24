# shadowstep/utils/conditions.py
from __future__ import annotations

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

Locator = tuple[str, str]

def visible(locator: Locator) -> bool:
    """Wraps EC.visibility_of_element_located."""
    return EC.visibility_of_element_located(locator) is not False

def not_visible(locator: Locator) -> bool:
    """Wraps EC.invisibility_of_element_located."""
    return EC.invisibility_of_element_located(locator) is not False

def clickable(locator: Locator | WebElement) -> bool:
    """Wraps EC.element_to_be_clickable."""
    return EC.element_to_be_clickable(locator) is not False

def not_clickable(locator: Locator | WebElement) -> bool:
    """Returns negation of EC.element_to_be_clickable."""
    return EC.element_to_be_clickable(locator) is not False

def present(locator: Locator) -> bool:
    """Wraps EC.presence_of_element_located."""
    return EC.presence_of_element_located(locator) is not False

def not_present(locator: Locator) -> bool:
    """Returns negation of EC.presence_of_element_located."""
    return EC.presence_of_element_located(locator) is not False
