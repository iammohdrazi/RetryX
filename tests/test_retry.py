import pytest
from retryxlib import retry

# A counter to track how many times the function has been called
counter = {"count": 0}

# Example function that fails twice, then succeeds
@retry(attempts=5, backoff="exponential", delay=0.01, exceptions=(ValueError,))
def fail_twice_then_succeed():
    if counter["count"] < 2:
        counter["count"] += 1
        raise ValueError("Intentional failure")
    return True

# Another example function with fixed backoff
@retry(attempts=3, backoff="fixed", delay=0.01, exceptions=(RuntimeError,))
def always_fail():
    raise RuntimeError("Failing on purpose")


def test_fail_twice_then_succeed():
    # Reset counter before test
    counter["count"] = 0
    result = fail_twice_then_succeed()
    assert result is True


def test_always_fail():
    with pytest.raises(RuntimeError, match="Failing on purpose"):
        always_fail()
