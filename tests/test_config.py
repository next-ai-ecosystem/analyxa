"""Tests for AnalyxaConfig — IF-005 verification suite."""

import os
from unittest.mock import patch

import pytest

from analyxa.config import AnalyxaConfig, get_config, reset_config


# ---------------------------------------------------------------------------
# Helper: clean ANALYXA env vars
# ---------------------------------------------------------------------------

ANALYXA_VARS = [
    "ANALYXA_PROVIDER", "ANALYXA_MODEL", "ANALYXA_SCHEMA",
    "ANALYXA_EMBEDDING_MODEL", "ANALYXA_EMBEDDINGS", "ANALYXA_SCHEMAS_DIR",
    "ANALYXA_LOG_LEVEL", "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
    "REDIS_URL", "QDRANT_URL", "QDRANT_COLLECTION",
]


@pytest.fixture(autouse=True)
def clean_env_and_singleton(monkeypatch):
    """Remove all ANALYXA_* and API key env vars, patch load_dotenv to no-op, reset singleton."""
    for var in ANALYXA_VARS:
        monkeypatch.delenv(var, raising=False)
    with patch("analyxa.config.load_dotenv"):
        yield
    reset_config()


# ---------------------------------------------------------------------------
# Test 1: defaults
# ---------------------------------------------------------------------------

def test_config_defaults():
    config = AnalyxaConfig()
    assert config.default_provider == "anthropic"
    assert config.default_schema == "universal"
    assert config.enable_embeddings is True
    assert config.redis_url == "redis://localhost:6379"
    assert config.qdrant_collection == "analyxa_analyses"


# ---------------------------------------------------------------------------
# Test 2: env override
# ---------------------------------------------------------------------------

def test_config_from_env(monkeypatch):
    monkeypatch.setenv("ANALYXA_PROVIDER", "openai")
    monkeypatch.setenv("ANALYXA_SCHEMA", "support")
    config = AnalyxaConfig()
    assert config.default_provider == "openai"
    assert config.default_schema == "support"


# ---------------------------------------------------------------------------
# Test 3: bool parsing for enable_embeddings
# ---------------------------------------------------------------------------

def test_config_embeddings_bool_parsing(monkeypatch):
    for value in ("false", "False", "FALSE"):
        monkeypatch.setenv("ANALYXA_EMBEDDINGS", value)
        assert AnalyxaConfig().enable_embeddings is False

    monkeypatch.setenv("ANALYXA_EMBEDDINGS", "0")
    assert AnalyxaConfig().enable_embeddings is False

    for value in ("true", "1", "yes"):
        monkeypatch.setenv("ANALYXA_EMBEDDINGS", value)
        assert AnalyxaConfig().enable_embeddings is True


# ---------------------------------------------------------------------------
# Test 4: to_dict masks API keys
# ---------------------------------------------------------------------------

def test_config_to_dict_masks_keys(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-secret-key-12345678")
    config = AnalyxaConfig()
    d = config.to_dict()
    masked = d["anthropic_api_key"]
    assert masked is not None
    assert "secret" not in masked
    assert masked.endswith("5678")
    assert masked.startswith("sk-...")


# ---------------------------------------------------------------------------
# Test 5: singleton
# ---------------------------------------------------------------------------

def test_config_singleton():
    c1 = get_config()
    c2 = get_config()
    assert c1 is c2

    reset_config()
    c3 = get_config()
    assert c3 is not c1


# ---------------------------------------------------------------------------
# Test 6: API keys return None when missing
# ---------------------------------------------------------------------------

def test_config_api_keys_none_when_missing():
    config = AnalyxaConfig()
    assert config.anthropic_api_key is None
    assert config.openai_api_key is None
