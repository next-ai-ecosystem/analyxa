"""Analyxa — Multi-dimensional extraction engine for AI conversations."""

__version__ = "0.1.0"

from analyxa.analyzer import Analyzer, AnalysisResult, analyze
from analyxa.schema import SchemaManager

__all__ = ["Analyzer", "AnalysisResult", "analyze", "SchemaManager", "__version__"]
