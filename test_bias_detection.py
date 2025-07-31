#!/usr/bin/env python3
"""
Test Bias Detection System

Demonstrates the bias detection capabilities:
- Multi-source comparison
- Bias analysis
- Source credibility scoring
"""

import os
import sys
from datetime import datetime
from config.settings import Config
from bias_detection.bias_analyzer import BiasAnalyzer
from bias_detection.source_comparator import SourceComparator
from bias_detection.credibility_scorer import CredibilityScorer
from utils.logger import setup_logger


def test_bias_detection():
    """Test the bias detection system"""
    print("🔍 Testing Bias Detection System")
    print("=" * 50)
    
    try:
        # Initialize components
        config = Config()
        logger = setup_logger("BiasDetectionTest")
        
        # Initialize bias detection components
        bias_analyzer = BiasAnalyzer(config)
        source_comparator = SourceComparator(config)
        credibility_scorer = CredibilityScorer(config)
        
        # Test topic
        test_topic = "artificial intelligence"
        print(f"🎯 Testing bias detection for topic: {test_topic}")
        print()
        
        # Test 1: Bias Analysis
        print("📊 Test 1: Bias Analysis")
        print("-" * 30)
        
        bias_results = bias_analyzer.analyze_topic_bias(test_topic, max_sources=3)
        
        if "error" not in bias_results:
            print(f"✅ Bias analysis completed")
            print(f"📰 Sources analyzed: {bias_results.get('sources_analyzed', 0)}")
            
            # Display bias results
            for source, analysis in bias_results.get('source_analyses', {}).items():
                if "error" not in analysis:
                    bias_level = analysis.get('bias_level', 'Unknown')
                    bias_score = analysis.get('overall_bias_score', 0)
                    print(f"   {source}: {bias_level} bias ({bias_score:.2f})")
            
            # Display recommendations
            recommendations = bias_results.get('recommendations', [])
            if recommendations:
                print("\n💡 Recommendations:")
                for rec in recommendations:
                    print(f"   • {rec}")
        else:
            print(f"❌ Bias analysis failed: {bias_results['error']}")
        
        print()
        
        # Test 2: Source Comparison
        print("📊 Test 2: Source Comparison")
        print("-" * 30)
        
        comparison_results = source_comparator.compare_sources_on_topic(test_topic)
        
        if "error" not in comparison_results:
            print(f"✅ Source comparison completed")
            print(f"📰 Sources compared: {len(comparison_results.get('sources_analyzed', []))}")
            
            # Display comparison summary
            summary = comparison_results.get('summary', {})
            key_findings = summary.get('key_findings', [])
            if key_findings:
                print("\n🔍 Key Findings:")
                for finding in key_findings:
                    print(f"   • {finding}")
            
            recommendations = summary.get('recommendations', [])
            if recommendations:
                print("\n💡 Recommendations:")
                for rec in recommendations:
                    print(f"   • {rec}")
        else:
            print(f"❌ Source comparison failed: {comparison_results['error']}")
        
        print()
        
        # Test 3: Credibility Scoring
        print("📊 Test 3: Credibility Scoring")
        print("-" * 30)
        
        # Get some articles for credibility testing
        from fetchers.newsapi_fetcher import NewsAPIFetcher
        fetcher = NewsAPIFetcher(config.NEWSAPI_KEY)
        articles = fetcher.fetch_news(test_topic, 5, config.SEARCH_DAYS_BACK)
        
        if articles:
            # Group articles by source
            articles_by_source = {}
            for article in articles:
                source = article.get('source', 'Unknown')
                if source not in articles_by_source:
                    articles_by_source[source] = []
                articles_by_source[source].append(article)
            
            # Score each source
            for source, source_articles in articles_by_source.items():
                credibility_result = credibility_scorer.score_source_credibility(source, source_articles)
                
                if "error" not in credibility_result:
                    credibility_level = credibility_result.get('credibility_level', 'Unknown')
                    credibility_score = credibility_result.get('overall_credibility', 0)
                    print(f"   {source}: {credibility_level} credibility ({credibility_score:.2f})")
                    
                    # Show recommendations
                    recs = credibility_result.get('recommendations', [])
                    if recs:
                        for rec in recs[:2]:  # Show first 2 recommendations
                            print(f"     • {rec}")
                else:
                    print(f"   {source}: Error - {credibility_result['error']}")
        else:
            print("❌ No articles found for credibility testing")
        
        print()
        
        # Test 4: Generate Credibility Report
        print("📊 Test 4: Credibility Report")
        print("-" * 30)
        
        credibility_report = credibility_scorer.generate_credibility_report()
        
        if "error" not in credibility_report:
            total_sources = credibility_report.get('total_sources_tracked', 0)
            print(f"📊 Total sources tracked: {total_sources}")
            
            top_sources = credibility_report.get('top_credible_sources', [])
            if top_sources:
                print("\n🏆 Top Credible Sources:")
                for i, source in enumerate(top_sources[:3], 1):
                    credibility = source.get('average_credibility', 0)
                    article_count = source.get('article_count', 0)
                    print(f"   {i}. {source['source']}: {credibility:.2f} ({article_count} articles)")
            
            recommendations = credibility_report.get('recommendations', [])
            if recommendations:
                print("\n💡 System Recommendations:")
                for rec in recommendations:
                    print(f"   • {rec}")
        else:
            print(f"❌ Credibility report failed: {credibility_report['error']}")
        
        print()
        print("✅ Bias detection testing completed!")
        
    except Exception as e:
        print(f"❌ Error in bias detection test: {e}")
        logger.error(f"Bias detection test error: {e}")


if __name__ == "__main__":
    test_bias_detection() 