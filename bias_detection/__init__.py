"""
Bias Detection Module for AI News Summarizer

This module provides tools for detecting bias in news articles through:
- Multi-source comparison
- Sentiment analysis
- Fact-checking integration
- Bias scoring
- Source credibility tracking
"""

from .bias_analyzer import BiasAnalyzer
from .source_comparator import SourceComparator
from .credibility_scorer import CredibilityScorer

__all__ = ['BiasAnalyzer', 'SourceComparator', 'CredibilityScorer'] 