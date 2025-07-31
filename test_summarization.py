#!/usr/bin/env python3
"""
Test script for news fetching and summarization
"""

import os
import json
from datetime import datetime
from config.settings import Config
from fetchers.newsapi_fetcher import NewsAPIFetcher
from summarizer.summarizer import TextSummarizer
from utils.logger import setup_logger

def test_news_fetching():
    """Test news fetching functionality"""
    print("🔍 Testing News Fetching...")
    
    try:
        config = Config()
        fetcher = NewsAPIFetcher(config.NEWSAPI_KEY)
        
        # Test fetching articles
        articles = fetcher.fetch_news("artificial intelligence", 3, 7)
        
        if articles:
            print(f"✅ Successfully fetched {len(articles)} articles")
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Source: {article['source']}")
                print(f"   URL: {article['url']}")
                print(f"   Content length: {len(article['content'])} characters")
            
            return articles
        else:
            print("❌ No articles fetched")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []

def test_summarization(articles):
    """Test summarization functionality"""
    print("\n📝 Testing Summarization...")
    
    try:
        summarizer = TextSummarizer()
        
        summarized_articles = []
        for i, article in enumerate(articles, 1):
            print(f"\n📝 Summarizing article {i}/{len(articles)}...")
            
            # Try to summarize
            summary = summarizer.summarize_text(article['content'], 150)
            article['summary'] = summary
            
            print(f"   Summary: {summary[:100]}...")
            summarized_articles.append(article)
        
        return summarized_articles
        
    except Exception as e:
        print(f"❌ Error in summarization: {e}")
        return articles

def save_results(articles, query):
    """Save results to file"""
    try:
        os.makedirs("data", exist_ok=True)
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "articles_count": len(articles),
            "articles": articles
        }
        
        with open("data/test_results.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to 'data/test_results.json'")
        
    except Exception as e:
        print(f"❌ Error saving results: {e}")

def main():
    """Main test function"""
    print("🧪 Testing News Fetching and Summarization")
    print("=" * 50)
    
    # Test news fetching
    articles = test_news_fetching()
    
    if articles:
        # Test summarization
        summarized_articles = test_summarization(articles)
        
        # Save results
        save_results(summarized_articles, "artificial intelligence")
        
        print("\n📊 Test Summary:")
        print(f"  - Articles fetched: {len(articles)}")
        print(f"  - Articles summarized: {len(summarized_articles)}")
        print(f"  - Results saved: data/test_results.json")
        
        # Show sample results
        if summarized_articles:
            print(f"\n📰 Sample Article:")
            article = summarized_articles[0]
            print(f"  Title: {article['title']}")
            print(f"  Summary: {article.get('summary', 'No summary')}")
    else:
        print("\n❌ No articles to test summarization")

if __name__ == "__main__":
    main() 