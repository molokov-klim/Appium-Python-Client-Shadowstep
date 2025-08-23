# shadowstep/utils/decorators.py
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
from typing_extensions import Concatenate, ParamSpec  # noqa: UP035

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


def fail_safe(  # noqa: C901
        retries: int = 3,
        delay: float = 0.5,
        raise_exception: type[Exception] | None = None,
        fallback: Any = None,
        exceptions: tuple[type[Exception], ...] = DEFAULT_EXCEPTIONS,
        log_args: bool = False,
) -> Callable[[F], F]:
    """
    Decorator that retries a method call on specified exceptions.

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
                            f"[fail_safe] Not connected before {func.__name__}(), reconnecting..."
                        )
                        self.logger.warning(f"{last_exc=}")
                        self.reconnect()
                    return func(self, *args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    method = func.__name__
                    self.logger.warning(
                        f"[fail_safe] {method} failed on attempt {attempt}: "
                        f"{type(e).__name__} – {e}"
                    )
                    if log_args:
                        def format_arg(arg: Any) -> str:
                            if arg is self:
                                return f"<{self.__class__.__name__} id={id(self)}>"
                            arg_repr = repr(arg)
                            return (arg_repr[:197] + '...') if len(arg_repr) > 200 else arg_repr

                        formatted_args = [format_arg(self)] + [format_arg(a) for a in args]
                        formatted_args += [f"{k}={format_arg(v)}" for k, v in kwargs.items()]
                        self.logger.debug(f"[fail_safe] args: {formatted_args}")
                    self.logger.debug(
                        f"[fail_safe] stack:\n{''.join(traceback.format_stack(limit=5))}"
                    )
                    if not self.is_connected():
                        self.logger.warning(
                            f"[fail_safe] Disconnected after exception in {method}, reconnecting..."
                        )
                        self.reconnect()
                    time.sleep(delay)
                except Exception as e:
                    self.logger.error(
                        f"[fail_safe] Unexpected error in {func.__name__}: "
                        f"{type(e).__name__} – {e}"
                    )
                    self.logger.debug("Stack:\n" + "".join(traceback.format_stack(limit=5)))
                    last_exc = e
                    break
            self.logger.error(f"[fail_safe] {func.__name__} failed after {retries} attempts")
            if last_exc:
                tb = "".join(
                    traceback.format_exception(
                        type(last_exc), last_exc, last_exc.__traceback__
                    )
                )
                self.logger.error(f"[fail_safe] Final exception:\n{tb}")
            if raise_exception and last_exc:
                raise raise_exception(
                    f"{func.__name__} failed after {retries} attempts"
                ) from last_exc
            if raise_exception:
                raise raise_exception(f"{func.__name__} failed after {retries} attempts")
            if fallback is not None:
                return fallback
            if last_exc:
                raise last_exc
            raise RuntimeError(f"{func.__name__} failed after {retries} attempts")

        return cast(F, wrapper)

    return decorator


def retry(max_retries: int = 3, delay: float = 1.0) -> Callable[[F], F]:
    """
    Retry decorator factory that repeats method execution if it returns False or None.

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

        return cast(F, wrapper)

    return decorator


def time_it(func: F) -> F:
    """
    Decorator that measures method execution time.

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
        print(f"Execution time of {func.__name__}: {execution_time:.2f} seconds")
        return result

    return cast(F, wrapper)


def step_info(
        my_str: str,
) -> Callable[
    [Callable[Concatenate[SelfT, P], T]],
    Callable[Concatenate[SelfT, P], T],
]:
    """
    Decorator for logging and allure reports
    """

    def func_decorator(
            func: Callable[Concatenate[SelfT, P], T],
    ) -> Callable[Concatenate[SelfT, P], T]:
        # @allure.step(my_str)
        @wraps(func)
        def wrapper(self: Any, *args: P.args, **kwargs: P.kwargs) -> T:
            method_name = func.__name__
            class_name = self.__class__.__name__

            self.logger.info(f"[{class_name}.{method_name}]")
            self.logger.info(f"🔵🔵🔵 -> {my_str} < args={args}, kwargs={kwargs}")
            screenshot = self.shadowstep.get_screenshot()
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_name_begin = f"screenshot_begin_{timestamp}.png"

            try:
                self.shadowstep.driver.start_recording_screen()
                self.logger.debug(f"[{class_name}.{method_name}] Запись экрана начата")
            except Exception as error:
                self.logger.error(
                    f"[{class_name}.{method_name}] Ошибка при запуске записи экрана: {error}"
                )

            try:
                result: T = func(self, *args, **kwargs)
            except Exception as error:
                result = cast(T, False)
                self.logger.error(error)
                # Скриншоты
                allure.attach(
                    screenshot,
                    name=screenshot_name_begin,
                    attachment_type=allure.attachment_type.PNG,
                )
                text = f"before {class_name}.{method_name} \n < args={args}, kwargs={kwargs} \n[{my_str}]"
                screenshot_end = self.shadowstep.get_screenshot()
                allure.attach(
                    screenshot_end,
                    name=text,
                    attachment_type=allure.attachment_type.PNG,
                )
                text = f"after {class_name}.{method_name} \n < args={args}, kwargs={kwargs} \n[{my_str}]"

                # Видео
                try:
                    video_data = self.shadowstep.driver.stop_recording_screen()
                    allure.attach(
                        base64.b64decode(video_data),
                        name=text,
                        attachment_type=allure.attachment_type.MP4,
                    )
                except Exception as error_video:
                    self.logger.warning(f"⚠️ [{class_name}.{method_name}] Видео не прикреплено")
                    self.logger.error(error_video)
                    self.telegram.send_message(f"Telegram error with send video: {error_video}")

                # Ошибка и трейсбек
                traceback_info = traceback.format_exc()
                error_details = (
                    f"❌ Ошибка в методе {class_name}.{method_name}: \n"
                    f"  args={args} \n"
                    f"  kwargs={kwargs} \n"
                    f"  error={error} \n"
                    f"  traceback=\n {traceback_info}"
                )
                self.logger.info(f"[{class_name}.{method_name}]")
                self.logger.info(f"❌❌❌ -> {my_str} > {result}")
                self.logger.error(error_details)
                allure.attach(
                    error_details, name="Traceback", attachment_type=allure.attachment_type.TEXT
                )
            self.logger.info(f"[{class_name}.{method_name}]")
            if result:
                self.logger.info(f"✅✅✅ -> {my_str} > {result}")
            else:
                self.logger.info(f"❌❌❌ -> {my_str} > {result}")
            return result

        return wrapper

    return func_decorator


def current_page() -> Callable[
    [Callable[Concatenate[SelfT, P], T]],
    Callable[Concatenate[SelfT, P], T],
]:
    """
    Decorator for method is_current_page from PageObject (better logging)
    """

    def func_decorator(
            func: Callable[Concatenate[SelfT, P], T],
    ) -> Callable[Concatenate[SelfT, P], T]:
        @wraps(func)
        def wrapper(self: Any, *args: P.args, **kwargs: P.kwargs) -> T:
            method_name = func.__name__

            self.logger.info(f"{method_name}() < {self!r}")
            result = func(self, *args, **kwargs)
            self.logger.info(f"{method_name}() > {result}")
            return result

        return wrapper

    return func_decorator


def log_info() -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator for logging method entry/exit with type hints preserved."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            method_name = func.__name__
            module = cast(ModuleType, inspect.getmodule(func))
            logger = logging.getLogger(module.__name__)
            logger.info(f"{method_name}() < args={args}, kwargs={kwargs}")
            result: T = func(*args, **kwargs)
            logger.info(f"{method_name}() > {result}")
            return result

        return wrapper

    return decorator
