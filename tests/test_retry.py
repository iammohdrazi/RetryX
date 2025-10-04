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
        print(f"[Callback] Attempt {attempt} failed with exception: {exc}")


# ------------------------------
# 1. Test sync function retry
# ------------------------------
def test_sync_retry_fixed_backoff():
    counter = {"count": 0}

    @retry(attempts=3, backoff='fixed', delay=0.1, exceptions=(ValueError,))
    def fail_twice():
        if counter["count"] < 2:
            counter["count"] += 1
            print(f"[Sync Fixed] Attempt {counter['count']}: Failing")
            raise ValueError("Failing")
        print(f"[Sync Fixed] Attempt {counter['count'] + 1}: Succeeded")
        return True

    start = time.time()
    result = fail_twice()
    elapsed = time.time() - start

    print(f"[Sync Fixed] Result: {result}, Attempts: {counter['count']}")
    assert result is True
    assert counter["count"] == 2
    assert elapsed >= 0.2


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
            print(f"[Sync Exp] Attempt {counter['count']}: Failing")
            raise ValueError("Failing")
        print(f"[Sync Exp] Attempt {counter['count'] + 1}: Succeeded")
        return "success"

    result = fail_twice()
    print(f"[Sync Exp] Result: {result}, Attempts: {counter['count']}, Callbacks: {len(tracker.calls)}")
    assert result == "success"
    assert counter["count"] == 2
    assert len(tracker.calls) == 2


# ------------------------------
# 2. Test default return value
# ------------------------------
def test_default_return_value():
    counter = {"count": 0}

    @retry(attempts=2, delay=0.1, exceptions=(ValueError,), default="failed")
    def always_fail():
        counter["count"] += 1
        print(f"[Default Return] Attempt {counter['count']}: Failing")
        raise ValueError("Fail")

    result = always_fail()
    print(f"[Default Return] Result: {result}, Attempts: {counter['count']}")
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
            print(f"[Retry If] Attempt {counter['count']}: Returning None")
            return None
        print(f"[Retry If] Attempt {counter['count'] + 1}: Returning 'done'")
        return "done"

    result = return_none_twice()
    print(f"[Retry If] Result: {result}, Attempts: {counter['count']}")
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
            print(f"[Async Fixed] Attempt {counter['count']}: Failing")
            raise RuntimeError("Async fail")
        print(f"[Async Fixed] Attempt {counter['count'] + 1}: Succeeded")
        return "ok"

    result = await async_fail_twice()
    print(f"[Async Fixed] Result: {result}, Attempts: {counter['count']}")
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
            print(f"[Async Exp] Attempt {counter['count']}: Failing")
            raise RuntimeError("Async fail")
        print(f"[Async Exp] Attempt {counter['count'] + 1}: Succeeded")
        return "ok"

    result = await async_fail_twice()
    print(f"[Async Exp] Result: {result}, Attempts: {counter['count']}, Callbacks: {len(tracker.calls)}")
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
        print(f"[Max Total] Attempt {counter['count']}: Failing")
        raise ValueError("Fail")

    with pytest.raises(ValueError):
        slow_fail()
    print(f"[Max Total] Attempts made before exceeding max_total_time: {counter['count']}")
    assert counter["count"] < 10
