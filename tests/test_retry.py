# tests/test_retry.py
import time
import asyncio
import pytest
from retryxlib.retry import retry

# ------------------------------
# Helper to track callback calls
# ------------------------------
class CallbackTracker:
    def __init__(self):
        self.calls = []

    def __call__(self, attempt, exc):
        self.calls.append((attempt, exc))


# ------------------------------
# 1. Test sync function retry
# ------------------------------
def test_sync_retry_fixed_backoff():
    counter = {"count": 0}

    @retry(attempts=3, backoff='fixed', delay=0.1, exceptions=(ValueError,))
    def fail_twice():
        if counter["count"] < 2:
            counter["count"] += 1
            raise ValueError("Failing")
        return True

    start = time.time()
    result = fail_twice()
    elapsed = time.time() - start

    assert result is True
    assert counter["count"] == 2
    assert elapsed >= 0.2  # 2 retries with 0.1s delay each


def test_sync_retry_exponential_backoff():
    counter = {"count": 0}
    tracker = CallbackTracker()

    @retry(
        attempts=3,
        backoff='exponential',
        delay=0.1,
        jitter=False,
        exceptions=(ValueError,),
        on_retry=tracker
    )
    def fail_twice():
        if counter["count"] < 2:
            counter["count"] += 1
            raise ValueError("Failing")
        return "success"

    result = fail_twice()
    assert result == "success"
    assert counter["count"] == 2
    # Check that callback called twice
    assert len(tracker.calls) == 2


# ------------------------------
# 2. Test default return value
# ------------------------------
def test_default_return_value():
    counter = {"count": 0}

    @retry(attempts=2, delay=0.1, exceptions=(ValueError,), default="failed")
    def always_fail():
        counter["count"] += 1
        raise ValueError("Fail")

    result = always_fail()
    assert result == "failed"
    assert counter["count"] == 2


# ------------------------------
# 3. Test retry_if (retry on return value)
# ------------------------------
def test_retry_if_condition():
    counter = {"count": 0}

    @retry(attempts=3, delay=0.1, retry_if=lambda x: x is None)
    def return_none_twice():
        if counter["count"] < 2:
            counter["count"] += 1
            return None
        return "done"

    result = return_none_twice()
    assert result == "done"
    assert counter["count"] == 2


# ------------------------------
# 4. Async function tests
# ------------------------------
@pytest.mark.asyncio
async def test_async_retry_fixed():
    counter = {"count": 0}

    @retry(attempts=3, backoff='fixed', delay=0.1, exceptions=(RuntimeError,))
    async def async_fail_twice():
        if counter["count"] < 2:
            counter["count"] += 1
            raise RuntimeError("Async fail")
        return "ok"

    result = await async_fail_twice()
    assert result == "ok"
    assert counter["count"] == 2


@pytest.mark.asyncio
async def test_async_retry_exponential_with_jitter():
    counter = {"count": 0}
    tracker = CallbackTracker()

    @retry(attempts=3, backoff='exponential', delay=0.1, jitter=True, exceptions=(RuntimeError,), on_retry=tracker)
    async def async_fail_twice():
        if counter["count"] < 2:
            counter["count"] += 1
            raise RuntimeError("Async fail")
        return "ok"

    result = await async_fail_twice()
    assert result == "ok"
    assert counter["count"] == 2
    assert len(tracker.calls) == 2


# ------------------------------
# 5. Max total time test
# ------------------------------
def test_max_total_time_exceeded():
    counter = {"count": 0}

    @retry(attempts=10, delay=0.5, max_total_time=0.6, exceptions=(ValueError,))
    def slow_fail():
        counter["count"] += 1
        raise ValueError("Fail")

    with pytest.raises(ValueError):
        slow_fail()
    # Should not attempt all 10 times due to max_total_time
    assert counter["count"] < 10
