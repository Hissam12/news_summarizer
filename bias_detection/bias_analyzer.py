#!/usr/bin/env python3
"""
Bias Analyzer for News Articles

Analyzes articles for bias through multiple methods:
- Multi-source comparison
- Sentiment analysis
- Language pattern detection
- Fact-checking integration
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import os

from config.settings import Config
from fetchers.newsapi_fetcher import NewsAPIFetcher
from summarizer.summarizer import TextSummarizer


class BiasAnalyzer:
    """Main bias analysis coordinator"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.fetcher = NewsAPIFetcher(config.NEWSAPI_KEY)
        self.summarizer = TextSummarizer(config.OLLAMA_MODEL, config.OLLAMA_BASE_URL)
        
        # Bias detection thresholds
        self.sentiment_threshold = 0.3  # Moderate bias threshold
        self.language_threshold = 0.4   # Loaded language threshold
        self.fact_check_threshold = 0.5 # Fact-checking confidence
        
    def analyze_topic_bias(self, topic: str, max_sources: int = 5) -> Dict:
        """
        Analyze bias for a specific topic across multiple sources
        
        Args:
            topic: The topic to analyze
            max_sources: Maximum number of sources to compare
            
        Returns:
            Dictionary containing bias analysis results
        """
        try:
            self.logger.info(f"🔍 Starting bias analysis for topic: {topic}")
            
            # Step 1: Fetch articles from multiple sources
            articles = self._fetch_multi_source_articles(topic, max_sources)
            
            if not articles:
                return {"error": "No articles found for analysis"}
            
            # Step 2: Group articles by source
            source_groups = self._group_by_source(articles)
            
            # Step 3: Analyze each source's bias
            source_analyses = {}
            for source, source_articles in source_groups.items():
                source_analyses[source] = self._analyze_source_bias(source_articles)
            
            # Step 4: Compare sources and detect discrepancies
            comparison_results = self._compare_sources(source_analyses)
            
            # Step 5: Generate overall bias report
            bias_report = self._generate_bias_report(topic, source_analyses, comparison_results)
            
            # Step 6: Save results
            self._save_bias_analysis(topic, bias_report)
            
            return bias_report
            
        except Exception as e:
            self.logger.error(f"❌ Error in bias analysis: {e}")
            return {"error": str(e)}
    
    def _fetch_multi_source_articles(self, topic: str, max_sources: int) -> List[Dict]:
        """Fetch articles from multiple sources for the same topic"""
        try:
            # Fetch articles with broader search to get different sources
            articles = self.fetcher.fetch_news(topic, max_sources * 3, self.config.SEARCH_DAYS_BACK)
            
            # Filter to ensure we have articles from different sources
            unique_sources = set()
            filtered_articles = []
            
            for article in articles:
                source = article.get('source', 'Unknown')
                if source not in unique_sources and len(filtered_articles) < max_sources:
                    unique_sources.add(source)
                    filtered_articles.append(article)
            
            self.logger.info(f"📰 Found {len(filtered_articles)} articles from {len(unique_sources)} sources")
            return filtered_articles
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching multi-source articles: {e}")
            return []
    
    def _group_by_source(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Group articles by their source"""
        source_groups = {}
        
        for article in articles:
            source = article.get('source', 'Unknown')
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(article)
        
        return source_groups
    
    def _analyze_source_bias(self, articles: List[Dict]) -> Dict:
        """Analyze bias for articles from a single source"""
        try:
            if not articles:
                return {"error": "No articles to analyze"}
            
            # Analyze sentiment bias
            sentiment_scores = self._analyze_sentiment_bias(articles)
            
            # Analyze language bias
            language_scores = self._analyze_language_bias(articles)
            
            # Analyze factual consistency
            fact_scores = self._analyze_factual_consistency(articles)
            
            # Calculate overall bias score
            overall_bias = self._calculate_overall_bias(sentiment_scores, language_scores, fact_scores)
            
            return {
                "source": articles[0].get('source', 'Unknown'),
                "article_count": len(articles),
                "sentiment_bias": sentiment_scores,
                "language_bias": language_scores,
                "factual_consistency": fact_scores,
                "overall_bias_score": overall_bias,
                "bias_level": self._classify_bias_level(overall_bias),
                "articles": articles
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing source bias: {e}")
            return {"error": str(e)}
    
    def _analyze_sentiment_bias(self, articles: List[Dict]) -> Dict:
        """Analyze emotional language and sentiment bias"""
        try:
            # This is a simplified sentiment analysis
            # In a full implementation, you'd use a proper sentiment analysis library
            
            total_articles = len(articles)
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for article in articles:
                content = article.get('content', '')
                title = article.get('title', '')
                full_text = f"{title} {content}".lower()
                
                # Simple keyword-based sentiment analysis
                positive_words = ['positive', 'good', 'great', 'excellent', 'success', 'win', 'gain', 'profit']
                negative_words = ['negative', 'bad', 'terrible', 'failure', 'loss', 'decline', 'crisis', 'problem']
                
                positive_score = sum(1 for word in positive_words if word in full_text)
                negative_score = sum(1 for word in negative_words if word in full_text)
                
                if positive_score > negative_score:
                    positive_count += 1
                elif negative_score > positive_score:
                    negative_count += 1
                else:
                    neutral_count += 1
            
            return {
                "positive_ratio": positive_count / total_articles if total_articles > 0 else 0,
                "negative_ratio": negative_count / total_articles if total_articles > 0 else 0,
                "neutral_ratio": neutral_count / total_articles if total_articles > 0 else 0,
                "sentiment_bias_score": (positive_count - negative_count) / total_articles if total_articles > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in sentiment analysis: {e}")
            return {"error": str(e)}
    
    def _analyze_language_bias(self, articles: List[Dict]) -> Dict:
        """Analyze loaded language and bias indicators"""
        try:
            loaded_language_count = 0
            total_articles = len(articles)
            
            # Loaded language indicators
            loaded_indicators = [
                'clearly', 'obviously', 'undoubtedly', 'certainly', 'definitely',
                'shocking', 'scandalous', 'outrageous', 'amazing', 'incredible',
                'disaster', 'crisis', 'catastrophe', 'miracle', 'breakthrough'
            ]
            
            for article in articles:
                content = article.get('content', '')
                title = article.get('title', '')
                full_text = f"{title} {content}".lower()
                
                # Count loaded language instances
                loaded_count = sum(1 for indicator in loaded_indicators if indicator in full_text)
                if loaded_count > 2:  # Threshold for loaded language
                    loaded_language_count += 1
            
            return {
                "loaded_language_ratio": loaded_language_count / total_articles if total_articles > 0 else 0,
                "language_bias_score": loaded_language_count / total_articles if total_articles > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in language bias analysis: {e}")
            return {"error": str(e)}
    
    def _analyze_factual_consistency(self, articles: List[Dict]) -> Dict:
        """Analyze factual consistency across articles"""
        try:
            # This is a simplified fact-checking approach
            # In a full implementation, you'd integrate with fact-checking APIs
            
            total_articles = len(articles)
            factual_issues = 0
            
            # Check for common factual issues
            for article in articles:
                content = article.get('content', '')
                
                # Look for potential factual issues (simplified)
                factual_red_flags = [
                    'unverified', 'rumor', 'allegedly', 'supposedly',
                    'according to sources', 'anonymous sources'
                ]
                
                if any(flag in content.lower() for flag in factual_red_flags):
                    factual_issues += 1
            
            return {
                "factual_issues_ratio": factual_issues / total_articles if total_articles > 0 else 0,
                "factual_consistency_score": 1 - (factual_issues / total_articles if total_articles > 0 else 0)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in factual consistency analysis: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_bias(self, sentiment_scores: Dict, language_scores: Dict, fact_scores: Dict) -> float:
        """Calculate overall bias score from individual components"""
        try:
            sentiment_score = abs(sentiment_scores.get('sentiment_bias_score', 0))
            language_score = language_scores.get('language_bias_score', 0)
            factual_score = 1 - fact_scores.get('factual_consistency_score', 0)
            
            # Weighted average of bias indicators
            overall_bias = (sentiment_score * 0.4 + language_score * 0.3 + factual_score * 0.3)
            
            return min(overall_bias, 1.0)  # Cap at 1.0
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating overall bias: {e}")
            return 0.0
    
    def _classify_bias_level(self, bias_score: float) -> str:
        """Classify bias level based on score"""
        if bias_score < 0.2:
            return "Low"
        elif bias_score < 0.4:
            return "Moderate"
        elif bias_score < 0.6:
            return "High"
        else:
            return "Very High"
    
    def _compare_sources(self, source_analyses: Dict) -> Dict:
        """Compare bias across different sources"""
        try:
            sources = list(source_analyses.keys())
            if len(sources) < 2:
                return {"error": "Need at least 2 sources for comparison"}
            
            # Calculate average bias scores
            bias_scores = []
            for source, analysis in source_analyses.items():
                if 'overall_bias_score' in analysis:
                    bias_scores.append(analysis['overall_bias_score'])
            
            if not bias_scores:
                return {"error": "No valid bias scores for comparison"}
            
            avg_bias = sum(bias_scores) / len(bias_scores)
            max_bias = max(bias_scores)
            min_bias = min(bias_scores)
            bias_variance = max_bias - min_bias
            
            return {
                "average_bias": avg_bias,
                "bias_range": bias_variance,
                "most_biased_source": max(source_analyses.items(), key=lambda x: x[1].get('overall_bias_score', 0))[0],
                "least_biased_source": min(source_analyses.items(), key=lambda x: x[1].get('overall_bias_score', 0))[0],
                "consistency_level": "High" if bias_variance < 0.2 else "Moderate" if bias_variance < 0.4 else "Low"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error comparing sources: {e}")
            return {"error": str(e)}
    
    def _generate_bias_report(self, topic: str, source_analyses: Dict, comparison_results: Dict) -> Dict:
        """Generate comprehensive bias report"""
        try:
            report = {
                "topic": topic,
                "analysis_timestamp": datetime.now().isoformat(),
                "sources_analyzed": len(source_analyses),
                "source_analyses": source_analyses,
                "comparison_results": comparison_results,
                "recommendations": self._generate_recommendations(source_analyses, comparison_results)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generating bias report: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, source_analyses: Dict, comparison_results: Dict) -> List[str]:
        """Generate recommendations based on bias analysis"""
        recommendations = []
        
        try:
            # Check for high bias sources
            high_bias_sources = [
                source for source, analysis in source_analyses.items()
                if analysis.get('bias_level', 'Low') in ['High', 'Very High']
            ]
            
            if high_bias_sources:
                recommendations.append(f"⚠️ High bias detected in sources: {', '.join(high_bias_sources)}")
            
            # Check for consistency
            consistency = comparison_results.get('consistency_level', 'Unknown')
            if consistency == 'Low':
                recommendations.append("⚠️ Significant bias variance detected across sources")
            elif consistency == 'High':
                recommendations.append("✅ Consistent bias levels across sources")
            
            # General recommendations
            recommendations.append("📖 Read multiple sources for balanced perspective")
            recommendations.append("🔍 Fact-check claims from high-bias sources")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Error generating recommendations: {e}")
            return ["Error generating recommendations"]
    
    def _save_bias_analysis(self, topic: str, bias_report: Dict):
        """Save bias analysis results"""
        try:
            os.makedirs("data", exist_ok=True)
            
            filename = f"data/bias_analysis_{topic.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(bias_report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Bias analysis saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving bias analysis: {e}") 