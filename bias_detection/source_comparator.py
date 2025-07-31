#!/usr/bin/env python3
"""
Source Comparator for News Articles

Compares articles from different sources on the same topic to identify:
- Factual discrepancies
- Different perspectives
- Coverage gaps
- Source reliability patterns
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import os

from config.settings import Config
from fetchers.newsapi_fetcher import NewsAPIFetcher


class SourceComparator:
    """Compare news coverage across different sources"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.fetcher = NewsAPIFetcher(config.NEWSAPI_KEY)
        
    def compare_sources_on_topic(self, topic: str, sources: List[str] = None) -> Dict:
        """
        Compare how different sources cover the same topic
        
        Args:
            topic: The topic to compare
            sources: List of specific sources to compare (optional)
            
        Returns:
            Dictionary containing comparison results
        """
        try:
            self.logger.info(f"🔍 Comparing sources on topic: {topic}")
            
            # Fetch articles from different sources
            articles_by_source = self._fetch_articles_by_source(topic, sources)
            
            if not articles_by_source:
                return {"error": "No articles found for comparison"}
            
            # Analyze coverage differences
            coverage_analysis = self._analyze_coverage_differences(articles_by_source)
            
            # Detect factual discrepancies
            factual_discrepancies = self._detect_factual_discrepancies(articles_by_source)
            
            # Identify perspective differences
            perspective_analysis = self._analyze_perspective_differences(articles_by_source)
            
            # Generate comparison report
            comparison_report = self._generate_comparison_report(
                topic, articles_by_source, coverage_analysis, 
                factual_discrepancies, perspective_analysis
            )
            
            # Save comparison results
            self._save_comparison_results(topic, comparison_report)
            
            return comparison_report
            
        except Exception as e:
            self.logger.error(f"❌ Error in source comparison: {e}")
            return {"error": str(e)}
    
    def _fetch_articles_by_source(self, topic: str, sources: List[str] = None) -> Dict[str, List[Dict]]:
        """Fetch articles grouped by source"""
        try:
            articles_by_source = {}
            
            if sources:
                # Fetch from specific sources
                for source in sources:
                    articles = self.fetcher.fetch_news(topic, 3, self.config.SEARCH_DAYS_BACK)
                    # Filter by source (simplified - in real implementation you'd use source parameter)
                    source_articles = [a for a in articles if a.get('source', '').lower() == source.lower()]
                    if source_articles:
                        articles_by_source[source] = source_articles
            else:
                # Fetch from multiple sources automatically
                articles = self.fetcher.fetch_news(topic, 15, self.config.SEARCH_DAYS_BACK)
                
                # Group by source
                for article in articles:
                    source = article.get('source', 'Unknown')
                    if source not in articles_by_source:
                        articles_by_source[source] = []
                    articles_by_source[source].append(article)
                
                # Keep only sources with multiple articles for better comparison
                articles_by_source = {
                    source: articles for source, articles in articles_by_source.items()
                    if len(articles) >= 1
                }
            
            self.logger.info(f"📰 Found articles from {len(articles_by_source)} sources")
            return articles_by_source
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching articles by source: {e}")
            return {}
    
    def _analyze_coverage_differences(self, articles_by_source: Dict[str, List[Dict]]) -> Dict:
        """Analyze how different sources cover the same topic"""
        try:
            coverage_analysis = {
                "sources_compared": len(articles_by_source),
                "coverage_patterns": {},
                "coverage_gaps": [],
                "coverage_overlap": {}
            }
            
            # Analyze coverage patterns for each source
            for source, articles in articles_by_source.items():
                coverage_analysis["coverage_patterns"][source] = {
                    "article_count": len(articles),
                    "average_length": sum(len(a.get('content', '')) for a in articles) / len(articles) if articles else 0,
                    "focus_areas": self._identify_focus_areas(articles),
                    "tone": self._analyze_source_tone(articles)
                }
            
            # Identify coverage gaps
            all_focus_areas = set()
            for source_data in coverage_analysis["coverage_patterns"].values():
                all_focus_areas.update(source_data["focus_areas"])
            
            for source, articles in articles_by_source.items():
                source_focus = set(coverage_analysis["coverage_patterns"][source]["focus_areas"])
                gaps = all_focus_areas - source_focus
                if gaps:
                    coverage_analysis["coverage_gaps"].append({
                        "source": source,
                        "missing_areas": list(gaps)
                    })
            
            return coverage_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing coverage differences: {e}")
            return {"error": str(e)}
    
    def _identify_focus_areas(self, articles: List[Dict]) -> List[str]:
        """Identify main focus areas in articles"""
        try:
            # Simplified focus area identification
            focus_keywords = {
                "politics": ["government", "policy", "election", "politician", "congress"],
                "economy": ["economy", "market", "business", "financial", "trade"],
                "technology": ["technology", "tech", "digital", "innovation", "ai"],
                "social": ["society", "community", "social", "people", "public"],
                "international": ["international", "global", "foreign", "world", "country"]
            }
            
            focus_counts = {area: 0 for area in focus_keywords.keys()}
            
            for article in articles:
                content = article.get('content', '').lower()
                title = article.get('title', '').lower()
                full_text = f"{title} {content}"
                
                for area, keywords in focus_keywords.items():
                    if any(keyword in full_text for keyword in keywords):
                        focus_counts[area] += 1
            
            # Return areas with significant coverage
            return [area for area, count in focus_counts.items() if count > 0]
            
        except Exception as e:
            self.logger.error(f"❌ Error identifying focus areas: {e}")
            return []
    
    def _analyze_source_tone(self, articles: List[Dict]) -> str:
        """Analyze the overall tone of a source's coverage"""
        try:
            positive_words = ['positive', 'good', 'success', 'improve', 'gain', 'benefit']
            negative_words = ['negative', 'bad', 'problem', 'crisis', 'loss', 'damage']
            neutral_words = ['report', 'announce', 'state', 'indicate', 'show']
            
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for article in articles:
                content = article.get('content', '').lower()
                title = article.get('title', '').lower()
                full_text = f"{title} {content}"
                
                pos_score = sum(1 for word in positive_words if word in full_text)
                neg_score = sum(1 for word in negative_words if word in full_text)
                neu_score = sum(1 for word in neutral_words if word in full_text)
                
                if pos_score > neg_score and pos_score > neu_score:
                    positive_count += 1
                elif neg_score > pos_score and neg_score > neu_score:
                    negative_count += 1
                else:
                    neutral_count += 1
            
            total = len(articles)
            if total == 0:
                return "neutral"
            
            if positive_count / total > 0.4:
                return "positive"
            elif negative_count / total > 0.4:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            self.logger.error(f"❌ Error analyzing source tone: {e}")
            return "neutral"
    
    def _detect_factual_discrepancies(self, articles_by_source: Dict[str, List[Dict]]) -> Dict:
        """Detect factual discrepancies between sources"""
        try:
            discrepancies = {
                "discrepancy_count": 0,
                "discrepancies": [],
                "consensus_areas": [],
                "contested_claims": []
            }
            
            # Extract key claims from each source
            claims_by_source = {}
            for source, articles in articles_by_source.items():
                claims_by_source[source] = self._extract_key_claims(articles)
            
            # Compare claims across sources
            all_claims = set()
            for claims in claims_by_source.values():
                all_claims.update(claims)
            
            for claim in all_claims:
                sources_with_claim = [
                    source for source, claims in claims_by_source.items()
                    if claim in claims
                ]
                
                if len(sources_with_claim) == 1:
                    # Contested claim - only one source mentions it
                    discrepancies["contested_claims"].append({
                        "claim": claim,
                        "source": sources_with_claim[0],
                        "type": "single_source_claim"
                    })
                    discrepancies["discrepancy_count"] += 1
                elif len(sources_with_claim) == len(articles_by_source):
                    # Consensus claim - all sources mention it
                    discrepancies["consensus_areas"].append(claim)
            
            return discrepancies
            
        except Exception as e:
            self.logger.error(f"❌ Error detecting factual discrepancies: {e}")
            return {"error": str(e)}
    
    def _extract_key_claims(self, articles: List[Dict]) -> List[str]:
        """Extract key factual claims from articles"""
        try:
            claims = []
            
            for article in articles:
                content = article.get('content', '')
                title = article.get('title', '')
                
                # Simplified claim extraction
                # Look for factual statements
                sentences = content.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 20 and any(word in sentence.lower() for word in ['said', 'reported', 'announced', 'confirmed']):
                        claims.append(sentence[:100] + "..." if len(sentence) > 100 else sentence)
            
            return claims[:5]  # Limit to top 5 claims
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting key claims: {e}")
            return []
    
    def _analyze_perspective_differences(self, articles_by_source: Dict[str, List[Dict]]) -> Dict:
        """Analyze differences in perspective and framing"""
        try:
            perspective_analysis = {
                "framing_differences": {},
                "perspective_keywords": {},
                "narrative_angles": {}
            }
            
            for source, articles in articles_by_source.items():
                # Analyze framing keywords
                framing_keywords = self._extract_framing_keywords(articles)
                perspective_analysis["framing_differences"][source] = framing_keywords
                
                # Analyze narrative angles
                narrative_angle = self._identify_narrative_angle(articles)
                perspective_analysis["narrative_angles"][source] = narrative_angle
            
            return perspective_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing perspective differences: {e}")
            return {"error": str(e)}
    
    def _extract_framing_keywords(self, articles: List[Dict]) -> List[str]:
        """Extract keywords that indicate framing"""
        try:
            framing_keywords = []
            
            for article in articles:
                content = article.get('content', '').lower()
                title = article.get('title', '').lower()
                full_text = f"{title} {content}"
                
                # Look for framing indicators
                framing_indicators = [
                    'crisis', 'opportunity', 'challenge', 'success', 'failure',
                    'controversy', 'breakthrough', 'scandal', 'achievement',
                    'struggle', 'victory', 'defeat', 'innovation', 'tradition'
                ]
                
                for indicator in framing_indicators:
                    if indicator in full_text:
                        framing_keywords.append(indicator)
            
            # Return unique keywords
            return list(set(framing_keywords))
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting framing keywords: {e}")
            return []
    
    def _identify_narrative_angle(self, articles: List[Dict]) -> str:
        """Identify the main narrative angle of coverage"""
        try:
            angle_keywords = {
                "conflict": ["conflict", "dispute", "battle", "fight", "opposition"],
                "cooperation": ["cooperation", "partnership", "collaboration", "agreement"],
                "progress": ["progress", "advance", "improve", "develop", "growth"],
                "crisis": ["crisis", "emergency", "danger", "threat", "problem"],
                "opportunity": ["opportunity", "chance", "potential", "prospect"]
            }
            
            angle_counts = {angle: 0 for angle in angle_keywords.keys()}
            
            for article in articles:
                content = article.get('content', '').lower()
                title = article.get('title', '').lower()
                full_text = f"{title} {content}"
                
                for angle, keywords in angle_keywords.items():
                    if any(keyword in full_text for keyword in keywords):
                        angle_counts[angle] += 1
            
            # Return the most common angle
            if angle_counts:
                return max(angle_counts.items(), key=lambda x: x[1])[0]
            else:
                return "neutral"
                
        except Exception as e:
            self.logger.error(f"❌ Error identifying narrative angle: {e}")
            return "neutral"
    
    def _generate_comparison_report(self, topic: str, articles_by_source: Dict, 
                                  coverage_analysis: Dict, factual_discrepancies: Dict, 
                                  perspective_analysis: Dict) -> Dict:
        """Generate comprehensive comparison report"""
        try:
            report = {
                "topic": topic,
                "comparison_timestamp": datetime.now().isoformat(),
                "sources_analyzed": list(articles_by_source.keys()),
                "coverage_analysis": coverage_analysis,
                "factual_discrepancies": factual_discrepancies,
                "perspective_analysis": perspective_analysis,
                "summary": self._generate_comparison_summary(coverage_analysis, factual_discrepancies, perspective_analysis)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generating comparison report: {e}")
            return {"error": str(e)}
    
    def _generate_comparison_summary(self, coverage_analysis: Dict, factual_discrepancies: Dict, 
                                   perspective_analysis: Dict) -> Dict:
        """Generate summary of comparison findings"""
        try:
            summary = {
                "key_findings": [],
                "recommendations": []
            }
            
            # Coverage findings
            if coverage_analysis.get("coverage_gaps"):
                summary["key_findings"].append(f"Coverage gaps detected in {len(coverage_analysis['coverage_gaps'])} sources")
            
            # Factual findings
            if factual_discrepancies.get("discrepancy_count", 0) > 0:
                summary["key_findings"].append(f"{factual_discrepancies['discrepancy_count']} factual discrepancies detected")
            
            # Perspective findings
            narrative_angles = set(perspective_analysis.get("narrative_angles", {}).values())
            if len(narrative_angles) > 1:
                summary["key_findings"].append(f"Different narrative angles detected: {', '.join(narrative_angles)}")
            
            # Recommendations
            if factual_discrepancies.get("discrepancy_count", 0) > 0:
                summary["recommendations"].append("🔍 Fact-check claims with multiple sources")
            
            if coverage_analysis.get("coverage_gaps"):
                summary["recommendations"].append("📖 Seek additional sources for complete coverage")
            
            summary["recommendations"].append("⚖️ Read multiple perspectives for balanced understanding")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Error generating comparison summary: {e}")
            return {"error": str(e)}
    
    def _save_comparison_results(self, topic: str, comparison_report: Dict):
        """Save comparison results to file"""
        try:
            os.makedirs("data", exist_ok=True)
            
            filename = f"data/source_comparison_{topic.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comparison_report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Source comparison saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving comparison results: {e}") 