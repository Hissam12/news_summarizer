#!/usr/bin/env python3
"""
Test script for news fetching and summarization with longer timeout
"""

import os
import json
import requests
from datetime import datetime
from config.settings import Config
from fetchers.newsapi_fetcher import NewsAPIFetcher
from utils.logger import setup_logger

def summarize_with_ollama(text, max_length=150, timeout=120):
    """Summarize text using Ollama with longer timeout"""
    try:
        prompt = f"""Please provide a concise summary of the following article in under {max_length} words. Focus on the main points and key information:

{text[:2000]}

Summary:"""
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_length * 2,
                    "temperature": 0.7
                }
            },
            timeout=timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get("response", "").strip()
            if summary.startswith("Summary:"):
                summary = summary[8:].strip()
            return summary
        else:
            return f"Error: HTTP {response.status_code}"
            
    except requests.Timeout:
        return "Error: Request timeout"
    except Exception as e:
        return f"Error: {str(e)}"

def test_news_fetching():
    """Test news fetching functionality"""
    print("🔍 Testing News Fetching...")
    
    try:
        config = Config()
        fetcher = NewsAPIFetcher(config.NEWSAPI_KEY)
        
        # Test fetching articles
        articles = fetcher.fetch_news("artificial intelligence", 2, 7)
        
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
    """Test summarization functionality with longer timeout"""
    print("\n📝 Testing Summarization...")
    
    summarized_articles = []
    for i, article in enumerate(articles, 1):
        print(f"\n📝 Summarizing article {i}/{len(articles)}...")
        print(f"   Title: {article['title'][:60]}...")
        
        # Try to summarize with longer timeout
        summary = summarize_with_ollama(article['content'], 100, 120)
        article['summary'] = summary
        
        print(f"   Summary: {summary[:80]}...")
        summarized_articles.append(article)
    
    return summarized_articles

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
        
        with open("data/test_results_fixed.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to 'data/test_results_fixed.json'")
        
    except Exception as e:
        print(f"❌ Error saving results: {e}")

def main():
    """Main test function"""
    print("🧪 Testing News Fetching and Summarization (Fixed)")
    print("=" * 60)
    
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
        print(f"  - Results saved: data/test_results_fixed.json")
        
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