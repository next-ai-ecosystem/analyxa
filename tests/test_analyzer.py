"""Tests for Analyzer pipeline — IF-004 verification suite (no real API keys)."""

import json
import os
import tempfile
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from analyxa.analyzer import Analyzer, AnalysisResult, analyze
from analyxa.llm_client import LLMResponse
from analyxa.sources.file_source import FileSource
from analyxa.sinks.json_sink import JsonSink
from analyxa.sinks.stdout_sink import StdoutSink
from analyxa.embeddings import EmbeddingGenerator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_conversation():
    return (
        "User: Hi, I was charged twice for my subscription this month.\n"
        "Agent: I'm sorry to hear that. Let me look into your account right away.\n"
        "User: It's really frustrating, this happened before too.\n"
        "Agent: I can see the duplicate charge. I'll process a refund immediately. "
        "You should see it in 3-5 business days.\n"
        "User: Okay, thank you. But please make sure it doesn't happen again.\n"
        "Agent: I've flagged your account to prevent future duplicates. Is there anything else?\n"
        "User: No, that's all. Thanks."
    )


@pytest.fixture
def mock_llm_response():
    fields = {
        "title": "Duplicate Subscription Charge Resolution",
        "summary": "Customer reported being charged twice for their monthly subscription. "
                   "Agent identified the duplicate charge and processed an immediate refund "
                   "with 3-5 business day timeline. Account was flagged to prevent recurrence.",
        "sentiment": "mixed",
        "sentiment_intensity": "medium",
        "topics": ["billing", "duplicate_charge", "refund"],
        "session_outcome": "resolved",
        "user_intent": "Get refund for duplicate subscription charge and prevent future occurrences",
        "risk_signals": ["frustration", "repeat_contact"],
        "key_entities": ["subscription", "refund"],
        "action_items": [
            "Process refund for duplicate charge",
            "Flag account to prevent future duplicates",
        ],
    }
    return LLMResponse(
        raw_text=json.dumps(fields),
        parsed_json=fields,
        model="claude-sonnet-4-20250514",
        provider="anthropic",
        input_tokens=800,
        output_tokens=250,
        latency_ms=1500.0,
        success=True,
        error=None,
    )


@pytest.fixture
def mock_embedding():
    return [0.01] * 1536


def _make_analyzer(schema_name="universal", enable_embeddings=True):
    """Create Analyzer with a fake API key (no real calls)."""
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        return Analyzer(schema_name=schema_name, enable_embeddings=enable_embeddings)


# ---------------------------------------------------------------------------
# Test 1: AnalysisResult.to_dict
# ---------------------------------------------------------------------------

def test_analysis_result_to_dict(mock_llm_response, mock_embedding):
    result = AnalysisResult(
        fields=mock_llm_response.parsed_json,
        schema_name="universal",
        schema_version="1.0.0",
        analyzed_at="2026-03-14T12:00:00+00:00",
        analysis_model="claude-sonnet-4-20250514",
        embedding_model="text-embedding-3-small",
        session_length=7,
        conversation_hash="abcd1234abcd1234",
        embedding=mock_embedding,
        llm_response=mock_llm_response,
        validation_errors=[],
    )
    d = result.to_dict()

    assert "title" in d
    assert "sentiment" in d
    assert "_meta" in d
    assert d["_meta"]["schema_name"] == "universal"
    assert d["_meta"]["analyzed_at"] == "2026-03-14T12:00:00+00:00"
    assert isinstance(d["_meta"]["has_embedding"], bool)
    assert d["_meta"]["has_embedding"] is True


# ---------------------------------------------------------------------------
# Test 2: AnalysisResult.to_flat_dict
# ---------------------------------------------------------------------------

def test_analysis_result_to_flat_dict(mock_llm_response):
    result = AnalysisResult(
        fields=mock_llm_response.parsed_json,
        schema_name="universal",
        schema_version="1.0.0",
        analyzed_at="2026-03-14T12:00:00+00:00",
        analysis_model="claude-sonnet-4-20250514",
        embedding_model=None,
        session_length=7,
        conversation_hash="abcd1234abcd1234",
        embedding=None,
        llm_response=mock_llm_response,
        validation_errors=[],
    )
    d = result.to_flat_dict()

    assert "_meta" not in d
    assert "schema_name" in d
    assert "analyzed_at" in d
    assert "embedding" not in d
    assert d["schema_name"] == "universal"


# ---------------------------------------------------------------------------
# Test 3: full pipeline with mocks
# ---------------------------------------------------------------------------

def test_analyzer_full_pipeline(sample_conversation, mock_llm_response, mock_embedding):
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        analyzer = Analyzer(schema_name="universal", enable_embeddings=True)

    analyzer.llm_client.analyze = MagicMock(return_value=mock_llm_response)
    analyzer.embedding_generator.generate = MagicMock(return_value=mock_embedding)

    result = analyzer.analyze(sample_conversation)

    assert len(result.fields) == 10
    assert result.schema_name == "universal"
    # ISO 8601 check
    datetime.fromisoformat(result.analyzed_at)
    assert len(result.conversation_hash) == 16
    assert result.session_length > 0
    assert result.embedding == mock_embedding
    assert len(result.embedding) == 1536
    assert result.validation_errors == []


# ---------------------------------------------------------------------------
# Test 4: pipeline without embeddings
# ---------------------------------------------------------------------------

def test_analyzer_without_embeddings(sample_conversation, mock_llm_response):
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        analyzer = Analyzer(schema_name="universal", enable_embeddings=False)

    analyzer.llm_client.analyze = MagicMock(return_value=mock_llm_response)

    result = analyzer.analyze(sample_conversation)

    assert result.embedding is None
    assert result.embedding_model is None
    assert result.fields  # analysis still worked


# ---------------------------------------------------------------------------
# Test 5: LLM failure propagation
# ---------------------------------------------------------------------------

def test_analyzer_llm_failure(sample_conversation):
    failed_response = LLMResponse(
        raw_text="",
        parsed_json=None,
        model="claude-sonnet-4-20250514",
        provider="anthropic",
        input_tokens=0,
        output_tokens=0,
        latency_ms=100.0,
        success=False,
        error="Connection refused",
    )

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        analyzer = Analyzer(schema_name="universal", enable_embeddings=False)

    analyzer.llm_client.analyze = MagicMock(return_value=failed_response)

    result = analyzer.analyze(sample_conversation)

    assert result.fields == {}
    assert len(result.validation_errors) >= 1
    assert "LLM failed" in result.validation_errors[0]


# ---------------------------------------------------------------------------
# Test 6: conversation_hash determinism
# ---------------------------------------------------------------------------

def test_conversation_hash_deterministic(sample_conversation, mock_llm_response):
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        analyzer = Analyzer(schema_name="universal", enable_embeddings=False)

    analyzer.llm_client.analyze = MagicMock(return_value=mock_llm_response)

    result1 = analyzer.analyze(sample_conversation)
    result2 = analyzer.analyze(sample_conversation)
    assert result1.conversation_hash == result2.conversation_hash

    other_response = LLMResponse(
        raw_text=mock_llm_response.raw_text,
        parsed_json=mock_llm_response.parsed_json,
        model=mock_llm_response.model,
        provider=mock_llm_response.provider,
        input_tokens=100,
        output_tokens=50,
        latency_ms=200.0,
        success=True,
    )
    analyzer.llm_client.analyze = MagicMock(return_value=other_response)
    result3 = analyzer.analyze("User: different conversation\nAgent: different reply")
    assert result3.conversation_hash != result1.conversation_hash


# ---------------------------------------------------------------------------
# Test 7: convenience function
# ---------------------------------------------------------------------------

def test_analyze_convenience_function(sample_conversation, mock_llm_response):
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        with patch("analyxa.analyzer.LLMClient") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.model = "claude-sonnet-4-20250514"
            mock_instance.analyze.return_value = mock_llm_response

            result = analyze(sample_conversation, schema="universal", enable_embeddings=False)

    assert isinstance(result, AnalysisResult)
    assert result.fields


# ---------------------------------------------------------------------------
# Test 8: FileSource.read
# ---------------------------------------------------------------------------

def test_file_source_read(sample_conversation):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(sample_conversation)
        tmp_path = f.name

    try:
        source = FileSource(tmp_path)
        content = source.read()
        assert "charged twice" in content
        assert "subscription" in content
    finally:
        Path(tmp_path).unlink()


# ---------------------------------------------------------------------------
# Test 9: FileSource.read_messages
# ---------------------------------------------------------------------------

def test_file_source_read_messages():
    text = "User: Hello\nAgent: Hi there\nUser: I need help with billing"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(text)
        tmp_path = f.name

    try:
        source = FileSource(tmp_path)
        messages = source.read_messages()
        assert len(messages) == 3
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
    finally:
        Path(tmp_path).unlink()


# ---------------------------------------------------------------------------
# Test 10: FileSource — file not found
# ---------------------------------------------------------------------------

def test_file_source_not_found():
    with pytest.raises(FileNotFoundError):
        FileSource("/nonexistent/path/file.txt")


# ---------------------------------------------------------------------------
# Test 11: JsonSink.write
# ---------------------------------------------------------------------------

def test_json_sink_write():
    result = {"title": "Test", "sentiment": "positive", "score": 42}
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "result.json"
        sink = JsonSink(out_path)
        returned = sink.write(result)

        assert returned == str(out_path)
        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert data["title"] == "Test"
        assert data["sentiment"] == "positive"


# ---------------------------------------------------------------------------
# Test 12: StdoutSink.write
# ---------------------------------------------------------------------------

def test_stdout_sink_write(capsys):
    result = {"title": "Hello", "status": "ok"}
    StdoutSink().write(result)
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed["title"] == "Hello"
    assert parsed["status"] == "ok"


# ---------------------------------------------------------------------------
# Test 13: EmbeddingGenerator — no API key (silent degradation)
# ---------------------------------------------------------------------------

def test_embedding_generator_no_api_key():
    env_clean = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    with patch.dict(os.environ, env_clean, clear=True):
        gen = EmbeddingGenerator()

    assert gen._client is None
    result = gen.generate("some text")
    assert result is None  # silent degradation, no exception


# ---------------------------------------------------------------------------
# Test 14: analyzer with support schema
# ---------------------------------------------------------------------------

def test_analyzer_support_schema(sample_conversation, mock_llm_response):
    support_fields = dict(mock_llm_response.parsed_json)
    support_fields.update({
        "satisfaction_prediction": "medium",
        "issue_category": "billing",
        "escalation_needed": "no",
        "resolution_quality": "good",
        "first_contact_resolution": "yes",
        "customer_effort_score": "low",
    })
    support_response = LLMResponse(
        raw_text=json.dumps(support_fields),
        parsed_json=support_fields,
        model="claude-sonnet-4-20250514",
        provider="anthropic",
        input_tokens=900,
        output_tokens=300,
        latency_ms=1800.0,
        success=True,
    )

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        analyzer = Analyzer(schema_name="support", enable_embeddings=False)

    analyzer.llm_client.analyze = MagicMock(return_value=support_response)

    result = analyzer.analyze(sample_conversation)

    assert result.schema_name == "support"
    assert "satisfaction_prediction" in result.fields
    assert "customer_effort_score" in result.fields
