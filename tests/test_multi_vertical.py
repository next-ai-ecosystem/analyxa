"""
Tests for multi-vertical schema system — IF-007
Covers: sales.yaml, coaching.yaml, schema inheritance, validation,
prompt builder integration, and CLI schemas commands.
"""

import pytest
from analyxa.schema import SchemaManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sm():
    return SchemaManager()


# ---------------------------------------------------------------------------
# Test 1: test_sales_schema_loads
# ---------------------------------------------------------------------------

def test_sales_schema_loads(sm):
    schema = sm.load_schema("sales")
    assert len(schema["fields"]) == 17
    assert schema["fields"][11]["name"] == "buying_stage"
    assert schema["fields"][16]["name"] == "next_best_action"
    assert schema["metadata"]["inherits"] == "universal"


# ---------------------------------------------------------------------------
# Test 2: test_coaching_schema_loads
# ---------------------------------------------------------------------------

def test_coaching_schema_loads(sm):
    schema = sm.load_schema("coaching")
    assert len(schema["fields"]) == 19
    assert schema["fields"][11]["name"] == "emotional_valence"
    assert schema["fields"][18]["name"] == "coping_strategies"
    assert schema["metadata"]["inherits"] == "universal"


# ---------------------------------------------------------------------------
# Test 3: test_all_schemas_list
# ---------------------------------------------------------------------------

def test_all_schemas_list(sm):
    schemas = sm.list_schemas()
    assert len(schemas) == 4
    assert sorted(schemas) == ["coaching", "sales", "support", "universal"]


# ---------------------------------------------------------------------------
# Test 4: test_sales_inherits_universal_fields
# ---------------------------------------------------------------------------

def test_sales_inherits_universal_fields(sm):
    universal = sm.load_schema("universal")
    sales = sm.load_schema("sales")
    for i in range(11):
        assert sales["fields"][i]["name"] == universal["fields"][i]["name"]
        assert sales["fields"][i]["type"] == universal["fields"][i]["type"]


# ---------------------------------------------------------------------------
# Test 5: test_coaching_inherits_universal_fields
# ---------------------------------------------------------------------------

def test_coaching_inherits_universal_fields(sm):
    universal = sm.load_schema("universal")
    coaching = sm.load_schema("coaching")
    for i in range(11):
        assert coaching["fields"][i]["name"] == universal["fields"][i]["name"]
        assert coaching["fields"][i]["type"] == universal["fields"][i]["type"]


# ---------------------------------------------------------------------------
# Test 6: test_validate_sales_result
# ---------------------------------------------------------------------------

def test_validate_sales_result(sm):
    result = {
        "language": "en",
        "title": "Sales demo request",
        "summary": "Prospect interested in analytics platform after conference.",
        "sentiment": "positive",
        "sentiment_intensity": "medium",
        "topics": ["analytics", "demo"],
        "session_outcome": "resolved",
        "user_intent": "Product demo request",
        "risk_signals": [],
        "key_entities": ["mike@acmecorp.com"],
        "action_items": ["Send trial setup to Mike"],
        "buying_stage": "consideration",
        "objections": [],
        "budget_signals": ["has_budget"],
        "decision_urgency": "short_term",
        "competitive_mentions": ["Qualtrics"],
        "next_best_action": "Set up trial and follow up in one week",
    }
    valid, errors = sm.validate_result("sales", result)
    assert valid is True
    assert errors == []


# ---------------------------------------------------------------------------
# Test 7: test_validate_coaching_result
# ---------------------------------------------------------------------------

def test_validate_coaching_result(sm):
    result = {
        "language": "en",
        "title": "Progress session — thesis anxiety",
        "summary": "User reports improved sleep and reduced anxiety.",
        "sentiment": "positive",
        "sentiment_intensity": "medium",
        "topics": ["anxiety", "thesis", "sleep"],
        "session_outcome": "resolved",
        "user_intent": "Share progress and set new goals",
        "risk_signals": [],
        "key_entities": [],
        "action_items": ["Present draft to study group"],
        "emotional_valence": "positive",
        "emotional_intensity": "moderate",
        "progress_indicators": ["Slept through the night three times"],
        "behavioral_patterns": ["growth_mindset", "engagement"],
        "growth_markers": ["Recognized catastrophizing pattern"],
        "therapeutic_momentum": "accelerating",
        "adaptation_level": "coping",
        "coping_strategies": ["emotional_regulation", "cognitive_reframing"],
    }
    valid, errors = sm.validate_result("coaching", result)
    assert valid is True
    assert errors == []


# ---------------------------------------------------------------------------
# Test 8: test_validate_sales_missing_buying_stage
# ---------------------------------------------------------------------------

def test_validate_sales_missing_buying_stage(sm):
    result = {
        "language": "en",
        "title": "Sales conversation",
        "summary": "A sales conversation.",
        "sentiment": "neutral",
        "sentiment_intensity": "low",
        "topics": ["sales"],
        "session_outcome": "unresolved",
        "user_intent": "Evaluate product",
        "risk_signals": [],
        "key_entities": [],
        "action_items": [],
        # buying_stage MISSING
        "objections": [],
        "budget_signals": ["budget_unclear"],
        "decision_urgency": "medium_term",
        "competitive_mentions": [],
        "next_best_action": "Follow up next week",
    }
    valid, errors = sm.validate_result("sales", result)
    assert valid is False
    assert any("buying_stage" in e for e in errors)


# ---------------------------------------------------------------------------
# Test 9: test_validate_coaching_invalid_momentum
# ---------------------------------------------------------------------------

def test_validate_coaching_invalid_momentum(sm):
    result = {
        "language": "en",
        "title": "Coaching session",
        "summary": "A coaching session.",
        "sentiment": "neutral",
        "sentiment_intensity": "low",
        "topics": ["coaching"],
        "session_outcome": "unresolved",
        "user_intent": "Talk about feelings",
        "risk_signals": [],
        "key_entities": [],
        "action_items": [],
        "emotional_valence": "neutral",
        "emotional_intensity": "low",
        "progress_indicators": [],
        "behavioral_patterns": ["openness"],
        "growth_markers": [],
        "therapeutic_momentum": "invalid_value",
        "adaptation_level": "coping",
        "coping_strategies": ["mindfulness"],
    }
    valid, errors = sm.validate_result("coaching", result)
    assert valid is False
    assert any("therapeutic_momentum" in e for e in errors)


# ---------------------------------------------------------------------------
# Test 10: test_prompt_builder_sales
# ---------------------------------------------------------------------------

def test_prompt_builder_sales(sm):
    from analyxa.prompt_builder import build_prompt
    schema = sm.load_schema("sales")
    result = build_prompt(schema, "User: I'm interested in your product.")
    full_prompt = result["system"] + result["user"]
    assert "buying_stage" in full_prompt
    assert "next_best_action" in full_prompt
    assert "awareness" in full_prompt


# ---------------------------------------------------------------------------
# Test 11: test_prompt_builder_coaching
# ---------------------------------------------------------------------------

def test_prompt_builder_coaching(sm):
    from analyxa.prompt_builder import build_prompt
    schema = sm.load_schema("coaching")
    result = build_prompt(schema, "User: I've been feeling much better this week.")
    full_prompt = result["system"] + result["user"]
    assert "emotional_valence" in full_prompt
    assert "coping_strategies" in full_prompt
    assert "avoidance" in full_prompt


# ---------------------------------------------------------------------------
# Test 12: test_cli_schemas_shows_four
# ---------------------------------------------------------------------------

def test_cli_schemas_shows_four():
    from click.testing import CliRunner
    from analyxa.cli import main
    runner = CliRunner()
    result = runner.invoke(main, ["schemas", "list"])
    assert result.exit_code == 0
    assert "universal" in result.output
    assert "support" in result.output
    assert "sales" in result.output
    assert "coaching" in result.output
