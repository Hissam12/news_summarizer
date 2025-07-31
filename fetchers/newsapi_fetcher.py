import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from utils.logger import setup_logger

class NewsAPIFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = setup_logger("NewsAPIFetcher")
        self.base_url = "https://newsapi.org/v2/everything"
        self.last_request_time = 0
        self.rate_limit_delay = 1  # seconds between requests

    def _rate_limit(self):
        """Implement basic rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            self._rate_limit()
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 401:
                self.logger.error("❌ Invalid API key")
                raise ValueError("Invalid NewsAPI key. Please check your API key.")
            elif response.status_code == 429:
                self.logger.warning("⚠️ Rate limit exceeded. Waiting...")
                time.sleep(60)  # Wait 1 minute
                return self._make_request(params)  # Retry
            elif response.status_code != 200:
                self.logger.error(f"❌ API request failed: {response.status_code}")
                raise Exception(f"API request failed with status {response.status_code}")
            
            return response.json()
            
        except requests.Timeout:
            self.logger.error("❌ Request timeout")
            raise Exception("Request timeout. Please check your internet connection.")
        except requests.ConnectionError:
            self.logger.error("❌ Connection error")
            raise Exception("Connection error. Please check your internet connection.")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
            raise

    def fetch_news(self, query: str, max_articles: int = 5, days_back: int = 7) -> List[Dict]:
        """Fetch news articles with comprehensive error handling"""
        self.logger.info(f"🔍 Fetching news for: {query}")
        
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)

        params = {
            "q": query,
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": max_articles,
            "apiKey": self.api_key,
        }

        try:
            data = self._make_request(params)
            
            if data.get("status") != "ok":
                error_message = data.get("message", "Unknown error")
                self.logger.error(f"❌ API returned error: {error_message}")
                raise Exception(f"NewsAPI error: {error_message}")

            articles = data.get("articles", [])
            self.logger.info(f"📰 Found {len(articles)} articles")
            
            cleaned = self._clean_articles(articles)
            self.logger.info(f"✅ Processed {len(cleaned)} valid articles")
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch news: {e}")
            raise

    def _clean_articles(self, articles: List[Dict]) -> List[Dict]:
        """Clean and validate articles"""
        cleaned = []
        
        for article in articles:
            try:
                # Check for required fields
                if not all(k in article for k in ("title", "description", "content")):
                    continue
                
                # Skip articles with missing content
                if not article["content"] or article["content"] == "[Removed]":
                    continue
                
                # Create full content
                full_content = f"{article['title']}\n\n{article['description']}\n\n{article['content']}"
                
                # Skip if content is too short
                if len(full_content.strip()) < 100:
                    continue
                
                cleaned_article = {
                    "title": article["title"].strip(),
                    "description": article["description"].strip(),
                    "content": full_content,
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "author": article.get("author", "Unknown"),
                    "url_to_image": article.get("urlToImage", "")
                }
                
                cleaned.append(cleaned_article)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to process article: {e}")
                continue
        
        return cleaned

    def get_article_count(self, query: str) -> int:
        """Get total article count for a query (for statistics)"""
        try:
            params = {
                "q": query,
                "language": "en",
                "pageSize": 1,  # Just get count
                "apiKey": self.api_key,
            }
            
            data = self._make_request(params)
            return data.get("totalResults", 0)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get article count: {e}")
            return 0
