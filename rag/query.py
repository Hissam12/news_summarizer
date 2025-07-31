import os
import json
from typing import Dict, List, Optional
from config.settings import Config
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from utils.logger import setup_logger
from utils.validators import validate_ollama_connection

class RAGQueryEngine:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger("RAGQueryEngine")
        self.embeddings = HuggingFaceEmbeddings(model_name=self.config.EMBEDDING_MODEL)
        self.llm = None
        self.store = None
        self.qa_chain = None
        self._initialize()

    def _initialize(self):
        """Initialize the query engine"""
        try:
            # Validate Ollama connection
            if not validate_ollama_connection(self.config.OLLAMA_BASE_URL):
                self.logger.warning("⚠️ Ollama not accessible")
                return
            
            # Initialize LLM
            self.llm = OllamaLLM(
                model=self.config.OLLAMA_MODEL,
                base_url=self.config.OLLAMA_BASE_URL,
                temperature=0.7
            )
            
            # Load vector store
            self._load_vector_store()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize query engine: {e}")

    def _load_vector_store(self):
        """Load the vector store and create QA chain"""
        try:
            store_path = self.config.VECTOR_STORE_PATH
            
            if not os.path.exists(store_path):
                self.logger.warning(f"⚠️ Vector store not found at {store_path}")
                return
            
            # Load existing vector store
            self.store = FAISS.load_local(store_path, self.embeddings, allow_dangerous_deserialization=True)
            
            # Create retrieval QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.store.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            
            self.logger.info("✅ Vector store loaded successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load vector store: {e}")

    def query(self, question: str) -> Dict:
        """Query the knowledge base"""
        try:
            if not self.qa_chain:
                return {"error": "Knowledge base not loaded. Please fetch some articles first."}
            
            # Use invoke instead of __call__ to avoid deprecation warning
            result = self.qa_chain.invoke({"query": question})
            
            # Extract answer and sources
            answer = result.get("result", "No answer generated")
            source_documents = result.get("source_documents", [])
            
            # Format sources
            sources = []
            for doc in source_documents:
                metadata = doc.metadata
                sources.append({
                    "title": metadata.get("title", "Unknown"),
                    "source": metadata.get("source", "Unknown"),
                    "url": metadata.get("url", ""),
                    "published_at": metadata.get("published_at", ""),
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                })
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in query: {e}")
            return {"error": f"Query failed: {str(e)}"}

    def get_knowledge_base_info(self) -> Dict:
        """Get information about the knowledge base"""
        try:
            if not self.store:
                return {"loaded": False}
            
            return {
                "loaded": True,
                "document_count": len(self.store.docstore._dict) if hasattr(self.store, 'docstore') else 0,
                "index_size": self.store.index.ntotal if hasattr(self.store, 'index') else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting knowledge base info: {e}")
            return {"loaded": False, "error": str(e)}

    def reload_vector_store(self) -> bool:
        """Reload the vector store"""
        try:
            self._load_vector_store()
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to reload vector store: {e}")
            return False
