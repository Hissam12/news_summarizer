#!/usr/bin/env python3
"""
Simplified AI News Summarizer
Fetches articles, summarizes them, and displays results directly
"""

import os
import sys
from datetime import datetime
from config.settings import Config
from fetchers.newsapi_fetcher import NewsAPIFetcher
from summarizer.summarizer import TextSummarizer
from utils.logger import setup_logger

def main():
    """Main function - simplified workflow"""
    print("📡 AI News Summarizer")
    print("=" * 50)
    
    try:
        # Initialize components
        config = Config()
        logger = setup_logger("SimpleNewsSummarizer")
        
        # Get search query
        query = input("🔍 What would you like to search for? (press Enter for 'artificial intelligence'): ").strip()
        query = query or "artificial intelligence"
        
        print(f"\n🔍 Searching for: {query}")
        print("=" * 50)
        
        # Fetch articles
        fetcher = NewsAPIFetcher(config.NEWSAPI_KEY)
        articles = fetcher.fetch_news(query, config.MAX_ARTICLES, config.SEARCH_DAYS_BACK)
        
        if not articles:
            print("❌ No articles found for this query.")
            return
        
        print(f"📰 Found {len(articles)} articles")
        print()
        
        # Display articles
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   URL: {article['url']}")
            print()
        
        # Summarize articles
        print("🤖 Generating AI summaries...")
        print("=" * 50)
        
        summarizer = TextSummarizer(config.OLLAMA_MODEL, config.OLLAMA_BASE_URL)
        summarized_articles = summarizer.summarize_articles(articles, config.SUMMARY_MAX_LENGTH)
        
        # Display summaries
        print(f"\n📄 AI Summaries ({len(summarized_articles)} articles)")
        print("=" * 50)
        
        for i, article in enumerate(summarized_articles, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   Summary: {article.get('summary', 'No summary generated')}")
            print("-" * 50)
        
        # Save results
        save_results(summarized_articles, query)
        
        print(f"\n✅ Done! Summaries saved to 'data/summaries.json'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Application error: {e}")

def save_results(articles, query):
    """Save summaries to file"""
    try:
        import json
        
        os.makedirs("data", exist_ok=True)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "articles_count": len(articles),
            "articles": []
        }
        
        for article in articles:
            results["articles"].append({
                "title": article['title'],
                "source": article['source'],
                "url": article['url'],
                "published_at": article['published_at'],
                "summary": article.get('summary', 'No summary generated')
            })
        
        with open("data/summaries.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"⚠️ Warning: Could not save results: {e}")

if __name__ == "__main__":
    main() 