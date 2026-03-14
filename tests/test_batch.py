"""Tests for batch.py — unit tests with mocked LLM (no API keys required)."""

from unittest.mock import MagicMock, patch

import pytest

from analyxa.batch import batch_analyze, BatchResult

# Patch target: Analyzer is imported inside the function from analyxa.analyzer
_ANALYZER_PATH = "analyxa.analyzer.Analyzer"


def _make_mock_result(title: str = "Mock Session") -> MagicMock:
    """Build a minimal mock AnalysisResult."""
    result = MagicMock()
    result.validation_errors = []
    result.to_dict.return_value = {"title": title, "summary": "Mock summary."}
    result.to_flat_dict.return_value = {"title": title, "summary": "Mock summary."}
    result.embedding = [0.0] * 1536
    return result


# ------------------------------------------------------------------
# Test 1: basic batch_analyze
# ------------------------------------------------------------------

def test_batch_analyze_basic():
    mock_result = _make_mock_result()

    with patch(_ANALYZER_PATH) as MockAnalyzer:
        instance = MockAnalyzer.return_value
        instance.analyze.return_value = mock_result

        conversations = [
            {"text": "conv one"},
            {"text": "conv two"},
        ]
        result = batch_analyze(
            conversations=conversations,
            schema_name="universal",
            provider="anthropic",
        )

    assert isinstance(result, BatchResult)
    assert result.total == 2
    assert result.successful == 2
    assert result.failed == 0
    assert result.success_rate == 1.0
    assert len(result.results) == 2
    assert len(result.errors) == 0


# ------------------------------------------------------------------
# Test 2: batch_analyze with failure
# ------------------------------------------------------------------

def test_batch_analyze_with_failure():
    mock_result = _make_mock_result()

    with patch(_ANALYZER_PATH) as MockAnalyzer:
        instance = MockAnalyzer.return_value
        # First call succeeds, second raises
        instance.analyze.side_effect = [
            mock_result,
            RuntimeError("LLM timeout"),
        ]

        conversations = [
            {"text": "conv one"},
            {"text": "conv two", "id": "failing-conv"},
        ]
        result = batch_analyze(
            conversations=conversations,
            schema_name="universal",
            provider="anthropic",
        )

    assert result.total == 2
    assert result.successful == 1
    assert result.failed == 1
    assert result.success_rate == 0.5
    assert len(result.errors) == 1
    assert result.errors[0]["id"] == "failing-conv"
    assert "RuntimeError" in result.errors[0]["error"]


# ------------------------------------------------------------------
# Test 3: progress callback
# ------------------------------------------------------------------

def test_batch_analyze_progress_callback():
    mock_result = _make_mock_result()
    calls = []

    def progress_cb(current, total, res):
        calls.append((current, total, res))

    with patch(_ANALYZER_PATH) as MockAnalyzer:
        instance = MockAnalyzer.return_value
        instance.analyze.return_value = mock_result

        conversations = [{"text": f"conv {i}"} for i in range(4)]
        batch_analyze(
            conversations=conversations,
            schema_name="universal",
            provider="anthropic",
            on_progress=progress_cb,
        )

    assert len(calls) == 4
    for i, (current, total, res) in enumerate(calls, 1):
        assert current == i
        assert total == 4
        assert res is not None


# ------------------------------------------------------------------
# Test 4: batch_analyze with sink
# ------------------------------------------------------------------

def test_batch_analyze_with_sink():
    mock_result = _make_mock_result()
    mock_sink = MagicMock()
    mock_sink.store = MagicMock()

    with patch(_ANALYZER_PATH) as MockAnalyzer:
        instance = MockAnalyzer.return_value
        instance.analyze.return_value = mock_result

        conversations = [{"text": "conv one"}, {"text": "conv two"}]
        batch_analyze(
            conversations=conversations,
            schema_name="universal",
            provider="anthropic",
            sink=mock_sink,
        )

    # store called once per successful analysis
    assert mock_sink.store.call_count == 2


# ------------------------------------------------------------------
# Test 5: elapsed time
# ------------------------------------------------------------------

def test_batch_result_elapsed_time():
    mock_result = _make_mock_result()

    with patch(_ANALYZER_PATH) as MockAnalyzer:
        instance = MockAnalyzer.return_value
        instance.analyze.return_value = mock_result

        conversations = [{"text": "conv one"}]
        result = batch_analyze(
            conversations=conversations,
            schema_name="universal",
            provider="anthropic",
        )

    assert result.elapsed_seconds >= 0.0
    assert isinstance(result.elapsed_seconds, float)
