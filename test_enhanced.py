#!/usr/bin/env python3
"""
Test Enhanced AI News Summarizer with LangSmith and ChromaDB
Demonstrates the integration without user input
"""

import os
import sys
from datetime import datetime
from config.settings import Config
from fetchers.newsapi_fetcher import NewsAPIFetcher
from summarizer.summarizer import TextSummarizer
from utils.logger import setup_logger

# LangChain imports
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA

# LangSmith setup
import langsmith

def setup_langsmith(config):
    """Setup LangSmith for observability"""
    if config.LANGSMITH_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = config.LANGSMITH_ENDPOINT
        os.environ["LANGCHAIN_API_KEY"] = config.LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = config.LANGSMITH_PROJECT
        print("🔍 LangSmith tracing enabled")
    else:
        print("⚠️ LangSmith API key not set - tracing disabled")

def test_enhanced_summarizer():
    """Test the enhanced summarizer with LangSmith and ChromaDB"""
    print("🚀 Testing Enhanced AI News Summarizer")
    print("=" * 50)
    
    try:
        # Initialize components
        config = Config()
        logger = setup_logger("TestEnhancedSummarizer")
        
        # Setup LangSmith
        setup_langsmith(config)
        
        # Test query
        query = "latest technology news"
        
        print(f"\n🔍 Searching for: {query}")
        print("=" * 50)
        
        # Fetch articles
        fetcher = NewsAPIFetcher(config.NEWSAPI_KEY)
        articles = fetcher.fetch_news(query, 3, config.SEARCH_DAYS_BACK)  # Reduced to 3 for testing
        
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
        
        # Store in ChromaDB
        print("\n💾 Storing in ChromaDB...")
        store_in_chromadb(summarized_articles, config)
        
        # Save results
        save_results(summarized_articles, query)
        
        print(f"\n✅ Done! Summaries saved and stored in ChromaDB")
        
        # Test RAG
        print("\n🔍 Testing RAG with ChromaDB...")
        test_rag(config)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Test error: {e}")

def store_in_chromadb(articles, config):
    """Store articles in ChromaDB"""
    try:
        # Initialize embeddings
        embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
        
        # Create documents
        documents = []
        for article in articles:
            # Combine title and summary for better retrieval
            content = f"Title: {article['title']}\n\nSummary: {article.get('summary', 'No summary')}\n\nSource: {article['source']}"
            
            doc = Document(
                page_content=content,
                metadata={
                    "title": article['title'],
                    "source": article['source'],
                    "url": article['url'],
                    "published_at": article['published_at'],
                    "summary": article.get('summary', 'No summary generated')
                }
            )
            documents.append(doc)
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        
        splits = text_splitter.split_documents(documents)
        
        # Store in ChromaDB
        os.makedirs(config.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=config.CHROMA_PERSIST_DIRECTORY
        )
        
        vectorstore.persist()
        print(f"✅ Stored {len(splits)} chunks in ChromaDB")
        
    except Exception as e:
        print(f"❌ Error storing in ChromaDB: {e}")

def test_rag(config):
    """Test RAG with ChromaDB"""
    try:
        print("\n🔍 Testing RAG System")
        print("=" * 30)
        
        # Load ChromaDB
        embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
        vectorstore = Chroma(
            persist_directory=config.CHROMA_PERSIST_DIRECTORY,
            embedding_function=embeddings
        )
        
        # Initialize LLM
        llm = OllamaLLM(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0.7
        )
        
        # Create RAG chain
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        
        # Test questions
        test_questions = [
            "What are the main technology developments mentioned?",
            "Which companies are discussed in the articles?"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            
            try:
                result = qa_chain.invoke({"query": question})
                
                print("\n📘 Answer:")
                print("-" * 40)
                print(result['result'])
                print("-" * 40)
                
                # Show sources
                sources = result.get('source_documents', [])
                if sources:
                    print(f"\n📚 Sources ({len(sources)}):")
                    for i, doc in enumerate(sources, 1):
                        print(f"{i}. {doc.metadata.get('title', 'Unknown')}")
                        print(f"   Source: {doc.metadata.get('source', 'Unknown')}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Error in RAG test: {e}")

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
        
        with open("data/enhanced_summaries.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        print("✅ Results saved to data/enhanced_summaries.json")
            
    except Exception as e:
        print(f"⚠️ Warning: Could not save results: {e}")

if __name__ == "__main__":
    test_enhanced_summarizer() 