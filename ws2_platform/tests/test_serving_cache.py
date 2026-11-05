"""Controlled concurrency/cache checks only; no fitting or real artifact writes."""
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Barrier, Event, Lock

import pandas as pd
import pytest

from ws2_platform.api import app as api
from ws2_platform.api.query import Store
from ws2_platform.tests.conftest import tiny_request


@pytest.mark.parametrize("fail", [False, True])
def test_same_key_shares_inflight_result_or_error_and_failure_can_retry(monkeypatch, fail):
    api._cache.clear()
    started, release, waiting = Event(), Event(), Event()
    guard, waiters, calls = Lock(), [], []

    class ObservedFuture(Future):
        def result(self, timeout=None):
            with guard:
                waiters.append(1)
                if len(waiters) == 3:
                    waiting.set()
            return super().result(timeout)

    monkeypatch.setattr(api, "Future", ObservedFuture)

    def compute():
        calls.append(1)
        started.set()
        assert release.wait(5)
        if fail:
            raise ValueError("temporary failure")
        return {"value": 7}

    with ThreadPoolExecutor(max_workers=4) as pool:
        leader = pool.submit(api._cached, "shared", compute)
        assert started.wait(5)
        followers = [pool.submit(api._cached, "shared", compute) for _ in range(3)]
        try:
            assert waiting.wait(5), "Followers did not join the in-flight result"
        finally:
            release.set()
        for task in [leader, *followers]:
            if fail:
                with pytest.raises(ValueError, match="temporary failure"):
                    task.result(timeout=5)
            else:
                assert task.result(timeout=5) == {"value": 7}
    assert len(calls) == 1
    assert not api._inflight
    if fail:
        assert api._cached("shared", lambda: {"value": 8}) == {"value": 8}
    api._cache.clear()


def test_different_cache_keys_compute_concurrently():
    barrier = Barrier(2)

    def compute():
        barrier.wait(timeout=5)
        return {"ok": True}

    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks = [pool.submit(api._cached, name, compute) for name in ("parallel-a", "parallel-b")]
        assert all(task.result(timeout=10) == {"ok": True} for task in tasks)
    api._cache.clear()


def test_lazy_store_initialization_returns_one_instance(monkeypatch):
    entered = Barrier(5)
    constructed = []

    class FakeStore:
        def __init__(self, directory):
            constructed.append(self)

    monkeypatch.setattr(api, "Store", FakeStore)
    monkeypatch.setattr(api, "_store", None)

    def get():
        entered.wait(timeout=5)
        return api.store()

    with ThreadPoolExecutor(max_workers=5) as pool:
        stores = list(pool.map(lambda _: get(), range(5)))
    assert len(constructed) == 1
    assert all(value is constructed[0] for value in stores)


def test_endpoint_keys_use_cell_membership_and_only_relevant_fields(tiny_api):
    base = api.AOIRequest(**tiny_request("bd"))
    x0, y0, x1, y1 = base.bbox
    polygon = base.model_copy(update={"bbox": None, "geometry": {
        "type": "Polygon", "coordinates": [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]],
    }})
    assert api._key("summary", base) == api._key("summary", polygon)
    changed = base.model_copy(update={"start": base.start.replace(year=2005), "res": "month"})
    for endpoint in ("outlook", "season"):
        assert api._key(endpoint, base) == api._key(endpoint, changed)
    assert api._key("summary", base) != api._key("summary", changed)
    assert api._key("cells", base) != api._key("cells", changed)
    assert api._key("periods", base) != api._key("periods", changed)
    assert len(api._key("summary", polygon)) < 100


def test_store_memo_cap_and_cell_identity_are_exact(tiny_api):
    s = api.store()
    s.__dict__.pop("_memo_cache", None)
    for i in range(70):
        assert s._memo("test", pd.DataFrame({"cell_id": [i]}), lambda i=i: i) == i
    assert len(s._memo_cache) == 64
    assert s._memo("ordered", pd.DataFrame({"cell_id": [2, 1]}), lambda: 123) == 123
    assert s._memo("ordered", pd.DataFrame({"cell_id": [1, 2]}), lambda: 999) == 123
    assert len(s._memo_cache) == 64
