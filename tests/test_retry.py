import pytest
from retryx import retry

def test_retry_success():
    calls = {"count": 0}

    @retry(attempts=3)
    def always_succeeds():
        calls["count"] += 1
        return "ok"

    result = always_succeeds()
    assert result == "ok"
    assert calls["count"] == 1  # should succeed first time

def test_retry_eventual_success():
    calls = {"count": 0}

    @retry(attempts=3)
    def succeeds_after_two():
        calls["count"] += 1
        if calls["count"] < 2:
            raise ValueError("fail")
        return "ok"

    result = succeeds_after_two()
    assert result == "ok"
    assert calls["count"] == 2
