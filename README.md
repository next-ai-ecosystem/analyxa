# Analyxa

**Multi-dimensional extraction engine for AI conversations — in any language.**

Analyxa takes opaque conversations between users and AI agents and decomposes them into N configurable dimensions — sentiment, intensity, topics, risk signals, intent, entities, and more — stored as 1,536-dimensional semantic vectors.

[![PyPI version](https://badge.fury.io/py/analyxa.svg)](https://pypi.org/project/analyxa/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Multi-Language](https://img.shields.io/badge/languages-20%2B-blue)](https://github.com/next-ai-ecosystem/analyxa#multi-language-support)

---

## What it does

```
Conversation → Analyxa → Structured JSON (N fields) + Semantic Vector (1536D)
```

One conversation in, structured intelligence out:

- **11 universal fields** extracted from any conversation (language, sentiment, topics, risk signals, intent, entities, action items...)
- **Vertical schemas** add domain-specific fields: support (17), sales (17), coaching (19)
- **Semantic vectors** enable similarity search across thousands of conversations
- **Pipeline ready**: Redis queue → Analyxa → Qdrant vector DB

## Multi-Language Support

Analyxa automatically detects the conversation language and generates extracted values in that language. No configuration needed.

```python
from analyxa import analyze

# Spanish conversation
result = analyze("Cliente: Tengo un problema con mi factura...", schema="support")
result.fields["language"]   # "es"
result.fields["sentiment"]  # "negativo"
result.fields["summary"]    # "El cliente reporta un problema..."

# French conversation
result = analyze("Client: J'ai un problème avec ma facture...", schema="support")
result.fields["language"]   # "fr"
result.fields["sentiment"]  # "négatif"
```

- **Field keys** always in English (`sentiment`, not `sentimiento`)
- **Field values** in the detected language
- Works with any language supported by your LLM provider
- Backward compatible: English conversations return the same results plus `language: "en"`

## Quick Start

### Installation

```bash
pip install analyxa
```

### Python API

```python
from analyxa import analyze

result = analyze(
    "User: I was charged twice for my subscription.\n"
    "Agent: I see the duplicate charge. Processing a refund now.\n"
    "User: Thanks, but please make sure it doesn't happen again.",
    schema="support"
)

print(result.fields["sentiment"])           # "negative"
print(result.fields["satisfaction_prediction"])  # "dissatisfied"
print(result.fields["issue_category"])      # "billing"
print(result.fields["risk_signals"])        # ["frustration", "repeat_contact"]
```

### CLI

```bash
# Analyze a conversation file
analyxa analyze conversation.txt --schema support --output result.json

# List available schemas
analyxa schemas list

# Show schema fields
analyxa schemas show support

# Batch analyze a directory
analyxa batch ./conversations/ --schema universal --output-dir ./results/
```

### Environment Setup

Create a `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-...      # Required for analysis
OPENAI_API_KEY=sk-...              # Optional, for embeddings
ANALYXA_PROVIDER=anthropic         # or "openai"
ANALYXA_SCHEMA=universal           # Default schema
```

## Schemas

Analyxa uses YAML schemas to define what to extract. Schemas are hierarchical — vertical schemas inherit all universal fields.

| Schema | Fields | Description |
|--------|--------|-------------|
| **universal** | 11 | Base fields for any conversation |
| **support** | 17 | Customer support (+satisfaction, issue category, effort score...) |
| **sales** | 17 | Sales conversations (+buying stage, objections, budget signals...) |
| **coaching** | 19 | Coaching/therapeutic (+emotional valence, behavioral patterns, coping strategies...) |

### Universal Fields (included in all schemas)

| Field | Type | Description |
|-------|------|-------------|
| language | string | ISO 639-1 code of the conversation language |
| title | string | Descriptive session name |
| summary | string | 3-5 sentence summary (vectorized for search) |
| sentiment | keyword | User sentiment: positive, negative, mixed, neutral |
| sentiment_intensity | keyword | low, medium, high |
| topics | keyword_array | Specific topics discussed |
| session_outcome | keyword | resolved, unresolved, escalated, abandoned |
| user_intent | string | What the user really needed |
| risk_signals | keyword_array | frustration, churn_risk, complaint, urgency... |
| key_entities | keyword_array | People, products, dates, amounts mentioned |
| action_items | string_array | Explicit commitments or next steps |

### Custom Schemas

Create your own schema by inheriting from universal:

```yaml
metadata:
  name: my_vertical
  version: "1.0"
  description: "Custom schema for my use case"
  inherits: universal

fields:
  - name: custom_field
    type: keyword
    required: true
    description: "My custom dimension"
    prompt_hint: "Instructions for the LLM on how to extract this field"
    allowed_values: [option_a, option_b, option_c]
```

## Production Pipeline

### Redis → Analyxa → Qdrant

```bash
# Start infrastructure
cd docker && docker compose up -d

# Push conversations to Redis queue
analyxa redis push conversation.txt --schema support

# Process all pending conversations
analyxa redis process

# Search by semantic similarity
analyxa search "frustrated customer with billing issue" --limit 5
```

### Python Pipeline

```python
from analyxa.sources.redis_source import RedisSource
from analyxa.sinks.qdrant_sink import QdrantSink
from analyxa.batch import batch_analyze_from_redis

# Process Redis queue → Qdrant
result = batch_analyze_from_redis()
print(f"Processed: {result.successful}/{result.total}")

# Search similar conversations
sink = QdrantSink()
similar = sink.search_similar(query_embedding, limit=10, filters={"sentiment": "negative"})
```

## Configuration

All settings via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| ANTHROPIC_API_KEY | — | Anthropic API key |
| OPENAI_API_KEY | — | OpenAI API key (for embeddings) |
| ANALYXA_PROVIDER | anthropic | LLM provider: anthropic or openai |
| ANALYXA_MODEL | (provider default) | Model override |
| ANALYXA_SCHEMA | universal | Default schema |
| ANALYXA_EMBEDDINGS | true | Enable/disable embeddings |
| REDIS_URL | redis://localhost:6379 | Redis connection |
| QDRANT_URL | http://localhost:6333 | Qdrant connection |

## Architecture

```
src/analyxa/
├── analyzer.py          # Pipeline orchestrator
├── schema.py            # YAML schema loader with inheritance
├── prompt_builder.py    # Dynamic prompt generation from schemas
├── llm_client.py        # Multi-provider LLM abstraction
├── embeddings.py        # Semantic vector generation (1536D)
├── config.py            # Centralized configuration
├── cli.py               # Click CLI
├── batch.py             # Batch processing
├── sources/
│   ├── file_source.py   # Read from files
│   └── redis_source.py  # Read from Redis queue
├── sinks/
│   ├── json_sink.py     # Write to JSON files
│   ├── stdout_sink.py   # Print to terminal
│   └── qdrant_sink.py   # Store in Qdrant
└── schemas/
    ├── universal.yaml   # 10 base fields
    ├── support.yaml     # +6 support fields
    ├── sales.yaml       # +6 sales fields
    └── coaching.yaml    # +8 coaching fields
```

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

Built by [Next AI Ecosystem](https://analyxa.ai)
