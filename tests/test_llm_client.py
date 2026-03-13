"""Tests for LLM Client — IF-003 verification suite (no real API keys required)."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

from analyxa.llm_client import LLMClient, LLMResponse


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_prompt():
    return {
        "system": "You are an analysis engine. Extract fields as JSON.",
        "user": "Analyze this conversation:\nUser: hello\nAgent: hi there",
    }


@pytest.fixture
def sample_json_response():
    return {
        "title": "Simple Greeting Exchange",
        "summary": "User greeted the agent and received a friendly response.",
        "sentiment": "neutral",
        "sentiment_intensity": "low",
        "topics": ["greeting"],
        "session_outcome": "resolved",
        "user_intent": "Simple greeting",
        "risk_signals": [],
        "key_entities": [],
        "action_items": [],
    }


def _make_client(provider="anthropic", key="test-key"):
    """Helper that instantiates LLMClient with a fake API key without hitting the network."""
    env_var = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
    with patch.dict(os.environ, {env_var: key}):
        return LLMClient(provider=provider)


# ---------------------------------------------------------------------------
# Test 1: LLMResponse dataclass
# ---------------------------------------------------------------------------

def test_llm_response_dataclass():
    resp = LLMResponse(
        raw_text='{"title": "Test"}',
        parsed_json={"title": "Test"},
        model="claude-sonnet-4-20250514",
        provider="anthropic",
        input_tokens=100,
        output_tokens=50,
        latency_ms=123.4,
        success=True,
    )
    assert resp.raw_text == '{"title": "Test"}'
    assert resp.parsed_json == {"title": "Test"}
    assert resp.model == "claude-sonnet-4-20250514"
    assert resp.provider == "anthropic"
    assert resp.input_tokens == 100
    assert resp.output_tokens == 50
    assert resp.latency_ms == 123.4
    assert resp.success is True
    assert resp.error is None  # default


# ---------------------------------------------------------------------------
# Test 2: _parse_json — clean JSON
# ---------------------------------------------------------------------------

def test_parse_json_clean():
    client = _make_client()
    result = client._parse_json('{"title": "Test", "sentiment": "positive"}')
    assert result == {"title": "Test", "sentiment": "positive"}


# ---------------------------------------------------------------------------
# Test 3: _parse_json — code fences
# ---------------------------------------------------------------------------

def test_parse_json_with_code_fences():
    client = _make_client()
    text = '```json\n{"title": "Test"}\n```'
    result = client._parse_json(text)
    assert result == {"title": "Test"}


# ---------------------------------------------------------------------------
# Test 4: _parse_json — surrounding text
# ---------------------------------------------------------------------------

def test_parse_json_with_surrounding_text():
    client = _make_client()
    text = 'Here is the analysis:\n{"title": "Test", "sentiment": "positive"}\nI hope this helps!'
    result = client._parse_json(text)
    assert result == {"title": "Test", "sentiment": "positive"}


# ---------------------------------------------------------------------------
# Test 5: _parse_json — invalid → None
# ---------------------------------------------------------------------------

def test_parse_json_invalid_returns_none():
    client = _make_client()
    result = client._parse_json("This is not JSON at all")
    assert result is None


# ---------------------------------------------------------------------------
# Test 6: _parse_json — empty string → None
# ---------------------------------------------------------------------------

def test_parse_json_empty_string():
    client = _make_client()
    result = client._parse_json("")
    assert result is None


# ---------------------------------------------------------------------------
# Test 7: __init__ — anthropic defaults
# ---------------------------------------------------------------------------

def test_client_init_anthropic_default():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        client = LLMClient(provider="anthropic")
    assert client.model == "claude-sonnet-4-20250514"
    assert client.provider == "anthropic"


# ---------------------------------------------------------------------------
# Test 8: __init__ — openai defaults
# ---------------------------------------------------------------------------

def test_client_init_openai():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = LLMClient(provider="openai")
    assert client.model == "gpt-4o"
    assert client.provider == "openai"


# ---------------------------------------------------------------------------
# Test 9: __init__ — invalid provider
# ---------------------------------------------------------------------------

def test_client_init_invalid_provider():
    with pytest.raises(ValueError):
        LLMClient(provider="gemini")


# ---------------------------------------------------------------------------
# Test 10: __init__ — no API key
# ---------------------------------------------------------------------------

def test_client_init_no_api_key():
    env_clean = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    with patch.dict(os.environ, env_clean, clear=True):
        with pytest.raises(ValueError) as exc_info:
            LLMClient(provider="anthropic")
    assert "ANTHROPIC_API_KEY" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Test 11: analyze — Anthropic success
# ---------------------------------------------------------------------------

def test_analyze_anthropic_success(sample_prompt, sample_json_response):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(sample_json_response))]
    mock_response.usage.input_tokens = 500
    mock_response.usage.output_tokens = 200

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    with patch("analyxa.llm_client.anthropic") as mock_anthropic_module:
        mock_anthropic_module.Anthropic.return_value = mock_client
        client = LLMClient(provider="anthropic", api_key="test")

    client._client = mock_client
    result = client.analyze(sample_prompt)

    assert result.success is True
    assert result.parsed_json == sample_json_response
    assert result.input_tokens == 500
    assert result.output_tokens == 200
    assert result.provider == "anthropic"
    assert result.latency_ms > 0


# ---------------------------------------------------------------------------
# Test 12: analyze — OpenAI success
# ---------------------------------------------------------------------------

def test_analyze_openai_success(sample_prompt, sample_json_response):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(sample_json_response)
    mock_response.usage.prompt_tokens = 500
    mock_response.usage.completion_tokens = 200

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("analyxa.llm_client.openai") as mock_openai_module:
        mock_openai_module.OpenAI.return_value = mock_client
        client = LLMClient(provider="openai", api_key="test")

    client._client = mock_client
    result = client.analyze(sample_prompt)

    assert result.success is True
    assert result.parsed_json == sample_json_response
    assert result.input_tokens == 500
    assert result.output_tokens == 200
    assert result.provider == "openai"
    assert result.latency_ms > 0


# ---------------------------------------------------------------------------
# Test 13: analyze — API error → failed response (no exception raised)
# ---------------------------------------------------------------------------

def test_analyze_api_error_returns_failed_response(sample_prompt):
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("Connection refused")

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test"}):
        client = LLMClient(provider="anthropic")
    client._client = mock_client

    result = client.analyze(sample_prompt)

    assert result.success is False
    assert result.parsed_json is None
    assert result.error is not None
    assert "Connection refused" in result.error


# ---------------------------------------------------------------------------
# Test 14: analyze — unparseable response
# ---------------------------------------------------------------------------

def test_analyze_unparseable_response(sample_prompt):
    raw = "I cannot analyze this conversation."

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=raw)]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 10

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test"}):
        client = LLMClient(provider="anthropic")
    client._client = mock_client

    result = client.analyze(sample_prompt)

    assert result.success is False
    assert result.parsed_json is None
    assert result.raw_text == raw
