import pytest
from retryx import retry

# Dummy function to test retry decorator
counter = {"count": 0}

@retry(attempts=3, backoff="fixed", delay=0.1, exceptions=(ValueError,))
def fail_twice_then_succeed():
    if counter["count"] < 2:
        counter["count"] += 1
        raise ValueError("Failing")
    return True

def test_retry_decorator():
    counter["count"] = 0
    result = fail_twice_then_succeed()
    assert result is True
    assert counter["count"] == 2

def test_import_retry():
    from retryx import retry
    assert retry is not None
