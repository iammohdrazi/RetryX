import pytest
from retryxlib import retry  # updated import

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
