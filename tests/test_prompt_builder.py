"""Tests for prompt_builder — IF-002 verification suite."""

import pytest

from analyxa.schema import SchemaManager
from analyxa.prompt_builder import build_prompt


@pytest.fixture
def schema_manager():
    return SchemaManager()


@pytest.fixture
def universal_schema(schema_manager):
    return schema_manager.load_schema("universal")


@pytest.fixture
def support_schema(schema_manager):
    return schema_manager.load_schema("support")


@pytest.fixture
def sample_conversation():
    return (
        "User: Hi, I've been charged twice for my subscription this month.\n"
        "Agent: I'm sorry to hear that. Let me look into your account right away.\n"
        "User: It's really frustrating, this is the second time this happens.\n"
        "Agent: I can see the duplicate charge. I'll process a refund immediately. "
        "You should see it in 3-5 business days.\n"
        "User: Okay, thank you. But please make sure it doesn't happen again.\n"
        "Agent: I've flagged your account to prevent future duplicates. "
        "Is there anything else I can help with?\n"
        "User: No, that's all. Thanks."
    )


def test_build_prompt_returns_correct_structure(universal_schema, sample_conversation):
    result = build_prompt(universal_schema, sample_conversation)

    assert isinstance(result, dict)
    assert "system" in result
    assert "user" in result
    assert isinstance(result["system"], str)
    assert isinstance(result["user"], str)
    assert len(result["system"]) > 0
    assert len(result["user"]) > 0


def test_system_prompt_contains_field_definitions(universal_schema, sample_conversation):
    result = build_prompt(universal_schema, sample_conversation)
    system = result["system"]

    expected_fields = [
        "title", "summary", "sentiment", "sentiment_intensity", "topics",
        "session_outcome", "user_intent", "risk_signals", "key_entities", "action_items",
    ]
    for field_name in expected_fields:
        assert field_name in system, f"Field '{field_name}' missing from system prompt"

    assert "required" in system
    assert "optional" in system


def test_system_prompt_contains_json_template(universal_schema, sample_conversation):
    result = build_prompt(universal_schema, sample_conversation)
    system = result["system"]

    assert '"title":' in system
    assert '"sentiment":' in system
    assert "positive|negative|mixed|neutral" in system


def test_user_prompt_contains_conversation(universal_schema, sample_conversation):
    result = build_prompt(universal_schema, sample_conversation)
    user = result["user"]

    assert "charged twice" in user
    assert "CONVERSATION:" in user


def test_support_schema_has_more_fields_in_prompt(universal_schema, support_schema, sample_conversation):
    prompt_universal = build_prompt(universal_schema, sample_conversation)
    prompt_support = build_prompt(support_schema, sample_conversation)

    support_system = prompt_support["system"]
    assert "satisfaction_prediction" in support_system
    assert "escalation_needed" in support_system
    assert "customer_effort_score" in support_system
    assert len(prompt_support["system"]) > len(prompt_universal["system"])


def test_context_injection(universal_schema, sample_conversation):
    context = {"agent_name": "SupportBot", "company": "Acme Corp", "language": "es"}
    result = build_prompt(universal_schema, sample_conversation, context=context)

    assert "SupportBot" in result["system"]
    assert "Acme Corp" in result["system"]


def test_context_none_values_excluded(universal_schema, sample_conversation):
    context = {"agent_name": "Bot", "company": None}
    result = build_prompt(universal_schema, sample_conversation, context=context)

    assert "Bot" in result["system"]
    assert "None" not in result["system"]


def test_language_in_user_prompt(universal_schema, sample_conversation):
    context = {"language": "es"}
    result = build_prompt(universal_schema, sample_conversation, context=context)

    assert "es" in result["user"]


def test_no_context_no_additional_section(universal_schema, sample_conversation):
    result = build_prompt(universal_schema, sample_conversation)

    assert "Additional context" not in result["system"]


def test_allowed_values_in_field_definitions(universal_schema, sample_conversation):
    result = build_prompt(universal_schema, sample_conversation)
    system = result["system"]

    assert "positive, negative, mixed, neutral" in system
    assert "resolved, unresolved, escalated, abandoned" in system


def test_prompt_guidelines_included(universal_schema, sample_conversation):
    result = build_prompt(universal_schema, sample_conversation)

    assert "Focus on the USER" in result["system"]


def test_empty_conversation_still_works(universal_schema):
    result = build_prompt(universal_schema, "")

    assert isinstance(result, dict)
    assert "system" in result
    assert "user" in result
    assert "CONVERSATION:" in result["user"]
