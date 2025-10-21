"""Decorators for element.py module only.

The functionality of decorators can be duplicated with other decorators while violating the DRY principle. This was done consciously.
The current decorators are separated from the others so that the changes only apply to a specific module.
"""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, TypeVar, cast

from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)
from typing_extensions import ParamSpec

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepElementException,
)

P = ParamSpec("P")
T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])
SelfT = TypeVar("SelfT")


def fail_safe_element(
    retries: int = 3,
    delay: float = 0.5,
    raise_exception: type[Exception] | None = ShadowstepElementException,
) -> Callable[[F], F]:
    """Only for element.py module."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:  # noqa: C901, RUF100
            attempts = retries
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    self.get_driver()
                    self._get_web_element(locator=self.locator)  # type: ignore[reportPrivateUsage]
                    return func(self, *args, **kwargs)
                except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                    self.utilities.handle_driver_error(error)
                except StaleElementReferenceException as error:
                    self.logger.debug(error)
                    self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                    self.native = None
                    self.get_native()
                    continue
                except WebDriverException as error:
                    err_msg = str(error).lower()
                    if (
                        "instrumentation process is not running" in err_msg
                        or "socket hang up" in err_msg
                    ):
                        self.utilities.handle_driver_error(error)
                        continue
                    msg = f"Failed to execute '{func.__qualname__}' within timeout={self.timeout}, locator={self.locator}"
                    raise (raise_exception or ShadowstepElementException)(msg) from error
                if attempts > 0:
                    msg = f"Failed: '{func.__qualname__}', try again in {attempts} attempts"
                    self.logger.warning(msg)
                    attempts -= 1
                    time.sleep(delay)
                else:
                    break
            msg = f"Failed to execute '{func.__qualname__}' within timeout={self.timeout}, locator={self.locator}"
            raise (raise_exception or ShadowstepElementException)(msg)

        return cast("F", wrapper)

    return decorator


def fail_safe_element_check(
    retries: int = 3,
    delay: float = 0.5,
    raise_exception: type[Exception] | None = ShadowstepElementException,
) -> Callable[[F], F]:
    """Only for element.py module."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:  # noqa: C901, RUF100
            attempts = retries
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    return func(self, *args, **kwargs)
                except (NoSuchDriverException, InvalidSessionIdException, AttributeError) as error:
                    self.utilities.handle_driver_error(error)
                except StaleElementReferenceException as error:
                    self.logger.debug(error)
                    self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                    self.native = None
                    self.get_native()
                    continue
                except WebDriverException as error:
                    err_msg = str(error).lower()
                    if (
                        "instrumentation process is not running" in err_msg
                        or "socket hang up" in err_msg
                    ):
                        self.utilities.handle_driver_error(error)
                        continue
                    msg = f"Failed to execute '{func.__qualname__}' within timeout={self.timeout}, locator={self.locator}"
                    raise (raise_exception or ShadowstepElementException)(msg) from error
                if attempts > 0:
                    msg = f"Failed: '{func.__qualname__}', try again in {attempts} attempts"
                    self.logger.warning(msg)
                    attempts -= 1
                    time.sleep(delay)
                else:
                    break
            msg = f"Failed to execute '{func.__qualname__}' within timeout={self.timeout}, locator={self.locator}"
            raise (raise_exception or ShadowstepElementException)(msg)

        return cast("F", wrapper)

    return decorator
