import numpy as np

from secrag.store import VectorStore


def _norm(v):
    v = np.asarray(v, dtype=np.float32)
    return v / np.linalg.norm(v)


def test_search_ranks_by_cosine():
    store = VectorStore()
    store.add(
        [_norm([1, 0, 0]), _norm([0, 1, 0]), _norm([1, 1, 0])],
        [{"id": "x"}, {"id": "y"}, {"id": "xy"}],
    )
    hits = store.search(_norm([1, 0, 0]), k=3)
    assert hits[0][0]["id"] == "x"          # identical vector wins
    assert hits[0][1] > hits[1][1]           # scores are ordered
    assert [h[0]["id"] for h in hits][:2] == ["x", "xy"]


def test_empty_store_returns_nothing():
    assert VectorStore().search(_norm([1, 0]), k=5) == []


def test_save_and_load_roundtrip(tmp_path):
    store = VectorStore()
    store.add([_norm([1, 0]), _norm([0, 1])], [{"id": "a"}, {"id": "b"}])
    path = str(tmp_path / "idx")
    store.save(path)
    loaded = VectorStore.load(path)
    assert len(loaded) == 2
    assert loaded.search(_norm([0, 1]), k=1)[0][0]["id"] == "b"
