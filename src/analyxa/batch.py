"""Batch processor — analyzes multiple conversations in sequence."""

import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class BatchResult:
    """Result of a batch analysis run."""

    total: int
    successful: int
    failed: int
    results: list  # list[AnalysisResult]
    errors: list[dict]  # [{"id": str, "error": str}]
    elapsed_seconds: float

    @property
    def success_rate(self) -> float:
        return self.successful / self.total if self.total > 0 else 0.0


def batch_analyze(
    conversations: list[dict],
    schema_name: str = "universal",
    provider: str = "anthropic",
    model: str | None = None,
    enable_embeddings: bool = True,
    sink: Any | None = None,
    on_progress: Callable | None = None,
) -> BatchResult:
    """Analyze a list of conversations in sequence.

    Args:
        conversations: List of dicts with at least {"text": str}.
                       Optional: {"text": str, "id": str, "context": dict}
        schema_name: Schema to use for all analyses.
        provider: LLM provider.
        model: LLM model override.
        enable_embeddings: Whether to generate embeddings.
        sink: If provided, write each result immediately after analysis.
              Supports QdrantSink.store() or JsonSink.write() / StdoutSink.write().
        on_progress: Callback (current: int, total: int, result | None) -> None
    """
    from analyxa.analyzer import Analyzer

    start = time.monotonic()
    total = len(conversations)
    successful = 0
    failed = 0
    results = []
    errors = []

    # Create a single Analyzer — reuses schema cache across all analyses
    analyzer = Analyzer(
        schema_name=schema_name,
        provider=provider,
        model=model,
        enable_embeddings=enable_embeddings,
    )

    for i, conv in enumerate(conversations, 1):
        text = conv.get("text", "")
        conv_id = conv.get("id", str(i))
        context = conv.get("context")

        try:
            result = analyzer.analyze(text, context=context)
            results.append(result)
            successful += 1

            if sink is not None:
                try:
                    if hasattr(sink, "store"):
                        sink.store(result)
                    elif hasattr(sink, "write"):
                        sink.write(result.to_flat_dict())
                except Exception:
                    pass  # Sink errors don't abort the batch

        except Exception as exc:
            failed += 1
            errors.append({"id": conv_id, "error": f"{type(exc).__name__}: {exc}"})
            results.append(None)

        if on_progress is not None:
            on_progress(i, total, results[-1])

    elapsed = time.monotonic() - start
    return BatchResult(
        total=total,
        successful=successful,
        failed=failed,
        results=[r for r in results if r is not None],
        errors=errors,
        elapsed_seconds=elapsed,
    )


def batch_analyze_from_redis(
    redis_source=None,
    qdrant_sink=None,
    max_items: int | None = None,
    provider: str = "anthropic",
    model: str | None = None,
    enable_embeddings: bool = True,
    on_progress: Callable | None = None,
) -> BatchResult:
    """Process pending conversations from Redis queue and store in Qdrant.

    Args:
        redis_source: RedisSource instance. Created with defaults if None.
        qdrant_sink: QdrantSink instance. Created with defaults if None.
        max_items: Max conversations to process. None = all pending.
        provider: LLM provider.
        model: LLM model override.
        enable_embeddings: Whether to generate embeddings.
        on_progress: Callback (current: int, total: int, result | None) -> None
    """
    from analyxa.sources.redis_source import RedisSource
    from analyxa.sinks.qdrant_sink import QdrantSink
    from analyxa.analyzer import Analyzer

    if redis_source is None:
        redis_source = RedisSource()
    if qdrant_sink is None:
        qdrant_sink = QdrantSink()

    # Gather pending conversations
    pending_ids = redis_source.pending()
    if max_items is not None:
        pending_ids = pending_ids[:max_items]

    total = len(pending_ids)
    start = time.monotonic()
    successful = 0
    failed = 0
    results = []
    errors = []

    for i, conv_id in enumerate(pending_ids, 1):
        conv_data = redis_source.get(conv_id)
        if conv_data is None:
            failed += 1
            errors.append({"id": conv_id, "error": "Conversation not found in Redis"})
            if on_progress is not None:
                on_progress(i, total, None)
            continue

        text = conv_data.get("text", "")
        schema = conv_data.get("schema", "universal")
        context = conv_data.get("context")

        try:
            analyzer = Analyzer(
                schema_name=schema,
                provider=provider,
                model=model,
                enable_embeddings=enable_embeddings,
            )
            result = analyzer.analyze(text, context=context)
            redis_source.mark_analyzed(conv_id)
            qdrant_sink.store(result)
            results.append(result)
            successful += 1

        except Exception as exc:
            error_msg = f"{type(exc).__name__}: {exc}"
            redis_source.mark_failed(conv_id, error_msg)
            failed += 1
            errors.append({"id": conv_id, "error": error_msg})

        if on_progress is not None:
            on_progress(i, total, results[-1] if results else None)

    elapsed = time.monotonic() - start
    return BatchResult(
        total=total,
        successful=successful,
        failed=failed,
        results=results,
        errors=errors,
        elapsed_seconds=elapsed,
    )
