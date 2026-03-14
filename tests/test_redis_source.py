"""Tests for RedisSource — integration tests requiring Redis running."""

import pytest

try:
    import redis as redis_lib
    _REDIS_AVAILABLE = True
    try:
        redis_lib.Redis.from_url("redis://localhost:6379", decode_responses=True).ping()
    except Exception:
        _REDIS_AVAILABLE = False
except ImportError:
    _REDIS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _REDIS_AVAILABLE,
    reason="Redis not available on localhost:6379",
)


@pytest.fixture
def redis_source():
    """Create RedisSource and flush after each test."""
    from analyxa.sources.redis_source import RedisSource
    source = RedisSource()
    yield source
    source.flush()


# ------------------------------------------------------------------
# Test 1: push and get
# ------------------------------------------------------------------

def test_push_and_get(redis_source):
    conv_id = redis_source.push("User: hello\nAgent: hi", schema="universal")
    data = redis_source.get(conv_id)

    assert data is not None
    assert data["text"] == "User: hello\nAgent: hi"
    assert data["schema"] == "universal"
    assert data["status"] == "pending"
    assert data["id"] == conv_id


# ------------------------------------------------------------------
# Test 2: push generates UUID
# ------------------------------------------------------------------

def test_push_generates_id(redis_source):
    conv_id = redis_source.push("hello")
    assert isinstance(conv_id, str)
    assert len(conv_id) == 36  # UUID4 format: 8-4-4-4-12
    assert conv_id.count("-") == 4


# ------------------------------------------------------------------
# Test 3: pending list
# ------------------------------------------------------------------

def test_pending_list(redis_source):
    id1 = redis_source.push("conv one")
    id2 = redis_source.push("conv two")
    id3 = redis_source.push("conv three")

    pending = redis_source.pending()
    assert len(pending) == 3
    assert id1 in pending
    assert id2 in pending
    assert id3 in pending


# ------------------------------------------------------------------
# Test 4: next returns pending (FIFO)
# ------------------------------------------------------------------

def test_next_returns_pending(redis_source):
    id1 = redis_source.push("first conversation")
    redis_source.push("second conversation")

    item = redis_source.next()
    assert item is not None
    assert item["id"] == id1
    assert item["text"] == "first conversation"
    assert "status" in item
    assert "schema" in item


# ------------------------------------------------------------------
# Test 5: mark_analyzed
# ------------------------------------------------------------------

def test_mark_analyzed(redis_source):
    conv_id = redis_source.push("test conversation")
    redis_source.mark_analyzed(conv_id)

    data = redis_source.get(conv_id)
    assert data["status"] == "analyzed"
    assert "analyzed_at" in data


# ------------------------------------------------------------------
# Test 6: mark_failed
# ------------------------------------------------------------------

def test_mark_failed(redis_source):
    conv_id = redis_source.push("test conversation")
    redis_source.mark_failed(conv_id, "API error: timeout")

    data = redis_source.get(conv_id)
    assert data["status"] == "failed"
    assert data["error"] == "API error: timeout"
    assert "failed_at" in data


# ------------------------------------------------------------------
# Test 7: list_all with filter
# ------------------------------------------------------------------

def test_list_all_with_filter(redis_source):
    id1 = redis_source.push("conv one")
    id2 = redis_source.push("conv two")
    id3 = redis_source.push("conv three")

    redis_source.mark_analyzed(id1)

    pending_list = redis_source.list_all(status="pending")
    analyzed_list = redis_source.list_all(status="analyzed")

    assert len(pending_list) == 2
    assert len(analyzed_list) == 1
    assert analyzed_list[0]["id"] == id1
    assert id2 in [item["id"] for item in pending_list]
    assert id3 in [item["id"] for item in pending_list]


# ------------------------------------------------------------------
# Test 8: flush
# ------------------------------------------------------------------

def test_flush(redis_source):
    for i in range(5):
        redis_source.push(f"conversation {i}")

    deleted = redis_source.flush()
    assert deleted >= 5  # 5 hashes + 1 list = 6

    all_items = redis_source.list_all()
    assert len(all_items) == 0


# ------------------------------------------------------------------
# Test 9: push with context
# ------------------------------------------------------------------

def test_push_with_context(redis_source):
    context = {"agent_name": "SupportBot", "session_id": "abc123"}
    conv_id = redis_source.push("User: help\nAgent: sure", context=context)

    data = redis_source.get(conv_id)
    assert data["context"] == context
    assert data["context"]["agent_name"] == "SupportBot"
    assert data["context"]["session_id"] == "abc123"
