# shadowstep/utils/decorators.py

import base64
import sys
import io
import time
import functools
import traceback
from functools import wraps
from datetime import datetime
from typing import TypeVar, Callable, Any, Tuple, Type, Optional

import allure
import numpy as np
import pytest
from PIL import Image
from selenium.common import NoSuchDriverException, InvalidSessionIdException, \
    StaleElementReferenceException

T = TypeVar("T", bound=Callable[..., Any])

DEFAULT_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    NoSuchDriverException,
    InvalidSessionIdException,
    StaleElementReferenceException,
)


def fail_safe(
        retries: int = 3,
        delay: float = 0.5,
        raise_exception: Optional[Type[Exception]] = None,
        fallback: Any = None,
        exceptions: Tuple[Type[Exception], ...] = DEFAULT_EXCEPTIONS,
        log_args: bool = False,
) -> Callable:
    """
    Decorator that retries a method call on specified exceptions.

    Parameters:
    -----------
    retries
        Number of retry attempts after the first call.
    delay
        Time in seconds to wait between retries.
    raise_exception
        Exception class to raise after all attempts are exhausted.
        If provided, fallback is ignored.
    fallback
        Value to return if all attempts fail and raise_exception is not set.
    exceptions
        Tuple of exception types that trigger a retry.
    log_args
        If True, logs the method arguments (class and id for self,
        repr() truncated to 200 chars for others) at debug level.

    Behavior:
    ---------
    1. Attempts the call (first attempt + retries).
       - If the call succeeds, returns the result.
       - If a specified exception occurs, logs it, attempts reconnect
         via self.base.reconnect(), waits delay, and retries.
       - If any other exception occurs, logs it as an error and breaks.
    2. After exhausting attempts:
       - If raise_exception is set, raises it.
       - Otherwise, returns fallback (None by default).
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exc: Optional[Exception] = None

            for attempt in range(1, retries + 2):
                try:
                    return func(self, *args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    method = func.__name__

                    # Log the main exception at WARNING level
                    self.logger.warning(
                        f"[fail_safe] {method} failed on attempt {attempt}: "
                        f"{type(e).__name__} – {e}"
                    )

                    # Optionally log arguments at DEBUG level
                    if log_args:
                        def format_arg(arg):
                            if arg is self:
                                # Log class name and object id for self
                                return f"<{self.__class__.__name__} id={id(self)}>"
                            # Truncate repr() of other args to 200 chars
                            r = repr(arg)
                            return (r[:197] + '...') if len(r) > 200 else r

                        formatted_args = [format_arg(self)] + [format_arg(a) for a in args]
                        formatted_args += [f"{k}={format_arg(v)}" for k, v in kwargs.items()]
                        self.logger.debug(f"[fail_safe] args: {formatted_args}")

                    # Log a short stack trace at DEBUG level
                    stack = "".join(traceback.format_stack(limit=5))
                    self.logger.debug(f"[fail_safe] stack:\n{stack}")

                    # Attempt to reconnect; if it fails, let the error propagate
                    if hasattr(self, "base") and hasattr(self.base, "reconnect"):
                        self.logger.debug("[fail_safe] Calling self.base.reconnect()")
                        self.base.reconnect()

                    # Wait before the next retry if any remain
                    if attempt <= retries:
                        time.sleep(delay)

                except Exception as e:
                    # Any unexpected exception stops further retries
                    self.logger.error(
                        f"[fail_safe] Unexpected error in {func.__name__}: "
                        f"{type(e).__name__} – {e}"
                    )
                    self.logger.debug("Stack:\n" + "".join(traceback.format_stack(limit=5)))
                    break

            # All attempts exhausted or an unexpected exception occurred
            self.logger.error(f"[fail_safe] {func.__name__} failed after {retries + 1} attempts")

            if raise_exception:
                # Raise the provided exception
                raise raise_exception(f"{func.__name__} failed after {retries + 1} attempts")
            return fallback

        return wrapper

    return decorator


def retry(func):
    """
    Повторяет выполнение метода если он возвращает False или None.
    3 tries hardcode in method
    """
    max_retries = 3

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        for _ in range(max_retries):
            result = func(*args, **kwargs)
            if result is not None and result is not False:
                return result
            time.sleep(1)
        return result

    # Возвращаем обертку функции
    return wrapper


def wait_until_window_change(poll_frequency: float = 0.1):
    """
    Декоратор, который ожидает пока окно не перестанет меняться.
    В обернутом методе должен быть аргумент
        decorator_args: dict
            timeout_window: общее время ожидания
            window_not_changing_period: период времени в течении которого окно не должно изменятся

    Аргументы:
        poll_frequency (float): Частота опроса содержимого окна на наличие изменений в секундах.
                               По умолчанию 0.1 секунды.

    Возвращает:
        function: Декорированная функция.
    """

    def func_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            """
            Оберточная функция, которая инкапсулирует декорированную функцию
            с логикой обнаружения изменений окна.

            Аргументы:
                self: Экземпляр класса, к которому принадлежит
                      декорированный метод.
                *args: Произвольное число аргументов, переданных в
                       декорированный метод.
                **kwargs: Произвольное число именованных аргументов, переданных в
                          декорированный метод.

            Возвращает:
                bool: True, если содержимое окна изменяется в течении
                      заданного периода времени, иначе False.
            """

            # Инициализация
            func_result = False
            decorator_args = kwargs.get('decorator_args', {})
            timeout_window = decorator_args.get('timeout_window', 30)
            window_not_changing_period = decorator_args.get('window_not_changing_period', 10)
            # Запись начального времени
            start_time = time.time()
            # Вызов декорированной функции и сохранение результата
            func_result = func(self, *args,
                               **kwargs)

            # Обнаружение изменений экрана с экспоненциальной задержкой
            poll_interval = poll_frequency
            # Продолжаем до достижения тайм-аута
            while time.time() - start_time < timeout_window:
                # Запускаем новый период, в течение которого окно не изменяется
                window_not_changing_period_start_time = time.time()
                # Флаг для отслеживания того, изменилось ли окно за период
                window_not_changed = True

                while (time.time() - window_not_changing_period_start_time
                       < window_not_changing_period):
                    # Делаем снимок экрана и сохраняем его в памяти
                    image_bytes = _get_screenshot_bytes(self)
                    # Преобразуем в оттенки серого
                    image = Image.open(io.BytesIO(image_bytes)).convert('L')
                    # Обрезаем снимок до определенной области (лево, верх, право, низ)
                    box = (50, 50, 400, 400)
                    image = image.crop(box)
                    # Ждем указанный интервал между опросами
                    time.sleep(poll_interval)
                    new_image_bytes = _get_screenshot_bytes(self)
                    # Преобразуем в оттенки серого
                    new_image = Image.open(io.BytesIO(new_image_bytes)).convert('L')
                    new_image = new_image.crop(box)

                    # Проверяем, отличается ли сумма значений пикселей на двух изображениях
                    if np.sum(image) != np.sum(new_image):
                        # Содержимое окна изменилось
                        window_not_changed = False
                        break

                if window_not_changed:
                    self.logger.debug("Содержимое окна не изменялось в течение периода")
                    return func_result
                # Удваиваем время ожидания для каждого опроса
                poll_interval *= 2

            return func_result

        # Возвращаем обертку функции
        return wrapper

    # Возвращаем декоратор функций
    return func_decorator


def wait_for_window_change(poll_frequency: float = 0.5):
    """
    Декоратор, который ожидает изменения окна после выполнения метода.
    Если окно не изменилось - выполняет еще попытку.
    В обернутом методе должен быть аргумент
        decorator_args: dict
            timeout_window: int, время ожидания на попытку
            tries: int, количество попыток выполнения метода

    Аргументы:
        poll_frequency (float): Частота проверки окна на изменения.

    Возвращает:
        Декоратор функции.
    """

    def func_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            """
            Оберточная функция, которая выполняет обнаружение изменения окна и
            выполнение декорированной функции.

            Аргументы:
                self: Экземпляр класса, содержащего декорированную функцию.
                *args: Переменное число аргументов.
                **kwargs: Произвольные именованные аргументы.

            Возвращает:
                Результат декорированной функции или False, если изменение окна не было обнаружено.
            """

            # Инициализация
            func_result = False
            decorator_args = kwargs.get('decorator_args', {})
            timeout_window = decorator_args.get('timeout_window', 10)
            tries = decorator_args.get('tries', 3)

            # Сделать снимок экрана и сохранить его в памяти в виде байтов
            image_bytes = _get_screenshot_bytes(self)
            # Открыть изображение из байтов и преобразовать его в оттенки серого
            image = Image.open(io.BytesIO(image_bytes)).convert(
                'L')

            # Обрезать снимок экрана до определенной области (лево, верх, право, низ)
            box = (50, 50, 400, 400)
            # Обрезать изображение на основе заданных координат области
            image = image.crop(box)

            # Попытаться обнаружить изменение экрана в течении tries попыток
            for _ in range(tries):
                # Записать текущее время начала попытки обнаружения
                start_time = time.time()
                # Выполнить декорированную функцию и сохранить результат
                func_result = func(self, *args,
                                   **kwargs)

                # Обнаружить изменение экрана с экспоненциальной задержкой
                poll_interval = poll_frequency
                # Проверить, находится ли прошедшее время в пределах заданного окна времени ожидания
                while time.time() - start_time < timeout_window:
                    # Приостановить выполнение на заданный интервал проверки
                    time.sleep(poll_interval)
                    # Сделать новый снимок экрана окна и получить данные изображения в виде байтов
                    new_image_bytes = _get_screenshot_bytes(self)
                    # Открыть новое изображение из байтов и преобразовать его в оттенки серого
                    new_image = Image.open(io.BytesIO(new_image_bytes)).convert(
                        'L')
                    # Обрезать новое изображение на основе заданных координат области
                    new_image = new_image.crop(
                        box)
                    # Сравнить суммы значений пикселей между исходным и новым изображениями
                    if not np.sum(image) == np.sum(
                            new_image):
                        # Записать сообщение о том, что произошло изменение экрана
                        self.logger.debug(
                            "Изменение экрана обнаружено")
                        # Вернуть True для обозначения обнаружения изменения экрана
                        return func_result
                        # Удвоить интервал проверки для следующей итерации
                        # (экспоненциальная задержка)
                    poll_interval *= 2

            return func_result

        # Возвращаем обертку функции
        return wrapper

    # Возвращаем декоратор функций
    return func_decorator


def wait_until_dom_change(poll_frequency: float = 0.1):
    """
    Декоратор, который ожидает пока DOM не перестанет меняться.
    В обернутом методе должен быть аргумент
        decorator_args: dict
            timeout_window: общее время ожидания
            window_not_changing_period: период времени в течении которого окно не должно изменятся

    Аргументы:
        poll_frequency (float): Частота опроса содержимого окна на наличие изменений в секундах.
                               По умолчанию 0.1 секунды.

    Возвращает:
        function: Декорированная функция.
    """

    def func_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            """
            Оберточная функция, которая инкапсулирует декорированную функцию
            с логикой обнаружения изменений DOM.

            Аргументы:
                self: Экземпляр класса, к которому принадлежит
                      декорированный метод.
                *args: Произвольное число аргументов, переданных в
                       декорированный метод.
                **kwargs: Произвольное число именованных аргументов, переданных в
                          декорированный метод.

            Возвращает:
                bool: True, если содержимое окна изменяется в течении
                      заданного периода времени, иначе False.
            """

            # Инициализация
            func_result = False
            decorator_args = kwargs.get('decorator_args', {})
            timeout_window = decorator_args.get('timeout_window', 30)
            window_not_changing_period = decorator_args.get('window_not_changing_period', 10)
            # Запись начального времени
            start_time = time.time()
            # Вызов декорированной функции и сохранение результата
            func_result = func(self, *args,
                               **kwargs)

            # Обнаружение изменений экрана с экспоненциальной задержкой
            poll_interval = poll_frequency
            # Продолжаем до достижения тайм-аута
            while time.time() - start_time < timeout_window:
                # Запускаем новый период, в течение которого окно не изменяется
                window_not_changing_period_start_time = time.time()
                # Флаг для отслеживания того, изменилось ли окно за период
                window_not_changed = True

                while (time.time() - window_not_changing_period_start_time
                       < window_not_changing_period):
                    # Делаем снимок DOM
                    page_source = self.driver.page_source
                    # Ждем указанный интервал между опросами
                    time.sleep(poll_interval)
                    new_page_source = self.driver.page_source

                    # Проверяем, отличается ли сумма значений пикселей на двух изображениях
                    if page_source != new_page_source:
                        # Содержимое окна изменилось
                        window_not_changed = False
                        break
                if window_not_changed:
                    self.logger.debug("Содержимое DOM не изменялось в течение периода")
                    return func_result
                # Удваиваем время ожидания для каждого опроса
                poll_interval *= 2

            return func_result

        # Возвращаем обертку функции
        return wrapper

    # Возвращаем декоратор функций
    return func_decorator


def wait_for_dom_change(poll_frequency: float = 0.5):
    """
    Декоратор, который ожидает изменения DOM после выполнения метода.
    Если DOM не изменилось - выполняет еще попытку.
    В обернутом методе должен быть аргумент
        decorator_args: dict
            timeout_window: int, время ожидания на попытку
            tries: int, количество попыток выполнения метода

    Аргументы:
        poll_frequency (float): Частота проверки окна на изменения.

    Возвращает:
        Декоратор функции.
    """

    def func_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            """
            Оберточная функция, которая выполняет обнаружение изменения окна и
            выполнение декорированной функции.

            Аргументы:
                self: Экземпляр класса, содержащего декорированную функцию.
                *args: Переменное число аргументов.
                **kwargs: Произвольные именованные аргументы.

            Возвращает:
                Результат декорированной функции или False, если изменение окна не было обнаружено.
            """

            # Инициализация
            func_result = False
            decorator_args = kwargs.get('decorator_args', {})
            timeout_window = decorator_args.get('timeout_window', 10)
            tries = decorator_args.get('tries', 3)

            # Сделать снимок DOM и сохранить его в памяти
            page_source = self.driver.page_source

            # Записать текущее время начала попытки обнаружения
            start_time = time.time()
            # Выполнить декорированную функцию и сохранить результат
            func_result = func(self, *args,
                               **kwargs)

            # Обнаружить изменение экрана с экспоненциальной задержкой
            poll_interval = poll_frequency
            # Проверить, находится ли прошедшее время в пределах заданного окна времени ожидания
            while time.time() - start_time < timeout_window:
                # Приостановить выполнение на заданный интервал проверки
                time.sleep(poll_interval)
                # Сделать новый снимок DOM
                new_page_source = self.driver.page_source
                # Сравнить
                if not page_source == new_page_source:
                    # Записать сообщение о том, что произошло изменение DOM
                    self.logger.debug(
                        "Изменение DOM обнаружено")
                    # Вернуть True для обозначения обнаружения изменения DOM
                    return func_result
                    # Удвоить интервал проверки для следующей итерации
                    # (экспоненциальная задержка)
                poll_interval *= 2

            return func_result

        # Возвращаем обертку функции
        return wrapper

    # Возвращаем декоратор функций
    return func_decorator


def time_it(func):
    """
    Замеряет время выполнения метода.
    Печатает результат замера.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time:.2f} seconds")
        return result

    # Возвращаем обертку функции
    return wrapper


def step_info(my_str):
    """
    Декоратор, который перед вызовом метода вызывает logger.info и @allure.step,
    передавая в них строковую переменную, принятую в параметрах.

    Аргументы:
        my_str (str): Строковая переменная для использования в logger.info и @allure.step.

    Возвращает:
        function: Декоратор функций.

    Пример использования:
        @my_step_info("Мой шаг")
        def my_function():
            ...
    """

    # Определяем декоратор функций
    def func_decorator(func):
        # Создаем обертку функции, сохраняющую метаданные исходной функции
        @allure.step(my_str)
        def wrapper(self, *args, **kwargs):
            result = None
            # Логируем информацию перед вызовом метода
            self.logger.info(my_str)
            # Получаем скриншот до вызова метода
            screenshot = _get_screenshot_bytes(self)
            # Генерируем временную метку для имени скриншота
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            # Устанавливаем имя скриншота до вызова метода
            screenshot_name_begin = f"screenshot_begin_{timestamp}.png"
            # Имя файла видеозаписи с временной меткой
            video_filename = f'screenrecord_{timestamp}.mp4'
            self.driver.start_recording_screen()
            try:
                # Выполняем исходную функцию
                result = func(self, *args, **kwargs)
            except Exception as error:
                # Если произошло исключение, прикрепляем скриншот до вызова метода к отчету
                allure.attach(screenshot,
                              name=screenshot_name_begin,
                              attachment_type=allure.attachment_type.PNG)
                # Получаем скриншот после вызова метода
                screenshot = _get_screenshot_bytes(self)
                # Генерируем временную метку для имени скриншота
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                # Устанавливаем имя скриншота до вызова метода
                screenshot_name_end = f"screenshot_end_{timestamp}.png"
                # Если произошло исключение, прикрепляем скриншот после вызова метода к отчету
                allure.attach(screenshot,
                              name=screenshot_name_end,
                              attachment_type=allure.attachment_type.PNG)

                # Если произошло исключение, прикрепляем видеозапись выполнения метода к отчету
                allure.attach(base64.b64decode(self.driver.stop_recording_screen()),
                              name=video_filename,
                              attachment_type=allure.attachment_type.MP4)

                # Прикрепляем информацию об ошибке AssertionError к отчету
                allure.attach(str(error),
                              name=str(error),
                              attachment_type=allure.attachment_type.TEXT)

                # Выводим информацию в лог
                self.logger.error(f"{my_str} [не выполнено]")
                traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
                error_msg = f"""Ошибка: {error},
                                        {args=},
                                        {kwargs=},
                            Traceback:
                            {traceback_info=}
                                """
                self.logger.error(error_msg)

                # В случае исключения помечаем тест провалившимся
                try:
                    pytest.fail(f"{func.__name__}({args}, {kwargs}), {error}")
                except Exception as e:
                    self.logger.error("Pytest не обнаружен")
                    raise

            # Логируем информацию после успешного выполнения метода
            self.logger.info(f"{my_str} [выполнено успешно]")
            # Возвращаем результат выполнения исходной функции
            return result

        # Возвращаем обертку функции
        return wrapper

    # Возвращаем декоратор функций
    return func_decorator


def screenshots():
    """
    В случае возникновения AssertionError в обернутом методе -
    прикрепляет к allure report скриншот до выполнения
    метода и после возникновения исключения, а также информацию об ошибке.
    В ином случае скриншот не прикрепляется.
    """

    # Определяем декоратор функций
    def func_decorator(func):
        # Создаем обертку функции, сохраняющую метаданные исходной функции
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Получаем скриншот до вызова метода
            screenshot = _get_screenshot_bytes(self)
            # Генерируем временную метку для имени скриншота
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            # Устанавливаем имя скриншота до вызова метода
            screenshot_name_begin = f"screenshot_begin_{timestamp}.png"
            try:
                # Выполняем исходную функцию
                result = func(self, *args, **kwargs)
            except AssertionError as error:
                # Если произошло исключение, прикрепляем скриншот до вызова метода к отчету
                allure.attach(screenshot,
                              name=screenshot_name_begin,
                              attachment_type=allure.attachment_type.PNG)
                # Прикрепляем информацию об ошибке AssertionError к отчету
                allure.attach(str(error),
                              name="AssertionError",
                              attachment_type=allure.attachment_type.TEXT)
                # Рейзим исключение AssertionError с сохраненным traceback
                raise AssertionError(str(error)).with_traceback(sys.exc_info()[2])
            finally:
                # Получаем скриншот после вызова метода
                screenshot = _get_screenshot_bytes(self)
                # Обновляем временную метку для имени скриншота
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                # Устанавливаем имя скриншота после вызова метода
                screenshot_name_end = f"screenshot_end_{timestamp}.png"
                # Прикрепляем скриншот после вызова метода к отчету
                allure.attach(screenshot,
                              name=screenshot_name_end,
                              attachment_type=allure.attachment_type.PNG)
            # Возвращаем результат выполнения исходной функции
            return result

        # Возвращаем обертку функции
        return wrapper

    # Возвращаем декоратор функций
    return func_decorator


def log_debug():
    """
    Логирует начало и завершение обернутого метода
    """

    # Определяем декоратор функций
    def func_decorator(func):
        # Создаем обертку функции, сохраняющую метаданные исходной функции
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Получаем имя метода
            method_name = func.__name__
            # Логируем начало выполнения метода и переданные аргументы
            self.logger.debug(f"{method_name}() < {', '.join(map(str, args))}, "
                              f"{', '.join(f'{k}={v}' for k, v in kwargs.items())}")
            # Выполняем исходную функцию
            result = func(self, *args, **kwargs)
            # Если результат существует, логируем его
            if result:
                self.logger.debug(f"{method_name}() > {str(result)}")
            # Возвращаем результат выполнения исходной функции
            return result

        # Возвращаем обертку функции
        return wrapper

    # Возвращаем декоратор функций
    return func_decorator


def print_me():
    """
    Печатает начало и завершение обернутого метода
    """

    # Определяем декоратор функций
    def func_decorator(func):
        # Создаем обертку функции, сохраняющую метаданные исходной функции
        def wrapper(*args, **kwargs):
            # Получаем имя метода
            method_name = func.__name__
            # Печатаем начало выполнения метода и переданные аргументы
            print(f"{method_name}() < {', '.join(map(str, args))}, "
                  f"{', '.join(f'{k}={v}' for k, v in kwargs.items())}")
            # Выполняем исходную функцию
            result = func(*args, **kwargs)
            # Если результат существует, логируем его
            if result:
                print(f"{method_name}() > {str(result)}")
            # Возвращаем результат выполнения исходной функции
            return result

        # Возвращаем обертку функции
        return wrapper

    # Возвращаем декоратор функций
    return func_decorator


def _get_screenshot_bytes(self) -> bytes:
    """
    Если не получается снять скриншот методами драйвера - возвращает белый квадрат
    """
    try:
        return self.driver.get_screenshot_as_png()
    except Exception:
        # Создаем белое изображение 100x100
        size = (100, 100)
        color = (255, 255, 255)  # белый цвет
        image = Image.new("RGB", size, color)

        # Сохраняем изображение в байтовый объект
        byte_io = io.BytesIO()
        image.save(byte_io, 'PNG')

        # Возвращаем байты изображения
        return byte_io.getvalue()
