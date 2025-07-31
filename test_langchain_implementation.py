#!/usr/bin/env python3
"""
Test script demonstrating proper LangChain implementation
"""

import os
import json
from datetime import datetime
from config.settings import Config
from fetchers.newsapi_fetcher import NewsAPIFetcher
from utils.logger import setup_logger

# LangChain imports (updated to use newer packages)
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def test_langchain_implementation():
    """Test the complete LangChain RAG pipeline"""
    print("🧠 Testing LangChain Implementation")
    print("=" * 50)
    
    try:
        config = Config()
        logger = setup_logger("LangChainTest")
        
        # 1. Fetch news articles
        print("📰 Step 1: Fetching news articles...")
        fetcher = NewsAPIFetcher(config.NEWSAPI_KEY)
        articles = fetcher.fetch_news("artificial intelligence", 3, 7)
        
        if not articles:
            print("❌ No articles fetched")
            return
        
        print(f"✅ Fetched {len(articles)} articles")
        
        # 2. Initialize LangChain components
        print("\n🔧 Step 2: Initializing LangChain components...")
        
        # LLM (Ollama + Mistral) - using updated import
        llm = OllamaLLM(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0.7
        )
        print("✅ LLM initialized")
        
        # Embeddings - using updated import
        embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
        print("✅ Embeddings initialized")
        
        # Text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        print("✅ Text splitter initialized")
        
        # 3. Process documents
        print("\n📝 Step 3: Processing documents...")
        documents = []
        
        for i, article in enumerate(articles, 1):
            print(f"   Processing article {i}: {article['title'][:50]}...")
            
            # Create document with metadata
            doc = Document(
                page_content=article['content'],
                metadata={
                    "title": article['title'],
                    "source": article['source'],
                    "url": article['url'],
                    "published_at": article['published_at'],
                    "author": article.get('author', 'Unknown')
                }
            )
            documents.append(doc)
        
        print(f"✅ Created {len(documents)} documents")
        
        # 4. Split documents into chunks
        print("\n✂️ Step 4: Splitting documents into chunks...")
        all_chunks = []
        for doc in documents:
            chunks = text_splitter.split_documents([doc])
            all_chunks.extend(chunks)
        
        print(f"✅ Created {len(all_chunks)} chunks")
        
        # 5. Create vector store
        print("\n🗄️ Step 5: Creating vector store...")
        vector_store = FAISS.from_documents(all_chunks, embeddings)
        print("✅ Vector store created")
        
        # 6. Create retrieval chain
        print("\n🔗 Step 6: Creating retrieval chain...")
        
        # Create prompt template
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""Based on the following context, answer the question. If you don't know the answer, say so.

Context: {context}

Question: {question}

Answer:"""
        )
        
        # Create retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": prompt_template}
        )
        print("✅ Retrieval QA chain created")
        
        # 7. Test the RAG system
        print("\n❓ Step 7: Testing RAG system...")
        
        test_questions = [
            "What are the main AI developments mentioned?",
            "How is China approaching AI?",
            "What is the EU doing with AI?"
        ]
        
        for question in test_questions:
            print(f"\nQuestion: {question}")
            try:
                # Use invoke instead of __call__ to avoid deprecation warning
                result = qa_chain.invoke({"query": question})
                answer = result.get("result", "No answer generated")
                print(f"Answer: {answer[:200]}...")
            except Exception as e:
                print(f"Error: {e}")
        
        # 8. Save vector store
        print("\n💾 Step 8: Saving vector store...")
        vector_store.save_local("data/faiss_store")
        print("✅ Vector store saved")
        
        # 9. Save metadata
        print("\n📊 Step 9: Saving metadata...")
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "articles_count": len(articles),
            "documents_count": len(documents),
            "chunks_count": len(all_chunks),
            "vector_store_path": "data/faiss_store",
            "model": config.OLLAMA_MODEL,
            "embedding_model": config.EMBEDDING_MODEL
        }
        
        with open("data/langchain_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print("✅ Metadata saved")
        
        print("\n🎉 LangChain implementation test completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Articles processed: {len(articles)}")
        print(f"   - Documents created: {len(documents)}")
        print(f"   - Chunks generated: {len(all_chunks)}")
        print(f"   - Vector store: data/faiss_store")
        print(f"   - Metadata: data/langchain_metadata.json")
        
    except Exception as e:
        print(f"❌ Error in LangChain implementation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_langchain_implementation() 