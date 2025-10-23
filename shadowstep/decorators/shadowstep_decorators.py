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
    WebDriverException,
)
from typing_extensions import ParamSpec

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepException,
)

P = ParamSpec("P")
T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])
SelfT = TypeVar("SelfT")


def fail_safe_shadowstep(
    retries: int = 3,
    delay: float = 0.5,
    raise_exception: type[Exception] | None = ShadowstepException,
) -> Callable[[F], F]:
    """Only for shadowstep.py module."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:  # noqa: C901, RUF100
            attempts = retries
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    return func(self, *args, **kwargs)
                except (NoSuchDriverException, InvalidSessionIdException):
                    self.reconnect()
                    time.sleep(0.3)
                except WebDriverException as error:
                    err_msg = str(error).lower()
                    if (
                        "instrumentation process is not running" in err_msg
                        or "socket hang up" in err_msg
                    ):
                        self.reconnect()
                        time.sleep(0.3)
                        continue
                    msg = f"Failed to execute '{func.__qualname__}' within timeout={self.timeout}"
                    raise (raise_exception or ShadowstepException)(msg) from error
                if attempts > 0:
                    msg = f"Failed: '{func.__qualname__}', try again in {attempts} attempts"
                    self.logger.warning(msg)
                    attempts -= 1
                    time.sleep(delay)
                else:
                    break
            msg = f"Failed to execute '{func.__qualname__}' within timeout={self.timeout}"
            raise (raise_exception or ShadowstepException)(msg)

        return cast("F", wrapper)

    return decorator
