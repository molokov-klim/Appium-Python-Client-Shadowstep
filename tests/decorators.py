import time


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


