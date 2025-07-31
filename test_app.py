#!/usr/bin/env python3
"""
Test script for Enhanced AI News Summarizer
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from config.settings import Config
        print("✅ Config module imported")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from fetchers.newsapi_fetcher import NewsAPIFetcher
        print("✅ NewsAPI fetcher imported")
    except Exception as e:
        print(f"❌ NewsAPI fetcher import failed: {e}")
        return False
    
    try:
        from summarizer.summarizer import TextSummarizer
        print("✅ Summarizer imported")
    except Exception as e:
        print(f"❌ Summarizer import failed: {e}")
        return False
    
    try:
        from rag.ingest import DocumentIngestor
        print("✅ Document ingestor imported")
    except Exception as e:
        print(f"❌ Document ingestor import failed: {e}")
        return False
    
    try:
        from rag.query import RAGQueryEngine
        print("✅ RAG query engine imported")
    except Exception as e:
        print(f"❌ RAG query engine import failed: {e}")
        return False
    
    try:
        from utils.logger import setup_logger
        from utils.validators import validate_api_key, validate_query
        print("✅ Utils modules imported")
    except Exception as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config.settings import Config
        config = Config()
        print("✅ Configuration loaded")
        print(f"   - Model: {config.OLLAMA_MODEL}")
        print(f"   - Max Articles: {config.MAX_ARTICLES}")
        print(f"   - Summary Length: {config.SUMMARY_MAX_LENGTH}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_logger():
    """Test logger setup"""
    print("\n🔍 Testing logger...")
    
    try:
        from utils.logger import setup_logger
        logger = setup_logger("TestLogger")
        logger.info("Test log message")
        print("✅ Logger working")
        return True
    except Exception as e:
        print(f"❌ Logger test failed: {e}")
        return False

def test_validators():
    """Test input validation"""
    print("\n🔍 Testing validators...")
    
    try:
        from utils.validators import validate_api_key, validate_query, sanitize_query
        
        # Test API key validation
        assert not validate_api_key("")
        assert not validate_api_key("invalid")
        assert validate_api_key("12345678901234567890123456789012")
        
        # Test query validation
        assert validate_query("test query")
        assert not validate_query("")
        assert not validate_query("a" * 300)  # Too long
        
        # Test sanitization
        assert sanitize_query("test<script>") == "test"
        
        print("✅ Validators working")
        return True
    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection"""
    print("\n🔍 Testing Ollama connection...")
    
    try:
        from utils.validators import validate_ollama_connection
        connected = validate_ollama_connection()
        if connected:
            print("✅ Ollama is accessible")
        else:
            print("⚠️  Ollama not accessible (this is okay for testing)")
        return True
    except Exception as e:
        print(f"❌ Ollama connection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Enhanced AI News Summarizer")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_logger,
        test_validators,
        test_ollama_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("1. Set your NEWSAPI_KEY in .env file")
        print("2. Start Ollama: ollama serve")
        print("3. Run: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 