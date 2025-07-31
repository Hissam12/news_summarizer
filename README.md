# 🤖 AI News Summarizer

An intelligent news processing system that fetches, summarizes, and analyzes news articles using AI-powered natural language processing.

## 🚀 Features

- **📰 News Fetching**: Real-time news retrieval from NewsAPI
- **🤖 AI Summarization**: Intelligent article summarization using Ollama (Mistral)
- **🔍 RAG System**: Retrieval-Augmented Generation for question answering
- **📊 Bias Detection**: Multi-source comparison and bias analysis
- **💾 Vector Storage**: ChromaDB integration for semantic search
- **📈 Observability**: LangSmith integration for monitoring and tracing

## 🛠️ Tech Stack

- **Python 3.13**
- **LangChain**: LLM orchestration and RAG
- **Ollama**: Local LLM server (Mistral)
- **ChromaDB**: Vector database
- **NewsAPI**: News data source
- **LangSmith**: Observability and monitoring

## 📦 Installation

### Prerequisites
- Python 3.13+
- Ollama installed and running
- NewsAPI key

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd news_summarizer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables
Create a `.env` file with:
```env
# NewsAPI Configuration
NEWSAPI_KEY=your_newsapi_key_here
MAX_ARTICLES=5
SEARCH_DAYS_BACK=7

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# LangSmith Configuration (optional)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=news-summarizer
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# ChromaDB Configuration
USE_CHROMA=true
CHROMA_PERSIST_DIRECTORY=data/chroma_db
```

## 🎯 Usage

### Simple News Summarizer
```bash
python main_simple.py
```

### Enhanced News App (with RAG)
```bash
python main_enhanced.py
```

### Full Interactive App
```bash
python main.py
```

## 📁 Project Structure

```
news_summarizer/
├── main.py                 # Full interactive application
├── main_simple.py         # Simplified news summarizer
├── main_enhanced.py       # Enhanced app with RAG
├── config/
│   └── settings.py        # Configuration management
├── fetchers/
│   └── newsapi_fetcher.py # News API integration
├── summarizer/
│   └── summarizer.py      # AI summarization
├── rag/
│   ├── ingest.py          # Document ingestion
│   └── query.py           # RAG querying
├── bias_detection/        # Bias analysis (planned)
├── categories/            # News categorization (planned)
├── digest/               # News digest generation (planned)
└── utils/
    └── logger.py         # Logging utilities
```

## 🔧 Configuration

### NewsAPI Setup
1. Get API key from [NewsAPI](https://newsapi.org/)
2. Add to `.env` file

### Ollama Setup
1. Install [Ollama](https://ollama.ai/)
2. Pull Mistral model: `ollama pull mistral`
3. Start Ollama server: `ollama serve`

### LangSmith Setup (Optional)
1. Get API key from [LangSmith](https://smith.langchain.com/)
2. Add to `.env` file for observability

## 🧪 Testing

```bash
# Test basic functionality
python test_app.py

# Test enhanced features
python test_enhanced.py

# Test LangChain implementation
python test_langchain_implementation.py
```

## 🔒 Security

- **API Keys**: Stored in `.env` file (not committed to git)
- **Data Privacy**: Local processing with Ollama
- **Vector Storage**: Local ChromaDB instance
- **Logging**: Configurable logging levels

## 📈 Roadmap

- [ ] **Bias Detection**: Multi-source comparison
- [ ] **News Categories**: Automated categorization
- [ ] **Digest Generation**: Morning/evening briefings
- [ ] **Web Interface**: User-friendly UI
- [ ] **Real-time Alerts**: Breaking news notifications
- [ ] **Personalization**: User preference learning

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Always verify information from multiple sources and use critical thinking when consuming news.

## 🆘 Support

If you encounter issues:
1. Check the [Issues](https://github.com/your-username/news_summarizer/issues) page
2. Ensure all dependencies are installed
3. Verify your API keys are correct
4. Check that Ollama is running

---

**Built with ❤️ using LangChain, Ollama, and NewsAPI**
