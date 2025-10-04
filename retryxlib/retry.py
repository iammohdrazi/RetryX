# retryxlib/retry.py
import time
import random
import functools
import asyncio
from inspect import iscoroutinefunction

def retry(
    attempts=3,
    backoff='fixed',
    delay=1,
    exceptions=(Exception,),
    max_delay=None,
    max_total_time=None,
    jitter=False,
    on_retry=None,
    default=None,
    retry_if=None
):
    """
    Robust retry decorator for sync and async functions.

    Parameters:
    - attempts: Number of retries
    - backoff: 'fixed' or 'exponential'
    - delay: Initial delay between retries
    - exceptions: Tuple of exception types to catch
    - max_delay: Maximum delay per retry (seconds)
    - max_total_time: Maximum total retry time (seconds)
    - jitter: If True, randomize delay slightly
    - on_retry: Optional callback(attempt, exception) called on each retry
    - default: Value to return if all retries fail
    - retry_if: Optional callable(result) -> bool; retry if returns True
    """
    def decorator(func):
        is_async = iscoroutinefunction(func)

        async def _async_wrapper(*args, **kwargs):
            start_time = time.time()
            last_exc = None
            for attempt in range(1, attempts + 1):
                try:
                    result = await func(*args, **kwargs)
                    if retry_if and retry_if(result):
                        raise ValueError(f"Retry condition met for return value: {result}")
                    return result
                except exceptions as e:
                    last_exc = e
                except Exception as e:
                    last_exc = e

                # Compute delay
                wait = delay * (2 ** (attempt - 1)) if backoff == 'exponential' else delay
                if jitter:
                    wait *= random.uniform(0.5, 1.5)
                if max_delay is not None:
                    wait = min(wait, max_delay)
                if max_total_time is not None:
                    elapsed = time.time() - start_time
                    if elapsed + wait > max_total_time:
                        break

                if on_retry:
                    on_retry(attempt, last_exc)

                await asyncio.sleep(wait)

            if default is not None:
                return default
            raise last_exc

        def _sync_wrapper(*args, **kwargs):
            start_time = time.time()
            last_exc = None
            for attempt in range(1, attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if retry_if and retry_if(result):
                        raise ValueError(f"Retry condition met for return value: {result}")
                    return result
                except exceptions as e:
                    last_exc = e
                except Exception as e:
                    last_exc = e

                # Compute delay
                wait = delay * (2 ** (attempt - 1)) if backoff == 'exponential' else delay
                if jitter:
                    wait *= random.uniform(0.5, 1.5)
                if max_delay is not None:
                    wait = min(wait, max_delay)
                if max_total_time is not None:
                    elapsed = time.time() - start_time
                    if elapsed + wait > max_total_time:
                        break

                if on_retry:
                    on_retry(attempt, last_exc)

                time.sleep(wait)

            if default is not None:
                return default
            raise last_exc

        return _async_wrapper if is_async else _sync_wrapper

    return decorator
