import os
import shutil
import json
from datetime import datetime
from typing import List, Dict
from config.settings import Config
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.logger import setup_logger

class DocumentIngestor:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger("DocumentIngestor")
        self.embeddings = HuggingFaceEmbeddings(model_name=self.config.EMBEDDING_MODEL)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)

    def ingest_documents(self, articles: List[Dict]) -> bool:
        """Ingest articles into the vector store"""
        try:
            if not articles:
                self.logger.warning("⚠️ No articles to ingest")
                return False
            
            self.logger.info(f"📝 Processing {len(articles)} articles")
            
            # Validate and process articles
            valid_articles = []
            for article in articles:
                if self._validate_article(article):
                    valid_articles.append(article)
                else:
                    self.logger.warning(f"⚠️ Skipping invalid article: {article.get('title', 'Unknown')}")
            
            if not valid_articles:
                self.logger.error("❌ No valid articles to process")
                return False
            
            # Create documents
            documents = []
            for article in valid_articles:
                doc = Document(
                    page_content=article['content'],
                    metadata=self._create_metadata(article)
                )
                documents.append(doc)
            
            self.logger.info(f"✅ Created {len(documents)} documents")
            
            # Split documents into chunks
            all_chunks = []
            for doc in documents:
                chunks = self.splitter.split_documents([doc])
                all_chunks.extend(chunks)
            
            self.logger.info(f"✅ Created {len(all_chunks)} chunks")
            
            # Load or create vector store
            self._load_or_create_store()
            
            # Add documents to vector store
            if self.store:
                self.store.add_documents(all_chunks)
                self.logger.info("✅ Documents added to vector store")
                
                # Save vector store
                self.store.save_local(self.config.VECTOR_STORE_PATH)
                self.logger.info(f"✅ Vector store saved to {self.config.VECTOR_STORE_PATH}")
                
                # Save ingestion metadata
                self._save_ingestion_metadata(valid_articles)
                
                return True
            else:
                self.logger.error("❌ Failed to create vector store")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in ingest_documents: {e}")
            return False

    def _validate_article(self, article: Dict) -> bool:
        """Validate article structure and content"""
        required_fields = ['title', 'content', 'source', 'url', 'published_at']
        
        # Check required fields
        for field in required_fields:
            if field not in article or not article[field]:
                return False
        
        # Check content length
        if len(article['content'].strip()) < 50:
            return False
        
        return True

    def _create_metadata(self, article: Dict) -> Dict:
        """Create metadata for document"""
        return {
            "title": article['title'],
            "source": article['source'],
            "url": article['url'],
            "published_at": article['published_at'],
            "author": article.get('author', 'Unknown'),
            "ingested_at": datetime.now().isoformat()
        }

    def _load_or_create_store(self):
        """Load existing vector store or create new one"""
        try:
            store_path = self.config.VECTOR_STORE_PATH
            
            if os.path.exists(store_path):
                self.logger.info("📂 Loading existing vector store")
                self.store = FAISS.load_local(store_path, self.embeddings, allow_dangerous_deserialization=True)
            else:
                self.logger.info("🆕 Creating new vector store")
                # Create empty vector store
                self.store = FAISS.from_documents([], self.embeddings)
                
        except Exception as e:
            self.logger.error(f"❌ Error loading/creating vector store: {e}")
            self.store = None

    def _save_ingestion_metadata(self, articles: List[Dict]):
        """Save ingestion metadata and summaries"""
        try:
            # Save metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "articles_count": len(articles),
                "articles": [
                    {
                        "title": article['title'],
                        "source": article['source'],
                        "url": article['url'],
                        "published_at": article['published_at']
                    }
                    for article in articles
                ]
            }
            
            metadata_path = "data/ingestion_metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Metadata saved to {metadata_path}")
            
            # Save summaries separately
            summaries = []
            for article in articles:
                summaries.append({
                    "title": article['title'],
                    "source": article['source'],
                    "url": article['url'],
                    "published_at": article['published_at'],
                    "summary": article.get('summary', 'No summary generated'),
                    "content_length": len(article.get('content', ''))
                })
            
            summaries_path = "data/summaries.json"
            with open(summaries_path, "w", encoding="utf-8") as f:
                json.dump(summaries, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Summaries saved to {summaries_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save metadata: {e}")

    def clear_vector_store(self) -> bool:
        """Clear the vector store"""
        try:
            store_path = self.config.VECTOR_STORE_PATH
            
            if os.path.exists(store_path):
                # Remove vector store directory
                shutil.rmtree(store_path)
                self.logger.info("🗑️ Vector store cleared")
            
            # Clear metadata files
            metadata_files = [
                "data/ingestion_metadata.json",
                "data/langchain_metadata.json"
            ]
            
            for file_path in metadata_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.logger.info(f"🗑️ Cleared {file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to clear vector store: {e}")
            return False

    def get_store_info(self) -> Dict:
        """Get information about the vector store"""
        try:
            store_path = self.config.VECTOR_STORE_PATH
            
            if not os.path.exists(store_path):
                return {"exists": False}
            
            # Try to load store to get document count
            try:
                store = FAISS.load_local(store_path, self.embeddings, allow_dangerous_deserialization=True)
                return {
                    "exists": True,
                    "document_count": len(store.docstore._dict) if hasattr(store, 'docstore') else 0
                }
            except Exception:
                return {"exists": True, "document_count": "Unknown"}
                
        except Exception as e:
            self.logger.error(f"❌ Error getting store info: {e}")
            return {"exists": False, "error": str(e)}
