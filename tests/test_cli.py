"""Tests for CLI commands — IF-005 verification suite."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from analyxa.cli import main
from analyxa.analyzer import AnalysisResult
from analyxa.llm_client import LLMResponse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_result():
    fields = {
        "title": "Test Analysis",
        "summary": "A test conversation.",
        "sentiment": "positive",
        "sentiment_intensity": "low",
        "topics": ["test"],
        "session_outcome": "resolved",
        "user_intent": "Testing",
        "risk_signals": [],
        "key_entities": [],
        "action_items": [],
    }
    llm_resp = LLMResponse(
        raw_text=json.dumps(fields),
        parsed_json=fields,
        model="claude-sonnet-4-20250514",
        provider="anthropic",
        input_tokens=100,
        output_tokens=50,
        latency_ms=500.0,
        success=True,
    )
    return AnalysisResult(
        fields=fields,
        schema_name="universal",
        schema_version="1.0.0",
        analyzed_at="2026-03-14T12:00:00+00:00",
        analysis_model="claude-sonnet-4-20250514",
        embedding_model=None,
        session_length=3,
        conversation_hash="abcd1234abcd1234",
        embedding=None,
        llm_response=llm_resp,
        validation_errors=[],
    )


# ---------------------------------------------------------------------------
# Test 1: schemas list
# ---------------------------------------------------------------------------

def test_cli_schemas_list():
    runner = CliRunner()
    result = runner.invoke(main, ["schemas", "list"])
    assert result.exit_code == 0
    assert "universal" in result.output
    assert "support" in result.output
    assert "Fields: 11" in result.output
    assert "Fields: 17" in result.output


# ---------------------------------------------------------------------------
# Test 2: schemas show universal
# ---------------------------------------------------------------------------

def test_cli_schemas_show_universal():
    runner = CliRunner()
    result = runner.invoke(main, ["schemas", "show", "universal"])
    assert result.exit_code == 0
    assert "title" in result.output
    assert "sentiment" in result.output
    assert "Fields (11)" in result.output


# ---------------------------------------------------------------------------
# Test 3: schemas show support
# ---------------------------------------------------------------------------

def test_cli_schemas_show_support():
    runner = CliRunner()
    result = runner.invoke(main, ["schemas", "show", "support"])
    assert result.exit_code == 0
    assert "satisfaction_prediction" in result.output
    assert "Fields (17)" in result.output
    assert "Inherits: universal" in result.output


# ---------------------------------------------------------------------------
# Test 4: schemas show not found
# ---------------------------------------------------------------------------

def test_cli_schemas_show_not_found():
    runner = CliRunner()
    result = runner.invoke(main, ["schemas", "show", "nonexistent"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "not found" in (result.stderr or "").lower()


# ---------------------------------------------------------------------------
# Test 5: version command
# ---------------------------------------------------------------------------

def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["version"])
    assert result.exit_code == 0
    assert "Analyxa v0.2.0" in result.output
    assert "Provider:" in result.output
    assert "Schema:" in result.output


# ---------------------------------------------------------------------------
# Test 6: analyze with mock
# ---------------------------------------------------------------------------

def test_cli_analyze_with_mock():
    mock_result = _make_mock_result()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("User: Hello\nAgent: Hi there")
        tmp_path = f.name

    try:
        with patch("analyxa.analyzer.Analyzer.analyze", return_value=mock_result):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                runner = CliRunner()
                result = runner.invoke(
                    main,
                    ["analyze", tmp_path, "--schema", "universal", "--no-embeddings"],
                )
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert "title" in parsed
    finally:
        Path(tmp_path).unlink()


# ---------------------------------------------------------------------------
# Test 7: analyze output to file
# ---------------------------------------------------------------------------

def test_cli_analyze_output_to_file():
    mock_result = _make_mock_result()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("User: Hello\nAgent: Hi there")
        tmp_input = f.name

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = str(Path(tmpdir) / "result.json")

        try:
            with patch("analyxa.analyzer.Analyzer.analyze", return_value=mock_result):
                with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                    runner = CliRunner()
                    result = runner.invoke(
                        main,
                        ["analyze", tmp_input, "--schema", "universal",
                         "--no-embeddings", "--output", out_path],
                    )
            assert result.exit_code == 0
            assert Path(out_path).exists()
            data = json.loads(Path(out_path).read_text(encoding="utf-8"))
            assert "title" in data
        finally:
            Path(tmp_input).unlink()


# ---------------------------------------------------------------------------
# Test 8: analyze file not found
# ---------------------------------------------------------------------------

def test_cli_analyze_file_not_found():
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "/nonexistent/file.txt"])
    assert result.exit_code != 0
