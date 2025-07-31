import os
import signal
import sys
from typing import Dict, List
from config.settings import Config
from fetchers.newsapi_fetcher import NewsAPIFetcher
from summarizer.summarizer import TextSummarizer
from rag.ingest import DocumentIngestor
from rag.query import RAGQueryEngine
from utils.logger import setup_logger
from utils.validators import validate_api_key, validate_query, validate_ollama_connection, sanitize_query

class NewsSummarizerApp:
    def __init__(self):
        self.logger = setup_logger("NewsSummarizerApp")
        self.config = None
        self.fetcher = None
        self.summarizer = None
        self.ingestor = None
        self.query_engine = None
        self.running = True

    def initialize(self) -> bool:
        """Initialize the application with error handling"""
        try:
            self.logger.info("🚀 Initializing Enhanced AI News Summarizer")
            
            # Load configuration
            self.config = Config()
            
            # Validate API key
            if not validate_api_key(self.config.NEWSAPI_KEY):
                self.logger.error("❌ Missing or invalid NewsAPI key")
                print("❌ Missing or invalid NewsAPI key")
                print("Please set your NEWSAPI_KEY in .env file or environment variables")
                return False
            
            # Validate Ollama connection
            if not validate_ollama_connection(self.config.OLLAMA_BASE_URL):
                self.logger.warning("⚠️ Ollama not accessible")
                print("⚠️ Warning: Ollama not accessible")
                print("Make sure Ollama is running and the model is installed")
                print("You can still use the app, but summarization may fail")
            
            # Initialize components
            self.fetcher = NewsAPIFetcher(self.config.NEWSAPI_KEY)
            self.summarizer = TextSummarizer(self.config.OLLAMA_MODEL, self.config.OLLAMA_BASE_URL)
            self.ingestor = DocumentIngestor()
            self.query_engine = RAGQueryEngine()
            
            self.logger.info("✅ Application initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize application: {e}")
            print(f"❌ Initialization failed: {e}")
            return False

    def display_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 60)
        print("📡 Enhanced AI News Summarizer")
        print("=" * 60)
        print("1. 📰 Fetch and summarize news")
        print("2. 🔍 Query knowledge base")
        print("3. 📊 View statistics")
        print("4. 📄 View saved summaries")
        print("5. 🗑️ Clear vector store")
        print("6. ⚙️ Settings")
        print("7. ❌ Exit")
        print("-" * 60)

    def handle_fetch_news(self):
        """Handle news fetching and summarization"""
        try:
            query = input("🔍 Search topic (press Enter for default): ").strip()
            query = query or self.config.DEFAULT_QUERY
            query = sanitize_query(query)
            
            if not validate_query(query):
                print("❌ Invalid query. Please use only letters, numbers, and common punctuation.")
                return
            
            print(f"🔍 Searching for: {query}")
            articles = self.fetcher.fetch_news(query, self.config.MAX_ARTICLES, self.config.SEARCH_DAYS_BACK)
            
            if not articles:
                print("❌ No articles found for this query.")
                return
            
            print(f"📰 Found {len(articles)} articles")
            
            # Display articles
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Source: {article['source']}")
                print(f"   Published: {article['published_at']}")
                print(f"   URL: {article['url']}")
            
            # Summarize articles
            print(f"\n📝 Summarizing {len(articles)} articles...")
            summarized = self.summarizer.summarize_articles(articles, self.config.SUMMARY_MAX_LENGTH)
            
            # Display summaries
            print(f"\n📄 Generated Summaries:")
            print("=" * 60)
            for i, article in enumerate(summarized, 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Source: {article['source']}")
                print(f"   Summary: {article.get('summary', 'No summary generated')}")
                print("-" * 40)
            
            # Ingest documents
            print("\n💾 Ingesting articles into knowledge base...")
            success = self.ingestor.ingest_documents(summarized)
            
            if success:
                print("✅ Articles processed and stored successfully!")
            else:
                print("❌ Failed to store articles")
                
        except Exception as e:
            self.logger.error(f"❌ Error in fetch_news: {e}")
            print(f"❌ Error: {e}")

    def handle_query_knowledge_base(self):
        """Handle knowledge base queries"""
        try:
            question = input("❓ Ask a question: ").strip()
            if not question:
                print("❌ Please provide a question.")
                return
            
            question = sanitize_query(question)
            print("🔍 Searching knowledge base...")
            
            result = self.query_engine.query(question)
            
            if result.get("error"):
                print(f"❌ Error: {result['error']}")
                return
            
            print("\n📘 Answer:")
            print("-" * 40)
            print(result['answer'])
            print("-" * 40)
            
            # Display sources
            sources = result.get('sources', [])
            if sources:
                print(f"\n📚 Sources ({len(sources)}):")
                for i, source in enumerate(sources, 1):
                    print(f"{i}. {source['title']}")
                    print(f"   Source: {source['source']}")
                    if source['url']:
                        print(f"   URL: {source['url']}")
                    print()
            
        except Exception as e:
            self.logger.error(f"❌ Error in query_knowledge_base: {e}")
            print(f"❌ Error: {e}")

    def handle_statistics(self):
        """Display application statistics"""
        try:
            print("\n📊 Application Statistics")
            print("-" * 40)
            
            # Knowledge base info
            kb_info = self.query_engine.get_knowledge_base_info()
            print(f"Knowledge Base:")
            print(f"  - Loaded: {'✅' if kb_info['loaded'] else '❌'}")
            print(f"  - Documents: {kb_info.get('document_count', 0)}")
            print(f"  - Index Size: {kb_info.get('index_size', 0)}")
            
            # Vector store info
            store_info = self.ingestor.get_store_info()
            print(f"\nVector Store:")
            print(f"  - Exists: {'✅' if store_info['exists'] else '❌'}")
            print(f"  - Document Count: {store_info.get('document_count', 0)}")
            
            # Configuration info
            print(f"\nConfiguration:")
            print(f"  - Model: {self.config.OLLAMA_MODEL}")
            print(f"  - Embedding Model: {self.config.EMBEDDING_MODEL}")
            print(f"  - Max Articles: {self.config.MAX_ARTICLES}")
            print(f"  - Summary Length: {self.config.SUMMARY_MAX_LENGTH}")
            
        except Exception as e:
            self.logger.error(f"❌ Error in statistics: {e}")
            print(f"❌ Error: {e}")

    def handle_view_summaries(self):
        """Display saved summaries"""
        try:
            import json
            import os
            
            summaries_path = "data/summaries.json"
            
            if not os.path.exists(summaries_path):
                print("❌ No saved summaries found.")
                print("Fetch some articles first to generate summaries.")
                return
            
            with open(summaries_path, "r", encoding="utf-8") as f:
                summaries = json.load(f)
            
            print(f"\n📄 Saved Summaries ({len(summaries)} articles)")
            print("=" * 60)
            
            for i, summary in enumerate(summaries, 1):
                print(f"\n{i}. {summary['title']}")
                print(f"   Source: {summary['source']}")
                print(f"   Published: {summary['published_at']}")
                print(f"   URL: {summary['url']}")
                print(f"   Summary: {summary['summary']}")
                print("-" * 40)
            
        except Exception as e:
            self.logger.error(f"❌ Error viewing summaries: {e}")
            print(f"❌ Error: {e}")

    def handle_clear_vector_store(self):
        """Handle vector store clearing"""
        try:
            confirm = input("🗑️ Are you sure you want to clear the vector store? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                success = self.ingestor.clear_vector_store()
                if success:
                    print("✅ Vector store cleared successfully")
                    # Reload query engine
                    self.query_engine.reload_vector_store()
                else:
                    print("❌ Failed to clear vector store")
            else:
                print("❌ Operation cancelled")
                
        except Exception as e:
            self.logger.error(f"❌ Error in clear_vector_store: {e}")
            print(f"❌ Error: {e}")

    def handle_settings(self):
        """Display and modify settings"""
        print("\n⚙️ Current Settings")
        print("-" * 40)
        print(f"Model: {self.config.OLLAMA_MODEL}")
        print(f"Max Articles: {self.config.MAX_ARTICLES}")
        print(f"Summary Length: {self.config.SUMMARY_MAX_LENGTH}")
        print(f"Search Days Back: {self.config.SEARCH_DAYS_BACK}")
        print(f"Default Query: {self.config.DEFAULT_QUERY}")
        print("\nTo change settings, modify your .env file or environment variables")

    def run(self):
        """Main application loop"""
        if not self.initialize():
            return
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        while self.running:
            try:
                self.display_menu()
                choice = input("Choose an option: ").strip()
                
                if choice == "1":
                    self.handle_fetch_news()
                elif choice == "2":
                    self.handle_query_knowledge_base()
                elif choice == "3":
                    self.handle_statistics()
                elif choice == "4":
                    self.handle_view_summaries()
                elif choice == "5":
                    self.handle_clear_vector_store()
                elif choice == "6":
                    self.handle_settings()
                elif choice == "7":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                self.logger.error(f"❌ Unexpected error: {e}")
                print(f"❌ Unexpected error: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n👋 Shutting down gracefully...")
        self.running = False

def main():
    app = NewsSummarizerApp()
    app.run()

if __name__ == "__main__":
    main()
