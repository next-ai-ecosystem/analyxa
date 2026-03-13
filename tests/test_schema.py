"""Tests for SchemaManager — IF-001 verification suite."""

import pytest

from analyxa.schema import SchemaManager


@pytest.fixture
def schema_manager():
    return SchemaManager()


def test_load_universal_schema(schema_manager):
    schema = schema_manager.load_schema("universal")

    assert "metadata" in schema
    assert "fields" in schema
    assert "auto_fields" in schema
    assert "prompt" in schema

    assert schema["metadata"]["name"] == "universal"
    assert schema["metadata"]["inherits"] is None

    fields = schema["fields"]
    assert len(fields) == 10
    assert fields[0]["name"] == "title"
    assert fields[-1]["name"] == "action_items"


def test_load_support_schema_with_inheritance(schema_manager):
    schema = schema_manager.load_schema("support")

    fields = schema["fields"]
    assert len(fields) == 16

    # First 10 fields from universal, in order
    universal_names = [
        "title", "summary", "sentiment", "sentiment_intensity", "topics",
        "session_outcome", "user_intent", "risk_signals", "key_entities", "action_items",
    ]
    for i, name in enumerate(universal_names):
        assert fields[i]["name"] == name, f"Field {i} should be '{name}', got '{fields[i]['name']}'"

    assert fields[10]["name"] == "satisfaction_prediction"
    assert fields[15]["name"] == "customer_effort_score"

    # Inherited auto_fields and prompt from universal
    assert "auto_fields" in schema
    assert len(schema["auto_fields"]) == 7
    assert "prompt" in schema
    assert "system_context" in schema["prompt"]


def test_schema_caching(schema_manager):
    schema_a = schema_manager.load_schema("universal")
    schema_b = schema_manager.load_schema("universal")
    assert schema_a is schema_b


def test_list_schemas(schema_manager):
    schemas = schema_manager.list_schemas()
    assert "universal" in schemas
    assert "support" in schemas
    assert schemas == sorted(schemas)


def test_get_field_names(schema_manager):
    universal_names = schema_manager.get_field_names("universal")
    assert len(universal_names) == 10
    assert universal_names[0] == "title"
    assert universal_names[-1] == "action_items"

    support_names = schema_manager.get_field_names("support")
    assert len(support_names) == 16
    assert support_names[10] == "satisfaction_prediction"


def test_validate_result_valid(schema_manager):
    result = {
        "title": "User requests refund for duplicate charge",
        "summary": "The user contacted support about a duplicate charge on their account. "
                   "The agent reviewed the billing history and confirmed the error. "
                   "A refund was initiated and the user was satisfied with the resolution.",
        "sentiment": "negative",
        "sentiment_intensity": "medium",
        "topics": ["billing", "refund"],
        "session_outcome": "resolved",
        "user_intent": "The user wanted a refund for a duplicate charge on their account.",
    }
    is_valid, errors = schema_manager.validate_result("universal", result)
    assert is_valid is True
    assert errors == []


def test_validate_result_missing_required(schema_manager):
    result = {
        "title": "User requests refund",
        "summary": "A refund was processed successfully.",
        "sentiment_intensity": "low",
        "topics": ["billing"],
        "session_outcome": "resolved",
        "user_intent": "Get a refund.",
        # "sentiment" intentionally missing
    }
    is_valid, errors = schema_manager.validate_result("universal", result)
    assert is_valid is False
    assert any("sentiment" in e for e in errors)


def test_validate_result_invalid_keyword(schema_manager):
    result = {
        "title": "Test session",
        "summary": "Test summary covering the conversation.",
        "sentiment": "invalid_value",
        "sentiment_intensity": "low",
        "topics": ["test"],
        "session_outcome": "resolved",
        "user_intent": "Test intent.",
    }
    is_valid, errors = schema_manager.validate_result("universal", result)
    assert is_valid is False
    assert any("sentiment" in e for e in errors)


def test_schema_not_found(schema_manager):
    with pytest.raises(FileNotFoundError):
        schema_manager.load_schema("nonexistent")


def test_field_types_correct(schema_manager):
    schema = schema_manager.load_schema("universal")
    fields = schema["fields"]

    keyword_fields = [f for f in fields if f["type"] == "keyword"]
    string_fields = [f for f in fields if f["type"] == "string"]

    for f in keyword_fields:
        assert f["allowed_values"] is not None, (
            f"Keyword field '{f['name']}' must have allowed_values"
        )

    for f in string_fields:
        assert f["allowed_values"] is None, (
            f"String field '{f['name']}' should not have allowed_values"
        )

    for f in fields:
        assert "name" in f
        assert "type" in f
        assert "required" in f
        assert "description" in f
        assert "prompt_hint" in f
