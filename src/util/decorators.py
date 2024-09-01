import logging
from contextlib import suppress
from functools import wraps
from time import time
from typing import Callable, Optional, TypeVar

T = TypeVar('T')


def cached(timeout_in_seconds, logged=False) -> Callable[..., T]:
    """
    Decorator that caches the results of a function for a specified timeout.

    Args:
        timeout_in_seconds (int): The cache timeout duration in seconds.
        logged (bool, optional): Whether to log cache initialization and hits (default is False).

    Returns:
        Callable: A decorated function with caching capabilities.
    """

    def decorator(function: Callable[..., T]) -> Callable[..., T]:
        if logged:
            logging.info("-- Initializing cache for", function.__name__)

        cache = {}

        @wraps(function)
        def decorated_function(*args, **kwargs) -> T:
            if logged:
                logging.info("-- Called function", function.__name__)

            key = args, frozenset(kwargs.items())
            result: Optional[tuple[T]] = None

            if key in cache:
                if logged:
                    logging.info("-- Cache hit for", function.__name__, key)

                cache_hit, expiry = cache[key]

                if time() - expiry < timeout_in_seconds:
                    result = cache_hit
                elif logged:
                    logging.info("-- Cache expired for", function.__name__, key)
            elif logged:
                logging.info("-- Cache miss for", function.__name__, key)

            if result is None:
                result = (function(*args, **kwargs),)
                cache[key] = result, time()

            return result[0]

        return decorated_function

    return decorator


def suppress_exception(function: Callable[..., T], exceptions: tuple = (BaseException,),
                       default_value_function: Callable[[], T] = lambda: None) -> Callable[..., T]:
    """
    Decorator that suppresses specified exceptions raised by a function.

    Args:
        function (Callable): The function to decorate.
        *exceptions (tuple, default: (BaseException,)): Variable number of exception types to suppress.
        default_value_function (Callable[[], T], default: lambda: None): Function that returns the default value.

    Returns:
        Callable: A decorated function that suppresses the specified exceptions.
    """
    if getattr(function, '__suppressed__', False):
        return function

    @wraps(function)
    def wrapper(*args, **kwargs) -> Callable[..., T]:
        with suppress(*exceptions):
            return function(*args, **kwargs)
        return default_value_function()

    wrapper.__suppressed__ = True

    return wrapper
