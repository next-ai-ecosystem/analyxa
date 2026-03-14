# API Reference

## Core Functions

### `analyze()`

Convenience function for quick analysis.

```python
from analyxa import analyze

result = analyze(
    conversation: str,       # Conversation text
    schema: str = "universal",   # Schema name
    provider: str = "anthropic", # LLM provider
    model: str | None = None,    # Model override
    context: dict | None = None, # Additional context
    enable_embeddings: bool = True
) -> AnalysisResult
```

### `Analyzer`

Reusable analyzer instance (recommended for multiple analyses).

```python
from analyxa import Analyzer

analyzer = Analyzer(
    schema_name="support",
    provider="anthropic",
    model=None,           # Uses provider default
    enable_embeddings=True
)

result = analyzer.analyze(conversation, context={"agent_name": "SupportBot"})
```

## AnalysisResult

```python
result.fields              # dict — Extracted fields
result.schema_name         # str — Schema used
result.schema_version      # str — Schema version
result.analyzed_at         # str — ISO 8601 timestamp
result.analysis_model      # str — LLM model used
result.embedding           # list[float] | None — 1536D vector
result.conversation_hash   # str — SHA-256 hash (16 chars)
result.session_length      # int — Number of messages
result.validation_errors   # list[str] — Validation warnings
result.llm_response        # LLMResponse — Full LLM response

result.to_dict()           # dict with fields + _meta (for storage)
result.to_flat_dict()      # dict with fields + meta at same level (for export)
```

## SchemaManager

```python
from analyxa import SchemaManager

sm = SchemaManager(schemas_dir=None)  # None = package default

sm.load_schema("support")           # dict — Full schema with inheritance
sm.list_schemas()                    # list[str] — Available schema names
sm.get_field_names("support")        # list[str] — Field names in order
sm.validate_result("support", data)  # (bool, list[str]) — Validation
```

## Batch Processing

```python
from analyxa.batch import batch_analyze, batch_analyze_from_redis, BatchResult

# From a list of conversations
result = batch_analyze(
    conversations=[{"text": "...", "id": "conv1"}, ...],
    schema_name="support",
    on_progress=lambda cur, tot, res: print(f"{cur}/{tot}")
)

# From Redis queue to Qdrant
result = batch_analyze_from_redis(max_items=100)

result.total          # int
result.successful     # int
result.failed         # int
result.success_rate   # float (0.0-1.0)
result.elapsed_seconds # float
```

## Sources

```python
from analyxa.sources.file_source import FileSource
from analyxa.sources.redis_source import RedisSource

# File
source = FileSource("conversation.txt")
text = source.read()
messages = source.read_messages()  # [{"role": "user", "content": "..."}]

# Redis
redis = RedisSource(url="redis://localhost:6379")
conv_id = redis.push("User: hello\nAgent: hi", schema="support")
data = redis.get(conv_id)
pending = redis.pending()
next_conv = redis.next()
redis.mark_analyzed(conv_id)
```

## Sinks

```python
from analyxa.sinks.json_sink import JsonSink
from analyxa.sinks.stdout_sink import StdoutSink
from analyxa.sinks.qdrant_sink import QdrantSink

# JSON file
JsonSink("result.json").write(result.to_flat_dict())

# Terminal
StdoutSink().write(result.to_flat_dict())

# Qdrant
qdrant = QdrantSink(url="http://localhost:6333", collection="analyxa_analyses")
point_id = qdrant.store(result)
similar = qdrant.search_similar(embedding, limit=10, filters={"sentiment": "negative"})
```

## Configuration

```python
from analyxa.config import get_config, reset_config

config = get_config()               # Singleton, reads .env
config.anthropic_api_key            # str | None
config.default_provider             # str
config.default_schema               # str
config.enable_embeddings            # bool
config.to_dict()                    # dict (API keys masked)

reset_config()                      # Reset singleton (for tests)
```
