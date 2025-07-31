import re
import requests
from typing import Optional

def validate_api_key(key: str) -> bool:
    """Validate API key with more flexible rules"""
    if not key or key == "your_newsapi_key_here":
        return False
    # NewsAPI keys are typically 32 characters, but let's be more flexible
    return len(key) >= 20 and key.isalnum()

def validate_query(query: str) -> bool:
    """Validate search query with more flexible rules"""
    if not query or not query.strip():
        return False
    # Allow more characters including quotes, parentheses, and special characters
    cleaned = query.strip()
    return len(cleaned) >= 2 and len(cleaned) <= 200

def validate_ollama_connection(base_url: str = "http://localhost:11434") -> bool:
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def validate_newsapi_connection(api_key: str) -> bool:
    """Test NewsAPI connection"""
    try:
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"country": "us", "apiKey": api_key},
            timeout=10
        )
        return response.status_code == 200
    except requests.RequestException:
        return False

def sanitize_query(query: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', query)
    return sanitized.strip()

def validate_summary_length(text: str, max_length: int = 200) -> bool:
    """Validate if text is appropriate for summarization"""
    if not text or len(text.strip()) < 50:
        return False
    return len(text) <= 10000  # Reasonable limit for summarization
