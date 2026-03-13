"""Analyzer — main pipeline orchestrator for Analyxa."""

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from analyxa.schema import SchemaManager
from analyxa.prompt_builder import build_prompt
from analyxa.llm_client import LLMClient, LLMResponse
from analyxa.embeddings import EmbeddingGenerator


@dataclass
class AnalysisResult:
    """Full result of a conversation analysis run."""

    # Fields extracted by the LLM
    fields: dict

    # Schema metadata
    schema_name: str
    schema_version: str

    # Auto-computed metadata
    analyzed_at: str           # ISO 8601 UTC timestamp
    analysis_model: str        # LLM model used
    embedding_model: str | None
    session_length: int        # Approximate line count
    conversation_hash: str     # SHA-256 truncated to 16 hex chars

    # Semantic vector
    embedding: list[float] | None

    # Execution metadata
    llm_response: LLMResponse
    validation_errors: list[str]

    def to_dict(self) -> dict:
        """Full dict with fields + nested _meta (for Qdrant/storage)."""
        result = {}
        result.update(self.fields)
        result["_meta"] = {
            "schema_name": self.schema_name,
            "schema_version": self.schema_version,
            "analyzed_at": self.analyzed_at,
            "analysis_model": self.analysis_model,
            "embedding_model": self.embedding_model,
            "session_length": self.session_length,
            "conversation_hash": self.conversation_hash,
            "has_embedding": self.embedding is not None,
            "input_tokens": self.llm_response.input_tokens,
            "output_tokens": self.llm_response.output_tokens,
            "latency_ms": self.llm_response.latency_ms,
            "validation_errors": self.validation_errors,
        }
        return result

    def to_flat_dict(self) -> dict:
        """Flat dict with fields + meta at same level, no embedding (for JSON/CSV export)."""
        result = {}
        result.update(self.fields)
        result["schema_name"] = self.schema_name
        result["schema_version"] = self.schema_version
        result["analyzed_at"] = self.analyzed_at
        result["analysis_model"] = self.analysis_model
        result["session_length"] = self.session_length
        result["conversation_hash"] = self.conversation_hash
        return result


class Analyzer:
    """Orchestrates the full analysis pipeline.

    Pipeline:
        conversation → build_prompt → LLMClient → validate → embed → AnalysisResult
    """

    def __init__(
        self,
        schema_name: str = "universal",
        provider: str = "anthropic",
        model: str | None = None,
        api_key: str | None = None,
        enable_embeddings: bool = True,
        embedding_api_key: str | None = None,
    ) -> None:
        self.schema_name = schema_name
        self.schema_manager = SchemaManager()
        self.schema = self.schema_manager.load_schema(schema_name)
        self.llm_client = LLMClient(provider=provider, model=model, api_key=api_key)

        if enable_embeddings:
            self.embedding_generator: EmbeddingGenerator | None = EmbeddingGenerator(
                api_key=embedding_api_key
            )
        else:
            self.embedding_generator = None

    def analyze(
        self, conversation: str, context: dict | None = None
    ) -> AnalysisResult:
        """Run the full pipeline on a conversation string."""
        # Step 1 — build prompt
        prompt = build_prompt(self.schema, conversation, context)

        # Step 2 — call LLM
        llm_response = self.llm_client.analyze(prompt)

        # Compute auto-fields (used regardless of LLM success)
        analyzed_at = datetime.now(timezone.utc).isoformat()
        session_length = conversation.count("\n") + 1
        conversation_hash = hashlib.sha256(conversation.encode()).hexdigest()[:16]

        # Step 3 — handle LLM failure
        if not llm_response.success or llm_response.parsed_json is None:
            return AnalysisResult(
                fields={},
                schema_name=self.schema_name,
                schema_version=self.schema["metadata"]["version"],
                analyzed_at=analyzed_at,
                analysis_model=self.llm_client.model,
                embedding_model=None,
                session_length=session_length,
                conversation_hash=conversation_hash,
                embedding=None,
                llm_response=llm_response,
                validation_errors=[
                    f"LLM failed: {llm_response.error or 'Could not parse JSON'}"
                ],
            )

        # Step 4 — validate against schema
        _is_valid, errors = self.schema_manager.validate_result(
            self.schema_name, llm_response.parsed_json
        )

        # Step 5 — generate embedding from summary field
        embedding = None
        embedding_model = None
        if self.embedding_generator:
            summary = llm_response.parsed_json.get("summary", "")
            if summary:
                embedding = self.embedding_generator.generate(summary)
                if embedding is not None:
                    embedding_model = "text-embedding-3-small"

        # Step 6 — build and return result
        return AnalysisResult(
            fields=llm_response.parsed_json,
            schema_name=self.schema_name,
            schema_version=self.schema["metadata"]["version"],
            analyzed_at=analyzed_at,
            analysis_model=self.llm_client.model,
            embedding_model=embedding_model,
            session_length=session_length,
            conversation_hash=conversation_hash,
            embedding=embedding,
            llm_response=llm_response,
            validation_errors=errors,
        )


def analyze(
    conversation: str,
    schema: str = "universal",
    provider: str = "anthropic",
    model: str | None = None,
    context: dict | None = None,
    enable_embeddings: bool = True,
) -> AnalysisResult:
    """Convenience function for quick one-shot analysis.

    Usage:
        from analyxa import analyze
        result = analyze("User: hello\\nAgent: hi", schema="support")
    """
    analyzer = Analyzer(
        schema_name=schema,
        provider=provider,
        model=model,
        enable_embeddings=enable_embeddings,
    )
    return analyzer.analyze(conversation, context=context)
