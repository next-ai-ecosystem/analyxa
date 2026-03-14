"""Qdrant Sink — stores analysis results as semantic vectors in Qdrant."""

import uuid

try:
    import qdrant_client
    from qdrant_client.models import (
        Distance,
        FieldCondition,
        Filter,
        MatchValue,
        PointStruct,
        VectorParams,
    )
except ImportError:
    qdrant_client = None

_VECTOR_SIZE = 1536
_ZERO_VECTOR = [0.0] * _VECTOR_SIZE


class QdrantSink:
    """Stores AnalysisResult objects as vector points in Qdrant.

    Auto-creates the collection on init if it doesn't exist.
    Points without embeddings use a zero vector and have _meta.has_embedding=False.
    """

    def __init__(
        self,
        url: str | None = None,
        collection: str | None = None,
    ) -> None:
        if qdrant_client is None:
            raise ImportError(
                "qdrant-client package not installed. Run: pip install qdrant-client"
            )

        if url is None:
            try:
                from analyxa.config import get_config
                config = get_config()
                url = config.qdrant_url
            except Exception:
                pass
        if url is None:
            url = "http://localhost:6333"

        if collection is None:
            try:
                from analyxa.config import get_config
                config = get_config()
                collection = config.qdrant_collection
            except Exception:
                pass
        if collection is None:
            collection = "analyxa_analyses"

        self.collection = collection
        self._client = qdrant_client.QdrantClient(url=url)
        self._ensure_collection()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        if not self._client.collection_exists(self.collection):
            self._client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=_VECTOR_SIZE, distance=Distance.COSINE),
            )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def store(self, result) -> str:
        """Store an AnalysisResult as a Qdrant point. Returns the point_id."""
        point_id = str(uuid.uuid4())

        vector = result.embedding if result.embedding is not None else _ZERO_VECTOR
        payload = result.to_dict()

        self._client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
        return point_id

    def write(self, result_dict: dict) -> None:
        """Alternative write interface for compatibility with other sinks."""
        # Not used for AnalysisResult objects — use store() instead
        raise NotImplementedError("Use store(AnalysisResult) for QdrantSink.")

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def search_similar(
        self,
        query_embedding: list[float],
        limit: int = 10,
        filters: dict | None = None,
    ) -> list[dict]:
        """Search for similar analyses by cosine distance.

        filters example: {"sentiment": "negative"} or {"_meta.schema_name": "support"}
        """
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
            qdrant_filter = Filter(must=conditions)

        response = self._client.query_points(
            collection_name=self.collection,
            query=query_embedding,
            limit=limit,
            query_filter=qdrant_filter,
            with_payload=True,
        )

        return [
            {
                "id": str(r.id),
                "score": r.score,
                "payload": r.payload,
            }
            for r in response.points
        ]

    def get(self, point_id: str) -> dict | None:
        """Retrieve a point by ID. Returns payload dict or None."""
        results = self._client.retrieve(
            collection_name=self.collection,
            ids=[point_id],
            with_payload=True,
        )
        if not results:
            return None
        return results[0].payload

    def count(self, filters: dict | None = None) -> int:
        """Count points in the collection with optional filters."""
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
            qdrant_filter = Filter(must=conditions)

        result = self._client.count(
            collection_name=self.collection,
            count_filter=qdrant_filter,
        )
        return result.count

    def delete_collection(self) -> None:
        """Delete the entire collection. Used for testing/reset."""
        self._client.delete_collection(collection_name=self.collection)
