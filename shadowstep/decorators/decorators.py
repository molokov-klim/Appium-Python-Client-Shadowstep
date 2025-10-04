"""Decorators module for Shadowstep framework.

This module provides various decorators for enhancing method functionality
including retry logic, logging, timing, and Allure reporting integration.
"""

from __future__ import annotations

import base64
import functools
import inspect
import logging
import time
import traceback
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from types import ModuleType
from typing import Any, TypeVar, cast

import allure
from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
)
from typing_extensions import Concatenate, ParamSpec


# Type variables for better type safety
P = ParamSpec("P")
T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])
SelfT = TypeVar("SelfT")

# Default exceptions for fail_safe decorator
DEFAULT_EXCEPTIONS: tuple[type[Exception], ...] = (
    NoSuchDriverException,
    InvalidSessionIdException,
    StaleElementReferenceException,
)


def fail_safe(  # noqa: C901, PLR0913
        retries: int = 3,
        delay: float = 0.5,
        raise_exception: type[Exception] | None = None,
        fallback: Any = None,
        exceptions: tuple[type[Exception], ...] = DEFAULT_EXCEPTIONS,
        log_args: bool = False,  # noqa: FBT001, FBT002
) -> Callable[[F], F]:
    """Retry a method call on specified exceptions.

    Args:
        retries: Number of retry attempts.
        delay: Delay between retries in seconds.
        raise_exception: Custom exception type to raise on final failure.
        fallback: Fallback value to return on failure if no exception is raised.
        exceptions: Tuple of exception types to catch and retry.
        log_args: Whether to log function arguments on failure.

    Returns:
        Decorated function with retry logic.

    Example:
        @fail_safe(retries=3, delay=1.0)
        def my_method(self):
            # This method will be retried up to 3 times
            pass

    """

    def decorator(func: F) -> F:  # noqa: C901
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:  # noqa: C901
            last_exc: Exception | None = None
            for attempt in range(1, retries + 1):
                try:
                    if not self.is_connected():
                        self.logger.warning(
                            "[fail_safe] Not connected before %s(), reconnecting...",
                            func.__name__,
                        )
                        self.logger.warning("last_exc=%s", last_exc)
                        self.reconnect()
                    return func(self, *args, **kwargs)
                except exceptions as e:  # noqa: PERF203
                    last_exc = e
                    method = func.__name__
                    self.logger.warning(
                        "[fail_safe] %s failed on attempt %s: %s - %s",
                        method,
                        attempt,
                        type(e).__name__,
                        e,
                    )
                    if log_args:
                        def format_arg(arg: Any) -> str:
                            if arg is self:
                                return f"<{self.__class__.__name__} id={id(self)}>"
                            arg_repr = repr(arg)
                            max_repr_length = 200
                            if len(arg_repr) > max_repr_length:
                                return arg_repr[:max_repr_length-3] + "..."
                            return arg_repr

                        formatted_args = [format_arg(self)] + [format_arg(a) for a in args]
                        formatted_args += [f"{k}={format_arg(v)}" for k, v in kwargs.items()]
                        self.logger.debug("[fail_safe] args: %s", formatted_args)
                    self.logger.debug(
                        "[fail_safe] stack:\n%s",
                        "".join(traceback.format_stack(limit=5)),
                    )
                    if not self.is_connected():
                        self.logger.warning(
                            "[fail_safe] Disconnected after exception in %s, reconnecting...",
                            method,
                        )
                        self.reconnect()
                    time.sleep(delay)
                except Exception as e:  # noqa: BLE001
                    self.logger.error(  # noqa: TRY400
                        "[fail_safe] Unexpected error in %s: %s - %s",
                        func.__name__,
                        type(e).__name__,
                        e,
                    )
                    self.logger.debug("Stack:\n%s", "".join(traceback.format_stack(limit=5)))
                    last_exc = e
                    break
            self.logger.error("[fail_safe] %s failed after %s attempts", func.__name__, retries)
            if last_exc:
                tb = "".join(
                    traceback.format_exception(
                        type(last_exc), last_exc, last_exc.__traceback__,
                    ),
                )
                self.logger.error("[fail_safe] Final exception:\n%s", tb)
            if raise_exception and last_exc:
                error_msg = f"{func.__name__} failed after {retries} attempts"
                raise raise_exception(error_msg) from last_exc
            if raise_exception:
                error_msg = f"{func.__name__} failed after {retries} attempts"
                raise raise_exception(error_msg)
            if fallback is not None:
                return fallback
            if last_exc:
                raise last_exc
            error_msg = f"{func.__name__} failed after {retries} attempts"
            raise RuntimeError(error_msg)

        return cast("F", wrapper)

    return decorator


def retry(max_retries: int = 3, delay: float = 1.0) -> Callable[[F], F]:
    """Create a retry decorator that repeats method execution if it returns False or None.

    Args:
        max_retries: Number of attempts (default: 3).
        delay: Delay in seconds between attempts (default: 1.0).

    Returns:
        A decorator that adds retry logic to a function.

    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result: Any = None
            for _ in range(max_retries):
                result = func(*args, **kwargs)
                if result is not None and result is not False:
                    return result
                time.sleep(delay)
            return result

        return cast("F", wrapper)

    return decorator


def time_it(func: F) -> F:
    """Measure method execution time.

    Args:
        func: Function to decorate.

    Returns:
        Decorated function that prints execution time.

    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time:.2f} seconds")  # noqa: T201
        return result

    return cast("F", wrapper)


def step_info(
        my_str: str,
) -> Callable[
    [Callable[Concatenate[SelfT, P], T]],
    Callable[Concatenate[SelfT, P], T],
   ]:
    """Log method execution and create Allure reports with screenshot and video capture.

    This decorator provides comprehensive logging, screenshot capture, and video
    recording for method execution. It automatically captures screenshots before
    and after method execution, records screen activity, and attaches all data
    to Allure reports.

    Args:
        my_str: Description string for the step in logs and reports.

    Returns:
        Decorator function that wraps the target method.

    Example:
        @step_info("Click on login button")
        def click_login(self):
            # Method implementation
            pass

    """

    def func_decorator(
            func: Callable[Concatenate[SelfT, P], T],
    ) -> Callable[Concatenate[SelfT, P], T]:
        # @allure.step(my_str)
        @wraps(func)
        def wrapper(self: Any, *args: P.args, **kwargs: P.kwargs) -> T:
            method_name = func.__name__
            class_name = self.__class__.__name__
            from shadowstep.shadowstep import Shadowstep  # noqa: PLC0415
            shadowstep = Shadowstep.get_instance()

            self.logger.info("[%s.%s]", class_name, method_name)
            self.logger.info("🔵🔵🔵 -> %s < args=%s, kwargs=%s", my_str, args, kwargs)
            screenshot = shadowstep.get_screenshot()
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # noqa: DTZ005
            screenshot_name_begin = f"screenshot_begin_{timestamp}.png"

            try:
                shadowstep.driver.start_recording_screen()
                self.logger.debug("[%s.%s] Screen recording started", class_name, method_name)
            except Exception as error:  # noqa: BLE001
                self.logger.error(  # noqa: TRY400
                    "[%s.%s] Error starting screen recording: %s",
                    class_name,
                    method_name,
                    error,
                )

            try:
                result: T = func(self, *args, **kwargs)
            except Exception as error:  # noqa: BLE001
                result = cast("T", False)  # noqa: FBT003
                self.logger.error("Error in %s: %s", func.__name__, error)  # noqa: TRY400
                # Screenshots
                allure.attach(
                    screenshot,
                    name=screenshot_name_begin,
                    attachment_type=allure.attachment_type.PNG,
                )
                text = (f"before {class_name}.{method_name} \n "
                       f"< args={args}, kwargs={kwargs} \n[{my_str}]")
                screenshot_end = shadowstep.get_screenshot()
                allure.attach(
                    screenshot_end,
                    name=text,
                    attachment_type=allure.attachment_type.PNG,
                )
                text = (f"after {class_name}.{method_name} \n "
                       f"< args={args}, kwargs={kwargs} \n[{my_str}]")

                # Video
                try:
                    video_data = shadowstep.driver.stop_recording_screen()
                    allure.attach(
                        base64.b64decode(video_data),
                        name=text,
                        attachment_type=allure.attachment_type.MP4,
                    )
                except Exception as error_video:  # noqa: BLE001
                    self.logger.warning("⚠️ [%s.%s] Video not attached", class_name, method_name)
                    self.logger.error("Video error: %s", error_video)  # noqa: TRY400
                    self.telegram.send_message(f"Telegram error with send video: {error_video}")

                # Error and traceback
                traceback_info = traceback.format_exc()
                error_details = (
                    f"❌ Error in method {class_name}.{method_name}: \n"
                    f"  args={args} \n"
                    f"  kwargs={kwargs} \n"
                    f"  error={error} \n"
                    f"  traceback=\n {traceback_info}"
                )
                self.logger.info("[%s.%s]", class_name, method_name)
                self.logger.info("❌❌❌ -> %s > %s", my_str, result)
                self.logger.error("Error details: %s", error_details)  # noqa: TRY400
                allure.attach(
                    error_details, name="Traceback", attachment_type=allure.attachment_type.TEXT,
                )
            self.logger.info("[%s.%s]", class_name, method_name)
            if result:
                self.logger.info("✅✅✅ -> %s > %s", my_str, result)
            else:
                self.logger.info("❌❌❌ -> %s > %s", my_str, result)
            return result

        return wrapper

    return func_decorator


def current_page() -> Callable[
    [Callable[Concatenate[SelfT, P], T]],
    Callable[Concatenate[SelfT, P], T],
   ]:
    """Add enhanced logging to PageObject is_current_page method.

    This decorator provides detailed logging for page verification methods,
    showing method entry and exit with the page object representation.

    Returns:
        Decorator function that wraps the target method.

    Example:
        @current_page()
        def is_current_page(self):
            # Page verification logic
            return True

    """

    def func_decorator(
            func: Callable[Concatenate[SelfT, P], T],
    ) -> Callable[Concatenate[SelfT, P], T]:
        @wraps(func)
        def wrapper(self: Any, *args: P.args, **kwargs: P.kwargs) -> T:
            method_name = func.__name__

            self.logger.info("%s() < %r", method_name, self)
            result = func(self, *args, **kwargs)
            self.logger.info("%s() > %s", method_name, result)
            return result

        return wrapper

    return func_decorator


def log_info() -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Log method entry/exit with type hints preserved.

    This decorator automatically logs method entry with arguments and exit with
    return value. It preserves type hints and works with any callable function.

    Returns:
        Decorator function that wraps the target method.

    Example:
        @log_info()
        def my_function(arg1: str, arg2: int) -> bool:
            # Function implementation
            return True

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            method_name = func.__name__
            module = cast(ModuleType, inspect.getmodule(func))  # noqa: TC006
            logger = logging.getLogger(module.__name__)
            logger.info("%s() < args=%s, kwargs=%s", method_name, args, kwargs)
            result: T = func(*args, **kwargs)
            logger.info("%s() > %s", method_name, result)
            return result

        return wrapper

    return decorator


def log_debug() -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Log method entry/exit with type hints preserved.

    This decorator automatically logs method entry with arguments and exit with
    return value. It preserves type hints and works with any callable function.

    Returns:
        Decorator function that wraps the target method.

    Example:
        @log_debug()
        def my_function(arg1: str, arg2: int) -> bool:
            # Function implementation
            return True

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            method_name = func.__name__
            module = cast(ModuleType, inspect.getmodule(func))  # noqa: TC006
            logger = logging.getLogger(module.__name__)
            logger.debug("%s() < args=%s, kwargs=%s", method_name, args, kwargs)
            result: T = func(*args, **kwargs)
            logger.debug("%s() > %s", method_name, result)
            return result

        return wrapper

    return decorator
