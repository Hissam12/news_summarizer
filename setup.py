#!/usr/bin/env python3
"""
Setup script for Enhanced AI News Summarizer
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create a sample .env file"""
    env_content = """# NewsAPI Configuration
# Get your API key from https://newsapi.org/
NEWSAPI_KEY=your_newsapi_key_here

# Ollama Configuration
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434

# Vector Store Configuration
VECTOR_STORE_PATH=data/faiss_store
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Application Settings
MAX_ARTICLES=5
SUMMARY_MAX_LENGTH=200
SEARCH_DAYS_BACK=7
DEFAULT_QUERY=artificial intelligence

# Logging
LOG_FILE=logs/app.log
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("⚠️  Please edit .env file and add your NewsAPI key")
    else:
        print("ℹ️  .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = ["data", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Created necessary directories")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import requests
        import langchain
        import faiss
        import sentence_transformers
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Enhanced AI News Summarizer")
    print("-" * 50)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file and add your NewsAPI key")
    print("2. Install Ollama: https://ollama.ai/")
    print("3. Pull a model: ollama pull mistral")
    print("4. Start Ollama: ollama serve")
    print("5. Run the app: python main.py")

if __name__ == "__main__":
    main() 