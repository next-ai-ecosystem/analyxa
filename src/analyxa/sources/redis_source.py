"""Redis Source — reads conversations from a Redis queue."""

import json
import uuid
from datetime import datetime, timezone

try:
    import redis as redis_lib
except ImportError:
    redis_lib = None

_QUEUE_KEY = "analyxa:conversations"
_CONV_PREFIX = "analyxa:conv:"


class RedisSource:
    """Reads and manages conversations from a Redis queue.

    Schema:
    - analyxa:conversations  → List (queue, FIFO). Each element is a conversation_id.
    - analyxa:conv:{id}      → Hash with: text, schema, context, status, pushed_at
    """

    def __init__(self, url: str | None = None) -> None:
        if redis_lib is None:
            raise ImportError("redis package not installed. Run: pip install redis")

        if url is None:
            try:
                from analyxa.config import get_config
                config = get_config()
                url = config.redis_url
            except Exception:
                pass
        if url is None:
            url = "redis://localhost:6379"

        self._url = url
        # Lazy connection — no error if Redis is unavailable at init
        self._client = redis_lib.Redis.from_url(url, decode_responses=True)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def push(
        self,
        conversation: str,
        conversation_id: str | None = None,
        schema: str = "universal",
        context: dict | None = None,
    ) -> str:
        """Push a conversation to the Redis queue. Returns the conversation_id."""
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())

        key = f"{_CONV_PREFIX}{conversation_id}"
        self._client.hset(key, mapping={
            "text": conversation,
            "schema": schema,
            "context": json.dumps(context) if context else "",
            "status": "pending",
            "pushed_at": datetime.now(timezone.utc).isoformat(),
        })
        self._client.rpush(_QUEUE_KEY, conversation_id)

        return conversation_id

    def mark_analyzed(self, conversation_id: str) -> None:
        """Mark conversation as successfully analyzed."""
        key = f"{_CONV_PREFIX}{conversation_id}"
        self._client.hset(key, mapping={
            "status": "analyzed",
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        })

    def mark_failed(self, conversation_id: str, error: str) -> None:
        """Mark conversation as failed with an error message."""
        key = f"{_CONV_PREFIX}{conversation_id}"
        self._client.hset(key, mapping={
            "status": "failed",
            "error": error,
            "failed_at": datetime.now(timezone.utc).isoformat(),
        })

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get(self, conversation_id: str) -> dict | None:
        """Retrieve a conversation by ID. Returns None if not found."""
        key = f"{_CONV_PREFIX}{conversation_id}"
        data = self._client.hgetall(key)
        if not data:
            return None

        # Parse context from JSON string
        raw_context = data.get("context", "")
        try:
            data["context"] = json.loads(raw_context) if raw_context else None
        except (json.JSONDecodeError, ValueError):
            data["context"] = None

        data["id"] = conversation_id
        return data

    def pending(self) -> list[str]:
        """Return list of conversation IDs with status='pending'."""
        all_ids = self._client.lrange(_QUEUE_KEY, 0, -1)
        result = []
        for conv_id in all_ids:
            key = f"{_CONV_PREFIX}{conv_id}"
            status = self._client.hget(key, "status")
            if status == "pending":
                result.append(conv_id)
        return result

    def next(self, _depth: int = 0) -> dict | None:
        """Pop next pending conversation from the queue (FIFO). Returns None if empty."""
        if _depth >= 100:
            return None

        conv_id = self._client.lpop(_QUEUE_KEY)
        if conv_id is None:
            return None

        data = self.get(conv_id)
        if data is None or data.get("status") != "pending":
            return self.next(_depth=_depth + 1)

        return data

    def list_all(self, status: str | None = None) -> list[dict]:
        """List all conversations (with optional status filter), sorted by pushed_at desc."""
        result = []
        for key in self._client.scan_iter(match=f"{_CONV_PREFIX}*"):
            conv_id = key[len(_CONV_PREFIX):]
            data = self._client.hgetall(key)
            if not data:
                continue
            if status is not None and data.get("status") != status:
                continue
            result.append({
                "id": conv_id,
                "schema": data.get("schema", "universal"),
                "status": data.get("status", "unknown"),
                "pushed_at": data.get("pushed_at", ""),
            })

        result.sort(key=lambda x: x["pushed_at"], reverse=True)
        return result

    def flush(self) -> int:
        """Delete all analyxa:* keys. Returns number of keys deleted."""
        keys = list(self._client.scan_iter(match="analyxa:*"))
        if not keys:
            return 0
        return self._client.delete(*keys)
