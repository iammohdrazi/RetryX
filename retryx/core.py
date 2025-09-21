import time
import random
import functools
from typing import Callable, Tuple, Type

def retry(
    attempts: int = 3,
    backoff: str = "exponential",
    jitter: bool = False,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    callback: Callable = None,
):
    """
    Retry decorator with backoff and optional jitter.

    Args:
        attempts (int): Number of retry attempts before giving up.
        backoff (str): Strategy: "fixed", "linear", or "exponential".
        jitter (bool): Add randomness to delay.
        exceptions (tuple): Exceptions to retry on.
        callback (callable): Optional callback(attempt, exception, wait).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    wait = 1
                    if backoff == "linear":
                        wait = attempt + 1
                    elif backoff == "exponential":
                        wait = 2 ** attempt
                    if jitter:
                        wait += random.uniform(0, 0.5)

                    if callback:
                        callback(attempt + 1, e, wait)

                    if attempt == attempts - 1:  # last attempt
                        raise
                    time.sleep(wait)
        return wrapper
    return decorator
