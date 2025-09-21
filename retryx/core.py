import time
import random
from functools import wraps

def retry(attempts=3, backoff="fixed", delay=1, jitter=False, exceptions=(Exception,)):
    """
    Retry decorator with backoff and optional jitter.
    
    Parameters:
        attempts (int): number of retries
        backoff (str): 'fixed', 'linear', or 'exponential'
        delay (float): base delay in seconds
        jitter (bool): add random jitter
        exceptions (tuple): exceptions to catch
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    # Calculate delay
                    if backoff == "fixed":
                        wait = delay
                    elif backoff == "linear":
                        wait = delay * attempt
                    elif backoff == "exponential":
                        wait = delay * (2 ** (attempt - 1))
                    else:
                        wait = delay
                    # Add jitter
                    if jitter:
                        wait = wait * random.uniform(0.5, 1.5)
                    print(f"Attempt {attempt} failed. Retrying in {wait:.2f} seconds...")
                    time.sleep(wait)
            # All retries failed
            raise last_exception
        return wrapper
    return decorator
