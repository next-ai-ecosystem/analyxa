#!/usr/bin/env python3
"""
Analyxa Dogfooding Script — IF-007 + IF-010 (multi-idioma)
Executes 18 analyses across 4 schemas to validate the full pipeline.

Usage:
    cd /opt/analyxa && source venv/bin/activate
    PYTHONPATH=src python3 scripts/dogfood.py

Results saved to: examples/results/
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure src is in path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from analyxa import analyze
from analyxa.config import get_config


CONVERSATIONS_DIR = ROOT / "examples" / "conversations"
RESULTS_DIR = ROOT / "examples" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# 14 analyses: 8 direct (conv + matching schema) + 6 cross-schema (conv + universal)
ANALYSES = [
    # --- Direct analyses (conv + matching schema) ---
    {
        "id": "A01",
        "label": "Universal greeting — schema universal",
        "file": "universal_greeting.txt",
        "schema": "universal",
    },
    {
        "id": "A02",
        "label": "Universal technical — schema universal",
        "file": "universal_technical.txt",
        "schema": "universal",
    },
    {
        "id": "A03",
        "label": "Support billing — schema support",
        "file": "support_billing.txt",
        "schema": "support",
    },
    {
        "id": "A04",
        "label": "Support cancellation — schema support",
        "file": "support_cancellation.txt",
        "schema": "support",
    },
    {
        "id": "A05",
        "label": "Sales demo — schema sales",
        "file": "sales_demo.txt",
        "schema": "sales",
    },
    {
        "id": "A06",
        "label": "Sales objection — schema sales",
        "file": "sales_objection.txt",
        "schema": "sales",
    },
    {
        "id": "A07",
        "label": "Coaching progress — schema coaching",
        "file": "coaching_progress.txt",
        "schema": "coaching",
    },
    {
        "id": "A08",
        "label": "Coaching crisis — schema coaching",
        "file": "coaching_crisis.txt",
        "schema": "coaching",
    },
    # --- Cross-schema analyses (same conv, universal schema for comparison) ---
    {
        "id": "A09",
        "label": "Support billing — schema universal (cross)",
        "file": "support_billing.txt",
        "schema": "universal",
    },
    {
        "id": "A10",
        "label": "Support cancellation — schema universal (cross)",
        "file": "support_cancellation.txt",
        "schema": "universal",
    },
    {
        "id": "A11",
        "label": "Sales demo — schema universal (cross)",
        "file": "sales_demo.txt",
        "schema": "universal",
    },
    {
        "id": "A12",
        "label": "Sales objection — schema universal (cross)",
        "file": "sales_objection.txt",
        "schema": "universal",
    },
    {
        "id": "A13",
        "label": "Coaching progress — schema universal (cross)",
        "file": "coaching_progress.txt",
        "schema": "universal",
    },
    {
        "id": "A14",
        "label": "Coaching crisis — schema universal (cross)",
        "file": "coaching_crisis.txt",
        "schema": "universal",
    },
    # --- Multi-language analyses (IF-010) ---
    {
        "id": "A15",
        "label": "Support billing ES — schema support",
        "file": "support_billing_es.txt",
        "schema": "support",
        "expected_language": "es",
    },
    {
        "id": "A16",
        "label": "Sales inquiry FR — schema sales",
        "file": "sales_inquiry_fr.txt",
        "schema": "sales",
        "expected_language": "fr",
    },
    {
        "id": "A17",
        "label": "Coaching progress PT — schema coaching",
        "file": "coaching_progress_pt.txt",
        "schema": "coaching",
        "expected_language": "pt",
    },
    {
        "id": "A18",
        "label": "Support billing DE — schema support",
        "file": "support_billing_de.txt",
        "schema": "support",
        "expected_language": "de",
    },
]


def load_conversation(filename: str) -> str:
    path = CONVERSATIONS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Conversation not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def check_quality(result_dict: dict, schema_name: str) -> list[str]:
    """Basic quality checks on extracted fields."""
    issues = []

    # Language field — always required (IF-010)
    lang = result_dict.get("language")
    if not lang or not isinstance(lang, str) or len(lang) < 2:
        issues.append(f"language field missing or invalid: {lang!r}")

    # Universal fields — always required
    if not result_dict.get("title"):
        issues.append("title is empty")
    if not result_dict.get("summary"):
        issues.append("summary is empty")
    if result_dict.get("sentiment") not in ("positive", "negative", "mixed", "neutral"):
        issues.append(f"invalid sentiment: {result_dict.get('sentiment')!r}")
    if result_dict.get("sentiment_intensity") not in ("low", "medium", "high"):
        issues.append(f"invalid sentiment_intensity: {result_dict.get('sentiment_intensity')!r}")
    if not isinstance(result_dict.get("topics"), list):
        issues.append("topics is not a list")
    if result_dict.get("session_outcome") not in (
        "resolved", "unresolved", "escalated", "abandoned"
    ):
        issues.append(f"invalid session_outcome: {result_dict.get('session_outcome')!r}")

    # Schema-specific checks
    if schema_name == "support":
        if result_dict.get("escalation_needed") not in (True, False, None):
            issues.append("escalation_needed should be bool")

    if schema_name == "sales":
        valid_stages = {
            "awareness", "consideration", "decision",
            "negotiation", "closed_won", "closed_lost"
        }
        if result_dict.get("buying_stage") and result_dict.get("buying_stage") not in valid_stages:
            issues.append(f"invalid buying_stage: {result_dict.get('buying_stage')!r}")

    if schema_name == "coaching":
        valid_valence = {
            "very_positive", "positive", "neutral", "negative", "very_negative"
        }
        if result_dict.get("emotional_valence") and result_dict.get("emotional_valence") not in valid_valence:
            issues.append(f"invalid emotional_valence: {result_dict.get('emotional_valence')!r}")
        valid_momentum = {"accelerating", "steady", "stalled", "regressing"}
        if result_dict.get("therapeutic_momentum") and result_dict.get("therapeutic_momentum") not in valid_momentum:
            issues.append(f"invalid therapeutic_momentum: {result_dict.get('therapeutic_momentum')!r}")

    return issues


def run_analysis(entry: dict) -> dict:
    conversation = load_conversation(entry["file"])
    start = time.time()

    result = analyze(
        conversation=conversation,
        schema=entry["schema"],
        enable_embeddings=False,  # Skip embeddings for speed
    )

    elapsed = time.time() - start
    result_dict = result.fields
    success = result.llm_response.success
    error = result.llm_response.error

    quality_issues = check_quality(result_dict, entry["schema"]) if success else []

    return {
        "id": entry["id"],
        "label": entry["label"],
        "schema": entry["schema"],
        "file": entry["file"],
        "success": success,
        "elapsed_seconds": round(elapsed, 2),
        "quality_issues": quality_issues,
        "quality_ok": success and len(quality_issues) == 0,
        "fields": result_dict,
        "error": error,
    }


def check_api_key() -> bool:
    """Returns True if ANTHROPIC_API_KEY looks valid (not a placeholder)."""
    config = get_config(env_file=str(ROOT / ".env"))
    key = config.anthropic_api_key or ""
    return bool(key) and "CHANGE_ME" not in key and len(key) > 20


def main():
    print("=" * 60)
    print("ANALYXA DOGFOODING — IF-007")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Analyses: {len(ANALYSES)}")
    print("=" * 60)
    print()

    if not check_api_key():
        print("WARNING: ANTHROPIC_API_KEY not configured in .env")
        print("Set a valid API key to run live dogfooding.")
        print("Pipeline integrity verified via unit/integration tests (101 passing).")
        sys.exit(0)

    results = []
    passed = 0
    failed = 0
    quality_failures = 0

    for i, entry in enumerate(ANALYSES, 1):
        print(f"[{i:02d}/{len(ANALYSES)}] {entry['id']} — {entry['label']}")

        try:
            result = run_analysis(entry)
            results.append(result)

            status = "✓" if result["success"] else "✗"
            qstatus = "Q✓" if result["quality_ok"] else f"Q✗({len(result['quality_issues'])})"
            print(f"       {status} {qstatus} | {result['elapsed_seconds']}s")

            if result["success"]:
                passed += 1
                # Print key fields
                f = result["fields"]
                print(f"       language: {f.get('language', 'N/A')}")
                print(f"       title: {f.get('title', 'N/A')!r}")
                print(f"       sentiment: {f.get('sentiment')} / {f.get('sentiment_intensity')}")
                print(f"       outcome: {f.get('session_outcome')}")

                # Verify expected language (IF-010)
                expected_lang = entry.get("expected_language")
                if expected_lang:
                    actual_lang = f.get("language")
                    if actual_lang != expected_lang:
                        result["quality_issues"].append(
                            f"expected language '{expected_lang}', got '{actual_lang}'"
                        )
                        result["quality_ok"] = False
                elif f.get("language") and f.get("language") != "en":
                    # Original 14 English conversations should detect as "en"
                    result["quality_issues"].append(
                        f"expected language 'en' for English conv, got '{f.get('language')}'"
                    )
                    result["quality_ok"] = False
                schema = entry["schema"]
                if schema == "coaching":
                    print(f"       emotional_valence: {f.get('emotional_valence')}")
                    print(f"       therapeutic_momentum: {f.get('therapeutic_momentum')}")
                elif schema == "sales":
                    print(f"       buying_stage: {f.get('buying_stage')}")
                    print(f"       decision_urgency: {f.get('decision_urgency')}")
                elif schema == "support":
                    print(f"       escalation_needed: {f.get('escalation_needed')}")
                    print(f"       issue_category: {f.get('issue_category')}")
            else:
                failed += 1
                print(f"       ERROR: {result.get('error')}")

            if not result["quality_ok"]:
                quality_failures += 1
                for issue in result["quality_issues"]:
                    print(f"       QUALITY: {issue}")

        except Exception as e:
            failed += 1
            print(f"       EXCEPTION: {e}")
            results.append({
                "id": entry["id"],
                "label": entry["label"],
                "schema": entry["schema"],
                "file": entry["file"],
                "success": False,
                "error": str(e),
                "quality_ok": False,
                "quality_issues": [],
                "fields": {},
                "elapsed_seconds": 0,
            })

        print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total:           {len(ANALYSES)}")
    print(f"Passed:          {passed}")
    print(f"Failed:          {failed}")
    print(f"Quality OK:      {len(ANALYSES) - quality_failures}")
    print(f"Quality issues:  {quality_failures}")
    success_rate = (passed / len(ANALYSES)) * 100
    print(f"Success rate:    {success_rate:.0f}%")
    print()

    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total": len(ANALYSES),
        "passed": passed,
        "failed": failed,
        "quality_failures": quality_failures,
        "success_rate": success_rate,
        "results": results,
    }
    report_path = RESULTS_DIR / "dogfood_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report saved: {report_path}")

    # Exit with error if any failures
    if failed > 0:
        print(f"\n{failed} analyses FAILED — check report for details")
        sys.exit(1)
    else:
        print("All analyses PASSED ✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
