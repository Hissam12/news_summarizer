import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    def __init__(self):
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate and set up required directories"""
        Path("logs").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
    
    @property
    def NEWSAPI_KEY(self):
        key = os.getenv("NEWSAPI_KEY")
        if not key or key == "your_newsapi_key_here":
            raise ValueError("NEWSAPI_KEY not set. Please set it in your .env file or environment variables.")
        return key
    
    @property
    def OLLAMA_MODEL(self):
        return os.getenv("OLLAMA_MODEL", "mistral")
    
    @property
    def OLLAMA_BASE_URL(self):
        return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    @property
    def VECTOR_STORE_PATH(self):
        return os.getenv("VECTOR_STORE_PATH", "data/faiss_store")
    
    @property
    def EMBEDDING_MODEL(self):
        return os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    @property
    def CHUNK_SIZE(self):
        return int(os.getenv("CHUNK_SIZE", "1000"))
    
    @property
    def CHUNK_OVERLAP(self):
        return int(os.getenv("CHUNK_OVERLAP", "200"))
    
    @property
    def LOG_FILE(self):
        return os.getenv("LOG_FILE", "logs/app.log")
    
    @property
    def MAX_ARTICLES(self):
        return int(os.getenv("MAX_ARTICLES", "5"))
    
    @property
    def SUMMARY_MAX_LENGTH(self):
        return int(os.getenv("SUMMARY_MAX_LENGTH", "200"))
    
    @property
    def SEARCH_DAYS_BACK(self):
        return int(os.getenv("SEARCH_DAYS_BACK", "7"))
    
    @property
    def DEFAULT_QUERY(self):
        return os.getenv("DEFAULT_QUERY", "artificial intelligence")
    
    @property
    def LANGSMITH_API_KEY(self):
        return os.getenv("LANGSMITH_API_KEY", "")
    
    @property
    def LANGSMITH_PROJECT(self):
        return os.getenv("LANGSMITH_PROJECT", "news-summarizer")
    
    @property
    def LANGSMITH_ENDPOINT(self):
        return os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    
    @property
    def CHROMA_PERSIST_DIRECTORY(self):
        return os.getenv("CHROMA_PERSIST_DIRECTORY", "data/chroma_db")
    
    @property
    def USE_CHROMA(self):
        return os.getenv("USE_CHROMA", "true").lower() == "true"

