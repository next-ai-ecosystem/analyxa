"""Tests for QdrantSink — integration tests requiring Qdrant running."""

import pytest

try:
    import qdrant_client as _qc
    _QDRANT_AVAILABLE = True
    try:
        _qc.QdrantClient(url="http://localhost:6333").get_collections()
    except Exception:
        _QDRANT_AVAILABLE = False
except ImportError:
    _QDRANT_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _QDRANT_AVAILABLE,
    reason="Qdrant not available on localhost:6333",
)

_TEST_COLLECTION = "analyxa_test_qdrant"
_VECTOR_SIZE = 1536


def _fake_embedding(seed: float = 1.0) -> list[float]:
    """Generate a deterministic fake 1536D embedding."""
    import math
    return [math.sin(i * seed * 0.01) for i in range(_VECTOR_SIZE)]


def _make_result(
    title: str = "Test Session",
    sentiment: str = "positive",
    schema_name: str = "universal",
    embedding: list[float] | None = None,
):
    """Build a minimal AnalysisResult-like object for tests."""
    from unittest.mock import MagicMock
    result = MagicMock()
    result.embedding = embedding if embedding is not None else _fake_embedding()
    result.validation_errors = []
    result.to_dict.return_value = {
        "title": title,
        "summary": f"Summary of {title}.",
        "sentiment": sentiment,
        "sentiment_intensity": "medium",
        "topics": ["billing"],
        "session_outcome": "resolved",
        "user_intent": "Test intent",
        "risk_signals": [],
        "key_entities": [],
        "action_items": [],
        "_meta": {
            "schema_name": schema_name,
            "schema_version": "1.0.0",
            "has_embedding": True,
        },
    }
    return result


@pytest.fixture
def qdrant_sink():
    """Create QdrantSink with test collection and clean up after."""
    from analyxa.sinks.qdrant_sink import QdrantSink
    sink = QdrantSink(collection=_TEST_COLLECTION)
    yield sink
    sink.delete_collection()


# ------------------------------------------------------------------
# Test 1: store and get
# ------------------------------------------------------------------

def test_store_and_get(qdrant_sink):
    result = _make_result(title="Billing Issue")
    point_id = qdrant_sink.store(result)

    assert isinstance(point_id, str)
    assert len(point_id) == 36  # UUID format

    payload = qdrant_sink.get(point_id)
    assert payload is not None
    assert payload["title"] == "Billing Issue"
    assert payload["sentiment"] == "positive"


# ------------------------------------------------------------------
# Test 2: search_similar
# ------------------------------------------------------------------

def test_search_similar(qdrant_sink):
    r1 = _make_result(title="Session A", embedding=_fake_embedding(1.0))
    r2 = _make_result(title="Session B", embedding=_fake_embedding(2.0))
    r3 = _make_result(title="Session C", embedding=_fake_embedding(3.0))

    qdrant_sink.store(r1)
    qdrant_sink.store(r2)
    qdrant_sink.store(r3)

    results = qdrant_sink.search_similar(_fake_embedding(1.0), limit=2)
    assert len(results) == 2
    assert all("score" in r for r in results)
    assert all(r["score"] > 0 for r in results)
    assert all("payload" in r for r in results)


# ------------------------------------------------------------------
# Test 3: search with filter
# ------------------------------------------------------------------

def test_search_with_filter(qdrant_sink):
    r_pos = _make_result(title="Positive", sentiment="positive")
    r_neg1 = _make_result(title="Negative 1", sentiment="negative", embedding=_fake_embedding(2.0))
    r_neg2 = _make_result(title="Negative 2", sentiment="negative", embedding=_fake_embedding(3.0))

    qdrant_sink.store(r_pos)
    qdrant_sink.store(r_neg1)
    qdrant_sink.store(r_neg2)

    results = qdrant_sink.search_similar(
        _fake_embedding(1.0),
        limit=10,
        filters={"sentiment": "negative"},
    )
    assert len(results) == 2
    assert all(r["payload"]["sentiment"] == "negative" for r in results)


# ------------------------------------------------------------------
# Test 4: count
# ------------------------------------------------------------------

def test_count(qdrant_sink):
    assert qdrant_sink.count() == 0

    qdrant_sink.store(_make_result(title="One"))
    qdrant_sink.store(_make_result(title="Two"))
    qdrant_sink.store(_make_result(title="Three"))

    assert qdrant_sink.count() == 3


# ------------------------------------------------------------------
# Test 5: count with filter
# ------------------------------------------------------------------

def test_count_with_filter(qdrant_sink):
    r_universal = _make_result(schema_name="universal")
    r_support1 = _make_result(schema_name="support", embedding=_fake_embedding(2.0))
    r_support2 = _make_result(schema_name="support", embedding=_fake_embedding(3.0))

    # Update _meta in to_dict return
    for r, sn in [(r_universal, "universal"), (r_support1, "support"), (r_support2, "support")]:
        d = r.to_dict.return_value
        d["_meta"]["schema_name"] = sn

    qdrant_sink.store(r_universal)
    qdrant_sink.store(r_support1)
    qdrant_sink.store(r_support2)

    support_count = qdrant_sink.count(filters={"_meta.schema_name": "support"})
    assert support_count == 2


# ------------------------------------------------------------------
# Test 6: store without embedding
# ------------------------------------------------------------------

def test_store_without_embedding(qdrant_sink):
    result = _make_result(title="No Embedding")
    result.embedding = None
    d = result.to_dict.return_value
    d["_meta"]["has_embedding"] = False

    point_id = qdrant_sink.store(result)
    assert isinstance(point_id, str)

    payload = qdrant_sink.get(point_id)
    assert payload is not None
    assert payload["_meta"]["has_embedding"] is False


# ------------------------------------------------------------------
# Test 7: delete collection
# ------------------------------------------------------------------

def test_delete_collection(qdrant_sink):
    qdrant_sink.store(_make_result())
    assert qdrant_sink.count() == 1

    qdrant_sink.delete_collection()

    # After deletion, creating again should give 0
    from analyxa.sinks.qdrant_sink import QdrantSink
    sink2 = QdrantSink(collection=_TEST_COLLECTION)
    assert sink2.count() == 0
    sink2.delete_collection()


# ------------------------------------------------------------------
# Test 8: _ensure_collection idempotent
# ------------------------------------------------------------------

def test_ensure_collection_idempotent(qdrant_sink):
    # Call multiple times — should not raise
    qdrant_sink._ensure_collection()
    qdrant_sink._ensure_collection()
    qdrant_sink._ensure_collection()

    # Collection still exists and works
    assert qdrant_sink.count() == 0
