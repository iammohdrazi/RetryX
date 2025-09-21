import time

def retry(attempts=3, backoff='fixed', delay=1, exceptions=(Exception,)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, attempts+1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if backoff == 'fixed':
                        time.sleep(delay)
                    elif backoff == 'exponential':
                        time.sleep(delay * (2 ** (attempt-1)))
            raise last_exc
        return wrapper
    return decorator
