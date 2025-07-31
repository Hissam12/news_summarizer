#!/usr/bin/env python3
"""
Credibility Scorer for News Sources

Tracks and scores source credibility based on:
- Historical bias patterns
- Fact-checking accuracy
- Source reputation
- Consistency metrics
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import os

from config.settings import Config


class CredibilityScorer:
    """Score and track source credibility"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.credibility_data_path = "data/source_credibility.json"
        self.credibility_data = self._load_credibility_data()
        
        # Known source reputations (simplified)
        self.known_sources = {
            "reuters": {"reputation": "high", "bias": "low", "fact_check": "excellent"},
            "associated press": {"reputation": "high", "bias": "low", "fact_check": "excellent"},
            "bbc": {"reputation": "high", "bias": "low", "fact_check": "excellent"},
            "cnn": {"reputation": "medium", "bias": "moderate", "fact_check": "good"},
            "fox news": {"reputation": "medium", "bias": "high", "fact_check": "mixed"},
            "msnbc": {"reputation": "medium", "bias": "moderate", "fact_check": "good"},
            "new york times": {"reputation": "high", "bias": "low", "fact_check": "excellent"},
            "washington post": {"reputation": "high", "bias": "low", "fact_check": "excellent"},
            "wall street journal": {"reputation": "high", "bias": "low", "fact_check": "excellent"},
            "usa today": {"reputation": "medium", "bias": "low", "fact_check": "good"}
        }
    
    def score_source_credibility(self, source: str, articles: List[Dict]) -> Dict:
        """
        Score the credibility of a news source
        
        Args:
            source: The source name
            articles: List of articles from this source
            
        Returns:
            Dictionary containing credibility score and analysis
        """
        try:
            self.logger.info(f"🔍 Scoring credibility for source: {source}")
            
            # Get base reputation score
            base_score = self._get_base_reputation_score(source)
            
            # Analyze recent performance
            performance_score = self._analyze_recent_performance(source, articles)
            
            # Calculate consistency score
            consistency_score = self._calculate_consistency_score(source, articles)
            
            # Calculate overall credibility
            overall_credibility = self._calculate_overall_credibility(
                base_score, performance_score, consistency_score
            )
            
            # Update historical data
            self._update_source_history(source, overall_credibility, articles)
            
            credibility_report = {
                "source": source,
                "overall_credibility": overall_credibility,
                "credibility_level": self._classify_credibility_level(overall_credibility),
                "base_reputation": base_score,
                "recent_performance": performance_score,
                "consistency_score": consistency_score,
                "recommendations": self._generate_credibility_recommendations(overall_credibility, source)
            }
            
            return credibility_report
            
        except Exception as e:
            self.logger.error(f"❌ Error scoring source credibility: {e}")
            return {"error": str(e)}
    
    def _load_credibility_data(self) -> Dict:
        """Load historical credibility data"""
        try:
            if os.path.exists(self.credibility_data_path):
                with open(self.credibility_data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"sources": {}, "last_updated": datetime.now().isoformat()}
                
        except Exception as e:
            self.logger.error(f"❌ Error loading credibility data: {e}")
            return {"sources": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_credibility_data(self):
        """Save credibility data to file"""
        try:
            os.makedirs("data", exist_ok=True)
            
            self.credibility_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.credibility_data_path, 'w', encoding='utf-8') as f:
                json.dump(self.credibility_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving credibility data: {e}")
    
    def _get_base_reputation_score(self, source: str) -> float:
        """Get base reputation score for a source"""
        try:
            source_lower = source.lower()
            
            # Check known sources
            if source_lower in self.known_sources:
                reputation = self.known_sources[source_lower]["reputation"]
                bias = self.known_sources[source_lower]["bias"]
                fact_check = self.known_sources[source_lower]["fact_check"]
                
                # Calculate base score
                reputation_scores = {"high": 0.9, "medium": 0.7, "low": 0.5}
                bias_scores = {"low": 0.9, "moderate": 0.7, "high": 0.5}
                fact_check_scores = {"excellent": 0.9, "good": 0.7, "mixed": 0.5, "poor": 0.3}
                
                base_score = (
                    reputation_scores.get(reputation, 0.5) * 0.4 +
                    bias_scores.get(bias, 0.5) * 0.3 +
                    fact_check_scores.get(fact_check, 0.5) * 0.3
                )
                
                return base_score
            
            # Unknown source - default to medium
            return 0.6
            
        except Exception as e:
            self.logger.error(f"❌ Error getting base reputation score: {e}")
            return 0.5
    
    def _analyze_recent_performance(self, source: str, articles: List[Dict]) -> float:
        """Analyze recent performance based on article quality"""
        try:
            if not articles:
                return 0.5
            
            # Analyze article quality indicators
            quality_scores = []
            
            for article in articles:
                content = article.get('content', '')
                title = article.get('title', '')
                
                # Quality indicators
                length_score = min(len(content) / 1000, 1.0)  # Prefer longer articles
                
                # Check for quality indicators
                quality_indicators = [
                    'according to', 'officials said', 'confirmed', 'announced',
                    'reported', 'stated', 'verified', 'official'
                ]
                
                indicator_count = sum(1 for indicator in quality_indicators if indicator in content.lower())
                indicator_score = min(indicator_count / 5, 1.0)
                
                # Check for red flags
                red_flags = [
                    'unverified', 'rumor', 'allegedly', 'supposedly',
                    'anonymous sources', 'sources say'
                ]
                
                red_flag_count = sum(1 for flag in red_flags if flag in content.lower())
                red_flag_penalty = red_flag_count * 0.1
                
                # Calculate article quality score
                article_score = (length_score * 0.3 + indicator_score * 0.7) - red_flag_penalty
                quality_scores.append(max(article_score, 0.0))
            
            # Return average quality score
            return sum(quality_scores) / len(quality_scores) if quality_scores else 0.5
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing recent performance: {e}")
            return 0.5
    
    def _calculate_consistency_score(self, source: str, articles: List[Dict]) -> float:
        """Calculate consistency score based on article patterns"""
        try:
            if not articles:
                return 0.5
            
            # Analyze consistency across articles
            tones = []
            lengths = []
            focus_areas = []
            
            for article in articles:
                content = article.get('content', '')
                title = article.get('title', '')
                
                # Analyze tone
                positive_words = ['positive', 'good', 'success', 'improve']
                negative_words = ['negative', 'bad', 'problem', 'crisis']
                
                pos_count = sum(1 for word in positive_words if word in content.lower())
                neg_count = sum(1 for word in negative_words if word in content.lower())
                
                if pos_count > neg_count:
                    tones.append('positive')
                elif neg_count > pos_count:
                    tones.append('negative')
                else:
                    tones.append('neutral')
                
                # Record length
                lengths.append(len(content))
                
                # Analyze focus areas
                focus_keywords = ['politics', 'economy', 'technology', 'social', 'international']
                article_focus = [keyword for keyword in focus_keywords if keyword in content.lower()]
                focus_areas.extend(article_focus)
            
            # Calculate consistency metrics
            tone_consistency = 1.0 - (len(set(tones)) / len(tones)) if tones else 0.5
            length_consistency = 1.0 - (max(lengths) - min(lengths)) / max(lengths) if lengths else 0.5
            focus_consistency = 1.0 - (len(set(focus_areas)) / len(focus_areas)) if focus_areas else 0.5
            
            # Weighted average
            consistency_score = (
                tone_consistency * 0.4 +
                length_consistency * 0.3 +
                focus_consistency * 0.3
            )
            
            return consistency_score
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating consistency score: {e}")
            return 0.5
    
    def _calculate_overall_credibility(self, base_score: float, performance_score: float, consistency_score: float) -> float:
        """Calculate overall credibility score"""
        try:
            # Weighted average of all scores
            overall_score = (
                base_score * 0.4 +
                performance_score * 0.4 +
                consistency_score * 0.2
            )
            
            return min(overall_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating overall credibility: {e}")
            return 0.5
    
    def _classify_credibility_level(self, credibility_score: float) -> str:
        """Classify credibility level based on score"""
        if credibility_score >= 0.8:
            return "Very High"
        elif credibility_score >= 0.6:
            return "High"
        elif credibility_score >= 0.4:
            return "Medium"
        elif credibility_score >= 0.2:
            return "Low"
        else:
            return "Very Low"
    
    def _update_source_history(self, source: str, credibility_score: float, articles: List[Dict]):
        """Update historical credibility data for a source"""
        try:
            if "sources" not in self.credibility_data:
                self.credibility_data["sources"] = {}
            
            if source not in self.credibility_data["sources"]:
                self.credibility_data["sources"][source] = {
                    "history": [],
                    "average_credibility": 0.0,
                    "article_count": 0,
                    "last_updated": datetime.now().isoformat()
                }
            
            # Add new data point
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "credibility_score": credibility_score,
                "article_count": len(articles),
                "average_article_length": sum(len(a.get('content', '')) for a in articles) / len(articles) if articles else 0
            }
            
            self.credibility_data["sources"][source]["history"].append(history_entry)
            
            # Keep only last 10 entries
            if len(self.credibility_data["sources"][source]["history"]) > 10:
                self.credibility_data["sources"][source]["history"] = self.credibility_data["sources"][source]["history"][-10:]
            
            # Update average credibility
            scores = [entry["credibility_score"] for entry in self.credibility_data["sources"][source]["history"]]
            self.credibility_data["sources"][source]["average_credibility"] = sum(scores) / len(scores)
            
            # Update total article count
            self.credibility_data["sources"][source]["article_count"] += len(articles)
            self.credibility_data["sources"][source]["last_updated"] = datetime.now().isoformat()
            
            # Save updated data
            self._save_credibility_data()
            
        except Exception as e:
            self.logger.error(f"❌ Error updating source history: {e}")
    
    def _generate_credibility_recommendations(self, credibility_score: float, source: str) -> List[str]:
        """Generate recommendations based on credibility score"""
        recommendations = []
        
        try:
            if credibility_score >= 0.8:
                recommendations.append("✅ High credibility source - generally reliable")
                recommendations.append("📖 Good source for primary information")
            elif credibility_score >= 0.6:
                recommendations.append("⚠️ Moderate credibility - verify important claims")
                recommendations.append("📖 Use as supplementary source")
            elif credibility_score >= 0.4:
                recommendations.append("⚠️ Low credibility - fact-check claims")
                recommendations.append("🔍 Cross-reference with high-credibility sources")
            else:
                recommendations.append("❌ Very low credibility - avoid as primary source")
                recommendations.append("🔍 Always fact-check claims from this source")
            
            # General recommendations
            recommendations.append("📚 Read multiple sources for balanced perspective")
            recommendations.append("🔍 Fact-check important claims regardless of source")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Error generating credibility recommendations: {e}")
            return ["Error generating recommendations"]
    
    def get_source_credibility_history(self, source: str) -> Dict:
        """Get historical credibility data for a source"""
        try:
            if source in self.credibility_data.get("sources", {}):
                return self.credibility_data["sources"][source]
            else:
                return {"error": "No historical data for this source"}
                
        except Exception as e:
            self.logger.error(f"❌ Error getting source credibility history: {e}")
            return {"error": str(e)}
    
    def get_top_credible_sources(self, limit: int = 5) -> List[Dict]:
        """Get top credible sources based on historical data"""
        try:
            sources = self.credibility_data.get("sources", {})
            
            # Sort by average credibility
            sorted_sources = sorted(
                sources.items(),
                key=lambda x: x[1].get("average_credibility", 0),
                reverse=True
            )
            
            top_sources = []
            for source, data in sorted_sources[:limit]:
                top_sources.append({
                    "source": source,
                    "average_credibility": data.get("average_credibility", 0),
                    "article_count": data.get("article_count", 0),
                    "last_updated": data.get("last_updated", "")
                })
            
            return top_sources
            
        except Exception as e:
            self.logger.error(f"❌ Error getting top credible sources: {e}")
            return []
    
    def generate_credibility_report(self) -> Dict:
        """Generate comprehensive credibility report"""
        try:
            sources = self.credibility_data.get("sources", {})
            
            report = {
                "total_sources_tracked": len(sources),
                "top_credible_sources": self.get_top_credible_sources(5),
                "credibility_distribution": self._calculate_credibility_distribution(sources),
                "last_updated": self.credibility_data.get("last_updated", ""),
                "recommendations": self._generate_system_recommendations(sources)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generating credibility report: {e}")
            return {"error": str(e)}
    
    def _calculate_credibility_distribution(self, sources: Dict) -> Dict:
        """Calculate distribution of credibility levels"""
        try:
            distribution = {
                "very_high": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "very_low": 0
            }
            
            for source_data in sources.values():
                avg_credibility = source_data.get("average_credibility", 0)
                level = self._classify_credibility_level(avg_credibility)
                
                if level == "Very High":
                    distribution["very_high"] += 1
                elif level == "High":
                    distribution["high"] += 1
                elif level == "Medium":
                    distribution["medium"] += 1
                elif level == "Low":
                    distribution["low"] += 1
                else:
                    distribution["very_low"] += 1
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating credibility distribution: {e}")
            return {}
    
    def _generate_system_recommendations(self, sources: Dict) -> List[str]:
        """Generate system-wide recommendations"""
        try:
            recommendations = []
            
            total_sources = len(sources)
            if total_sources == 0:
                recommendations.append("📊 No sources tracked yet - start analyzing articles")
                return recommendations
            
            # Analyze credibility distribution
            high_credibility_count = sum(
                1 for data in sources.values()
                if data.get("average_credibility", 0) >= 0.6
            )
            
            if high_credibility_count / total_sources < 0.3:
                recommendations.append("⚠️ Low proportion of high-credibility sources")
                recommendations.append("🔍 Focus on fact-checking and verification")
            
            if high_credibility_count / total_sources > 0.7:
                recommendations.append("✅ Good proportion of high-credibility sources")
            
            recommendations.append("📚 Continue reading from diverse sources")
            recommendations.append("🔍 Regular fact-checking improves media literacy")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Error generating system recommendations: {e}")
            return ["Error generating recommendations"] 