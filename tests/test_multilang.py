"""Tests for multi-language support — IF-010 verification suite (no real API keys)."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from analyxa.analyzer import Analyzer, AnalysisResult
from analyxa.llm_client import LLMResponse
from analyxa.schema import SchemaManager
from analyxa.prompt_builder import build_prompt
from analyxa.sinks.json_sink import JsonSink


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_llm_response(fields: dict) -> LLMResponse:
    """Create a mock LLMResponse from a fields dict."""
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


SPANISH_FIELDS = {
    "language": "es",
    "title": "Problema de acceso premium",
    "summary": "El cliente reporta falta de acceso premium después del pago.",
    "sentiment": "negative",
    "sentiment_intensity": "medium",
    "topics": ["facturación", "acceso a cuenta"],
    "session_outcome": "resolved",
    "user_intent": "Activar suscripción premium",
    "risk_signals": [],
    "key_entities": ["javier@ejemplo.com"],
    "action_items": ["Verificar activación automática"],
}

FRENCH_FIELDS = {
    "language": "fr",
    "title": "Demande plan entreprise startup",
    "summary": "Le client demande des informations sur le plan entreprise et une réduction startup.",
    "sentiment": "positive",
    "sentiment_intensity": "medium",
    "topics": ["tarification", "plan entreprise", "réduction startup"],
    "session_outcome": "unresolved",
    "user_intent": "Obtenir un prix réduit pour le plan entreprise",
    "risk_signals": [],
    "key_entities": ["199€/mois", "139€/mois"],
    "action_items": ["Envoyer proposition formelle"],
}

ENGLISH_FIELDS = {
    "language": "en",
    "title": "Duplicate Subscription Charge Resolution",
    "summary": "Customer reported being charged twice for their monthly subscription. "
               "Agent identified the duplicate charge and processed an immediate refund.",
    "sentiment": "mixed",
    "sentiment_intensity": "medium",
    "topics": ["billing", "duplicate_charge", "refund"],
    "session_outcome": "resolved",
    "user_intent": "Get refund for duplicate subscription charge",
    "risk_signals": ["frustration", "repeat_contact"],
    "key_entities": ["subscription", "refund"],
    "action_items": ["Process refund for duplicate charge"],
}


# ---------------------------------------------------------------------------
# Test 1: universal schema has language field
# ---------------------------------------------------------------------------

def test_universal_schema_has_language_field():
    sm = SchemaManager()
    schema = sm.load_schema("universal")
    fields = schema["fields"]

    assert fields[0]["name"] == "language", f"First field should be 'language', got '{fields[0]['name']}'"
    assert fields[0]["type"] == "string"
    assert fields[0]["required"] is True


# ---------------------------------------------------------------------------
# Test 2: all schemas inherit language
# ---------------------------------------------------------------------------

def test_all_schemas_inherit_language():
    sm = SchemaManager()
    expected_counts = {
        "universal": 11,
        "support": 17,
        "sales": 17,
        "coaching": 19,
    }

    for name, expected in expected_counts.items():
        schema = sm.load_schema(name)
        field_names = [f["name"] for f in schema["fields"]]

        assert "language" in field_names, f"Schema '{name}' missing 'language' field"
        assert len(schema["fields"]) == expected, (
            f"Schema '{name}': expected {expected} fields, got {len(schema['fields'])}"
        )


# ---------------------------------------------------------------------------
# Test 3: prompt contains multilang instructions
# ---------------------------------------------------------------------------

def test_prompt_contains_multilang_instructions():
    sm = SchemaManager()
    schema = sm.load_schema("universal")
    prompt = build_prompt(schema, "Hola, tengo un problema con mi cuenta")

    sys_prompt = prompt["system"]
    assert "language" in sys_prompt.lower(), "System prompt missing 'language' instructions"
    assert "639" in sys_prompt, "System prompt missing ISO 639 reference"
    assert "LANGUAGE INSTRUCTIONS" in sys_prompt, "System prompt missing LANGUAGE INSTRUCTIONS header"


# ---------------------------------------------------------------------------
# Test 4: prompt contains language field definition
# ---------------------------------------------------------------------------

def test_prompt_contains_language_field_definition():
    sm = SchemaManager()
    schema = sm.load_schema("universal")
    prompt = build_prompt(schema, "Test conversation")

    sys_prompt = prompt["system"]
    # The field definitions list should include language as field #1
    assert "1. language" in sys_prompt, "Field definitions missing 'language' as first field"


# ---------------------------------------------------------------------------
# Test 5: mock Spanish analysis
# ---------------------------------------------------------------------------

def test_mock_spanish_analysis():
    mock_response = _make_llm_response(SPANISH_FIELDS)

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        analyzer = Analyzer(schema_name="universal", enable_embeddings=False)

    analyzer.llm_client.analyze = MagicMock(return_value=mock_response)

    conversation = (
        "Cliente: Hola, compré una suscripción premium hace 2 días y aún no tengo acceso.\n"
        "Agente: ¡Hola! Lamento el inconveniente. Déjame revisar tu cuenta ahora mismo."
    )
    result = analyzer.analyze(conversation)

    assert result.fields["language"] == "es"
    assert result.fields["sentiment"] == "negative"
    assert "facturación" in result.fields["topics"]


# ---------------------------------------------------------------------------
# Test 6: mock French analysis
# ---------------------------------------------------------------------------

def test_mock_french_analysis():
    mock_response = _make_llm_response(FRENCH_FIELDS)

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        analyzer = Analyzer(schema_name="universal", enable_embeddings=False)

    analyzer.llm_client.analyze = MagicMock(return_value=mock_response)

    conversation = (
        "Client: Bonjour, je suis intéressé par votre plan entreprise.\n"
        "Agent: Bonjour! Notre plan entreprise est à 199€/mois."
    )
    result = analyzer.analyze(conversation)

    assert result.fields["language"] == "fr"


# ---------------------------------------------------------------------------
# Test 7: mock English backward compatible
# ---------------------------------------------------------------------------

def test_mock_english_backward_compatible():
    mock_response = _make_llm_response(ENGLISH_FIELDS)

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        analyzer = Analyzer(schema_name="universal", enable_embeddings=False)

    analyzer.llm_client.analyze = MagicMock(return_value=mock_response)

    conversation = (
        "User: Hi, I was charged twice for my subscription this month.\n"
        "Agent: I'm sorry to hear that. Let me look into your account."
    )
    result = analyzer.analyze(conversation)

    assert result.fields["language"] == "en"
    # All existing fields still present
    for key in ["title", "summary", "sentiment", "sentiment_intensity", "topics",
                "session_outcome", "user_intent", "risk_signals", "key_entities", "action_items"]:
        assert key in result.fields, f"Missing expected field: {key}"


# ---------------------------------------------------------------------------
# Test 8: field keys always English
# ---------------------------------------------------------------------------

def test_field_keys_always_english():
    mock_response = _make_llm_response(SPANISH_FIELDS)

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        analyzer = Analyzer(schema_name="universal", enable_embeddings=False)

    analyzer.llm_client.analyze = MagicMock(return_value=mock_response)

    result = analyzer.analyze("Cliente: Hola\nAgente: Hola")
    keys = set(result.fields.keys())

    # Keys must be in English
    assert "sentiment" in keys
    assert "summary" in keys
    assert "topics" in keys
    assert "action_items" in keys

    # Spanish keys must NOT exist
    assert "sentimiento" not in keys
    assert "resumen" not in keys
    assert "temas" not in keys
    assert "acciones" not in keys


# ---------------------------------------------------------------------------
# Test 9: language field in JSON sink output
# ---------------------------------------------------------------------------

def test_language_field_in_json_sink_output():
    result_dict = {"language": "es", "title": "Test", "sentiment": "positive"}

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "result.json"
        sink = JsonSink(out_path)
        sink.write(result_dict)

        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert "language" in data
        assert data["language"] == "es"


# ---------------------------------------------------------------------------
# Test 10: prompt multilang preserved with context
# ---------------------------------------------------------------------------

def test_prompt_multilang_preserved_with_context():
    sm = SchemaManager()
    schema = sm.load_schema("universal")
    prompt = build_prompt(schema, "Test conversation", context={"company": "Acme Corp"})

    sys_prompt = prompt["system"]
    assert "LANGUAGE INSTRUCTIONS" in sys_prompt, "Multi-lang instructions missing when context provided"
    assert "Acme Corp" in sys_prompt, "Context not present in prompt"
