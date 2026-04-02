# Changelog

All notable changes to Analyxa will be documented in this file.

This project follows [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-04-02

### Added
- **Multi-language support**: Analyxa now automatically detects the conversation language and generates field values in that language
- New `language` field (ISO 639-1) in all schemas — universal (11 fields), support (17), sales (17), coaching (19)
- Four new example conversations: Spanish (support), French (sales), Portuguese (coaching), German (support)
- 10 new multi-language tests

### How it works
- Language detection is automatic — no configuration needed
- Field **keys** remain in English (`sentiment`, not `sentimiento`) for API consistency
- Field **values** are generated in the detected language
- English conversations produce identical results to v0.1.0, plus the new `language: "en"` field
- Supported: any language your LLM provider supports (Claude and GPT-4o handle 20+ languages natively)

### Example
```python
from analyxa import analyze

result = analyze("Cliente: Hola, tengo un problema con mi factura...", schema="support")
print(result.fields["language"])   # "es"
print(result.fields["sentiment"])  # "negativo"
print(result.fields["summary"])    # "El cliente reporta un problema de facturación..."
```

## [0.1.0] - 2026-03-14

### Added
- Initial release
- Multi-dimensional extraction engine for AI conversations
- 4 schemas: universal (10 fields), support (16), sales (16), coaching (18)
- Multi-provider LLM support: Anthropic (Claude) and OpenAI (GPT-4o)
- Semantic embeddings (1,536D) via OpenAI text-embedding-3-small
- Redis source for conversation queuing
- Qdrant sink for vector storage and semantic search
- CLI with 8+ commands: analyze, batch, search, schemas, redis, version
- Python API: `from analyxa import analyze`
- Docker Compose for Redis + Qdrant infrastructure
- Apache 2.0 license
